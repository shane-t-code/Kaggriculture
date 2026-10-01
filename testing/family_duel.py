# FAMILY DUEL — one agent vs another, both seats, paired by seed.
# GATE (fixed before any game) used for every submission candidate: vs every
# opponent wins > losses; vs the agent it would replace, zero losses in cells
# where that agent vs itself would tie; 0 errors; max callback < 900 ms.
# Usage: python family_duel.py <agent> <opponent> <seed_start> <n_seeds>
#   <agent>/<opponent> = a name from ROSTER or a path to an agent .py file.
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True
from run_local import _silence_fds
with _silence_fds():
    from kaggle_environments import make
    from kaggle_environments.agent import get_last_callable

DATA = ROOT / "data"
ROSTER = {
    "final": ROOT / "agent" / "main.py",
}


class _Roster(dict):
    """Names from ROSTER, or any path to an agent file."""

    def __missing__(self, key):
        return Path(key)


FAM = _Roster(ROSTER)
GROW = DATA


def load(p):
    return get_last_callable(p.read_text(encoding="utf-8"), path=str(p))


def timed(fn, rec):
    def w(obs, cfg=None):
        t0 = time.perf_counter()
        try:
            return fn(obs, cfg)
        finally:
            rec[0] = max(rec[0], (time.perf_counter() - t0) * 1000)
    return w


def main():
    var, opp, s0, n = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    DATA.mkdir(exist_ok=True)
    out = DATA / f"duel_{Path(str(var)).stem}_vs_{Path(str(opp)).stem}.jsonl"
    with (DATA / "SEEDS.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps({"tool": "family_duel", "var": var, "opp": opp,
                            "start": s0, "count": n,
                            "ts": time.strftime("%Y-%m-%d %H:%M:%S")}) + "\n")
    done = set()
    if out.exists():
        for l in out.read_text(encoding="utf-8").splitlines():
            if l.strip():
                r = json.loads(l)
                done.add((r["seed"], r["pid"]))
    for seed in range(s0, s0 + n):
        for pid in (0, 1):
            if (seed, pid) in done:
                continue
            rec = [0.0]
            ags = [None, None]
            ags[pid] = timed(load(FAM[var]), rec)
            ags[1 - pid] = load(FAM[opp])
            with _silence_fds():
                env = make("kaggriculture",
                           configuration={"episodeSteps": 720, "seed": seed})
                env.run(ags)
            rw = [s.reward for s in env.steps[-1]]
            m = rw[pid] - rw[1 - pid]
            row = {"seed": seed, "pid": pid, "margin": m,
                   "res": "W" if m > 0 else "L" if m < 0 else "T",
                   "max_ms": round(rec[0]),
                   "statuses": [str(s.status) for s in env.steps[-1]]}
            with out.open("a", encoding="utf-8") as f:
                f.write(json.dumps(row) + "\n")
            print(json.dumps(row), flush=True)
    rows = [json.loads(l) for l in out.read_text(encoding="utf-8").splitlines()
            if l.strip()]
    w = sum(r["res"] == "W" for r in rows)
    l = sum(r["res"] == "L" for r in rows)
    t = sum(r["res"] == "T" for r in rows)
    print(f"{var} vs {opp}: W{w}-L{l}-T{t}  max {max(r['max_ms'] for r in rows)}ms",
          flush=True)


if __name__ == "__main__":
    main()
