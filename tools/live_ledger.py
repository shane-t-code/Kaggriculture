"""Live loss ledger: band record via fresh LB join + revenue-by-good gap +
ops/stop (work actions per stationary stop) both sides.

Usage: python tools/live_ledger.py <replay_dir> <lb_csv>
"""
import json, glob, os, sys, csv
from collections import defaultdict

ME = "Shane Thivaharraja"
WORK = {"HARVEST", "FEED", "CARE", "WATER", "PLANT", "FERTILIZE",
        "COLLECT_FERTILIZER", "BUILD_COOP", "BUILD_PASTURE", "PICKUP",
        "PLACE", "DROP", "DIG"}
MOVES = {"NORTH", "SOUTH", "EAST", "WEST"}
PRODUCTS = ("STRAWBERRY", "MELON", "MILK", "WOOL", "EGG", "WHEAT", "TOMATO",
            "CARROT", "FERTILIZER")


def main():
    d, lbcsv = sys.argv[1], sys.argv[2]
    lb = {}
    for r in csv.reader(open(lbcsv, encoding="utf-8")):
        try:
            lb[r[2]] = float(r[4])
        except (ValueError, IndexError):
            pass
    band = defaultdict(lambda: [0, 0])
    rev = defaultdict(lambda: defaultdict(float))
    stops = {"us": [0.0, 0.0], "them": [0.0, 0.0]}  # [work ops, stops]
    n = 0
    for f in glob.glob(os.path.join(d, "*.json")):
        blob = json.load(open(f, encoding="utf-8"))
        steps = blob.get("steps") or []
        if len(steps) < 700:
            continue
        names = blob["info"]["TeamNames"]
        if ME not in names:
            continue
        me = names.index(ME)
        opp = 1 - me
        n += 1
        won = (blob["rewards"][me] or 0) > (blob["rewards"][opp] or 0)
        r = lb.get(names[opp])
        b = ("<600" if r and r < 600 else "600-756" if r and r < 756 else
             "756-900" if r and r < 900 else "900-1200" if r and r < 1200 else
             "1200+" if r else "unknown")
        band[b][0] += 1 if won else 0
        band[b][1] += 1
        # revenue by good: money increase per SELL commit is hard; use market
        # holdings outflow x price (same estimator as choreo tools)
        for side, seat in (("us", me), ("them", opp)):
            # ops/stop: per unit, consecutive turns at same position with work
            prev_pos = {}
            cur_ops = {}
            for t in range(len(steps) - 1):
                o = steps[t][seat]["observation"]
                farm = o["farms"][seat]
                act = steps[t + 1][seat].get("action") or {}
                upos = [farm.get("farmer")] + list(farm.get("hands") or [])
                verbs = [act.get("farmer") or ["PASS"]] + list(act.get("hands") or [])
                priv = o["private"]
                o1 = steps[t + 1][seat]["observation"]
                p1 = o1["private"]
                for it in PRODUCTS:
                    h0 = priv["shed"].get(it, 0) + sum(i.get(it, 0) for i in priv["inventories"])
                    h1 = p1["shed"].get(it, 0) + sum(i.get(it, 0) for i in p1["inventories"])
                    # production adds happen at day tick (hour 23->0); skip
                    if o["hour"] != 23 and h1 < h0:
                        px = o["market"]["prices"].get(it, 0)
                        rev[side][it] += (h0 - h1) * px
                for ui, pos in enumerate(upos):
                    v = verbs[ui][0] if ui < len(verbs) and verbs[ui] else "PASS"
                    key = (ui,)
                    p = tuple(pos) if isinstance(pos, (list, tuple)) else None
                    if prev_pos.get(key) == p:
                        if v in WORK:
                            cur_ops[key] = cur_ops.get(key, 0) + 1
                    else:
                        if cur_ops.get(key, 0) > 0:
                            stops[side][0] += cur_ops[key]
                            stops[side][1] += 1
                        cur_ops[key] = 1 if v in WORK else 0
                        prev_pos[key] = p
    print(f"games: {n}")
    print("\nBAND RECORD (opp joined to fresh LB):")
    for b in ("<600", "600-756", "756-900", "900-1200", "1200+", "unknown"):
        w, tot = band[b]
        if tot:
            print(f"  {b:>8}: {w}W-{tot-w}L ({w/tot:.0%})")
    print("\nREVENUE BY GOOD ($/game, holdings-outflow x price):")
    tot_us = tot_them = 0
    for it in PRODUCTS:
        u = rev['us'][it] / n
        t = rev['them'][it] / n
        tot_us += u
        tot_them += t
        print(f"  {it:>11}: us {u:8,.0f}  them {t:8,.0f}  gap {u-t:+8,.0f}")
    print(f"  {'TOTAL':>11}: us {tot_us:8,.0f}  them {tot_them:8,.0f}  gap {tot_us-tot_them:+8,.0f}")
    for side in ("us", "them"):
        ops, st = stops[side]
        print(f"ops/stop {side}: {ops/max(1,st):.2f} ({ops/n:.0f} ops, {st/n:.0f} stops per game)")


if __name__ == "__main__":
    main()
