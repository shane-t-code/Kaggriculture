#!/usr/bin/env python3
"""labor_trace.py —: per-unit-turn labor split, ours vs a target agent.

Runs paired local games and classifies EVERY unit-turn per seat:
  MOVE  = NORTH/SOUTH/EAST/WEST
  IDLE  = PASS (or missing op)
  CARRY = PICKUP / DROP / PLACE
  WORK  = everything else (WATER, HARVEST, PLANT, FEED, CARE,
          COLLECT_FERTILIZER, FERTILIZE, DIG, BUILD_*)
Prints the season split per seat, a per-phase (d0-9 / d10-19 / d20-29)
breakdown, and hands-alive-per-day, so we can see WHERE walking and
idling concentrate.  This is the campaign's opening measurement — the
target agent's split is the number to beat.

Usage: python tools/labor_trace.py <agentA> <agentB> <seed> [<seed> ...]
"""
import sys
from collections import Counter
from kaggle_environments import make

MOVES = {"NORTH", "SOUTH", "EAST", "WEST"}
CARRY = {"PICKUP", "DROP", "PLACE"}


def classify(op):
    if not isinstance(op, list) or not op or op[0] == "PASS":
        return "idle"
    if op[0] in MOVES:
        return "move"
    if op[0] in CARRY:
        return "carry"
    return "work"


def trace(a, b, seed):
    env = make("kaggriculture", configuration={"seed": seed}, debug=False)
    env.run([a, b])
    st = env.steps
    season = {0: Counter(), 1: Counter()}
    phase = {0: {}, 1: {}}
    units_alive = {0: Counter(), 1: Counter()}
    for si in range(1, len(st)):
        d = (si - 1) // 24
        ph = f"d{(d // 10) * 10}-{(d // 10) * 10 + 9}"
        for seat in (0, 1):
            act = st[si][seat].get("action") or {}
            ops = [act.get("farmer")] + list(act.get("hands") or [])
            units_alive[seat][d] = max(units_alive[seat][d], len(ops))
            for u in ops:
                c = classify(u)
                season[seat][c] += 1
                phase[seat].setdefault(ph, Counter())[c] += 1
    banks = [s.get("reward") for s in st[-1]]
    return season, phase, units_alive, banks


def pct(c):
    n = sum(c.values()) or 1
    return "  ".join(f"{k} {100*c[k]/n:4.1f}%" for k in ("work", "carry", "move", "idle"))


def main():
    a, b = sys.argv[1], sys.argv[2]
    seeds = [int(s) for s in sys.argv[3:]] or [0]
    tot = {0: Counter(), 1: Counter()}
    for seed in seeds:
        season, phase, units, banks = trace(a, b, seed)
        print(f"\n=== seed {seed}:  A={a.split('/')[-1]} {banks[0]:,.0f}  vs  "
              f"B={b.split('/')[-1]} {banks[1]:,.0f} ===")
        for seat, label in ((0, "A"), (1, "B")):
            tot[seat].update(season[seat])
            print(f"  {label} season: {pct(season[seat])}   "
                  f"(unit-turns {sum(season[seat].values()):,})")
            for ph in sorted(phase[seat]):
                print(f"     {ph}: {pct(phase[seat][ph])}")
    if len(seeds) > 1:
        print("\n=== TOTALS over", len(seeds), "seeds ===")
        for seat, label in ((0, "A"), (1, "B")):
            print(f"  {label}: {pct(tot[seat])}")


if __name__ == "__main__":
    main()
