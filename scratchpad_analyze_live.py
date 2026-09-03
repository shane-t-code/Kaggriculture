#!/usr/bin/env python3
"""Full live-replay decode: one detailed record per episode, no skimming.

Usage: python scratchpad_analyze_live.py replays/live_v45 replays/live_v43
Writes live_decode.jsonl (one record per episode) and prints a summary table.
"""
import json, os, sys, ast
from collections import Counter

ME = "Shane Thivaharraja"

SPECIES = ("GOOSE", "COW", "SHEEP")
CROPS = ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON")

def farm_fingerprint(farm):
    animals = Counter()
    crops = Counter()
    weeds = 0
    tiles = farm.get("tiles", [])
    for row in tiles:
        for t in row:
            if not isinstance(t, dict):
                continue
            k = t.get("kind")
            if k == "WEED":
                weeds += 1
            elif k == "PLANT":
                crops[t.get("crop")] += 1
            elif t.get("animal"):
                animals[t["animal"]] += 1
    quads = sum(1 for q in farm.get("purchased_quadrants", []) if q) if "purchased_quadrants" in farm else None
    return {"animals": dict(animals), "crops": dict(crops), "weeds": weeds,
            "quads": quads, "unlocked": sum(1 for row in tiles for t in row if t is not None or isinstance(t, dict))}

def analyze(path):
    rep = json.load(open(path, encoding="utf-8"))
    info = rep.get("info", {})
    teams = info.get("TeamNames")
    if isinstance(teams, str):
        teams = ast.literal_eval(teams)
    my = teams.index(ME)
    opp = 1 - my
    rewards = rep.get("rewards", [None, None])
    steps = rep["steps"]

    # bank trajectory per day (hour 23 snapshot)
    my_traj, opp_traj = [], []
    for d in range(30):
        si = min(d * 24 + 23, len(steps) - 1)
        obs = steps[si][0]["observation"]
        farms = obs["farms"]
        my_traj.append(farms[my].get("money", 0))
        opp_traj.append(farms[opp].get("money", 0))

    # divergence day: last day the gap was within 5k before running away
    final_gap = (rewards[my] or 0) - (rewards[opp] or 0)
    div_day = None
    for d in range(29, -1, -1):
        if abs(my_traj[d] - opp_traj[d]) < max(5000, abs(final_gap) * 0.15):
            div_day = d + 1
            break

    # farm fingerprints at day 12 and 20 and hands (max over day)
    def fp(day):
        si = min(day * 24 + 12, len(steps) - 1)
        farms = steps[si][0]["observation"]["farms"]
        return farm_fingerprint(farms[my]), farm_fingerprint(farms[opp])
    my12, opp12 = fp(12)
    my20, opp20 = fp(20)

    def max_hands(pi):
        best = 0
        for d in (5, 12, 20, 27):
            si = min(d * 24 + 12, len(steps) - 1)
            a = steps[si][pi].get("action") or {}
            best = max(best, len(a.get("hands") or []))
        return best

    # opponent opening: buys on day 0 (tape detector: 4 SHEEP+1 COW+5 MELON)
    opening = Counter()
    for si in range(0, 24):
        if si >= len(steps):
            break
        a = steps[si][opp].get("action") or {}
        for o in a.get("market") or []:
            if isinstance(o, list) and len(o) >= 2 and o[0] in ("BUY_ANIMAL", "BUY_SEED"):
                opening[f"{o[0][4:]}:{o[1]}"] += int(o[2]) if len(o) > 2 else 1

    # town: shops at day 14
    si14 = min(14 * 24, len(steps) - 1)
    shops = steps[si14][0]["observation"].get("town", {}).get("unlocked_shops", [])

    # statuses / overage
    statuses = rep.get("statuses")
    last = steps[-1]
    my_over = last[my].get("observation", {}).get("remainingOverageTime")
    if my_over is None:
        my_over = last[0]["observation"].get("remainingOverageTime")

    return {
        "episode": info.get("EpisodeId") or rep.get("id"),
        "seed": info.get("seed"),
        "opp_name": teams[opp],
        "my_seat": my,
        "my_bank": rewards[my], "opp_bank": rewards[opp],
        "win": bool(rewards[my] is not None and rewards[opp] is not None and rewards[my] > rewards[opp]),
        "tie": rewards[my] == rewards[opp],
        "margin": final_gap,
        "div_day": div_day,
        "my_traj": my_traj, "opp_traj": opp_traj,
        "my12": my12, "opp12": opp12, "my20": my20, "opp20": opp20,
        "my_hands": max_hands(my), "opp_hands": max_hands(opp),
        "opp_opening": dict(opening),
        "shops14": shops,
        "statuses": statuses,
        "my_overage_left": my_over,
        "n_steps": len(steps),
    }

def main():
    out = []
    for d in sys.argv[1:]:
        tag = os.path.basename(d)
        for f in sorted(os.listdir(d)):
            if not f.endswith(".json"):
                continue
            try:
                r = analyze(os.path.join(d, f))
                r["sub"] = tag
                out.append(r)
            except Exception as e:
                print(f"FAILED {f}: {e!r}")
    with open("live_decode.jsonl", "w") as fo:
        for r in out:
            fo.write(json.dumps(r) + "\n")
    # summary table
    for r in sorted(out, key=lambda r: (r["sub"], r["margin"])):
        o12 = r["opp12"]
        an = "".join(f"{s[0]}{n}" for s, n in sorted(o12["animals"].items()))
        cr = "".join(f"{c[0]}{n}" for c, n in sorted(o12["crops"].items()) if n)
        print(f"{r['sub']} ep{r['episode']} {'W' if r['win'] else ('T' if r['tie'] else 'L')} "
              f"{r['my_bank']:>9,.0f} vs {r['opp_bank']:>9,.0f} ({r['margin']:+9,.0f}) "
              f"div_d{str(r['div_day']):>4} hands {r['my_hands']}/{r['opp_hands']} "
              f"opp[{an}|{cr}] {r['opp_name'][:24]}")
    n = len(out); w = sum(1 for r in out if r["win"])
    print(f"\nTOTAL {n} episodes, {w}W-{n-w}L")

if __name__ == "__main__":
    main()
