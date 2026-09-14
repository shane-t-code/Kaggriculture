"""Early-game (d0-9) idle decode: WHY do our units pass while work sits available?

For each live detonator game, days 0-9, OUR side:
  - idle turns by (day, hour) and by unit index (farmer=0)
  - for each idle unit-turn: what the unit held, whether it stood ON a tile
    with doable work, nearest doable-work distance, and which op classes
    were available anywhere
  - hire timeline: hands present by day (are idle turns pre-work or
    post-work-exhaustion?)
Also the opponent's same-phase profile for contrast (what their units DO
in d0-9: op mix by day).

Usage: python tools/choreo_idle_early.py
"""
import json, glob, os
from collections import defaultdict

ME = "Shane Thivaharraja"
DIRS = [
    r"C:\Kaggriculture\replays\live_v71c_sep13",
    r"C:\Kaggriculture\replays\live_v70c_sep13",
    r"C:\Kaggriculture\replays\live_v67c",
]
WORK = {"HARVEST", "FEED", "CARE", "WATER", "PLANT", "FERTILIZE",
        "COLLECT_FERTILIZER", "BUILD_COOP", "BUILD_PASTURE", "PICKUP",
        "PLACE", "DROP", "DIG"}
MOVES = {"NORTH", "SOUTH", "EAST", "WEST"}

klass_by_ep = {}
for line in open(r"C:\Kaggriculture\results\decodes\choreo_melon.jsonl"):
    r = json.loads(line)
    klass_by_ep[r["ep"]] = r["klass"]


def doable(t):
    """Op classes doable standing on tile t right now."""
    ops = set()
    if not isinstance(t, dict):
        return ops
    if t.get("animal"):
        if not t.get("fed_today"):
            ops.add("FEED")
        if not t.get("cared_today"):
            ops.add("CARE")
        if t.get("fertilizer_available"):
            ops.add("COLLECT")
    elif t.get("crop"):
        if not t.get("watered_today"):
            ops.add("WATER")
    return ops


def main():
    idle_dh = defaultdict(float)          # (day) -> idle turns
    idle_hour = defaultdict(float)        # hour -> idle turns (d0-9)
    idle_unit = defaultdict(float)        # unit idx -> idle
    on_tile_work = 0.0                    # idle while standing ON doable work
    near = defaultdict(float)             # nearest-doable-distance bucket
    idle_loaded = 0.0
    idle_total = 0.0
    opp_ops = defaultdict(lambda: defaultdict(float))  # day -> op -> count
    us_ops = defaultdict(lambda: defaultdict(float))
    hands_by_day = defaultdict(lambda: [0.0, 0])
    n = 0
    for d in DIRS:
        for f in glob.glob(os.path.join(d, "*.json")):
            ep = os.path.basename(f).split("-")[1]
            if ep not in klass_by_ep:
                continue
            blob = json.load(open(f, encoding="utf-8"))
            names = blob["info"]["TeamNames"]
            me = names.index(ME)
            steps = blob["steps"]
            n += 1
            for t in range(0, 10 * 24):
                for side, seat in (("us", me), ("them", 1 - me)):
                    o = steps[t][seat]["observation"]
                    day, hour = o["day"], o["hour"]
                    farm = o["farms"][seat]
                    tiles = farm["tiles"]
                    act = steps[t + 1][seat].get("action") or {}
                    verbs = [act.get("farmer") or ["PASS"]] + list(act.get("hands") or [])
                    upos = [farm.get("farmer")] + list(farm.get("hands") or [])
                    if side == "us" and hour == 12:
                        hands_by_day[day][0] += len(farm.get("hands") or [])
                        hands_by_day[day][1] += 1
                    for ui, pos in enumerate(upos):
                        v = verbs[ui][0] if ui < len(verbs) and verbs[ui] else "PASS"
                        book = us_ops if side == "us" else opp_ops
                        book[day][v if v in WORK else ("MOVE" if v in MOVES else "IDLE")] += 1
                        if side != "us" or v in WORK or v in MOVES:
                            continue
                        # our idle turn
                        idle_total += 1
                        idle_dh[day] += 1
                        idle_hour[hour] += 1
                        idle_unit[min(ui, 9)] += 1
                        priv = o["private"]
                        inv = (priv["inventories"][ui]
                               if ui < len(priv["inventories"]) else {})
                        if sum(inv.values()) > 0:
                            idle_loaded += 1
                        ux, uy = int(pos[0]), int(pos[1])
                        here = doable(tiles[uy][ux]) if 0 <= ux < 10 and 0 <= uy < 10 else set()
                        if here:
                            on_tile_work += 1
                        best = 99
                        for y, row in enumerate(tiles):
                            for x, tl in enumerate(row):
                                if doable(tl):
                                    dd = abs(x - ux) + abs(y - uy)
                                    if dd < best:
                                        best = dd
                        b = ("0" if best == 0 else "1-2" if best <= 2 else
                             "3-5" if best <= 5 else "6+" if best < 99 else "none")
                        near[b] += 1

    print(f"games: {n} | OUR d0-9 idle turns/game: {idle_total/n:.0f} "
          f"(loaded while idle: {idle_loaded/idle_total:.0%})")
    print("idle by day:", {k: round(v/n, 1) for k, v in sorted(idle_dh.items())})
    print("idle by hour:", {k: round(v/n, 1) for k, v in sorted(idle_hour.items())})
    print("idle by unit (0=farmer):", {k: round(v/n, 1) for k, v in sorted(idle_unit.items())})
    print(f"idle STANDING ON doable work: {on_tile_work/idle_total:.0%}")
    print("nearest doable work while idle:", {k: round(v/n, 1) for k, v in sorted(near.items())})
    print("\nour hands by day:", {d: round(s/c, 1) for d, (s, c) in sorted(hands_by_day.items())})
    print("\nop mix by day (ours vs theirs, work ops only):")
    for day in range(10):
        u = us_ops[day]; p = opp_ops[day]
        uw = sum(v for k, v in u.items() if k in WORK) / n
        pw = sum(v for k, v in p.items() if k in WORK) / n
        ui_ = u.get("IDLE", 0) / n; pi = p.get("IDLE", 0) / n
        um = u.get("MOVE", 0) / n; pm = p.get("MOVE", 0) / n
        print(f"  d{day}: us work {uw:5.1f} move {um:5.1f} idle {ui_:5.1f} | "
              f"them work {pw:5.1f} move {pm:5.1f} idle {pi:5.1f}")


if __name__ == "__main__":
    main()
