"""Build fork/c27.py = c23s + EARLY STRAWBERRY-SWAP WINDOW .

The tape's day-5-8 strawberry wave (20 plants, native-watered same day)
harvests day 15+ into the zero-str-shop floor.  c23s's swap window starts at
day 10 and misses it.  c27 opens the STRAWBERRY swap window at day 6 (once
two shop draws are visible), wheat swaps unchanged at day 10.  Each swap also
cancels a $100 native strawberry-seed purchase via the existing seed-cut
machinery, so the early swaps are self-funding.
"""
src = open(r'fork\c23s.py', encoding='utf-8').read()
assert '_CA_STR_FROM' not in src

old = '_CA_STR_SHOPS = ("BRUNCH_SPOT", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP", "FARMERS_MARKET")'
new = '''_CA_STR_SHOPS = ("BRUNCH_SPOT", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP", "FARMERS_MARKET")
_CA_STR_FROM = 6'''
assert src.count(old) == 1
src = src.replace(old, new)

old = """        str_bad = (_CA_STR_SWAP and p_c >= 35 and
                   not any(s in _CA_STR_SHOPS for s in observation["town"].get("unlocked_shops", [])))
        if _CA_FROM <= day <= _CA_TO and (pays_now or str_bad):"""
new = """        _shops_seen = observation["town"].get("unlocked_shops", [])
        str_bad = (_CA_STR_SWAP and p_c >= 35 and len(_shops_seen) >= 2 and
                   not any(s in _CA_STR_SHOPS for s in _shops_seen))
        wheat_go = pays_now and _CA_FROM <= day <= _CA_TO
        str_go = str_bad and _CA_STR_FROM <= day <= _CA_TO
        if wheat_go or str_go:"""
assert src.count(old) == 1
src = src.replace(old, new)

old = """                is_w = pays_now and cmd[:2] == ["PLANT", "WHEAT"]
                is_s = str_bad and cmd[:2] == ["PLANT", "STRAWBERRY"]"""
new = """                is_w = wheat_go and cmd[:2] == ["PLANT", "WHEAT"]
                is_s = str_go and cmd[:2] == ["PLANT", "STRAWBERRY"]"""
assert src.count(old) == 1
src = src.replace(old, new)

old = 'if _CA_FROM <= day <= _CA_TO - 1 and (pays_now or str_bad) and len(market) < 10:'
new = 'if ((wheat_go and day <= _CA_TO - 1) or (str_go and day <= _CA_TO - 1)) and len(market) < 10:'
assert src.count(old) == 1
src = src.replace(old, new)

import ast
ast.parse(src)
open(r'fork\c27.py', 'w', encoding='utf-8', newline='\n').write(src)
print(f'wrote fork/c27.py ({len(src):,} chars), syntax OK')
