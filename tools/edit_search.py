#!/usr/bin/env python3
"""Automated edit-search over the pipe16 tape on the kagsim C++ engine.

Menu = append-constant overrides (the v106a trick: layers share module
globals) + optional glutgate layer. Each config plays SEEDS seeds x both
seats vs the opponent on kagsim; margins vs the pipe16 baseline on the same
seeds decide. Survivors must later re-verify in the REAL engine (py_ab).

Usage: python tools/edit_search.py [--seeds 10] [--start 200] [--procs 11]
Writes results/edit_search.jsonl (append) + prints a ranked summary.
Exploration seeds only — never the gate ledger.
"""
import sys, os, json, itertools, tempfile, statistics
from multiprocessing import Pool

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

BASE = os.path.join(ROOT, "external", "pipe16_main.py")
OPP = os.path.join(ROOT, "external", "agents", "tetsutani__demand-preserving.py")
GLUT = os.path.join(ROOT, "fork", "glutgate_layer.py")
OUT = os.path.join(ROOT, "results", "edit_search.jsonl")

# ---- the menu: None = leave at default ----
MENU = {
    "_ALT_MODE": [None, "'EarlyCycle'", "'TomatoInsteadOfCow'"],
    "_CA_MARGIN": [None, "-15.0", "-25.0"],
    "_CA_FEED_DAYS": [None, "2"],
    "_OR2_SLOT_MARGIN": [None, "10.0", "30.0"],
    "GLUTGATE": [None, "on"],          # append the glutgate layer
    "_GG_TRICKLE": [None, "12"],       # only meaningful with GLUTGATE on
}


def configs():
    keys = list(MENU)
    for combo in itertools.product(*(MENU[k] for k in keys)):
        cfg = {k: v for k, v in zip(keys, combo) if v is not None}
        if "_GG_TRICKLE" in cfg and "GLUTGATE" not in cfg:
            continue
        # limit to <=2 simultaneous edits tonight (interpretable results)
        n_edits = len([k for k in cfg if k != "_GG_TRICKLE"])
        if n_edits == 0 or n_edits > 2:
            continue
        yield cfg


def build(cfg, tmpdir, idx):
    src = open(BASE, "rb").read()
    if "GLUTGATE" in cfg:
        src += b"\n\n" + open(GLUT, "rb").read()
    tail = "\n\n# edit_search config\n"
    for k, v in cfg.items():
        if k == "GLUTGATE":
            continue
        tail += f"{k} = {v}\n"
    path = os.path.join(tmpdir, f"cand_{idx}.py")
    with open(path, "wb") as f:
        f.write(src + tail.encode())
    return path


def play(args):
    path, seed = args
    import importlib.util, kagsim
    res = []
    for seat_a in (0, 1):
        def load(p, nm):
            spec = importlib.util.spec_from_file_location(nm, p)
            m = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
            return m.agent
        try:
            a = load(path, f"a{seed}{seat_a}")
            b = load(OPP, f"b{seed}{seat_a}")
            g = kagsim.Game(seed)
            ag = (a, b) if seat_a == 0 else (b, a)
            while not g.done:
                g.step(ag[0](g.observe(0)), ag[1](g.observe(1)))
            res.append(g.reward(seat_a) - g.reward(1 - seat_a))
        except Exception as e:
            res.append(None)
    return res


def main():
    args = sys.argv[1:]
    n_seeds = int(args[args.index("--seeds") + 1]) if "--seeds" in args else 10
    start = int(args[args.index("--start") + 1]) if "--start" in args else 200
    procs = int(args[args.index("--procs") + 1]) if "--procs" in args else 11
    seeds = list(range(start, start + n_seeds))
    tmpdir = tempfile.mkdtemp(prefix="editsearch_")
    cands = [({}, BASE)] + [(c, build(c, tmpdir, i))
                            for i, c in enumerate(configs())]
    print(f"{len(cands)} configs (incl. baseline) x {n_seeds} seeds x 2 seats "
          f"vs tetsutani on kagsim")
    rows = []
    with Pool(procs) as pool:
        for cfg, path in cands:
            jobs = [(path, s) for s in seeds]
            out = pool.map(play, jobs)
            margins = [m for pair in out for m in pair if m is not None]
            fails = sum(1 for pair in out for m in pair if m is None)
            mean = statistics.mean(margins) if margins else float("-inf")
            rows.append((mean, cfg, len(margins), fails))
            with open(OUT, "a", encoding="utf-8") as f:
                f.write(json.dumps({"cfg": cfg, "mean": mean,
                                    "n": len(margins), "fails": fails,
                                    "seeds": [start, start + n_seeds]}) + "\n")
            print(f"  mean {mean:+9,.0f} n={len(margins)} fails={fails}  {cfg}",
                  flush=True)
    rows.sort(key=lambda r: -r[0])
    base_mean = next(r[0] for r in rows if r[1] == {})
    print(f"\nbaseline pipe16: {base_mean:+,.0f}\ntop 8 vs baseline:")
    for mean, cfg, n, fails in rows[:8]:
        print(f"  {mean - base_mean:+8,.0f} rel | {mean:+9,.0f} abs | {cfg}")


if __name__ == "__main__":
    main()
