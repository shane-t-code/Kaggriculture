"""Live fert-machine transfer check: on-tick%, watered-same-night%, coverage,
both sides, across a replay dir.  Usage: python fert_dials_live.py <dir>"""
import json, glob, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ME = "Shane Thivaharraja"

def dials(steps, seat):
    on_tick = total = watered_same = 0
    prev = {}
    cov = ticks = 0
    for t in range(len(steps) - 1):
        o = steps[t][seat]["observation"]
        d = o["day"]
        for y, row in enumerate(o["farms"][seat]["tiles"]):
            for x, tile in enumerate(row):
                if not (isinstance(tile, dict) and tile.get("crop") == "STRAWBERRY"):
                    prev.pop((x, y), None)
                    continue
                fud = tile.get("fertilized_until_day", -1)
                key = (x, y)
                if key in prev and fud > prev[key]:
                    total += 1
                    pd = tile.get("planted_day", 0)
                    dsf = (d + 1) - pd - 10
                    if dsf >= 0 and dsf % 2 == 0:
                        on_tick += 1
                    te = min(d * 24 + 23, len(steps) - 2)
                    tt = steps[te][seat]["observation"]["farms"][seat]["tiles"][y][x]
                    if isinstance(tt, dict) and tt.get("watered_today"):
                        watered_same += 1
                prev[key] = fud
    for d in range(0, 29):
        t = d * 24 + 23
        if t >= len(steps):
            break
        o = steps[t][seat]["observation"]
        for row in o["farms"][seat]["tiles"]:
            for tile in row:
                if not (isinstance(tile, dict) and tile.get("crop") == "STRAWBERRY"):
                    continue
                pd = tile.get("planted_day", 0)
                dsf = (d + 1) - pd - 10
                if dsf < 0 or dsf % 2 != 0:
                    continue
                ticks += 1
                if tile.get("watered_today", False) and tile.get("fertilized_until_day", -1) >= d:
                    cov += 1
    return total, on_tick, watered_same, ticks, cov

A = [0] * 5
B = [0] * 5
n = 0
for f in sorted(glob.glob(sys.argv[1] + "/*.json")):
    try:
        blob = json.load(open(f, encoding="utf-8"))
    except Exception:
        continue
    names = blob["info"]["TeamNames"]
    if ME not in names:
        continue
    steps = blob["steps"]
    if len(steps) < 700:
        continue
    me = names.index(ME)
    for i, v in enumerate(dials(steps, me)):
        A[i] += v
    for i, v in enumerate(dials(steps, 1 - me)):
        B[i] += v
    n += 1
for label, S in (("US", A), ("OPPONENTS", B)):
    t2, ot, ws, tk, cv = S
    print(f"{label} ({n} games): apps {t2} | on-tick {100*ot/max(1,t2):.0f}% | "
          f"watered-same-night {100*ws/max(1,t2):.0f}% | coverage {100*cv/max(1,tk):.0f}% ({cv}/{tk})")
