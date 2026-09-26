"""Build fork/c31.py = c23s + DEMAND-MATCHED SWAP CROP .

c23s's str-replant swap hardcodes CARROT.  The 100-world census
(results/str_world_scan.jsonl) shows swap-fired worlds where revealed
demand is tomato-only (e.g. PIZZA_SHOP x3, no PET_CAFE): there the swap
plants into near-zero carrot demand.  This build chooses the replacement
crop from REVEALED shops at swap time:
  TOMATO iff day <= _CA_TOM_LAST (age-8 first yield must fit the season),
  drain-weighted revenue favors it (n_tom*p_t > n_car*p_c, PET_CAFE
  counted double per the single-product doubling law, engine :741), a
  tomato seed is in hand, and the tomato yield path over the native's
  own future visits banks >= 3 units.  Otherwise CARROT (unchanged).
Engine laws used (kaggriculture.py): ongoing crops produce +1 unit at
midnight of ages first..first+ (max_yield-1)*interval, MAX max_yield
productions TOTAL (:789-802); HARVEST refuses ongoing crops before
first_yield_day (:453); 2 consecutive unwatered days = weed, plant-day
counts (consecutive_unwatered starts at 1).

All surgery is assert-guarded string replacement on fork/c23s.py.
"""

src = open(r'fork\c23s.py', encoding='utf-8').read()
assert '_CA_TOM_SWAP' not in src

# --- 1. dials ---
old = '_CA_STR_SHOPS = ("BRUNCH_SPOT", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP", "FARMERS_MARKET")'
new = '''_CA_STR_SHOPS = ("BRUNCH_SPOT", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP", "FARMERS_MARKET")
_CA_TOM_SWAP = True
_CA_TOM_SHOPS = ("PIZZA_SHOP", "FARMERS_MARKET")
_CA_TOM_LAST = 19
_CA_TOM_MAX_SEEDS = 6'''
assert src.count(old) == 1
src = src.replace(old, new)

# --- 2. state: credit_tom ---
old = '{"step": -1, "tiles": {}, "spare_wheat": 0, "spare_carrot": 0, "spare_str": 0, "credit": 0}'
new = '{"step": -1, "tiles": {}, "spare_wheat": 0, "spare_carrot": 0, "spare_str": 0, "credit": 0, "credit_tom": 0, "spare_tom": 0, "tom_bought": 0}'
assert src.count(old) == 1
src = src.replace(old, new)

# --- 3. the tomato yield model, injected before _ca_wheat_total ---
old = "def _ca_wheat_total(obs):"
new = '''def _ca_tom_path(planted, visits):
    """Banked TOMATO units for a plant on ``planted`` under tape ``visits``.
    Engine: +1 unit at midnight of ages 8..11 (4 productions total, standing
    cap 4); HARVEST banks standing only at age >= 8; 2 consecutive dry days
    = weed (plant day counts, consecutive_unwatered starts at 1)."""
    water = {t // 24 for t, i, op in visits if op == "WATER"}
    kills = [t for t, i, op in visits if op in ("PLANT", "DIG", "BUILD_COOP", "BUILD_PASTURE")]
    kill_t = min(kills) if kills else 720
    harv = sorted(t for t, i, op in visits if op == "HARVEST" and t < kill_t)
    banked = standing = hi = 0
    dry = 1
    for day in range(planted, min(29, planted + 13) + 1):
        while hi < len(harv) and harv[hi] < (day + 1) * 24:
            if day - planted >= 8 and standing > 0:
                banked += standing
                standing = 0
            hi += 1
        dry = 0 if day in water else dry + 1
        if dry >= 2:
            return banked
        age = day + 1 - planted
        if 8 <= age <= 11:
            standing = min(4, standing + 1)
    return banked


def _ca_wheat_total(obs):'''
assert src.count(old) == 1
src = src.replace(old, new)

# --- 4. crop choice inside the str-swap branch ---
old = """                else:
                    if cu < 2 or cu * (p_c - _CA_DROP) - 20 <= _CA_MARGIN:
                        continue
                units[i] = ["PLANT", "CARROT"]
                seeds_c -= 1
                st["spare_carrot"] -= 1
                st["tiles"][pos] = day"""
new = """                else:
                    p_t = int(prices.get("TOMATO", 0))
                    tu = 0
                    if _CA_TOM_SWAP and day <= _CA_TOM_LAST and p_t >= 2:
                        shops_now = observation["town"].get("unlocked_shops", [])
                        n_t = sum(1 for s in shops_now if s in _CA_TOM_SHOPS)
                        n_c = 2 * sum(1 for s in shops_now if s == "PET_CAFE") + sum(
                            1 for s in shops_now if s == "FARMERS_MARKET")
                        # only OUR bought seeds — never the native's stock
                        # (note: consuming its pre-buys bricks the
                        # tape's own later tomato program via atomic-PLANT)
                        seeds_t = min(st["spare_tom"],
                                      int(priv["seeds"].get("TOMATO", 0))
                                      - sum(1 for c in units if c[:2] == ["PLANT", "TOMATO"]))
                        if seeds_t >= 1 and n_t * p_t > n_c * p_c:
                            tv = _ca_visits(observation, action, pos,
                                            min(719, (day + 14) * 24), start=step + 1)
                            tu = _ca_tom_path(day, tv)
                    if tu >= 3 and tu * (p_t - _CA_DROP) - 50 > max(0, cu) * (p_c - _CA_DROP) - 20:
                        units[i] = ["PLANT", "TOMATO"]
                        st["spare_tom"] -= 1
                        st["tiles"][pos] = day
                        st["spare_str"] += 1
                        _CA_REPORT["ca_tom_swaps"] = _CA_REPORT.get("ca_tom_swaps", 0) + 1
                        changed = True
                        continue
                    if cu < 2 or cu * (p_c - _CA_DROP) - 20 <= _CA_MARGIN:
                        continue
                units[i] = ["PLANT", "CARROT"]
                seeds_c -= 1
                st["spare_carrot"] -= 1
                st["tiles"][pos] = day"""
assert src.count(old) == 1
src = src.replace(old, new)

# --- 5. tomato seed buffer (max 4, cash-guarded) after the carrot buy block ---
old = """            if q > 0 and int(farm.get("money", 0)) >= _CA_CASH + 20 * q:
                market.append(["BUY_SEED", "CARROT", q])
                st["spare_carrot"] += q
                _CA_REPORT["ca_seed_bought"] += q
                changed = True"""
new = """            if q > 0 and int(farm.get("money", 0)) >= _CA_CASH + 20 * q:
                market.append(["BUY_SEED", "CARROT", q])
                st["spare_carrot"] += q
                _CA_REPORT["ca_seed_bought"] += q
                changed = True
        if (_CA_TOM_SWAP and str_bad and _CA_FROM <= day <= _CA_TOM_LAST
                and len(market) < 10):
            shops_now = observation["town"].get("unlocked_shops", [])
            n_t = sum(1 for s in shops_now if s in _CA_TOM_SHOPS)
            n_c = 2 * sum(1 for s in shops_now if s == "PET_CAFE") + sum(
                1 for s in shops_now if s == "FARMERS_MARKET")
            p_t = int(prices.get("TOMATO", 0))
            if n_t * p_t > n_c * p_c:
                qt = min(_CA_TOM_MAX_SEEDS - st["tom_bought"], 4 - st["spare_tom"])
                if qt > 0 and int(farm.get("money", 0)) >= _CA_CASH + 50 * qt:
                    market.append(["BUY_SEED", "TOMATO", qt])
                    st["spare_tom"] += qt
                    st["tom_bought"] += qt
                    _CA_REPORT["ca_tom_seed_bought"] = _CA_REPORT.get("ca_tom_seed_bought", 0) + qt
                    changed = True"""
assert src.count(old) == 1
src = src.replace(old, new)

# --- 6. crop-aware bookkeeping/rescue (tomato: credit on harvest, keep tile) ---
old = """        for pos, planted in list(st["tiles"].items()):
            tile = tiles[pos[1]][pos[0]]
            if not (isinstance(tile, dict) and tile.get("crop") == "CARROT" and int(tile.get("planted_day", -9)) == planted):
                st["tiles"].pop(pos, None)
                continue
            here = [i for i, p in enumerate(positions) if p == pos and i < len(units)]
            if not here:
                continue
            i = here[0]
            cmd = units[i]
            yu = int(tile.get("yield_units", 0))
            if cmd and cmd[0] == "HARVEST":
                if day - planted >= 2 and yu > 0:
                    st["credit"] += yu
                    _CA_REPORT["ca_harvested"] += yu
                    st["tiles"].pop(pos, None)
                continue
            if not _CA_RESCUE or (cmd and cmd[0] in _CA_MOVES) or day - planted < 2 or yu <= 0:
                continue"""
new = """        for pos, planted in list(st["tiles"].items()):
            tile = tiles[pos[1]][pos[0]]
            _crop = tile.get("crop") if isinstance(tile, dict) else None
            if not (_crop in ("CARROT", "TOMATO") and int(tile.get("planted_day", -9)) == planted):
                st["tiles"].pop(pos, None)
                continue
            here = [i for i, p in enumerate(positions) if p == pos and i < len(units)]
            if not here:
                continue
            i = here[0]
            cmd = units[i]
            yu = int(tile.get("yield_units", 0))
            _mat = day - planted >= (8 if _crop == "TOMATO" else 2)
            if cmd and cmd[0] == "HARVEST":
                if _mat and yu > 0:
                    st["credit_tom" if _crop == "TOMATO" else "credit"] += yu
                    _CA_REPORT["ca_harvested"] += yu
                    if _crop == "CARROT":
                        st["tiles"].pop(pos, None)
                continue
            if not _CA_RESCUE or (cmd and cmd[0] in _CA_MOVES) or not _mat or yu <= 0:
                continue
            if _crop == "TOMATO":
                if yu >= 3:
                    units[i] = ["HARVEST"]
                    st["credit_tom"] += yu
                    _CA_REPORT["ca_harvested"] += yu
                    _CA_REPORT["ca_rescues"] += 1
                    changed = True
                continue"""
assert src.count(old) == 1
src = src.replace(old, new)

# --- 7. sell credited tomatoes (clone of the carrot credit sell) ---
old = """        # 4. sell credited carrots
        if st["credit"] > 0 and p_c >= 2 and len(market) < 10:"""
new = """        # 4b. sell credited tomatoes
        if st["credit_tom"] > 0 and int(prices.get("TOMATO", 0)) >= 2 and len(market) < 10:
            _view = {"farmer": units[0], "hands": units[1:], "market": market}
            _stock = int(projected_shed(_view, FarmView(observation)).get("TOMATO", 0))
            _selling = sum(int(o[2]) for o in market if len(o) >= 3 and o[:2] == ["SELL", "TOMATO"])
            _q = min(st["credit_tom"], _stock - _selling)
            if _q > 0:
                market.insert(0, ["SELL", "TOMATO", _q])
                st["credit_tom"] -= _q
                _CA_REPORT["ca_sold"] += _q
                changed = True
        # 4. sell credited carrots
        if st["credit"] > 0 and p_c >= 2 and len(market) < 10:"""
assert src.count(old) == 1
src = src.replace(old, new)

import ast
ast.parse(src)
open(r'fork\c31.py', 'w', encoding='utf-8', newline='\n').write(src)
print(f'wrote fork/c31.py ({len(src):,} chars), syntax OK')
