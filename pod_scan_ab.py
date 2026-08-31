#!/usr/bin/env python3
"""Pod job: large-scale validation of v31b's dead-town branch.

Phase 1 — scan seeds for towns that fire the day-9 latch (main-vs-main,
240 steps ≈ 10 days, reads the 3-draw shop list, applies the v31b rule).
Phase 2 — full paired A/B (v31b vs main.py, both seats, 720 steps) on every
fired seed.  Prints per-seed margins and the W-L-T total.

Usage:
    python3.13 pod_scan_ab.py --scan-seeds 2000 --procs 32
"""
import argparse
import os
import sys
from multiprocessing import Pool

SHOP_DEMAND = {
    "BAKERY":         ("EGG", "WHEAT"),
    "PIZZA_SHOP":     ("MILK", "TOMATO", "WHEAT"),
    "BRUNCH_SPOT":    ("EGG", "WHEAT", "STRAWBERRY"),
    "YARN_STORE":     ("WOOL",),
    "ICE_CREAM_SHOP": ("STRAWBERRY", "MILK", "WHEAT"),
    "PET_CAFE":       ("CARROT",),
    "SMOOTHIE_SHOP":  ("STRAWBERRY", "MILK"),
    "FARMERS_MARKET": ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY"),
}


def _drain(item, shops):
    d = 0 if item == "FERTILIZER" else 1
    for s in shops:
        prods = SHOP_DEMAND.get(s, ())
        if item in prods:
            d += 6 * (2 if len(prods) == 1 else 1)
    return d


def _scan_one(seed):
    from kaggle_environments import make
    env = make("kaggriculture",
               configuration={"episodeSteps": 240, "seed": seed}, debug=False)
    env.run(["main.py", "main.py"])
    shops = (env.steps[-1][0]["observation"].get("town", {}) or {}) \
        .get("unlocked_shops", []) or []
    fire = (_drain("STRAWBERRY", shops) <= 1 and _drain("MILK", shops) <= 1
            and _drain("WHEAT", shops) >= 7)
    return seed, fire, tuple(shops)


def _ab_one(job):
    seed, seat = job
    from kaggle_environments import make
    env = make("kaggriculture",
               configuration={"episodeSteps": 720, "seed": seed}, debug=False)
    pair = ["versions/v31b.py", "main.py"] if seat == 0 else ["main.py", "versions/v31b.py"]
    env.run(pair)
    final = env.steps[-1]
    ok = all(s.status == "DONE" for s in final)
    a = final[0].reward if seat == 0 else final[1].reward
    b = final[1].reward if seat == 0 else final[0].reward
    return seed, seat, a, b, ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan-seeds", type=int, default=2000)
    ap.add_argument("--start-seed", type=int, default=0)
    ap.add_argument("--procs", type=int, default=32)
    args = ap.parse_args()

    seeds = list(range(args.start_seed, args.start_seed + args.scan_seeds))
    with Pool(args.procs) as pool:
        scanned = pool.map(_scan_one, seeds, chunksize=8)
    fired = [s for s, f, _ in scanned if f]
    print(f"SCAN: fired {len(fired)}/{len(seeds)} seeds "
          f"({100.0 * len(fired) / max(1, len(seeds)):.1f}%)", flush=True)
    print(f"FIRED SEEDS: {fired}", flush=True)

    jobs = [(s, seat) for s in fired for seat in (0, 1)]
    with Pool(args.procs) as pool:
        results = pool.map(_ab_one, jobs, chunksize=1)

    w = l = t = bad = 0
    margins = []
    by_seed = {}
    for seed, seat, a, b, ok in results:
        if not ok:
            bad += 1
            continue
        m = a - b
        margins.append(m)
        by_seed.setdefault(seed, []).append(m)
        if m > 0:
            w += 1
        elif m < 0:
            l += 1
        else:
            t += 1
    for seed in sorted(by_seed):
        ms = by_seed[seed]
        print(f"  seed {seed:>4}: " + "  ".join(f"{m:>+9,.0f}" for m in ms),
              flush=True)
    n = max(1, len(margins))
    mean = sum(margins) / n
    pos_seeds = sum(1 for ms in by_seed.values() if sum(ms) > 0)
    print(f"\nFIRED A/B TOTAL: {w}W - {l}L - {t}T  (n={len(margins)}, "
          f"crashed={bad})")
    print(f"mean margin {mean:+,.0f}   net-positive towns "
          f"{pos_seeds}/{len(by_seed)}")


if __name__ == "__main__":
    main()
