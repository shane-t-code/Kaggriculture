"""route_compiler.py — offline crop-program compiler v1 .

Enumerates STRAWBERRY-TILE TAKEOVER programs over the static route table:
for every ongoing-strawberry tile in every route, find a CLEAR slot (a
displaceable native op turned into DIG), a PLANT slot (a displaceable op
followed by a native WATER on the SAME tile LATER THE SAME DAY — plants
die if unwatered on plant day), and forward water coverage without two
consecutive dry days.  Emits fork/cv_programs.json for the runtime layer.

Spec: docs/COMPILER_PLAN.md.  Proof of mechanism: work//review2/.

Usage: python tools/route_compiler.py work//review2/routes_7000.json fork/cv_programs.json
"""
import json, sys
from collections import defaultdict

MOVES = {"NORTH": (0, -1), "SOUTH": (0, 1), "EAST": (1, 0), "WEST": (-1, 0)}
ACCESS = ((4, 4), (5, 4), (4, 5), (5, 5))
ONE_SHOT = {"WHEAT", "CARROT", "MELON"}
DISPLACEABLE = {"WATER", "FERTILIZE", "CARE", "PASS"}   # ops safe to repurpose on an str tile


def spawn(positions):
    occ = {a: 0 for a in ACCESS}
    for p in positions:
        if tuple(p) in occ:
            occ[tuple(p)] += 1
    return list(min(ACCESS, key=lambda a: (occ[a], ACCESS.index(a))))


def simulate(route_tape, tail_tape):
    """Yield (t, actor, pos, op, cmd) for every unit-turn of a route,
    honoring the step-648 switch to the shared tail route and the
    midnight position/hand reset."""
    positions = [[4, 4]]
    for t in range(719):
        act = (tail_tape if t >= 648 else route_tape)[t]
        if not isinstance(act, dict):
            act = {}
        units = [act.get("farmer") or ["PASS"]] + list(act.get("hands") or [])
        for i in range(len(positions)):
            cmd = units[i] if i < len(units) and units[i] else ["PASS"]
            op = cmd[0]
            if op in MOVES:
                dx, dy = MOVES[op]
                nx, ny = positions[i][0] + dx, positions[i][1] + dy
                if 0 <= nx < 10 and 0 <= ny < 10:
                    positions[i] = [nx, ny]
            else:
                yield t, i, tuple(positions[i]), op, cmd
        for _ in range(sum(1 for o in (act.get("market") or []) if o and o[0] == "HIRE")):
            positions.append(spawn(positions))
        if t % 24 == 23:
            positions = [[4, 4]]


def compile_route(rid, route_tape, tail_tape):
    # visit timeline + strawberry tile lifetimes
    visits = defaultdict(list)                 # tile -> [(t, actor, op)]
    str_planted = {}                            # tile -> planted step (open interval)
    intervals = defaultdict(list)               # tile -> [(t0, t1)] strawberry-occupied
    for t, actor, pos, op, cmd in simulate(route_tape, tail_tape):
        visits[pos].append((t, actor, op))
        if op == "PLANT" and len(cmd) > 1:
            if cmd[1] == "STRAWBERRY":
                str_planted[pos] = t
            elif pos in str_planted:            # replanted with something else
                intervals[pos].append((str_planted.pop(pos), t))
        elif op == "DIG" and pos in str_planted:
            intervals[pos].append((str_planted.pop(pos), t))
    for pos, t0 in str_planted.items():
        intervals[pos].append((t0, 719))

    programs = []
    for pos, spans in intervals.items():
        for (t0, t1) in spans:
            vs = [(t, a, op) for (t, a, op) in visits[pos] if t0 < t < t1]
            # plant slots: displaceable op with a WATER later the same day
            for k, (t, a, op) in enumerate(vs):
                day = t // 24
                if day < 10 or day > 26 or op not in DISPLACEABLE:
                    continue
                same_day_water = next((t2 for (t2, a2, op2) in vs[k + 1:]
                                       if t2 // 24 == day and op2 == "WATER"), None)
                if same_day_water is None:
                    continue
                # clear slot: the latest displaceable-or-HARVEST visit before t,
                # v2: at most 24 steps earlier (short armed window — note,
                # the naked-dig class: dig whose plant later fails)
                clear = next(((tc, ac, oc) for (tc, ac, oc) in reversed(vs[:k])
                              if t - tc <= 24 and oc in ("HARVEST", "WATER", "FERTILIZE", "CARE")), None)
                if clear is None:
                    continue
                # survival: visit-day coverage day+1..day+3 with no 2-day gap
                wdays = {t2 // 24 for (t2, a2, op2) in vs if op2 in ("WATER", "FERTILIZE", "HARVEST") and t2 > t}
                if any(d not in wdays and d + 1 not in wdays for d in (day + 1, day + 2)):
                    continue
                harvestable = sorted(d for d in wdays if day + 2 <= d <= day + 5)
                if not harvestable:
                    continue
                # v2 displaced-value proxy: native HARVEST visits we forfeit
                # between our plant and the interval's natural end (t1 = the
                # native's own dig/replant — production after that was never
                # ours to displace).  Wrong-forecast insurance = pick minimal.
                displaced_harvests = sum(1 for (t2, a2, op2) in vs if op2 == "HARVEST" and t2 > t)
                programs.append({
                    "tile": list(pos),
                    "clear": {"step": clear[0], "actor": clear[1], "orig": clear[2]},
                    "plant": {"step": t, "actor": a, "orig": op},
                    "water_days": sorted(wdays),
                    "harvest_days": harvestable,
                    "displaced": "STRAWBERRY",
                    "displaced_harvests": displaced_harvests,
                    "interval_end": t1,
                })
    # per tile keep one program; per route optionally keep only the
    # least-destructive tiles (MAX_TILES=0 keeps all).
    best = {}
    for p in programs:
        key = tuple(p["tile"])
        if PICK == "mindisp":
            rank = (p["displaced_harvests"], -p["plant"]["step"])
            old = best.get(key)
            if old is None or rank < (old["displaced_harvests"], -old["plant"]["step"]):
                best[key] = p
        else:  # earliest plant = longest carrot window
            if key not in best or p["plant"]["step"] < best[key]["plant"]["step"]:
                best[key] = p
    keep = sorted(best.values(), key=lambda p: (p["displaced_harvests"], p["plant"]["step"]))
    if MAX_TILES:
        keep = keep[:MAX_TILES]
    return sorted(keep, key=lambda p: p["plant"]["step"])


PICK = "mindisp"
MAX_TILES = 8


def main():
    global PICK, MAX_TILES
    routes_path, out_path = sys.argv[1], sys.argv[2]
    if len(sys.argv) > 3:
        MAX_TILES = int(sys.argv[3])
    if len(sys.argv) > 4:
        PICK = sys.argv[4]
    routes = json.load(open(routes_path, encoding="utf-8"))
    tail = routes["2"]
    table = {}
    total = 0
    for rid in sorted(routes, key=int):
        progs = compile_route(rid, routes[rid], tail)
        if progs:
            table[rid] = progs
            total += len(progs)
    json.dump(table, open(out_path, "w", encoding="utf-8"), indent=1)
    sizes = {rid: len(p) for rid, p in table.items()}
    print(f"compiled {total} programs across {len(table)}/{len(routes)} routes -> {out_path}")
    print("per-route counts:", sizes)


if __name__ == "__main__":
    main()
