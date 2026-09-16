"""Fingerprint screen for v85a berry-first hardening (tuning seeds 0-99 only).

Runs candidate + baseline vs a tape on the same seeds, classifies each world
(milk shops seen by d9 / yarn / boom-eligible) and reports the mechanism dials:
STR tiles @d9, cows/sheep @d9, STR seeds+money @d9, unfed animal-days, bank.

Usage: python tools/fp_v85a.py --cand versions/v85a.py --base versions/v84c.py \
           --opp versions/pool_band_amitesh.py --seeds 0,1,2,...  [--procs 11]
"""
import argparse, json, os, sys
from collections import defaultdict
from multiprocessing import Pool

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

MILK = ("PIZZA_SHOP", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP")


def stats(steps, seat):
    o9 = steps[min(9 * 24, len(steps) - 1)][seat]["observation"]
    farm = o9["farms"][seat]
    an = defaultdict(int)
    strn = 0
    for row in farm["tiles"]:
        for t in row:
            if isinstance(t, dict):
                if t.get("animal"):
                    an[t["animal"]] += 1
                if t.get("crop") == "STRAWBERRY":
                    strn += 1
    shops9 = o9["town"]["unlocked_shops"]
    milk9 = sum(1 for s in shops9 if s in MILK)
    yarn = "YARN_STORE" in shops9
    # unfed animal-days: animal tiles with fed==False at end of any day
    unfed = tot = 0
    for day in range(1, 29):
        t = min(day * 24 + 23, len(steps) - 1)
        o = steps[t][seat]["observation"]
        for row in o["farms"][seat]["tiles"]:
            for x in row:
                if isinstance(x, dict) and x.get("animal"):
                    tot += 1
                    if not x.get("fed_today", True):
                        unfed += 1
    # sheep placed by d16 (yarn towns)
    t16 = min(16 * 24, len(steps) - 1)
    sheep16 = sum(1 for row in steps[t16][seat]["observation"]["farms"][seat]["tiles"]
                  for x in row if isinstance(x, dict) and x.get("animal") == "SHEEP")
    return dict(str9=strn, cow9=an.get("COW", 0), sheep9=an.get("SHEEP", 0),
                milk9=milk9, yarn=yarn, unfed_pct=100 * unfed / max(1, tot),
                sheep16=sheep16, money9=farm["money"])


def run_one(job):
    agent, opp, seed = job
    from run_local import play, _silence_fds
    with _silence_fds():
        ra, rb, env = play(agent, opp, seed)
    st = stats(env.steps, 0)
    st.update(seed=seed, bank=ra, opp_bank=rb)
    return st


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cand", required=True)
    ap.add_argument("--base", required=True)
    ap.add_argument("--opp", required=True)
    ap.add_argument("--seeds", required=True, help="comma list")
    ap.add_argument("--procs", type=int, default=11)
    args = ap.parse_args()
    seeds = [int(s) for s in args.seeds.split(",")]
    jobs = ([(args.cand, args.opp, s) for s in seeds]
            + [(args.base, args.opp, s) for s in seeds])
    with Pool(args.procs) as pool:
        rows = pool.map(run_one, jobs)
    cand = {r["seed"]: r for r in rows[:len(seeds)]}
    base = {r["seed"]: r for r in rows[len(seeds):]}
    print(f"{'seed':>4s} {'world':14s} | {'STR@d9':>11s} {'cow@d9':>9s} {'shp@d9':>9s} "
          f"{'shp@d16':>9s} {'unfed%':>11s} {'margin':>16s}")
    for s in seeds:
        c, b = cand[s], base[s]
        world = f"milk{b['milk9']}" + ("+yarn" if b["yarn"] else "")
        print(f"{s:4d} {world:14s} | {b['str9']:4d}->{c['str9']:4d} "
              f"{b['cow9']:3d}->{c['cow9']:3d} {b['sheep9']:3d}->{c['sheep9']:3d} "
              f"{b['sheep16']:3d}->{c['sheep16']:3d} "
              f"{b['unfed_pct']:4.1f}->{c['unfed_pct']:4.1f} "
              f"{b['bank']-b['opp_bank']:+7,.0f}->{c['bank']-c['opp_bank']:+7,.0f}")


if __name__ == "__main__":
    main()
