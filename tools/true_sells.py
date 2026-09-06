"""Ground-truth sell decode: market inventory deltas attributed to the seat that
ordered the sell that step. Floor sales add no inventory (engine) so this slightly
undercounts $1-floor dumping, which is ~zero revenue anyway.
Also: realized revenue per phase from money deltas (positive deltas = sell income)."""
import json, os, ast, sys
from collections import Counter, defaultdict

ME = "Shane Thivaharraja"
GAMES = [int(x) for x in sys.argv[2:]] if len(sys.argv) > 2 else \
    [105813562, 105670201, 105765358, 105660802, 105669265, 105671115, 105656155]
D = sys.argv[1] if len(sys.argv) > 1 else r"C:\Kaggriculture\replays\live_v54k"

units = {"ME": defaultdict(Counter), "OPP": defaultdict(Counter)}
rev = {"ME": Counter(), "OPP": Counter()}   # phase -> positive money delta sum
amb = Counter()
n = 0
for ep in GAMES:
    p = os.path.join(D, f"episode-{ep}-replay.json")
    if not os.path.exists(p):
        cands = [f for f in os.listdir(D) if str(ep) in f]
        if not cands: continue
        p = os.path.join(D, cands[0])
    n += 1
    rep = json.load(open(p, encoding="utf-8"))
    teams = rep["info"].get("TeamNames")
    if isinstance(teams, str): teams = ast.literal_eval(teams)
    my = teams.index(ME)
    steps = rep["steps"]
    for si in range(len(steps) - 1):
        day = si // 24
        ph = ("d0-4" if day < 5 else "d5-9" if day < 10 else "d10-14" if day < 15
              else "d15-21" if day < 22 else "d22-29")
        inv0 = steps[si][0]["observation"]["market"]["inventory"]
        inv1 = steps[si + 1][0]["observation"]["market"]["inventory"]
        sellers = defaultdict(list)   # item -> [who]
        for who, seat in (("ME", my), ("OPP", 1 - my)):
            a = steps[si][seat].get("action") or {}
            for o in a.get("market") or []:
                if isinstance(o, list) and len(o) >= 3 and o[0] == "SELL":
                    sellers[o[1]].append(who)
        for item, whos in sellers.items():
            d = inv1.get(item, 0) - inv0.get(item, 0)
            if d <= 0:
                continue
            if len(set(whos)) == 1:
                units[whos[0]][ph][item] += d
            else:
                amb[item] += d
        # realized revenue: positive money delta this step
        farms0 = steps[si][0]["observation"]["farms"]
        farms1 = steps[si + 1][0]["observation"]["farms"]
        for who, seat in (("ME", my), ("OPP", 1 - my)):
            dm = farms1[seat].get("money", 0) - farms0[seat].get("money", 0)
            if dm > 0:
                rev[who][ph] += dm

print(f"n={n} games. EXECUTED units (market-inventory ground truth, per game avg):")
for ph in ("d0-4", "d5-9", "d10-14", "d15-21", "d22-29"):
    print(f"\n  {ph}:   [positive-money-delta income: ME {rev['ME'][ph]/n:>9,.0f}  OPP {rev['OPP'][ph]/n:>9,.0f}]")
    items = sorted(set(units["ME"][ph]) | set(units["OPP"][ph]))
    for it in items:
        print(f"    {it:>11}: ME {units['ME'][ph][it]/n:>7.1f}   OPP {units['OPP'][ph][it]/n:>7.1f}")
if amb:
    print("\nambiguous (both sold same item same step, unattributed):", dict(amb))
