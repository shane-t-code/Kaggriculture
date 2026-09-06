#!/usr/bin/env python3
"""Land-slip diagnosis: for each live replay, find the turn we issue BUY_LAND,
the day each quadrant count changes, and cash levels around the day-6 window.
Usage: python land_probe.py replays/live_v54k [replays/live_v52b]"""
import json, os, sys, ast
from collections import Counter

ME = "Shane Thivaharraja"

def analyze(path):
    rep = json.load(open(path, encoding="utf-8"))
    info = rep.get("info", {})
    teams = info.get("TeamNames")
    if isinstance(teams, str):
        teams = ast.literal_eval(teams)
    my = teams.index(ME)
    steps = rep["steps"]

    # our BUY_LAND turns (action of seat my)
    land_turns = []
    for si, st in enumerate(steps):
        a = st[my].get("action") or {}
        for o in a.get("market") or []:
            if isinstance(o, list) and o and o[0] == "BUY_LAND":
                land_turns.append(si)

    # quadrant count per day (from seat-0 obs, farms[my])
    def quads(si):
        f = steps[min(si, len(steps)-1)][0]["observation"]["farms"][my]
        uq = f.get("unlocked_quadrants")
        if uq is not None:
            return len(uq)
        pq = f.get("purchased_quadrants")
        if pq is not None:
            return sum(1 for q in pq if q)
        return None
    q_day = {}
    prev = quads(0)
    for d in range(30):
        q = quads(d * 24 + 23)
        if q != prev:
            q_day[q] = d
            prev = q

    # morning cash days 4-11 + herd size
    cash = {}
    herd = {}
    for d in range(4, 12):
        si = min(d * 24, len(steps) - 1)
        f = steps[si][0]["observation"]["farms"][my]
        cash[d] = f.get("money")
        n = 0
        for row in f.get("tiles", []):
            for t in row:
                if isinstance(t, dict) and t.get("animal"):
                    n += 1
        herd[d] = n

    return {
        "ep": info.get("EpisodeId") or os.path.basename(path),
        "land_turns": land_turns,
        "land_days": [t // 24 for t in land_turns],
        "q_change_days": q_day,
        "cash": cash, "herd": herd,
    }

def main():
    rows = []
    for d in sys.argv[1:]:
        for f in sorted(os.listdir(d)):
            if f.endswith(".json"):
                try:
                    rows.append(analyze(os.path.join(d, f)))
                except Exception as e:
                    print(f"FAIL {f}: {e!r}")
    day2_hist = Counter()
    day3_hist = Counter()
    for r in rows:
        q2 = r["q_change_days"].get(2)
        q3 = r["q_change_days"].get(3)
        day2_hist[q2] += 1
        day3_hist[q3] += 1
        c = r["cash"]
        print(f"ep{r['ep']} q2_day={q2} q3_day={q3} buy_turturns_days={r['land_days'][:4]} "
              f"cash d5={c.get(5)} d6={c.get(6)} d7={c.get(7)} d8={c.get(8)} d9={c.get(9)} "
              f"herd d6={r['herd'].get(6)}")
    print("\nQ2 purchase-day histogram:", dict(sorted(day2_hist.items(), key=lambda x: (x[0] is None, x[0]))))
    print("Q3 purchase-day histogram:", dict(sorted(day3_hist.items(), key=lambda x: (x[0] is None, x[0]))))

if __name__ == "__main__":
    main()
