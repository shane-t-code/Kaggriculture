"""Decompose STR + WOOL gap in band losses: units vs price vs phase vs tiles.

For each band loss: per side, per phase (d7-14 / d15-21 / d22-29):
  STR units sold, avg realized $/u, STR tile count at phase start,
  WOOL units sold + $/u, sheep count.
Usage: python tools/band_loss_str.py replays/live_v83a results/leaderboards/lb_2026-09-16.csv
"""
import json, glob, os, sys, csv
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ME = "Shane Thivaharraja"
PHASES = [(7, 14), (15, 21), (22, 29)]


def holdings(priv, good):
    return priv["shed"].get(good, 0) + sum(i.get(good, 0) for i in priv["inventories"])


def sold_by_phase(steps, seat, good):
    out = {p: [0, 0.0] for p in PHASES}  # units, $
    for t in range(len(steps) - 1):
        o0 = steps[t][seat]["observation"]
        o1 = steps[t + 1][seat]["observation"]
        day = o0["day"]
        b0, b1 = o0["farms"][seat]["money"], o1["farms"][seat]["money"]
        if b1 <= b0:
            continue
        h0 = holdings(o0["private"], good)
        h1 = holdings(o1["private"], good)
        drop = h0 - h1
        if drop <= 0:
            continue
        px = o0["market"]["prices"].get(good, 0)
        for lo, hi in PHASES:
            if lo <= day <= hi:
                out[(lo, hi)][0] += drop
                out[(lo, hi)][1] += min(drop * px, b1 - b0)
    return out


def tiles_at(steps, seat, day, crop):
    t = min(day * 24, len(steps) - 1)
    farm = steps[t][seat]["observation"]["farms"][seat]["tiles"]
    return sum(1 for row in farm for x in row
               if isinstance(x, dict) and x.get("crop") == crop)


def animals_at(steps, seat, day, kind):
    t = min(day * 24, len(steps) - 1)
    farm = steps[t][seat]["observation"]["farms"][seat]["tiles"]
    return sum(1 for row in farm for x in row
               if isinstance(x, dict) and x.get("animal") == kind)


def main():
    d, lbcsv = sys.argv[1], sys.argv[2]
    lb = {}
    for r in csv.reader(open(lbcsv, encoding="utf-8")):
        try:
            lb[r[2]] = float(r[4])
        except (ValueError, IndexError):
            pass
    agg = defaultdict(lambda: [0, 0.0, 0, 0.0])  # phase -> us_u, us_$, them_u, them_$
    agg_w = defaultdict(lambda: [0, 0.0, 0, 0.0])
    tile_sum = defaultdict(lambda: [0, 0])
    n = 0
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
        margin = (blob["rewards"][me] or 0) - (blob["rewards"][opp] or 0)
        if orating is None or not (756 <= orating <= 900) or margin >= 0:
            continue
        if oname == ME:
            continue  # mirror
        n += 1
        my_s = sold_by_phase(steps, me, "STRAWBERRY")
        op_s = sold_by_phase(steps, opp, "STRAWBERRY")
        my_w = sold_by_phase(steps, me, "WOOL")
        op_w = sold_by_phase(steps, opp, "WOOL")
        print(f"--- vs {oname} ({orating:.0f}) margin {margin:+,.0f} ---")
        for p in PHASES:
            mu, md = my_s[p]; ou, od = op_s[p]
            mpx = md / mu if mu else 0
            opx = od / ou if ou else 0
            print(f"  STR d{p[0]}-{p[1]}: us {mu:3d}u @{mpx:5.1f} = {md:7,.0f} | "
                  f"them {ou:3d}u @{opx:5.1f} = {od:7,.0f}")
            agg[p][0] += mu; agg[p][1] += md; agg[p][2] += ou; agg[p][3] += od
            wu, wd = my_w[p]; owu, owd = op_w[p]
            agg_w[p][0] += wu; agg_w[p][1] += wd; agg_w[p][2] += owu; agg_w[p][3] += owd
        for day in (10, 15, 20, 24, 28):
            mt = tiles_at(steps, me, day, "STRAWBERRY")
            ot = tiles_at(steps, opp, day, "STRAWBERRY")
            tile_sum[day][0] += mt; tile_sum[day][1] += ot
        ms = animals_at(steps, me, 20, "SHEEP")
        osp = animals_at(steps, opp, 20, "SHEEP")
        print(f"  sheep@d20 us {ms} them {osp}   WOOL total us "
              f"{sum(v[1] for v in my_w.values()):,.0f} them {sum(v[1] for v in op_w.values()):,.0f}")
    print(f"\n=== AGGREGATE ({n} losses, mirror excluded) ===")
    print("STR:")
    for p in PHASES:
        mu, md, ou, od = agg[p]
        print(f"  d{p[0]:2d}-{p[1]}: us {mu/n:5.1f}u @{md/mu if mu else 0:5.1f} = {md/n:7,.0f}/g | "
              f"them {ou/n:5.1f}u @{od/ou if ou else 0:5.1f} = {od/n:7,.0f}/g  diff {od/n-md/n:+7,.0f}")
    print("WOOL:")
    for p in PHASES:
        mu, md, ou, od = agg_w[p]
        print(f"  d{p[0]:2d}-{p[1]}: us {mu/n:5.1f}u @{md/mu if mu else 0:5.1f} = {md/n:7,.0f}/g | "
              f"them {ou/n:5.1f}u @{od/ou if ou else 0:5.1f} = {od/n:7,.0f}/g  diff {od/n-md/n:+7,.0f}")
    print("STR tiles (avg us/them): " + "  ".join(
        f"d{day}:{v[0]/n:.1f}/{v[1]/n:.1f}" for day, v in sorted(tile_sum.items())))


if __name__ == "__main__":
    main()
