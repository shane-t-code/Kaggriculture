

# EXECUTOR v108a (spec: fork/EXECUTOR_SPEC.md). Permanent takeover of ALL
# unit actions from day _EX_DON; parent's market kept (reactive reflexes +
# hires), executor appends seed/feed buys. Rules GUARANTEE feed/care/water/
# harvest; recycling (dig inert -> plant carrot) uses only proven slack.
# FERTILIZE tier deferred to v2 (carried-fert chain complexity).
_EX_DON = 22
_EX_PLANT_TO = 26
_EX_MAX_PLANTS = 55         # top-10 run ~50-60 planted tiles on 11 hands
_EX_TELEM = {"feeds": 0, "cares": 0, "waters": 0, "harvs": 0, "digs": 0,
             "plants": 0, "collects": 0, "pickups": 0, "drops": 0,
             "seed_buys": 0, "feed_buys": 0, "moves": 0, "idle": 0,
             "errors": 0}
_EX_ACCESS = [(4, 4), (5, 4), (4, 5), (5, 5)]
_EX_CAP = {"COW": 6, "SHEEP": 6, "GOOSE": 4}
_EX_STATE = {}   # seat -> {"day": d, "assign": {unit_i: (kind, tx, ty, crop)}}
_EX_KEY = {"FEED": "feeds", "CARE": "cares", "WATER": "waters",
           "HARVEST": "harvs", "COLLECT_FERTILIZER": "collects",
           "DIG": "digs", "PLANT": "plants"}

_EX_PARENT = agent
def agent(observation, configuration=None):
    action = _EX_PARENT(observation, configuration)
    try:
        day = int(observation.get("day", 0))
        if day < _EX_DON or not isinstance(action, dict):
            return action
        hour = int(observation.get("hour", 0))
        seat = int(observation.get("player", 0))
        farm = observation["farms"][seat]
        tiles = farm["tiles"]
        priv = observation.get("private", {})
        shed = priv.get("shed", {})
        seeds = priv.get("seeds", {})
        invs = priv.get("inventories") or []
        hands = farm.get("hands", [])
        n_u = 1 + len(hands)
        pos = [tuple(farm.get("farmer", (4, 4)))] + [tuple(h) for h in hands]
        carry = [dict(invs[i]) if i < len(invs) and invs[i] else {}
                 for i in range(n_u)]
        unlocked_access = [p for p in _EX_ACCESS
                           if tiles[p[1]][p[0]] != "LOCKED"]

        # ---- scan board ----
        feed_t, care_t, water_t, harv_t, coll_t, dig_t, empty_t = \
            [], [], [], [], [], [], []
        n_plants = 0
        for y in range(10):
            for x in range(10):
                t = tiles[y][x]
                if not isinstance(t, dict):
                    continue
                if t.get("kind") == "PLANT":
                    n_plants += 1
                    yu = int(t.get("yield_units", 0))
                    age = day - int(t.get("planted_day", day))
                    inert = yu == 0 and age > 6
                    if yu > 0 and age >= 2:
                        harv_t.append((x, y))
                    # inert tiles never get water (they can't weed, can't
                    # yield — watering them starved the live wheat: 73
                    # waters/game all spent on dead STR in fingerprint 2)
                    if not t.get("watered_today") and not inert:
                        water_t.append((x, y))
                    if inert and day <= _EX_PLANT_TO:
                        dig_t.append((x, y))
                elif "animal" in t:
                    a = t["animal"]
                    yu = int(t.get("yield_units", 0))
                    if not t.get("fed_today"):
                        feed_t.append((x, y))
                    if not t.get("cared_today"):
                        care_t.append((x, y))
                    if yu >= _EX_CAP.get(a, 6) - 1 or (day >= 28 and yu > 0):
                        harv_t.append((x, y))
                    if t.get("fertilizer_available"):
                        coll_t.append((x, y))
                elif t is None:
                    pass
        for y in range(10):
            for x in range(10):
                if tiles[y][x] is None and (x, y) not in _EX_ACCESS:
                    empty_t.append((x, y))

        units = [["PASS"] for _ in range(n_u)]
        busy = [False] * n_u
        taken = set()
        st = _EX_STATE.get(seat)
        if st is None or st.get("day") != day:
            st = _EX_STATE[seat] = {"day": day, "assign": {}}
        assign = st["assign"]

        def step_toward(i, tx, ty):
            x, y = pos[i]
            units[i] = ["EAST" if tx > x else "WEST" if tx < x
                        else "SOUTH" if ty > y else "NORTH"]
            _EX_TELEM["moves"] += 1

        def do(i, tx, ty, cmd, key, sticky=None):
            if pos[i] == (tx, ty):
                units[i] = cmd
                _EX_TELEM[key] += 1
                assign.pop(i, None)          # task executes: free next hour
            else:
                step_toward(i, tx, ty)
                if sticky:
                    assign[i] = sticky       # keep walking to THIS task
            busy[i] = True
            taken.add((tx, ty))

        # SAME-TILE FIRST (the walking law: finish the tile you stand on —
        # fingerprint 3 measured 3 walks/op, 64 ops/day vs the tape's 127):
        # any unit standing on a tile with pending work does it NOW.
        tile_q = {}
        for lst, kind in ((feed_t, "FEED"), (care_t, "CARE"),
                          (harv_t, "HARVEST"),
                          (coll_t, "COLLECT_FERTILIZER"),
                          (water_t, "WATER")):
            for p in lst:
                tile_q.setdefault(p, []).append(kind)
        for i in range(n_u):
            p = pos[i]
            # never divert a unit already on a sticky errand (fp4: diverted
            # walkers collapsed watering to 51 and idled 332 unit-hours)
            if busy[i] or i in assign or p in taken or p not in tile_q:
                continue
            for kind in tile_q[p]:
                if kind == "FEED" and carry[i].get("WHEAT", 0) <= 0:
                    continue
                units[i] = [kind]
                _EX_TELEM[_EX_KEY[kind]] += 1
                busy[i] = True
                taken.add(p)
                assign.pop(i, None)
                break

        # STICKY REPLAY: units keep yesterday-hour's task while still valid
        # (fix for the thrash that weeded the farm: 1470 moves / 73 waters)
        still = {"FEED": set(feed_t), "CARE": set(care_t),
                 "WATER": set(water_t), "HARVEST": set(harv_t),
                 "COLLECT_FERTILIZER": set(coll_t), "DIG": set(dig_t)}
        for i, a in list(assign.items()):
            kind, tx, ty = a[0], a[1], a[2]
            if i >= n_u or (tx, ty) in taken:
                assign.pop(i, None)
                continue
            if kind == "PLANT":
                ok = tiles[ty][tx] is None
                cmd = ["PLANT", a[3]]
            else:
                ok = (tx, ty) in still.get(kind, set())
                cmd = [kind]
            if not ok:
                assign.pop(i, None)
                continue
            if kind == "FEED" and carry[i].get("WHEAT", 0) <= 0:
                assign.pop(i, None)
                continue
            do(i, tx, ty, cmd, _EX_KEY[kind], sticky=a)

        # ===== REGION-SWEEP SCHEDULER (fp6) =====
        # fp5 wall: greedy-nearest = ~75 ops/day at 3 walks/op vs tape 127.
        # Campers own the animal tiles (all four ops from the same square);
        # every other unit owns a column strip and sweeps it serpentine.
        animal_pos = {p for p in feed_t} | {p for p in care_t} | \
                     {p for p in coll_t}
        anim_yield = [p for p in harv_t if p in animal_pos or
                      isinstance(tiles[p[1]][p[0]], dict) and
                      "animal" in tiles[p[1]][p[0]]]
        anim_all = set(anim_yield) | animal_pos
        harv_plant = [p for p in harv_t if p not in anim_all]
        campers = [i for i in (1, 2, 3) if i < n_u]
        strippers = [i for i in range(n_u) if i not in campers]

        # COURIER FIRST (fp6: campers went busy on CARE, wheat got fetched
        # by strippers who may not FEED — herd starved with wheat in hand):
        # when herd is hungry and nobody carries wheat, a camper fetches NOW.
        nobody_carries = not any(carry[i].get("WHEAT", 0) > 0
                                 for i in range(n_u) if not busy[i])
        if feed_t and nobody_carries and int(shed.get("WHEAT", 0)) > 0 \
                and unlocked_access:
            free = [i for i in campers if not busy[i]] or \
                   [i for i in strippers if not busy[i]]
            if free:
                ax, ay = unlocked_access[0]
                i = min(free, key=lambda j: abs(pos[j][0] - ax)
                        + abs(pos[j][1] - ay))
                if pos[i] == (ax, ay):
                    units[i] = ["PICKUP", "WHEAT", min(len(feed_t) + 2, 8)]
                    _EX_TELEM["pickups"] += 1
                else:
                    step_toward(i, ax, ay)
                busy[i] = True
        # FEED: ANY unit carrying wheat may feed; then campers do the rest
        anim_tasks = ([("FEED", p) for p in feed_t]
                      + [("CARE", p) for p in care_t]
                      + [("COLLECT_FERTILIZER", p) for p in coll_t]
                      + [("HARVEST", p) for p in anim_yield])
        for kind, (tx, ty) in anim_tasks:
            if (tx, ty) in taken:
                continue
            if kind == "FEED":
                cand = [i for i in range(n_u) if not busy[i]
                        and carry[i].get("WHEAT", 0) > 0]
            else:
                cand = [i for i in campers if not busy[i]]
            if not cand:
                continue
            i = min(cand, key=lambda j: abs(pos[j][0] - tx)
                    + abs(pos[j][1] - ty))
            do(i, tx, ty, [kind], _EX_KEY[kind], sticky=(kind, tx, ty))

        # strippers: own columns, serpentine order, water > harvest > dig > plant
        avail = {"CARROT": int(seeds.get("CARROT", 0)),
                 "WHEAT": int(seeds.get("WHEAT", 0))}
        for a in assign.values():
            if a[0] == "PLANT":
                avail[a[3]] = avail.get(a[3], 0) - 1
        free_s = [i for i in strippers if not busy[i]]
        if free_s:
            ncols = max(1, (10 + len(free_s) - 1) // len(free_s))
            strip_of = {}
            for k, i in enumerate(sorted(free_s)):
                for c in range(k * ncols, min((k + 1) * ncols, 10)):
                    strip_of[c] = i
            can_plant = (day <= _EX_PLANT_TO and hour <= 19
                         and n_plants < _EX_MAX_PLANTS)
            field_tasks = ([("WATER", p) for p in water_t]
                           + [("HARVEST", p) for p in harv_plant]
                           + [("DIG", p) for p in dig_t if day <= _EX_PLANT_TO]
                           + ([("PLANT", p) for p in empty_t] if can_plant else []))
            field_tasks.sort(key=lambda kp: (
                {"WATER": 0, "HARVEST": 1, "DIG": 2, "PLANT": 3}[kp[0]],
                kp[1][0], kp[1][1] if kp[1][0] % 2 == 0 else 9 - kp[1][1]))
            spill = []
            for kind, (tx, ty) in field_tasks:
                if (tx, ty) in taken:
                    continue
                i = strip_of.get(tx)
                if i is None or busy[i]:
                    spill.append((kind, tx, ty))
                    continue
                if kind == "PLANT":
                    crop = "CARROT" if avail.get("CARROT", 0) > 0 else \
                        ("WHEAT" if avail.get("WHEAT", 0) > 0 else None)
                    if crop is None:
                        continue
                    if pos[i] == (tx, ty):
                        units[i] = ["PLANT", crop]
                        _EX_TELEM["plants"] += 1
                        assign.pop(i, None)
                    else:
                        step_toward(i, tx, ty)
                        assign[i] = ("PLANT", tx, ty, crop)
                    avail[crop] -= 1
                    busy[i] = True
                    taken.add((tx, ty))
                else:
                    do(i, tx, ty, [kind], _EX_KEY[kind], sticky=(kind, tx, ty))
            # spill: unclaimed tasks go to any free unit, nearest-first
            for kind, tx, ty in spill:
                if (tx, ty) in taken or kind == "PLANT":
                    continue
                cand = [i for i in range(n_u) if not busy[i]]
                if not cand:
                    break
                i = min(cand, key=lambda j: abs(pos[j][0] - tx)
                        + abs(pos[j][1] - ty))
                do(i, tx, ty, [kind], _EX_KEY[kind], sticky=(kind, tx, ty))
        # tier 7: evening cargo runs (only if shed has room)
        room = 100 - sum(int(v) for v in shed.values())
        if hour >= 21 and room > 5 and unlocked_access:
            ax, ay = unlocked_access[0]
            for i in range(n_u):
                if busy[i] or sum(carry[i].values()) == 0:
                    continue
                if pos[i] == (ax, ay):
                    units[i] = ["DROP"]
                    _EX_TELEM["drops"] += 1
                else:
                    step_toward(i, ax, ay)
                busy[i] = True
        _EX_TELEM["idle"] += sum(1 for i in range(n_u) if not busy[i])

        # ---- market appends ----
        market = [list(o) for o in (action.get("market") or [])]
        # fp5: the board drained (97 harvests / 24 plants) — replanting is
        # seed-bound. Top up BOTH crops hard, every day (top-10 buy seeds
        # through d27; empty_t auto-includes harvested tiles for replant).
        if day <= 27 and farm.get("money", 0) > 1200:
            for crop, floor_n in (("WHEAT", 10), ("CARROT", 8)):
                held = int(seeds.get(crop, 0))
                if held < floor_n and len(market) < 10 and \
                        not any(o[:2] == ["BUY_SEED", crop] for o in market):
                    market.append(["BUY_SEED", crop, floor_n - held])
                    _EX_TELEM["seed_buys"] += 1
        n_animals = sum(1 for y in range(10) for x in range(10)
                        if isinstance(tiles[y][x], dict)
                        and "animal" in tiles[y][x])
        wheat_stock = int(shed.get("WHEAT", 0)) + \
            sum(c.get("WHEAT", 0) for c in carry)
        if wheat_stock < n_animals and day < 29 and len(market) < 10 \
                and farm.get("money", 0) > 1000 \
                and not any(o[:2] == ["BUY_PRODUCT", "WHEAT"] for o in market):
            market.append(["BUY_PRODUCT", "WHEAT",
                           min(n_animals * 2 - wheat_stock, 10)])
            _EX_TELEM["feed_buys"] += 1
        return dict(action, farmer=units[0], hands=units[1:],
                    market=market[:10])
    except Exception:
        _EX_TELEM["errors"] += 1
        return action
agent.telemetry = _EX_TELEM
agent = globals().pop("agent")
