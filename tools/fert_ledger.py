"""fert_ledger.py — fertilizer flow per seat: collected vs applied vs sold vs stranded.
Also collection efficiency: animal-days (each spawns 1 collectible fert overnight)
vs COLLECT_FERTILIZER ops. Usage: python tools/fert_ledger.py <replay_path...>"""
import json, sys

for path in sys.argv[1:]:
    rep = json.load(open(path, encoding="utf-8"))
    steps = rep["steps"]
    stats = [{"collect": 0, "fertilize": 0, "animal_days": 0} for _ in (0, 1)]
    for si in range(1, len(steps)):
        for seat in (0, 1):
            a = steps[si][seat].get("action") or {}
            for u in [a.get("farmer") or ["PASS"]] + (a.get("hands") or []):
                if isinstance(u, list) and u:
                    if u[0] == "COLLECT_FERTILIZER":
                        stats[seat]["collect"] += 1
                    elif u[0] == "FERTILIZE":
                        stats[seat]["fertilize"] += 1
    for day in range(30):
        si = min(day * 24 + 23, len(steps) - 1)
        farms = steps[si][0]["observation"]["farms"]
        for seat in (0, 1):
            n = sum(1 for row in farms[seat]["tiles"] for t in row
                    if isinstance(t, dict) and "animal" in t)
            stats[seat]["animal_days"] += n
    last = steps[-1]
    print(f"\n== {path} ==")
    for seat in (0, 1):
        shed_end = last[seat]["observation"]["private"]["shed"].get("FERTILIZER", 0) \
            if "private" in last[seat]["observation"] else -1
        s = stats[seat]
        # note: COLLECT ops == units collected (1 per op); animal_days-? = spawn ceiling
        print(f"  seat{seat}: animal-days {s['animal_days']} (= max collectible) | "
              f"collected {s['collect']} ({s['collect']/max(1,s['animal_days']):.0%}) | "
              f"applied {s['fertilize']} | shed@end {shed_end}")
