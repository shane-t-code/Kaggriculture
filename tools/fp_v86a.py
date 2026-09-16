"""Fingerprint screen for v86a d7 seed-cohort cash timing (tuning seeds only).

Dials: cash @d7 h0, STR tiles @d9/@d15, melon tiles @d15+@d20 (wave-2 intact),
melons sold by d11 h13 (detonation intact), unfed animal-day %, bank.
Usage: python tools/fp_v86a.py --cand versions/v86a.py --base versions/v84c.py \
           --opp versions/pool_band_amitesh.py --seeds 0,1,2,... [--procs 11]
"""
import argparse, os, sys
from collections import defaultdict
from multiprocessing import Pool

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)


def count(o, seat, crop):
    return sum(1 for row in o["farms"][seat]["tiles"] for t in row
               if isinstance(t, dict) and t.get("crop") == crop)


def stats(steps, seat):
    o7 = steps[min(7 * 24, len(steps) - 1)][seat]["observation"]
    cash7 = o7["farms"][seat]["money"]
    o9 = steps[min(9 * 24, len(steps) - 1)][seat]["observation"]
    o15 = steps[min(15 * 24, len(steps) - 1)][seat]["observation"]
    o20 = steps[min(20 * 24, len(steps) - 1)][seat]["observation"]
    # melons sold by d11 h13: holdings drop of MELON during d10-d11h13
    sold = 0
    for t in range(10 * 24, min(11 * 24 + 13, len(steps) - 1)):
        p0 = steps[t][seat]["observation"]["private"]
        p1 = steps[t + 1][seat]["observation"]["private"]
        h0 = p0["shed"].get("MELON", 0) + sum(i.get("MELON", 0) for i in p0["inventories"])
        h1 = p1["shed"].get("MELON", 0) + sum(i.get("MELON", 0) for i in p1["inventories"])
        if h1 < h0:
            sold += h0 - h1
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
    return dict(cash7=cash7, str9=count(o9, seat, "STRAWBERRY"),
                str15=count(o15, seat, "STRAWBERRY"),
                mel15=count(o15, seat, "MELON"), mel20=count(o20, seat, "MELON"),
                sold11=sold, unfed=100 * unfed / max(1, tot))


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
    ap.add_argument("--seeds", required=True)
    ap.add_argument("--procs", type=int, default=11)
    args = ap.parse_args()
    seeds = [int(s) for s in args.seeds.split(",")]
    jobs = ([(args.cand, args.opp, s) for s in seeds]
            + [(args.base, args.opp, s) for s in seeds])
    with Pool(args.procs) as pool:
        rows = pool.map(run_one, jobs)
    cand = {r["seed"]: r for r in rows[:len(seeds)]}
    base = {r["seed"]: r for r in rows[len(seeds):]}
    print(f"{'seed':>4s} | {'cash@d7':>13s} {'STR@d9':>9s} {'STR@d15':>9s} "
          f"{'MEL@d15':>9s} {'sold_d11h13':>11s} {'unfed%':>11s} {'margin':>17s}")
    for s in seeds:
        c, b = cand[s], base[s]
        print(f"{s:4d} | {b['cash7']:5,.0f}->{c['cash7']:5,.0f} "
              f"{b['str9']:3d}->{c['str9']:3d} {b['str15']:3d}->{c['str15']:3d} "
              f"{b['mel15']:3d}->{c['mel15']:3d} {b['sold11']:4d}->{c['sold11']:4d} "
              f"{b['unfed']:4.1f}->{c['unfed']:4.1f} "
              f"{b['bank']-b['opp_bank']:+7,.0f}->{c['bank']-c['opp_bank']:+7,.0f}")


if __name__ == "__main__":
    main()
