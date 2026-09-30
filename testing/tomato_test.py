# TOMATO-CHECK TEST  — dtrwt (tomato project opens if EITHER the
# value check OR the original rule says yes) vs an opponent, paired with
# dtrw in the same world, both seats.  Only cells where the two checks
# DISAGREE (base=yes, value=no) can differ; those are the measured cells.
# PREDECLARED (from EXP 199b): on disagreeing cells wins > losses vs dtrw
# in the same world, mean margin change > 0, no single loss worse than -6k,
# 0 errors, every move < 900ms.  Falsifier: opened games trail at the end.
# Usage: python -X utf8 tomato_test.py <opp> <seed_start> <n_seeds> <procs>
import json, sys, time
from multiprocessing import Pool
from pathlib import Path
sys.path.insert(0, r"C:\Kaggriculture"); sys.dont_write_bytecode = True
GROW = Path(r"C:\Kaggriculture\work\build_a\grow")
OUT = GROW / "tomato_rows.jsonl"

def pinned_town(seed):
    """A town with exactly 3 tomato-buying shops among the first 6 (the pattern
    the fix is for); other slots random; deterministic per seed."""
    import random
    rng = random.Random(seed * 7 + 1)
    others = ["BAKERY", "BRUNCH_SPOT", "YARN_STORE", "ICE_CREAM_SHOP", "PET_CAFE", "SMOOTHIE_SHOP"]
    slots = rng.sample(range(6), 3)
    seq = []
    for i in range(8):
        if i in slots:
            seq.append(rng.choice(["PIZZA_SHOP", "FARMERS_MARKET"]))
        else:
            seq.append(rng.choice(others + ["PIZZA_SHOP", "FARMERS_MARKET"]) if i >= 6 else rng.choice(others))
    return seq


def game(var, opp, seed, pid):
    from run_local import _silence_fds
    with _silence_fds():
        from kaggle_environments import make
        from kaggle_environments.agent import get_last_callable
    sys.path.insert(0, str(GROW))
    from family_duel import FAM, load, timed
    FAM["dtrwt"] = GROW / "variants" / "dtrwt.py"
    FAM["majkel"] = Path(r"C:\Kaggriculture") / "work" / "" / "review9" / "majkel.py"
    rec = [0.0]
    fn = load(FAM[var])
    ags = [None, None]; ags[pid] = timed(fn, rec); ags[1 - pid] = load(FAM[opp])
    import os
    pin = None
    if os.environ.get("TOMATO_PIN") == "1":
        from tools import shop_pin
        pin = pinned_town(seed); shop_pin.install(pin)
    try:
        with _silence_fds():
            env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}); env.run(ags)
    finally:
        if pin:
            shop_pin.uninstall()
    rw = [s.reward for s in env.steps[-1]]
    rep = fn.__globals__.get("_CXTB_REPORT", {})
    feats = rep.get("cxtb_features", [])
    return {"var": var, "opp": opp, "seed": seed, "pid": pid, "us": rw[pid], "them": rw[1 - pid],
            "margin": rw[pid] - rw[1 - pid], "max_ms": round(rec[0]),
            "statuses": [str(s.status) for s in env.steps[-1]],
            "feat": feats[-1] if feats else None, "pin": pin}

def job(j):
    return game(*j)

def main():
    opp, s0, n, procs = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    with (GROW / "SEEDS.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps({"tool": "tomato_test", "opp": opp, "start": s0, "count": n, "ts": time.strftime("%Y-%m-%d %H:%M:%S")}) + "\n")
    import os
    seeds = [int(x) for x in os.environ["TOMATO_SEEDS"].split(",")] if os.environ.get("TOMATO_SEEDS") else list(range(s0, s0 + n))
    jobs = [("dtrwt", opp, s, p) for s in seeds for p in (0, 1)]
    fired = []
    with Pool(procs) as pool:
        for r in pool.imap_unordered(job, jobs):
            with OUT.open("a", encoding="utf-8") as f: f.write(json.dumps(r) + "\n")
            ft = r["feat"] or {}
            tag = "FIRED" if ft.get("base") and not (ft.get("revenue", 0) >= 9000) else "same"
            if tag == "FIRED" or os.environ.get("TOMATO_SEEDS"): fired.append((opp, r["seed"], r["pid"]))
            print(f"dtrwt vs {opp} seed {r['seed']} seat {r['pid']} margin {r['margin']:>+9,.0f} {tag} feat {ft} {r['max_ms']}ms {r['statuses']}", flush=True)
    print(f"\n{len(fired)} fired cells of {len(jobs)} -> running dtrw controls on those", flush=True)
    ctl = [("dtrw", o, s, p) for o, s, p in fired]
    with Pool(procs) as pool:
        for r in pool.imap_unordered(job, ctl):
            with OUT.open("a", encoding="utf-8") as f: f.write(json.dumps(r) + "\n")
            print(f"dtrw  vs {opp} seed {r['seed']} seat {r['pid']} margin {r['margin']:>+9,.0f} (control)", flush=True)

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8"); main()
