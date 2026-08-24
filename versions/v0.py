"""
main.py — Kaggriculture agent.  ENTRY POINT (must be at archive root, must be named main.py).

STATUS: v0 scaffold.  This is a deliberately simple, readable baseline whose job is to
(a) prove the toolchain end-to-end and (b) give us a correct skeleton to grow.
It is NOT the competitive agent.  See .md for where the real edge is.

!! VALIDATE ON FIRST RUN.  Action-string formats below follow the documented spec, but the
   ENGINE is the source of truth and invalid actions are SILENT NO-OPS (they do not error).
   Run `python run_local.py --debug --seeds 1` and confirm actions are actually landing
   before trusting any result.

Design notes already baked in (from RESEARCH.md):
  * Finish the tile you are standing on before moving.  Walking is the binding constraint;
    one competitor cut moving from 83% -> 55% of unit-turns and roughly TRIPLED their bank.
  * Never let a plant miss two waterings (it becomes a weed).  A seed planted and not watered
    the same day dies that night - consecutive_unwatered starts at 1.
  * Sell in small batches.  Premium goods crash to the $1 floor fast, and floor sales do not
    even add to market inventory (pure loss).
  * Only request PLANT when we actually hold the seed: PLANT is validated COLLECTIVELY per crop
    per turn, and over-requesting converts ALL plant requests that turn to PASS.
"""
from __future__ import annotations

# ----------------------------------------------------------------------------------
# Tunables - the things worth A/B testing first
# ----------------------------------------------------------------------------------
CROP = "MELON"          # MELON has the highest profit/tile-day at base price (142.0)
HARVEST_AGE = 10        # MELON reaches its 6-unit cap at age 10; ages 11-12 add nothing
SELL_BATCH = 6          # small batches: melon floors after ~158 net units sold
MIN_SELL_PRICE = 120    # do not dump into the floor
SEED_BUFFER = 1         # how many spare seeds to hold

DIRS = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0)}
DIR_ACTION = {"N": "NORTH", "S": "SOUTH", "E": "EAST", "W": "WEST"}


def _tile_at(tiles, x, y):
    if 0 <= y < len(tiles) and 0 <= x < len(tiles[0]):
        return tiles[y][x]
    return "LOCKED"


def _is_unlocked_empty(tiles, x, y):
    return _tile_at(tiles, x, y) is None


def _step_toward(fx, fy, tx, ty):
    """One greedy step. Locked tiles are passable, so no pathfinding needed for v0."""
    if fx < tx:
        return DIR_ACTION["E"]
    if fx > tx:
        return DIR_ACTION["W"]
    if fy < ty:
        return DIR_ACTION["S"]
    if fy > ty:
        return DIR_ACTION["N"]
    return None


def _nearest(tiles, fx, fy, predicate):
    """Nearest tile (manhattan) satisfying predicate(tile, x, y). Returns (x, y) or None."""
    best, best_d = None, 10**9
    for y, row in enumerate(tiles):
        for x, t in enumerate(row):
            if predicate(t, x, y):
                d = abs(x - fx) + abs(y - fy)
                if d < best_d:
                    best, best_d = (x, y), d
    return best


def agent(obs):
    player = obs["player"]
    me = obs["farms"][player]
    private = obs["private"]

    tiles = me["tiles"]
    fx, fy = me["farmer"]
    money = me["money"]
    day = obs["day"]

    seeds = private.get("seeds", {}) or {}
    shed = private.get("shed", {}) or {}
    prices = (obs.get("market", {}) or {}).get("prices", {}) or {}

    market = []
    here = _tile_at(tiles, fx, fy)

    # ------------------------------------------------------------------ market layer
    # Keep a seed in the bag so PLANT never over-requests.
    have_seeds = seeds.get(CROP, 0)
    seed_cost = {"WHEAT": 10, "CARROT": 20, "TOMATO": 50, "MELON": 80, "STRAWBERRY": 100}[CROP]
    if have_seeds <= SEED_BUFFER and money >= seed_cost:
        market.append(["BUY_SEED", CROP, 1])

    # Sell in small batches, never into the floor.
    in_shed = shed.get(CROP, 0)
    price = prices.get(CROP, 0)
    if in_shed > 0 and price >= MIN_SELL_PRICE:
        market.append(["SELL", CROP, min(SELL_BATCH, in_shed)])

    def act(a):
        return {"farmer": a if isinstance(a, list) else [a], "hands": [], "market": market}

    # ------------------------------------------------------- finish the tile we stand on
    # (do all same-square work before considering any movement)
    if isinstance(here, dict) and here.get("kind") == "PLANT":
        age = day - here.get("planted_day", day)
        if here.get("yield_units", 0) > 0 and age >= HARVEST_AGE:
            return act("HARVEST")
        if not here.get("watered_today", False):
            return act("WATER")

    if isinstance(here, dict) and here.get("kind") == "WEED":
        return act("DIG")

    if here is None and have_seeds > 0:
        return act(["PLANT", CROP])

    # ------------------------------------------------------------------ choose a target
    # 1) any plant that still needs water today (never lose a plant to the weed timer)
    def needs_water(t, x, y):
        return isinstance(t, dict) and t.get("kind") == "PLANT" and not t.get("watered_today", False)

    # 2) any plant ready to harvest
    def ready(t, x, y):
        if not (isinstance(t, dict) and t.get("kind") == "PLANT"):
            return False
        return t.get("yield_units", 0) > 0 and (day - t.get("planted_day", day)) >= HARVEST_AGE

    # 3) an empty tile to plant on (only if we hold a seed)
    def plantable(t, x, y):
        return t is None

    for pred, need_seed in ((ready, False), (needs_water, False), (plantable, True)):
        if need_seed and have_seeds <= 0:
            continue
        tgt = _nearest(tiles, fx, fy, pred)
        if tgt:
            mv = _step_toward(fx, fy, tgt[0], tgt[1])
            if mv:
                return act(mv)

    return act("PASS")
