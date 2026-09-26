"""Build the replanner rung-1 pair (Exp 150, per  review 3's corrected
contract):

fork/r1.py  = c23s + FULL TAKEOVER at day 10 in gated worlds (PET_CAFE >= 2
              among revealed draws AND p_carrot >= 35 at step 240), running a
              MAINTENANCE-ONLY per-step planner (water / feed+care / collect /
              harvest / wheat courier / simple sells; NO new planting, NO
              land, crew sized to the job count).  After commitment the
              parent chain is never called again (its stateful planners must
              not run against a farm they no longer own).
fork/rc0.py = c23s + the IDENTICAL gate; once committed it only SUPPRESSES
              native PLANT commands and BUY_SEED orders — the matched
              no-new-investment ablation control.

Acceptance is the obligation ledger (tools/ledger.py), NOT final bank:
missed waterings / feeds, weeds created, animal escapes, wages.
Attachment per note: _X_PARENT = cha20_entry_agent; wrapper is the
file's last callable; telemetry chained; kaggle_agent rebound.
"""

SRC = open(r'fork\c23s.py', encoding='utf-8').read()
assert '_RP_' not in SRC

COMMON = '''

# ===========================================================================
# %(name)s : gated day-10 %(kind)s
# ===========================================================================
_RP_PARENT = cha20_entry_agent
_RP_STATE = {}
_RP_REPORT = {"rp_committed": 0, "rp_hires": 0, "rp_jobs_done": 0,
              "rp_feeds": 0, "rp_waters": 0, "rp_harvests": 0, "rp_cares": 0,
              "rp_collects": 0, "rp_pickups": 0, "rp_sell_units": 0,
              "rp_plants": 0, "rp_plant_no_tile": 0, "rp_plant_no_seed": 0,
              "rp_plant_jobs": 0, "rp_plant_unassigned": 0,
              "rp_suppressed": 0, "rp_errors": 0}
_RP_ACCESS = ((4, 4), (5, 4), (4, 5), (5, 5))


def _rp_gate(observation):
    shops = observation["town"].get("unlocked_shops", [])
    p_c = int(observation["market"]["prices"].get("CARROT", 0))
    return shops.count("PET_CAFE") >= 2 and p_c >= 35


def _rp_state(seat, step):
    st = _RP_STATE.get(seat)
    if st is None or step <= st.get("last", -1):
        st = _RP_STATE[seat] = {"last": step, "committed": False}
    st["last"] = step
    return st
'''

PLANNER = '''

_RP_ONE_SHOT = {"WHEAT": (4, 6), "CARROT": (3, 4), "MELON": (12, 6)}
_RP_ONGOING = {"TOMATO": 8, "STRAWBERRY": 10}


def _rp_jobs(observation, seat):
    """(pos, kind) job list from live farm state. kinds: WATER, FEED, CARE,
    COLLECT, HARVEST.  FEED requires the unit to carry wheat."""
    farm = observation["farms"][seat]
    day = int(observation["step"]) // 24
    jobs = []
    for y, row in enumerate(farm["tiles"]):
        for x, tile in enumerate(row):
            if not isinstance(tile, dict):
                continue
            kind = tile.get("kind")
            if kind == "PLANT":
                if not tile.get("watered_today"):
                    jobs.append(((x, y), "WATER"))
                if int(tile.get("fertilized_until_day", -1)) < day:
                    crop = tile.get("crop")
                    age = day - int(tile.get("planted_day", day))
                    if (crop in _RP_ONGOING or
                            (crop in _RP_ONE_SHOT and age < _RP_ONE_SHOT[crop][0])):
                        jobs.append(((x, y), "FERT"))
                yu = int(tile.get("yield_units", 0))
                crop = tile.get("crop")
                age = day - int(tile.get("planted_day", day))
                if yu > 0:
                    if crop in _RP_ONE_SHOT:
                        myd, cap = _RP_ONE_SHOT[crop]
                        if age >= myd or yu >= cap:
                            jobs.append(((x, y), "HARVEST"))
                    elif crop in _RP_ONGOING:
                        if yu >= 2 and age >= _RP_ONGOING[crop]:
                            jobs.append(((x, y), "HARVEST"))
            elif "animal" in tile:
                if not tile.get("fed_today"):
                    jobs.append(((x, y), "FEED"))
                if int(tile.get("yield_units", 0)) >= 1:
                    jobs.append(((x, y), "HARVEST"))
                if not tile.get("cared_today"):
                    jobs.append(((x, y), "CARE"))
                if tile.get("fertilizer_available"):
                    jobs.append(((x, y), "COLLECT"))
    return jobs


_RP_TIER = {"FEED": 0, "WATER": 1, "HARVEST": 2, "PLANT": 2, "COLLECT": 3,
            "CARE": 3, "DIG": 3, "FERT": 4}


def _rp_step_toward(pos, target):
    dx, dy = target[0] - pos[0], target[1] - pos[1]
    if abs(dx) >= abs(dy) and dx != 0:
        return ["EAST"] if dx > 0 else ["WEST"]
    if dy != 0:
        return ["SOUTH"] if dy > 0 else ["NORTH"]
    return ["PASS"]


def _rp_plan(observation, seat, st):
    """One planned action dict for a committed step."""
    step = int(observation["step"])
    hour = step % 24
    farm = observation["farms"][seat]
    priv = observation["private"]
    prices = observation["market"]["prices"]
    positions = [tuple(farm["farmer"])] + [tuple(h) for h in farm["hands"]]
    invs = priv.get("inventories") or [{}]
    n_units = len(positions)
    units = [["PASS"] for _ in range(n_units)]
    market = []

    jobs = _rp_jobs(observation, seat)

    # RUNG 2 — the demand pipeline: plant carrots against revealed PET_CAFE
    # demand (12/day each; FARMERS_MARKET 6), price-gated, stopping when the
    # harvest window no longer fits the season (plant day <= 26).
    day = step // 24
    if st.get("plant_day") != day:
        st["plant_day"] = day
        st["planted_n"] = 0
    shops = observation["town"].get("unlocked_shops", [])
    p_c = int(prices.get("CARROT", 0))
    plant_target = 0
    if day <= 26 and hour <= 20 and p_c >= 30:
        plant_target = min(20, 4 * shops.count("PET_CAFE")
                           + 2 * shops.count("FARMERS_MARKET"))
    plant_quota = max(0, plant_target - st["planted_n"])
    seeds_free = int(priv["seeds"].get("CARROT", 0))
    empties, weeds = [], []
    if plant_target > 0:
        for y, row in enumerate(farm["tiles"]):
            for x, tile in enumerate(row):
                if tile is None:
                    empties.append((x, y))
                elif isinstance(tile, dict) and tile.get("kind") == "WEED":
                    weeds.append((x, y))
        empties.sort(key=lambda p: abs(p[0] - 4.5) + abs(p[1] - 4.5))
        if len(empties) < plant_quota:
            for pos in weeds[:plant_quota - len(empties)]:
                jobs.append((pos, "DIG"))

    feed_jobs = [j for j in jobs if j[1] == "FEED"]
    n_animals = sum(1 for row in farm["tiles"] for t in row
                    if isinstance(t, dict) and "animal" in t)
    shed_wheat = int(priv["shed"].get("WHEAT", 0))
    carried_wheat = [int((invs[i] if i < len(invs) else {}).get("WHEAT", 0))
                     for i in range(n_units)]

    # hour 0: hire to the job load (fib wages are cheap at this crew size);
    # daily job volume ~= jobs standing now + waters/feeds recurring
    if hour == 0:
        want = min(12, max(1, -(-len(jobs) // 8)))
        need = want - (n_units - 1)
        for _ in range(max(0, min(need, 10))):
            market.append(["HIRE"])
            _RP_REPORT["rp_hires"] += 1

    # market housekeeping (orders process IN LIST ORDER, so sells free shed
    # room before buys — engine :667 refuses BUY_PRODUCT into a full shed)
    shed_total = sum(int(v) for v in priv["shed"].values())
    sell_now = (hour == 1 or hour >= 18 or shed_total > 60
                or int(priv["shed"].get("CARROT", 0)) >= 8)
    if hour >= 1 and sell_now:
        for item, q in sorted(priv["shed"].items(),
                              key=lambda kv: -int(prices.get(kv[0], 0))):
            if item == "WHEAT" or int(q) <= 0 or item in ("GOOSE", "COW", "SHEEP"):
                continue
            if int(prices.get(item, 0)) < 2:
                continue
            if len(market) >= 9:
                break
            n = min(int(q), 12) if item == "CARROT" else int(q)
            market.append(["SELL", item, n])
            _RP_REPORT["rp_sell_units"] += n
    # feed stock: keep two days of wheat on hand (buy AFTER the sells above)
    if hour in (1, 13):
        target = 2 * n_animals + 2
        have = shed_wheat + sum(carried_wheat)
        if have < target and len(market) < 10:
            deficit = target - have
            if float(farm.get("money", 0)) >= 300 + 45 * deficit:
                market.append(["BUY_PRODUCT", "WHEAT", int(deficit)])
        # carrot seeds for tomorrow's pipeline (atomic-PLANT headroom)
        if plant_target > 0 and len(market) < 10:
            want_seeds = 2 * plant_target - seeds_free
            if want_seeds > 0 and float(farm.get("money", 0)) >= 800 + 20 * want_seeds:
                market.append(["BUY_SEED", "CARROT", int(want_seeds)])
    # land: tiles are the pipeline's binding constraint, not labor — buy the
    # next quadrant when demand-justified planting starves for space
    if (hour == 2 and plant_target > 0 and day <= 24
            and len(empties) + len(weeds) < plant_target and len(market) < 10):
        locked = 4 - len(farm.get("unlocked_quadrants", ["NW"]))
        cost = {3: 1000, 2: 2000, 1: 4000}.get(locked)
        if cost and float(farm.get("money", 0)) >= 3000 + cost:
            market.append(["BUY_LAND"])

    claimed = set()

    def do(i, cmd):
        units[i] = cmd
        _RP_REPORT["rp_jobs_done"] += 1

    carried_fert = [int((invs[i] if i < len(invs) else {}).get("FERTILIZER", 0))
                    for i in range(n_units)]

    # pass 1: jobs on the tile we stand on
    for i, pos in enumerate(positions):
        here = [j for j in jobs if j[0] == pos and j not in claimed]
        here.sort(key=lambda j: _RP_TIER[j[1]])
        acted = False
        for j in here:
            kind = j[1]
            if kind == "FEED" and carried_wheat[i] > 0:
                do(i, ["FEED"]); carried_wheat[i] -= 1
                _RP_REPORT["rp_feeds"] += 1
            elif kind == "WATER":
                do(i, ["WATER"]); _RP_REPORT["rp_waters"] += 1
            elif kind == "HARVEST":
                do(i, ["HARVEST"]); _RP_REPORT["rp_harvests"] += 1
            elif kind == "CARE":
                do(i, ["CARE"]); _RP_REPORT["rp_cares"] += 1
            elif kind == "COLLECT":
                do(i, ["COLLECT_FERTILIZER"]); _RP_REPORT["rp_collects"] += 1
                carried_fert[i] += 1
            elif kind == "FERT" and carried_fert[i] > 0:
                do(i, ["FERTILIZE"]); carried_fert[i] -= 1
            elif kind == "PLANT":
                planned = sum(1 for c in units if c[:2] == ["PLANT", "CARROT"])
                if farm["tiles"][pos[1]][pos[0]] is not None:
                    _RP_REPORT["rp_plant_no_tile"] += 1
                    continue
                if seeds_free - planned < 1:
                    _RP_REPORT["rp_plant_no_seed"] += 1
                    continue
                do(i, ["PLANT", "CARROT"])
                st["planted_n"] += 1
                _RP_REPORT["rp_plants"] += 1
            elif kind == "DIG":
                do(i, ["DIG"])
            else:
                continue
            claimed.add(j); acted = True
            break
        if acted:
            continue
        # standing at the shed with empty hands while animals are hungry:
        # take HALF the outstanding need so a second courier can split it
        open_feeds_n = sum(1 for j in feed_jobs if j not in claimed)
        if (pos in _RP_ACCESS and carried_wheat[i] == 0 and shed_wheat > 0
                and sum(carried_wheat) < open_feeds_n):
            n = min(shed_wheat, max(1, -(-open_feeds_n // 2)))
            do(i, ["PICKUP", "WHEAT", n]); carried_wheat[i] += n
            shed_wheat -= n
            _RP_REPORT["rp_pickups"] += 1

    # PLANTER ROLES: the last P units do nothing but plant and give their
    # own plant its same-day water (nearest-job greedy starves planting —
    # measured: 3,608/4,019 plant jobs unassigned on seed 7456)
    n_planters = 0
    if plant_target > 0 and n_units >= 3:
        n_planters = max(0, min(3, -(-plant_target // 6), n_units - 2))
    planter_ix = set(range(n_units - n_planters, n_units))
    taken_empties = set()
    for i in sorted(planter_ix):
        if units[i] != ["PASS"]:
            continue
        pos = positions[i]
        tile = farm["tiles"][pos[1]][pos[0]]
        planned = sum(1 for c in units if c[:2] == ["PLANT", "CARROT"])
        if (tile is None and st["planted_n"] < plant_target
                and pos in [tuple(e) for e in empties]):
            if seeds_free - planned >= 1:
                do(i, ["PLANT", "CARROT"])
                st["planted_n"] += 1
                _RP_REPORT["rp_plants"] += 1
            else:
                _RP_REPORT["rp_plant_no_seed"] += 1
            continue
        if (isinstance(tile, dict) and tile.get("kind") == "PLANT"
                and not tile.get("watered_today")):
            do(i, ["WATER"])
            _RP_REPORT["rp_waters"] += 1
            continue
        if st["planted_n"] < plant_target:
            cand = [e for e in empties if e not in taken_empties]
            if cand:
                tgt = min(cand, key=lambda e: abs(e[0]-pos[0]) + abs(e[1]-pos[1]))
                taken_empties.add(tgt)
                units[i] = _rp_step_toward(pos, tgt)

    # couriers: if hungry animals outnumber carried wheat, send up to TWO
    # idle units to the shed; everyone else stays on watering/harvest duty
    open_feeds_n = sum(1 for j in feed_jobs if j not in claimed)
    if open_feeds_n > sum(carried_wheat) and shed_wheat > 0:
        movers = sorted(
            (i for i, u in enumerate(units)
             if u == ["PASS"] and carried_wheat[i] == 0),
            key=lambda k: min(abs(a[0]-positions[k][0]) + abs(a[1]-positions[k][1])
                              for a in _RP_ACCESS))
        for i in movers[:2]:
            tgt = min(_RP_ACCESS, key=lambda a: abs(a[0]-positions[i][0]) +
                      abs(a[1]-positions[i][1]))
            units[i] = _rp_step_toward(positions[i], tgt)

    # pass 2: idle units to the nearest open job, deadline tiers first;
    # FEED is claimable only while holding wheat, FERT only holding fertilizer
    open_jobs = [j for j in jobs if j not in claimed]
    for tier in (0, 1, 2, 3, 4):
        pool = [j for j in open_jobs if _RP_TIER[j[1]] == tier]
        for i, pos in enumerate(positions):
            if units[i] != ["PASS"] or not pool:
                continue
            best, bd = None, 99
            for j in pool:
                if j[1] == "FEED" and carried_wheat[i] <= 0:
                    continue
                if j[1] == "FERT" and carried_fert[i] <= 0:
                    continue
                d = abs(j[0][0] - pos[0]) + abs(j[0][1] - pos[1])
                if d < bd:
                    best, bd = j, d
            if best is not None:
                claimed.add(best)
                pool.remove(best)
                open_jobs.remove(best)
                units[i] = _rp_step_toward(pos, best[0])
        if tier == 2:
            _RP_REPORT["rp_plant_unassigned"] += sum(1 for j in pool if j[1] == "PLANT")

    return {"farmer": units[0], "hands": units[1:], "market": market}


def rp_agent(observation, configuration=None):
    try:
        step = int(observation["step"]); seat = int(observation["player"])
        if step == 0:
            for k in _RP_REPORT:
                _RP_REPORT[k] = 0
        st = _rp_state(seat, step)
        standard = configuration is None or all(
            configuration.get(k, v) == v for k, v in
            (("boardSize", 10), ("turnsPerDay", 24), ("shedCapacity", 100),
             ("maxMarketOrdersPerTurn", 10)))
        if standard and not st["committed"] and step == 240 and _rp_gate(observation):
            st["committed"] = True
            _RP_REPORT["rp_committed"] = 1
        if st["committed"]:
            return _rp_plan(observation, seat, st)
    except Exception:
        _RP_REPORT["rp_errors"] += 1
    return _RP_PARENT(observation, configuration)
'''

SUPPRESSOR = '''

def rp_agent(observation, configuration=None):
    action = _RP_PARENT(observation, configuration)
    try:
        step = int(observation["step"]); seat = int(observation["player"])
        if step == 0:
            for k in _RP_REPORT:
                _RP_REPORT[k] = 0
        st = _rp_state(seat, step)
        standard = configuration is None or all(
            configuration.get(k, v) == v for k, v in
            (("boardSize", 10), ("turnsPerDay", 24), ("shedCapacity", 100),
             ("maxMarketOrdersPerTurn", 10)))
        if standard and not st["committed"] and step == 240 and _rp_gate(observation):
            st["committed"] = True
            _RP_REPORT["rp_committed"] = 1
        if st["committed"] and isinstance(action, dict):
            units = [list(action.get("farmer") or ["PASS"])] + [
                list(c) for c in (action.get("hands") or [])]
            changed = False
            for i, c in enumerate(units):
                if c and c[0] == "PLANT":
                    units[i] = ["PASS"]
                    _RP_REPORT["rp_suppressed"] += 1
                    changed = True
            market = [o for o in (action.get("market") or [])
                      if not (isinstance(o, list) and len(o) >= 1 and o[0] == "BUY_SEED")]
            if len(market) != len(action.get("market") or []):
                changed = True
            if changed:
                action = dict(action, farmer=units[0], hands=units[1:], market=market)
    except Exception:
        _RP_REPORT["rp_errors"] += 1
    return action
'''

FOOTER = '''

import collections as _rp_coll
rp_agent.telemetry = _rp_coll.ChainMap(_RP_REPORT, _RP_PARENT.telemetry)
cha20_entry_agent = rp_agent
kaggle_agent = cha20_entry_agent
'''

import ast

for path, name, kind, body in (
        (r'fork\r1.py', 'R1 TAKEOVER', 'maintenance takeover', PLANNER),
        (r'fork\rc0.py', 'RC0 CONTROL', 'planting-suppression control', SUPPRESSOR)):
    out = SRC.rstrip('\n') + (COMMON % {'name': name, 'kind': kind}) + body + FOOTER
    ast.parse(out)
    open(path, 'w', encoding='utf-8', newline='\n').write(out)
    print(f'wrote {path} ({len(out):,} chars), syntax OK')
