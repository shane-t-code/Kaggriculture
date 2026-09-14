"""STR-fert choreography decode + window audit, both sides, detonator games.

Per game and side:
  - STR FERTILIZE ops: count, hour-of-day histo, day histo
  - missed opportunity: in-window (age 7-15) STR tile-days ending the day
    UNfertilized (fertilized_until_day < day), split by whether fert supply
    (shed+pockets) existed that evening  -> labor problem vs supply problem
  - fert flow: collected (pasture fertilizer_available consumed), applied
    (all crops), sold (shed outflow), end inventory

Usage: python tools/choreo_fert.py
"""
import json, glob, os
from collections import defaultdict

ME = "Shane Thivaharraja"
DIRS = [
    r"C:\Kaggriculture\replays\live_v71c_sep13",
    r"C:\Kaggriculture\replays\live_v70c_sep13",
    r"C:\Kaggriculture\replays\live_v67c",
]
klass_by_ep = {}
for line in open(r"C:\Kaggriculture\results\decodes\choreo_melon.jsonl"):
    r = json.loads(line)
    klass_by_ep[r["ep"]] = r["klass"]

STR_WIN = (7, 15)


def main():
    agg = defaultdict(lambda: defaultdict(float))
    nn = defaultdict(int)
    hour_h = defaultdict(lambda: defaultdict(float))
    day_h = defaultdict(lambda: defaultdict(float))
    for d in DIRS:
        for f in glob.glob(os.path.join(d, "*.json")):
            ep = os.path.basename(f).split("-")[1]
            if ep not in klass_by_ep:
                continue
            blob = json.load(open(f, encoding="utf-8"))
            names = blob["info"]["TeamNames"]
            me = names.index(ME)
            steps = blob["steps"]
            for side, seat in (("us", me), ("them", 1 - me)):
                key = (klass_by_ep[ep], side)
                nn[key] += 1
                a = agg[key]
                for t in range(len(steps) - 1):
                    o = steps[t][seat]["observation"]
                    day, hour = o["day"], o["hour"]
                    farm = o["farms"][seat]
                    act = steps[t + 1][seat].get("action") or {}
                    tiles = farm["tiles"]
                    upos = [farm.get("farmer")] + list(farm.get("hands") or [])
                    verbs = [act.get("farmer") or ["PASS"]] + list(act.get("hands") or [])
                    for pos, v in zip(upos, verbs):
                        if v and v[0] == "FERTILIZE" and isinstance(pos, (list, tuple)):
                            x, y = int(pos[0]), int(pos[1])
                            tl = tiles[y][x] if 0 <= x < 10 and 0 <= y < 10 else None
                            if isinstance(tl, dict):
                                crop = tl.get("crop")
                                if crop == "STRAWBERRY":
                                    a["str_fert_ops"] += 1
                                    hour_h[key][hour] += 1
                                    day_h[key][day] += 1
                                elif crop:
                                    a["other_fert_ops"] += 1
                    if hour == 23:
                        priv = o["private"]
                        supply = priv["shed"].get("FERTILIZER", 0) + sum(
                            i.get("FERTILIZER", 0) for i in priv["inventories"])
                        for row in tiles:
                            for tl in row:
                                if not (isinstance(tl, dict) and tl.get("crop") == "STRAWBERRY"):
                                    continue
                                age = day - tl.get("planted_day", day)
                                if STR_WIN[0] <= age <= STR_WIN[1]:
                                    a["window_tile_days"] += 1
                                    if tl.get("fertilized_until_day", -1) < day:
                                        a["missed_tile_days"] += 1
                                        if supply > 0:
                                            a["missed_with_supply"] += 1
                        # fert sells: shed outflow proxy across the day handled below
                # fert sold across game: track holdings drop hour-to-hour
                sold = 0.0
                for t in range(len(steps) - 1):
                    o = steps[t][seat]["observation"]
                    p0 = o["private"]
                    p1 = steps[t + 1][seat]["observation"]["private"]
                    h0 = p0["shed"].get("FERTILIZER", 0) + sum(i.get("FERTILIZER", 0) for i in p0["inventories"])
                    h1 = p1["shed"].get("FERTILIZER", 0) + sum(i.get("FERTILIZER", 0) for i in p1["inventories"])
                    # FERTILIZE also consumes 1 from pocket; subtract applies
                    act = steps[t + 1][seat].get("action") or {}
                    verbs = [act.get("farmer") or ["PASS"]] + list(act.get("hands") or [])
                    applies = sum(1 for v in verbs if v and v[0] == "FERTILIZE")
                    drop = h0 - h1 - applies
                    if drop > 0:
                        sold += drop
                agg[(klass_by_ep[ep], side)]["fert_sold"] += sold

    for klass in ("fast", "slow"):
        print(f"\n===== {klass.upper()} games =====")
        for side in ("us", "them"):
            key = (klass, side)
            n = max(1, nn[key])
            a = agg[key]
            miss = a["missed_tile_days"]
            print(f" {side:>5}: STR fert ops/game {a['str_fert_ops']/n:.1f} | other-crop fert {a['other_fert_ops']/n:.1f} "
                  f"| fert sold/game {a['fert_sold']/n:.1f}")
            print(f"        window STR tile-days {a['window_tile_days']/n:.1f}, missed {miss/n:.1f} "
                  f"({miss/max(1,a['window_tile_days']):.0%}), of which WITH supply on hand {a['missed_with_supply']/max(1,miss):.0%}")
            hh = sorted(hour_h[key].items())
            print("        ops by hour:", {h: round(v/n, 1) for h, v in hh if v/n >= 0.5})
            dd = sorted(day_h[key].items())
            print("        ops by day:", {int(d): round(v/n, 1) for d, v in dd if v/n >= 1.0})


if __name__ == "__main__":
    main()
