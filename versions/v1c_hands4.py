"""
main.py — Kaggriculture agent.  ENTRY POINT (must be at archive root, must be named main.py).

STATUS: v1 — Phase 2: multi-unit task scheduler + daily hiring.

The three ideas (all measured by competitors):
  1. Rebuild a TASK LIST every turn: every tile that needs WATER / HARVEST / DIG / PLANT
     becomes a task with a priority ("a plant that missed watering yesterday dies tonight"
     outranks everything).
  2. ASSIGN UNITS TO TASKS, not tasks to units: greedy by (priority, distance), and no two
     units are ever sent to the same tile.  Uncoordinated units chasing the same "best" tile
     is the 83%-of-turns-spent-walking failure mode.
  3. STICKINESS: a unit standing on a tile with work does that work before moving anywhere.
     Walking is the binding constraint, not labor.

Engine facts baked in (verified in docs/ENGINE_NOTES.md section B, with line numbers):
  * Hands cost fib(n) per day (1,1,2,3,5...) and reset daily — 2 hands = $2/day. (B.1)
  * PLANT is validated COLLECTIVELY per crop per turn: over-requesting converts ALL of that
    crop's PLANT requests to PASS.  We hard-cap issued PLANTs at seeds held. (B.3)
  * Seeds bought this turn arrive AFTER unit actions run — buy at least one turn ahead. (B.3)
  * Day 29 has NO end-of-day: survival-watering and planting are worthless, and anything
    harvested on day 29 must be hand-carried to the shed or it can never be sold. (B.4)
  * Sales at the $1 floor don't add to market inventory; shed overflow past 100 is DESTROYED
    at end-of-day drop — force-sell before that happens. (B.3/B.7)
  * The last actionable turn is step 718 = day 29 hour 22. (B.4)
"""
from __future__ import annotations

DEBUG = False

# ----------------------------------------------------------------------------------
# Tunables — the things worth A/B testing
# ----------------------------------------------------------------------------------
TARGET_HANDS = 4         # hands hired each morning (fib cost: 4 hands = $7/day)
MELON_CAP = 12           # cap concurrent melons: town eats only 30/season and the price
                         # floors after ~158 net units sold — volume past that is wasted
FILLER = "CARROT"        # remaining tiles grow carrots: 3-day cycle, hinge price curve
                         # (barely drops before ~900 net units), best early cash flow
SEED_BUFFER = 3          # seeds to keep on hand per active crop (buys happen 1 turn ahead)
LIQUIDATE_FROM_DAY = 28  # from this day sell stock every turn, ignoring min-price floors
SHED_FORCE_SELL = 80     # shed count >= this -> sell regardless of price (overflow is destroyed)

# (batch size, min price) per crop — sell small: premium goods crash to $1 on gluts
SELL_RULES = {"MELON": (6, 120), "CARROT": (10, 25)}

# Per-crop engine constants (verified against CROPS + watering logic, ENGINE_NOTES B.1/B.3):
#   first      = first day-age HARVEST is allowed
#   ready      = the age we actually want to harvest at (max yield reached)
#   last_plant = latest planting day that can still reach `first` by day 29
#   window     = (start_age, end_age) where WATER adds +1 yield immediately
CROP_INFO = {
    "MELON":  {"cost": 80, "first": 10, "ready": 10, "last_plant": 19, "window": (6, 12)},
    "CARROT": {"cost": 20, "first": 2,  "ready": 3,  "last_plant": 26, "window": (2, 3)},
}

SHED_TILE = (4, 4)       # NW shed-access tile — always unlocked, reachable all game
LAST_DAY = 29

# Task priorities (lower = more urgent)
P_SAVE = 0     # water/harvest a plant that turns to weed tonight if ignored
P_HARVEST = 1  # ready produce (also frees the tile)
P_SHED_RUN = 1 # day-29 only: carry harvested goods to the shed so they can be sold
P_WATER = 2    # normal daily watering (bonus window + keeps the weed clock at 0)
P_PLANT = 3    # empty tile + seed in hand (an unplanted tile is a lost tile-day)
P_DIG = 4      # weeds (only cost the tile, no deadline)


def _step_toward(fx, fy, tx, ty):
    """One greedy step (locked tiles are passable, so straight-line walking is optimal)."""
    if fx < tx:
        return "EAST"
    if fx > tx:
        return "WEST"
    if fy < ty:
        return "SOUTH"
    if fy > ty:
        return "NORTH"
    return None


def _build_tasks(tiles, day, seeds):
    """Scan the farm and produce the turn's task list: dicts of (prio, x, y, op)."""
    tasks = []
    melon_count = 0
    empty_tiles = []

    for y, row in enumerate(tiles):
        for x, t in enumerate(row):
            if t == "LOCKED":
                continue
            if t is None:
                empty_tiles.append((x, y))
                continue
            if not isinstance(t, dict):
                continue
            kind = t.get("kind")

            if kind == "WEED":
                if day < LAST_DAY:  # a weed dug on day 29 frees a tile nobody will use
                    tasks.append({"prio": P_DIG, "x": x, "y": y, "op": ["DIG"]})
                continue

            if kind == "PLANT":
                crop = t.get("crop")
                info = CROP_INFO.get(crop)
                age = day - t.get("planted_day", day)
                dying = t.get("consecutive_unwatered", 0) >= 1 and not t.get("watered_today", False)
                if crop == "MELON":
                    melon_count += 1

                # Harvest: at/after the max-yield age, or on the final day at any legal age.
                ready_age = info["ready"] if info else 10
                first_age = info["first"] if info else ready_age
                harvestable = t.get("yield_units", 0) > 0 and (
                    age >= ready_age or (day == LAST_DAY and age >= first_age)
                )
                if harvestable:
                    # Harvesting also removes the plant, so it doubles as the save action.
                    tasks.append({"prio": P_SAVE if dying else P_HARVEST, "x": x, "y": y,
                                  "op": ["HARVEST"]})
                    continue

                if not t.get("watered_today", False):
                    if day == LAST_DAY:
                        # No end-of-day ever runs again: water ONLY if it adds yield right now.
                        if info and info["window"][0] <= age <= info["window"][1]:
                            tasks.append({"prio": P_WATER, "x": x, "y": y, "op": ["WATER"]})
                    else:
                        tasks.append({"prio": P_SAVE if dying else P_WATER, "x": x, "y": y,
                                      "op": ["WATER"]})
                continue

    # Planting: pick a crop per empty tile, capped by seeds actually held right now
    # (a unit walking to a tile with no seed available is a wasted trip, and issuing more
    # PLANTs than seeds this turn would void ALL of them — the collective-validation trap).
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

    return tasks


def _assign(units, tasks, inventories, day):
    """Return {unit_index: task}. Stickiness first, then global greedy by (prio, distance)."""
    assignment = {}
    taken = [False] * len(tasks)

    # Day-29 shed runs: any unit carrying produce must reach the shed or the goods are lost.
    if day == LAST_DAY:
        for ui, (ux, uy) in enumerate(units):
            inv = inventories[ui] if ui < len(inventories) else {}
            if inv and sum(inv.values()) > 0:
                assignment[ui] = {"prio": P_SHED_RUN, "x": SHED_TILE[0], "y": SHED_TILE[1],
                                  "op": ["DROP"]}

    # Stickiness: work on the tile you stand on beats walking anywhere.
    for ui, (ux, uy) in enumerate(units):
        if ui in assignment:
            continue
        best = None
        for ti, task in enumerate(tasks):
            if taken[ti] or task["x"] != ux or task["y"] != uy:
                continue
            if best is None or task["prio"] < tasks[best]["prio"]:
                best = ti
        if best is not None:
            assignment[ui] = tasks[best]
            taken[best] = True

    # Global greedy: most urgent task first, closest free unit wins; ties broken
    # deterministically (tile order) so assignments are stable turn-to-turn (anti-thrash).
    pairs = []
    for ti, task in enumerate(tasks):
        if taken[ti]:
            continue
        for ui, (ux, uy) in enumerate(units):
            if ui in assignment:
                continue
            d = abs(task["x"] - ux) + abs(task["y"] - uy)
            pairs.append((task["prio"], d, task["y"] * 16 + task["x"], ui, ti))
    pairs.sort()
    for prio, d, _, ui, ti in pairs:
        if ui in assignment or taken[ti]:
            continue
        assignment[ui] = tasks[ti]
        taken[ti] = True

    return assignment


def _unit_action(unit_pos, task):
    """Turn an assignment into this turn's action: do it if standing there, else walk."""
    if task is None:
        return ["PASS"]
    ux, uy = unit_pos
    if (ux, uy) == (task["x"], task["y"]):
        return list(task["op"])
    mv = _step_toward(ux, uy, task["x"], task["y"])
    return [mv] if mv else ["PASS"]


def _market_orders(day, hour, money, seeds, shed, prices, hires_today, n_hands):
    """Ordered market queue: SELL (income first), HIRE, then BUY_SEED (spend last)."""
    orders = []

    # Sell per crop. Normal mode: small batches above a min price. Liquidation mode
    # (or a shed close to the 100-item destruction cap): sell every turn regardless.
    shed_total = sum(shed.values())
    for crop, (batch, min_price) in SELL_RULES.items():
        stock = shed.get(crop, 0)
        if stock <= 0:
            continue
        price = prices.get(crop, 0)
        if day >= LIQUIDATE_FROM_DAY or shed_total >= SHED_FORCE_SELL or price >= min_price:
            orders.append(["SELL", crop, min(batch, stock)])

    # Hire the day's hands in one burst at hour 0 (they exist from the next turn on).
    if hour == 0 and day < LAST_DAY:
        for _ in range(max(0, TARGET_HANDS - n_hands - hires_today)):
            orders.append(["HIRE"])

    # Keep a small seed buffer per active crop so PLANT never over-requests and
    # units never walk to a tile they can't plant.
    active = ["MELON"] + ([FILLER] if FILLER else [])
    for crop in active:
        info = CROP_INFO[crop]
        if day > info["last_plant"]:
            continue
        have = seeds.get(crop, 0)
        want = SEED_BUFFER
        if have < want and money >= info["cost"]:
            n = min(want - have, int(money // info["cost"]))
            if n > 0:
                orders.append(["BUY_SEED", crop, n])
                money -= n * info["cost"]

    return orders[:10]  # engine cap: extras are silently dropped


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

    tasks = _build_tasks(tiles, day, seeds)
    assignment = _assign(units, tasks, inventories, day)

    actions = [_unit_action(units[ui], assignment.get(ui)) for ui in range(len(units))]

    # Final guard against the PLANT collective-validation trap: never issue more PLANTs
    # for a crop this turn than seeds held right now (seeds bought this turn arrive later).
    plant_counts = {}
    for i, a in enumerate(actions):
        if a and a[0] == "PLANT":
            crop = a[1]
            plant_counts[crop] = plant_counts.get(crop, 0) + 1
            if plant_counts[crop] > seeds.get(crop, 0):
                actions[i] = ["PASS"]

    market = _market_orders(day, hour, money, seeds, shed, prices,
                            me.get("hires_today", 0), len(me.get("hands", [])))

    if DEBUG:
        n_move = sum(1 for a in actions if a[0] in ("NORTH", "SOUTH", "EAST", "WEST"))
        print(f"d{day} h{hour} units={len(units)} tasks={len(tasks)} "
              f"moving={n_move} market={market}")

    return {"farmer": actions[0], "hands": actions[1:], "market": market}
