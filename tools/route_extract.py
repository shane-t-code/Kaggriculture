"""Decompress multi_route's 10 action tables and extract per-route SELL
schedules (item, day, hour, qty) -> results/decodes/route_sells.json."""
import re, json, zlib, base64, os
from collections import defaultdict

SRC = r"C:\Kaggriculture\versions\pool_kaggriculture_multi_route_farming_agent.py"
OUT = r"C:\Kaggriculture\results\decodes\route_sells.json"

src = open(SRC, encoding="utf-8").read()
tables = {}
for m in re.finditer(
        r"^(_(?:LEGACY_)?ACTIONS_\w+)\s*=\s*json\.loads\(zlib\.decompress\(base64\.b85decode\(\s*'([^']+)'",
        src, re.M | re.S):
    name, blob = m.group(1), m.group(2)
    try:
        tables[name] = json.loads(zlib.decompress(base64.b85decode(blob)))
    except Exception as e:
        print(f"FAIL {name}: {e!r}")

print(f"decoded {len(tables)} tables")
out = {}
for name, tab in tables.items():
    # figure out the structure first
    if not out:
        print(f"structure sample ({name}):", type(tab),
              (list(tab.keys())[:5] if isinstance(tab, dict) else str(tab[:1])[:200]))
    sells = defaultdict(list)     # item -> [(step, qty)]
    opening = defaultdict(int)    # BUY day 0
    def walk_orders(step, orders):
        for o in orders or []:
            if isinstance(o, list) and o:
                if o[0] == "SELL" and len(o) >= 3:
                    sells[o[1]].append((int(step), int(o[2])))
                elif o[0] in ("BUY_ANIMAL", "BUY_SEED") and int(step) < 24:
                    opening[f"{o[0][4:]}:{o[1]}"] += int(o[2]) if len(o) > 2 else 1
    if isinstance(tab, dict):
        for k, v in tab.items():
            step = int(k)
            if isinstance(v, dict):
                walk_orders(step, v.get("market"))
            elif isinstance(v, list):
                walk_orders(step, v)
    elif isinstance(tab, list):
        for step, v in enumerate(tab):
            if isinstance(v, dict):
                walk_orders(step, v.get("market"))
            elif isinstance(v, list):
                walk_orders(step, v)
    out[name] = {
        "opening_d0": dict(opening),
        "sell_totals": {it: sum(q for _, q in ss) for it, ss in sells.items()},
        "sells": {it: ss for it, ss in sells.items()},
    }

os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(out, open(OUT, "w"), indent=1)
print(f"wrote {OUT}")
for name, d in out.items():
    if name.startswith("_LEGACY"):
        continue
    tot = d["sell_totals"]
    print(f"\n{name}: opening {d['opening_d0']}")
    for it, ss in sorted(d["sells"].items()):
        days = sorted(set(s // 24 for s, _ in ss))
        print(f"   {it:>11}: {tot[it]:>4} units over days {days[:12]}{'...' if len(days) > 12 else ''}")
