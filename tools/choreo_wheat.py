"""Wheat-lane decode, both sides, live games: acreage, sells, buys, prices.

Answers: where does their wheat +$4.5k/game come from — acreage (tile-days),
sell timing/price, or buy-low-sell-high arbitrage?

Usage: python tools/choreo_wheat.py <replay_dir>
"""
import json, glob, os, sys
from collections import defaultdict

ME = "Shane Thivaharraja"


def main():
    d = sys.argv[1]
    agg = defaultdict(lambda: defaultdict(float))
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
        n += 1
        for side, seat in (("us", me), ("them", 1 - me)):
            a = agg[side]
            for t in range(len(steps) - 1):
                o = steps[t][seat]["observation"]
                day, hour = o["day"], o["hour"]
                priv = o["private"]
                p1 = steps[t + 1][seat]["observation"]["private"]
                h0 = priv["shed"].get("WHEAT", 0) + sum(i.get("WHEAT", 0) for i in priv["inventories"])
                h1 = p1["shed"].get("WHEAT", 0) + sum(i.get("WHEAT", 0) for i in p1["inventories"])
                px = o["market"]["prices"].get("WHEAT", 0)
                # harvest adds within-day come from HARVEST ops; production at tick
                act = steps[t + 1][seat].get("action") or {}
                farm = o["farms"][seat]
                tiles = farm["tiles"]
                upos = [farm.get("farmer")] + list(farm.get("hands") or [])
                verbs = [act.get("farmer") or ["PASS"]] + list(act.get("hands") or [])
                harv = 0
                for pos, v in zip(upos, verbs):
                    if v and v[0] == "HARVEST" and isinstance(pos, (list, tuple)):
                        x, y = int(pos[0]), int(pos[1])
                        tl = tiles[y][x] if 0 <= x < 10 and 0 <= y < 10 else None
                        if isinstance(tl, dict) and tl.get("crop") == "WHEAT":
                            harv += tl.get("yield_units", 0) or 0
                # market BUY lands in shed same turn: holdings up beyond harvest
                dh = h1 - h0
                if hour != 23:
                    if dh > harv:  # bought (or fed-wheat consumed reduces... feeds subtract)
                        a["bought_u"] += dh - harv
                        a["bought_$"] += (dh - harv) * px
                    elif dh < harv:
                        sold = harv - dh
                        # FEED ops also consume 1 wheat each — subtract
                        feeds = sum(1 for v in verbs if v and v[0] == "FEED")
                        sold = max(0, sold - feeds)
                        a["sold_u"] += sold
                        a["sold_$"] += sold * px
                if hour == 12:
                    wt = sum(1 for row in tiles for tl in row
                             if isinstance(tl, dict) and tl.get("crop") == "WHEAT")
                    ph = ("d0-9" if day < 10 else "d10-19" if day < 20 else "d20-29")
                    a[f"tiles_{ph}"] += wt / 10.0  # per-day average within phase
    print(f"games: {n}")
    for side in ("us", "them"):
        a = agg[side]
        print(f"\n===== {side.upper()} =====")
        print(f"  wheat tiles avg: d0-9 {a['tiles_d0-9']/n:.1f} | d10-19 {a['tiles_d10-19']/n:.1f} | d20-29 {a['tiles_d20-29']/n:.1f}")
        su, sd = a["sold_u"] / n, a["sold_$"] / n
        bu, bd = a["bought_u"] / n, a["bought_$"] / n
        print(f"  sold {su:.0f} u/game @ ${sd/max(1,su):.1f} = ${sd:,.0f}")
        print(f"  bought {bu:.0f} u/game @ ${bd/max(1,bu):.1f} = ${bd:,.0f}")
        print(f"  net wheat cash: ${sd-bd:,.0f}")


if __name__ == "__main__":
    main()
