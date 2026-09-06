"""Why do sheep-10 farms harvest 2.7x the strawberries off the same plant count?
Per seat: STR plant-days, WATER/FERTILIZE/HARVEST action counts, sold units,
plus daily STR plant count trace, fert state coverage, and unwatered incidents."""
import json, os, ast
from collections import Counter, defaultdict

ME = "Shane Thivaharraja"
GAMES = [105813562, 105670201, 105765358, 105660802, 105669265, 105671115, 105656155]
D = r"C:\Kaggriculture\replays\live_v54k"

tot = {"ME": Counter(), "OPP": Counter()}
str_days = {"ME": defaultdict(int), "OPP": defaultdict(int)}  # day -> plants (summed over games)
n = 0
for ep in GAMES:
    p = os.path.join(D, f"episode-{ep}-replay.json")
    if not os.path.exists(p):
        cands = [f for f in os.listdir(D) if str(ep) in f]
        p = os.path.join(D, cands[0])
    n += 1
    rep = json.load(open(p, encoding="utf-8"))
    teams = rep["info"].get("TeamNames")
    if isinstance(teams, str): teams = ast.literal_eval(teams)
    my = teams.index(ME)
    steps = rep["steps"]
    for si, s in enumerate(steps):
        day, hour = si // 24, si % 24
        farms = s[0]["observation"]["farms"]
        for who, seat in (("ME", my), ("OPP", 1 - my)):
            # noon snapshot: STR plant count + fertilized share + unwatered
            if hour == 12:
                for row in farms[seat].get("tiles", []):
                    for t in row:
                        if isinstance(t, dict) and t.get("kind") == "PLANT" and t.get("crop") == "STRAWBERRY":
                            str_days[who][day] += 1
                            tot[who]["str_plant_days"] += 1
                            if t.get("fertilized_days_left") or t.get("fertilized"):
                                tot[who]["str_fert_days"] += 1
                            if t.get("consecutive_unwatered", 0) >= 1:
                                tot[who]["str_unwatered_noon"] += 1
            a = s[seat].get("action") or {}
            for o in a.get("market") or []:
                if isinstance(o, list) and len(o) >= 3 and o[0] == "SELL" and o[1] == "STRAWBERRY":
                    tot[who]["str_sold"] += int(o[2])
                if isinstance(o, list) and len(o) >= 3 and o[0] == "BUY_SEED" and o[1] == "STRAWBERRY":
                    tot[who]["str_seed_bought"] += int(o[2])
            units = [a.get("farmer") or ["PASS"]] + list(a.get("hands") or [])
            for u in units:
                if not u: continue
                if u[0] == "WATER": tot[who]["water"] += 1
                elif u[0] == "FERTILIZE": tot[who]["fertilize"] += 1
                elif u[0] == "HARVEST": tot[who]["harvest"] += 1

print(f"n={n} games (totals /game):")
for k in ("str_plant_days", "str_fert_days", "str_unwatered_noon", "str_sold",
          "str_seed_bought", "water", "fertilize", "harvest"):
    print(f"  {k:>20}: ME {tot['ME'][k]/n:>8.1f}   OPP {tot['OPP'][k]/n:>8.1f}")
print("\nSTR plants by day (avg over games):")
print("  day: " + " ".join(f"{d:>4}" for d in range(0, 30, 2)))
print("  ME : " + " ".join(f"{str_days['ME'][d]/n:>4.0f}" for d in range(0, 30, 2)))
print("  OPP: " + " ".join(f"{str_days['OPP'][d]/n:>4.0f}" for d in range(0, 30, 2)))
