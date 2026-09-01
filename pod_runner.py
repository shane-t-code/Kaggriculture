#!/usr/bin/env python3
"""pod_runner.py — parallel paired A/B battery for RunPod CPU (or any box).

Same paired design as pool_ab.py (candidate A and baseline B vs every pool
opponent on identical seeds, both seats) but:
  - runs games in parallel across all cores (multiprocessing, ~Nx faster)
  - calls the engine directly (no run_local subprocess / stdout parsing)
  - reports W-L-T explicitly (pool_ab counted mirror TIES as A-losses —
    harness law, Exp 45) and mirror dWins excludes ties
  - writes one JSON line per game for stratified decodes (fired-game
    analysis without rerunning anything)

Usage (local smoke test):
    python pod_runner.py --a versions/v24c.py --seeds 4 --procs 4
On the pod (32 vCPU):
    python pod_runner.py --a versions/v24c.py --seeds 500 --procs 32 \
        --jsonl results_v24c.jsonl
"""
from __future__ import annotations
import argparse, json, os, sys
from multiprocessing import Pool, cpu_count

POOL_OPPS = [
    ("mirror", None),                       # None -> baseline B itself
    ("tape", "versions/meta_boatlee.py"),
    ("v6a", "versions/v6a.py"),
    ("v12", "versions/v12b.py"),
]

_AGENT_CACHE: dict = {}

def _load_agent(path):
    if path not in _AGENT_CACHE:
        import importlib.util
        name = "agent_" + os.path.basename(path).replace(".py", "").replace("-", "_")
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _AGENT_CACHE[path] = mod.agent
    return _AGENT_CACHE[path]

def _play(job):
    """job = (leg, agent0_path, agent1_path, seed). Returns final banks."""
    leg, p0, p1, seed = job
    from kaggle_environments import make
    env = make("kaggriculture", configuration={"seed": seed})
    env.run([_load_agent(p0), _load_agent(p1)])
    farms = env.steps[-1][0]["observation"]["farms"]
    statuses = [s["status"] for s in env.steps[-1]]
    # day-14 shop draw: lets analyses bucket paired results by town scenario
    # (STR-dead towns, egg towns, wheat towns...) without rerunning games
    try:
        shops14 = env.steps[min(336, len(env.steps) - 1)][0]["observation"]["town"]["unlocked_shops"]
    except Exception:
        shops14 = []
    return {"leg": leg, "p0": p0, "p1": p1, "seed": seed,
            "banks": [farms[0]["money"], farms[1]["money"]],
            "statuses": statuses, "shops14": shops14}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True)
    ap.add_argument("--b", default="main.py")
    ap.add_argument("--seeds", type=int, default=64)
    ap.add_argument("--start-seed", type=int, default=0)
    ap.add_argument("--procs", type=int, default=max(1, cpu_count() - 1))
    ap.add_argument("--jsonl", default=None, help="write per-game rows here")
    ap.add_argument("--legs", default="mirror,tape,v6a,v12")
    args = ap.parse_args()

    legs = [x for x in POOL_OPPS if x[0] in args.legs.split(",")]
    seeds = range(args.start_seed, args.start_seed + args.seeds)

    jobs = []
    for name, opp in legs:
        if opp is None:
            for s in seeds:                      # A vs B, both orientations
                jobs.append((name, args.a, args.b, s))
                jobs.append((name, args.b, args.a, s))
        else:
            for s in seeds:                      # each vs opp, both orientations
                for me in (args.a, args.b):
                    jobs.append((name, me, opp, s))
                    jobs.append((name, opp, me, s))

    print(f"POD BATTERY: A={args.a} B={args.b} seeds={args.seeds} "
          f"from {args.start_seed} | {len(jobs)} games on {args.procs} procs",
          flush=True)

    results = []
    with Pool(processes=args.procs) as pool:
        for i, r in enumerate(pool.imap_unordered(_play, jobs, chunksize=1)):
            results.append(r)
            if (i + 1) % 50 == 0:
                print(f"  {i+1}/{len(jobs)} games done", flush=True)

    if args.jsonl:
        with open(args.jsonl, "w", encoding="utf-8") as f:
            for r in results:
                f.write(json.dumps(r) + "\n")

    # ---- summary ----
    def bank_of(r, path):
        return r["banks"][0] if r["p0"] == path else r["banks"][1]

    tot_dw = 0
    print()
    for name, opp in legs:
        rows = [r for r in results if r["leg"] == name]
        if opp is None:
            w = l = t = 0
            dm = 0.0
            for r in rows:
                a, b = bank_of(r, args.a), bank_of(r, args.b)
                if a > b: w += 1
                elif a < b: l += 1
                else: t += 1
                dm += a - b
            n = len(rows)
            print(f"  {name:<8} A {w}W-{l}L-{t}T of {n}, margin {dm/max(1,n):+,.0f} "
                  f"(ties excluded from dWins)")
            tot_dw += w - l
        else:
            # pair by (seed, orientation-of-me)
            def key(r, me):
                return (r["seed"], 0 if r["p0"] == me else 1)
            A = {key(r, args.a): bank_of(r, args.a) - bank_of(r, opp)
                 for r in rows if args.a in (r["p0"], r["p1"])}
            B = {key(r, args.b): bank_of(r, args.b) - bank_of(r, opp)
                 for r in rows if args.b in (r["p0"], r["p1"])}
            ks = sorted(set(A) & set(B))
            aw = sum(1 for k in ks if A[k] > 0)
            bw = sum(1 for k in ks if B[k] > 0)
            dbank = sum(A[k] - B[k] for k in ks) / max(1, len(ks))
            print(f"  {name:<8} A {aw}/{len(ks)} | B {bw}/{len(ks)} | "
                  f"dWins {aw-bw:+d} | dBank {dbank:+,.0f}")
            tot_dw += aw - bw
    bad = [r for r in results if any(s != "DONE" for s in r["statuses"])]
    print(f"\nTOTAL dWins {tot_dw:+d} over {len(results)} games"
          f"{' | NON-DONE GAMES: ' + str(len(bad)) if bad else ''}")

if __name__ == "__main__":
    main()
