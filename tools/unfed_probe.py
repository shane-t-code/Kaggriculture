"""unfed_probe.py — per-day unfed-animal fingerprint for seat 0 from a replay.
The standing promotion gate : unfed% must be checked AT BOOM SCALE
(12-16 animals), not just the ~13-animal default.
Usage: python tools/unfed_probe.py <replay_path>"""
import json, sys

rep = json.load(open(sys.argv[1], encoding="utf-8"))
steps = rep["steps"]
tot_days = tot_unfed = 0
peak = 0
print("day | animals | unfed@23h | unfed%")
for day in range(30):
    si = min(day * 24 + 23, len(steps) - 1)
    farm = steps[si][0]["observation"]["farms"][0]
    n = unfed = 0
    for row in farm["tiles"]:
        for t in row:
            if isinstance(t, dict) and "animal" in t:
                n += 1
                if not t.get("fed_today", False):
                    unfed += 1
    if n:
        tot_days += n
        tot_unfed += unfed
        peak = max(peak, n)
        flag = "  <-- UNFED" if unfed else ""
        print(f" {day:>2} |   {n:>3}   |   {unfed:>3}    | {unfed/n:>5.0%}{flag}")
print(f"\npeak herd {peak} | season unfed {tot_unfed}/{tot_days} animal-days "
      f"({tot_unfed/max(1,tot_days):.1%})")
