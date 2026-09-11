"""str_timing.py — per-day STRAWBERRY production vs selling for our seat .
Distinguishes 'grown late' from 'sold late' in the d15-21 loss week.
For each day: harvested-into-stock (shed+inventory delta + sells), stock at day end,
units sold that day. Usage: python tools/str_timing.py <replay_dir> <ep_id...>"""
import json, os, sys, ast

ME = "Shane Thivaharraja"
ITEM = "STRAWBERRY"

d = sys.argv[1]
eps = sys.argv[2:]

for ep in eps:
    cands = [f for f in os.listdir(d) if ep in f and f.endswith(".json")]
    if not cands:
        print(ep, "not found"); continue
    rep = json.load(open(os.path.join(d, cands[0]), encoding="utf-8"))
    teams = (rep.get("info") or {}).get("TeamNames")
    if isinstance(teams, str):
        teams = ast.literal_eval(teams)
    if teams and ME in teams:
        my = teams.index(ME)
    else:
        my = 0  # local replay: seat 0 = agent A
        teams = ["seat0(A)", "seat1(B)"]
    steps = rep["steps"]
    print(f"\n== ep {ep} vs {teams[1-my]} ==")
    print("day | stock@end | sold | tiles(STR planted)")
    prev_stock = 0
    for day in range(30):
        end_si = min(day * 24 + 23, len(steps) - 1)
        obs = steps[end_si][my]["observation"]
        priv = obs["private"]
        stock = priv["shed"].get(ITEM, 0) + sum(inv.get(ITEM, 0) for inv in priv["inventories"])
        sold = 0
        for si in range(day * 24, min((day + 1) * 24, len(steps))):
            a = steps[si][my].get("action") or {}
            for o in (a.get("market") or []):
                if isinstance(o, list) and len(o) >= 3 and o[0] == "SELL" and o[1] == ITEM:
                    try: sold += int(o[2])
                    except Exception: pass
        farm = steps[end_si][0]["observation"]["farms"][my]
        ntiles = sum(1 for row in farm["tiles"] for t in row
                     if isinstance(t, dict) and t.get("kind") == "PLANT" and t.get("crop") == ITEM)
        harvested = max(0, stock - prev_stock) + sold  # approx: new units this day
        print(f" {day:>2} |   {stock:>4}    | {sold:>4} | {ntiles:>3}   (harv~{harvested})")
        prev_stock = stock
