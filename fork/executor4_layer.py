

# ============================================================
# EXECUTOR fp10 (executor4) — MICRO-CYCLE PORT + DEMAND-SCALED
# CARROT CONVERSION, on the validated subsystem partition.
#
# Ported from the top-10 answer key (Sep 22-23 decode of Majkel/
# Orbital/DSM/SpaTaro/Mother-Goose/THIRD FARM replays):
#   - recycle EXACTLY-SPENT tiles (engine-exact test) within hours;
#   - continuous short cycles: plant -> water -> harvest@age2-3 ->
#     REPLANT the same tile, to d26; never leave a dug tile empty;
#   - crop-mix pivot: when the town opened >=2 carrot-demand shops
#     (PET_CAFE / FARMERS_MARKET), scale conversion up (their CAR
#     tile-days flex 50 -> 509 by world; our tape stays ~76-143).
#
# Framework (fp9-validated, lossless): claim ONLY hands whose entire
# remaining tape day is worth ~zero; herd/courier hours untouched.
# FIX over executor3: the claim test's WATER branch now uses the
# ENGINE-EXACT spent test (the old 'yield0 & age>6' judged watering
# mid-production STR as waste and could steal live-crop waters).
# ============================================================
_E4_DON = 18               # Majkel's recycling starts d18
_E4_PLANT_TO = 26          # carrot planted <=26 harvests <=29
_E4_MAX_OWN_BASE = 6
_E4_MAX_OWN_CARROT = 14    # in carrot-demand worlds
_E4_CARROT_SHOPS = ("PET_CAFE", "FARMERS_MARKET")
_E4_ANIMAL_V = {"FEED", "CARE", "COLLECT_FERTILIZER", "PLACE"}
_E4_MOVES = {"EAST": (1, 0), "WEST": (-1, 0), "SOUTH": (0, 1), "NORTH": (0, -1)}
_E4_LAST_AGE = {"WHEAT": 4, "CARROT": 3, "MELON": 12,
                "TOMATO": 8 + 3 * 1, "STRAWBERRY": 10 + 3 * 2}
_E4_TELEM = {"claimed_hand_hours": 0, "own_waters": 0, "own_harvs": 0,
             "digs": 0, "plants": 0, "replants": 0, "seed_buys": 0,
             "carrot_sells": 0, "route_miss": 0, "moves": 0, "idle": 0,
             "proj_started": 0, "aggr_days": 0, "errors": 0}
_E4_STATE = {}


def _e4_routes():
    try:
        return _IMPL.chassis.routes
    except Exception:
        return None


def _e4_active_route(seat):
    try:
        r = _IMPL.chassis.players.get(seat, {}).get("route")
        if r is not None and r in _IMPL.chassis.routes:
            return r
    except Exception:
        pass
    return None


def _e4_spent(t, day):
    """Engine-exact: a crop tile is truly spent iff yield 0 AND past its
    last possible production age."""
    if not (isinstance(t, dict) and t.get("kind") == "PLANT"):
        return False
    yu = int(t.get("yield_units", 0))
    age = day - int(t.get("planted_day", day))
    last = _E4_LAST_AGE.get(t.get("crop"))
    return yu == 0 and last is not None and age > last


def _e4_hand_done(routes, ridx, step, j, day_end, pos, tiles, day):
    """Claimable iff the hand's ENTIRE remaining tape day is worth ~zero:
    no animal/courier action, and every remaining WATER/HARVEST would be a
    no-op or hit a truly-spent tile (engine-exact).  Trace is positional and
    used ONLY for the claim decision (never replicated: fp9b lesson)."""
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
        if v in _E4_ANIMAL_V or v == "PICKUP":
            return False
        if v in _E4_MOVES:
            dx, dy = _E4_MOVES[v]
            x = min(9, max(0, x + dx))
            y = min(9, max(0, y + dy))
            continue
        if v == "WATER":
            t = tiles[y][x]
            if isinstance(t, dict) and t.get("kind") == "PLANT" \
                    and not _e4_spent(t, day):
                return False            # real watering remains
            continue                    # spent/empty water = waste, ok
        if v == "HARVEST":
            t = tiles[y][x]
            if isinstance(t, dict) and int(t.get("yield_units", 0)) > 0:
                return False
            continue
        if v == "PASS":
            continue
        return False                    # any other work: not done
    return True


_E4_PARENT = kaggle_submission_agent


def _e4_agent(observation, configuration=None):
    action = _E4_PARENT(observation, configuration)
    try:
        day = int(observation.get("day", 0))
        if day < _E4_DON or not isinstance(action, dict):
            return action
        hour = int(observation.get("hour", 0))
        step = day * 24 + hour
        seat = int(observation.get("player", 0))
        farm = observation["farms"][seat]
        tiles = farm["tiles"]
        priv = observation.get("private", {})
        seeds = dict(priv.get("seeds", {}))
        shed = priv.get("shed", {}) or {}
        hands = farm.get("hands", [])
        n_h = len(hands)
        pos_h = [tuple(h) for h in hands]

        routes = _e4_routes()
        ridx = _e4_active_route(seat) if routes else None
        if routes is None or ridx is None:
            _E4_TELEM["route_miss"] += 1
            return action

        shops = (observation.get("town") or {}).get("unlocked_shops") or []
        n_carrot_shops = sum(1 for s in shops if s in _E4_CARROT_SHOPS)
        aggressive = n_carrot_shops >= 2
        max_own = _E4_MAX_OWN_CARROT if aggressive else _E4_MAX_OWN_BASE

        day_end = day * 24 + 23
        st = _E4_STATE.get(seat)
        if st is None:
            st = _E4_STATE[seat] = {"day": -1, "claimed": {}, "own": {},
                                    "proj": {}}
        if st["day"] != day:
            st["day"] = day
            st["claimed"] = {}
            st["proj"] = {}
            st.setdefault("owe", {})
            if aggressive:
                _E4_TELEM["aggr_days"] += 1
        owe = st.setdefault("owe", {})   # crop -> units we harvested and
                                         # MUST sell before midnight (shed
                                         # cap 100: unsold overflow DESTROYS
                                         # the tape's premium goods, -30k
                                         # measured at seed 5108)
        own = st["own"]                # (x,y) -> planted_day

        for p in list(own.keys()):
            t = tiles[p[1]][p[0]]
            if not (isinstance(t, dict) and t.get("kind") == "PLANT"):
                # tile empty: either just harvested by us (replant project
                # pending) or lost — registry entry dropped either way
                own.pop(p, None)

        for j in range(n_h):
            if j in st["claimed"]:
                continue
            if _e4_hand_done(routes, ridx, step, j, day_end, pos_h[j],
                             tiles, day):
                st["claimed"][j] = {"di": 0}

        if not st["claimed"]:
            return action

        # raw material: spent crops + weeds (need DIG) + EMPTY tiles (plant
        # directly).  Key finding (Sep 23): the tape recycles its own spent
        # tiles, but in some worlds leaves 15-20 tiles EMPTY d18-27 — that
        # unused land is the real capacity, and it concentrates in exactly
        # the farmers-market/pet-café worlds where carrots have demand.
        inert = []      # (x, y, needs_dig)
        for y in range(10):
            for x in range(10):
                if (x, y) in own:
                    continue
                t = tiles[y][x]
                if _e4_spent(t, day):
                    inert.append((x, y, True))
                elif isinstance(t, dict) and t.get("kind") == "WEED":
                    inert.append((x, y, True))
                elif t is None:
                    inert.append((x, y, False))

        hands_out = [list(h) if h else ["PASS"]
                     for h in (action.get("hands") or [])]
        while len(hands_out) < n_h:
            hands_out.append(["PASS"])
        taken = set()

        plants_now = {"CARROT": 0, "WHEAT": 0}
        fa = action.get("farmer") or []
        if fa and fa[0] == "PLANT" and len(fa) > 1 and fa[1] in plants_now:
            plants_now[fa[1]] += 1
        for j, h in enumerate(hands_out):
            if j not in st["claimed"] and h and h[0] == "PLANT" \
                    and len(h) > 1 and h[1] in plants_now:
                plants_now[h[1]] += 1

        def pick_crop():
            if int(seeds.get("CARROT", 0)) - plants_now["CARROT"] > 0:
                return "CARROT"
            if int(seeds.get("WHEAT", 0)) - plants_now["WHEAT"] > 0:
                return "WHEAT"
            return None

        def move_toward(j, tx, ty):
            px, py = pos_h[j]
            hands_out[j] = ["EAST" if tx > px else "WEST" if tx < px
                            else "SOUTH" if ty > py else "NORTH"]
            _E4_TELEM["moves"] += 1

        for j, cst in st["claimed"].items():
            if j >= n_h:
                continue
            _E4_TELEM["claimed_hand_hours"] += 1
            px, py = pos_h[j]
            acted = False

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
                            _E4_TELEM["digs"] += 1
                            st["proj"][j] = ("PLANT", tx, ty)
                            acted = True
                        else:
                            st["proj"][j] = ("PLANT", tx, ty)
                    if not acted and st["proj"].get(j, ("", 0, 0))[0] == "PLANT":
                        crop = pick_crop()
                        if t is None and crop and day <= _E4_PLANT_TO:
                            hands_out[j] = ["PLANT", crop]
                            plants_now[crop] += 1
                            _E4_TELEM["plants"] += 1
                            own[(tx, ty)] = day
                            st["proj"][j] = ("WATER", tx, ty)
                            acted = True
                        elif t is None and crop is None and day <= _E4_PLANT_TO:
                            hands_out[j] = ["PASS"]   # wait for seed buys
                            acted = True
                        else:
                            st["proj"].pop(j, None)
                    elif not acted and st["proj"].get(j, ("", 0, 0))[0] == "WATER":
                        if isinstance(t, dict) and not t.get("watered_today"):
                            hands_out[j] = ["WATER"]
                            _E4_TELEM["own_waters"] += 1
                        st["proj"].pop(j, None)
                        acted = True
                if acted:
                    continue

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
                    taken.add((tx, ty))
                    if need == "HARVEST":
                        _E4_TELEM["own_harvs"] += 1
                        t2 = tiles[ty][tx]
                        crop = t2.get("crop") if isinstance(t2, dict) else None
                        units = int(t2.get("yield_units", 0)) if isinstance(t2, dict) else 0
                        if crop and units > 0:
                            owe[crop] = owe.get(crop, 0) + units
                        # MICRO-CYCLE: chain a replant on this same tile
                        # (harvest clears non-ongoing tiles to None)
                        if day <= _E4_PLANT_TO:
                            st["proj"][j] = ("PLANT", tx, ty)
                            _E4_TELEM["replants"] += 1
                    else:
                        _E4_TELEM["own_waters"] += 1
                continue

            if (day <= _E4_PLANT_TO and hour <= 19 and len(own) < max_own
                    and j not in st["proj"]):
                cand = None
                for (tx, ty, ndig) in inert:
                    if (tx, ty) in taken:
                        continue
                    dd = abs(tx - px) + abs(ty - py)
                    need = dd + (3 if ndig else 2)
                    if need <= (23 - hour) and (cand is None or dd < cand[0]):
                        cand = (dd, tx, ty, ndig)
                if cand:
                    _d, tx, ty, ndig = cand
                    st["proj"][j] = ("DIG" if ndig else "PLANT", tx, ty)
                    inert.remove((tx, ty, ndig))
                    taken.add((tx, ty))
                    _E4_TELEM["proj_started"] += 1
                    if (px, py) != (tx, ty):
                        move_toward(j, tx, ty)
                    elif ndig:
                        hands_out[j] = ["DIG"]
                        _E4_TELEM["digs"] += 1
                        st["proj"][j] = ("PLANT", tx, ty)
                    else:
                        crop = pick_crop()
                        if crop:
                            hands_out[j] = ["PLANT", crop]
                            plants_now[crop] += 1
                            _E4_TELEM["plants"] += 1
                            own[(tx, ty)] = day
                            st["proj"][j] = ("WATER", tx, ty)
                    continue
            _E4_TELEM["idle"] += 1

        market = [list(o) for o in (action.get("market") or [])]
        # seed buys: ONCE per day (h6), high money floor — any drain ripples
        # the tape's live funding logic (v117 lesson: -100 tripped skips)
        if day <= _E4_PLANT_TO and hour == 6 and farm.get("money", 0) > 5000:
            carrot_floor = 10 if aggressive else 6
            for crop, floor_n in (("CARROT", carrot_floor), ("WHEAT", 4)):
                held = int(seeds.get(crop, 0))
                if held < floor_n and len(market) < 10 and \
                        not any(o[:2] == ["BUY_SEED", crop] for o in market):
                    market.append(["BUY_SEED", crop, floor_n - held])
                    _E4_TELEM["seed_buys"] += 1
        # MANDATORY same-evening sell of everything our registry harvested:
        # unsold units overflow the 100-cap shed at midnight and DESTROY the
        # tape's premium goods (-30k measured).  h18-22, chunks of 8.
        if hour >= 18:
            prices = (observation.get("market") or {}).get("prices") or {}
            for crop in list(owe.keys()):
                n = owe.get(crop, 0)
                if n <= 0:
                    owe.pop(crop, None)
                    continue
                if len(market) >= 10:
                    break
                q = min(8, n)
                market.append(["SELL", crop, q])
                owe[crop] = n - q
                _E4_TELEM["carrot_sells"] += 1
        return dict(action, hands=hands_out, market=market[:10])
    except Exception:
        _E4_TELEM["errors"] += 1
        return action


_e4_agent.telemetry = _E4_TELEM
agent = _e4_agent
kaggle_submission_agent = _e4_agent
