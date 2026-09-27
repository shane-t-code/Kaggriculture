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

import json as _json

SRC = open(r'fork\c23s.py', encoding='utf-8').read()
assert '_RP_' not in SRC

# the distilled crop-mix head : tools/mk_distill.py -> literals
_HEAD_LIT = _json.load(open(r'results\distill\head_lit.json', encoding='utf-8'))

COMMON = '''

# ===========================================================================
# %(name)s : gated day-10 %(kind)s
# ===========================================================================
_RP_PARENT = cha20_entry_agent
_RP_STATE = {}
_RP_REPORT = {"rp_committed": 0, "rp_hires": 0, "rp_jobs_done": 0,
              "rp_feeds": 0, "rp_waters": 0, "rp_harvests": 0, "rp_cares": 0,
              "rp_collects": 0, "rp_pickups": 0, "rp_sell_units": 0,
              "rp_survival_moves": 0, "rp_survival_waters": 0,
              "rp_adm_capped": 0, "rp_adm_expanded": 0, "rp_adm_shed": 0,
              "rp_plants": 0, "rp_plant_no_tile": 0, "rp_plant_no_seed": 0,
              "rp_plant_jobs": 0, "rp_plant_unassigned": 0,
              "rp_wheat_plants": 0, "rp_wheat_sold": 0,
              "rp_emergency_wheat": 0, "rp_delivered": 0,
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
_RP_WHE_SHOPS = ("BAKERY", "PIZZA_SHOP", "BRUNCH_SPOT", "ICE_CREAM_SHOP",
                 "FARMERS_MARKET")

# ---------------------------------------------------------------------------
# The distilled CROP-MIX HEAD : a linear
# model over 65 acting-player-visible features, trained on the top-10
# teams' 29 public episodes (split by episode; held-out test beat the
# calendar and shops baselines; carrot head learned +PET_CAFE +price
# -market-glut, wheat head learned -PET_CAFE +PIZZA +land).  It predicts
# the teacher's LANDED plants over the next 3 days.  Pure-Python dot
# product — no imports, trivially inside the step budget.
# ---------------------------------------------------------------------------
_RP_USE_HEAD = __USE_HEAD__
_RP_HEAD = __HEAD_LIT__
_RP_HEAD_SHOPS = ["BAKERY", "PIZZA_SHOP", "BRUNCH_SPOT", "YARN_STORE",
                  "ICE_CREAM_SHOP", "PET_CAFE", "SMOOTHIE_SHOP",
                  "FARMERS_MARKET"]
_RP_HEAD_PRODUCTS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON",
                     "EGG", "MILK", "WOOL", "FERTILIZER"]
_RP_HEAD_CROPS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON"]


def _rp_head_counts(farm):
    crop_n = {c: 0 for c in _RP_HEAD_CROPS}
    ani_n = {"GOOSE": 0, "COW": 0, "SHEEP": 0}
    empt = weed = 0
    for row in farm["tiles"]:
        for t in row:
            if t is None:
                empt += 1
            elif isinstance(t, dict):
                if t.get("kind") == "PLANT":
                    crop_n[t.get("crop")] = crop_n.get(t.get("crop"), 0) + 1
                elif t.get("kind") == "WEED":
                    weed += 1
                elif "animal" in t:
                    ani_n[t.get("animal")] = ani_n.get(t.get("animal"), 0) + 1
    return crop_n, ani_n, empt, weed


def _rp_head_targets(observation, seat, prev_crew):
    """(wheat, carrot) plants the teachers would land over the NEXT 3 DAYS.
    Features are built by NAME and selected per the exported feature list,
    so training-side feature changes cannot silently misalign."""
    day = int(observation["step"]) // 24
    d = str(min(28, max(10, day)))
    farm = observation["farms"][seat]
    opp = observation["farms"][1 - seat]
    priv = observation["private"]
    prices = observation["market"]["prices"]
    inv = observation["market"]["inventory"]
    shops = observation["town"].get("unlocked_shops", [])
    cn, an, empt, weed = _rp_head_counts(farm)
    on, oan, oempt, _w = _rp_head_counts(opp)
    vals = {"day": day, "days_left": 29 - day,
            "money": float(farm.get("money", 0)) / 1000.0,
            "prev_crew": prev_crew,
            "quads": len(farm.get("unlocked_quadrants", [])),
            "my_empty": empt, "my_weed": weed,
            "opp_money": float(opp.get("money", 0)) / 1000.0,
            "opp_empty": oempt}
    for s in _RP_HEAD_SHOPS:
        vals["shop_" + s] = shops.count(s)
    for p in _RP_HEAD_PRODUCTS:
        vals["p_" + p] = int(prices.get(p, 0))
        vals["minv_" + p] = int(inv.get(p, 0)) / 1000.0
        vals["shed_" + p] = int(priv["shed"].get(p, 0))
    for c in _RP_HEAD_CROPS:
        vals["seed_" + c] = int(priv["seeds"].get(c, 0))
        vals["my_" + c] = cn[c]
        vals["op_" + c] = on[c]
    for a in ("GOOSE", "COW", "SHEEP"):
        vals["my_" + a] = an[a]
        vals["op_" + a] = oan[a]
    x = [vals[n] for n in _RP_HEAD["feature_names"]]
    mu, sd = _RP_HEAD["mu"], _RP_HEAD["sd"]
    z = [(x[i] - mu[i]) / sd[i] for i in range(len(mu))] + [1.0]
    w = sum(z[i] * _RP_HEAD["W_wheat"][i] for i in range(len(z)))
    c = sum(z[i] * _RP_HEAD["W_carrot"][i] for i in range(len(z)))
    return (w + _RP_HEAD["day_mean_wheat"][d],
            c + _RP_HEAD["day_mean_carrot"][d])


def _rp_jobs(observation, seat, shed=()):
    """(pos, kind) job list from live farm state. kinds: WATER, FEED, CARE,
    COLLECT, HARVEST.  FEED requires the unit to carry wheat.  Tiles in
    `shed` are deliberately unserviced (valued allocator): salvage-harvest
    any standing yield, never water or fertilize again."""
    farm = observation["farms"][seat]
    day = int(observation["step"]) // 24
    jobs = []
    for y, row in enumerate(farm["tiles"]):
        for x, tile in enumerate(row):
            if not isinstance(tile, dict):
                continue
            kind = tile.get("kind")
            if kind == "PLANT" and (x, y) in shed:
                if int(tile.get("yield_units", 0)) > 0:
                    jobs.append(((x, y), "HARVEST"))
                continue
            if kind == "PLANT":
                crop = tile.get("crop")
                age = day - int(tile.get("planted_day", day))
                # DAILY WATERING (kept after two measured rung-3 kills,
                # Sep 27): the champion skips age-1 waters on one-shot
                # crops (no bonus, no survival need) and reinvests ~143
                # unit-hours — but OUR greedy executor cannot convert the
                # freed labor: skip-only screened −1,107 (13 seeds, both
                # seats), skip+wheat-filler +450, both within ±2k noise →
                # reverted per predeclared rule.  Reopen only inside the
                # route scheduler where freed slots are explicitly re-spent.
                if not tile.get("watered_today"):
                    jobs.append(((x, y), "WATER"))
                if int(tile.get("fertilized_until_day", -1)) < day:
                    if (crop in _RP_ONGOING or
                            (crop in _RP_ONE_SHOT and age < _RP_ONE_SHOT[crop][0])):
                        jobs.append(((x, y), "FERT"))
                yu = int(tile.get("yield_units", 0))
                if yu > 0:
                    if crop in _RP_ONE_SHOT:
                        myd, cap = _RP_ONE_SHOT[crop]
                        if age >= myd or yu >= cap:
                            jobs.append(((x, y), "HARVEST"))
                    elif crop in _RP_ONGOING:
                        # standing yield caps at 4 — slow visits DESTROY
                        # production (measured: 79 str units banked vs 247)
                        if yu >= 1 and age >= _RP_ONGOING[crop]:
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

    # RUNG 2 — the demand pipeline: carrots against revealed PET_CAFE demand
    # (12/day each; FARMERS_MARKET 6), price-gated, plant day <= 26.
    # GRAIN ENGINE : r1's
    # -18,726 was mostly a grain hole — it planted carrots only, BOUGHT 209
    # feed wheat and sold zero.  The farm must feed itself: one standing
    # wheat tile ~ one animal-day of feed (~5u per 5-day cycle), plus sale
    # tiles into revealed wheat demand.
    day = step // 24
    if st.get("plant_day") != day:
        st["plant_day"] = day
        st["planted_n"] = 0
        st["planted_w"] = 0
    shops = observation["town"].get("unlocked_shops", [])
    p_c = int(prices.get("CARROT", 0))
    p_w = int(prices.get("WHEAT", 0))
    n_animals = sum(1 for row in farm["tiles"] for t in row
                    if isinstance(t, dict) and "animal" in t)
    whe_standing = sum(1 for row in farm["tiles"] for t in row
                       if isinstance(t, dict) and t.get("crop") == "WHEAT")
    if hour == 12:
        st["crew_prev"] = n_units - 1
    car_target = whe_target = 0
    if day <= 26 and hour <= 20:
        if _RP_USE_HEAD:
            # THE HEAD sets the quotas (closed-loop test of the distilled
            # crop-mix model); hand heuristics keep only safety floors.
            if st.get("head_day") != day:
                st["head_day"] = day
                try:
                    w3, c3 = _rp_head_targets(observation, seat,
                                              st.get("crew_prev", 10))
                except Exception:
                    w3, c3 = 0.0, 0.0
                    _RP_REPORT["rp_errors"] += 1
                st["head_w"], st["head_c"] = w3, c3
            car_target = max(0, min(16, int(round(st["head_c"] / 3.0))))
            whe_target = max(0, min(8, int(round(st["head_w"] / 3.0))))
            if p_c < 20:
                car_target = 0
        else:
            # v5 hand quotas (the tuned incumbent)
            if p_c >= 30:
                car_target = min(16, 4 * shops.count("PET_CAFE")
                                 + 2 * shops.count("FARMERS_MARKET"))
            want_standing = n_animals if day <= 24 else 0
            whe_buyers = sum(1 for s in shops if s in _RP_WHE_SHOPS)
            # rung-3b wheat filler (buyers>=1 & p_w>=15 → up to 12 sale
            # tiles, glut-guarded) tested Sep 27: 13-seed both-seat screen
            # mean +450 SE ~2,000 = WASH (predeclared rule) — reverted to
            # the v5 quota; the filler design is killed, not the lane.
            if p_w >= 22 and whe_buyers >= 2 and day <= 24:
                want_standing += min(6, 2 * whe_buyers)
            whe_target = max(0, min(8, want_standing - whe_standing))
        # feed never depends on a model: burn floor when stock is thin
        if (day <= 24 and int(priv["shed"].get("WHEAT", 0)) < n_animals
                and whe_standing + whe_target < n_animals):
            whe_target = max(whe_target, min(8, n_animals - whe_standing))

        # RUNG-3 SCHEDULER ATTEMPTS (Sep 27, both REVERTED — see
        # docs/BUILD_A_PLAN.md): (v1) feasibility-only ledger admission
        # measured −26k mean (refused $50 carrots to keep watering junk);
        # (v1b) value-per-action allocator with deliberate shedding
        # measured −48k mean — its hour-0 daily lock missed the HOURLY
        # carrot-price windows v5's quota check catches (0 carrot births
        # on the fixture), and crude keep-values abandoned young wheat.
        # The rung needs cycle templates with reserved routes and exact
        # bookkeeping (review §6), built fresh — not scalar heuristics.
    plant_target = car_target + whe_target
    plant_quota = max(0, plant_target - st["planted_n"] - st["planted_w"])
    seeds_free = int(priv["seeds"].get("CARROT", 0))
    seeds_w_free = int(priv["seeds"].get("WHEAT", 0))
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

    # DAY-29 VALUED CLOSURE (rung 2): feeding/caring/fertilizing pay out
    # only AFTER the final acting step — zero salvage value on the last
    # day.  HARVEST and COLLECT convert to cash, and so does WATER on a
    # RIPE one-shot tile: the in-window water bonus (+1 yield, engine
    # :440-443) is banked by the same-day harvest — dropping those waters
    # measured −3.8k/−7.3k on the all-PET challenges.  The hire calculation
    # above still sees the full job list ( probe 1's crew-sizing bug);
    # stranding is handled by the departure deadline + idle sweep below.
    if day == 29:
        keep_jobs = []
        for j in jobs:
            if j[1] in ("HARVEST", "COLLECT"):
                keep_jobs.append(j)
            elif j[1] == "WATER":
                t_ = farm["tiles"][j[0][1]][j[0][0]]
                if isinstance(t_, dict):
                    cr_ = t_.get("crop")
                    ag_ = day - int(t_.get("planted_day", day))
                    if cr_ in _RP_ONE_SHOT and ag_ >= _RP_ONE_SHOT[cr_][0]:
                        keep_jobs.append(j)
        jobs = keep_jobs
        feed_jobs = []

    # market housekeeping (orders process IN LIST ORDER, so sells free shed
    # room before buys — engine :667 refuses BUY_PRODUCT into a full shed).
    # RUNG 2 : sell orders are now built at the
    # END of the planner from the PROJECTED shed (unit actions execute
    # before market orders, so this turn's PLACE deposits are sellable same
    # turn) and PREPENDED so sells still precede buys.
    shed_total = sum(int(v) for v in priv["shed"].values())
    sell_now = (hour == 1 or hour >= 18 or day == 29 or shed_total > 60
                or int(priv["shed"].get("CARROT", 0)) >= 8)
    # feed: EMERGENCY buys only (grain engine grows the rest — Exp 156);
    # none on day 29 — feeding has no salvage value on the last day
    if hour in (1, 13) and day < 29:
        need_today = n_animals + 1
        have = shed_wheat + sum(carried_wheat)
        if have < need_today and len(market) < 10:
            deficit = need_today - have
            if float(farm.get("money", 0)) >= 300 + 45 * deficit:
                market.append(["BUY_PRODUCT", "WHEAT", int(deficit)])
                _RP_REPORT["rp_emergency_wheat"] += int(deficit)
        # seeds for tomorrow's pipeline (atomic-PLANT headroom)
        if car_target > 0 and len(market) < 10:
            want_seeds = 2 * car_target - seeds_free
            if want_seeds > 0 and float(farm.get("money", 0)) >= 800 + 20 * want_seeds:
                market.append(["BUY_SEED", "CARROT", int(want_seeds)])
        if whe_target > 0 and len(market) < 10:
            want_w = 2 * whe_target - seeds_w_free
            if want_w > 0 and float(farm.get("money", 0)) >= 500 + 10 * want_w:
                market.append(["BUY_SEED", "WHEAT", int(want_w)])
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

    # RUNG 2 : per-unit day-29 departure deadline replaces the
    # blanket hour-14 recall.  Final acting step is 718 (= hour 22): a unit
    # must arrive AND spend one PLACE per cargo type by then.  Near units
    # keep harvesting hours longer; far heavy units leave earlier instead of
    # stranding goods.  One hour of safety buffer.
    must_leave = set()
    if day == 29:
        for i, pos in enumerate(positions):
            inv_i = invs[i] if i < len(invs) else {}
            n_types = sum(1 for v in inv_i.values() if int(v or 0) > 0)
            if not n_types:
                continue
            dist = min(abs(a[0] - pos[0]) + abs(a[1] - pos[1])
                       for a in _RP_ACCESS)
            if hour >= 22 - dist - n_types:
                must_leave.add(i)

    def _unfed_at(p):
        t_ = farm["tiles"][p[1]][p[0]]
        return int(t_.get("consecutive_unfed", 0)) if isinstance(t_, dict) else 0

    def _unwatered_at(p):
        t_ = farm["tiles"][p[1]][p[0]]
        return int(t_.get("consecutive_unwatered", 0)) if isinstance(t_, dict) else 0

    # pass 1: jobs on the tile we stand on
    for i, pos in enumerate(positions):
        if i in must_leave:
            continue           # its remaining hours belong to the shed run
        here = [j for j in jobs if j[0] == pos and j not in claimed]
        here.sort(key=lambda j: _RP_TIER[j[1]])
        acted = False
        for j in here:
            kind = j[1]
            # RUNG 1 : a wheat carrier must not do on-tile chores
            # while an animal elsewhere is on death row (unfed >= 1 escapes
            # at midnight, engine :817-819).  7709 forensic: u6 stood one
            # tile from the dying cow doing CARE/COLLECT for two hours.
            if (day < 29 and kind in ("CARE", "COLLECT", "FERT")
                    and carried_wheat[i] > 0
                    and any(j2 not in claimed and j2[0] != pos
                            and _unfed_at(j2[0]) >= 1 for j2 in feed_jobs)):
                continue
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

    # planter roster decided early: survival dispatch below may conscript a
    # planter only for a death-row feed (unfed >= 1)
    n_planters = 0
    if plant_target > 0 and n_units >= 3:
        n_planters = max(0, min(3, -(-plant_target // 6), n_units - 2))
    planter_ix = set(range(n_units - n_planters, n_units))

    # RUNG-1 SURVIVAL DISPATCH : the 7709 cow
    # died because evening delivery (hour >= 19) walked wheat carriers home
    # first — u4 was 4 steps away with 5 hours left and unloaded fertilizer
    # instead.  Feeding OUTRANKS delivery — but only when the day is running
    # out: all-day dispatch measured −9,726 on pinned 7709 s0 (labor drained
    # from watering/harvest).  Mornings stay organic (v5 fed those fine);
    # from hour 15 route wheat carriers to open feeds, death-row (unfed>=1)
    # tiles any hour and they alone may conscript a planter.
    if day < 29:
        for j in sorted((j for j in feed_jobs if j not in claimed),
                        key=lambda j: -_unfed_at(j[0])):
            urgent = _unfed_at(j[0]) >= 1
            if not urgent and hour < 15:
                continue
            cand = [i for i in range(n_units)
                    if units[i] == ["PASS"] and carried_wheat[i] > 0
                    and (urgent or i not in planter_ix)]
            if not cand:
                continue
            i = min(cand, key=lambda k: abs(j[0][0] - positions[k][0])
                    + abs(j[0][1] - positions[k][1]))
            claimed.add(j)
            units[i] = _rp_step_toward(positions[i], j[0])
            carried_wheat[i] -= 1      # earmarked for this animal
            _RP_REPORT["rp_survival_moves"] += 1

    # DYING-CROP DISPATCH : a tile on its
    # second dry day weeds at midnight.  7427 anatomy: 45 deaths/game, zero
    # seed-day misses — established plants starved of visits by nearest-job
    # churn and evening delivery.  ⚠ UNCAPPED dispatch measured −4,149 mean
    # margin and MORE deaths (walkers drained routine service, creating
    # tomorrow's dying tiles).  Cap: 3 rescue walkers, nearest pairs, only
    # when they can physically arrive before midnight.
    if day < 29 and hour >= 12:
        dying = [j for j in jobs if j[1] == "WATER" and j not in claimed
                 and _unwatered_at(j[0]) >= 1]
        for _ in range(min(3, len(dying))):
            best = None
            for j in dying:
                if j in claimed:
                    continue
                for i in range(n_units):
                    if units[i] != ["PASS"] or i in planter_ix:
                        continue
                    dd = (abs(j[0][0] - positions[i][0])
                          + abs(j[0][1] - positions[i][1]))
                    if dd <= 23 - hour and (best is None or dd < best[0]):
                        best = (dd, i, j)
            if best is None:
                break
            _, i, j = best
            claimed.add(j)
            units[i] = _rp_step_toward(positions[i], j[0])
            _RP_REPORT["rp_survival_waters"] += 1

    # DELIVERY : harvested goods are worth NOTHING carried — the
    # shed is the only sellable stock, and the game ends with no midnight
    # deposit before scoring (engine: final acting step 718).  Every evening
    # cargo goes home; on day 29 everything goes home from hour 14.
    # r1's audited leaks: 495 carrots harvested / 449 sold, 111 wool / 103,
    # 72 melons / 61.  PLACE is capacity-capped and never destroys (:394).
    deliver_all = day == 29
    if hour >= 19 or deliver_all:
        for i, pos in enumerate(positions):
            if units[i] != ["PASS"]:
                continue
            if deliver_all and i not in must_leave:
                continue       # day 29: pre-deadline units keep working
            inv_i = invs[i] if i < len(invs) else {}
            cargo = {k: int(v) for k, v in inv_i.items()
                     if int(v or 0) > 0 and (deliver_all or k != "WHEAT")}
            if not cargo:
                continue
            if pos in _RP_ACCESS:
                item = max(cargo, key=lambda k: cargo[k] * int(prices.get(k, 1)))
                do(i, ["PLACE", item, cargo[item]])
                _RP_REPORT["rp_delivered"] += cargo[item]
            else:
                tgt = min(_RP_ACCESS, key=lambda a: abs(a[0] - pos[0])
                          + abs(a[1] - pos[1]))
                units[i] = _rp_step_toward(pos, tgt)

    # PLANTER ROLES: the last P units do nothing but plant and give their
    # own plant its same-day water (nearest-job greedy starves planting —
    # measured: 3,608/4,019 plant jobs unassigned on seed 7456).
    # (planter_ix computed above, before the survival dispatch)
    taken_empties = set()
    for i in sorted(planter_ix):
        if units[i] != ["PASS"]:
            continue
        pos = positions[i]
        tile = farm["tiles"][pos[1]][pos[0]]
        planned_c = sum(1 for c in units if c[:2] == ["PLANT", "CARROT"])
        planned_w = sum(1 for c in units if c[:2] == ["PLANT", "WHEAT"])
        if (tile is None
                and st["planted_n"] + st["planted_w"] < plant_target
                and pos in [tuple(e) for e in empties]):
            # wheat first (the feed engine is survival), then demand carrots
            if st["planted_w"] < whe_target and seeds_w_free - planned_w >= 1:
                do(i, ["PLANT", "WHEAT"])
                st["planted_w"] += 1
                _RP_REPORT["rp_wheat_plants"] += 1
            elif st["planted_n"] < car_target and seeds_free - planned_c >= 1:
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
        if st["planted_n"] + st["planted_w"] < plant_target:
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

    # day-29 second delivery sweep (rung 2): a unit pass 2 left IDLE with
    # cargo heads home now — deposits must trickle in all day because the
    # carrot sell cap is 12/turn; hoarding until the deadline measured −235
    # mean margin (late dump can't clear before the final step)
    if day == 29:
        for i, pos in enumerate(positions):
            if units[i] != ["PASS"]:
                continue
            inv_i = invs[i] if i < len(invs) else {}
            cargo = {k: int(v) for k, v in inv_i.items() if int(v or 0) > 0}
            if not cargo:
                continue
            if pos in _RP_ACCESS:
                item = max(cargo, key=lambda k: cargo[k] * int(prices.get(k, 1)))
                do(i, ["PLACE", item, cargo[item]])
                _RP_REPORT["rp_delivered"] += cargo[item]
            else:
                tgt = min(_RP_ACCESS, key=lambda a: abs(a[0] - pos[0])
                          + abs(a[1] - pos[1]))
                units[i] = _rp_step_toward(pos, tgt)

    # SELL from the PROJECTED shed (rung 2): pre-action shed + this turn's
    # PLACE deposits.  The old loop read the stale shed, so the last
    # delivery of the day was never sold — on day 29 that stranded value.
    sells = []
    if hour >= 1 and sell_now:
        proj = {k: int(v) for k, v in priv["shed"].items()}
        for c in units:
            if isinstance(c, list) and len(c) > 2 and c[0] == "PLACE":
                proj[c[1]] = proj.get(c[1], 0) + int(c[2])
        # wheat above the feed reserve is a SALE crop (the grain engine's
        # whole point); on day 29 the reserve is worthless — sell it all
        reserve_w = 2 * n_animals + 4 if day < 29 else 0
        for item, q in sorted(proj.items(),
                              key=lambda kv: -int(prices.get(kv[0], 0))):
            if int(q) <= 0 or item in ("GOOSE", "COW", "SHEEP"):
                continue
            # $1 floor sells DO execute (engine :654): take them on day 29
            # when the alternative is $0; skip mid-game (price may recover)
            if int(prices.get(item, 0)) < 2 and day < 29:
                continue
            # FERT SELL TIMING (rung 3c, market-only class): don't dump
            # fert the hour it lands — c23s times fert sales (~$8.6k vs
            # our ~$4.4k on the fixture).  Hold below $8 unless the game
            # is ending or the shed needs the room.
            if (item == "FERTILIZER" and day < 28 and shed_total <= 80
                    and int(prices.get(item, 0)) < 8):
                continue
            if len(sells) + len(market) >= 10:
                break
            n = int(q)
            if item == "WHEAT":
                n = max(0, n - reserve_w)
                if n <= 0:
                    continue
                _RP_REPORT["rp_wheat_sold"] += n
            elif item == "CARROT":
                n = min(n, 12)
            sells.append(["SELL", item, n])
            _RP_REPORT["rp_sell_units"] += n

    return {"farmer": units[0], "hands": units[1:], "market": sells + market}


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

import sys as _sys
_USE_HEAD = '--hand' not in _sys.argv
_R1_OUT = r'fork\r1_hand.py' if not _USE_HEAD else r'fork\r1_head.py'

for path, name, kind, body in (
        (_R1_OUT, 'R1 TAKEOVER', 'maintenance takeover', PLANNER),
        (r'fork\rc0.py', 'RC0 CONTROL', 'planting-suppression control', SUPPRESSOR)):
    body = body.replace('__HEAD_LIT__', repr(_HEAD_LIT))
    body = body.replace('__USE_HEAD__', repr(_USE_HEAD))
    out = SRC.rstrip('\n') + (COMMON % {'name': name, 'kind': kind}) + body + FOOTER
    ast.parse(out)
    open(path, 'w', encoding='utf-8', newline='\n').write(out)
    print(f'wrote {path} ({len(out):,} chars), syntax OK')
