

# EXECUTOR fp9b — SUBSYSTEM PARTITION, net-positive crop scheduler.
# (fp9a validated the framework: herd frozen on tape via zero-remaining-
# animal-action claim = lossless, herd survives; but naive crop logic was a
# liquidator: −24.7k, plants 58→0, harvest-early + dig-no-replant.)
#
# fp9b principle: claimed hands must FIRST do everything the tape would have
# done with them today (the DUTY LIST, traced exactly from the tape's route:
# positions are relative, so tracing moves from the hand's claim-time
# position gives the exact tiles its WATER/HARVEST/PLANT would land on).
# Only leftover hours go to RECYCLING PROJECTS: DIG an inert tile, PLANT
# carrot, WATER it — 3 consecutive hours, same tile, same hand (satisfies
# the same-night weed law).  Our planted tiles live in a persistent registry
# and are serviced daily (water; harvest at maturity) with priority right
# after duties.  The tape never knows: its own units occasionally water our
# tiles for free when their route passes.
_E3_DON = 20
_E3_PLANT_TO = 26          # carrot needs ~2-3 days; plant ≤26 → harvest ≤29
_E3_MAX_OWN = 6           # registry cap: never plant more than we can water
_E3_ANIMAL_V = {"FEED", "CARE", "COLLECT_FERTILIZER", "PLACE"}
_E3_MOVES = {"EAST": (1, 0), "WEST": (-1, 0), "SOUTH": (0, 1), "NORTH": (0, -1)}
_E3_TELEM = {"claimed_hand_hours": 0, "duty_waters": 0, "duty_harvs": 0,
             "duty_plants": 0, "own_waters": 0, "own_harvs": 0,
             "digs": 0, "plants": 0, "seed_buys": 0, "route_miss": 0,
             "moves": 0, "idle": 0, "proj_started": 0, "errors": 0}
_E3_STATE = {}


def _e3_routes():
    try:
        return _IMPL.chassis.routes
    except Exception:
        return None


def _e3_active_route(seat):
    try:
        r = _IMPL.chassis.players.get(seat, {}).get("route")
        if r is not None and r in _IMPL.chassis.routes:
            return r
    except Exception:
        pass
    return None


def _e3_hand_done(routes, ridx, step, j, day_end, pos, tiles, day):
    """A hand is claimable iff its ENTIRE remaining tape day is worth ~zero:
    no animal/courier action, and every remaining WATER/HARVEST/PLANT lands
    on a tile where it would be a no-op or waste (traced positionally).
    fp9b lesson: NEVER substitute for productive tape hours — the chassis
    adapts its route to live state, so any replication of ours diverges and
    compounds.  The trace is used ONLY for this claim decision."""
    seq = routes.get(ridx)
    if seq is None:
        return False
    x, y = pos
    for s in range(step, min(day_end + 1, len(seq))):
        hands = seq[s].get("hands") or []
        if j >= len(hands) or not hands[j]:
            continue
        a = hands[j]
        v = a[0]
        if v in _E3_ANIMAL_V:
            return False
        if v == "PICKUP":
            return False
        if v in _E3_MOVES:
            dx, dy = _E3_MOVES[v]
            x = min(9, max(0, x + dx))
            y = min(9, max(0, y + dy))
            continue
        if v in ("WATER", "HARVEST", "PLANT", "FERTILIZE", "DIG",
                 "BUILD_PASTURE", "BUILD_COOP", "DROP"):
            t = tiles[y][x]
            if v == "WATER":
                # productive water = live non-inert plant not yet watered
                if isinstance(t, dict) and t.get("kind") == "PLANT":
                    yu = int(t.get("yield_units", 0))
                    age = day - int(t.get("planted_day", day))
                    if not (yu == 0 and age > 6):
                        return False        # real watering remains
                continue                    # inert/empty water = waste, ok
            if v == "HARVEST":
                if isinstance(t, dict) and int(t.get("yield_units", 0)) > 0:
                    return False
                continue
            return False                    # any other work: not done
    return True


_E3_PARENT = agent
def agent(observation, configuration=None):
    action = _E3_PARENT(observation, configuration)
    try:
        day = int(observation.get("day", 0))
        if day < _E3_DON or not isinstance(action, dict):
            return action
        hour = int(observation.get("hour", 0))
        step = day * 24 + hour
        seat = int(observation.get("player", 0))
        farm = observation["farms"][seat]
        tiles = farm["tiles"]
        priv = observation.get("private", {})
        seeds = dict(priv.get("seeds", {}))
        hands = farm.get("hands", [])
        n_h = len(hands)
        pos_h = [tuple(h) for h in hands]

        routes = _e3_routes()
        ridx = _e3_active_route(seat) if routes else None
        if routes is None or ridx is None:
            _E3_TELEM["route_miss"] += 1
            return action

        day_end = day * 24 + 23
        st = _E3_STATE.get(seat)
        if st is None:
            st = _E3_STATE[seat] = {"day": -1, "claimed": {}, "own": {},
                                    "proj": {}}
        if st["day"] != day:
            st["day"] = day
            st["claimed"] = {}     # j -> {"duties":[...], "di":0}
            st["proj"] = {}        # j -> ("DIG"/"PLANT"/"WATER", x, y)
        own = st["own"]            # (x,y) -> planted_day (persists all days)

        # registry hygiene: drop tiles that are no longer our live plants
        for p in list(own.keys()):
            t = tiles[p[1]][p[0]]
            if not (isinstance(t, dict) and t.get("kind") == "PLANT"):
                own.pop(p, None)

        # claim newly-eligible hands (remaining tape day worth ~zero)
        for j in range(n_h):
            if j in st["claimed"]:
                continue
            if _e3_hand_done(routes, ridx, step, j, day_end, pos_h[j],
                             tiles, day):
                st["claimed"][j] = {"di": 0}

        if not st["claimed"]:
            return action

        # board facts for recycling — TRULY-spent tiles only.  Engine math:
        # ongoing crops (STR/TOM) produce until age = first_yield_day +
        # (max_yield-1)*interval (STR: 10+3*2=16); non-ongoing yield only
        # in the water window ending max_yield_day.  fp9c lesson: the old
        # test (yield 0 & age>6) dug MID-PRODUCTION strawberries (yield is
        # 0 right after each tape harvest) and bled ~$1k/day.
        _CD_LAST_AGE = {"WHEAT": 4, "CARROT": 3, "MELON": 12,
                        "TOMATO": 8 + 3 * 1, "STRAWBERRY": 10 + 3 * 2}
        inert = []
        for y in range(10):
            for x in range(10):
                t = tiles[y][x]
                if isinstance(t, dict) and t.get("kind") == "PLANT" \
                        and (x, y) not in own:
                    yu = int(t.get("yield_units", 0))
                    age = day - int(t.get("planted_day", day))
                    last = _CD_LAST_AGE.get(t.get("crop"))
                    if yu == 0 and last is not None and age > last:
                        inert.append((x, y))

        hands_out = [list(h) if h else ["PASS"]
                     for h in (action.get("hands") or [])]
        while len(hands_out) < n_h:
            hands_out.append(["PASS"])
        taken = set()

        # PLANT collective validation: count tape's own PLANTs this turn
        plants_now = {"CARROT": 0, "WHEAT": 0}
        fa = action.get("farmer") or []
        if fa and fa[0] == "PLANT" and len(fa) > 1 and fa[1] in plants_now:
            plants_now[fa[1]] += 1
        for j, h in enumerate(hands_out):
            if j not in st["claimed"] and h and h[0] == "PLANT" \
                    and len(h) > 1 and h[1] in plants_now:
                plants_now[h[1]] += 1

        def move_toward(j, tx, ty):
            px, py = pos_h[j]
            hands_out[j] = ["EAST" if tx > px else "WEST" if tx < px
                            else "SOUTH" if ty > py else "NORTH"]
            _E3_TELEM["moves"] += 1

        for j, cst in st["claimed"].items():
            if j >= n_h:
                continue
            _E3_TELEM["claimed_hand_hours"] += 1
            px, py = pos_h[j]
            acted = False

            # 1) active recycling project (finish it: dig->plant->water)
            proj = st["proj"].get(j)
            if proj:
                stage, tx, ty = proj
                if (px, py) != (tx, ty):
                    move_toward(j, tx, ty)
                    acted = True
                else:
                    t = tiles[ty][tx]
                    if stage == "DIG":
                        if isinstance(t, dict) and t.get("kind") == "PLANT":
                            hands_out[j] = ["DIG"]
                            _E3_TELEM["digs"] += 1
                            st["proj"][j] = ("PLANT", tx, ty)
                            acted = True
                        else:
                            st["proj"][j] = ("PLANT", tx, ty)
                    if not acted and st["proj"].get(j, ("", 0, 0))[0] == "PLANT":
                        crop = "CARROT" if int(seeds.get("CARROT", 0)) - \
                            plants_now["CARROT"] > 0 else \
                            ("WHEAT" if int(seeds.get("WHEAT", 0)) -
                             plants_now["WHEAT"] > 0 else None)
                        if t is None and crop:
                            hands_out[j] = ["PLANT", crop]
                            plants_now[crop] += 1
                            _E3_TELEM["plants"] += 1
                            own[(tx, ty)] = day
                            st["proj"][j] = ("WATER", tx, ty)
                            acted = True
                        elif t is None and crop is None:
                            acted = True   # wait for seeds (buys pending)
                            hands_out[j] = ["PASS"]
                        else:
                            st["proj"].pop(j, None)
                    elif not acted and st["proj"].get(j, ("", 0, 0))[0] == "WATER":
                        if isinstance(t, dict) and not t.get("watered_today"):
                            hands_out[j] = ["WATER"]
                            _E3_TELEM["own_waters"] += 1
                        st["proj"].pop(j, None)
                        acted = True
                if acted:
                    continue

            # 2) service OUR registry (water daily; harvest at maturity)
            best = None
            for (tx, ty), pd in own.items():
                if (tx, ty) in taken:
                    continue
                t = tiles[ty][tx]
                if not (isinstance(t, dict) and t.get("kind") == "PLANT"):
                    continue
                age = day - pd
                need = None
                if int(t.get("yield_units", 0)) > 0 and age >= 2:
                    need = "HARVEST"
                elif not t.get("watered_today"):
                    need = "WATER"
                if need:
                    dd = abs(tx - px) + abs(ty - py)
                    if best is None or dd < best[0]:
                        best = (dd, tx, ty, need)
            if best:
                _d, tx, ty, need = best
                if (px, py) != (tx, ty):
                    move_toward(j, tx, ty)
                else:
                    hands_out[j] = [need]
                    _E3_TELEM["own_harvs" if need == "HARVEST"
                              else "own_waters"] += 1
                    taken.add((tx, ty))
                continue

            # 3) start a new recycling project (enough hours left: dig+plant
            # +water = walk + 3; require slack before hour 19)
            if (day <= _E3_PLANT_TO and hour <= 19 and len(own) < _E3_MAX_OWN
                    and j not in st["proj"]):
                cand = None
                for (tx, ty) in inert:
                    if (tx, ty) in taken:
                        continue
                    dd = abs(tx - px) + abs(ty - py)
                    if dd + 3 <= (23 - hour) and (cand is None or dd < cand[0]):
                        cand = (dd, tx, ty)
                if cand:
                    _d, tx, ty = cand
                    st["proj"][j] = ("DIG", tx, ty)
                    inert.remove((tx, ty))
                    taken.add((tx, ty))
                    _E3_TELEM["proj_started"] += 1
                    if (px, py) != (tx, ty):
                        move_toward(j, tx, ty)
                    else:
                        hands_out[j] = ["DIG"]
                        _E3_TELEM["digs"] += 1
                        st["proj"][j] = ("PLANT", tx, ty)
                    continue
            _E3_TELEM["idle"] += 1

        # ---- market: keep tape, append carrot/wheat seed floors ----
        market = [list(o) for o in (action.get("market") or [])]
        if day <= _E3_PLANT_TO and farm.get("money", 0) > 1200:
            for crop, floor_n in (("CARROT", 6), ("WHEAT", 4)):
                held = int(seeds.get(crop, 0))
                if held < floor_n and len(market) < 10 and \
                        not any(o[:2] == ["BUY_SEED", crop] for o in market):
                    market.append(["BUY_SEED", crop, floor_n - held])
                    _E3_TELEM["seed_buys"] += 1
        return dict(action, hands=hands_out, market=market[:10])
    except Exception:
        _E3_TELEM["errors"] += 1
        return action
agent.telemetry = _E3_TELEM
agent = globals().pop("agent")
