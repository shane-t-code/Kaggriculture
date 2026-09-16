"""v83a live transfer battery: per game — STR hold, chain, caravan, result.

Usage: python tools/live_v83a_check.py <replay_dir> <lb_csv>
"""
import json, glob, os, sys, csv
from collections import defaultdict

ME = "Shane Thivaharraja"
WORK = {"HARVEST", "FEED", "CARE", "WATER", "PLANT", "FERTILIZE",
        "COLLECT_FERTILIZER", "BUILD_COOP", "BUILD_PASTURE", "PICKUP",
        "PLACE", "DROP", "DIG"}


def main():
    d, lbcsv = sys.argv[1], sys.argv[2]
    lb = {}
    for r in csv.reader(open(lbcsv, encoding="utf-8")):
        try:
            lb[r[2]] = float(r[4])
        except (ValueError, IndexError):
            pass
    rows = []
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
        margin = (blob["rewards"][me] or 0) - (blob["rewards"][opp] or 0)
        o5 = steps[5 * 24][me]["observation"]
        coh = sum(1 for row in o5["farms"][opp]["tiles"] for t in row
                  if isinstance(t, dict) and t.get("crop") == "MELON"
                  and t.get("planted_day", 99) <= 1)
        o24 = steps[24 * 24][me]["observation"]
        str24 = sum(1 for row in o24["farms"][me]["tiles"] for t in row
                    if isinstance(t, dict) and t.get("crop") == "STRAWBERRY")
        late_rev = 0.0
        for t in range(22 * 24, min(29 * 24, len(steps) - 1)):
            o = steps[t][me]["observation"]
            if o["hour"] == 23:
                continue
            p0 = o["private"]
            p1 = steps[t + 1][me]["observation"]["private"]
            h0 = p0["shed"].get("STRAWBERRY", 0) + sum(i.get("STRAWBERRY", 0) for i in p0["inventories"])
            h1 = p1["shed"].get("STRAWBERRY", 0) + sum(i.get("STRAWBERRY", 0) for i in p1["inventories"])
            if h1 < h0:
                late_rev += (h0 - h1) * o["market"]["prices"].get("STRAWBERRY", 0)
        chains = 0
        prev = {}
        run = defaultdict(list)
        for t in range(len(steps) - 1):
            o = steps[t][me]["observation"]
            farm = o["farms"][me]
            act = steps[t + 1][me].get("action") or {}
            upos = [farm.get("farmer")] + list(farm.get("hands") or [])
            verbs = [act.get("farmer") or ["PASS"]] + list(act.get("hands") or [])
            for ui, pos in enumerate(upos):
                v = verbs[ui][0] if ui < len(verbs) and verbs[ui] else "PASS"
                p = tuple(pos) if isinstance(pos, (list, tuple)) else None
                if prev.get(ui) != p:
                    ops = set(run[ui])
                    if "FEED" in ops and ({"CARE", "COLL"} & ops):
                        chains += 1
                    run[ui] = []
                    prev[ui] = p
                if v in WORK:
                    run[ui].append(v[:4])
        by13 = 0.0
        for t in range(10 * 24, 10 * 24 + 14):
            o = steps[t][me]["observation"]
            p0 = o["private"]
            act = steps[t + 1][me].get("action") or {}
            farm = o["farms"][me]
            tiles = farm["tiles"]
            upos = [farm.get("farmer")] + list(farm.get("hands") or [])
            verbs = [act.get("farmer") or ["PASS"]] + list(act.get("hands") or [])
            harv = sum((tiles[int(p[1])][int(p[0])].get("yield_units", 0) or 0)
                       for p, v in zip(upos, verbs)
                       if v and v[0] == "HARVEST" and isinstance(p, (list, tuple))
                       and isinstance(tiles[int(p[1])][int(p[0])], dict)
                       and tiles[int(p[1])][int(p[0])].get("crop") == "MELON")
            h0 = p0["shed"].get("MELON", 0) + sum(i.get("MELON", 0) for i in p0["inventories"])
            p1 = steps[t + 1][me]["observation"]["private"]
            h1 = p1["shed"].get("MELON", 0) + sum(i.get("MELON", 0) for i in p1["inventories"])
            by13 += max(0, h0 + harv - h1)
        r = lb.get(names[opp])
        band = ("<600" if r and r < 600 else "600-756" if r and r < 756 else
                "756-900" if r and r < 900 else "900-1200" if r and r < 1200 else
                "1200+" if r else "?")
        rows.append(dict(ep=os.path.basename(f).split("-")[1], opp=names[opp],
                         lbr=r, band=band, won=margin > 0, margin=margin,
                         coh=coh, str24=str24, late_rev=late_rev,
                         chains=chains, by13=by13))
    n = len(rows)
    print(f"games: {n} | W{sum(1 for r in rows if r['won'])}-L{sum(1 for r in rows if not r['won'])}")
    print("\nBAND RECORD:")
    for b in ("<600", "600-756", "756-900", "900-1200", "1200+", "?"):
        sub = [r for r in rows if r["band"] == b]
        if sub:
            w = sum(1 for r in sub if r["won"])
            print(f"  {b:>8}: {w}W-{len(sub)-w}L | mean margin {sum(r['margin'] for r in sub)/len(sub):+,.0f}")
    print(f"\nSTR HOLD: tiles at d24 mean {sum(r['str24'] for r in rows)/n:.1f} "
          f"(pre-hold ~12-18) | late-STR rev d22-28 ${sum(r['late_rev'] for r in rows)/n:,.0f}/game")
    det = [r for r in rows if r["coh"] >= 10]
    nod = [r for r in rows if r["coh"] < 10]
    print(f"CHAIN (detonator games, n={len(det)}): chained feed-stops "
          f"{sum(r['chains'] for r in det)/max(1,len(det)):.1f}/game (family ~134; pre-chain ~0)")
    print(f"CARAVAN: melons by h13 in detonator games {sum(r['by13'] for r in det)/max(1,len(det)):.1f}")
    print(f"non-detonator chains (should be ~0): {sum(r['chains'] for r in nod)/max(1,len(nod)):.1f}")
    print("\nWORST LOSSES:")
    for r in sorted(rows, key=lambda r: r["margin"])[:8]:
        print(f"  L {r['margin']:+9,.0f} {r['band']:>8} lb={r['lbr']} coh{r['coh']:>2} "
              f"str24={r['str24']:>2} {r['opp'][:24]}")


if __name__ == "__main__":
    main()
