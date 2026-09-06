#!/usr/bin/env python3
"""mr_waves.py — build per-route executed-sell wave tables from mr_games.jsonl.

Input:  results/decodes/mr_games.jsonl (from tools/mr_decode.py)
Output: results/decodes/mr_waves.json  + a paste-ready _MR_SELLS literal on stdout.

Attribution: multi_route re-evaluates its route label EVERY step (town shops are
shared and drawn 1/3days), so a game can switch tapes mid-game.  Each executed
sell is credited to the label active at that step (from the game's route
timeline), not the final label.

A (route, item, step) entry survives into the wave table when the sell fired in
>= FIRE_FRACTION of the games where that label was active at that step, and its
median executed units >= MIN_UNITS.  Schedules are deterministic tapes; only
execution amounts vary, so medians are the honest per-game expectation.
"""
from __future__ import annotations
import json, os, statistics, sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IN = os.path.join(ROOT, "results", "decodes", "mr_games.jsonl")
OUT = os.path.join(ROOT, "results", "decodes", "mr_waves.json")

FIRE_FRACTION = 0.5
MIN_UNITS = 3

def label_at(timeline, step):
    lbl = timeline[0][1]
    for s, l in timeline:
        if s <= step:
            lbl = l
        else:
            break
    return lbl

def main():
    games = [json.loads(l) for l in open(IN, encoding="utf-8")]
    print(f"{len(games)} games")

    # exposure[label][step] = number of games where label active at step
    exposure = defaultdict(lambda: defaultdict(int))
    # obs[(label, item, step)] = list of executed units (one per firing game)
    obs = defaultdict(list)
    route_games = defaultdict(int)

    for g in games:
        tl = g["route_timeline"]
        route_games[g["final_route"]] += 1
        # exposure per step: walk the timeline
        for i, (s, lbl) in enumerate(tl):
            end = tl[i + 1][0] if i + 1 < len(tl) else 719
            for step in range(s, end):
                exposure[lbl][step] += 1
        for item, pairs in g["sells"].items():
            for step, units in pairs:
                obs[(label_at(tl, step), item, step)].append(units)

    print("games per final route:", dict(route_games))
    switches = sum(1 for g in games if len(g["route_timeline"]) > 1)
    print(f"games with mid-game route switch: {switches}")

    tables = defaultdict(lambda: defaultdict(list))  # label -> item -> [(step, med)]
    for (lbl, item, step), units in sorted(obs.items(), key=lambda kv: (kv[0][0], kv[0][1], kv[0][2])):
        n_exposed = exposure[lbl][step]
        if n_exposed == 0:
            continue
        fire = len(units) / n_exposed
        med = int(statistics.median(units))
        if fire >= FIRE_FRACTION and med >= MIN_UNITS:
            tables[lbl][item].append((step, med))

    out = {lbl: {it: v for it, v in items.items()} for lbl, items in tables.items()}
    json.dump(out, open(OUT, "w", encoding="utf-8"), indent=1)
    print(f"wrote {OUT}\n")

    # paste-ready literal, yarn routes first
    order = ["6c12s_4q_first_yarn", "6c12s_4q_second_yarn", "6c8s_3q",
             "10c4s_3q", "8c6s_3q"]
    print("_MR_SELLS = {")
    for lbl in order:
        if lbl not in tables:
            continue
        print(f'    "{lbl}": {{')
        for item in sorted(tables[lbl]):
            waves = ", ".join(f"({s},{u})" for s, u in tables[lbl][item])
            tot = sum(u for _, u in tables[lbl][item])
            print(f'        "{item}": ({waves}),  # {tot} u')
        print("    },")
    print("}")

    # summary: executed totals per route/item (medians, from table)
    print("\nper-route executed totals (from wave tables):")
    for lbl in order:
        if lbl not in tables:
            continue
        tots = {it: sum(u for _, u in v) for it, v in tables[lbl].items()}
        print(f"  {lbl} (n={route_games.get(lbl, 0)}): {tots}")

if __name__ == "__main__":
    main()
