# ---------------------------------------------------------------------------
# ⚰ BENCHED : 78 paired seeds 3969-4046 vs tetsutani:
# margin-diff −530 ± 375 (t=−1.41), flips +0/−1.  FIRED IN ONLY 2/78 WORLDS
# (the engine math held: pxT ≥ 2x wheat needs ~256u town drain = rare), and
# BOTH firings were catastrophic (−23,450 / −17,851 margin; own −13k/−20k).
# ⭐ THE FEED LAW (new, engine-level): on this chassis WHEAT IS THE ANIMAL
# FEED SUPPLY, not just a crop.  A carrot swap returns its tile in 3 days; a
# tomato squats it permanently → every future wheat cycle on that tile dies →
# feed collapses → the animal engine (the route's core revenue) starves.
# Any layer that squats wheat tiles must replace the FEED, not the revenue.
# With a 2.6% firing rate, even a perfect version nets ~+50/game — tomato on
# this chassis is now measured shut through all four doors (fib-wage hires,
# tail-idle labor, wheat-swap, Q4 patch).  Kept for the mechanism library:
# the swap trick itself (rewrite tape PLANT commands) is sound and reusable.
# ---------------------------------------------------------------------------
#  TOMSWAP layer (Shane Thivaharraja fork, Exp 123): the tomato program
# with ZERO added labor — "swap, don't staff".
#
# Lesson of v98a/v98b: the fib wage law kills any extra hand.  Lesson of the
# chassis's own v9 CARROT layer: the route's wheat replant cycle (water daily,
# harvest every ~3 days) can be re-crop'd by rewriting the tape's own PLANT
# commands, and every worker keeps its schedule.  We apply the author's trick
# to the crop he never gave it to: rewrite PLANT WHEAT -> PLANT TOMATO on up
# to 8 tiles in d10-16.  Engine facts that make it work (verified L440-468,
# L799-800): HARVEST on yield 0 is a harmless no-op (the tape's early visits
# pass through), an ongoing tomato SURVIVES harvest (the tile becomes a
# permanent tomato the tape waters daily — no weeds — and re-harvests every
# cycle), and yield accrues +1/night from age 8 (tomato base 60, hinge book,
# T=200: ~unglutable).  Wheat-as-feed is protected by the same shed reserve
# the carrot layer uses.  Tomato seeds come from our own small money-guarded
# BUY_SEED orders (a tomato never replants — ~8 seeds/game total), never from
# the tape's wheat seed pipeline.  Sales are ours, price-gated on the hinge.
# Own implementation, Apache-2.0 like the chassis it wraps.
# ---------------------------------------------------------------------------
_TS_FIRST_DAY = 10
_TS_LAST_DAY = 16             # swap by d16: mature d24, >=5 harvest days left
_TS_MAX_TILES = 8
_TS_RATIO = 2.0               # tomato px must beat 2x wheat px...
_TS_MIN_PX = 50               # ...and an absolute floor (glutted town = skip)
_TS_WHEAT_RESERVE = 40        # same feed guard as the chassis's carrot layer
_TS_SELL_PX = 70              # hinge book: hold for scarcity...
_TS_SELL_DAY = 27             # ...but dump whatever is left from d27
_TS_STATE = {}
_TS_REPORT = {"ts_swaps": 0, "ts_rescues": 0, "ts_sold": 0, "ts_seed_buys": 0,
              "ts_lost_tiles": 0, "ts_errors": 0}

_TS_PARENT = agent
del agent


def agent(observation, configuration=None):
    action = _TS_PARENT(observation, configuration)
    try:
        step = int(observation["step"])
        seat = int(observation["player"])
        st = _TS_STATE.get(seat)
        if step == 0 or st is None or step <= st["step"]:
            st = _TS_STATE[seat] = {"step": -1, "tiles": {}, "seed_day": -1}
            if step == 0:
                for k in _TS_REPORT:
                    _TS_REPORT[k] = 0
        st["step"] = step
        if not isinstance(action, dict) or step > 711:
            return action
        day = step // 24
        farm = observation["farms"][seat]
        tiles = farm["tiles"]
        prices = observation["market"]["prices"]
        priv = observation["private"]
        money = farm.get("money", 0)
        commands = [list(action.get("farmer") or ["PASS"])] + \
                   [list(c) for c in (action.get("hands") or [])]
        market = [list(o) for o in (action.get("market") or [])]
        pos_all = [farm["farmer"]] + list(farm["hands"])
        changed = False

        # ---- registry upkeep: drop tiles that stopped being our tomato
        for p in list(st["tiles"]):
            t = tiles[p[1]][p[0]]
            if not (isinstance(t, dict) and t.get("crop") == "TOMATO"):
                st["tiles"].pop(p)
                _TS_REPORT["ts_lost_tiles"] += 1

        # ---- harvest rescue: a tape WATER visit on a mature loaded tomato
        # becomes HARVEST — but only when yesterday was watered (cu == 0), so
        # skipping today's water can never weed the tile.
        for i in range(min(len(commands), len(pos_all))):
            if commands[i][:1] != ["WATER"]:
                continue
            p = tuple(pos_all[i])
            if p not in st["tiles"]:
                continue
            t = tiles[p[1]][p[0]]
            if not isinstance(t, dict):
                continue
            age = day - int(t.get("planted_day", day))
            if (age >= 8 and int(t.get("yield_units", 0)) >= 3
                    and int(t.get("consecutive_unwatered", 1)) == 0):
                commands[i] = ["HARVEST"]
                _TS_REPORT["ts_rescues"] += 1
                changed = True

        # ---- the swap: rewrite the tape's PLANT WHEAT to PLANT TOMATO
        px_t = int(prices.get("TOMATO", 0))
        px_w = int(prices.get("WHEAT", 99))
        wheat_held = int(priv["shed"].get("WHEAT", 0)) + \
            sum(int(i.get("WHEAT", 0)) for i in priv["inventories"])
        if (_TS_FIRST_DAY <= day <= _TS_LAST_DAY
                and len(st["tiles"]) < _TS_MAX_TILES
                and wheat_held >= _TS_WHEAT_RESERVE
                and px_t >= _TS_MIN_PX and px_t >= _TS_RATIO * max(1, px_w)):
            # PLANT is validated collectively per crop: never swap more than
            # the tomato seeds we actually hold this turn
            tom_seeds = int(priv["seeds"].get("TOMATO", 0)) - \
                sum(1 for c in commands if c[:2] == ["PLANT", "TOMATO"])
            room = _TS_MAX_TILES - len(st["tiles"])
            for i in range(min(len(commands), len(pos_all))):
                if room <= 0 or tom_seeds <= 0:
                    break
                if commands[i][:2] == ["PLANT", "WHEAT"]:
                    commands[i][1] = "TOMATO"
                    st["tiles"][tuple(pos_all[i])] = day
                    tom_seeds -= 1
                    room -= 1
                    _TS_REPORT["ts_swaps"] += 1
                    changed = True

        # ---- our own seed pipeline: tiny, money-guarded, once a day
        if (_TS_FIRST_DAY <= day <= _TS_LAST_DAY and st["seed_day"] != day
                and len(st["tiles"]) < _TS_MAX_TILES
                and int(priv["seeds"].get("TOMATO", 0)) < 4
                and money >= 1500 + 4 * 50 and len(market) < 10
                and px_t >= _TS_MIN_PX and px_t >= _TS_RATIO * max(1, px_w)):
            market.append(["BUY_SEED", "TOMATO", 4])
            st["seed_day"] = day
            _TS_REPORT["ts_seed_buys"] += 4
            changed = True

        # ---- sells: the tape has no planned tomato sale — price-gated ours
        shed_t = int(priv["shed"].get("TOMATO", 0))
        planned = sum(int(o[2]) for o in market
                      if len(o) >= 3 and o[:2] == ["SELL", "TOMATO"])
        avail = shed_t - planned
        if avail > 0 and len(market) < 10 and (px_t >= _TS_SELL_PX
                                               or day >= _TS_SELL_DAY):
            market.append(["SELL", "TOMATO", avail])
            _TS_REPORT["ts_sold"] += avail
            changed = True

        if changed:
            action = dict(action)
            action["farmer"] = commands[0]
            action["hands"] = commands[1:]
            action["market"] = market
    except Exception:
        _TS_REPORT["ts_errors"] += 1
    return action


agent.telemetry = _TS_REPORT
agent = globals().pop('agent')
