"""herd_timeline.py — per-day animal counts both seats.
Usage: python tools/herd_timeline.py <replay_path...>"""
import json, sys

for path in sys.argv[1:]:
    rep = json.load(open(path, encoding="utf-8"))
    steps = rep["steps"]
    print(f"== {path} ==")
    print("day | ME C/S/G | KING C/S/G")
    for day in range(0, 16):
        si = min(day * 24 + 23, len(steps) - 1)
        farms = steps[si][0]["observation"]["farms"]
        row = []
        for seat in (0, 1):
            c = {"COW": 0, "SHEEP": 0, "GOOSE": 0}
            for r in farms[seat]["tiles"]:
                for t in r:
                    if isinstance(t, dict) and t.get("animal") in c:
                        c[t["animal"]] += 1
            row.append(c)
        a, b = row
        print(f" {day:>2} |  {a['COW']}/{a['SHEEP']}/{a['GOOSE']}   |  {b['COW']}/{b['SHEEP']}/{b['GOOSE']}")
