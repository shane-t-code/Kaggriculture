#!/usr/bin/env python3
"""wheat_ledger.py — did the opponent's wheat BUY_PRODUCT churn actually profit?
Tracks, per game: wheat units bought (at posted price), wheat units sold (at
posted price), feed consumed (inferred: bought+harvested-sold-held), and the
cash ledger of the position.  Prices are posted-price approximations (engine
fills marginally, so buys cost a bit more / sells earn a bit less at size).

Usage: python tools/wheat_ledger.py <dir> <ep> [<ep>...]
"""
import json, os, sys, ast

ME = "Shane Thivaharraja"


def ledger(path):
    rep = json.load(open(path, encoding="utf-8"))
    teams = rep["info"].get("TeamNames")
    if isinstance(teams, str):
        teams = ast.literal_eval(teams)
    my = teams.index(ME)
    steps = rep["steps"]
    print(f"\n===== ep{rep['info'].get('EpisodeId')} opp={teams[1-my]} =====")
    for who, seat in (("OPP", 1 - my), ("US", my)):
        buy_u = buy_cost = sell_u = sell_rev = 0
        buy_days, sell_days = {}, {}
        for si in range(len(steps) - 1):
            day = si // 24
            a = steps[si + 1][seat].get("action") or {}
            px = (steps[si][0]["observation"]["market"].get("prices") or {}).get("WHEAT", 0)
            for o in a.get("market") or []:
                if not isinstance(o, list) or len(o) < 2:
                    continue
                q = int(o[2]) if len(o) > 2 else 1
                if o[0] == "BUY_PRODUCT" and o[1] == "WHEAT":
                    buy_u += q; buy_cost += q * px
                    buy_days[day] = buy_days.get(day, 0) + q
                elif o[0] == "SELL" and o[1] == "WHEAT":
                    sell_u += q; sell_rev += q * px
                    sell_days[day] = sell_days.get(day, 0) + q
        avg_b = buy_cost / buy_u if buy_u else 0
        avg_s = sell_rev / sell_u if sell_u else 0
        print(f"  {who}: bought {buy_u:,}u @avg ${avg_b:.0f} (${buy_cost:,.0f})   "
              f"sold {sell_u:,}u @avg ${avg_s:.0f} (${sell_rev:,.0f})   "
              f"net units {sell_u - buy_u:+,} net cash {sell_rev - buy_cost:+,.0f}")
        print(f"       buy days:  {dict(sorted(buy_days.items()))}")
        print(f"       sell days: {dict(sorted(sell_days.items()))}")


if __name__ == "__main__":
    d = sys.argv[1]
    for ep in sys.argv[2:]:
        cands = [f for f in os.listdir(d) if str(ep) in f]
        if cands:
            ledger(os.path.join(d, cands[0]))
        else:
            print("missing", ep)
