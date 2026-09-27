"""Build fork/p1.py = c23s + PORT 1 v4: world-fitted animal liquidation +
freed-tile crop cell .

THE DECODED MECHANISM (MMPQ replay ep 113751027, tile-by-tile): from d16 the
top team STOPS FEEDING feed-negative animals -> 2 consecutive unfed days ->
the animal ESCAPES leaving the bare structure (engine :817-819) -> DIG
removes an empty coop/pasture (:486) -> the tile is replanted with demanded
crops the same day.  They shed 5 cows + 1 goose d16-26 in a 1-milk-buyer,
p_wheat~40 world and kept sheep (YARN present) until d29.  Our c23s in the
same world holds 8 cows, feeds 130 animal-days after d16 (own sellable
wheat ~= $4-5k burned) and its late board has ZERO empty tiles (measured:
0-2 at any hour d23-26) - which is why every "plant a cell on empty land"
design failed (v1-v3, all fixture-negative).  Liquidation CREATES the land.

THE SHED RULE is price-led EV per day (robust to the delayed-demand law -
buyer counts alone would repeat the str_bad forecast mistake):
  COW:   ev = p_milk/2 + fert - p_wheat   (milk every 2 days)
  GOOSE: ev = p_egg      + fert - p_wheat (egg daily)
  shed when ev < -5, day 15-27; SHEEP NEVER (V233/V234 committed projects).
A later milk/egg shop raises the product price and stops further shedding.

OWNERSHIP / INTERFERENCE CONTRACT (BASE_REPERTOIRE.md, mistakes #42-#47):
  - FEED suppression only on OUR latched target tiles; the carried wheat
    stays with the unit and midnight-drops to the shed (native sells it).
  - DIG only on a bare structure WE starved (registry), and only replacing
    that unit's dead command (FEED/CARE/COLLECT on a no-animal tile is a
    silent no-op anyway) or PASS.
  - The cell plants ONLY on registry tiles (freed land), with OWN hands
    (hired hours 4-8: R51's fertilizer-tour admission at cha22 :2249 runs
    hours 1-3 and refuses any foreign worker index - measured iteration-1
    kill), OWN seeds (spare accounts; atomic-PLANT guard), PLACE delivery
    (:394, never destroys), credit-only prepended sells.
  - Crop choice on freed tiles: CARROT if carrot drain (12*PET+6*FARMERS)
    >= 12 and p_c >= 35, else WHEAT if p_w >= 22, else leave (no dig).
  - farmer, native hands (other than dead commands on OUR tiles), native
    order sequence: untouched.

Attachment per note: _P1_PARENT = cha20_entry_agent; p1_agent is the
file's LAST callable; telemetry ChainMap; cha20_entry_agent+kaggle_agent
rebound.  Rung 0 (byte-inertness on a world where no species is ever
feed-negative) is mandatory before any bench.
"""

SRC = open(r'fork\c23s.py', encoding='utf-8').read()
assert '_P1_' not in SRC
assert SRC.rstrip().endswith('kaggle_agent = cha20_entry_agent')

LAYER = '''

# ===========================================================================
# P1 v4 : animal liquidation + freed-tile cell - allocation port 1
# ===========================================================================
_P1_PARENT = cha20_entry_agent
_P1_STATE = {}
_P1_REPORT = {"p1_targets": 0, "p1_feed_suppressed": 0, "p1_escapes": 0,
              "p1_digs": 0, "p1_hire_orders": 0, "p1_hands_confirmed": 0,
              "p1_hire_failed": 0, "p1_crew_mismatch": 0, "p1_seed_bought": 0,
              "p1_plants": 0, "p1_plant_no_seed": 0, "p1_waters": 0,
              "p1_harvest_units": 0, "p1_delivered": 0, "p1_sold": 0,
              "p1_tiles_lost": 0, "p1_parent_cmd_overridden": 0,
              "p1_admits": 0, "p1_decl_ev": 0, "p1_decl_cert": 0,
              "p1_decl_rival": 0, "p1_decl_yield": 0, "p1_cycles": 0,
              "p1_errors": 0}
_P1_ADMLOG = []        # reviewable admission records ( review-4 ask)
_P1_ACCESS = ((4, 4), (5, 4), (4, 5), (5, 5))
_P1_FROM = 15          # first starve day (6/8 shop draws in by ~d17 escape)
_P1_TO = 25            # last admission day (needs escape + one full cycle)
_P1_MARGIN = 300       # RELEASE must beat KEEP by this over the horizon
_P1_INTERVAL = {"COW": 2, "GOOSE": 1}
_P1_PRODUCT = {"COW": "MILK", "GOOSE": "EGG"}
_P1_LAST_PLANT = 26    # crop planted day <= 26 still banks by day 29
_P1_MIN_PC = 35        # carrot admission on freed tiles
_P1_MIN_PW = 22        # wheat admission on freed tiles
_P1_SELL_PC = 25
_P1_SELL_PW = 15
_P1_MAX_HANDS = 2
_P1_CASH_HIRE = 3000
_P1_CASH_SEED = 2500
_P1_HIRE_H0, _P1_HIRE_H1 = 4, 8
_P1_DEAD_CMDS = ("FEED", "CARE", "COLLECT_FERTILIZER", "PASS")
_P1_CROP = {"CARROT": (3, 20), "WHEAT": (4, 10)}   # (harvest age, seed cost)


def _p1_state(seat, step):
    st = _P1_STATE.get(seat)
    if st is None or step <= st.get("last", -1):
        st = _P1_STATE[seat] = {
            "last": step, "day": -1, "own": set(), "hired": 0, "pending": None,
            "no_hire": False, "targets": {}, "freed": set(), "tiles": {},
            "spare": {"CARROT": 0, "WHEAT": 0}, "credit": {"CARROT": 0, "WHEAT": 0},
            "planted_today": 0, "visits": {}, "cycled": set(), "had_crop": set()}
    st["last"] = step
    return st


def _p1_step_toward(pos, target):
    dx, dy = target[0] - pos[0], target[1] - pos[1]
    if abs(dx) >= abs(dy) and dx != 0:
        return ["EAST"] if dx > 0 else ["WEST"]
    if dy != 0:
        return ["SOUTH"] if dy > 0 else ["NORTH"]
    return ["PASS"]


def _p1_cell_crop(shops, prices):
    p_c = int(prices.get("CARROT", 0))
    p_w = int(prices.get("WHEAT", 0))
    drain = 12 * shops.count("PET_CAFE") + 6 * shops.count("FARMERS_MARKET")
    if drain >= 12 and p_c >= _P1_MIN_PC:
        return "CARROT"
    if p_w >= _P1_MIN_PW:
        return "WHEAT"
    return None


def _p1_apply(observation, action):
    step = int(observation["step"]); seat = int(observation["player"])
    st = _p1_state(seat, step)
    day, hour = step // 24, step % 24
    farm = observation["farms"][seat]
    priv = observation["private"]
    shops = observation["town"].get("unlocked_shops", [])
    prices = observation["market"]["prices"]
    tiles = farm["tiles"]
    n_hands = len(farm["hands"])

    # resolve a pending hire batch: claim ONLY on an exact count match
    if st["pending"] is not None:
        ps, base, k = st["pending"]
        if step == ps + 1:
            if n_hands == base + k:
                st["own"].update(range(base, base + k))
                st["hired"] += k
                _P1_REPORT["p1_hands_confirmed"] += k
            elif n_hands == base:
                _P1_REPORT["p1_hire_failed"] += k
            else:
                st["no_hire"] = True
                _P1_REPORT["p1_crew_mismatch"] += 1
        st["pending"] = None

    if day != st["day"]:
        st["day"] = day
        st["own"] = set(); st["hired"] = 0; st["pending"] = None
        st["no_hire"] = False; st["planted_today"] = 0
        for c in st["spare"]:
            st["spare"][c] = min(st["spare"][c], int(priv["seeds"].get(c, 0)))
        # --- daily RETAIN-vs-RELEASE admission ( review 4, lane a) ---
        # one conversion in the starve->dig->first-cycle pipeline at a time;
        # KEEP is care-adjusted (a cared cow banks (1+interval)/interval
        # units/day, engine :823-830); RELEASE needs an observed-service
        # certificate and must not enrich a rival still farming the species.
        pipeline_open = (not st["targets"]
                         and not (st["freed"] - st["cycled"]))
        if _P1_FROM <= day <= _P1_TO and pipeline_open:
            p_w = int(prices.get("WHEAT", 0))
            p_fert = min(8, int(prices.get("FERTILIZER", 0)))
            crop_now = _p1_cell_crop(shops, prices)
            opp = observation["farms"][1 - seat]
            opp_sp = {}
            for row_ in opp["tiles"]:
                for t_ in row_:
                    if isinstance(t_, dict) and "animal" in t_:
                        opp_sp[t_["animal"]] = opp_sp.get(t_["animal"], 0) + 1
            remaining = 29 - day
            best = None
            for y, row_ in enumerate(tiles):
                for x, t in enumerate(row_):
                    if not (isinstance(t, dict)
                            and t.get("animal") in _P1_INTERVAL):
                        continue
                    sp = t["animal"]
                    rec = {"day": day, "pos": (x, y), "sp": sp}
                    if crop_now is None:
                        continue
                    if int(t.get("yield_units", 0)) > 0:
                        _P1_REPORT["p1_decl_yield"] += 1
                        continue           # harvest-before-starve
                    if opp_sp.get(sp, 0) > 0:
                        _P1_REPORT["p1_decl_rival"] += 1
                        rec["decline"] = "rival:%d" % opp_sp[sp]
                        _P1_ADMLOG.append(rec)
                        continue
                    vh = st["visits"].get((x, y), {})
                    traffic = vh.get(day - 1, 0) + vh.get(day - 2, 0)
                    if traffic < 4:        # ~2 service visits/day observed
                        _P1_REPORT["p1_decl_cert"] += 1
                        rec["decline"] = "cert:%d" % traffic
                        _P1_ADMLOG.append(rec)
                        continue
                    iv = _P1_INTERVAL[sp]
                    p_prod = int(prices.get(_P1_PRODUCT[sp], 0))
                    keep_d = ((1.0 + iv) / iv) * p_prod + p_fert - 0.8 * p_w
                    myd, seed_cost = _P1_CROP[crop_now]
                    p_crop = int(prices.get(crop_now, 0))
                    units = 3.5 if crop_now == "CARROT" else 5.0
                    crop_d = (units * p_crop - seed_cost) / (myd + 1.0)
                    # rel_d is the crop's daily value ALONE: keep_d already
                    # subtracts the 0.8*p_w feed cost, so adding the feed
                    # saving here would count it twice ( review 5 §5:
                    # the old `0.8*p_w + crop_d` produced a 2f error).
                    rel_d = crop_d
                    gain = (rel_d - keep_d) * max(0, remaining - 3)
                    rec.update(keep_d=round(keep_d, 1), rel_d=round(rel_d, 1),
                               gain=round(gain), traffic=traffic)
                    if gain < _P1_MARGIN:
                        _P1_REPORT["p1_decl_ev"] += 1
                        rec["decline"] = "ev"
                        _P1_ADMLOG.append(rec)
                        continue
                    if best is None or gain > best[0]:
                        best = (gain, (x, y), sp, rec)
            if best is not None:
                _, pos_, sp_, rec = best
                st["targets"][pos_] = sp_
                rec["decline"] = None
                _P1_ADMLOG.append(rec)
                _P1_REPORT["p1_targets"] += 1
                _P1_REPORT["p1_admits"] += 1

    # --- observe service traffic at animal tiles (the certificate's data):
    # count units standing on cow/goose tiles executing FEED/CARE/COLLECT ---
    if _P1_FROM - 3 <= day <= _P1_TO:
        _acts = [action.get("farmer")] + list(action.get("hands") or [])
        _pos = [tuple(farm["farmer"])] + [tuple(h) for h in farm["hands"]]
        for _i, _c in enumerate(_acts):
            if (_i < len(_pos) and isinstance(_c, list) and _c
                    and _c[0] in ("FEED", "CARE", "COLLECT_FERTILIZER")):
                _t = tiles[_pos[_i][1]][_pos[_i][0]]
                if isinstance(_t, dict) and _t.get("animal") in _P1_INTERVAL:
                    vh = st["visits"].setdefault(_pos[_i], {})
                    vh[day] = vh.get(day, 0) + 1

    if not (st["targets"] or st["tiles"] or st["own"]
            or any(st["credit"].values())):
        return action                       # byte-inert outside the port

    units = [list(action.get("farmer") or ["PASS"])] + [
        list(c) if isinstance(c, list) else ["PASS"]
        for c in (action.get("hands") or [])]
    while len(units) < 1 + n_hands:
        units.append(["PASS"])
    market = [o for o in (action.get("market") or [])]
    positions = [tuple(farm["farmer"])] + [tuple(h) for h in farm["hands"]]
    changed = False

    # --- starve + dig: suppress feeds, dig the bare structure we created ---
    for pos, species in list(st["targets"].items()):
        t = tiles[pos[1]][pos[0]]
        if isinstance(t, dict) and "animal" in t:
            continue                        # still starving
        if isinstance(t, dict) and t.get("kind") in ("COOP", "PASTURE"):
            if pos not in st["freed"]:
                st["freed"].add(pos)
                _P1_REPORT["p1_escapes"] += 1
        else:
            st["targets"].pop(pos)          # dug (or something else) already
    # v5: NO hired hands (four wage-negative iterations measured) — the port
    # piggybacks DEAD native commands at its own tiles: units standing on a
    # freed/port tile whose command is FEED/CARE/COLLECT on a gone animal, or
    # PASS, do the port's work for free at native cadence.  MOVE/PICKUP/
    # PLACE/HARVEST and every live command stay untouched.
    crop0 = _p1_cell_crop(shops, prices) if day <= _P1_LAST_PLANT else None
    for pos, (pcrop, pd) in list(st["tiles"].items()):
        t = tiles[pos[1]][pos[0]]
        if not (isinstance(t, dict) and t.get("crop") == pcrop
                and int(t.get("planted_day", -9)) == pd):
            st["tiles"].pop(pos)
            # a resolved freed tile (harvested by anyone, replanted, or even
            # weeded) completes its pipeline slot; only weeds count as losses
            if pos in st["freed"] and pos not in st["cycled"]:
                st["cycled"].add(pos)
                _P1_REPORT["p1_cycles"] += 1
            if isinstance(t, dict) and t.get("kind") == "WEED":
                _P1_REPORT["p1_tiles_lost"] += 1
    held0 = {c: int(priv["seeds"].get(c, 0)) for c in _P1_CROP}
    plants0 = {c: sum(1 for u in units
                      if isinstance(u, list) and len(u) > 1
                      and u[0] == "PLANT" and u[1] == c)
               for c in _P1_CROP}
    for i, cmd in enumerate(units):
        if i >= len(positions):
            break
        pos = positions[i]
        op = cmd[0] if isinstance(cmd, list) and cmd else "PASS"
        #  review-4 one-line repair: suppress FEED only while the animal
        # is still on the tile — a FEED aimed at the bare structure is a DEAD
        # command that must fall through and become the DIG.
        if (op == "FEED" and pos in st["targets"]
                and isinstance(tiles[pos[1]][pos[0]], dict)
                and tiles[pos[1]][pos[0]].get("animal")):
            units[i] = ["PASS"]
            _P1_REPORT["p1_feed_suppressed"] += 1
            changed = True
            continue
        if op not in _P1_DEAD_CMDS:
            continue
        t = tiles[pos[1]][pos[0]]
        if pos in st["tiles"] and isinstance(t, dict):
            pcrop, pd = st["tiles"][pos]
            if not t.get("watered_today"):
                units[i] = ["WATER"]
                _P1_REPORT["p1_waters"] += 1
                changed = True
            elif (day - pd >= _P1_CROP[pcrop][0]
                    and int(t.get("yield_units", 0)) > 0):
                units[i] = ["HARVEST"]
                st["credit"][pcrop] += int(t.get("yield_units", 0))
                _P1_REPORT["p1_harvest_units"] += int(t.get("yield_units", 0))
                st["tiles"].pop(pos)
                if pos in st["freed"] and pos not in st["cycled"]:
                    st["cycled"].add(pos)
                    _P1_REPORT["p1_cycles"] += 1
                changed = True
        elif (pos in st["freed"] and isinstance(t, dict)
                and t.get("kind") in ("COOP", "PASTURE")
                and "animal" not in t and crop0 is not None):
            units[i] = ["DIG"]
            _P1_REPORT["p1_digs"] += 1
            changed = True
        elif (pos in st["freed"] and t is None and crop0 is not None
                and hour <= 16 and pos not in st["tiles"]):
            if (st["spare"][crop0] > 0
                    and held0[crop0] - plants0[crop0] >= 1):
                units[i] = ["PLANT", crop0]
                plants0[crop0] += 1
                st["spare"][crop0] -= 1
                st["tiles"][pos] = (crop0, day)
                _P1_REPORT["p1_plants"] += 1
                changed = True
            else:
                _P1_REPORT["p1_plant_no_seed"] += 1

    # --- the freed-tile cell ---
    crop = _p1_cell_crop(shops, prices) if day <= _P1_LAST_PLANT else None
    plantable = [p for p in st["freed"]
                 if tiles[p[1]][p[0]] is None and p not in st["tiles"]]
    diggable = [p for p in st["freed"]
                if isinstance(tiles[p[1]][p[0]], dict)
                and tiles[p[1]][p[0]].get("kind") in ("COOP", "PASTURE")
                and "animal" not in tiles[p[1]][p[0]]]

    # hiring disabled in v5 (the wage bill killed iterations 1-4; the
    # exemplar does this with an unchanged crew)
    want = 0
    if (want > st["hired"] and _P1_HIRE_H0 <= hour <= _P1_HIRE_H1
            and st["pending"] is None and not st["no_hire"]):
        k = min(want - st["hired"], 10 - len(market))
        if k > 0 and float(farm.get("money", 0)) >= _P1_CASH_HIRE + 500 * k:
            base = n_hands + sum(
                1 for o in market
                if isinstance(o, list) and o and o[0] == "HIRE")
            for _ in range(k):
                market.append(["HIRE"])
            st["pending"] = (step, base, k)
            _P1_REPORT["p1_hire_orders"] += k
            changed = True

    # own seed account (appended orders; parent funding order untouched)
    if crop and plantable and hour <= 20 and len(market) < 10:
        cost = _P1_CROP[crop][1]
        need = min(len(plantable), 8) - st["spare"][crop]
        if need > 0 and float(farm.get("money", 0)) >= _P1_CASH_SEED + cost * need:
            market.append(["BUY_SEED", crop, need])
            st["spare"][crop] += need
            _P1_REPORT["p1_seed_bought"] += need
            changed = True

    # our hands work the cell (never the farmer, never native hands)
    if st["own"]:
        held = {c: int(priv["seeds"].get(c, 0)) for c in _P1_CROP}
        base_plants = {c: sum(1 for u in units
                              if isinstance(u, list) and len(u) > 1
                              and u[0] == "PLANT" and u[1] == c)
                       for c in _P1_CROP}
        invs = priv.get("inventories") or []
        for pos, (pcrop, pd) in list(st["tiles"].items()):
            t = tiles[pos[1]][pos[0]]
            if not (isinstance(t, dict) and t.get("crop") == pcrop
                    and int(t.get("planted_day", -9)) == pd):
                st["tiles"].pop(pos)
                _P1_REPORT["p1_tiles_lost"] += 1
        our_plants = {c: 0 for c in _P1_CROP}
        claimed = set()
        for hi in sorted(st["own"]):
            if hi >= n_hands:
                continue
            ui = hi + 1
            if units[ui] and units[ui][0] != "PASS":
                _P1_REPORT["p1_parent_cmd_overridden"] += 1
            pos = tuple(farm["hands"][hi])
            inv = invs[ui] if ui < len(invs) else {}
            carrying = sum(int(inv.get(c, 0) or 0) for c in _P1_CROP)
            t = tiles[pos[1]][pos[0]]
            cmd = None
            # 1. work the tile we stand on (ours only)
            if pos in st["tiles"] and isinstance(t, dict):
                pcrop, pd = st["tiles"][pos]
                if not t.get("watered_today"):
                    cmd = ["WATER"]
                    _P1_REPORT["p1_waters"] += 1
                elif (day - pd >= _P1_CROP[pcrop][0]
                        and int(t.get("yield_units", 0)) > 0):
                    cmd = ["HARVEST"]
                    st["credit"][pcrop] += int(t.get("yield_units", 0))
                    _P1_REPORT["p1_harvest_units"] += int(t.get("yield_units", 0))
                    st["tiles"].pop(pos)
            # 2. dig a bare structure under our feet
            if (cmd is None and pos in st["freed"] and isinstance(t, dict)
                    and t.get("kind") in ("COOP", "PASTURE")
                    and "animal" not in t and crop):
                cmd = ["DIG"]
                _P1_REPORT["p1_digs"] += 1
            # 3. plant a freed tile under our feet (atomic-PLANT guard)
            if (cmd is None and crop and hour <= 20 and t is None
                    and pos in st["freed"] and pos not in st["tiles"]):
                if (st["spare"][crop] > 0
                        and held[crop] - base_plants[crop] - our_plants[crop] >= 1):
                    cmd = ["PLANT", crop]
                    our_plants[crop] += 1
                    st["spare"][crop] -= 1
                    st["planted_today"] += 1
                    st["tiles"][pos] = (crop, day)
                    _P1_REPORT["p1_plants"] += 1
                else:
                    _P1_REPORT["p1_plant_no_seed"] += 1
            # 4. forced delivery (end of day, or a full pocket)
            if cmd is None and carrying > 0 and (hour >= 18 or carrying >= 6):
                if pos in _P1_ACCESS:
                    for c in _P1_CROP:
                        n = int(inv.get(c, 0) or 0)
                        if n > 0:
                            cmd = ["PLACE", c, n]
                            _P1_REPORT["p1_delivered"] += n
                            break
                else:
                    tgt = min(_P1_ACCESS,
                              key=lambda a: abs(a[0] - pos[0]) + abs(a[1] - pos[1]))
                    cmd = _p1_step_toward(pos, tgt)
            # 5. walk to cell work: water/harvest > dig > plant
            if cmd is None:
                jobs = [p for p, (pcrop, pd) in st["tiles"].items()
                        if p not in claimed and p != pos
                        and isinstance(tiles[p[1]][p[0]], dict)
                        and (not tiles[p[1]][p[0]].get("watered_today")
                             or (day - pd >= _P1_CROP[pcrop][0]
                                 and int(tiles[p[1]][p[0]].get("yield_units", 0)) > 0))]
                if not jobs and crop:
                    jobs = [p for p in (diggable + plantable)
                            if p not in claimed and p != pos]
                if jobs:
                    tgt = min(jobs, key=lambda p: abs(p[0] - pos[0]) + abs(p[1] - pos[1]))
                    claimed.add(tgt)
                    cmd = _p1_step_toward(pos, tgt)
            # 6. idle: bring the pocket home
            if cmd is None and carrying > 0:
                if pos in _P1_ACCESS:
                    for c in _P1_CROP:
                        n = int(inv.get(c, 0) or 0)
                        if n > 0:
                            cmd = ["PLACE", c, n]
                            _P1_REPORT["p1_delivered"] += n
                            break
                else:
                    tgt = min(_P1_ACCESS,
                              key=lambda a: abs(a[0] - pos[0]) + abs(a[1] - pos[1]))
                    cmd = _p1_step_toward(pos, tgt)
            units[ui] = cmd or ["PASS"]
            changed = True

    # --- sell our credit (prepended: sales-first; shed stock is the bound) ---
    for c, floor in (("CARROT", _P1_SELL_PC), ("WHEAT", _P1_SELL_PW)):
        p = int(prices.get(c, 0))
        if (st["credit"][c] > 0 and len(market) < 10
                and (p >= floor or (hour >= 20 and p >= 2))):
            _view = {"farmer": units[0], "hands": units[1:], "market": market}
            _stock = int(projected_shed(_view, FarmView(observation)).get(c, 0))
            _selling = sum(int(o[2]) for o in market
                           if isinstance(o, list) and len(o) >= 3
                           and o[:2] == ["SELL", c])
            q = min(st["credit"][c], 12, _stock - _selling)
            if q > 0:
                market.insert(0, ["SELL", c, q])
                st["credit"][c] -= q
                _P1_REPORT["p1_sold"] += q
                changed = True

    if not changed:
        return action
    return dict(action, farmer=units[0], hands=units[1:], market=market)


def p1_agent(observation, configuration=None):
    if int(observation.get("step", 0)) == 0:
        for _k in _P1_REPORT:
            _P1_REPORT[_k] = 0
        del _P1_ADMLOG[:]
    action = _P1_PARENT(observation, configuration)
    try:
        standard = configuration is None or all(
            configuration.get(k, v) == v for k, v in
            (("boardSize", 10), ("turnsPerDay", 24), ("shedCapacity", 100),
             ("maxMarketOrdersPerTurn", 10)))
        if standard and isinstance(action, dict):
            action = _p1_apply(observation, action)
    except Exception:
        _P1_REPORT["p1_errors"] += 1
    return action


import collections as _p1_coll
p1_agent.telemetry = _p1_coll.ChainMap(_P1_REPORT, _P1_PARENT.telemetry)
cha20_entry_agent = p1_agent
kaggle_agent = cha20_entry_agent
'''

import ast

out = SRC.rstrip('\n') + LAYER
ast.parse(out)
open(r'fork\p1.py', 'w', encoding='utf-8', newline='\n').write(out)
print(f'wrote fork/p1.py ({len(out):,} chars), syntax OK')
