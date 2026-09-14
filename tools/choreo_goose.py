"""Choreography decode of detonator opponents' GOOSE operation from live replays.

Extracts, for each detonator opponent (melon tiles >=10 at d5):
  - goose placements: coords, placed_day, distance from shed
  - goose count + total animal count over time (d5/10/15/20/25)
  - purchase pattern: geese sitting in shed (bought, unplaced) by day
  - husbandry on geese: fed_today / cared_today rates by day band
  - egg economics: eggs sold per game, sell-hour distribution, $/u
Aggregated over all games and split fast/slow via results/decodes/choreo_melon.jsonl.

Usage: python tools/choreo_goose.py
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


def main():
    games = []
    for d in DIRS:
        for f in glob.glob(os.path.join(d, "*.json")):
            ep = os.path.basename(f).split("-")[1]
            if ep not in klass_by_ep:
                continue
            blob = json.load(open(f, encoding="utf-8"))
            names = blob["info"]["TeamNames"]
            me = names.index(ME)
            opp = 1 - me
            steps = blob["steps"]
            g = dict(ep=ep, klass=klass_by_ep[ep], opp=names[opp])

            # goose placements + animal census over time
            placements = {}
            census = {}
            shed_geese = {}
            for dday in (5, 10, 12, 14, 16, 20, 25):
                t = dday * 24
                if t >= len(steps):
                    continue
                o = steps[t][opp]["observation"]
                cnt = defaultdict(int)
                for y, row in enumerate(o["farms"][opp]["tiles"]):
                    for x, tl in enumerate(row):
                        if isinstance(tl, dict) and tl.get("animal"):
                            cnt[tl["animal"]] += 1
                            if tl["animal"] == "GOOSE" and (x, y) not in placements:
                                placements[(x, y)] = (tl.get("placed_day"), dist_shed(x, y))
                census[dday] = dict(cnt)
                shed_geese[dday] = o["private"]["shed"].get("GOOSE", 0)

            # goose husbandry + egg sells per day
            fed = {"d5-14": [0, 0], "d15-28": [0, 0]}
            cared = {"d5-14": [0, 0], "d15-28": [0, 0]}
            eggs_sold = 0.0
            egg_rev = 0.0
            egg_hours = defaultdict(float)
            for t in range(0, len(steps) - 1):
                o = steps[t][opp]["observation"]
                day, hour = o["day"], o["hour"]
                if hour == 23 and day >= 5:
                    band = "d5-14" if day <= 14 else "d15-28"
                    for row in o["farms"][opp]["tiles"]:
                        for tl in row:
                            if isinstance(tl, dict) and tl.get("animal") == "GOOSE":
                                fed[band][1] += 1
                                cared[band][1] += 1
                                fed[band][0] += 1 if tl.get("fed_today") else 0
                                cared[band][0] += 1 if tl.get("cared_today") else 0
                # egg outflow = holdings drop
                priv = o["private"]
                h0 = priv["shed"].get("EGG", 0) + sum(i.get("EGG", 0) for i in priv["inventories"])
                o1 = steps[t + 1][opp]["observation"]
                p1 = o1["private"]
                h1 = p1["shed"].get("EGG", 0) + sum(i.get("EGG", 0) for i in p1["inventories"])
                # production adds at day tick; within-day drops are sells
                if h1 < h0 and hour != 23:
                    n = h0 - h1
                    px = o["market"]["prices"].get("EGG", 0)
                    eggs_sold += n
                    egg_rev += n * px
                    egg_hours[hour] += n
            g.update(placements={f"{k}": v for k, v in placements.items()},
                     census=census, shed_geese=shed_geese,
                     fed=fed, cared=cared, eggs_sold=eggs_sold,
                     egg_rev=egg_rev, egg_hours=dict(egg_hours))
            games.append(g)

    os.makedirs(r"C:\Kaggriculture\results\decodes", exist_ok=True)
    with open(r"C:\Kaggriculture\results\decodes\choreo_goose.jsonl", "w") as fo:
        for g in games:
            fo.write(json.dumps(g) + "\n")

    with_geese = [g for g in games if any(c.get("GOOSE") for c in g["census"].values())]
    print(f"detonator games: {len(games)} | games where opp fields geese: {len(with_geese)}")
    for klass in ("fast", "slow"):
        sub = [g for g in with_geese if g["klass"] == klass]
        alln = [g for g in games if g["klass"] == klass]
        if not alln:
            continue
        print(f"\n===== {klass.upper()}: {len(sub)}/{len(alln)} games field geese =====")
        if not sub:
            continue
        n = len(sub)
        pd_h = defaultdict(int)
        dist_h = defaultdict(int)
        for g in sub:
            for _, (pd, dd) in g["placements"].items():
                pd_h[pd] += 1
                dist_h[dd] += 1
        print("goose placed_day histo:", dict(sorted(pd_h.items())),
              "| dist histo:", dict(sorted(dist_h.items())))
        for dday in (10, 14, 20, 25):
            cs = [g["census"].get(dday, {}) for g in sub]
            gz = sum(c.get("GOOSE", 0) for c in cs) / n
            tot = sum(sum(c.values()) for c in cs) / n
            sg = sum(g["shed_geese"].get(dday, 0) for g in sub) / n
            print(f"  d{dday}: geese {gz:.1f} placed (+{sg:.1f} in shed) of {tot:.1f} animals")
        for band in ("d5-14", "d15-28"):
            f = [sum(g["fed"][band][0] for g in sub), sum(g["fed"][band][1] for g in sub)]
            c = [sum(g["cared"][band][0] for g in sub), sum(g["cared"][band][1] for g in sub)]
            print(f"  {band}: goose fed {f[0]/max(1,f[1]):.0%}, cared {c[0]/max(1,c[1]):.0%}")
        print("  eggs sold/game:", round(sum(g["eggs_sold"] for g in sub) / n, 1),
              "| $/u:", round(sum(g["egg_rev"] for g in sub) / max(1, sum(g["eggs_sold"] for g in sub)), 1))
        hh = defaultdict(float)
        for g in sub:
            for h, v in g["egg_hours"].items():
                hh[int(h)] += v
        top = sorted(hh.items(), key=lambda kv: -kv[1])[:5]
        print("  egg sell hours (top):", [(h, round(v / n, 1)) for h, v in top])


if __name__ == "__main__":
    main()
