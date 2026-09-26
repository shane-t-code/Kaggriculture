"""day_census.py — per-day operations census of one seat in a replay .

The phase-0 evidence for the crop-worker-day replanner: what does a winning
day actually consist of (ops, walking share, hires, wages, plant/harvest mix,
sells), day by day, versus ours.

Usage: python tools/day_census.py <replay.json> <seat> [label]
"""
import json, sys
from collections import Counter

WORK_OPS = ("PLANT", "WATER", "HARVEST", "FERTILIZE", "CARE", "FEED",
            "COLLECT_FERTILIZER", "DIG", "BUILD_COOP", "BUILD_PASTURE",
            "PLACE", "PICKUP", "DROP")
MOVES = ("NORTH", "SOUTH", "EAST", "WEST")


def fib_wages(h):
    # daily wage = fib sequence over hires present that day (engine :880 area)
    a, b, tot = 1, 1, 0
    for _ in range(h):
        tot += a
        a, b = b, a + b
    return tot


def main():
    path, seat = sys.argv[1], int(sys.argv[2])
    label = sys.argv[3] if len(sys.argv) > 3 else f"seat{seat}"
    rep = json.load(open(path, encoding="utf-8"))
    steps = rep["steps"]
    print(f"{label}: {path}  ({len(steps)} steps)")
    obs0 = steps[0][0]["observation"]
    print("shops final:", steps[-1][0]["observation"]["town"]["unlocked_shops"])
    hdr = (f"{'d':>2} | {'hands':>5} {'money':>8} | {'work':>4} {'walk':>4} {'pass':>4} "
           f"walk%% | {'plant':>18} | {'harv':>4} {'watr':>4} {'feed':>4} {'care':>4} | sells")
    print(hdr.replace('%%', '%'))
    for day in range(30):
        t0 = day * 24
        if t0 + 1 >= len(steps):
            break
        obs = steps[min(t0 + 12, len(steps) - 1)][0]["observation"]
        farm = obs["farms"][seat]
        money = farm.get("money", 0)
        nh = len(farm["hands"])
        ops = Counter()
        plants = Counter()
        sells = Counter()
        for t in range(t0, min(t0 + 24, len(steps) - 1)):
            act = steps[t + 1][seat].get("action") or {}
            if not isinstance(act, dict):
                continue
            units = [act.get("farmer")] + list(act.get("hands") or [])
            for u in units:
                if not isinstance(u, list) or not u:
                    ops["PASS"] += 1
                    continue
                op = u[0]
                if op in MOVES:
                    ops["MOVE"] += 1
                elif op in WORK_OPS:
                    ops[op] += 1
                    if op == "PLANT" and len(u) > 1:
                        plants[u[1]] += 1
                else:
                    ops["PASS"] += 1
            for o in (act.get("market") or []):
                if isinstance(o, list) and len(o) > 2 and o[0] == "SELL":
                    try:
                        sells[o[1]] += int(o[2])
                    except Exception:
                        pass
        work = sum(v for k, v in ops.items() if k not in ("MOVE", "PASS"))
        walk = ops["MOVE"]; pas = ops["PASS"]
        tot = max(1, work + walk + pas)
        pl = "+".join(f"{c[:3]}{n}" for c, n in plants.most_common()) or "-"
        sl = " ".join(f"{c[:3]}{n}" for c, n in sells.most_common(4)) or "-"
        print(f"{day:>2} | {nh:>5} {money:>8,.0f} | {work:>4} {walk:>4} {pas:>4} "
              f"{100*walk//tot:>4}% | {pl:>18} | {ops['HARVEST']:>4} {ops['WATER']:>4} "
              f"{ops['FEED']:>4} {ops['CARE']:>4} | {sl}")


if __name__ == "__main__":
    main()
