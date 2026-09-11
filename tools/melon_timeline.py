"""melon_timeline.py — per-day melon sells (units, approx price) both seats.
Price = observed market price at the order's step (close to realized for small
batches). Usage: python tools/melon_timeline.py <replay_path...>"""
import json, sys
from collections import defaultdict

ITEM = "MELON"
for path in sys.argv[1:]:
    rep = json.load(open(path, encoding="utf-8"))
    steps = rep["steps"]
    per = [defaultdict(lambda: [0, 0.0]) for _ in (0, 1)]  # day -> [units, $]
    tiles = [defaultdict(int) for _ in (0, 1)]
    for si in range(1, len(steps)):
        day = steps[si - 1][0]["observation"].get("step", si - 1) // 24
        px = steps[si - 1][0]["observation"]["market"]["prices"].get(ITEM, 0)
        for seat in (0, 1):
            a = steps[si][seat].get("action") or {}
            for o in (a.get("market") or []):
                if isinstance(o, list) and len(o) >= 3 and o[0] == "SELL" and o[1] == ITEM:
                    try:
                        n = int(o[2])
                    except Exception:
                        continue
                    per[seat][day][0] += n
                    per[seat][day][1] += n * px
    print(f"\n== {path} ==")
    print("day | ME sold  avg$ | KING sold  avg$")
    for day in range(30):
        a, b = per[0][day], per[1][day]
        if a[0] or b[0]:
            pa = a[1] / a[0] if a[0] else 0
            pb = b[1] / b[0] if b[0] else 0
            print(f" {day:>2} |  {a[0]:>3}   {pa:>5.0f}  |  {b[0]:>3}    {pb:>5.0f}")
    for seat, name in ((0, "ME"), (1, "KING")):
        tot_u = sum(v[0] for v in per[seat].values())
        tot_d = sum(v[1] for v in per[seat].values())
        print(f"{name}: {tot_u}u ~${tot_d:,.0f} (~${tot_d/max(1,tot_u):.0f}/u)")
