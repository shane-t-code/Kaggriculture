"""
main.py — Kaggriculture agent.  ENTRY POINT (must be at archive root, must be named main.py).

STATUS: v17i REJECTED — pool 8 seeds: mirror 0/16 (-10,383!), tape +1,537,
v6a -1,712, v12 -8,089 (dWins -7); POOL TOTAL dWins -23, mean dBank -4,662.
The formula caps hardest exactly against real suppliers (mirror/v12: opponent
inflow subtracts, cap pins near 12) and surrenders the ramp — our largest
revenue engine — for gluts that are TRANSIENT (strawberry has the game's biggest
town drain).  Second failure of pre-emptive strawberry capping (v17a was the
trigger form, this the formula form).  CARD CLOSED: opponent-conditional
strawberry supply-cutting loses in both shapes; reactive triage (v16) plus the
deliberate STRAWBERRY exclusion (v15e evidence) is the settled policy.
Original hypothesis: v17 + DEMAND-DERIVED STRAWBERRY CAP.  Mirror games sold
combined ~300 strawberries at $97 avg (vs $200+ absorbed); v17a's opponent-COUNT
melon trigger failed (pre-emptive surrender), so this uses the absorption law as a
FORMULA: cap = clamp(12, 35, (town drain - opponent's visible STR inflow) / 0.75
units-per-plant-day).  Re-evaluated every turn as shops unlock and the opponent's
field grows; planted berries stay, only expansion is gated.  Variance decomp of
77 live games: our bank swings ~$20k on the MILK SHOP DRAW alone (0 outlets: 55.7k,
1: 77.2k, 2: 81.7k, 3: 94.2k) because the herd is fixed while market capacity is
rolled per game.  Engine (L867-891, verified): one shop unlocks every 3 days, drawn
with replacement from 8 types (3 serve milk -> expectation 3 outlets); by cow-tail
purchase time (days 6-12) 2-4 draws are visible.  Change: cows #7-8 require
projected final milk outlets >= 2.0 (seen instances + remaining draws x 3/8);
otherwise the herd caps at 6 cows and the cash flows to strawberry seeds (existing
herd-gated ramp logic).  First true shop-draw-adaptive PRODUCTION decision — the
margin a replay tape structurally cannot copy.
A/B: conditional mechanism — fired in 9/48 towns (~19%); in fired games
15W-3L (83.3%), mean +2,022 (pre-stated criterion: positive record AND margin in
fired games; unfired games are byte-identical mirrors). p~0.004 binomial.
Base: v16 — Phase 6 fix #6: v15 + DOOMED-CROP TRIAGE (MELON+CARROT only).
Action-mix diff vs the strongest live loss (Hem, 116.8k, same walk share, same
productive-action count, +$30k revenue): we spent 105 more WATERS — 11 melons
watered daily days 17-24 into a $1 market.  When melon/carrot's 3-day projected
price <= $15, generate no water/rescue tasks and stop planting them; harvests
continue (free the tile).  STRAWBERRY deliberately excluded: its gluts are
transient (biggest drain in the game) and v15e, which could skip it, lost its
out-of-sample batch (53.1%, fat tails) to strawberry abandonment.
A/B: v15f beat v15 41-23 over 64 (64.1%: 65.6% +461 seeds 0-15, 62.5% +596 fresh
16-31 — both batches positive).  Action-mix diff vs the Hem loss (their 116.8k, same walk share 59-60%,
nearly same productive actions, +$30k revenue): we spent 105 MORE waters — measured
destination: 11 melons watered daily through days 17-24 into a FLOORED melon market
($1).  Watering, rescuing, replanting crops whose product is dead is the labor leak
that starves care (5-8/12) and fertilize (56 vs their 103).  Fix: when a crop's
3-day projected price <= $15 (same forecast as care-skip), generate NO water/rescue
tasks for its plants and stop planting it; harvests continue (they free the tile
for a live crop).  Labor-only reallocation.
Base: v15 — Phase 6 fix #5: v14 + DAY-0 FOURTH SHEEP.  Opening decode (tape vs
v12, same game, days 0-8): tape out-earns us $9.2k to $5.9k; biggest single cause is
sheep timing — tape owns 4 sheep at hour 0, we bought #4 on day 4.  Sheep first-tick
is 6 days, so all four of theirs pay days 5-6 (the $4.6k wool spike that funds cows
3-8) while ours started day 10.  We missed it because day 0 spent $380 on
strawberry+carrot seeds that yield nothing before day 10 anyway.  Fix: on day 0,
defer STRAWBERRY/CARROT seed buys until the day-0 herd (4 sheep + 1 cow) is owned.
A/B: v14b beat v14 56-8 over 64 (87.5%!! — 84.4% +3.0k seeds 0-15, 90.6% +3.4k
fresh 16-31; STRONGEST promotion in the project).
Base: v14 — Phase 6 fix #4: v13 + HERD-GATED STRAWBERRY RAMP.  PLANT_ORDER puts
STRAWBERRY ahead of WHEAT for tiles (cap 35) but STR seed buying stays at 3/turn
until herd_complete, 5/turn after — cows always outrank berries for cash.  Found by
falsifying two wrong forms first: v13b (cap raise alone, 56.2% — cap was never the
constraint) and v13c (priority + early seed burst, 37.5% — the $500+/turn day-0 seed
spend delayed every cow 1-2 days and marginal strawberry revenue at 35 mirror-plants
is ~$385/tile net, not the $1,100 average at 23).
A/B: v13d beat v13 42-22 over 64 (65.6% BOTH batches: +2.5k seeds 0-15, +1.2k fresh
16-31).
Base: v13 — v12 + endgame wheat factory (62.5% both batches over 64).  Live-loss analysis of
all 64 v10/v11 Kaggle episodes: floored WOOL/MILK games bank 68k vs 88k clean; ~25%
of our wool+milk sold at <=$5.  v12a (sell-timing rules) was a 50.0% wash and proved
the leak is NOT timing — we already sell on arrival; the back half of production
lands after the market dies.  CARE multiplies output (cared = 1+interval units vs 1),
so when the product's projected price ~3 days out (glut curve, combined inflow vs
town drain) is <=$15, the care turn buys nearly nothing and deepens the glut.  Skip
CARE for that species while doomed (FEED/COLLECT/HARVEST unchanged); care resumes on
recovery; freed unit-turns flow to crops.  Labor-only -> occupancy unchanged.
A/B: v12b beat v11 46-18 over 64 (71.9%; 71.9% seeds 0-15 +1.7k, 71.9% fresh 16-31
+2.2k — held out-of-sample).
Base: v11 — Phase 6 fix #1: v10 + FOCUSED FEEDERS (found by direct measurement).
Audit of v10: from day 12 on, only 2-8 of 12 animals got fed daily while CARE stayed
~12 — and an animal unfed on its production day produces base 1 and its WHOLE banked
care bonus is WIPED (engine B.4), so the care labor was being thrown away exactly in
the day-18-27 window where our live losses show us being overtaken.  Trace: the farmer
picks up ALL the feed wheat at hour 0, then greedy assignment sends him across the map
for P_SAVE crop rescues (prio 0 beats FEED's 1; he wins distance ties as unit 0) —
13-hour round trips carrying 20 wheat while the 12 FEED tasks only he could perform
sat waiting.  FIX: while FEED tasks are pending, wheat-carrying units are eligible for
FEED tasks ONLY (hands handle plant rescues).  Audit after: 10-12/12 fed daily.
A/B: v11e beat v10 49-15 over 64 (76.6%; 75.0% seeds 0-15, 78.1% fresh 16-31).
Base (v10) = v9 + faster herd (cushion 4 -> 2 days, none on days 0-1; 65.6% over 64).
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
ANIMAL_TARGETS = {"SHEEP": 4, "COW": 8}
BUY_PRIORITY = ["SHEEP", "COW"]
ANIMAL_INFO = {
    "COW":   {"cost": 400, "build": "BUILD_PASTURE", "first": 8, "interval": 2, "product": "MILK"},
    "SHEEP": {"cost": 500, "build": "BUILD_PASTURE", "first": 6, "interval": 3, "product": "WOOL"},
}
# Ring around the shed-access tile (4,4): FEED/CARE/HARVEST/COLLECT all happen standing ON
# the animal tile and the wheat lives at the shed, so clustering minimizes walking.
ANIMAL_SLOTS = [(3, 4), (4, 3), (3, 3), (2, 4), (4, 2), (2, 3), (3, 2), (2, 2),
                (4, 5), (3, 5), (2, 5), (4, 6)]   # +4 SW slots (build when land unlocks)
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
    "STRAWBERRY": {"cost": 100, "first": 10, "ready": 10, "last_plant": 17, "window": (0, -1), "cap": 35},
    "CARROT":     {"cost": 20,  "first": 2,  "ready": 3,  "last_plant": 26, "window": (2, 3),  "cap": 12},
}
# Planting priority when a tile opens up: melon (highest $/tile-day, tiny cap), wheat (feeds
# the herd — replaces market buys at scarcity prices), strawberry (biggest town demand:
# ~426/season median), carrot (fast filler, capped so we stop glutting our own market).
PLANT_ORDER = ["MELON", "STRAWBERRY", "WHEAT", "CARROT"]
SEED_WANT = {"MELON": 3, "WHEAT": 4, "STRAWBERRY": 5, "CARROT": 4}
WHEAT_FEED_RESERVE_DAYS = 2   # hold animals*this much wheat before selling any surplus

# Endgame wheat factory (v13a).  Milestone diff vs the tape: it sells ~479 wheat at
# ~$40 ($19.4k) by converting freed premium tiles to wheat wall-to-wall late-game;
# wheat demand never gluts (6 shop types).  From this day, wheat stops being
# feed-sized and becomes the default cash crop for open land.
WHEAT_FACTORY_DAY = 18
WHEAT_FACTORY_CAP = 45        # replaces CROP_INFO cap 20 from factory day
WHEAT_FACTORY_SEED_WANT = 10  # replaces SEED_WANT 4 from factory day

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

# Doomed-market care skip (v12b).  A cared animal yields 1+interval units vs 1 —
# but if the product's market is projected at/near the floor when those units
# land (~3 days out), the care action is labor spent deepening a glut.  Skip CARE
# for that species while the projection stays doomed; everything else (FEED,
# COLLECT_FERTILIZER, HARVEST) continues.  Checked fresh every turn, so care
# resumes the moment the market recovers.
STR_CAP_MIN = 12         # demand-derived strawberry cap bounds (v17i)
STR_CAP_MAX = 35
STR_PER_PLANT = 0.75     # units/day one fertilized-ish plant feeds the market
CARE_SKIP_PRICE = 15     # projected price at/below this = care not worth the turn
CARE_SKIP_HORIZON = 3    # days until a banked care bonus typically pays out

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


CROP_SKIP_PRICE = 15     # crop's 3-day projected price at/below this = its labor
                         # (water/rescue/replant) is spent on worthless goods

def _crop_skip(tiles, opp_tiles, market_inv, shops):
    """Crops whose market is projected dead — stop watering/planting them."""
    skip = set()
    my_crops, my_animals = _opp_capacity(tiles)
    opp_crops, opp_animals = _opp_capacity(opp_tiles)
    # MELON/CARROT only: melon's town drain is ~1/day so a floored melon market
    # never recovers (safe to abandon); carrot is cheap filler.  STRAWBERRY is
    # excluded — its drain is the biggest in the game, gluts PASS, and v15e
    # (which could skip it) lost its out-of-sample batch 17-15 with -1.2k/5.6k sd:
    # abandoning 35 strawberries during a transient dip is catastrophic.
    for crop in ("MELON", "CARROT"):
        if crop not in MARKET_ABOVE:
            continue
        x = market_inv.get(crop, MARKET_I0) - MARKET_I0
        net = (_town_drain_per_day(crop, shops)
               - _inflow_per_day(crop, my_crops, my_animals)
               - _inflow_per_day(crop, opp_crops, opp_animals))
        proj = _glut_price(crop, max(0, x - net * CARE_SKIP_HORIZON))
        if proj <= CROP_SKIP_PRICE:
            skip.add(crop)
    return skip


def _care_skip_species(tiles, opp_tiles, market_inv, shops):
    """Species whose product market is projected dead when a care bonus would land."""
    skip = set()
    my_crops, my_animals = _opp_capacity(tiles)
    opp_crops, opp_animals = _opp_capacity(opp_tiles)
    for sp, info in ANIMAL_INFO.items():
        item = info["product"]
        if item not in MARKET_ABOVE:
            continue
        x = market_inv.get(item, MARKET_I0) - MARKET_I0
        net = (_town_drain_per_day(item, shops)
               - _inflow_per_day(item, my_crops, my_animals)
               - _inflow_per_day(item, opp_crops, opp_animals))
        proj = _glut_price(item, max(0, x - net * CARE_SKIP_HORIZON))
        if proj <= CARE_SKIP_PRICE:
            skip.add(sp)
    return skip


def _build_tasks(tiles, day, seeds, tape_mode=False, care_skip=(), crop_skip=(),
                 str_cap=STR_CAP_MAX):
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

                if not t.get("cared_today", False) and t["animal"] not in care_skip:
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

                # Doomed-crop triage (v15e): its market is projected dead, so its
                # water/rescue labor buys $1 goods — spend those unit-turns on live
                # crops and animals instead.  Harvests above still run (they free
                # the tile); the plant may weed and gets dug at leisure (P_DIG).
                if crop in crop_skip:
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
                cap = info["cap"]
                if c == "WHEAT" and day >= WHEAT_FACTORY_DAY:
                    cap = WHEAT_FACTORY_CAP
                if c == "STRAWBERRY":
                    cap = min(cap, str_cap)
                if (planned.get(c, 0) < cap and day <= info["last_plant"]
                        and budget.get(c, 0) > 0
                        and c not in crop_skip
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
    if n_feed > carried_wheat and shed.get("WHEAT", 0) > 0:
        n = min(n_feed - carried_wheat + 2, shed["WHEAT"])
        tasks.append({"prio": P_CHAIN, "x": SHED_TILE[0], "y": SHED_TILE[1],
                      "op": ["PICKUP", "WHEAT", n]})

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

    def feeds_open():
        return any(t["op"][0] == "FEED" and not taken[ti]
                   for ti, t in enumerate(tasks))

    def eligible(ui, task):
        req = task.get("require")
        if req is not None and inv_of(ui).get(req, 0) <= 0:
            return False
        # FOCUSED FEEDER (v11e): while FEED tasks are pending, wheat carriers do
        # feeds ONLY.  Measured failure: the sole wheat carrier was assigned P_SAVE
        # crop rescues across the map and fed 2-6 of 12 animals/day from day 12 on —
        # an animal unfed on its production day wipes its whole banked care bonus.
        # Hands can rescue plants; only wheat carriers can feed.
        if (task["op"][0] != "FEED" and inv_of(ui).get("WHEAT", 0) > 0
                and feeds_open()):
            return False
        return True

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
    # (v16c) milk projection must precede herd_complete: a capped herd (6 cows
    # on a poor milk draw) counts as COMPLETE so the strawberry ramp still opens.
    milk_seen = sum(1 for s in shops if s in ("PIZZA_SHOP", "ICE_CREAM_SHOP",
                                              "SMOOTHIE_SHOP"))
    milk_proj = milk_seen + max(0, 8 - len(shops)) * 0.375
    cow_target = 6 if milk_proj < 2.0 else ANIMAL_TARGETS["COW"]
    herd_complete = (owned["SHEEP"] >= ANIMAL_TARGETS["SHEEP"]
                     and owned["COW"] >= cow_target)

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
            if sp == "COW" and owned["COW"] >= cow_target:
                continue
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
        if day > info["last_plant"] or info["cap"] <= 0:
            continue
        want = SEED_WANT[crop]
        if crop == "WHEAT" and day >= WHEAT_FACTORY_DAY:
            want = WHEAT_FACTORY_SEED_WANT
        if crop == "STRAWBERRY" and not herd_complete:
            # Cows before berries: v13c's day-0 seed burst ($500+) delayed the
            # first cow by days and lost every downstream milk/fert/care dollar.
            want = 3
        if (day == 0 and crop in ("STRAWBERRY", "CARROT")
                and (owned["SHEEP"] < ANIMAL_TARGETS["SHEEP"] or owned["COW"] < 1)):
            # Day-0 fourth sheep (v14b): premium seeds yield nothing before day
            # 10, but a sheep bought day 0 vs day 4 moves its whole wool stream
            # up 4 days — the tape's day-0 allocation, decoded and copied.
            continue
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
    if not _TAPE_SEEN.get(player, False) and 1 <= day <= 2:
        _oc, _oa = _opp_capacity(opp.get("tiles", []))
        # Self-exclusion (v15 copies the tape's 4-sheep opening): the tape shows
        # 4 SHEEP + COW + exactly 5 MELONS from day 1 (byte-identical opening);
        # our lineage has no placed cow on days 1-2 and at most 3 melons before
        # day 3.  Both extra conditions + the day-2 cutoff keep us from false-
        # latching tape counters against our own versions in self-matches.
        if (_oa.get("SHEEP", 0) == 4 and _oa.get("COW", 0) >= 1
                and _oc.get("MELON", 0) == 5):
            _TAPE_SEEN[player] = True
    tape_mode = _TAPE_SEEN.get(player, False)

    market_inv = (obs.get("market", {}) or {}).get("inventory", {}) or {}
    shops = (obs.get("town", {}) or {}).get("unlocked_shops", []) or []
    care_skip = _care_skip_species(tiles, opp.get("tiles", []), market_inv, shops)
    crop_skip = _crop_skip(tiles, opp.get("tiles", []), market_inv, shops)

    # Demand-derived strawberry cap (v17i): plant only what the market can
    # absorb after the opponent's visible strawberry inflow (absorption law —
    # opponent-COUNT triggers failed in v17a; demand-derived is the v17 pattern).
    _ocs, _oas = _opp_capacity(opp.get("tiles", []))
    _str_drain = _town_drain_per_day("STRAWBERRY", shops)
    _opp_str_in = _inflow_per_day("STRAWBERRY", _ocs, _oas)
    str_cap = max(STR_CAP_MIN,
                  min(STR_CAP_MAX, int((_str_drain - _opp_str_in) / STR_PER_PLANT)))
    tasks, n_feed = _build_tasks(tiles, day, seeds, tape_mode, care_skip, crop_skip,
                                 str_cap)
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
                            len(me.get("unlocked_quadrants", ["NW"])),
                            opp.get("tiles", []), market_inv, shops, tape_mode)

    if DEBUG:
        print(f"d{day} h{hour} units={len(units)} tasks={len(tasks)} market={market}")

    return {"farmer": actions[0], "hands": actions[1:], "market": market}
