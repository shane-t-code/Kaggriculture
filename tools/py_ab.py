"""py_ab.py — parallel UNPINNED A/B on the REAL python engine .

Natural shop draws, fresh seeds, both seats, multiprocessing.  Appends one
JSON line per game to --out so capped chunks accumulate; summarize with
tools/py_ab_sum.py.

Usage (chunked under the 10-min background cap):
  python tools/py_ab.py --a main.py --b versions/pool_band_killer.py
      --seeds 20 --start-seed 519 --tag v70c --out results/ab_v74d_gate.jsonl
"""
import argparse, json, os, sys
from multiprocessing import Pool

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

def play_one(job):
    a, b, seed = job
    from run_local import play, _silence_fds
    with _silence_fds():
        ra, rb, _ = play(a, b, seed)
    return {"seed": seed, "a": ra, "b": rb}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True)
    ap.add_argument("--b", required=True)
    ap.add_argument("--seeds", type=int, required=True)
    ap.add_argument("--start-seed", type=int, required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--procs", type=int, default=max(1, (os.cpu_count() or 4) - 1))
    args = ap.parse_args()

    jobs = [(args.a, args.b, s)
            for s in range(args.start_seed, args.start_seed + args.seeds)]
    with Pool(args.procs) as pool:
        rows = pool.map(play_one, jobs)
    with open(args.out, "a", encoding="utf-8") as fh:
        for r in rows:
            r["tag"] = args.tag
            fh.write(json.dumps(r) + "\n")
    ms = [r["a"] - r["b"] for r in rows]
    print(f"{args.tag}: {len(rows)} seeds done "
          f"({args.start_seed}-{args.start_seed+args.seeds-1}); "
          f"mean margin {sum(ms)/len(ms):+,.0f}")

if __name__ == "__main__":
    main()
