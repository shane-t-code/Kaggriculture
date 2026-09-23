#!/usr/bin/env python3
"""adapt_decode.py — what does an adaptive top agent's policy respond to?

Compares ONE team's play across several of its replays, aligned by day:
  farm layer : crop-tile mix, animals, hands, money  (does the BUILD adapt?)
  market layer: SELL orders by item/day vs that game's shop draws + prices
                (does the SELLING adapt?)
Prints per-game daily tables and a cross-game divergence summary: the first
day each layer separates between game pairs, plus sells-vs-shops evidence.

Usage: python tools/adapt_decode.py <name_substring> <replay.json> [...]
"""
import json, sys, os
from collections import Counter, defaultdict

TPD = 24
KEY_ITEMS = ["WHEAT", "CARROT", "STRAWBERRY", "TOMATO", "MELON",
             "MILK", "WOOL", "EGG", "FERTILIZER"]


def find_pid(info, name):
    for i, a in enumerate(info.get("Agents") or []):
        if isinstance(a, dict) and name.lower() in str(a.get("Name", "")).lower():
            return i
    return None


def day_profile(replay, pid):
    steps = replay["steps"]
    prof = {}
    sells = defaultdict(Counter)
    for t in range(len(steps) - 1):
        day, hour = t // TPD, t % TPD
        act = steps[t + 1][pid].get("action") or {}
        if isinstance(act, dict):
            for o in (act.get("market") or []):
                if isinstance(o, list) and o and o[0] == "SELL" and len(o) > 1:
                    try:
                        sells[day][o[1]] += int(o[2]) if len(o) > 2 else 1
                    except (TypeError, ValueError):
                        sells[day][o[1]] += 1
        if hour != 12:
            continue
        obs = steps[t][0]["observation"]
        farm = obs["farms"][pid]
        crops = Counter()
        animals = Counter()
        for row in farm["tiles"]:
            for tl in row:
                if isinstance(tl, dict):
                    if tl.get("kind") == "PLANT":
                        crops[tl.get("crop")] += 1
                    elif tl.get("kind") in ("COOP", "PASTURE") and tl.get("animal"):
                        animals[tl["animal"]] += 1
        prof[day] = {
            "money": farm.get("money", 0),
            "crops": dict(crops),
            "animals": dict(animals),
            "hands": len(farm.get("hands", [])),
            "shops": tuple(obs["town"]["unlocked_shops"]),
            "prices": {k: obs["market"]["prices"].get(k) for k in KEY_ITEMS
                       if isinstance(obs["market"].get("prices"), dict)},
        }
    return prof, sells


def farm_dist(p, q):
    d = 0
    for c in set(p["crops"]) | set(q["crops"]):
        d += abs(p["crops"].get(c, 0) - q["crops"].get(c, 0))
    for a in set(p["animals"]) | set(q["animals"]):
        d += abs(p["animals"].get(a, 0) - q["animals"].get(a, 0))
    return d


def main():
    name = sys.argv[1]
    games = []
    for path in sys.argv[2:]:
        rep = json.load(open(path))
        pid = find_pid(rep.get("info", {}), name)
        if pid is None:
            print(f"skip {path}: no seat matching {name!r}")
            continue
        prof, sells = day_profile(rep, pid)
        games.append((os.path.basename(path), prof, sells))
        rew = [rep["steps"][-1][i]["reward"] for i in range(2)]
        print(f"loaded {os.path.basename(path)} seat{pid} final {rew[pid]:,.0f}")

    # per-game daily table
    for gname, prof, sells in games:
        print(f"\n--- {gname} ---")
        print("day money crops | animals | hands | new-shop | sells")
        prev_shops = ()
        for day in sorted(prof):
            p = prof[day]
            new = [s for s in p["shops"] if len(p["shops"]) > len(prev_shops)
                   and p["shops"][:len(prev_shops)] == prev_shops
                   for s in p["shops"][len(prev_shops):]]
            prev_shops = p["shops"]
            cr = " ".join(f"{c[:3]}{n}" for c, n in sorted(p["crops"].items()))
            an = " ".join(f"{a[:3]}{n}" for a, n in sorted(p["animals"].items()))
            sl = " ".join(f"{i[:4]}{n}" for i, n in sorted(sells[day].items()))
            print(f"d{day:>2} {p['money']:>7,.0f} {cr:<34} | {an:<18} | "
                  f"h{p['hands']} | {','.join(new) or '-':<14} | {sl}")

    # cross-game farm divergence
    if len(games) >= 2:
        print("\n=== CROSS-GAME FARM-LAYER DISTANCE (tile-mix+animals L1) ===")
        for i in range(len(games)):
            for j in range(i + 1, len(games)):
                na, pa, _ = games[i]
                nb, pb, _ = games[j]
                row = []
                for day in range(0, 30, 2):
                    if day in pa and day in pb:
                        row.append(f"d{day}:{farm_dist(pa[day], pb[day])}")
                print(f"{na[8:17]} vs {nb[8:17]}: " + " ".join(row))

        print("\n=== SELLS (d10+) vs SHOP DRAWS per game ===")
        for gname, prof, sells in games:
            tot = Counter()
            for day, c in sells.items():
                if day >= 10:
                    tot.update(c)
            last_day = max(prof)
            print(f"{gname[8:17]}: shops={list(prof[last_day]['shops'])}")
            print(f"   sells d10+: {dict(tot)}")


if __name__ == "__main__":
    main()
