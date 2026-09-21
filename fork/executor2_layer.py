

# EXECUTOR fp8 — WHOLE-DAY ROUTE SCHEDULER (spec: fork/EXECUTOR_SPEC.md;
# supersedes fp1-fp7's hourly greedy core in executor_layer.py).
# fp7 verdict: hourly re-deciding topped out at 75-95 ops/day vs the tape's
# ~127 (walking dominated).  fp8 computes each day's COMPLETE schedule at
# hour 0 — every job on the board, tiles partitioned into contiguous column
# regions, one serpentine route per unit, ALL jobs on a tile chained before
# moving (the walking law) — hours then just execute the route.
# Kept from fp1-fp7 (each paid for by a falsification): permanent takeover
# (positional-tape law), parent market kept + append-only (ORDERPRI2),
# courier-first feed chain (herd starvation), inert tiles never watered,
# replant + daily seed floors (board drain), PLANT collective validation.
_E2_DON = 22
_E2_PLANT_TO = 26
_E2_MAX_PLANTS = 55
_E2_ACCESS = [(4, 4), (5, 4), (4, 5), (5, 5)]
_E2_CAP = {"COW": 6, "SHEEP": 6, "GOOSE": 4}
_E2_TELEM = {"feeds": 0, "cares": 0, "waters": 0, "harvs": 0, "digs": 0,
             "plants": 0, "collects": 0, "pickups": 0, "drops": 0,
             "seed_buys": 0, "feed_buys": 0, "moves": 0, "idle": 0,
             "replans": 0, "spilled_tiles": 0, "errors": 0}
_E2_STATE = {}


def _e2_scan(tiles, day):
    """Per-tile ordered job lists + board facts."""
    jobs = {}          # (x,y) -> [job,...]  job = ["VERB"] or ["PLANT",crop]
    animal_tiles, n_plants, empties = [], 0, []
    for y in range(10):
        for x in range(10):
            t = tiles[y][x]
            if t is None:
                if (x, y) not in _E2_ACCESS:
                    empties.append((x, y))
                continue
            if not isinstance(t, dict):
                continue
            j = []
            if t.get("kind") == "PLANT":
                n_plants += 1
                yu = int(t.get("yield_units", 0))
                age = day - int(t.get("planted_day", day))
                inert = yu == 0 and age > 6
                if inert and day <= _E2_PLANT_TO:
                    j += [["DIG"], ["PLANT", None], ["WATER"]]  # chained
                else:
                    if yu > 0 and age >= 2:
                        j.append(["HARVEST"])
                    if not t.get("watered_today") and not inert:
                        j.append(["WATER"])
            elif "animal" in t:
                animal_tiles.append((x, y))
                if not t.get("fed_today"):
                    j.append(["FEED"])
                if not t.get("cared_today"):
                    j.append(["CARE"])
                if t.get("fertilizer_available"):
                    j.append(["COLLECT_FERTILIZER"])
                yu = int(t.get("yield_units", 0))
                if yu >= _E2_CAP.get(t["animal"], 6) - 1 or (day >= 28 and yu > 0):
                    j.append(["HARVEST"])
            if j:
                jobs[(x, y)] = j
    return jobs, animal_tiles, n_plants, empties


def _e2_plan(seat, obs, day):
    """Build the whole-day plan: courier owns the animal cluster; other
    units own contiguous column bands, serpentine tile order."""
    farm = obs["farms"][seat]
    tiles = farm["tiles"]
    seeds = obs.get("private", {}).get("seeds", {})
    hands = farm.get("hands", [])
    n_u = 1 + len(hands)
    pos = [tuple(farm.get("farmer", (4, 4)))] + [tuple(h) for h in hands]

    jobs, animal_tiles, n_plants, empties = _e2_scan(tiles, day)

    # replants on empty tiles while capacity + season allow (chained water)
    avail = {"CARROT": int(seeds.get("CARROT", 0)),
             "WHEAT": int(seeds.get("WHEAT", 0))}
    # plan-time seeds understate the day (the daily floor buys land during
    # h0-2); plan PLANT jobs against seeds + the floors — the executor
    # already waits at the tile when a seed hasn't arrived yet.
    budget = sum(avail.values()) + 12
    if day <= _E2_PLANT_TO:
        for (x, y) in sorted(empties):
            if budget <= 0 or n_plants >= _E2_MAX_PLANTS:
                break
            jobs[(x, y)] = [["PLANT", None], ["WATER"]]
            n_plants += 1
            budget -= 1

    unlocked_access = [p for p in _E2_ACCESS if tiles[p[1]][p[0]] != "LOCKED"]
    ax, ay = unlocked_access[0] if unlocked_access else (4, 4)

    # campers: the animal cluster is ~35-45 job-hours (17 animals x feed/
    # care/collect/harvest) — more than one unit-day.  1 camper per ~8
    # animal tiles, each starts with a wheat PICKUP (courier-first law).
    routes = {i: [] for i in range(n_u)}
    campers = []
    if animal_tiles:
        n_camp = min(max(1, -(-len(animal_tiles) // 8)), max(1, n_u - 1))
        by_dist = sorted(range(n_u),
                         key=lambda i: abs(pos[i][0] - ax) + abs(pos[i][1] - ay))
        campers = by_dist[:n_camp]
        anim_sorted = sorted(animal_tiles,
                             key=lambda p: (p[0], p[1] if p[0] % 2 == 0
                                            else 9 - p[1]))
        share = -(-len(anim_sorted) // n_camp)
        for k, i in enumerate(campers):
            mine = [p for p in anim_sorted[k * share:(k + 1) * share]
                    if p in jobs]
            n_feeds = sum(1 for p in mine
                          if any(j == ["FEED"] for j in jobs[p]))
            routes[i] = ([("SHED", ax, ay,
                           [["PICKUP", "WHEAT", min(n_feeds + 2, 12)]])]
                         + [(None, x, y, list(jobs[(x, y)])) for (x, y) in mine])
        for p in anim_sorted:
            jobs.pop(p, None)

    # field units: contiguous column bands over remaining job tiles
    field_units = [i for i in range(n_u) if i not in campers]
    tile_list = sorted(jobs.keys(),
                       key=lambda p: (p[0], p[1] if p[0] % 2 == 0
                                      else 9 - p[1]))
    if field_units and tile_list:
        # balance by job count: split the serpentine tile sequence into
        # len(field_units) chunks of ~equal total jobs
        total = sum(len(jobs[p]) for p in tile_list)
        per = max(1, -(-total // len(field_units)))
        k, acc = 0, 0
        chunks = [[] for _ in field_units]
        for p in tile_list:
            if acc >= per and k < len(field_units) - 1:
                k += 1
                acc = 0
            chunks[k].append(p)
            acc += len(jobs[p])
        # assign chunks to units by proximity of chunk start (h0 positions
        # cluster at the shed spawn, so order barely matters; keep stable)
        for k, i in enumerate(field_units):
            routes[i] = [(None, x, y, list(jobs[(x, y)]))
                         for (x, y) in chunks[k]] if k < len(chunks) else []

    return {"day": day, "routes": routes, "idx": {i: 0 for i in range(n_u)},
            "planted": 0}


_E2_PARENT = agent
def agent(observation, configuration=None):
    action = _E2_PARENT(observation, configuration)
    try:
        day = int(observation.get("day", 0))
        if day < _E2_DON or not isinstance(action, dict):
            return action
        hour = int(observation.get("hour", 0))
        seat = int(observation.get("player", 0))
        farm = observation["farms"][seat]
        tiles = farm["tiles"]
        priv = observation.get("private", {})
        shed = priv.get("shed", {})
        seeds = dict(priv.get("seeds", {}))
        invs = priv.get("inventories") or []
        hands = farm.get("hands", [])
        n_u = 1 + len(hands)
        pos = [tuple(farm.get("farmer", (4, 4)))] + [tuple(h) for h in hands]
        carry = [dict(invs[i]) if i < len(invs) and invs[i] else {}
                 for i in range(n_u)]

        st = _E2_STATE.get(seat)
        # replan on a new day AND whenever the crew grows: the tape's morning
        # HIREs execute during h0-3, so the h0 plan sees only the farmer
        # (fp8 first fingerprint: 11 hands idled all day, waters 0).
        if st is None or st.get("day") != day or len(st["routes"]) < n_u:
            st = _E2_STATE[seat] = _e2_plan(seat, observation, day)
            _E2_TELEM["replans"] += 1

        routes, idx = st["routes"], st["idx"]
        units = [["PASS"] for _ in range(n_u)]
        # PLANT collective validation: plants emitted THIS TURN per crop
        # must be <= seeds held now.  Track per-crop budget this hour.
        plant_budget = {"CARROT": int(seeds.get("CARROT", 0)),
                        "WHEAT": int(seeds.get("WHEAT", 0))}
        plants_this_turn = {"CARROT": 0, "WHEAT": 0}

        axy = [p for p in _E2_ACCESS if tiles[p[1]][p[0]] != "LOCKED"]
        shed_xy = axy[0] if axy else (4, 4)

        def job_valid(x, y, job):
            t = tiles[y][x]
            v = job[0]
            if v == "PICKUP":
                return True     # empty shed -> WAIT there (feed buys restock)
            if v == "PLANT":
                return t is None
            if not isinstance(t, dict):
                return False
            if v == "WATER":
                return not t.get("watered_today")
            if v == "FEED":
                return "animal" in t and not t.get("fed_today")
            if v == "CARE":
                return "animal" in t and not t.get("cared_today")
            if v == "COLLECT_FERTILIZER":
                return bool(t.get("fertilizer_available"))
            if v == "HARVEST":
                return int(t.get("yield_units", 0)) > 0
            if v == "DIG":
                return t.get("kind") == "PLANT"
            return False

        for i in range(n_u):
            route = routes.get(i, [])
            acted = False
            while idx.get(i, 0) < len(route):
                _tag, tx, ty, jlist = route[idx[i]]
                # drop finished/invalid jobs at the current tile
                while jlist and not job_valid(tx, ty, jlist[0]):
                    jlist.pop(0)
                if not jlist:
                    idx[i] += 1
                    continue
                job = jlist[0]
                if pos[i] != (tx, ty):
                    x, y = pos[i]
                    units[i] = ["EAST" if tx > x else "WEST" if tx < x
                                else "SOUTH" if ty > y else "NORTH"]
                    _E2_TELEM["moves"] += 1
                    acted = True
                    break
                v = job[0]
                if v == "FEED" and carry[i].get("WHEAT", 0) <= 0:
                    # out of wheat mid-route: refill at the shed and come
                    # back (popping here starved the herd: fingerprint 2
                    # fed 49 of 136 and the animals died 17->5)
                    feeds_left = sum(1 for e in route[idx[i]:]
                                     for jj in e[3] if jj and jj[0] == "FEED")
                    route.insert(idx[i], ("SHED", shed_xy[0], shed_xy[1],
                                          [["PICKUP", "WHEAT",
                                            min(feeds_left + 1, 12)]]))
                    continue
                if v == "PLANT":
                    crop = job[1]
                    if crop is None:
                        crop = "CARROT" if (plant_budget["CARROT"]
                                            - plants_this_turn["CARROT"]) > 0 \
                            else ("WHEAT" if (plant_budget["WHEAT"]
                                              - plants_this_turn["WHEAT"]) > 0
                                  else None)
                    if crop is None or (plant_budget[crop]
                                        - plants_this_turn[crop]) <= 0:
                        # wait on this tile for seeds (market append below
                        # restocks); waiting is cheap, walking is not
                        acted = True
                        break
                    units[i] = ["PLANT", crop]
                    plants_this_turn[crop] += 1
                    _E2_TELEM["plants"] += 1
                    jlist.pop(0)
                    acted = True
                    break
                if v == "PICKUP":
                    if int(shed.get("WHEAT", 0)) <= 0:
                        # wait at the shed for the feed buy to land
                        acted = True
                        break
                    units[i] = ["PICKUP", "WHEAT", job[2]]
                    _E2_TELEM["pickups"] += 1
                    jlist.pop(0)
                    acted = True
                    break
                units[i] = [v]
                _E2_TELEM[{"FEED": "feeds", "CARE": "cares", "WATER": "waters",
                           "HARVEST": "harvs", "DIG": "digs",
                           "COLLECT_FERTILIZER": "collects"}[v]] += 1
                jlist.pop(0)
                acted = True
                break
            if not acted:
                # route done: evening cargo, else idle in place
                if hour >= 21 and sum(carry[i].values()) > 0:
                    axy = [p for p in _E2_ACCESS
                           if tiles[p[1]][p[0]] != "LOCKED"]
                    if axy:
                        ax, ay = axy[0]
                        if pos[i] == (ax, ay):
                            room = 100 - sum(int(x) for x in shed.values())
                            if room > sum(carry[i].values()):
                                units[i] = ["DROP"]
                                _E2_TELEM["drops"] += 1
                        else:
                            x, y = pos[i]
                            units[i] = ["EAST" if ax > x else "WEST" if ax < x
                                        else "SOUTH" if ay > y else "NORTH"]
                            _E2_TELEM["moves"] += 1
                        continue
                _E2_TELEM["idle"] += 1

        # ---- market appends (kept from fp5/fp7, proven) ----
        market = [list(o) for o in (action.get("market") or [])]
        if day <= 27 and farm.get("money", 0) > 1200:
            for crop, floor_n in (("WHEAT", 10), ("CARROT", 8)):
                held = int(seeds.get(crop, 0))
                if held < floor_n and len(market) < 10 and \
                        not any(o[:2] == ["BUY_SEED", crop] for o in market):
                    market.append(["BUY_SEED", crop, floor_n - held])
                    _E2_TELEM["seed_buys"] += 1
        n_animals = sum(1 for y in range(10) for x in range(10)
                        if isinstance(tiles[y][x], dict)
                        and "animal" in tiles[y][x])
        wheat_stock = int(shed.get("WHEAT", 0)) + \
            sum(c.get("WHEAT", 0) for c in carry)
        if wheat_stock < n_animals + 2 and day < 29 and len(market) < 10 \
                and farm.get("money", 0) > 1000 \
                and not any(o[:2] == ["BUY_PRODUCT", "WHEAT"] for o in market):
            market.append(["BUY_PRODUCT", "WHEAT",
                           min(n_animals + 4 - wheat_stock, 12)])
            _E2_TELEM["feed_buys"] += 1
        return dict(action, farmer=units[0], hands=units[1:],
                    market=market[:10])
    except Exception:
        _E2_TELEM["errors"] += 1
        return action
agent.telemetry = _E2_TELEM
agent = globals().pop("agent")
