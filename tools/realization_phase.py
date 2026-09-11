"""Post-process realization jsonl: per-product breakdown of ONE phase,
ME vs OPP, split by result. Usage: python tools/realization_phase.py <jsonl> [phase]"""
import json, sys
from collections import defaultdict

path = sys.argv[1]
PH = sys.argv[2] if len(sys.argv) > 2 else "d15-21"
groups = {g: defaultdict(lambda: defaultdict(float)) for g in ("ME-W", "ME-L", "OPP-inW", "OPP-inL")}
counts = {"W": 0, "L": 0}
for line in open(path, encoding="utf-8"):
    rec = json.loads(line)
    res = "W" if (rec.get("margin") or 0) > 0 else "L"
    counts[res] += 1
    for w in ("ME", "OPP"):
        g = f"{w.replace('OPP', 'OPP-in')}{res}" if w == "OPP" else f"ME-{res}"
        for key, v in rec["acc"][w].items():
            ph, item = key.split("|")
            if ph != PH:
                continue
            for k2, val in v.items():
                groups[g][item][k2] += val

print(f"phase {PH}: {counts['W']} wins, {counts['L']} losses (per-game means)")
for g in ("ME-W", "OPP-inW", "ME-L", "OPP-inL"):
    n = max(1, counts["W"] if "W" in g else counts["L"])
    t = groups[g]
    net = sum(v["realized"] - v.get("buy_cost", 0) for v in t.values()) / n
    print(f"\n  {g}  (NET ${net:,.0f}/game)")
    for item in sorted(t, key=lambda i: -(t[i]["realized"] - t[i].get("buy_cost", 0))):
        v = t[item]
        print(f"    {item:>11}: sell {v['units']/n:>5.0f}u ${v['realized']/n:>7,.0f}"
              f"  buy ${v.get('buy_cost',0)/n:>7,.0f}"
              f"  NET ${(v['realized']-v.get('buy_cost',0))/n:>7,.0f}"
              f"  floor {v['floor']/n:>3.0f}u")
