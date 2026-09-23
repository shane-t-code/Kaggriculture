#!/usr/bin/env python3
"""adapt_audit.py — full adaptive-dimension audit of one seat in a replay.

Per game/seat, one compact row per dimension:
  crop tile-days by crop (allocation shape), animal mix, goose use,
  floor sells (SELL orders while that item's market price <= 2) vs real
  sells, land-buy days, hires/day mean, first/last plant days.
Run over many games of the same agent → the VARIATION across worlds is the
adaptivity; compare our tape's variation with the top-10's.

Usage: python tools/adapt_audit.py <name_or_seat> <replay.json> [...]
"""
import json, sys, os
from collections import Counter, defaultdict

TPD = 24


def find_pid(info, name):
    if name in ("0", "1"):
        return int(name)
    for i, a in enumerate(info.get("Agents") or []):
        if isinstance(a, dict) and name.lower() in str(a.get("Name", "")).lower():
            return i
    return None


def audit(path, who):
    rep = json.load(open(path))
    pid = find_pid(rep.get("info", {}), who)
    if pid is None:
        print(f"{os.path.basename(path)}: no seat for {who!r}")
        return
    steps = rep["steps"]
    rew = [steps[-1][i]["reward"] for i in range(2)]
    crop_days = Counter()
    animals_final = {}
    hires = 0
    land_days = []
    floor_sells = Counter()
    ok_sells = Counter()
    plant_days = []
    for t in range(len(steps) - 1):
        day, hour = t // TPD, t % TPD
        obs = steps[t][0]["observation"]
        farm = obs["farms"][pid]
        if hour == 12:
            for row in farm["tiles"]:
                for tl in row:
                    if isinstance(tl, dict) and tl.get("kind") == "PLANT":
                        crop_days[tl.get("crop")] += 1
            animals_final = Counter()
            for row in farm["tiles"]:
                for tl in row:
                    if isinstance(tl, dict) and tl.get("animal"):
                        animals_final[tl["animal"]] += 1
        act = steps[t + 1][pid].get("action") or {}
        if not isinstance(act, dict):
            continue
        prices = obs["market"].get("prices") or {}
        for o in (act.get("market") or []):
            if not (isinstance(o, list) and o):
                continue
            if o[0] == "SELL" and len(o) > 1:
                qty = o[2] if len(o) > 2 else 1
                try:
                    qty = int(qty)
                except (TypeError, ValueError):
                    qty = 1
                qty = min(qty, 100)
                if prices.get(o[1], 99) <= 2:
                    floor_sells[o[1]] += qty
                else:
                    ok_sells[o[1]] += qty
            elif o[0] == "BUY_LAND":
                land_days.append(day)
            elif o[0] == "HIRE":
                hires += 1
        for a in [act.get("farmer")] + list(act.get("hands") or []):
            if isinstance(a, list) and a:
                if a[0] == "PLANT":
                    plant_days.append(day)
    total_floor = sum(floor_sells.values())
    name = os.path.basename(path).replace("episode-", "").replace("-replay.json", "")
    cd = " ".join(f"{c[:3]}{n}" for c, n in crop_days.most_common())
    an = " ".join(f"{a[:3]}{n}" for a, n in sorted(animals_final.items()))
    fl = " ".join(f"{i[:4]}{n}" for i, n in floor_sells.most_common(4))
    print(f"{name[:24]:<24} {'W' if rew[pid]>rew[1-pid] else 'L' if rew[pid]<rew[1-pid] else 'T'}"
          f" {rew[pid]:>8,.0f} | crop-days {cd:<38} | {an:<16} | "
          f"land d{land_days} | hires {hires} | FLOOR {total_floor:>3} [{fl}]"
          f" | lastP d{max(plant_days) if plant_days else '-'}")


def main():
    who = sys.argv[1]
    for p in sys.argv[2:]:
        audit(p, who)


if __name__ == "__main__":
    main()
