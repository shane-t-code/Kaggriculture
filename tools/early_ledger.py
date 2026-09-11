"""early_ledger.py — per-day money / seeds / herd / STR tiles for seat 0 (or ME).
Usage: python tools/early_ledger.py <replay_path> [days]"""
import json, sys

rep = json.load(open(sys.argv[1], encoding="utf-8"))
days = int(sys.argv[2]) if len(sys.argv) > 2 else 12
steps = rep["steps"]
print("day | money@end | seedsSTR | COW SHEEP | STRtiles | hands")
for day in range(days):
    si = min(day * 24 + 23, len(steps) - 1)
    obs = steps[si][0]["observation"]
    farm = obs["farms"][0]
    priv = obs["private"]
    seeds = priv["seeds"].get("STRAWBERRY", 0)
    cows = sheep = strt = 0
    for row in farm["tiles"]:
        for t in row:
            if isinstance(t, dict):
                if t.get("animal") == "COW":
                    cows += 1
                elif t.get("animal") == "SHEEP":
                    sheep += 1
                elif t.get("kind") == "PLANT" and t.get("crop") == "STRAWBERRY":
                    strt += 1
    print(f" {day:>2} | {farm['money']:>9,.0f} | {seeds:>4} | {cows:>3} {sheep:>4} "
          f"| {strt:>3} | {len(farm.get('hands', []))}")
