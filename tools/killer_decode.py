#!/usr/bin/env python3
"""killer_decode.py — day-by-day build-order decode of specific opponents.

For each (replay_dir, episode) the OPPONENT gets a daily table d0-16:
purchases made that day (animals/seeds/land/hires), farm contents at day end
(animals + crops), money at day end, income that day (positive money deltas).
Then a compact phase-sell table (executed, market-delta ground truth) and the
same daily line for US in one game for contrast.

Usage: python tools/killer_decode.py <dir> <ep> [<ep> ...]
"""
import json, os, sys, ast
from collections import Counter

ME = "Shane Thivaharraja"


def tile_counts(farm):
    c = Counter()
    for row in farm.get("tiles") or []:
        for t in row or []:
            if isinstance(t, dict):
                k = t.get("animal") or (t.get("crop") if t.get("kind") == "PLANT" else None)
                if k:
                    c[k] += 1
    return c


def fmt_counts(c):
    order = ["COW", "SHEEP", "GOOSE", "STRAWBERRY", "MELON", "WHEAT", "CARROT", "TOMATO"]
    return " ".join(f"{k[:3]}{c[k]}" for k in order if c.get(k))


def decode(path, focus_me=False):
    rep = json.load(open(path, encoding="utf-8"))
    teams = rep["info"].get("TeamNames")
    if isinstance(teams, str):
        teams = ast.literal_eval(teams)
    my = teams.index(ME)
    seat = my if focus_me else 1 - my
    steps = rep["steps"]
    rw = rep.get("rewards", [0, 0])
    name = "US" if focus_me else teams[1 - my]
    print(f"\n===== ep{rep['info'].get('EpisodeId')} {name} "
          f"(final {rw[seat]:,.0f} vs {rw[1-seat]:,.0f}) =====")
    print(f"{'day':>3} {'money':>8} {'income':>7}  buys / hires  |  farm at day end")
    for d in range(17):
        buys = Counter()
        hires = 0
        income = 0
        for si in range(d * 24, min((d + 1) * 24, len(steps) - 1)):
            a = steps[si + 1][seat].get("action") or {}  # +1 offset alignment
            for o in a.get("market") or []:
                if not isinstance(o, list) or not o:
                    continue
                if o[0] in ("BUY_ANIMAL", "BUY_SEED"):
                    buys[f"{o[0][4:5]}:{o[1][:4]}"] += int(o[2]) if len(o) > 2 else 1
                elif o[0] == "BUY_LAND":
                    buys["LAND"] += 1
                elif o[0] == "BUY_PRODUCT":
                    buys[f"P:{o[1][:4]}"] += int(o[2]) if len(o) > 2 else 1
                elif o[0] == "HIRE":
                    hires += 1
            f0 = steps[si][0]["observation"]["farms"][seat].get("money", 0)
            f1 = steps[si + 1][0]["observation"]["farms"][seat].get("money", 0)
            if f1 > f0:
                income += f1 - f0
        si_end = min((d + 1) * 24 - 1, len(steps) - 1)
        farm = steps[si_end][0]["observation"]["farms"][seat]
        bstr = " ".join(f"{k}x{v}" for k, v in sorted(buys.items()))
        if hires:
            bstr += f" HIREx{hires}"
        print(f"{d:>3} {farm.get('money', 0):>8,.0f} {income:>7,.0f}  {bstr:<44} | {fmt_counts(tile_counts(farm))}")


if __name__ == "__main__":
    d = sys.argv[1]
    for ep in sys.argv[2:]:
        cands = [f for f in os.listdir(d) if str(ep) in f]
        if not cands:
            print("missing", ep)
            continue
        decode(os.path.join(d, cands[0]))
    # one US table for contrast, from the first episode
    cands = [f for f in os.listdir(d) if str(sys.argv[2]) in f]
    if cands:
        decode(os.path.join(d, cands[0]), focus_me=True)
