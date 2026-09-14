"""Choreography decode of detonator opponents' d10 melon morning from live replays.

For every live replay where the OPPONENT is a melon detonator (>=10 melon tiles
at d5), extract THEIR execution:
  - layout: melon tiles / animals / distances from the 4 shed-access tiles
  - build order (planted_day / placed_day)
  - d9 evening staging (unit positions h20-23, pockets at h23)
  - d10 hour-by-hour: harvests, deposits (PLACE), sells, pockets, shed, price
  - labor allocation on d10 morning (feed/care/water done or skipped)
Classifies fast (>=25 melons sold by end of d10 h13) vs slow.

Usage: python tools/choreo_melon.py [--detail EPISODE_ID]
Output: aggregate to stdout; per-game rows to results/decodes/choreo_melon.jsonl
"""
import json, glob, sys, os
from collections import defaultdict

ME = "Shane Thivaharraja"
DIRS = [
    r"C:\Kaggriculture\replays\live_v71c_sep13",
    r"C:\Kaggriculture\replays\live_v70c_sep13",
    r"C:\Kaggriculture\replays\live_v67c",
]
SHED = [(4, 4), (5, 4), (4, 5), (5, 5)]


def dist_shed(x, y):
    return min(abs(x - sx) + abs(y - sy) for sx, sy in SHED)


def farm_tiles(obs, seat):
    return obs["farms"][seat]["tiles"]


def units_of(farm):
    return [farm.get("farmer")] + list(farm.get("hands") or [])


def verbs_of(act):
    return [act.get("farmer") or ["PASS"]] + list(act.get("hands") or [])


def holdings(priv):
    tot = priv["shed"].get("MELON", 0)
    for inv in priv["inventories"]:
        tot += inv.get("MELON", 0)
    return tot


def decode_game(path):
    try:
        blob = json.load(open(path, encoding="utf-8"))
    except Exception:
        return None
    steps = blob.get("steps") or []
    if len(steps) < 700:
        return None
    names = blob["info"]["TeamNames"]
    if ME not in names:
        return None
    me = names.index(ME)
    opp = 1 - me

    def obs_at(t, seat):
        return steps[t][seat]["observation"]

    # detonator filter: opp melon tiles >= 10 at d5 h0
    t5 = 5 * 24
    mel5 = sum(1 for row in farm_tiles(obs_at(t5, 0), opp) for tl in row or []
               if isinstance(tl, dict) and tl.get("crop") == "MELON")
    if mel5 < 10:
        return None

    opp_name = names[opp]
    won = (blob["rewards"][me] or 0) > (blob["rewards"][opp] or 0)

    # ---- layout at d10 h0 (opp) ----
    t10 = 10 * 24
    o10 = obs_at(t10, opp)  # opp's own observation → their private too
    tiles10 = farm_tiles(o10, opp)
    mel_tiles, animals = [], []
    for y, row in enumerate(tiles10):
        for x, tl in enumerate(row):
            if not isinstance(tl, dict):
                continue
            if tl.get("crop") == "MELON":
                mel_tiles.append((x, y, tl.get("planted_day"), dist_shed(x, y)))
            if tl.get("animal"):
                animals.append((x, y, tl["animal"], tl.get("placed_day"),
                                dist_shed(x, y)))
    hands10 = len(o10["farms"][opp].get("hands") or [])

    # ---- d9 evening staging ----
    d9 = {}
    for h in (20, 23):
        t = 9 * 24 + h
        f = obs_at(t, opp)["farms"][opp]
        d9[f"pos_h{h}"] = units_of(f)
    priv923 = obs_at(9 * 24 + 23, opp)["private"]
    d9["pockets_h23"] = sum(inv.get("MELON", 0) for inv in priv923["inventories"])
    d9["shed_h23"] = priv923["shed"].get("MELON", 0)

    # ---- d10 (and d11) hour-by-hour ledger ----
    hourly = []
    sold_cum = 0.0
    rev_cum = 0.0
    for t in range(10 * 24, min(12 * 24, len(steps) - 1)):
        o = obs_at(t, opp)
        priv = o["private"]
        hold0 = holdings(priv)
        px = o["market"]["prices"].get("MELON", 0)
        act = steps[t + 1][opp].get("action") or {}
        tiles = farm_tiles(o, opp)
        harv = 0
        deposits = 0
        feeds = cares = waters = moves = 0
        upos = units_of(o["farms"][opp])
        for pos, v in zip(upos, verbs_of(act)):
            verb = v[0] if v else "PASS"
            if verb == "HARVEST" and isinstance(pos, (list, tuple)):
                x, y = int(pos[0]), int(pos[1])
                tl = tiles[y][x] if 0 <= x < 10 and 0 <= y < 10 else None
                if isinstance(tl, dict) and tl.get("crop") == "MELON":
                    harv += tl.get("yield_units", 0) or 0
            elif verb == "PLACE" and len(v) > 1 and v[1] == "MELON":
                deposits += v[2] if len(v) > 2 else 0
            elif verb == "FEED":
                feeds += 1
            elif verb == "CARE":
                cares += 1
            elif verb == "WATER":
                waters += 1
            elif verb in ("NORTH", "SOUTH", "EAST", "WEST"):
                moves += 1
        sell_ord = sum(m[2] for m in (act.get("market") or [])
                       if m and m[0] == "SELL" and m[1] == "MELON")
        o_next = obs_at(t + 1, opp)
        hold1 = holdings(o_next["private"])
        sold = max(0, hold0 + harv - hold1)  # actual units that left the farm
        sold_cum += sold
        rev_cum += sold * px
        hourly.append(dict(t=t, day=o["day"], hour=o["hour"], px=px, harv=harv,
                           dep=deposits, sell_ord=sell_ord, sold=sold,
                           pockets=sum(i.get("MELON", 0) for i in priv["inventories"]),
                           shed=priv["shed"].get("MELON", 0),
                           feeds=feeds, cares=cares, waters=waters, moves=moves))

    d10_rows = [r for r in hourly if r["day"] == 10]
    sold_by_h13 = sum(r["sold"] for r in d10_rows if r["hour"] <= 13)
    total_sold = sum(r["sold"] for r in hourly)
    klass = "fast" if sold_by_h13 >= 25 else "slow"

    return dict(ep=os.path.basename(path).split("-")[1], opp=opp_name,
                won=won, klass=klass, mel5=mel5, hands10=hands10,
                mel_tiles=mel_tiles, animals=animals, d9=d9, hourly=hourly,
                sold_by_h13=sold_by_h13, total_sold=total_sold,
                wavg_px=(rev_cum / sold_cum) if sold_cum else 0)


def main():
    detail_ep = None
    if "--detail" in sys.argv:
        detail_ep = sys.argv[sys.argv.index("--detail") + 1]
    rows = []
    for d in DIRS:
        for f in glob.glob(os.path.join(d, "*.json")):
            r = decode_game(f)
            if r:
                rows.append(r)
    os.makedirs(r"C:\Kaggriculture\results\decodes", exist_ok=True)
    with open(r"C:\Kaggriculture\results\decodes\choreo_melon.jsonl", "w") as fo:
        for r in rows:
            fo.write(json.dumps(r) + "\n")

    print(f"detonator games decoded: {len(rows)} "
          f"(fast {sum(1 for r in rows if r['klass']=='fast')}, "
          f"slow {sum(1 for r in rows if r['klass']=='slow')})")

    for klass in ("fast", "slow"):
        sub = [r for r in rows if r["klass"] == klass]
        if not sub:
            continue
        print(f"\n===== {klass.upper()} copies (n={len(sub)}) — "
              f"win-rate vs us {sum(1 for r in sub if not r['won'])/len(sub):.0%} them =====")
        # layout: melon distance histogram + plant day
        dist_h = defaultdict(int)
        pd_h = defaultdict(int)
        for r in sub:
            for x, y, pd, dd in r["mel_tiles"]:
                dist_h[dd] += 1
                pd_h[pd] += 1
        n = len(sub)
        print("melon tiles/game:", round(sum(dist_h.values()) / n, 1),
              "| dist-from-shed histo (per game):",
              {k: round(v / n, 1) for k, v in sorted(dist_h.items())})
        print("planted_day histo:", {k: round(v / n, 1) for k, v in sorted(pd_h.items())})
        an_h = defaultdict(int)
        for r in sub:
            for x, y, sp, pd, dd in r["animals"]:
                an_h[(sp, dd)] += 1
        print("animals (species,dist): ", {f"{s}@{d}": round(c / n, 1)
              for (s, d), c in sorted(an_h.items())})
        print("hands at d10:", round(sum(r["hands10"] for r in sub) / n, 1))
        print("d9 h23 staging: pockets", round(sum(r["d9"]["pockets_h23"] for r in sub) / n, 1),
              "shed", round(sum(r["d9"]["shed_h23"] for r in sub) / n, 1))
        # hour-by-hour aggregate d10
        agg = defaultdict(lambda: defaultdict(float))
        for r in sub:
            for row in r["hourly"]:
                if row["day"] != 10:
                    continue
                for k in ("harv", "dep", "sold", "px", "pockets", "shed",
                          "feeds", "cares", "waters", "moves"):
                    agg[row["hour"]][k] += row[k]
        print("d10 hour: harv dep sold px | pockets shed | feed care water move")
        for h in sorted(agg):
            a = agg[h]
            print(f"  h{h:>2}: {a['harv']/n:5.1f} {a['dep']/n:5.1f} {a['sold']/n:5.1f} "
                  f"${a['px']/n:4.0f} | {a['pockets']/n:5.1f} {a['shed']/n:5.1f} | "
                  f"{a['feeds']/n:4.1f} {a['cares']/n:4.1f} {a['waters']/n:4.1f} {a['moves']/n:4.1f}")
        print("sold_by_h13", round(sum(r["sold_by_h13"] for r in sub) / n, 1),
              "| total d10-11", round(sum(r["total_sold"] for r in sub) / n, 1),
              "| wavg $/u", round(sum(r["wavg_px"] for r in sub) / n, 1))

    if detail_ep:
        r = next((x for x in rows if x["ep"] == detail_ep), None)
        if r:
            print(f"\n===== DETAIL ep {detail_ep} ({r['opp']}, {r['klass']}) =====")
            print("melon tiles (x,y,planted,dist):", r["mel_tiles"])
            print("animals (x,y,species,placed,dist):", r["animals"])
            print("d9:", {k: v for k, v in r["d9"].items() if k != "pos_h20"})
            for row in r["hourly"]:
                if row["harv"] or row["dep"] or row["sold"] or row["sell_ord"]:
                    print(row)


if __name__ == "__main__":
    main()
