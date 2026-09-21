

# EXECUTOR fp9 — SUBSYSTEM PARTITION (herd frozen on tape).  Spec: review
# REVIEW_2026-09-21 §1.2 + our route-query correction (unit-days are 60%
# mixed, so NOT unit-level; hands expire midnight, so whole-day claim of a
# hand with ZERO remaining animal actions today is corruption-free).
#
# Each hour from _E3_DON: identify the tape's active route (match its emitted
# action against the known route table), and for each HAND look ahead in that
# route to the end of today.  A hand with NO remaining animal/courier action
# today is CLAIMED for crops for the rest of today (its crop route is expend-
# able — it respawns at midnight).  Claimed hands run a crop-only scheduler
# (water live crops they'd tend + DIG inert strawberries + PLANT carrot/wheat,
# water-paired).  The farmer and every unclaimed hand pass through the tape
# action byte-for-byte -> the entire feed/care/courier choreography is intact.
# Market: tape kept, crop seed buys appended.
_E3_DON = 22
_E3_PLANT_TO = 27
_E3_ANIMAL_V = {"FEED", "CARE", "COLLECT_FERTILIZER", "PLACE"}
_E3_CROP_CAP = {"COW": 6, "SHEEP": 6, "GOOSE": 4}
_E3_TELEM = {"claimed_hand_hours": 0, "waters": 0, "harvs": 0, "digs": 0,
             "plants": 0, "seed_buys": 0, "passthru": 0, "route_miss": 0,
             "moves": 0, "idle": 0, "errors": 0}
_E3_STATE = {}


def _e3_route_lookahead():
    """Return the module-level tape route table {idx:[step,...]} or None."""
    try:
        return _IMPL.chassis.routes
    except Exception:
        return None


def _e3_active_route(seat):
    """Read the tape's own current route index from chassis state
    (chassis.players[seat]['route'])."""
    try:
        r = _IMPL.chassis.players.get(seat, {}).get("route")
        if r is not None and r in _IMPL.chassis.routes:
            return r
    except Exception:
        pass
    return None


def _e3_hand_animal_free(routes, ridx, step, j, day_end_step):
    """True if hand j has NO animal/courier action from `step` to day end."""
    seq = routes.get(ridx)
    if seq is None:
        return False
    for s in range(step, min(day_end_step + 1, len(seq))):
        hands = seq[s].get("hands") or []
        if j >= len(hands):
            continue
        a = hands[j]
        if not a:
            continue
        v = a[0]
        if v in _E3_ANIMAL_V:
            return False
        if v == "PICKUP" and len(a) > 1 and a[1] == "WHEAT":
            return False
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

        routes = _e3_route_lookahead()
        if routes is None:
            return action
        ridx = _e3_active_route(seat)
        if ridx is None:
            _E3_TELEM["route_miss"] += 1
            return action     # can't identify route -> stay 100% on tape

        day_end = day * 24 + 23
        # which hands are claimable for crops for the rest of today?
        st = _E3_STATE.get(seat)
        if st is None or st.get("day") != day:
            st = _E3_STATE[seat] = {"day": day, "claimed": set()}
        claimed = st["claimed"]
        for j in range(n_h):
            if j in claimed:
                continue
            if _e3_hand_animal_free(routes, ridx, step, j, day_end):
                claimed.add(j)

        if not claimed:
            return action

        # ---- crop-only board scan ----
        water_t, harv_t, dig_t, empty_t = [], [], [], []
        for y in range(10):
            for x in range(10):
                t = tiles[y][x]
                if t is None:
                    if (x, y) not in ((4, 4), (5, 4), (4, 5), (5, 5)):
                        empty_t.append((x, y))
                    continue
                if not isinstance(t, dict) or t.get("kind") != "PLANT":
                    continue
                yu = int(t.get("yield_units", 0))
                age = day - int(t.get("planted_day", day))
                inert = yu == 0 and age > 6
                if yu > 0 and age >= 2:
                    harv_t.append((x, y))
                if not t.get("watered_today") and not inert:
                    water_t.append((x, y))
                if inert and day <= _E3_PLANT_TO:
                    dig_t.append((x, y))

        hands_out = [list(h) if h else ["PASS"]
                     for h in (action.get("hands") or [["PASS"]] * n_h)]
        while len(hands_out) < n_h:
            hands_out.append(["PASS"])
        taken = set()
        avail = {"CARROT": int(seeds.get("CARROT", 0)),
                 "WHEAT": int(seeds.get("WHEAT", 0))}
        plants_turn = {"CARROT": 0, "WHEAT": 0}

        def nearest_task(px, py, pool):
            best = None
            for (tx, ty) in pool:
                if (tx, ty) in taken:
                    continue
                d = abs(tx - px) + abs(ty - py)
                if best is None or d < best[0]:
                    best = (d, tx, ty)
            return best

        # priority: water live crops (completeness) > harvest > dig > plant
        for j in sorted(claimed):
            if j >= n_h:
                continue
            px, py = pos_h[j]
            _E3_TELEM["claimed_hand_hours"] += 1
            # same-tile first (walking law)
            here = tiles[py][px] if 0 <= px < 10 and 0 <= py < 10 else None
            did = False
            if isinstance(here, dict) and here.get("kind") == "PLANT" \
                    and (px, py) not in taken:
                yu = int(here.get("yield_units", 0))
                age = day - int(here.get("planted_day", day))
                inert = yu == 0 and age > 6
                if yu > 0 and age >= 2:
                    hands_out[j] = ["HARVEST"]
                    _E3_TELEM["harvs"] += 1
                    taken.add((px, py))
                    did = True
                elif not here.get("watered_today") and not inert:
                    hands_out[j] = ["WATER"]
                    _E3_TELEM["waters"] += 1
                    taken.add((px, py))
                    did = True
                elif inert and day <= _E3_PLANT_TO:
                    hands_out[j] = ["DIG"]
                    _E3_TELEM["digs"] += 1
                    taken.add((px, py))
                    did = True
            if did:
                continue
            # else walk toward nearest crop task (water > harvest > dig)
            tgt = (nearest_task(px, py, water_t) or nearest_task(px, py, harv_t)
                   or nearest_task(px, py, dig_t))
            if tgt is None:
                _E3_TELEM["idle"] += 1
                continue
            _d, tx, ty = tgt
            if (px, py) == (tx, ty):
                tt = tiles[ty][tx]
                yu = int(tt.get("yield_units", 0)) if isinstance(tt, dict) else 0
                age = day - int(tt.get("planted_day", day)) if isinstance(tt, dict) else 0
                if yu > 0 and age >= 2:
                    hands_out[j] = ["HARVEST"]; _E3_TELEM["harvs"] += 1
                elif isinstance(tt, dict) and yu == 0 and age > 6:
                    hands_out[j] = ["DIG"]; _E3_TELEM["digs"] += 1
                else:
                    hands_out[j] = ["WATER"]; _E3_TELEM["waters"] += 1
                taken.add((tx, ty))
            else:
                hands_out[j] = ["EAST" if tx > px else "WEST" if tx < px
                                else "SOUTH" if ty > py else "NORTH"]
                _E3_TELEM["moves"] += 1

        _E3_TELEM["passthru"] += n_h - len(claimed)

        # ---- market: keep tape, append crop seed floors on takeover ----
        market = [list(o) for o in (action.get("market") or [])]
        if day <= _E3_PLANT_TO and farm.get("money", 0) > 1200:
            for crop, floor_n in (("CARROT", 8), ("WHEAT", 6)):
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
