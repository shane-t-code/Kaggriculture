"""
versions/v2a.py — Phase 3 candidate: v1 scheduler + ANIMALS (sheep/cows, CARE, fertilizer).

Everything from v1 (task list, greedy assignment, stickiness, 4 hands, melon-12 + carrot mix,
day-29 endgame) plus the livestock pipeline:

  BUY_ANIMAL (-> shed) -> BUILD_PASTURE (free, 1 action) -> PICKUP animal at shed -> carry ->
  PLACE -> daily FEED (1 wheat from the unit's own inventory) + CARE + HARVEST + COLLECT_FERTILIZER.

Engine facts this file leans on (verified, docs/ENGINE_NOTES.md B):
  * FEED consumes WHEAT from the acting unit's PERSONAL inventory, not the shed (B.3) —
    someone must PICKUP wheat before walking the animal circuit.
  * BUY_ANIMAL / BUY_PRODUCT deliver into the shed and fail if it is full (B.3).
  * fertilizer_available is set for every SURVIVING animal every end-of-day, fed or not;
    it does not accumulate — collect daily or lose $98/day (B.7 / A).
  * Animal production ticks at the end of day t = placed_day + first_yield - 1 + k*interval.
    The LAST refresh of the game is end of day 28 (B.4): feeding/caring only pays if the
    animal still has a tick <= 28.  CARE banked on day d pays on the first tick STRICTLY
    after d (production is checked before the day's care is banked, B.4).
  * An animal unfed 2 consecutive days escapes BEFORE producing or making fertilizer (B.4).
  * Structures are free (no money check in BUILD_COOP/BUILD_PASTURE, engine L493-503).
"""
from __future__ import annotations

DEBUG = False

# ----------------------------------------------------------------------------------
# Tunables
# ----------------------------------------------------------------------------------
TARGET_HANDS = 4         # A/B'd in Phase 2: 2<3<4, 6 loses by its own wage bill
MELON_CAP = 12           # town eats only 30 melons/season; price floors after ~158 net sold
FILLER = "CARROT"        # hinge price curve absorbs volume; best early cash flow
SEED_BUFFER = 3
LIQUIDATE_FROM_DAY = 28  # unsold inventory is worth $0 at the end — sell everything late
SHED_FORCE_SELL = 80     # shed cap is 100 and overflow is DESTROYED at end-of-day drop
UNLOAD_AT = 8            # a unit carrying this many items runs them to the shed (sellable today)

# Livestock plan: sheep first (slowest payout -> place earliest, CARE stacks highest on it),
# cows are the meta-proven workhorse. 6 animals ring the shed on one quadrant.
ANIMAL_TARGETS = {"SHEEP": 2, "COW": 6}
BUY_PRIORITY = ["SHEEP", "COW"]
ANIMAL_INFO = {
    "COW":   {"cost": 400, "build": "BUILD_PASTURE", "first": 8, "interval": 2, "product": "MILK"},
    "SHEEP": {"cost": 500, "build": "BUILD_PASTURE", "first": 6, "interval": 3, "product": "WOOL"},
}
# Ring around the shed-access tile (4,4): FEED/CARE/HARVEST/COLLECT all happen standing ON
# the animal tile and the wheat lives at the shed, so clustering minimizes walking.
ANIMAL_SLOTS = [(3, 4), (4, 3), (3, 3), (2, 4), (4, 2), (2, 3), (3, 2), (2, 2)]
MONEY_RESERVE = 150      # keep enough cash for the day's wheat + seeds when buying animals

# (batch, min_price, liquidation_day). Wheat is FEED (an input): min price 10**9 means it
# only ever sells during its own liquidation window (day 29, after the last feeding).
SELL_RULES = {
    "MELON":      (6, 120, 28),
    "CARROT":     (10, 25, 28),
    "MILK":       (3, 90, 28),
    "WOOL":       (3, 90, 28),
    "FERTILIZER": (5, 40, 28),
    "WHEAT":      (10, 10**9, 29),
}
NEVER_FORCE_SELL = {"WHEAT"}

CROP_INFO = {
    "MELON":  {"cost": 80, "first": 10, "ready": 10, "last_plant": 19, "window": (6, 12)},
    "CARROT": {"cost": 20, "first": 2,  "ready": 3,  "last_plant": 26, "window": (2, 3)},
}

SHED_TILE = (4, 4)
LAST_DAY = 29
LAST_TICK_DAY = 28       # the game's final end-of-day refresh (ENGINE_NOTES B.4)

# Task priorities (lower = more urgent)
P_SAVE = 0     # plant/animal that is lost tonight if ignored
P_FEED = 1
P_HARVEST = 1
P_CHAIN = 1    # supply-chain steps: PICKUP wheat/animal, PLACE animal
P_WATER = 2
P_CARE = 2
P_COLLECT = 3  # fertilizer: $98/day, but re-offered tomorrow if missed
P_PLANT = 3
P_BUILD = 3
P_UNLOAD = 3
P_DIG = 4


def _step_toward(fx, fy, tx, ty):
    if fx < tx:
        return "EAST"
    if fx > tx:
        return "WEST"
    if fy < ty:
        return "SOUTH"
    if fy > ty:
        return "NORTH"
    return None


def _next_tick_day(placed_day, first, interval, after_day):
    """First production tick day STRICTLY after `after_day`, or None if past day 28."""
    first_tick = placed_day + first - 1
    if first_tick > after_day:
        t = first_tick
    else:
        t = first_tick + interval * ((after_day - first_tick) // interval + 1)
    return t if t <= LAST_TICK_DAY else None


def _build_tasks(tiles, day, seeds):
    """Scan the farm -> the turn's task list. Returns (tasks, n_feed_needed)."""
    tasks = []
    melon_count = 0
    empty_tiles = []
    n_feed = 0
    reserved = set(ANIMAL_SLOTS[:sum(ANIMAL_TARGETS.values())])

    for y, row in enumerate(tiles):
        for x, t in enumerate(row):
            if t == "LOCKED":
                continue
            if t is None:
                if (x, y) in reserved:
                    # Animal slot without a structure yet: build it (free, 1 action).
                    if day < LAST_DAY:
                        tasks.append({"prio": P_BUILD, "x": x, "y": y, "op": ["BUILD_PASTURE"]})
                else:
                    empty_tiles.append((x, y))
                continue
            if not isinstance(t, dict):
                continue
            kind = t.get("kind")

            if kind == "WEED":
                if day < LAST_DAY:
                    tasks.append({"prio": P_DIG, "x": x, "y": y, "op": ["DIG"]})
                continue

            # ---------------- animals (any tile dict carrying an "animal" key) ----------
            if "animal" in t and t["animal"]:
                info = ANIMAL_INFO.get(t["animal"])
                if info is None:
                    continue
                placed = t.get("placed_day", 0)
                cu = t.get("consecutive_unfed", 0)

                if t.get("yield_units", 0) > 0:
                    tasks.append({"prio": P_HARVEST, "x": x, "y": y, "op": ["HARVEST"]})

                if t.get("fertilizer_available", False):
                    tasks.append({"prio": P_COLLECT, "x": x, "y": y,
                                  "op": ["COLLECT_FERTILIZER"]})

                if not t.get("fed_today", False) and day <= LAST_TICK_DAY:
                    # Feed only while it still pays: a tick today-or-later, or the animal
                    # would escape tonight and cut off the daily fertilizer stream.
                    tick_ahead = _next_tick_day(placed, info["first"], info["interval"], day - 1)
                    if tick_ahead is not None or cu >= 1:
                        n_feed += 1
                        tasks.append({"prio": P_SAVE if cu >= 1 else P_FEED, "x": x, "y": y,
                                      "op": ["FEED"], "require": "WHEAT"})

                if not t.get("cared_today", False):
                    # CARE banked on day d pays on the first tick AFTER d (must be <= 28).
                    if _next_tick_day(placed, info["first"], info["interval"], day) is not None:
                        tasks.append({"prio": P_CARE, "x": x, "y": y, "op": ["CARE"]})
                continue

            # Empty structure (no animal yet): nothing to do here; PLACE is handled by
            # the carrier override in _assign.
            if kind in ("COOP", "PASTURE"):
                continue

            # ---------------- plants (same rules as v1) --------------------------------
            if kind == "PLANT":
                crop = t.get("crop")
                info = CROP_INFO.get(crop)
                age = day - t.get("planted_day", day)
                dying = t.get("consecutive_unwatered", 0) >= 1 and not t.get("watered_today", False)
                if crop == "MELON":
                    melon_count += 1

                ready_age = info["ready"] if info else 10
                first_age = info["first"] if info else ready_age
                harvestable = t.get("yield_units", 0) > 0 and (
                    age >= ready_age or (day == LAST_DAY and age >= first_age)
                )
                if harvestable:
                    tasks.append({"prio": P_SAVE if dying else P_HARVEST, "x": x, "y": y,
                                  "op": ["HARVEST"]})
                    continue

                if not t.get("watered_today", False):
                    if day == LAST_DAY:
                        if info and info["window"][0] <= age <= info["window"][1]:
                            tasks.append({"prio": P_WATER, "x": x, "y": y, "op": ["WATER"]})
                    else:
                        tasks.append({"prio": P_SAVE if dying else P_WATER, "x": x, "y": y,
                                      "op": ["WATER"]})
                continue

    # ---------------- planting (unchanged from v1, minus reserved animal slots) --------
    if day < LAST_DAY:
        budget = dict(seeds)
        planned_melons = melon_count
        for (x, y) in empty_tiles:
            crop = None
            if (planned_melons < MELON_CAP and day <= CROP_INFO["MELON"]["last_plant"]
                    and budget.get("MELON", 0) > 0):
                crop = "MELON"
                planned_melons += 1
            elif (FILLER and day <= CROP_INFO[FILLER]["last_plant"]
                    and budget.get(FILLER, 0) > 0):
                crop = FILLER
            if crop is None:
                continue
            budget[crop] -= 1
            tasks.append({"prio": P_PLANT, "x": x, "y": y, "op": ["PLANT", crop]})

    return tasks, n_feed


def _supply_tasks(tasks, n_feed, units, inventories, shed, tiles, day):
    """Shed-side chain steps: PICKUP wheat for feeders, PICKUP a bought animal."""
    if day >= LAST_DAY:
        return

    carried_wheat = sum(inv.get("WHEAT", 0) for inv in inventories)
    if n_feed > carried_wheat and shed.get("WHEAT", 0) > 0:
        n = min(n_feed - carried_wheat + 2, shed["WHEAT"])
        tasks.append({"prio": P_CHAIN, "x": SHED_TILE[0], "y": SHED_TILE[1],
                      "op": ["PICKUP", "WHEAT", n]})

    # One animal-pickup per turn: an animal sits in the shed and an empty structure waits.
    empty_pasture = any(
        isinstance(t, dict) and t.get("kind") == "PASTURE" and not t.get("animal")
        for row in tiles for t in row
    )
    if empty_pasture:
        carrying = any(any(sp in inv for sp in ANIMAL_INFO) for inv in inventories)
        if not carrying:
            for sp in BUY_PRIORITY:
                if shed.get(sp, 0) > 0:
                    tasks.append({"prio": P_CHAIN, "x": SHED_TILE[0], "y": SHED_TILE[1],
                                  "op": ["PICKUP", sp, 1]})
                    break


def _assign(units, tasks, inventories, tiles, day, hour):
    """{unit_index: task}. Carrier overrides, then stickiness, then greedy (prio, dist)."""
    assignment = {}
    taken = [False] * len(tasks)

    def inv_of(ui):
        return inventories[ui] if ui < len(inventories) else {}

    # Override 1: a unit carrying an animal delivers it to the nearest empty pasture.
    for ui, (ux, uy) in enumerate(units):
        inv = inv_of(ui)
        species = next((sp for sp in ANIMAL_INFO if inv.get(sp, 0) > 0), None)
        if species is None:
            continue
        best, best_d = None, 10**9
        for y, row in enumerate(tiles):
            for x, t in enumerate(row):
                if isinstance(t, dict) and t.get("kind") == "PASTURE" and not t.get("animal"):
                    d = abs(x - ux) + abs(y - uy)
                    if d < best_d:
                        best, best_d = (x, y), d
        if best:
            assignment[ui] = {"prio": P_CHAIN, "x": best[0], "y": best[1],
                              "op": ["PLACE", species]}

    # Override 2 (day 29 only): loaded units must reach the shed and DROP by hour 22 or
    # their cargo is worth $0 (no end-of-day drop ever runs again). Leave just in time.
    if day == LAST_DAY:
        for ui, (ux, uy) in enumerate(units):
            if ui in assignment:
                continue
            inv = inv_of(ui)
            load = sum(inv.values())
            if load <= 0:
                continue
            dist = abs(ux - SHED_TILE[0]) + abs(uy - SHED_TILE[1])
            if hour >= 21 - dist:  # 1-turn safety margin before the hour-22 cutoff
                assignment[ui] = {"prio": P_SAVE, "x": SHED_TILE[0], "y": SHED_TILE[1],
                                  "op": ["DROP"]}

    def eligible(ui, task):
        req = task.get("require")
        return req is None or inv_of(ui).get(req, 0) > 0

    # Stickiness: finish the tile you stand on.
    for ui, (ux, uy) in enumerate(units):
        if ui in assignment:
            continue
        best = None
        for ti, task in enumerate(tasks):
            if taken[ti] or task["x"] != ux or task["y"] != uy or not eligible(ui, task):
                continue
            if best is None or task["prio"] < tasks[best]["prio"]:
                best = ti
        if best is not None:
            assignment[ui] = tasks[best]
            taken[best] = True

    # Global greedy: most urgent first, nearest eligible unit wins, stable tie-break.
    pairs = []
    for ti, task in enumerate(tasks):
        if taken[ti]:
            continue
        for ui, (ux, uy) in enumerate(units):
            if ui in assignment or not eligible(ui, task):
                continue
            d = abs(task["x"] - ux) + abs(task["y"] - uy)
            pairs.append((task["prio"], d, task["y"] * 16 + task["x"], ui, ti))
    pairs.sort()
    for prio, d, _, ui, ti in pairs:
        if ui in assignment or taken[ti]:
            continue
        assignment[ui] = tasks[ti]
        taken[ti] = True

    # Idle-but-loaded units bank their cargo (sellable today instead of tomorrow),
    # but never while still carrying feed wheat for pending FEED tasks.
    feeds_pending = any(t.get("op", [None])[0] == "FEED" for ti, t in enumerate(tasks)
                        if not taken[ti])
    for ui, (ux, uy) in enumerate(units):
        if ui in assignment:
            continue
        inv = inv_of(ui)
        if sum(inv.values()) >= UNLOAD_AT and not (feeds_pending and inv.get("WHEAT", 0) > 0):
            assignment[ui] = {"prio": P_UNLOAD, "x": SHED_TILE[0], "y": SHED_TILE[1],
                              "op": ["DROP"]}

    return assignment


def _unit_action(unit_pos, task):
    if task is None:
        return ["PASS"]
    ux, uy = unit_pos
    if (ux, uy) == (task["x"], task["y"]):
        return list(task["op"])
    mv = _step_toward(ux, uy, task["x"], task["y"])
    return [mv] if mv else ["PASS"]


def _market_orders(day, hour, money, seeds, shed, inventories, prices, hires_today,
                   n_hands, tiles):
    """Queue order: SELL (income first), HIRE, wheat, animals, seeds. Engine cap: 10."""
    orders = []

    shed_total = sum(shed.values())
    for item, (batch, min_price, liq_day) in SELL_RULES.items():
        stock = shed.get(item, 0)
        if stock <= 0:
            continue
        price = prices.get(item, 0)
        force = shed_total >= SHED_FORCE_SELL and item not in NEVER_FORCE_SELL
        if day >= liq_day or force or price >= min_price:
            orders.append(["SELL", item, min(batch, stock)])

    if hour == 0 and day < LAST_DAY:
        for _ in range(max(0, TARGET_HANDS - n_hands - hires_today)):
            orders.append(["HIRE"])

    # Wheat feed: keep (shed + carried) >= animals placed, +2 buffer. Bought wheat lands
    # in the shed after this turn's unit actions, so buy ahead of need.
    placed_animals = sum(
        1 for row in tiles for t in row
        if isinstance(t, dict) and t.get("animal") in ANIMAL_INFO
    )
    if day <= LAST_TICK_DAY and placed_animals > 0:
        wheat_stock = shed.get("WHEAT", 0) + sum(inv.get("WHEAT", 0) for inv in inventories)
        want = placed_animals + 2
        wheat_price = max(1, prices.get("WHEAT", 25))
        if wheat_stock < want and money > MONEY_RESERVE:
            n = min(want - wheat_stock, int((money - MONEY_RESERVE) // wheat_price))
            if n > 0:
                orders.append(["BUY_PRODUCT", "WHEAT", n])
                money -= n * wheat_price

    # Animals: buy toward targets (sheep first), one per turn, money-gated.
    if day <= 20:  # a cow placed after ~day 20 barely produces before the season ends
        owned = {sp: shed.get(sp, 0) for sp in ANIMAL_INFO}
        for inv in inventories:
            for sp in ANIMAL_INFO:
                owned[sp] += inv.get(sp, 0)
        for row in tiles:
            for t in row:
                if isinstance(t, dict) and t.get("animal") in owned:
                    owned[t["animal"]] += 1
        for sp in BUY_PRIORITY:
            cost = ANIMAL_INFO[sp]["cost"]
            if owned[sp] < ANIMAL_TARGETS[sp] and money >= cost + MONEY_RESERVE:
                orders.append(["BUY_ANIMAL", sp, 1])
                money -= cost
                break

    active = ["MELON"] + ([FILLER] if FILLER else [])
    for crop in active:
        info = CROP_INFO[crop]
        if day > info["last_plant"]:
            continue
        have = seeds.get(crop, 0)
        if have < SEED_BUFFER and money >= info["cost"]:
            n = min(SEED_BUFFER - have, int(money // info["cost"]))
            if n > 0:
                orders.append(["BUY_SEED", crop, n])
                money -= n * info["cost"]

    return orders[:10]


def agent(obs):
    player = obs["player"]
    me = obs["farms"][player]
    private = obs["private"]

    tiles = me["tiles"]
    day = obs["day"]
    hour = obs["hour"]
    money = me["money"]
    seeds = private.get("seeds", {}) or {}
    shed = private.get("shed", {}) or {}
    inventories = private.get("inventories", []) or []
    prices = (obs.get("market", {}) or {}).get("prices", {}) or {}

    units = [tuple(me["farmer"])] + [tuple(h) for h in me.get("hands", [])]

    tasks, n_feed = _build_tasks(tiles, day, seeds)
    _supply_tasks(tasks, n_feed, units, inventories, shed, tiles, day)
    assignment = _assign(units, tasks, inventories, tiles, day, hour)

    actions = [_unit_action(units[ui], assignment.get(ui)) for ui in range(len(units))]

    # PLANT collective-validation guard (unchanged from v1).
    plant_counts = {}
    for i, a in enumerate(actions):
        if a and a[0] == "PLANT":
            crop = a[1]
            plant_counts[crop] = plant_counts.get(crop, 0) + 1
            if plant_counts[crop] > seeds.get(crop, 0):
                actions[i] = ["PASS"]

    market = _market_orders(day, hour, money, seeds, shed, inventories, prices,
                            me.get("hires_today", 0), len(me.get("hands", [])), tiles)

    if DEBUG:
        print(f"d{day} h{hour} units={len(units)} tasks={len(tasks)} market={market}")

    return {"farmer": actions[0], "hands": actions[1:], "market": market}
