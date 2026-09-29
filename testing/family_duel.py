# FAMILY DUEL  — variant vs each family member, both seats.
# PREDECLARED gate (before any game): for dso to be a submission candidate:
#   vs every family opponent: wins > losses; vs dtrw (the live agent it would
#   replace): ZERO losses in cells where dtrw-vs-dtrw would tie; 0 errors;
#   max callback < 900ms. Then a tape no-harm screen before any submit talk.
# Usage: python family_duel.py <variant> <opp> <seed_start> <n_seeds>
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
FAM = {
    "dtrw": GROW / "variants" / "dtrw.py",
    "dt": GROW / "variants" / "dt.py",
    "dso": GROW / "variants" / "dso.py",
    "dso2": GROW / "variants" / "dso2.py",
    "dsl": GROW / "variants" / "dsl.py",
    "ca22": Path(r"C:\Kaggriculture\work\build_a\s1009r_ca22.py"),
    "s1009r": Path(r"C:\Kaggriculture\work\build_a\step1009r.py"),
    "candidate": Path(r"C:\Kaggriculture\work\\review10\candidate.py"),
}


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
    out = GROW / f"fam_{var}_vs_{opp}.jsonl"
    with (GROW / "SEEDS.jsonl").open("a", encoding="utf-8") as f:
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
