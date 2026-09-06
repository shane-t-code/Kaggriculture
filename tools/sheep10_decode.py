"""Decode the sheep-10 family (v54k's new band killer): per-phase sells, land,
fert applies, care counts, and daily bank trajectory gap vs us."""
import json, os, ast
from collections import Counter, defaultdict

ME = "Shane Thivaharraja"
# sheep-10 losses from live_decode_sep5 (C2-6 + S9-11 opp shapes)
GAMES = [105813562, 105670201, 105765358, 105660802, 105669265, 105671115, 105656155]
D = r"C:\Kaggriculture\replays\live_v54k"

sell_units = {"ME": defaultdict(Counter), "OPP": defaultdict(Counter)}
land_days = {"ME": Counter(), "OPP": Counter()}
acts = {"ME": Counter(), "OPP": Counter()}
gap_by_day = defaultdict(list)   # opp_bank - my_bank at end of day
opp_anim_day = defaultdict(list)
n = 0
for ep in GAMES:
    p = os.path.join(D, f"episode-{ep}-replay.json")
    if not os.path.exists(p):
        # try other naming
        cands = [f for f in os.listdir(D) if str(ep) in f]
        if not cands:
            print("missing", ep); continue
        p = os.path.join(D, cands[0])
    n += 1
    rep = json.load(open(p, encoding="utf-8"))
    teams = rep["info"].get("TeamNames")
    if isinstance(teams, str): teams = ast.literal_eval(teams)
    my = teams.index(ME)
    steps = rep["steps"]
    for si, s in enumerate(steps):
        day = si // 24
        win = ("d0-4" if day < 5 else "d5-9" if day < 10 else "d10-14" if day < 15
               else "d15-21" if day < 22 else "d22-29")
        for who, seat in (("ME", my), ("OPP", 1 - my)):
            a = s[seat].get("action") or {}
            for o in a.get("market") or []:
                if isinstance(o, list) and len(o) >= 3 and o[0] == "SELL":
                    sell_units[who][win][o[1]] += int(o[2])
                if isinstance(o, list) and o and o[0] == "BUY_LAND":
                    land_days[who][day] += 1
            units = [a.get("farmer") or ["PASS"]] + list(a.get("hands") or [])
            for u in units:
                if u and u[0] in ("FERTILIZE", "CARE", "FEED", "PASS", "MOVE"):
                    acts[who][u[0]] += 1
        if si % 24 == 23:
            farms = s[0]["observation"]["farms"]
            gap_by_day[day].append(farms[1-my].get("money", 0) - farms[my].get("money", 0))
            na = 0
            for row in farms[1-my].get("tiles", []):
                for t in row:
                    if isinstance(t, dict) and t.get("animal"):
                        na += 1
            opp_anim_day[day].append(na)

print(f"n={n} sheep-10 loss games.  SELL units ordered (per game avg), by phase:")
for win in ("d0-4", "d5-9", "d10-14", "d15-21", "d22-29"):
    print(f"\n  {win}:")
    items = sorted(set(sell_units["ME"][win]) | set(sell_units["OPP"][win]))
    for it in items:
        print(f"    {it:>11}: ME {sell_units['ME'][win][it]/n:>7.1f}   OPP {sell_units['OPP'][win][it]/n:>7.1f}")
print("\nland buy days: ME", dict(sorted(land_days["ME"].items())), " OPP", dict(sorted(land_days["OPP"].items())))
print("acts/game:  " + "  ".join(f"{k} ME {acts['ME'][k]/n:.0f}/OPP {acts['OPP'][k]/n:.0f}"
                                 for k in ("FERTILIZE", "CARE", "FEED", "PASS", "MOVE")))
print("\nbank gap (OPP-ME) by day (avg): " +
      " ".join(f"d{d}:{sum(v)/len(v):+,.0f}" for d, v in sorted(gap_by_day.items()) if d in (4,8,12,16,20,24,29)))
print("opp animals by day (avg): " +
      " ".join(f"d{d}:{sum(v)/len(v):.1f}" for d, v in sorted(opp_anim_day.items()) if d in (2,4,6,8,10,12)))
