"""Our own d10 melon profile in the SAME detonator games (mirror of choreo_melon.py).
Reads results/decodes/choreo_melon.jsonl for the game list/class, then profiles ME.
"""
import json, glob, os
from collections import defaultdict

ME = "Shane Thivaharraja"
DIRS = [
    r"C:\Kaggriculture\replays\live_v71c_sep13",
    r"C:\Kaggriculture\replays\live_v70c_sep13",
    r"C:\Kaggriculture\replays\live_v67c",
]
SHED = [(4, 4), (5, 4), (4, 5), (5, 5)]
klass_by_ep = {}
for line in open(r"C:\Kaggriculture\results\decodes\choreo_melon.jsonl"):
    r = json.loads(line)
    klass_by_ep[r["ep"]] = r["klass"]

def dist_shed(x, y):
    return min(abs(x - sx) + abs(y - sy) for sx, sy in SHED)

def holdings(priv):
    return priv["shed"].get("MELON", 0) + sum(i.get("MELON", 0) for i in priv["inventories"])

agg = {k: defaultdict(lambda: defaultdict(float)) for k in ("fast", "slow")}
nn = defaultdict(int)
lay = {k: defaultdict(int) for k in ("fast", "slow")}
meln = defaultdict(float)
for d in DIRS:
    for f in glob.glob(os.path.join(d, "*.json")):
        ep = os.path.basename(f).split("-")[1]
        if ep not in klass_by_ep:
            continue
        blob = json.load(open(f, encoding="utf-8"))
        names = blob["info"]["TeamNames"]
        me = names.index(ME)
        k = klass_by_ep[ep]
        nn[k] += 1
        o10 = blob["steps"][240][me]["observation"]
        for y, row in enumerate(o10["farms"][me]["tiles"]):
            for x, tl in enumerate(row):
                if isinstance(tl, dict) and tl.get("crop") == "MELON":
                    lay[k][dist_shed(x, y)] += 1
                    meln[k] += 1
        for t in range(240, 288):
            o = blob["steps"][t][me]["observation"]
            priv = o["private"]
            act = blob["steps"][t + 1][me].get("action") or {}
            tiles = o["farms"][me]["tiles"]
            farm = o["farms"][me]
            upos = [farm.get("farmer")] + list(farm.get("hands") or [])
            verbs = [act.get("farmer") or ["PASS"]] + list(act.get("hands") or [])
            harv = dep = 0
            for pos, v in zip(upos, verbs):
                verb = v[0] if v else "PASS"
                if verb == "HARVEST" and isinstance(pos, (list, tuple)):
                    x, y = int(pos[0]), int(pos[1])
                    tl = tiles[y][x] if 0 <= x < 10 and 0 <= y < 10 else None
                    if isinstance(tl, dict) and tl.get("crop") == "MELON":
                        harv += tl.get("yield_units", 0) or 0
                elif verb == "PLACE" and len(v) > 1 and v[1] == "MELON":
                    dep += v[2] if len(v) > 2 else 0
            hold0 = holdings(priv)
            hold1 = holdings(blob["steps"][t + 1][me]["observation"]["private"])
            sold = max(0, hold0 + harv - hold1)
            day, hour = o["day"], o["hour"]
            if day != 10:
                continue
            a = agg[k][hour]
            a["harv"] += harv; a["dep"] += dep; a["sold"] += sold
            a["px"] += o["market"]["prices"].get("MELON", 0)
            a["pockets"] += sum(i.get("MELON", 0) for i in priv["inventories"])
            a["shed"] += priv["shed"].get("MELON", 0)

for k in ("fast", "slow"):
    n = nn[k]
    print(f"\n===== US vs {k.upper()} copies (n={n}) =====")
    print("our melon tiles/game:", round(meln[k] / n, 1),
          "| dist histo:", {kk: round(v / n, 1) for kk, v in sorted(lay[k].items())})
    print("d10 hour: harv dep sold px | pockets shed")
    for h in sorted(agg[k]):
        a = agg[k][h]
        print(f"  h{h:>2}: {a['harv']/n:5.1f} {a['dep']/n:5.1f} {a['sold']/n:5.1f} "
              f"${a['px']/n:4.0f} | {a['pockets']/n:5.1f} {a['shed']/n:5.1f}")
    tot = sum(a["sold"] for a in agg[k].values())
    by13 = sum(a["sold"] for h, a in agg[k].items() if h <= 13)
    print("our sold_by_h13", round(by13 / n, 1), "| total d10", round(tot / n, 1))
