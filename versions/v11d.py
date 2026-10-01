"""
main.py — Kaggriculture agent.  ENTRY POINT (must be at archive root, must be named main.py).

STATUS: v11d CANDIDATE — v10 + WEEK-1 HERD CAPITAL REBALANCE.  Real-loss evidence: in
9 of 14 live losses we led at day 18 and were overtaken by 14-30-animal farms; v11a
proved animals bought on days 12-16 cannot repay themselves — the winners build their
herds in WEEK 1 by converting every early dollar into animals.  Changes as one
coherent mechanism: (a) ANIMAL_TARGETS 8C/4S -> 10C/6S (16 animals, +4 slots);
(b) while the herd is incomplete, SKIP melon/strawberry seed purchases (the two big
capital sinks — $80-100/seed) so early cash becomes animals instead; cheap wheat/
carrot seeds still bought (cash flow + feed); (c) parallel feed carriers (v11a's
proven fix — one carrier per turn starves a 16+ herd).
Base was: v9 + FASTER HERD (opening speed).  The meta tape's herd is
complete by day 8 (first cow milk lands day 7); v9's completed ~day 15 because the
animal-buy gate demanded cost + reserve + a 4-day whole-herd feed cushion (~$1,900 for
a $400 cow at herd 8).  That cushion predated the feed-sacred fix (feed buys bypass
every reserve), so it was double protection.  Change: cushion 4 -> 2 days, and none on
days 0-1 (the daily fertilizer stream — ~$98/animal/day — starts before the first feed
bill can hurt).  Each animal still arrives with its 3-wheat dowry.
A/B: v8d beat v9 42-22 over 64 (65.6% on BOTH seed batches, margin +2.0k/+3.0k).
Base (v9) = v8 rational thresholds + tape-family counter:
  * MELON: its day-20 wave kills the melon market permanently (measured: $246 -> $16 -> $1).
    Sell everything before it lands (threshold 60 from day 15, dump from day 18) and stop
    planting melons after day 8 (a melon maturing past ~day 18 will be worth $1).
  * WOOL: its wool dump floors the market from day ~10.  Sell wool at anything >= 35
    through day 12 rather than hold stock the market will never pay for again.
Verified byte-identical vs non-tape opponents (4-seed exact-mirror check).  Vs the tape:
margin -48.5k (v8: -54.0k, v7: -59.5k), sd 10.5k (was 16.0k); still 0-16 — the rest of
the gap is production, targeted next (strawberry volume, opening speed).
A/B record: v7a beat v7 51-13 over 64 (79.7%) | v6a beat v6 46-18 (71.9%) | v5b beat
v5 31-1 | v5a beat v4 27-5 | v4c beat v3 28-4 | v3a beat v2 30-2 | v2a beat v1 32-0 |
v1 beat v0 32-0.  Bank-diff risk (v7b): WASH, shelved for Phase 6.

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

import math

DEBUG = False

# ----------------------------------------------------------------------------------
# Tunables
# ----------------------------------------------------------------------------------
TARGET_HANDS = 6         # scale retest: 10 hands at 3 quadrants ($143/day fib)
HANDS_PER_EXTRA_QUADRANT = 2
LAND_MAX_QUADRANTS = 3   # v5b: retry the 3rd quadrant now that fert + cash bugs are fixed
LAND_PRICES = [1000, 2000, 4000]   # engine LAND_PRICES (ENGINE_NOTES B.1); order NE->SW->SE
# (crop mix now lives in CROP_INFO caps + PLANT_ORDER + SEED_WANT below)
LIQUIDATE_FROM_DAY = 28  # unsold inventory is worth $0 at the end — sell everything late
SHED_FORCE_SELL = 80     # shed cap is 100 and overflow is DESTROYED at end-of-day drop
UNLOAD_AT = 8            # a unit carrying this many items runs them to the shed (sellable today)

# Livestock plan: sheep first (slowest payout -> place earliest, CARE stacks highest on it),
# cows are the meta-proven workhorse. 6 animals ring the shed on one quadrant.
ANIMAL_TARGETS = {"SHEEP": 6, "COW": 10}
BUY_PRIORITY = ["SHEEP", "COW"]
ANIMAL_INFO = {
    "COW":   {"cost": 400, "build": "BUILD_PASTURE", "first": 8, "interval": 2, "product": "MILK"},
    "SHEEP": {"cost": 500, "build": "BUILD_PASTURE", "first": 6, "interval": 3, "product": "WOOL"},
}
# Ring around the shed-access tile (4,4): FEED/CARE/HARVEST/COLLECT all happen standing ON
# the animal tile and the wheat lives at the shed, so clustering minimizes walking.
ANIMAL_SLOTS = [(3, 4), (4, 3), (3, 3), (2, 4), (4, 2), (2, 3), (3, 2), (2, 2),
                (4, 5), (3, 5), (2, 5), (4, 6),   # SW slots (build when land unlocks)
                (5, 4), (5, 3), (3, 6), (2, 6)]   # v11d: +4 (NE/SW shed-adjacent)
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
}
NEVER_FORCE_SELL = {"WHEAT"}

# cap = max concurrent plants (market- or purpose-bound, not space-bound).
# Window (0,-1) = "watering never adds instant yield" (ongoing crops bonus only via fertilizer).
CROP_INFO = {
    "MELON":      {"cost": 80,  "first": 10, "ready": 10, "last_plant": 19, "window": (6, 12), "cap": 12},
    "WHEAT":      {"cost": 10,  "first": 2,  "ready": 4,  "last_plant": 24, "window": (2, 4),  "cap": 20},
    "STRAWBERRY": {"cost": 100, "first": 10, "ready": 10, "last_plant": 17, "window": (0, -1), "cap": 24},
    "CARROT":     {"cost": 20,  "first": 2,  "ready": 3,  "last_plant": 26, "window": (2, 3),  "cap": 12},
}
# Planting priority when a tile opens up: melon (highest $/tile-day, tiny cap), wheat (feeds
# the herd — replaces market buys at scarcity prices), strawberry (biggest town demand:
# ~426/season median), carrot (fast filler, capped so we stop glutting our own market).
PLANT_ORDER = ["MELON", "WHEAT", "STRAWBERRY", "CARROT"]
SEED_WANT = {"MELON": 3, "WHEAT": 4, "STRAWBERRY": 3, "CARROT": 4}
WHEAT_FEED_RESERVE_DAYS = 2   # hold animals*this much wheat before selling any surplus

# Fertilize-only addition (v4c): a $90 fertilizer applied to a STRAWBERRY doubles its
# production ticks while watered (engine-verified) — ~$200+ of berries. Melon: reaches its
# 6-cap ~2 days earlier. Everything else is byte-identical to v3a.
FERT_CROPS = {"STRAWBERRY": (7, 15), "MELON": (5, 7)}   # crop -> (min_age, max_age)
FERT_KEEP = 6            # hold this much fertilizer stock back from selling

# Opponent-pressure-aware selling (Phase 5, v6a). The opponent's farm is PUBLIC every
# turn. When their visible capacity in a premium product is large, their dump is coming:
# the first seller gets the better price and a crashed market hurts the later seller more
# (measured by a competitor: selling harder cost them $4k and the opponent $11.8k). So
# under pressure we sell earlier (lower threshold) and faster (bigger batch); with no
# opposing capacity we hold for full price as usual. Tapes cannot respond to this.
OPP_PRESSURE = {
    #            how to count opponent capacity      trigger  threshold x  batch +
    "MILK":       ("animal", "COW",        4),
    "WOOL":       ("animal", "SHEEP",      3),
    "STRAWBERRY": ("crop",   "STRAWBERRY", 8),
    "MELON":      ("crop",   "MELON",      8),
}
PRESSURE_THRESHOLD_MULT = 0.65
PRESSURE_BATCH_BONUS = 3

# Tape-family counter (v7c).  Fingerprint: the meta tape places exactly 4 SHEEP and
# its first COW on day 0 (visible from day 1); we field 3 sheep and no cow then, so
# there is no self-detection.  Checked on days 1-3 and latched for the episode.
# STALENESS WARNING: the wave timings below are decoded from the CURRENT public tape
# (2026-08-24).  If the meta shifts openings the latch simply stops firing (fail-safe),
# but a NEW tape with the same opening and a different sell schedule would make these
# timed dumps wrong — re-verify weekly against fresh top-ladder replays.
TAPE_MELON_LAST_PLANT = 8    # a melon maturing after ~day 18 sells into their wave's wreckage
TAPE_WOOL_SALVAGE_UNTIL = 12
TAPE_WOOL_SALVAGE = 35
TAPE_MELON_SOFT_DAY = 15     # sell melons at >= 60 from here...
TAPE_MELON_SOFT = 60
TAPE_MELON_DUMP_DAY = 18     # ...and at any price from here (their wave lands day 20)
TAPE_MELON_DUMP = 10
_TAPE_SEEN = {}              # player -> latched?  (reset at step 0 each episode)

# ---------------------------------------------------------------------------
# Rational sell thresholds (v7a).  The engine's glut-side price curve, verbatim
# (ENGINE_NOTES B.1, engine L41-74): price = base - target*base*f(x)/f(T),
# floored at $1, where x = market_inventory - I0 (I0 = 10,000).
# If even the town's full drain until liquidation day cannot lift the price back
# above our static threshold, the static threshold is a fantasy — accept the best
# still-reachable price instead of holding the stock down to the $1 floor.
# ---------------------------------------------------------------------------
MARKET_I0 = 10000
MARKET_ABOVE = {
    #             base   T    func      target
    "WOOL":       (200, 105, "sq",     3.2),
    "MILK":       (160, 122, "linear", 1.6),
    "MELON":      (250, 300, "sq",     3.6),
    "STRAWBERRY": (120, 100, "linear", 1.6),
    "CARROT":     (35,  450, "sqrt",   0.7),
    "FERTILIZER": (100, 200, "linear", 0.4),
}

# Engine SHOPS map (verified verbatim vs source).  Single-product shops consume
# 2x.  Each instance ticks every 4 turns (6x/day); the town center additionally
# eats 1/day of everything except fertilizer.
SHOP_DEMAND = {
    "BAKERY":         ("EGG", "WHEAT"),
    "PIZZA_SHOP":     ("MILK", "TOMATO", "WHEAT"),
    "BRUNCH_SPOT":    ("EGG", "WHEAT", "STRAWBERRY"),
    "YARN_STORE":     ("WOOL",),
    "ICE_CREAM_SHOP": ("STRAWBERRY", "MILK", "WHEAT"),
    "PET_CAFE":       ("CARROT",),
    "SMOOTHIE_SHOP":  ("STRAWBERRY", "MILK"),
    "FARMERS_MARKET": ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY"),
}


def _glut_price(item, x):
    """Engine price at net glut x units past I0 (above branch only)."""
    base, T, func, target = MARKET_ABOVE[item]
    if x <= 0:
        return base
    if func == "linear":
        f = x / T
    elif func == "sq":
        f = (x / T) ** 2
    elif func == "sqrt":
        f = (x / T) ** 0.5
    else:  # log
        f = math.log1p(x) / math.log1p(T)
    return max(1, int(round(base * (1.0 - target * f))))


def _town_drain_per_day(item, shops):
    d = 0 if item == "FERTILIZER" else 1          # town center, 1/day
    for s in shops:
        prods = SHOP_DEMAND.get(s, ())
        if item in prods:
            d += 6 * (2 if len(prods) == 1 else 1)
    return d


def _inflow_per_day(item, crops, animals):
    """Rough units/day BOTH-farms production feeding this market (cared/watered rates)."""
    if item == "WOOL":
        return animals.get("SHEEP", 0) * 1.33     # cared sheep: 4 wool / 3 days
    if item == "MILK":
        return animals.get("COW", 0) * 1.5        # cared cow: 3 milk / 2 days
    if item == "FERTILIZER":
        return float(sum(animals.values()))       # 1/animal/day, fed or not
    if item == "MELON":
        return crops.get("MELON", 0) * 0.6        # 6 units / ~10-day cycle
    if item == "STRAWBERRY":
        return crops.get("STRAWBERRY", 0) * 0.75  # fertilized ongoing ~1.5 / 2 days
    if item == "CARROT":
        return crops.get("CARROT", 0) * 1.0       # 3 units / 3-day cycle
    return 0.0


def _opp_capacity(opp_tiles):
    """Count the opponent's visible production sources by kind."""
    crops = {}
    animals = {}
    for row in opp_tiles:
        for t in row:
            if isinstance(t, dict):
                if t.get("kind") == "PLANT":
                    crops[t.get("crop")] = crops.get(t.get("crop"), 0) + 1
                elif t.get("animal"):
                    animals[t["animal"]] = animals.get(t["animal"], 0) + 1
    return crops, animals

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
P_FERT = 3     # apply fertilizer to a strawberry/melon in its payoff window
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


def _build_tasks(tiles, day, seeds, tape_mode=False):
    """Scan the farm -> the turn's task list. Returns (tasks, n_feed_needed)."""
    tasks = []
    crop_counts = {}
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

                if crop in FERT_CROPS and day < 26:
                    lo, hi = FERT_CROPS[crop]
                    if lo <= age <= hi and t.get("fertilized_until_day", -1) < day:
                        tasks.append({"prio": P_FERT, "x": x, "y": y,
                                      "op": ["FERTILIZE"], "require": "FERTILIZER"})
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
                        and budget.get(c, 0) > 0
                        and not (tape_mode and c == "MELON"
                                 and day > TAPE_MELON_LAST_PLANT)):
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
    shortfall = n_feed - carried_wheat
    if shortfall > 0 and shed.get("WHEAT", 0) > 0:
        # One wheat-carrier per turn starves a 16+ herd (v11a, measured: escapes from
        # day 16).  Split the load across up to 3 concurrent carriers.
        remaining = min(shortfall + 2, shed["WHEAT"])
        carriers = min(3, (shortfall + 5) // 6)
        for i in range(carriers):
            n = min(6 + (2 if i == 0 else 0), remaining)
            if n <= 0:
                break
            tasks.append({"prio": P_CHAIN, "x": SHED_TILE[0], "y": SHED_TILE[1],
                          "op": ["PICKUP", "WHEAT", n]})
            remaining -= n

    # Fertilizer for FERTILIZE tasks: circuit units already carry some from
    # COLLECT_FERTILIZER; top up from the shed only when several plants are waiting.
    # PRIORITY MATTERS: at P_CHAIN(1) this errand outranked WATER(2) and the scheduler
    # yo-yoed units to the shed while crops died — measured: WATER 800->609, wheat
    # weeded out, 26 melon replants. Fertilizing is a luxury; restock at P_FERT(3).
    n_fert = sum(1 for t in tasks if t["op"][0] == "FERTILIZE")
    carried_fert = sum(inv.get("FERTILIZER", 0) for inv in inventories)
    if n_fert - carried_fert >= 3 and shed.get("FERTILIZER", 0) > 0:
        n = min(n_fert - carried_fert, shed["FERTILIZER"])
        tasks.append({"prio": P_FERT, "x": SHED_TILE[0], "y": SHED_TILE[1],
                      "op": ["PICKUP", "FERTILIZER", n]})

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

    def greedy(candidate_tis):
        """Most urgent first, nearest eligible unit wins, stable tie-break."""
        pairs = []
        for ti in candidate_tis:
            if taken[ti]:
                continue
            task = tasks[ti]
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

    # Urgent work (saves, feeds, harvests, supply chains) is assigned globally — a dying
    # plant doesn't care about zones.
    greedy([ti for ti, t in enumerate(tasks) if t["prio"] < P_WATER])

    # ZONED SWEEP for routine work (water/care/collect/plant/dig): order the remaining
    # tasks along a serpentine (row-by-row, alternating direction) and carve them into one
    # contiguous chunk per free unit, matched to units by the same ordering. Each worker
    # sweeps its own strip of farm instead of crisscrossing the whole board — walking was
    # 52-54% of unit-turns under pure global-greedy (reported competitive floor ~33%).
    def serp(x, y):
        return (y, x if y % 2 == 0 else 15 - x)

    low = [ti for ti, t in enumerate(tasks) if not taken[ti] and t["prio"] >= P_WATER]
    free = [ui for ui in range(len(units)) if ui not in assignment]
    if low and free:
        low.sort(key=lambda ti: serp(tasks[ti]["x"], tasks[ti]["y"]))
        free.sort(key=lambda ui: serp(units[ui][0], units[ui][1]))
        chunk = (len(low) + len(free) - 1) // len(free)
        for k, ui in enumerate(free):
            part = low[k * chunk:(k + 1) * chunk]
            ux, uy = units[ui]
            best, best_key = None, None
            for ti in part:
                if taken[ti] or not eligible(ui, tasks[ti]):
                    continue
                t = tasks[ti]
                key = (t["prio"], abs(t["x"] - ux) + abs(t["y"] - uy), t["y"] * 16 + t["x"])
                if best_key is None or key < best_key:
                    best, best_key = ti, key
            if best is not None:
                assignment[ui] = tasks[best]
                taken[best] = True

    # Cleanup: anything still unmatched (require-filtered tasks, empty chunks) falls back
    # to plain global greedy so no unit idles while work exists.
    greedy(range(len(tasks)))

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
                   n_hands, tiles, n_quadrants, opp_tiles, market_inv, shops, tape_mode):
    opp_crops, opp_animals = _opp_capacity(opp_tiles)
    my_crops, my_animals = _opp_capacity(tiles)
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
        if item == "FERTILIZER" and 8 <= day < LAST_DAY:
            # Hold stock for crop fertilizing — but ONLY once the farm is liquid. In the
            # $0-bank opening, fertilizer sales are the survival cash that buys feed;
            # hoarding them starved the sheep that produce them (measured: 0-32 vs v3a).
            stock -= FERT_KEEP
        if stock <= 0:
            continue
        price = prices.get(item, 0)
        force = shed_total >= SHED_FORCE_SELL and item not in NEVER_FORCE_SELL
        threshold, n = min_price, batch
        if item in MARKET_ABOVE and day < liq_day:
            # Rational threshold: once a market is glutted (x > 0), project where its
            # price can still go before liquidation day.  Net recovery = town drain
            # minus BOTH farms' ongoing production (ours + the opponent's public
            # capacity).  If the best still-reachable price is below our static
            # threshold, that threshold is a fantasy — accept the reachable price
            # now and dump faster (the first seller gets the better price).
            x = market_inv.get(item, MARKET_I0) - MARKET_I0
            if x > 0:
                net = (_town_drain_per_day(item, shops)
                       - _inflow_per_day(item, my_crops, my_animals)
                       - _inflow_per_day(item, opp_crops, opp_animals))
                reachable = _glut_price(item, x - net * (liq_day - day))
                if reachable < threshold:
                    threshold = max(3, reachable)
                    n = batch + PRESSURE_BATCH_BONUS
        if item in OPP_PRESSURE and day < liq_day:
            kind, source, trigger = OPP_PRESSURE[item]
            count = (opp_animals if kind == "animal" else opp_crops).get(source, 0)
            if count >= trigger:
                # Their dump is coming — sell first, sell faster.
                threshold = max(2, int(threshold * PRESSURE_THRESHOLD_MULT))
                n = batch + PRESSURE_BATCH_BONUS
        if tape_mode and day < liq_day:
            # We know the tape's decoded sell schedule; it cannot know ours.
            if item == "WOOL" and day <= TAPE_WOOL_SALVAGE_UNTIL:
                threshold = min(threshold, TAPE_WOOL_SALVAGE)
                n = batch + 5
            elif item == "MELON" and day >= TAPE_MELON_DUMP_DAY:
                threshold = min(threshold, TAPE_MELON_DUMP)
                n = batch + 5
            elif item == "MELON" and day >= TAPE_MELON_SOFT_DAY:
                threshold = min(threshold, TAPE_MELON_SOFT)
        if day >= liq_day or force or price >= threshold:
            orders.append(["SELL", item, min(n, stock)])

    # Wheat feed top-up from the market only if growing hasn't covered it. Bought wheat
    # lands in the shed after this turn's unit actions, so buy ahead of need.
    wheat_price = max(1, prices.get("WHEAT", 25))
    if day <= LAST_TICK_DAY and placed_animals > 0:
        wheat_stock = shed.get("WHEAT", 0) + sum(inv.get("WHEAT", 0) for inv in inventories)
        want = placed_animals + 2
        if wheat_stock < want and money > 0:
            # FEED IS SACRED: feed buys bypass every reserve (the reserve exists FOR feed).
            n = min(want - wheat_stock, int(money // wheat_price))
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

    # Animals: buy toward targets (sheep first), one per turn — ONLY if the bank can also
    # carry ~4 days of feed for the herd this animal joins (pre-income starvation destroyed
    # ~$1.7k of animals in v4a before this gate existed). Each arrives with a wheat dowry.
    if day <= 20 and not herd_complete:
        herd_after = sum(owned.values()) + 1
        # 2-day cushion (feed buys are already sacred; 4 days double-protected and
        # delayed the herd ~6 days).  Days 0-1: no cushion — the fertilizer stream
        # (~$98/animal/day) starts before the first feed bill can hurt.
        feed_cushion = 0 if day <= 1 else herd_after * wheat_price * 2
        for sp in BUY_PRIORITY:
            cost = ANIMAL_INFO[sp]["cost"]
            if owned[sp] < ANIMAL_TARGETS[sp] and money >= cost + MONEY_RESERVE + feed_cushion:
                orders.append(["BUY_ANIMAL", sp, 1])
                money -= cost
                orders.append(["BUY_PRODUCT", "WHEAT", 3])
                money -= 3 * wheat_price
                break

    # Land: NE after 6 animals owned, SW after 8 (waiting for the full 12-herd would
    # deadlock — animals 9-12 place on SW slots that need the land first).
    land_ready = sum(owned.values()) >= (6 if n_quadrants == 1 else 8)
    if (n_quadrants < LAND_MAX_QUADRANTS and day <= 20 and land_ready):
        land_cost = LAND_PRICES[n_quadrants - 1]
        if money >= land_cost + MONEY_RESERVE + 200:
            orders.append(["BUY_LAND"])
            money -= land_cost

    # Seeds spend only what the herd's feed budget doesn't claim (the day-0 seed burst
    # once drained the bank to $0 and freshly placed sheep starved before any income).
    feed_hold = sum(owned.values()) * wheat_price * 4
    spendable = money - feed_hold
    for crop in PLANT_ORDER:
        info = CROP_INFO[crop]
        if day > info["last_plant"]:
            continue
        if not herd_complete and info["cost"] >= 80:
            # Week-1 capital rebalance: while the herd is incomplete, $80-100 premium
            # seeds are deferred — every early dollar becomes an animal instead
            # (cheap wheat/carrot seeds still bought: cash flow + feed).
            continue
        want = SEED_WANT[crop]
        have = seeds.get(crop, 0)
        if have < want and spendable >= info["cost"]:
            n = min(want - have, int(spendable // info["cost"]))
            if n > 0:
                orders.append(["BUY_SEED", crop, n])
                spendable -= n * info["cost"]

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

    # Tape-family fingerprint: evaluated on days 1-3, latched for the episode.
    opp = obs["farms"][1 - player]
    step = obs.get("step", day * 24 + hour)
    if step == 0:
        _TAPE_SEEN[player] = False
    if not _TAPE_SEEN.get(player, False) and 1 <= day <= 3:
        _oc, _oa = _opp_capacity(opp.get("tiles", []))
        if _oa.get("SHEEP", 0) == 4 and _oa.get("COW", 0) >= 1:
            _TAPE_SEEN[player] = True
    tape_mode = _TAPE_SEEN.get(player, False)

    tasks, n_feed = _build_tasks(tiles, day, seeds, tape_mode)
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

    market_inv = (obs.get("market", {}) or {}).get("inventory", {}) or {}
    shops = (obs.get("town", {}) or {}).get("unlocked_shops", []) or []
    market = _market_orders(day, hour, money, seeds, shed, inventories, prices,
                            me.get("hires_today", 0), len(me.get("hands", [])), tiles,
                            len(me.get("unlocked_quadrants", ["NW"])),
                            opp.get("tiles", []), market_inv, shops, tape_mode)

    if DEBUG:
        print(f"d{day} h{hour} units={len(units)} tasks={len(tasks)} market={market}")

    return {"farmer": actions[0], "hands": actions[1:], "market": market}
