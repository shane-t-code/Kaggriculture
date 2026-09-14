"""Labor-engine decode: unit-turn accounting, us vs opponent, same live games.

For every decoded detonator game (results/decodes/choreo_melon.jsonl):
  - classify every unit-turn: MOVE / WORK (by op) / IDLE (PASS or missing)
  - by day-phase and hour-of-day
  - for OUR idle turns: what work was available on the board that hour
    (unwatered live crop, unfed/uncared animal, ready harvest, fert on
    pasture uncollected, in-window STR unfertilized with supply on hand)
    -> the "idle-with-work" histogram BY MISSED OP = the port list.
  - same availability scan for their idle turns (do they idle only when
    nothing is left?)

Usage: python tools/choreo_idle.py
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


def phase(day):
    if day <= 4:
        return "d0-4"
    if day <= 9:
        return "d5-9"
    if day <= 14:
        return "d10-14"
    if day <= 21:
        return "d15-21"
    return "d22-29"


def avail_work(tiles, day, fert_supply):
    """What op classes are still doable on this board right now."""
    out = set()
    for row in tiles:
        for t in row:
            if not isinstance(t, dict):
                continue
            if t.get("animal"):
                if not t.get("fed_today"):
                    out.add("FEED")
                if not t.get("cared_today"):
                    out.add("CARE")
                if t.get("fertilizer_available"):
                    out.add("COLLECT_FERT")
                continue
            crop = t.get("crop")
            if crop:
                if not t.get("watered_today"):
                    out.add("WATER")
                if t.get("yield_units", 0) > 0 and crop in ("STRAWBERRY", "WHEAT",
                                                            "TOMATO", "CARROT"):
                    out.add("HARVEST")
                if (crop == "STRAWBERRY" and fert_supply > 0
                        and t.get("fertilized_until_day", -1) < day):
                    age = day - t.get("planted_day", day)
                    if 7 <= age <= 15:
                        out.add("FERT_STR")
    return out


def main():
    cnt = defaultdict(lambda: defaultdict(float))     # (side) -> class of turn
    ph = defaultdict(lambda: defaultdict(float))      # (side, phase) -> idle/total
    hh = defaultdict(lambda: defaultdict(float))      # (side) -> hour -> idle
    missed = defaultdict(lambda: defaultdict(float))  # side -> op -> idle turns w/ that op available
    ngames = 0
    for d in DIRS:
        for f in glob.glob(os.path.join(d, "*.json")):
            ep = os.path.basename(f).split("-")[1]
            if ep not in klass_by_ep:
                continue
            blob = json.load(open(f, encoding="utf-8"))
            names = blob["info"]["TeamNames"]
            me = names.index(ME)
            steps = blob["steps"]
            ngames += 1
            for side, seat in (("us", me), ("them", 1 - me)):
                for t in range(len(steps) - 1):
                    o = steps[t][seat]["observation"]
                    day, hour = o["day"], o["hour"]
                    farm = o["farms"][seat]
                    act = steps[t + 1][seat].get("action") or {}
                    verbs = [act.get("farmer") or ["PASS"]] + list(act.get("hands") or [])
                    n_units = 1 + len(farm.get("hands") or [])
                    priv = o["private"]
                    fs = priv["shed"].get("FERTILIZER", 0) + sum(
                        i.get("FERTILIZER", 0) for i in priv["inventories"])
                    aw = None
                    for i in range(n_units):
                        v = verbs[i][0] if i < len(verbs) and verbs[i] else "PASS"
                        if v in MOVES:
                            k = "move"
                        elif v in WORK:
                            k = "work"
                        else:
                            k = "idle"
                        cnt[side][k] += 1
                        ph[(side, phase(day))]["tot"] += 1
                        if k == "idle":
                            ph[(side, phase(day))]["idle"] += 1
                            hh[side][hour] += 1
                            if aw is None:
                                aw = avail_work(farm["tiles"], day, fs)
                            if aw:
                                missed[side]["ANY"] += 1
                                for op in aw:
                                    missed[side][op] += 1
                            else:
                                missed[side]["nothing-left"] += 1

    print(f"games: {ngames} (both sides each)")
    for side in ("us", "them"):
        c = cnt[side]
        tot = sum(c.values())
        print(f"\n===== {side.upper()} — unit-turns/game {tot/ngames:.0f} =====")
        print(f"  move {c['move']/tot:.1%} | work {c['work']/tot:.1%} | idle {c['idle']/tot:.1%}")
        for p in ("d0-4", "d5-9", "d10-14", "d15-21", "d22-29"):
            r = ph[(side, p)]
            print(f"  {p:>7}: idle {r['idle']/max(1,r['tot']):.1%} ({r['idle']/ngames:.0f}/game)")
        top = sorted(hh[side].items(), key=lambda kv: -kv[1])[:6]
        print("  idle by hour (top):", [(h, round(v/ngames, 1)) for h, v in top])
        m = missed[side]
        print(f"  idle turns with work available: {m['ANY']/ngames:.0f}/game "
              f"vs truly-nothing-left {m['nothing-left']/ngames:.0f}/game")
        print("  available-op histogram during idle (turns/game):",
              {k: round(v/ngames, 1) for k, v in sorted(m.items(), key=lambda kv: -kv[1])
               if k not in ("ANY", "nothing-left")})


if __name__ == "__main__":
    main()
