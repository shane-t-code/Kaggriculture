"""shop_pin.py — pin the town's shop-unlock sequence in local games.

WHY (the re-roll trap, engine-verified): each evening a per-day RNG first spends
one draw per EMPTY TILE on both farms (weeds), then draws the next shop from the
SAME rng (kaggriculture.py L869-891). So any difference in tile occupancy between
two agents re-rolls the shop world, which (a) breaks the seed as a control and
(b) makes recorded-tape opponents play for a world they never saw (flatters us:
field measurement 78% re-rolled vs 40% preserved).

FIX: monkeypatch _end_of_day; after the engine appends its own (rng-driven) shop,
overwrite the unlocked list with a caller-pinned sequence. Length is preserved
(the engine adds exactly one instance every townShopUnlockInterval days, cap 8,
independent of rng), so both farms in both A and B runs see the SAME world.

Weeds still vary with occupancy — that is real game variance, not the trap.

Usage:
    from tools import shop_pin
    shop_pin.install("MILK0")            # preset
    shop_pin.install(["BAKERY", ...])    # explicit sequence (up to 8)
    shop_pin.uninstall()
Presets (milk shops = PIZZA_SHOP / ICE_CREAM_SHOP / SMOOTHIE_SHOP):
    MILK0  premium-thin: zero milk shops, no yarn      (the loss-mode world)
    MILK1  one milk shop, unlocked late (slot 5)
    MILK3  three milk shops early                      (the boom world)
    YARN2  two yarn stores, no milk
    MIXED  a representative middling draw
"""
import kaggle_environments.envs.kaggriculture.kaggriculture as K

PRESETS = {
    "MILK0": ["BAKERY", "PET_CAFE", "FARMERS_MARKET", "BRUNCH_SPOT",
              "BAKERY", "PET_CAFE", "FARMERS_MARKET", "BRUNCH_SPOT"],
    "MILK1": ["BAKERY", "PET_CAFE", "FARMERS_MARKET", "BRUNCH_SPOT",
              "SMOOTHIE_SHOP", "BAKERY", "PET_CAFE", "FARMERS_MARKET"],
    "MILK3": ["SMOOTHIE_SHOP", "ICE_CREAM_SHOP", "PIZZA_SHOP", "BAKERY",
              "FARMERS_MARKET", "PET_CAFE", "BAKERY", "BRUNCH_SPOT"],
    "YARN2": ["YARN_STORE", "BAKERY", "YARN_STORE", "PET_CAFE",
              "FARMERS_MARKET", "BRUNCH_SPOT", "BAKERY", "PET_CAFE"],
    "MIXED": ["BAKERY", "ICE_CREAM_SHOP", "PET_CAFE", "YARN_STORE",
              "FARMERS_MARKET", "SMOOTHIE_SHOP", "BRUNCH_SPOT", "PIZZA_SHOP"],
}

_ORIG = K._end_of_day
_SEQ = None


def install(seq):
    """seq: preset name or list of shop names (validated against engine SHOPS)."""
    global _SEQ
    if isinstance(seq, str):
        seq = PRESETS[seq.upper()]
    bad = [s for s in seq if s not in K.SHOPS]
    if bad:
        raise ValueError(f"unknown shops {bad}; valid: {sorted(K.SHOPS)}")
    _SEQ = list(seq)

    def _pinned_end_of_day(state, env, day):
        _ORIG(state, env, day)
        town = state[0].observation.town
        shops = town.get("unlocked_shops", [])
        n = len(shops)
        if n <= len(_SEQ):
            town["unlocked_shops"] = _SEQ[:n]
        else:  # sequence shorter than needed: keep engine draws for the tail
            town["unlocked_shops"] = _SEQ + shops[len(_SEQ):]

    _pinned_end_of_day._shop_pin = True
    K._end_of_day = _pinned_end_of_day


def uninstall():
    global _SEQ
    K._end_of_day = _ORIG
    _SEQ = None
