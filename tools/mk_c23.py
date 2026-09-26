"""Build fork/c23*.py = cha22 + carrot-program mechanisms .

Mechanism A (_CA_FEED_BUYOUT): when the feed guard blocks a profitable
wheat->carrot swap, buy replacement feed wheat (shed/cash-guarded) instead
of refusing the swap.
Mechanism B (_CA_STR_SWAP): swap planned strawberry plants to carrot ONLY
in worlds with zero strawberry-demanding shops (public info at plant time).
Both behind flags; variants: c23a (both), c23f (buyout only), c23s (str only).
"""
import sys

src = open(r'external\cha22_main.py', encoding='utf-8').read()

# --- 1. dials ---
old = "_CA_RESCUE = True"
new = """_CA_RESCUE = True
_CA_FEED_BUYOUT = True
_CA_STR_SWAP = True
_CA_STR_SHOPS = ("BRUNCH_SPOT", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP", "FARMERS_MARKET")"""
assert src.count(old) == 1
src = src.replace(old, new)

# --- 2. state init: add spare_str ---
old = '{"step": -1, "tiles": {}, "spare_wheat": 0, "spare_carrot": 0, "credit": 0}'
new = '{"step": -1, "tiles": {}, "spare_wheat": 0, "spare_carrot": 0, "spare_str": 0, "credit": 0}'
assert src.count(old) == 1
src = src.replace(old, new)

# --- 3. the swap section ---
old = """        # 2. swaps
        pays_now = 3 * (p_c - _CA_DROP) - 20 > 4 * p_w - 10 + _CA_MARGIN
        if _CA_FROM <= day <= _CA_TO and pays_now:
            seeds_c = min(st["spare_carrot"],
                          int(priv["seeds"].get("CARROT", 0)) - sum(1 for c in units if c[:2] == ["PLANT", "CARROT"]))
            wheat_ok = None
            for i, cmd in enumerate(units):
                if cmd[:2] != ["PLANT", "WHEAT"] or i >= len(positions) or seeds_c <= 0:
                    continue
                pos = positions[i]
                if tiles[pos[1]][pos[0]] is not None:
                    continue
                if wheat_ok is None:
                    wheat_ok = _ca_wheat_total(observation) >= _ca_feed_need(seat, step, _CA_FEED_DAYS)
                if not wheat_ok:
                    _CA_REPORT["ca_feed_block"] += 1
                    break
                visits = _ca_visits(observation, action, pos, (day + 6) * 24, start=step + 1)
                wu, _, _ = _ca_yield_path("WHEAT", day, visits)
                ch, cr, _ = _ca_yield_path("CARROT", day, visits)
                cu = max(ch, cr if _CA_RESCUE else 0)
                if cu * (p_c - _CA_DROP) - 20 > wu * p_w - 10 + _CA_MARGIN:
                    units[i] = ["PLANT", "CARROT"]
                    seeds_c -= 1
                    st["spare_carrot"] -= 1
                    st["tiles"][pos] = day
                    st["spare_wheat"] += 1
                    _CA_REPORT["ca_swaps"] += 1
                    changed = True"""
new = """        # 2. swaps
        pays_now = 3 * (p_c - _CA_DROP) - 20 > 4 * p_w - 10 + _CA_MARGIN
        str_bad = (_CA_STR_SWAP and p_c >= 35 and
                   not any(s in _CA_STR_SHOPS for s in observation["town"].get("unlocked_shops", [])))
        if _CA_FROM <= day <= _CA_TO and (pays_now or str_bad):
            seeds_c = min(st["spare_carrot"],
                          int(priv["seeds"].get("CARROT", 0)) - sum(1 for c in units if c[:2] == ["PLANT", "CARROT"]))
            wheat_ok = None
            for i, cmd in enumerate(units):
                is_w = pays_now and cmd[:2] == ["PLANT", "WHEAT"]
                is_s = str_bad and cmd[:2] == ["PLANT", "STRAWBERRY"]
                if not (is_w or is_s) or i >= len(positions) or seeds_c <= 0:
                    continue
                pos = positions[i]
                if tiles[pos[1]][pos[0]] is not None:
                    continue
                topup = 0
                if is_w:
                    if wheat_ok is None:
                        wheat_ok = _ca_wheat_total(observation) >= _ca_feed_need(seat, step, _CA_FEED_DAYS)
                    if not wheat_ok:
                        if not _CA_FEED_BUYOUT:
                            _CA_REPORT["ca_feed_block"] += 1
                            break
                        topup = 6 * (p_w + 10)
                visits = _ca_visits(observation, action, pos, (day + 6) * 24, start=step + 1)
                ch, cr, _ = _ca_yield_path("CARROT", day, visits)
                cu = max(ch, cr if _CA_RESCUE else 0)
                if is_w:
                    wu, _, _ = _ca_yield_path("WHEAT", day, visits)
                    if cu * (p_c - _CA_DROP) - 20 - topup <= wu * p_w - 10 + _CA_MARGIN:
                        continue
                    if topup:
                        if (len(market) >= MAX_ORDERS
                                or int(farm.get("money", 0)) < _CA_CASH + topup):
                            _CA_REPORT["ca_feed_block"] += 1
                            break
                        _view = {"farmer": units[0], "hands": units[1:], "market": market}
                        if sum(projected_shed(_view, FarmView(observation)).values()) + 6 > 94:
                            _CA_REPORT["ca_feed_block"] += 1
                            break
                        market.append(["BUY_PRODUCT", "WHEAT", 6])
                        _CA_REPORT["ca_feed_buyout"] = _CA_REPORT.get("ca_feed_buyout", 0) + 1
                        wheat_ok = True
                else:
                    if cu < 2 or cu * (p_c - _CA_DROP) - 20 <= _CA_MARGIN:
                        continue
                units[i] = ["PLANT", "CARROT"]
                seeds_c -= 1
                st["spare_carrot"] -= 1
                st["tiles"][pos] = day
                if is_w:
                    st["spare_wheat"] += 1
                    _CA_REPORT["ca_swaps"] += 1
                else:
                    st["spare_str"] += 1
                    _CA_REPORT["ca_str_swaps"] = _CA_REPORT.get("ca_str_swaps", 0) + 1
                changed = True"""
assert src.count(old) == 1
src = src.replace(old, new)

# --- 4. seed-cut filter: also cancel planned STRAWBERRY seed buys vs spare_str ---
old = """            if len(o) >= 3 and o[0] == "BUY_SEED" and o[1] in ("WHEAT", "CARROT"):
                key = "spare_wheat" if o[1] == "WHEAT" else "spare_carrot\""""
new = """            if len(o) >= 3 and o[0] == "BUY_SEED" and o[1] in ("WHEAT", "CARROT", "STRAWBERRY"):
                key = {"WHEAT": "spare_wheat", "CARROT": "spare_carrot", "STRAWBERRY": "spare_str"}[o[1]]"""
assert src.count(old) == 1
src = src.replace(old, new)

# --- 5. carrot seed buying: also under str_bad, with a deeper buffer there ---
old = 'if _CA_FROM <= day <= _CA_TO - 1 and pays_now and len(market) < 10:'
new = 'if _CA_FROM <= day <= _CA_TO - 1 and (pays_now or str_bad) and len(market) < 10:'
assert src.count(old) == 1
src = src.replace(old, new)

old = '            q = _CA_BUFFER - have - buying'
new = '            q = (_CA_BUFFER * 2 if str_bad else _CA_BUFFER) - have - buying'
assert src.count(old) == 1
src = src.replace(old, new)

variants = {
    r'fork\c23a.py': {},
    r'fork\c23f.py': {'_CA_STR_SWAP = True': '_CA_STR_SWAP = False'},
    r'fork\c23s.py': {'_CA_FEED_BUYOUT = True': '_CA_FEED_BUYOUT = False'},
}
for path, flips in variants.items():
    out = src
    for o, n in flips.items():
        assert out.count(o) == 1
        out = out.replace(o, n)
    open(path, 'w', encoding='utf-8', newline='\n').write(out)
    print(f'wrote {path} ({len(out):,} chars)')
