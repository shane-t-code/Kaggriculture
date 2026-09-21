

# STRDIG v107a: recycle inert strawberry tiles with PASS-only labor.
# Dig inert STR (yield 0, age>6) from day 18, replant CARROT (WHEAT backup),
# water EVERY day (no-weed rule), harvest when ready. Only units whose parent
# action is PASS are used (the tape wants them idle: no completeness damage,
# no fib hires). Only ex-STR tiles are touched (feed-law safe: never a wheat
# feed-cycle tile). Chassis reflexes handle the selling.
_SD_FROM = 18          # first dig day
_SD_PLANT_TO = 26      # last plant day (carrot needs ~3 days + window waters)
_SD_CAP = 8            # max tiles in flight
_SD_SEED_MIN = 3       # top up seeds below this
_SD_STATE = {}
_SD_TELEM = {"digs": 0, "plants": 0, "waters": 0, "harvs": 0, "buys": 0,
             "idle_used": 0, "errors": 0}

_SD_PARENT = agent
def agent(observation, configuration=None):
    action = _SD_PARENT(observation, configuration)
    try:
        day = int(observation.get("day", 0))
        if day < _SD_FROM or not isinstance(action, dict):
            return action
        hour = int(observation.get("hour", 0))
        seat = int(observation.get("player", 0))
        step = int(observation.get("step", day * 24 + hour))
        st = _SD_STATE.get(seat)
        if st is None or step <= st["step"]:
            st = _SD_STATE[seat] = {"step": -1, "mine": set()}
        st["step"] = step
        farm = observation["farms"][seat]
        tiles = farm["tiles"]
        priv = observation.get("private", {})
        seeds = priv.get("seeds", {})

        def tl(x, y):
            t = tiles[y][x]
            return t if isinstance(t, dict) else None

        # forget tiles that stopped being ours (harvested & gone, weeded...)
        st["mine"] = {p for p in st["mine"] if (lambda t: t is None or (
            t.get("kind") == "PLANT")) (tl(*p))}
        # task lists
        water_now, harv_now, plant_now, dig_now = [], [], [], []
        inflight = 0
        for (x, y) in list(st["mine"]):
            t = tl(x, y)
            if t is None:
                if day <= _SD_PLANT_TO:
                    plant_now.append((x, y))
                    inflight += 1
                continue
            inflight += 1
            yu = int(t.get("yield_units", 0))
            age = day - int(t.get("planted_day", day))
            if yu > 0 and age >= 2:
                harv_now.append((x, y))
            if not t.get("watered_today") and t.get("crop"):
                water_now.append((x, y))
        if day <= _SD_PLANT_TO and inflight < _SD_CAP:
            for y in range(10):
                for x in range(10):
                    if (x, y) in st["mine"]:
                        continue
                    t = tl(x, y)
                    if (t and t.get("kind") == "PLANT"
                            and t.get("crop") == "STRAWBERRY"
                            and int(t.get("yield_units", 0)) == 0
                            and day - int(t.get("planted_day", 0)) > 6):
                        dig_now.append((x, y))
            dig_now = dig_now[: _SD_CAP - inflight]

        hands = farm.get("hands", [])
        units = [list(action.get("farmer") or ["PASS"])] + \
                [list(c) for c in (action.get("hands") or [])]
        while len(units) < 1 + len(hands):
            units.append(["PASS"])
        positions = [tuple(farm.get("farmer", (4, 4)))] + [tuple(h) for h in hands]

        # TAIL-IDLE ONLY: the route is positional — a PASS can mean "stand
        # here for tomorrow". NEVER move the farmer (persists across days);
        # a hand is free only if the tape gives it nothing but PASS for the
        # REST OF TODAY (hands expire at midnight, so then it's truly spare).
        def hand_free(hi):
            try:
                native = _IMPL.chassis.players.get(seat)
                if not native:
                    return False
                for t in range(step + 1, day * 24 + 24):
                    tape = _IMPL.chassis.routes[2 if t >= 648 else native["route"]]
                    if t >= len(tape) or not isinstance(tape[t], dict):
                        continue
                    hs = tape[t].get("hands") or []
                    if hi < len(hs) and hs[hi] and hs[hi][0] != "PASS":
                        return False
                return True
            except Exception:
                return False

        idle = [i for i in range(1, 1 + len(hands))
                if i < len(units) and units[i] and units[i][0] == "PASS"
                and hand_free(i - 1)]
        n_carrot = int(seeds.get("CARROT", 0))
        n_wheat = int(seeds.get("WHEAT", 0))
        planted_this_turn = {"CARROT": 0, "WHEAT": 0}
        for c in units:
            if c[:1] == ["PLANT"] and len(c) > 1 and c[1] in planted_this_turn:
                planted_this_turn[c[1]] += 1
        taken = set()
        changed = False

        def assign(tasks, kind):
            nonlocal changed
            for (tx, ty) in tasks:
                if not idle or (tx, ty) in taken:
                    continue
                i = min(idle, key=lambda j: abs(positions[j][0] - tx)
                        + abs(positions[j][1] - ty))
                x, y = positions[i]
                if (x, y) == (tx, ty):
                    if kind == "PLANT":
                        crop = "CARROT" if n_carrot - planted_this_turn["CARROT"] > 0 \
                            else ("WHEAT" if n_wheat - planted_this_turn["WHEAT"] > 0
                                  else None)
                        if crop is None or hour > 20:
                            continue
                        units[i] = ["PLANT", crop]
                        planted_this_turn[crop] += 1
                        _SD_TELEM["plants"] += 1
                    else:
                        units[i] = [kind]
                        _SD_TELEM[{"WATER": "waters", "HARVEST": "harvs",
                                   "DIG": "digs"}[kind]] += 1
                        if kind == "DIG":
                            st["mine"].add((tx, ty))
                else:
                    units[i] = ["EAST" if tx > x else "WEST" if tx < x
                                else "SOUTH" if ty > y else "NORTH"]
                idle.remove(i)
                taken.add((tx, ty))
                _SD_TELEM["idle_used"] += 1
                changed = True

        assign(water_now, "WATER")
        assign(harv_now, "HARVEST")
        assign(plant_now, "PLANT")
        if hour >= 6:                      # after the tape's morning hires land
            assign(dig_now, "DIG")

        market = [list(o) for o in (action.get("market") or [])]
        if day <= _SD_PLANT_TO and n_carrot < _SD_SEED_MIN and len(market) < 10 \
                and farm.get("money", 0) > 2000 \
                and not any(o[:2] == ["BUY_SEED", "CARROT"] for o in market):
            market.append(["BUY_SEED", "CARROT", 4])
            _SD_TELEM["buys"] += 1
            changed = True
        if changed:
            return dict(action, farmer=units[0], hands=units[1:], market=market[:10])
        return action
    except Exception:
        _SD_TELEM["errors"] += 1
        return action
agent.telemetry = _SD_TELEM
agent = globals().pop("agent")
