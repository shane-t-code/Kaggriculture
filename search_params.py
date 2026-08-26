#!/usr/bin/env python3
"""search_params.py — overnight coordinate-descent over main.py's tuned constants.

Why: every hand-designed mechanism card is closed (PLAN.md experiments 20-29);
the remaining path to +15-25k median bank includes tuning the ~10 constants we
set by judgment, not measurement.  Local games are free; this drives thousands.

Method: coordinate descent.  For each parameter in PARAMS (in order), patch
main.py's source with each candidate value, evaluate PAIRED vs two distinct
opponents (v6a, v12b) on a fixed seed list, and keep the value only if it beats
the current best by the acceptance rule.  The winning source becomes the base
for the next parameter.  Two sweeps by default.

Anti-overfitting: search seeds (100+) are DISJOINT from promotion seeds (0-31).
The final config is written to versions/vSEARCH.py and MUST then pass the
standard promotion protocol (pool_ab on seeds 0-15, both batches) before it
touches main.py.  The search result is a candidate, not a promotion.

Acceptance rule: dWins > 0, or dWins == 0 and mean dBank > +300 (occupancy
changes make the town draw drift, so small bank deltas are noise).

Usage:
    ./.venv/Scripts/python.exe search_params.py             # full search
    ./.venv/Scripts/python.exe search_params.py --sweeps 1  # quicker
Resumable: state in search_state.json (delete it to start fresh).
"""
from __future__ import annotations
import argparse, ast, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "main.py")
WORK = os.path.join(HERE, "versions", "vSEARCH_work.py")   # patched candidate
OUT = os.path.join(HERE, "versions", "vSEARCH.py")         # best config found
STATE = os.path.join(HERE, "search_state.json")
OPPONENTS = ["versions/v6a.py", "versions/v12b.py"]
# 24 seeds/eval, not 8: the first run's winner (TARGET_HANDS=7 +
# WHEAT_FACTORY_DAY=15, "32/32") was REJECTED at 64 held-out seeds — 8-seed
# evals cannot measure occupancy-changing constants because the changed farm
# consumes RNG differently and every town draw shifts (seed-20 autopsy: same
# seed rolled 4 milk outlets for baseline, 2 for the candidate — a 47k swing).
SEEDS = 24
START_SEED = 100    # disjoint from promotion seeds 0-31 (held out)

# (name, regex with ONE capture group ending right before the number, values).
# First value listed = current baseline (documentation only; the true baseline
# is whatever main.py holds).
PARAMS = [
    ("TARGET_HANDS",       r"(^TARGET_HANDS = )\d+",                      [6, 5, 7]),
    ("WHEAT_FACTORY_DAY",  r"(^WHEAT_FACTORY_DAY = )\d+",                 [18, 15, 16, 20]),
    ("WHEAT_FACTORY_CAP",  r"(^WHEAT_FACTORY_CAP = )\d+",                 [45, 35, 55]),
    ("STR_CAP",            r'("STRAWBERRY": \{"cost": 100[^\n]*"cap": )\d+', [35, 30, 40]),
    ("STR_LAST_PLANT",     r'("STRAWBERRY": \{"cost": 100[^\n]*"last_plant": )\d+', [17, 15, 19]),
    ("CARROT_CAP",         r'("CARROT":\s+\{"cost": 20[^\n]*"cap": )\d+', [12, 8, 16]),
    ("CARE_SKIP_PRICE",    r"(^CARE_SKIP_PRICE = )\d+",                   [15, 10, 25]),
    ("CROP_SKIP_PRICE",    r"(^CROP_SKIP_PRICE = )\d+",                   [15, 10, 25]),
    ("UNLOAD_AT",          r"(^UNLOAD_AT = )\d+",                         [8, 6, 10]),
    ("STR_MIN_PRICE",      r'("STRAWBERRY":\s+\(4, )\d+(?=, 28\))',       [100, 85, 110]),
]


def patch(src: str, name: str, pattern: str, value: int) -> str:
    new, n = re.subn(pattern, lambda m: m.group(1) + str(value), src, flags=re.M)
    if n != 1:
        raise RuntimeError(f"pattern for {name} matched {n} times (want exactly 1)")
    return new


def run_games(agent_path: str, opp: str):
    """[(seed, seat, my_bank, opp_bank)] via run_local.py."""
    cmd = [sys.executable, os.path.join(HERE, "run_local.py"), "--a", agent_path,
           "--b", opp, "--seeds", str(SEEDS), "--start-seed", str(START_SEED)]
    out = subprocess.run(cmd, capture_output=True, text=True, cwd=HERE).stdout
    games = []
    for line in out.splitlines():
        m = re.match(r"\s+seed\s+(\d+)\s+seat0: A\s+([\d,]+) vs B\s+([\d,]+)"
                     r"\s+seat1: A\s+([\d,]+) vs B\s+([\d,]+)", line)
        if m:
            s = int(m.group(1))
            v = [int(x.replace(",", "")) for x in m.groups()[1:]]
            games.append((s, 0, v[0], v[1]))
            games.append((s, 1, v[2], v[3]))
    if len(games) != SEEDS * 2:
        raise RuntimeError(f"run_local returned {len(games)} games (want {SEEDS*2}); "
                           f"output head: {out[:400]!r}")
    return games


def evaluate(src: str, label: str, cache: dict):
    """Score a candidate source: total wins and mean bank across both opponents."""
    if label in cache:
        return tuple(cache[label])
    with open(WORK, "w", encoding="utf-8") as f:
        f.write(src)
    ast.parse(src)  # refuse to burn 30 games on a syntax error
    wins = 0
    banks = []
    for opp in OPPONENTS:
        for _, _, mine, theirs in run_games(WORK, opp):
            wins += 1 if mine > theirs else 0
            banks.append(mine)
    score = (wins, sum(banks) / len(banks))
    cache[label] = list(score)
    return score


def accept(cand, best):
    # Strict: occupancy noise means SE of mean bank is ~1k even at 96
    # games/eval.  Require a wins edge of >= 3, or equal wins and a bank edge
    # comfortably above noise.
    return cand[0] >= best[0] + 3 or (cand[0] >= best[0] and cand[1] > best[1] + 1500)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sweeps", type=int, default=2)
    args = ap.parse_args()

    state = {"seeds": SEEDS, "values": {}, "cache": {}}
    if os.path.exists(STATE):
        loaded = json.load(open(STATE, encoding="utf-8"))
        if loaded.get("seeds") == SEEDS:
            state = loaded
            print(f"resuming: {len(state['cache'])} evals cached")
        else:
            print(f"discarding stale state (was {loaded.get('seeds')} seeds/eval, "
                  f"now {SEEDS}) — scores are not comparable across eval sizes")

    base_src = open(BASE, encoding="utf-8").read()
    values = state["values"]        # name -> chosen value (only when != baseline)
    cache = state["cache"]

    def build(vals):
        src = base_src
        for name, pattern, _ in PARAMS:
            if name in vals:
                src = patch(src, name, pattern, vals[name])
        return src

    def key(vals):
        return json.dumps(vals, sort_keys=True) or "baseline"

    def save():
        json.dump(state, open(STATE, "w", encoding="utf-8"), indent=1)

    best = evaluate(build(values), key(values), cache)
    save()
    print(f"start config {key(values)}: wins={best[0]}/{SEEDS*2*len(OPPONENTS)} "
          f"mean_bank={best[1]:,.0f}")

    for sweep in range(args.sweeps):
        print(f"\n=== sweep {sweep + 1}/{args.sweeps} ===")
        for name, pattern, vals in PARAMS:
            current = values.get(name)
            for v in vals:
                if v == current or (current is None and v == vals[0]):
                    continue
                trial = dict(values)
                if v == vals[0]:
                    trial.pop(name, None)   # back to baseline value
                else:
                    trial[name] = v
                score = evaluate(build(trial), key(trial), cache)
                save()
                mark = ""
                if accept(score, best):
                    values.clear(); values.update(trial)
                    best = score
                    mark = "  <-- KEPT"
                print(f"  {name}={v}: wins={score[0]} bank={score[1]:,.0f}{mark}")
        save()

    final_src = build(values)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(final_src.replace(
            "STATUS: v17", "STATUS: vSEARCH (from search_params.py) — base v17", 1))
    print(f"\nBEST CONFIG: {key(values)}")
    print(f"  wins={best[0]}/{SEEDS*2*len(OPPONENTS)}  mean_bank={best[1]:,.0f}")
    print(f"  written to {OUT}")
    print("  NEXT: pool_ab.py --a versions/vSEARCH.py --seeds 8 --start-seed 0 AND")
    print("        --start-seed 8 (promotion seeds are held out from the search).")


if __name__ == "__main__":
    main()
