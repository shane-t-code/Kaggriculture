"""Choreography decode: the band's d0-9 FUNDING ENGINE .

How do the mel7/mel12 band classes afford 5-6 cows AND 15-19 STR seeds by d9?
For each band game (opponent rated 756-900), extract BOTH sides, days 0-9:
  - cash at each day h0 (the funding curve)
  - every market order (day, hour, op, item, qty) from the action stream
  - revenue by good by day (bank-rise matched to holdings-drop, price-capped)
  - feed source: FEED ops + wheat bought vs harvested
  - fert: COLLECT_FERTILIZER ops + fert sold
  - planting timeline: crop -> list of (day, count planted that day)
  - animal arrivals: kind -> list of placement days
Aggregates by opponent class (d0 melon cohort: mel7 vs mel10+).
Usage: python tools/choreo_funding.py replays/live_v83a results/leaderboards/lb_2026-09-16.csv [more_replay_dirs...]
"""
import json, glob, os, sys, csv
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ME = "Shane Thivaharraja"
GOODS = ["MELON", "STRAWBERRY", "TOMATO", "CARROT", "WHEAT", "MILK", "WOOL",
         "EGG", "FERTILIZER"]
DMAX = 9


def hold(o, good):
    p = o["private"]
    return p["shed"].get(good, 0) + sum(i.get(good, 0) for i in p["inventories"])


def decode_side(steps, seat):
    out = {
        "cash": {}, "orders": [], "rev": defaultdict(float),
        "rev_by_day": defaultdict(float), "spend": defaultdict(float),
        "feeds": 0, "collects": 0, "waters": 0, "plants": defaultdict(list),
        "animal_days": defaultdict(list), "wheat_bought": 0, "wheat_harvested": 0,
    }
    seen_animals = {}
    seen_crops = {}
    for day in range(DMAX + 1):
        t = min(day * 24, len(steps) - 1)
        out["cash"][day] = steps[t][seat]["observation"]["farms"][seat]["money"]
    for t in range(min((DMAX + 1) * 24, len(steps) - 1)):
        o0 = steps[t][seat]["observation"]
        o1 = steps[t + 1][seat]["observation"]
        day, hour = o0["day"], o0["hour"]
        px = o0["market"]["prices"]
        b0 = o0["farms"][seat]["money"]
        b1 = o1["farms"][seat]["money"]
        # market orders from the action stream
        act = steps[t][seat].get("action") or {}
        for order in (act.get("market") or []):
            if not (isinstance(order, list) and order):
                continue
            op = str(order[0])
            item = str(order[1]) if len(order) > 1 else ""
            qty = order[2] if len(order) > 2 and isinstance(order[2], int) else 1
            out["orders"].append((day, hour, op, item, qty, px.get(item, 0)))
        # unit ops
        for v in [act.get("farmer")] + list(act.get("hands") or []):
            if not v:
                continue
            op = v[0] if isinstance(v, list) else v
            if op == "FEED":
                out["feeds"] += 1
            elif op == "COLLECT_FERTILIZER":
                out["collects"] += 1
            elif op == "WATER":
                out["waters"] += 1
        # revenue attribution
        gained = max(0, b1 - b0)
        for g in GOODS:
            drop = hold(o0, g) - hold(o1, g)
            if drop > 0 and gained > 0:
                take = min(drop * max(1, px.get(g, 1)), gained)
                out["rev"][g] += take
                out["rev_by_day"][(g, day)] += take
                gained -= take
        lost = max(0, b0 - b1)
        for g in ("WHEAT", "FERTILIZER"):
            gain = hold(o1, g) - hold(o0, g)
            if gain > 0 and lost > 0:
                take = min(gain * px.get(g, 0), lost)
                out["spend"][g] += take
                lost -= take
                if g == "WHEAT":
                    out["wheat_bought"] += gain
        # board diffs: new crops / animals
        farm1 = o1["farms"][seat]["tiles"]
        for y, row in enumerate(farm1):
            for x, tile in enumerate(row):
                if not isinstance(tile, dict):
                    continue
                c = tile.get("crop")
                if c and tile.get("planted_day") is not None:
                    key = (x, y, c, tile["planted_day"])
                    if key not in seen_crops and tile["planted_day"] <= DMAX:
                        seen_crops[key] = True
                        out["plants"][c].append(tile["planted_day"])
                a = tile.get("animal")
                if a and tile.get("placed_day") is not None:
                    key = (x, y, a, tile["placed_day"])
                    if key not in seen_animals and tile["placed_day"] <= DMAX:
                        seen_animals[key] = True
                        out["animal_days"][a].append(tile["placed_day"])
    return out


def summarize(tag, sides):
    n = len(sides)
    print(f"\n===== {tag} (n={n} games) =====")
    cash = defaultdict(float)
    for s in sides:
        for d, v in s["cash"].items():
            cash[d] += v / n
    print("cash @h0: " + "  ".join(f"d{d}:{cash[d]:,.0f}" for d in sorted(cash)))
    rev = defaultdict(float); spend = defaultdict(float)
    for s in sides:
        for g, v in s["rev"].items():
            rev[g] += v / n
        for g, v in s["spend"].items():
            spend[g] += v / n
    print("rev d0-9: " + "  ".join(f"{g[:4]}:{rev[g]:,.0f}" for g in GOODS if rev[g] > 50))
    print(f"spend d0-9: WHEAT {spend['WHEAT']:,.0f} ({sum(s['wheat_bought'] for s in sides)/n:.0f}u)  FERT {spend['FERTILIZER']:,.0f}")
    print(f"ops d0-9: feeds {sum(s['feeds'] for s in sides)/n:.0f}  collects {sum(s['collects'] for s in sides)/n:.0f}  waters {sum(s['waters'] for s in sides)/n:.0f}")
    # planting timeline
    for c in ("MELON", "STRAWBERRY", "WHEAT"):
        hist = defaultdict(float)
        for s in sides:
            for pd in s["plants"].get(c, []):
                hist[pd] += 1 / n
        if hist:
            print(f"plant {c[:4]}: " + "  ".join(f"d{d}:{hist[d]:.1f}" for d in sorted(hist)))
    for a in ("COW", "SHEEP", "GOOSE"):
        hist = defaultdict(float)
        for s in sides:
            for pd in s["animal_days"].get(a, []):
                hist[pd] += 1 / n
        if hist:
            print(f"place {a}: " + "  ".join(f"d{d}:{hist[d]:.1f}" for d in sorted(hist)))
    # purchase timeline (aggregated by day)
    buy = defaultdict(float)
    sell_fert = defaultdict(float)
    for s in sides:
        for (day, hour, op, item, qty, p) in s["orders"]:
            if op.startswith("BUY"):
                buy[(day, op.replace("BUY_", ""), item)] += qty / n
            elif op == "SELL" and item in ("FERTILIZER", "WHEAT", "WOOL", "MILK"):
                sell_fert[(day, item)] += qty / n
    print("buys by day: " + "  ".join(
        f"d{d}:{op[:4]}{it[:4]}x{q:.1f}" for (d, op, it), q in sorted(buy.items()) if q >= 0.5))
    print("early sells: " + "  ".join(
        f"d{d}:{it[:4]}x{q:.1f}" for (d, it), q in sorted(sell_fert.items()) if q >= 1))


def main():
    lbcsv = sys.argv[2]
    dirs = [sys.argv[1]] + sys.argv[3:]
    lb = {}
    for r in csv.reader(open(lbcsv, encoding="utf-8")):
        try:
            lb[r[2]] = float(r[4])
        except (ValueError, IndexError):
            pass
    classes = defaultdict(list)   # class tag -> list of opponent side decodes
    mine = defaultdict(list)      # same keyed classes -> our side
    for d in dirs:
        for f in sorted(glob.glob(os.path.join(d, "*.json"))):
            blob = json.load(open(f, encoding="utf-8"))
            steps = blob.get("steps") or []
            if len(steps) < 700:
                continue
            names = blob["info"]["TeamNames"]
            if ME not in names:
                continue
            me = names.index(ME)
            opp = 1 - me
            oname = names[opp]
            orating = lb.get(oname)
            if orating is None or not (756 <= orating <= 900) or oname == ME:
                continue
            o5 = steps[min(5 * 24, len(steps) - 1)][me]["observation"]
            coh = sum(1 for row in o5["farms"][opp]["tiles"] for t in row
                      if isinstance(t, dict) and t.get("crop") == "MELON"
                      and t.get("planted_day", 99) <= 1)
            tag = "mel7-class" if coh <= 9 else "mel10+-class"
            classes[tag].append(decode_side(steps, opp))
            mine[tag].append(decode_side(steps, me))
    for tag in sorted(classes):
        summarize(f"THEM {tag}", classes[tag])
        summarize(f"US vs {tag}", mine[tag])


if __name__ == "__main__":
    main()
