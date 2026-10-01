"""
main.py — Kaggriculture agent.  ENTRY POINT (must be at archive root, must be named main.py).

STATUS: v3 — Phase 4: v2 (scheduler + 6 cows/2 sheep + CARE + fertilizer) + NE LAND +
diversified crops (melon 12 / wheat-as-feed 10 / strawberry 10 / carrot 12) + hands scale
with land.  A/B record: v3a beat v2 30-2 (93.8%).

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
TARGET_HANDS = 4         # A/B'd in Phase 2: 2<3<4, 6 loses by its own wage bill (1 quadrant)
HANDS_PER_EXTRA_QUADRANT = 2   # each new 25-tile quadrant brings ~30 more chores/day
LAND_MAX_QUADRANTS = 2   # v3a: NW + NE. SW/SE are separate A/Bs.
LAND_PRICES = [1000, 2000, 4000]   # engine LAND_PRICES (ENGINE_NOTES B.1); order NE->SW->SE
# (crop mix now lives in CROP_INFO caps + PLANT_ORDER + SEED_WANT below)
LIQUIDATE_FROM_DAY = 28  # unsold inventory is worth $0 at the end — sell everything late
SHED_FORCE_SELL = 80     # shed cap is 100 and overflow is DESTROYED at end-of-day drop
UNLOAD_AT = 8            # a unit carrying this many items runs them to the shed (sellable today)

# Livestock plan: sheep first (slowest payout -> place earliest, CARE stacks highest on it),
# cows are the meta-proven workhorse. 6 animals ring the shed on one quadrant.
ANIMAL_TARGETS = {"SHEEP": 2, "COW": 6, "GOOSE": 4}
# Sheep first (slowest payout, biggest CARE multiplier), then geese (first yield in 4 days,
# daily eggs into a glut-immune log-curve market), then cows.
BUY_PRIORITY = ["SHEEP", "GOOSE", "COW"]
ANIMAL_INFO = {
    "COW":   {"cost": 400, "structure": "PASTURE", "build": "BUILD_PASTURE", "first": 8, "interval": 2, "product": "MILK"},
    "SHEEP": {"cost": 500, "structure": "PASTURE", "build": "BUILD_PASTURE", "first": 6, "interval": 3, "product": "WOOL"},
    "GOOSE": {"cost": 300, "structure": "COOP",    "build": "BUILD_COOP",    "first": 4, "interval": 1, "product": "EGG"},
}
STRUCT_BUILD = {"PASTURE": "BUILD_PASTURE", "COOP": "BUILD_COOP"}
# Ring around the shed-access tile (4,4): FEED/CARE/HARVEST/COLLECT all happen standing ON
# the animal tile and the wheat lives at the shed, so clustering minimizes walking.
ANIMAL_SLOTS = [(3, 4), (4, 3), (3, 3), (2, 4), (4, 2), (2, 3), (3, 2), (2, 2),
                (1, 4), (4, 1), (1, 3), (3, 1)]
# Slot i hosts the structure for the i-th animal in expanded BUY_PRIORITY order:
# 8 pastures (2 sheep + 6 cows) on the inner ring, 4 coops (geese) on the outer.
SLOT_STRUCTURES = (["PASTURE"] * (ANIMAL_TARGETS["SHEEP"] + ANIMAL_TARGETS["COW"])
                   + ["COOP"] * ANIMAL_TARGETS["GOOSE"])
MONEY_RESERVE = 150      # keep enough cash for the day's wheat + seeds when buying animals

# (batch, min_price, liquidation_day). Wheat doubles as animal feed: a reserve is held back
# (see WHEAT_FEED_RESERVE_DAYS) and the min price 30 (> base 25) means surplus only sells
# into scarcity, never at a loss against our own feed needs.
SELL_RULES = {
    "MELON":      (6, 120, 28),
    "CARROT":     (10, 25, 28),
    "STRAWBERRY": (4, 100, 28),
    "MILK":       (3, 90, 28),
    "WOOL":       (3, 90, 28),
    "FERTILIZER": (5, 40, 28),
    "WHEAT":      (6, 30, 29),
    "EGG":        (4, 35, 28),   # log glut curve: even heavy selling barely moves the price
}
NEVER_FORCE_SELL = {"WHEAT"}

# cap = max concurrent plants (market- or purpose-bound, not space-bound).
# Window (0,-1) = "watering never adds instant yield" (ongoing crops bonus only via fertilizer).
CROP_INFO = {
    "MELON":      {"cost": 80,  "first": 10, "ready": 10, "last_plant": 19, "window": (6, 12), "cap": 12},
    "WHEAT":      {"cost": 10,  "first": 2,  "ready": 4,  "last_plant": 24, "window": (2, 4),  "cap": 12},
    "STRAWBERRY": {"cost": 100, "first": 10, "ready": 10, "last_plant": 17, "window": (0, -1), "cap": 10},
    "CARROT":     {"cost": 20,  "first": 2,  "ready": 3,  "last_plant": 26, "window": (2, 3),  "cap": 12},
}
# Planting priority when a tile opens up: melon (highest $/tile-day, tiny cap), wheat (feeds
# the herd — replaces market buys at scarcity prices), strawberry (biggest town demand:
# ~426/season median), carrot (fast filler, capped so we stop glutting our own market).
PLANT_ORDER = ["MELON", "WHEAT", "STRAWBERRY", "CARROT"]
SEED_WANT = {"MELON": 3, "WHEAT": 5, "STRAWBERRY": 3, "CARROT": 4}
WHEAT_FEED_RESERVE_DAYS = 2   # hold animals*this much wheat before selling any surplus

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
    crop_counts = {}
    empty_tiles = []
    n_feed = 0
    reserved = {ANIMAL_SLOTS[i]: SLOT_STRUCTURES[i]
                for i in range(min(len(ANIMAL_SLOTS), sum(ANIMAL_TARGETS.values())))}

    for y, row in enumerate(tiles):
        for x, t in enumerate(row):
            if t == "LOCKED":
                continue
            if t is None:
                if (x, y) in reserved:
                    # Animal slot without a structure yet: build it (free, 1 action).
                    if day < LAST_DAY:
                        tasks.append({"prio": P_BUILD, "x": x, "y": y,
                                      "op": [STRUCT_BUILD[reserved[(x, y)]]]})
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
                crop_counts[crop] = crop_counts.get(crop, 0) + 1

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

    # ---------------- planting: fill empty tiles by PLANT_ORDER, respecting caps --------
    # Caps are market-bound (melon/carrot glut their price) or purpose-bound (wheat = feed),
    # so extra land raises variety, not just volume. Capped by seeds actually held (the
    # PLANT collective-validation trap) so no unit ever walks to an unplantable tile.
    if day < LAST_DAY:
        budget = dict(seeds)
        planned = dict(crop_counts)
        for (x, y) in empty_tiles:
            crop = None
            for c in PLANT_ORDER:
                info = CROP_INFO[c]
                if (planned.get(c, 0) < info["cap"] and day <= info["last_plant"]
                        and budget.get(c, 0) > 0):
                    crop = c
                    break
            if crop is None:
                continue
            planned[crop] = planned.get(crop, 0) + 1
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

    # One animal-pickup per turn: an animal sits in the shed and a MATCHING empty
    # structure (pasture for cow/sheep, coop for goose) waits for it.
    empty_kinds = {
        t.get("kind")
        for row in tiles for t in row
        if isinstance(t, dict) and t.get("kind") in ("PASTURE", "COOP")
        and not t.get("animal")
    }
    if empty_kinds:
        carrying = any(any(sp in inv for sp in ANIMAL_INFO) for inv in inventories)
        if not carrying:
            for sp in BUY_PRIORITY:
                if shed.get(sp, 0) > 0 and ANIMAL_INFO[sp]["structure"] in empty_kinds:
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
        needed_kind = ANIMAL_INFO[species]["structure"]
        best, best_d = None, 10**9
        for y, row in enumerate(tiles):
            for x, t in enumerate(row):
                if isinstance(t, dict) and t.get("kind") == needed_kind and not t.get("animal"):
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
                   n_hands, tiles, n_quadrants):
    """Queue order: SELL (income), HIRE, wheat, animals, LAND, seeds. Engine cap: 10."""
    orders = []

    placed_animals = sum(
        1 for row in tiles for t in row
        if isinstance(t, dict) and t.get("animal") in ANIMAL_INFO
    )

    # HIREs first: with 7 sellable products the 10-order cap could starve hour-0 hiring,
    # and a lost hand costs a whole day of labor while a delayed sale costs one turn.
    hands_target = TARGET_HANDS + HANDS_PER_EXTRA_QUADRANT * (n_quadrants - 1)
    if hour == 0 and day < LAST_DAY:
        for _ in range(max(0, hands_target - n_hands - hires_today)):
            orders.append(["HIRE"])

    shed_total = sum(shed.values())
    for item, (batch, min_price, liq_day) in SELL_RULES.items():
        stock = shed.get(item, 0)
        if item == "WHEAT" and day < LAST_DAY:
            # Never sell the herd's next few days of feed.
            stock -= placed_animals * WHEAT_FEED_RESERVE_DAYS
        if stock <= 0:
            continue
        price = prices.get(item, 0)
        force = shed_total >= SHED_FORCE_SELL and item not in NEVER_FORCE_SELL
        if day >= liq_day or force or price >= min_price:
            orders.append(["SELL", item, min(batch, stock)])

    # Wheat feed top-up from the market only if growing hasn't covered it. Bought wheat
    # lands in the shed after this turn's unit actions, so buy ahead of need.
    if day <= LAST_TICK_DAY and placed_animals > 0:
        wheat_stock = shed.get("WHEAT", 0) + sum(inv.get("WHEAT", 0) for inv in inventories)
        want = placed_animals + 2
        wheat_price = max(1, prices.get("WHEAT", 25))
        if wheat_stock < want and money > MONEY_RESERVE:
            n = min(want - wheat_stock, int((money - MONEY_RESERVE) // wheat_price))
            if n > 0:
                orders.append(["BUY_PRODUCT", "WHEAT", n])
                money -= n * wheat_price

    # How many of each animal we own anywhere (placed + shed + carried) — used for both
    # the animal buys and the land trigger below.
    owned = {sp: shed.get(sp, 0) for sp in ANIMAL_INFO}
    for inv in inventories:
        for sp in ANIMAL_INFO:
            owned[sp] += inv.get(sp, 0)
    for row in tiles:
        for t in row:
            if isinstance(t, dict) and t.get("animal") in owned:
                owned[t["animal"]] += 1
    herd_complete = all(owned[sp] >= ANIMAL_TARGETS[sp] for sp in ANIMAL_TARGETS)

    # Animals: buy toward targets (sheep first), one per turn, money-gated.
    if day <= 20 and not herd_complete:  # placed after ~day 20 barely produces in time
        for sp in BUY_PRIORITY:
            cost = ANIMAL_INFO[sp]["cost"]
            if owned[sp] < ANIMAL_TARGETS[sp] and money >= cost + MONEY_RESERVE:
                orders.append(["BUY_ANIMAL", sp, 1])
                money -= cost
                break

    # Land: after the herd (animals out-earn bare land per dollar), buy the next quadrant.
    # NE is $1k for 25 tiles — pays back within days at our per-tile earnings. Keep a
    # cushion so the wheat/seed pipeline never starves (cash once dipped to $81 on day 5).
    if (n_quadrants < LAND_MAX_QUADRANTS and day <= 20 and herd_complete):
        land_cost = LAND_PRICES[n_quadrants - 1]
        if money >= land_cost + MONEY_RESERVE + 200:
            orders.append(["BUY_LAND"])
            money -= land_cost

    for crop in PLANT_ORDER:
        info = CROP_INFO[crop]
        if day > info["last_plant"]:
            continue
        want = SEED_WANT[crop]
        have = seeds.get(crop, 0)
        if have < want and money >= info["cost"]:
            n = min(want - have, int(money // info["cost"]))
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
                            me.get("hires_today", 0), len(me.get("hands", [])), tiles,
                            len(me.get("unlocked_quadrants", ["NW"])))

    if DEBUG:
        print(f"d{day} h{hour} units={len(units)} tasks={len(tasks)} market={market}")

    return {"farmer": actions[0], "hands": actions[1:], "market": market}
