# ---------------------------------------------------------------------------
#  TOM layer (fork): the tomato program the
# 2945 Farm's author names as his unsolved problem (section 6: top-10 farms
# buy ~9 tomato seeds from day ~12, hold ~10 tiles at day 20, sell ~71 at
# $114 into an empty book; every graft he tried failed because the route's
# labour is booked solid).  THE FIX HIS DIAGNOSIS IMPLIES: a DEDICATED hand.
# We add one extra HIRE each morning from the commit day; the route tape
# never commands units beyond its own hand count, so the extra hand defaults
# to PASS and this layer owns it completely — zero route interference beyond
# its fib-priced wage (~$144/day at hire #12) and the seed cash.
# Own implementation; gate logic descends from our hinge-gated tomato module
# (live-proven on our previous chassis).  Apache-2.0 like everything here.
# ---------------------------------------------------------------------------
_TM_FROM = 12 * 24            # commit window opens day 12
_TM_TO = 14 * 24              # ...and closes end of day 13 (uncommitted after)
_TM_LAST_PLANT = 20           # a tomato planted later can't finish its ticks
_TM_TILES = 9                 # the top-10 pattern per the Farm's own ledger
_TM_SEED_COST = 50
_TM_CASH_RESERVE = 1200       # never starve the route's own purchases
_TM_PX_GATE = 58              # ~base 60: hinge scarcity crop, T=200 sqrt glut
                              # — supplying an empty book pays; OR a tomato shop:
_TM_SHOPS = ("PIZZA_SHOP", "FARMERS_MARKET")
_TM_SELL_BATCH = 4
_TM_SELL_MIN_PX = 55
_TM_MOVES = {"NORTH": (0, -1), "SOUTH": (0, 1), "EAST": (1, 0), "WEST": (-1, 0)}
_TM_STATE = {}
_TM_REPORT = {"tm_committed": 0, "tm_planted": 0, "tm_waters": 0, "tm_harvested": 0,
              "tm_sold": 0, "tm_hires": 0, "tm_errors": 0, "tm_abort": "",
              "tm_seeds_max": 0, "tm_empty_seen": 0, "tm_hand_turns": 0}


def _tm_step_toward(pos, target):
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


def _tm_shed_tiles(board):
    half = board // 2
    return [(half - 1, half - 1), (half, half - 1), (half - 1, half), (half, half)]


_TM_PARENT = agent
del agent


def agent(observation, configuration=None):
    action = _TM_PARENT(observation, configuration)
    try:
        step = int(observation["step"])
        seat = int(observation["player"])
        st = _TM_STATE.get(seat)
        if step == 0 or st is None or step <= st["step"]:
            st = _TM_STATE[seat] = {"step": -1, "mode": None, "tiles": {}, "planted": 0,
                                    "seeds_ordered": False, "carry_est": 0}
            if step == 0:
                _TM_REPORT.update(tm_committed=0, tm_planted=0, tm_waters=0, tm_harvested=0,
                                  tm_sold=0, tm_hires=0, tm_errors=0, tm_abort="")
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
        n_hands_now = len(farm.get("hands") or [])

        # ---- commit decision (once, in the window) ------------------------
        if st["mode"] is None and _TM_FROM <= step < _TM_TO:
            shops = list((observation.get("town") or {}).get("unlocked_shops") or [])
            has_shop = any(s in _TM_SHOPS for s in shops)
            px_ok = int(prices.get("TOMATO", 0)) >= _TM_PX_GATE
            if has_shop or px_ok:
                st["mode"] = "ON"
                _TM_REPORT["tm_committed"] = 1
            elif step >= _TM_TO - 1:
                st["mode"] = "OFF"
                _TM_REPORT["tm_abort"] = "gate"
        if st["mode"] != "ON":
            return action

        # ---- land: the route only ever buys 3 quadrants (measured: SE stays
        # LOCKED all game with $15-66k banked).  $4,000 buys 25 virgin tiles
        # entirely outside the tape's world — no plant races, no conflicts.
        quads = list(farm.get("unlocked_quadrants") or [])
        if (len(quads) == 3 and not st.get("land_ordered")
                and money >= 4000 + 3000 and len(market) < 10):
            market.append(["BUY_LAND"])
            st["land_ordered"] = True
            _TM_REPORT["tm_land"] = 1
        if len(quads) < 4 and not st.get("land_ordered"):
            # wait for the route's own 3rd quadrant first
            pass

        # ---- seeds: one order, cash-guarded (one spare: the chassis's own
        # small V219 tomato project may PLANT the same turn; the collective
        # per-crop validation voids ALL tomato plants if seeds run short) ---
        seeds_held = int(priv["seeds"].get("TOMATO", 0))
        if (not st["seeds_ordered"] and st["planted"] < _TM_TILES
                and seeds_held < _TM_TILES + 1
                and money >= (_TM_TILES + 1) * _TM_SEED_COST + _TM_CASH_RESERVE
                and len(market) < 10):
            market.append(["BUY_SEED", "TOMATO", _TM_TILES + 1 - seeds_held])
            st["seeds_ordered"] = True

        # ---- one extra hire each morning while the program runs -----------
        # The route fills all 10 market slots at hour 0 (its own hire wave),
        # so take the first free slot in hours 0-3 instead.  Our hand's index
        # = hands alive now + route HIREs queued AHEAD of ours this turn
        # (orders execute in list order; hires spawn in order).  Hands expire
        # at midnight, so the index resets daily.
        if hour == 0:
            st["my_idx"] = None
        if st.get("hired_day") != day:
            active = st["planted"] > 0 or seeds_held > 0 or not st["seeds_ordered"]
            if hour <= 3 and day <= 28 and active and len(market) < 10:
                route_hires_this_turn = sum(1 for o in market if o and o[0] == "HIRE")
                st["my_idx"] = n_hands_now + route_hires_this_turn
                market.append(["HIRE"])
                st["hired_day"] = day
                _TM_REPORT["tm_hires"] += 1

        # ---- our unit exists once the hand count covers its index ---------
        my_idx = st.get("my_idx")
        if my_idx is not None and n_hands_now <= my_idx:
            my_idx = None   # not spawned yet this day (or hire failed)
        units = [list(action.get("farmer") or ["PASS"])] + \
                [list(c) if c else ["PASS"] for c in route_hands] + \
                [["PASS"]] * (n_hands_now - len(route_hands))

        # ---- registry upkeep ----------------------------------------------
        for pos in list(st["tiles"]):
            t = tiles[pos[1]][pos[0]]
            if not (isinstance(t, dict) and t.get("crop") == "TOMATO"):
                st["tiles"].pop(pos)

        _TM_REPORT["tm_seeds_max"] = max(_TM_REPORT["tm_seeds_max"], seeds_held)
        if my_idx is not None:
            _TM_REPORT["tm_hand_turns"] += 1
            hand_pos = tuple(farm["hands"][my_idx])
            inv = priv["inventories"][my_idx + 1] if my_idx + 1 < len(priv["inventories"]) else {}
            carrying = int(inv.get("TOMATO", 0))
            _patch = [(5, 6), (5, 7), (5, 8), (6, 7), (6, 6), (6, 5),
                      (7, 5), (7, 6), (7, 7)][:_TM_TILES]

            # Deterministic day plan, rebuilt whenever the hand spawns:
            # plant->water pairs first (a seed unwatered on its planting day
            # weeds THAT NIGHT), then water every dry tile, then harvests,
            # then a shed run.  No priorities, no races.
            if st.get("plan_day") != day:
                st["plan_day"] = day
                plan = []
                can_plant = (st["planted"] < _TM_TILES and day <= _TM_LAST_PLANT
                             and len(quads) >= 4)
                if can_plant:
                    budget = min(2, max(0, seeds_held))
                    for pos in _patch:
                        if budget <= 0:
                            break
                        if pos in st["tiles"]:
                            continue
                        t = tiles[pos[1]][pos[0]]
                        empty = t is None or t == {} or (isinstance(t, dict)
                                and not t.get("kind") and not t.get("crop")
                                and not t.get("animal"))
                        if empty:
                            plan.append(("PLANTWATER", pos))
                            budget -= 1
                for pos in _patch:
                    if pos in st["tiles"] and not any(p == pos for _, p in plan):
                        plan.append(("TEND", pos))
                plan.append(("SHED", None))
                st["plan"] = plan
                st["ip"] = 0
                st["substep"] = 0

            cmd = None
            plan = st.get("plan") or []
            while cmd is None and st["ip"] < len(plan):
                kind, pos = plan[st["ip"]]
                if kind == "PLANTWATER":
                    t = tiles[pos[1]][pos[0]]
                    if st["substep"] == 0:
                        empty = t is None or t == {} or (isinstance(t, dict)
                                and not t.get("kind") and not t.get("crop")
                                and not t.get("animal"))
                        if not empty or seeds_held < 1:
                            st["ip"] += 1
                            continue
                        if hand_pos != pos:
                            cmd = _tm_step_toward(hand_pos, pos)
                        else:
                            cmd = ["PLANT", "TOMATO"]
                            st["tiles"][pos] = day
                            st["planted"] += 1
                            st["substep"] = 1
                            _TM_REPORT["tm_planted"] += 1
                    else:
                        if isinstance(t, dict) and t.get("crop") == "TOMATO"                                 and not t.get("watered_today"):
                            cmd = ["WATER"]
                            _TM_REPORT["tm_waters"] += 1
                        st["ip"] += 1
                        st["substep"] = 0
                elif kind == "TEND":
                    t = tiles[pos[1]][pos[0]]
                    if not (isinstance(t, dict) and t.get("crop") == "TOMATO"):
                        st["tiles"].pop(pos, None)
                        st["ip"] += 1
                        continue
                    if hand_pos != pos:
                        cmd = _tm_step_toward(hand_pos, pos)
                    elif not t.get("watered_today"):
                        cmd = ["WATER"]
                        _TM_REPORT["tm_waters"] += 1
                        # stay on this plan step: harvest check next turn
                        st["substep"] = 1
                    elif int(t.get("yield_units", 0)) >= 2 or (
                            int(t.get("yield_units", 0)) >= 1 and day >= 26):
                        cmd = ["HARVEST"]
                        _TM_REPORT["tm_harvested"] += int(t.get("yield_units", 0))
                        st["ip"] += 1
                        st["substep"] = 0
                    else:
                        st["ip"] += 1
                        st["substep"] = 0
                        continue
                    if cmd == ["WATER"]:
                        pass
                    elif cmd == ["HARVEST"]:
                        pass
                    else:
                        continue
                    if cmd == ["WATER"] and st["substep"] == 1:
                        st["substep"] = 2
                    elif st["substep"] == 2:
                        st["ip"] += 1
                        st["substep"] = 0
                else:  # SHED
                    if carrying >= 1:
                        shed = min(_tm_shed_tiles(board),
                                   key=lambda a: abs(a[0] - hand_pos[0]) + abs(a[1] - hand_pos[1]))
                        if hand_pos == shed:
                            cmd = ["DROP"]
                            st["ip"] += 1
                        else:
                            cmd = _tm_step_toward(hand_pos, shed)
                    else:
                        st["ip"] += 1
                        continue
            if cmd:
                units[1 + my_idx] = cmd

        # ---- sell tomatoes that reach the shed ----------------------------
        shed_tom = int(priv["shed"].get("TOMATO", 0))
        planned = sum(int(o[2]) for o in market if len(o) >= 3 and o[:2] == ["SELL", "TOMATO"])
        px = int(prices.get("TOMATO", 0))
        batch_ok = shed_tom - planned >= _TM_SELL_BATCH and px >= _TM_SELL_MIN_PX
        evening_ok = shed_tom - planned >= 1 and hour >= 20 and px >= _TM_SELL_MIN_PX
        if (batch_ok or evening_ok or day >= 28) and shed_tom - planned >= 1 and len(market) < 10:
            n = shed_tom - planned if (day >= 28 or evening_ok) else _TM_SELL_BATCH
            market.append(["SELL", "TOMATO", n])
            _TM_REPORT["tm_sold"] += n

        action = dict(action)
        action["farmer"] = units[0]
        action["hands"] = units[1:]
        action["market"] = market
    except Exception:
        _TM_REPORT["tm_errors"] += 1
    return action


agent.telemetry = _TM_REPORT
agent = globals().pop('agent')
