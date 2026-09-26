"""ledger.py — obligation ledger for the day-10 takeover harness .

Plays <candidate> vs fork/c23s.py on one seed (candidate seat 0) and prints,
for each day from the takeover on: weeds created on crop tiles, animal
escapes, animals unfed at hour 23, crop tiles unwatered at hour 23
(advisory — the final step can still water), harvest actions executed,
hands employed, wages paid, and the money trajectory.  Outcomes (weeds,
escapes) are the ground truth; banks are secondary at this rung.

Usage: python tools/ledger.py <candidate.py> <seed> [label]
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

FIB_WAGE = {}


def wages(h):
    if h not in FIB_WAGE:
        a, b, tot = 1, 1, 0
        for _ in range(h):
            tot += a
            a, b = b, a + b
        FIB_WAGE[h] = tot
    return FIB_WAGE[h]


def main():
    cand, seed = sys.argv[1], int(sys.argv[2])
    label = sys.argv[3] if len(sys.argv) > 3 else os.path.basename(cand)
    from run_local import _silence_fds
    from kaggle_environments import make
    with _silence_fds():
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed})
        env.run([cand, r'fork\c23s.py'])
    steps = env.steps
    final = steps[-1]
    seat = 0
    obs240 = steps[240][0]["observation"]
    shops = obs240["town"].get("unlocked_shops", [])
    print(f"{label} vs c23s seed {seed}: {final[0].reward:,.0f} vs {final[1].reward:,.0f} "
          f"(margin {final[0].reward - final[1].reward:+,.0f})  statuses {[s.status for s in final]}")
    print(f"  d10 shops: {shops}  (gate: PET x{shops.count('PET_CAFE')})")
    print(f"{'d':>2} | {'hands':>5} {'wage':>4} | {'weeds':>5} {'escap':>5} | "
          f"{'unfed':>5} {'unwat':>5} | {'harv':>4} {'plt':>3} {'cSel':>4} | {'money':>8}")
    for day in range(10, 30):
        t_eve = day * 24 + 23
        t_next = (day + 1) * 24
        if t_eve >= len(steps):
            break
        eve = steps[t_eve][0]["observation"]["farms"][seat]
        nxt = (steps[t_next][0]["observation"]["farms"][seat]
               if t_next < len(steps) else None)
        weeds = escapes = 0
        if nxt is not None:
            for y in range(10):
                for x in range(10):
                    a, b = eve["tiles"][y][x], nxt["tiles"][y][x]
                    if (isinstance(a, dict) and a.get("kind") == "PLANT"
                            and isinstance(b, dict) and b.get("kind") == "WEED"):
                        weeds += 1
                    if (isinstance(a, dict) and "animal" in a
                            and isinstance(b, dict) and "animal" not in b):
                        escapes += 1
        unfed = sum(1 for row in eve["tiles"] for t in row
                    if isinstance(t, dict) and "animal" in t and not t.get("fed_today"))
        unwat = sum(1 for row in eve["tiles"] for t in row
                    if isinstance(t, dict) and t.get("kind") == "PLANT"
                    and not t.get("watered_today"))
        harv = plants = csell = 0
        for t in range(day * 24, min(day * 24 + 24, len(steps) - 1)):
            act = steps[t + 1][seat].get("action") or {}
            if isinstance(act, dict):
                for u in [act.get("farmer")] + list(act.get("hands") or []):
                    if isinstance(u, list) and u:
                        if u[0] == "HARVEST":
                            harv += 1
                        elif u[0] == "PLANT":
                            plants += 1
                for o in (act.get("market") or []):
                    if (isinstance(o, list) and len(o) > 2
                            and o[0] == "SELL" and o[1] == "CARROT"):
                        csell += int(o[2])
        nh = len(eve["hands"])
        print(f"{day:>2} | {nh:>5} {wages(nh):>4} | {weeds:>5} {escapes:>5} | "
              f"{unfed:>5} {unwat:>5} | {harv:>4} {plants:>3} {csell:>4} | "
              f"{eve.get('money', 0):>8,.0f}")


if __name__ == "__main__":
    main()
