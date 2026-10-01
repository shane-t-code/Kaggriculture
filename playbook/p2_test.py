# MGX TEST — the borrowed-playbook agent vs a real opponent on
# FRESH natural worlds, both seats, paired by seed.  Margin and W-L first.
# Usage: python -X utf8 p2_test.py <label> <opponent_path> <seed_start> <n_seeds> <procs>
import json
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path

R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R))
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.dont_write_bytecode = True
OUT = R / "data" / "playbook_rows.jsonl"


def run(job):
    label, opp, seed, seat = job
    from run_local import _silence_fds
    with _silence_fds():
        from kaggle_environments import make
    import importlib
    mgx = importlib.import_module("mgx")
    mgx._STATE.clear()
    mod = importlib.import_module(os.environ.get("MGX_MODULE", "mgx"))
    pair = [None, None]
    pair[seat] = mod.agent
    pair[1 - seat] = opp
    t0 = time.time()
    with _silence_fds():
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed})
        env.run(pair)
        fin = env.toJSON()["steps"][-1]
    st = mgx._STATE.get("mgx")
    shops = fin[0]["observation"]["town"]["unlocked_shops"]
    log = st.log if st else []
    return {"label": label, "opp": Path(opp).stem, "seed": seed, "seat": seat,
            "us": fin[seat]["reward"], "them": fin[1 - seat]["reward"],
            "status": [s["status"] for s in fin], "shops": shops,
            "switches": [l for l in log if l[1] == "switch"],
            "defers": len([l for l in log if l[1] == "defer"]),
            "errors": [l for l in log if l[1] == "error"][:3],
            "final_match": st.match if st else None,
            "secs": round(time.time() - t0)}


def main():
    label, opp, s0, n, procs = (sys.argv[1], sys.argv[2], int(sys.argv[3]),
                                int(sys.argv[4]), int(sys.argv[5]))
    with open(R / "data" / "SEEDS.jsonl", "a",
              encoding="utf-8") as fh:
        fh.write(json.dumps({"tool": "mgx_p2_test", "label": label,
                             "opp": Path(opp).stem, "start": s0, "count": n,
                             "ts": time.strftime("%Y-%m-%d %H:%M:%S")}) + "\n")
    jobs = [(label, opp, s0 + i, seat) for i in range(n) for seat in (0, 1)]
    rows = []
    with Pool(procs) as pool:
        for r in pool.imap_unordered(run, jobs):
            rows.append(r)
            with open(OUT, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(r) + "\n")
            print(f"{r['label']} seed {r['seed']} seat {r['seat']} | us "
                  f"{r['us']:>9,.0f} them {r['them']:>9,.0f} margin "
                  f"{r['us'] - r['them']:>+9,.0f} | match {r['final_match']} "
                  f"switches {len(r['switches'])} defers {r['defers']} "
                  f"errors {len(r['errors'])} {r['status']} {r['secs']}s",
                  flush=True)
    m = sorted(r["us"] - r["them"] for r in rows)
    w = sum(x > 0 for x in m)
    print(f"\n{label} vs {Path(opp).stem}: W{w}-L{len(m) - w}  median margin "
          f"{m[len(m) // 2]:+,.0f}  mean {sum(m) / len(m):+,.0f}  "
          f"worst {m[0]:+,.0f}  best {m[-1]:+,.0f}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
