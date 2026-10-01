# ---------------------------------------------------------------------------
# ⚰ FALSIFIED : vs today's tetsutani 39 paired seeds
# 3813-3851: margin-diff −12,239 ± 1,347 (t=−9.09), wins 21→0, negative on
# 39/39 seeds; own-bank diff −12,192 = the whole loss.  CAUSE = THE FIB WAGE
# LAW (engine L99-101/L690-707): the n-th hire OF THE DAY costs fib(n); the
# route morning-rehires 9-14 hands, so these two layer hands were hires
# #10-16 of the day = 377-1,597/day = 10-20k/season in wages vs ~3-4k of
# produce.  The good probe world (3754, own +3,705) was a cheap-labor
# lottery: route hired only ~9 there, making our hands #9-10 (144/day).
# Secondary: "SE locked" is world-dependent — route sometimes buys Q4 and
# builds pastures on our plots (collisions damage the route's own economy).
# The mechanics WORK (25-38 toms harvested when staffed); the staffing
# model is what's dead.  Only live successor design: tail-idle
# commandeering — ceiling measured +0-1k, down-ranked.
# ---------------------------------------------------------------------------
#  QFARM layer (fork): the 4th-quadrant
# micro-farm.  The route chassis only ever buys 3 quadrants (measured; SE
# stays locked all game with $15-66k banked).  We buy it ($4k), staff it with
# TWO dedicated extra hands the tape never commands, and run it as our own
# 19-tile farm: 9 FERTILIZED tomatoes (the 2945 author's unsolved section-6
# program: top-10 sell ~71 at $114 = 8/tile, only possible at the +2
# fertilized tick) + 10 fast-cycle carrots (the chassis's own CARROT2 layer
# proves the carrot book pays; T=450, zero floor risk).  v98a taught the
# economics: 9 unfertilized tomatoes alone cannot carry the land+wage tax
# (-9.4k t=-15.6); utilization and the fert doubling are the whole game.
# Deterministic day-scripts per hand — a seed unwatered on its planting day
# weeds THAT NIGHT, so planting is always an adjacent plant->water pair.
# Own implementation, Apache-2.0 like the chassis it wraps.
# ---------------------------------------------------------------------------
_QF_FROM = 12 * 24
_QF_TO = 14 * 24
_QF_TOM = [(5, 6), (5, 7), (5, 8), (6, 6), (6, 7), (6, 8), (7, 6), (7, 7)]
_QF_CAR = [(7, 8), (5, 9), (6, 9), (7, 9), (8, 6), (8, 7), (8, 8), (8, 9)]
_QF_TOM_LAST_PLANT = 20
_QF_CAR_LAST_PLANT = 25       # age-3 harvest still lands by d28
_QF_SEED_RESERVE = 3000       # cash the route keeps untouched
_QF_TOM_SELL_PX = 78          # hinge book: hold for the scarcity price...
_QF_TOM_SELL_DAY = 26         # ...but never past d26 (dump whatever's left)
_QF_CAR_SELL_PX = 30
_QF_STATE = {}
_QF_REPORT = {"qf_committed": 0, "qf_land": 0, "qf_tom_planted": 0, "qf_car_planted": 0,
              "qf_waters": 0, "qf_ferts": 0, "qf_tom_harv": 0, "qf_car_harv": 0,
              "qf_tom_sold": 0, "qf_car_sold": 0, "qf_hires": 0, "qf_errors": 0}


def _qf_step(pos, target):
    x, y = pos
    tx, ty = target
    if x < tx:
        return ["EAST"]
    if x > tx:
        return ["WEST"]
    if y < ty:
        return ["SOUTH"]
    if y > ty:
        return ["NORTH"]
    return None


def _qf_empty(t):
    return t is None or t == {} or (isinstance(t, dict) and not t.get("kind")
                                    and not t.get("crop") and not t.get("animal"))


def _qf_hand_program(st, key, plots, crop, tiles, hand_pos, inv, priv, day, board, seeds_key):
    """One dedicated hand's next command over its plot list.  Priorities, in
    strict order: (1) finish a plant->water pair, (2) water any dry live
    plot, (3) fertilize an unfertilized tomato in its window, (4) harvest
    ready plots, (5) plant the next empty plot (starting a pair), (6) walk
    cargo to the shed in the evening."""
    reg = st[key]                       # pos -> planted_day
    seeds = int(priv["seeds"].get(crop, 0))
    carrying = sum(int(inv.get(p, 0)) for p in ("TOMATO", "CARROT", "FERTILIZER"))
    fert_inv = int(inv.get("FERTILIZER", 0))

    # (1) unfinished pair: a plot planted this day and still dry
    pend = st.get(key + "_pend")
    if pend:
        t = tiles[pend[1]][pend[0]]
        if isinstance(t, dict) and t.get("crop") == crop and not t.get("watered_today"):
            if hand_pos == pend:
                _QF_REPORT["qf_waters"] += 1
                return ["WATER"]
            return _qf_step(hand_pos, pend)
        st[key + "_pend"] = None

    # registry upkeep
    for pos in list(reg):
        t = tiles[pos[1]][pos[0]]
        if not (isinstance(t, dict) and t.get("crop") == crop):
            reg.pop(pos)

    # (2) BRINK water only: weeds need 2 consecutive dry days, and watering
    # adds nothing to a tomato's tick (+1 regardless) — so water each tile
    # every OTHER day, exactly when consecutive_unwatered >= 1.  This halves
    # the water load; v98b's daily watering ate every turn and the fruit
    # died on the vine.  Carrots DO need window (age 2-3) watering for yield.
    best = None
    for pos, pd in reg.items():
        t = tiles[pos[1]][pos[0]]
        if not isinstance(t, dict) or t.get("watered_today"):
            continue
        brink = int(t.get("consecutive_unwatered", 0)) >= 1
        window = crop == "CARROT" and 2 <= (day - pd) <= 3
        if not (brink or window):
            continue
        d = abs(pos[0] - hand_pos[0]) + abs(pos[1] - hand_pos[1])
        cand = (d, pos)
        if best is None or cand < best:
            best = cand
    if best:
        pos = best[1]
        if hand_pos == pos:
            _QF_REPORT["qf_waters"] += 1
            return ["WATER"]
        return _qf_step(hand_pos, pos)

    # (2b) harvest ready plots BEFORE any non-urgent work
    ready_age = 8 if crop == "TOMATO" else 2
    bar = 2 if crop == "TOMATO" else 3
    for pos, pd in reg.items():
        t = tiles[pos[1]][pos[0]]
        if not isinstance(t, dict):
            continue
        yv = int(t.get("yield_units", 0))
        if (day - pd) >= ready_age and (yv >= bar or (yv >= 1 and day >= 27)):
            if hand_pos == pos:
                if crop == "TOMATO":
                    _QF_REPORT["qf_tom_harv"] += yv
                else:
                    _QF_REPORT["qf_car_harv"] += yv
                    reg.pop(pos, None)
                return ["HARVEST"]
            return _qf_step(hand_pos, pos)

    # (3) tomato fertilization: cover the tick window (age 7+; one op = 3 days)
    if crop == "TOMATO":
        for pos, pd in reg.items():
            t = tiles[pos[1]][pos[0]]
            if not isinstance(t, dict):
                continue
            age = day - pd
            if age >= 7 and int(t.get("fertilized_until_day", -1)) < day:
                if fert_inv < 1:
                    shed_fert = int(priv["shed"].get("FERTILIZER", 0))
                    if shed_fert >= 1:
                        half = board // 2
                        access = min([(half-1, half-1), (half, half-1), (half-1, half), (half, half)],
                                     key=lambda a: abs(a[0]-hand_pos[0]) + abs(a[1]-hand_pos[1]))
                        if hand_pos == access:
                            return ["PICKUP", "FERTILIZER", 3]
                        return _qf_step(hand_pos, access)
                    continue
                if hand_pos == pos:
                    _QF_REPORT["qf_ferts"] += 1
                    return ["FERTILIZE"]
                return _qf_step(hand_pos, pos)

    # (5) plant the next empty plot (starts a pair)
    last_plant = _QF_TOM_LAST_PLANT if crop == "TOMATO" else _QF_CAR_LAST_PLANT
    if seeds >= 1 and day <= last_plant:
        for pos in plots:
            if pos in reg:
                continue
            t = tiles[pos[1]][pos[0]]
            if t == "LOCKED" or not _qf_empty(t):
                continue
            if hand_pos == pos:
                reg[pos] = day
                st[key + "_pend"] = pos
                if crop == "TOMATO":
                    _QF_REPORT["qf_tom_planted"] += 1
                else:
                    _QF_REPORT["qf_car_planted"] += 1
                return ["PLANT", crop]
            return _qf_step(hand_pos, pos)

    # (6) evening shed run
    if carrying >= 1:
        half = board // 2
        access = min([(half-1, half-1), (half, half-1), (half-1, half), (half, half)],
                     key=lambda a: abs(a[0]-hand_pos[0]) + abs(a[1]-hand_pos[1]))
        if hand_pos == access:
            return ["DROP"]
        return _qf_step(hand_pos, access)
    return None


_QF_PARENT = agent
del agent


def agent(observation, configuration=None):
    action = _QF_PARENT(observation, configuration)
    try:
        step = int(observation["step"])
        seat = int(observation["player"])
        st = _QF_STATE.get(seat)
        if step == 0 or st is None or step <= st["step"]:
            st = _QF_STATE[seat] = {"step": -1, "mode": None, "tom": {}, "car": {},
                                    "tom_pend": None, "car_pend": None,
                                    "seeds_day": -1, "land_ordered": False,
                                    "hired_day": -1, "idx": {}}
            if step == 0:
                for k in list(_QF_REPORT):
                    _QF_REPORT[k] = 0 if k != "qf_errors" else 0
        st["step"] = step
        if not isinstance(action, dict) or step > 717:
            return action
        day, hour = step // 24, step % 24
        farm = observation["farms"][seat]
        tiles = farm["tiles"]
        board = len(tiles)
        priv = observation["private"]
        prices = observation["market"]["prices"]
        money = farm.get("money", 0)
        market = [list(o) for o in (action.get("market") or [])]
        route_hands = list(action.get("hands") or [])
        n_hands = len(farm.get("hands") or [])

        # ---- commit: tomato is a hinge book (base 60) and carrot's T=450
        # absorbs anything — commit whenever the cash is there ---------------
        if st["mode"] is None and _QF_FROM <= step < _QF_TO:
            if money >= 4000 + _QF_SEED_RESERVE:
                st["mode"] = "ON"
                _QF_REPORT["qf_committed"] = 1
            elif step >= _QF_TO - 1:
                st["mode"] = "OFF"
        if st["mode"] != "ON":
            return action
        quads = list(farm.get("unlocked_quadrants") or [])

        # ---- land ----------------------------------------------------------
        if (len(quads) == 3 and not st["land_ordered"]
                and money >= 4000 + _QF_SEED_RESERVE and len(market) < 10):
            market.append(["BUY_LAND"])
            st["land_ordered"] = True
            _QF_REPORT["qf_land"] = 1

        # ---- seeds: top up daily (carrot replants burn seeds) --------------
        if st["seeds_day"] != day and len(quads) >= 4 and len(market) < 10:
            want = []
            tom_seeds = int(priv["seeds"].get("TOMATO", 0))
            car_seeds = int(priv["seeds"].get("CARROT", 0))
            if day <= _QF_TOM_LAST_PLANT and st.get("qf_tom_done", 0) < len(_QF_TOM) \
                    and tom_seeds < 10:
                want.append(["BUY_SEED", "TOMATO", 10 - tom_seeds])
            if day <= _QF_CAR_LAST_PLANT and car_seeds < 6:
                want.append(["BUY_SEED", "CARROT", 6 - car_seeds])
            # fert: BUY_PRODUCT is legal for FERTILIZER and its price only
            # decays (zero town drain) — 2 apps/tile double every tick
            fert_px = int(prices.get("FERTILIZER", 999))
            shed_fert = int(priv["shed"].get("FERTILIZER", 0))
            if day <= 24 and shed_fert < 2 and fert_px <= 70:
                want.append(["BUY_PRODUCT", "FERTILIZER", 3])
            cost = sum(o[2] * (50 if o[1] == "TOMATO" else (fert_px if o[1] == "FERTILIZER" else 20))
                       for o in want)
            if want and money >= cost + _QF_SEED_RESERVE and len(market) + len(want) <= 10:
                market.extend(want)
                st["seeds_day"] = day
        st["qf_tom_done"] = len(st["tom"])

        # ---- two extra hires, first free slots hours 0-3 -------------------
        if hour == 0:
            st["idx"] = {}
        if st["hired_day"] != day and hour <= 3 and day <= 28 and len(quads) >= 4:
            free = 10 - len(market)
            if free >= 2:
                ahead = sum(1 for o in market if o and o[0] == "HIRE")
                st["idx"]["tom"] = n_hands + ahead
                st["idx"]["car"] = n_hands + ahead + 1
                market.append(["HIRE"])
                market.append(["HIRE"])
                st["hired_day"] = day
                _QF_REPORT["qf_hires"] += 2

        units = [list(action.get("farmer") or ["PASS"])] + \
                [list(c) if c else ["PASS"] for c in route_hands] + \
                [["PASS"]] * max(0, n_hands - len(route_hands))

        for key, plots, crop in (("tom", _QF_TOM, "TOMATO"), ("car", _QF_CAR, "CARROT")):
            idx = st["idx"].get(key)
            if idx is None or n_hands <= idx:
                continue
            hand_pos = tuple(farm["hands"][idx])
            inv = priv["inventories"][idx + 1] if idx + 1 < len(priv["inventories"]) else {}
            cmd = _qf_hand_program(st, key, plots, crop, tiles, hand_pos, inv,
                                   priv, day, board, crop)
            if cmd:
                units[1 + idx] = cmd

        # ---- sells ----------------------------------------------------------
        for crop, px_gate, batch, rep in (("TOMATO", _QF_TOM_SELL_PX, 4, "qf_tom_sold"),
                                          ("CARROT", _QF_CAR_SELL_PX, 8, "qf_car_sold")):
            shed_n = int(priv["shed"].get(crop, 0))
            planned = sum(int(o[2]) for o in market
                          if len(o) >= 3 and o[0] == "SELL" and o[1] == crop)
            avail = shed_n - planned
            px = int(prices.get(crop, 0))
            late = day >= (_QF_TOM_SELL_DAY if crop == "TOMATO" else 27)
            if avail >= 1 and len(market) < 10 and (px >= px_gate or late) \
                    and (avail >= batch or late or hour >= 21):
                n = avail if (late or hour >= 21) else batch
                market.append(["SELL", crop, n])
                _QF_REPORT[rep] += n

        action = dict(action)
        action["farmer"] = units[0]
        action["hands"] = units[1:]
        action["market"] = market
    except Exception:
        _QF_REPORT["qf_errors"] += 1
    return action


agent.telemetry = _QF_REPORT
agent = globals().pop('agent')
