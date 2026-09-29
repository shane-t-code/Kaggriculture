# DT MIRROR DUELS — dt vs candidate, both seats, per-callback timing.
# Mirror games are deterministic per (seed, matchup, seat): each cell is a
# direct measurement, no census control needed (candidate-vs-candidate is a
# structural tie). Gates in build_dt.py header: (W-L)>0, ZERO losses, every
# callback of BOTH agents < 900ms.
# Usage: python dt_duel.py <seeds_json>   Output: dt_duel_rows.jsonl (resumable)
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, r"C:\Kaggriculture")
sys.dont_write_bytecode = True
from run_local import _silence_fds
with _silence_fds():
    from kaggle_environments import make
    from kaggle_environments.agent import get_last_callable

GROW = Path(r"C:\Kaggriculture\work\build_a\grow")
CAND = Path(r"C:\Kaggriculture\work\\review10\candidate.py")
OUT = GROW / "dt_duel_rows.jsonl"

def load(p):
    return get_last_callable(p.read_text(encoding="utf-8"), path=str(p))

def timed(fn, rec):
    def wrapped(obs, cfg=None):
        t0 = time.perf_counter()
        try:
            return fn(obs, cfg)
        finally:
            ms = (time.perf_counter() - t0) * 1000
            if ms > rec["max_ms"]:
                rec["max_ms"] = ms
                rec["max_step"] = int(obs["step"])
    return wrapped

def main():
    seeds = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    done = set()
    if OUT.exists():
        for line in OUT.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                done.add((r["seed"], r["pid"]))
    for seed in seeds:
        for pid in (0, 1):
            if (seed, pid) in done:
                continue
            rec_dt = {"max_ms": 0.0, "max_step": -1}
            rec_c = {"max_ms": 0.0, "max_step": -1}
            agents = [None, None]
            agents[pid] = timed(load(GROW / "variants" / "dt.py"), rec_dt)
            agents[1 - pid] = timed(load(CAND), rec_c)
            t0 = time.time()
            with _silence_fds():
                env = make("kaggriculture",
                           configuration={"episodeSteps": 720, "seed": seed})
                env.run(agents)
            last = env.steps[-1]
            rewards = [s.reward for s in last]
            m = (None if None in rewards
                 else rewards[pid] - rewards[1 - pid])
            row = {"seed": seed, "pid": pid, "margin": m,
                   "res": "W" if m and m > 0 else "L" if m and m < 0 else "T",
                   "dt_max_ms": round(rec_dt["max_ms"]),
                   "dt_max_step": rec_dt["max_step"],
                   "cand_max_ms": round(rec_c["max_ms"]),
                   "statuses": [str(s.status) for s in last],
                   "secs": round(time.time() - t0, 1)}
            with OUT.open("a", encoding="utf-8") as f:
                f.write(json.dumps(row) + "\n")
            print(json.dumps(row), flush=True)
    rows = [json.loads(l) for l in OUT.read_text(encoding="utf-8").splitlines()
            if l.strip()]
    w = sum(r["res"] == "W" for r in rows)
    l = sum(r["res"] == "L" for r in rows)
    t = sum(r["res"] == "T" for r in rows)
    print(f"DT DUELS: W{w}-L{l}-T{t}  max dt callback "
          f"{max(r['dt_max_ms'] for r in rows)}ms", flush=True)

if __name__ == "__main__":
    main()
