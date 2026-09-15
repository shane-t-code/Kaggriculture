"""v80b LIVE TRANSFER CHECK: did the d10 melon caravan fire on the ladder?

Per live game: opponent's d0 melon cohort (latch condition, planted_day<=1
count at d5), OUR d10 melon profile (sold by h13, total, wavg price,
pockets at d10 h23), result + margin.  Split: latch-should-fire vs not,
and opponent detonator class (fast/slow by their sell timing).

Usage: python tools/live_v80b_check.py <replay_dir>
"""
import json, glob, os, sys

ME = "Shane Thivaharraja"


def holdings(priv):
    return priv["shed"].get("MELON", 0) + sum(i.get("MELON", 0) for i in priv["inventories"])


def main():
    d = sys.argv[1]
    rows = []
    for f in glob.glob(os.path.join(d, "*.json")):
        try:
            blob = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        steps = blob.get("steps") or []
        if len(steps) < 700:
            continue
        names = blob["info"]["TeamNames"]
        if ME not in names:
            continue
        me = names.index(ME)
        opp = 1 - me
        # latch condition at d5 (any obs d4-8; use d5 h12)
        o5 = steps[5 * 24 + 12][me]["observation"]
        cohort = sum(1 for row in o5["farms"][opp]["tiles"] for t in row
                     if isinstance(t, dict) and t.get("crop") == "MELON"
                     and t.get("planted_day", 99) <= 1)
        # our d10 profile
        sold = by13 = rev = 0.0
        pock23 = 0
        for t in range(10 * 24, min(12 * 24, len(steps) - 1)):
            o = steps[t][me]["observation"]
            priv = o["private"]
            farm = o["farms"][me]
            act = steps[t + 1][me].get("action") or {}
            tiles = farm["tiles"]
            upos = [farm.get("farmer")] + list(farm.get("hands") or [])
            verbs = [act.get("farmer") or ["PASS"]] + list(act.get("hands") or [])
            harv = 0
            for pos, v in zip(upos, verbs):
                if v and v[0] == "HARVEST" and isinstance(pos, (list, tuple)):
                    x, y = int(pos[0]), int(pos[1])
                    tl = tiles[y][x] if 0 <= x < 10 and 0 <= y < 10 else None
                    if isinstance(tl, dict) and tl.get("crop") == "MELON":
                        harv += tl.get("yield_units", 0) or 0
            h0 = holdings(priv)
            h1 = holdings(steps[t + 1][me]["observation"]["private"])
            s = max(0, h0 + harv - h1)
            px = o["market"]["prices"].get("MELON", 0)
            sold += s
            rev += s * px
            if o["day"] == 10 and o["hour"] <= 13:
                by13 += s
            if o["day"] == 10 and o["hour"] == 23:
                pock23 = sum(i.get("MELON", 0) for i in priv["inventories"])
        # opp class: their melons sold by end d10 h13 (fast) — reuse holdings
        osold13 = 0.0
        for t in range(10 * 24, 10 * 24 + 14):
            o = steps[t][opp]["observation"]
            priv = o["private"]
            act = steps[t + 1][opp].get("action") or {}
            farm = o["farms"][opp]
            tiles = farm["tiles"]
            upos = [farm.get("farmer")] + list(farm.get("hands") or [])
            verbs = [act.get("farmer") or ["PASS"]] + list(act.get("hands") or [])
            harv = 0
            for pos, v in zip(upos, verbs):
                if v and v[0] == "HARVEST" and isinstance(pos, (list, tuple)):
                    x, y = int(pos[0]), int(pos[1])
                    tl = tiles[y][x] if 0 <= x < 10 and 0 <= y < 10 else None
                    if isinstance(tl, dict) and tl.get("crop") == "MELON":
                        harv += tl.get("yield_units", 0) or 0
            h0 = holdings(priv)
            h1 = holdings(steps[t + 1][opp]["observation"]["private"])
            osold13 += max(0, h0 + harv - h1)
        margin = (blob["rewards"][me] or 0) - (blob["rewards"][opp] or 0)
        rows.append(dict(ep=os.path.basename(f).split("-")[1], cohort=cohort,
                         fire=cohort >= 10, by13=by13, sold=sold,
                         wavg=rev / sold if sold else 0, pock23=pock23,
                         opp13=osold13, won=margin > 0, margin=margin,
                         opp=names[opp]))
    n = len(rows)
    print(f"games decoded: {n}")
    for cond, name in ((lambda r: r["fire"], "LATCH FIRES (opp d0-cohort >=10)"),
                       (lambda r: not r["fire"], "latch off")):
        sub = [r for r in rows if cond(r)]
        if not sub:
            continue
        k = len(sub)
        w = sum(1 for r in sub if r["won"])
        print(f"\n== {name}: {k} games, W{w}-L{k-w}, mean margin {sum(r['margin'] for r in sub)/k:+,.0f}")
        print(f"   our melons by h13: {sum(r['by13'] for r in sub)/k:.1f} | total {sum(r['sold'] for r in sub)/k:.1f} "
              f"| wavg ${sum(r['wavg'] for r in sub)/k:.0f} | pockets@h23 {sum(r['pock23'] for r in sub)/k:.1f}")
        print(f"   their melons by h13: {sum(r['opp13'] for r in sub)/k:.1f}")
        for r in sorted(sub, key=lambda r: r["margin"])[:6]:
            print(f"     {'W' if r['won'] else 'L'} {r['margin']:+8,.0f} coh{r['cohort']:>2} "
                  f"by13 {r['by13']:>4.0f} vs their {r['opp13']:>4.0f}  {r['opp'][:22]}")


if __name__ == "__main__":
    main()
