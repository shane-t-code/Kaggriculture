#!/usr/bin/env python3
"""conv_decode.py — decode a top agent's mid-game tile-conversion choreography.

For the target seat in each replay: every DIG on a crop tile (day, hour, tile,
crop, age, yield state, remaining-production per engine CROPS math), what got
planted there afterwards (crop + delay), how the replacement was watered
(ages at watering), and what it harvested.  Plus daily op counts both seats,
the STR-tile census by day, and SELL orders by item/day for the target.

Usage: python tools/conv_decode.py <replay_dir_or_file> <target_submission_id>
"""
import json, os, sys, glob
from collections import Counter, defaultdict

CROPS = {
    "WHEAT":      {"first": 2, "maxd": 4,  "interval": 0, "maxy": 6, "ongoing": False},
    "CARROT":     {"first": 2, "maxd": 3,  "interval": 0, "maxy": 4, "ongoing": False},
    "TOMATO":     {"first": 8, "maxd": 8,  "interval": 1, "maxy": 4, "ongoing": True},
    "STRAWBERRY": {"first": 10, "maxd": 10, "interval": 2, "maxy": 4, "ongoing": True},
    "MELON":      {"first": 10, "maxd": 12, "interval": 0, "maxy": 6, "ongoing": False},
}
TPD = 24


def remaining_prods(crop, age):
    """Engine-exact remaining production events for an ongoing crop at `age`
    (age = current_day - planted_day), or remaining harvest window info."""
    cd = CROPS[crop]
    if not cd["ongoing"]:
        return max(0, cd["maxd"] - age + 1)  # days left in harvest window-ish
    last_age = cd["first"] + (cd["maxy"] - 1) * cd["interval"]
    if age > last_age:
        return 0
    n = 0
    a = max(age + 1, cd["first"])
    # production fires on ages where (a - first) % interval == 0
    iv = max(1, cd["interval"])
    while a <= last_age:
        if (a - cd["first"]) % iv == 0:
            n += 1
        a += 1
    return n


def find_pid(info, target):
    ags = info.get("Agents") or []
    for i, a in enumerate(ags):
        if isinstance(a, dict):
            for k in ("SubmissionId", "submissionId", "Id", "id"):
                if a.get(k) == target:
                    return i
            name = str(a.get("Name", ""))
            if isinstance(target, str) and target.lower() in name.lower():
                return i
    return None


def decode(path, target):
    d = json.load(open(path))
    info = d.get("info", {})
    pid = find_pid(info, target)
    steps = d["steps"]
    name = os.path.basename(path)
    if pid is None:
        print(f"{name}: target sub {target} not in Agents "
              f"{[a for a in (info.get('Agents') or [])][:2]}")
        return
    rew = [steps[-1][i]["reward"] for i in range(2)]
    print(f"\n=== {name}  target=seat{pid}  final {rew[pid]:,.0f} vs "
          f"{rew[1-pid]:,.0f}  ({'W' if rew[pid] > rew[1-pid] else 'L' if rew[pid] < rew[1-pid] else 'T'}"
          f" {rew[pid]-rew[1-pid]:+,.0f}) ===")

    digs = []            # dicts per dig event on a PLANT tile
    tile_watch = {}      # (x,y) -> dig record awaiting replant/waters/harvest
    ops = defaultdict(lambda: Counter())      # (pid, day) -> verb counts
    str_census = {}      # day -> producing STR tiles (target)
    sells = defaultdict(Counter)              # day -> item: qty (target)

    for t in range(len(steps) - 1):
        day, hour = t // TPD, t % TPD
        farms = steps[t][0]["observation"]["farms"]
        if hour == 12:
            n_str = sum(1 for row in farms[pid]["tiles"] for tl in row
                        if isinstance(tl, dict) and tl.get("kind") == "PLANT"
                        and tl.get("crop") == "STRAWBERRY")
            str_census[day] = n_str
        for p in range(2):
            act = steps[t + 1][p].get("action") or {}
            if not isinstance(act, dict):
                continue
            farm = farms[p]
            units = [farm.get("farmer") or [0, 0]] + [list(h) for h in farm.get("hands", [])]
            uacts = [act.get("farmer") or ["PASS"]] + list(act.get("hands") or [])
            for upos, ua in zip(units, uacts):
                if not (isinstance(ua, list) and ua):
                    continue
                verb = ua[0]
                ops[(p, day)][verb] += 1
                if p != pid:
                    continue
                x, y = int(upos[0]), int(upos[1])
                tile = farm["tiles"][y][x] if 0 <= y < 10 and 0 <= x < 10 else None
                if verb == "DIG" and isinstance(tile, dict) and tile.get("kind") == "PLANT":
                    crop = tile.get("crop")
                    age = day - tile.get("planted_day", day)
                    rec = {"day": day, "h": hour, "xy": (x, y), "crop": crop,
                           "age": age, "yield": tile.get("yield_units", 0),
                           "rem": remaining_prods(crop, age) if crop in CROPS else "?",
                           "replant": None, "waters": [], "harvests": []}
                    digs.append(rec)
                    tile_watch[(x, y)] = rec
                elif (x, y) in tile_watch:
                    rec = tile_watch[(x, y)]
                    if verb == "PLANT" and len(ua) > 1:
                        if rec["replant"] is None:
                            rec["replant"] = (ua[1], day, hour)
                            rec["_pd"] = day
                    elif verb == "WATER" and rec["replant"]:
                        rec["waters"].append(day - rec["_pd"])
                    elif verb == "HARVEST" and rec["replant"]:
                        yy = tile.get("yield_units", "?") if isinstance(tile, dict) else "?"
                        rec["harvests"].append((day - rec["_pd"], yy))
            for order in (act.get("market") or []):
                if p == pid and isinstance(order, list) and order and order[0] == "SELL":
                    item = order[1] if len(order) > 1 else "?"
                    qty = order[2] if len(order) > 2 else 1
                    try:
                        sells[day][item] += int(qty)
                    except (TypeError, ValueError):
                        sells[day][item] += 1

    crop_digs = [r for r in digs]
    print(f"crop-tile DIGs: {len(crop_digs)}")
    by_crop = Counter((r["crop"], "live" if (r["rem"] and r["rem"] != "?" and r["rem"] > 0)
                       else "spent") for r in crop_digs)
    print("  by crop/liveness:", dict(by_crop))
    for r in crop_digs:
        rp = r["replant"]
        rp_s = f"-> {rp[0]} d{rp[1]}h{rp[2]}" if rp else "-> (no replant)"
        wa = ",".join(map(str, r["waters"][:6]))
        ha = " ".join(f"a{a}:y{yv}" for a, yv in r["harvests"][:4])
        print(f"  d{r['day']:>2}h{r['h']:>2} {str(r['xy']):>8} {r['crop']:<10} "
              f"age {r['age']:>2} yld {r['yield']} rem {r['rem']}  {rp_s}"
              f"  waters@age[{wa}] harv[{ha}]")

    print("STR census d10..d29:",
          {d: n for d, n in sorted(str_census.items()) if 10 <= d <= 29 and d % 2 == 0})
    print("target daily ops d14-29 (D=dig P=plant W=water H=harvest):")
    for day in range(14, 30):
        c = ops[(pid, day)]
        o = ops[(1 - pid, day)]
        print(f"  d{day:>2}: us D{c['DIG']:>2} P{c['PLANT']:>2} W{c['WATER']:>3} "
              f"H{c['HARVEST']:>3} | opp D{o['DIG']:>2} P{o['PLANT']:>2} "
              f"W{o['WATER']:>3} H{o['HARVEST']:>3}")
    tot = Counter()
    for day, c in sells.items():
        tot.update(c)
    late = Counter()
    for day, c in sells.items():
        if day >= 15:
            late.update(c)
    print("SELLS total:", dict(tot))
    print("SELLS d15+:", dict(late))


def main():
    src, target = sys.argv[1], sys.argv[2]
    if target.isdigit():
        target = int(target)
    files = [src] if os.path.isfile(src) else sorted(glob.glob(os.path.join(src, "*.json")))
    for f in files:
        decode(f, target)


if __name__ == "__main__":
    main()
