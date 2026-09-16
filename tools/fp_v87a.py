"""Fingerprint for v87a premium-goods express (tuning seeds only).

Dials: first WOOL sale day + units, first MILK sale day, cash @d7 h0,
pocket premium-goods at each midnight (should drop ~0), unfed %, STR@d9,
melons sold by d11h13 (caravan intact), margin.
Usage: python tools/fp_v87a.py --cand versions/v87a.py --base versions/v84c.py \
           --opp versions/pool_band_amitesh.py --seeds 0,1,... [--procs 11]
"""
import argparse, os, sys
from collections import defaultdict
from multiprocessing import Pool

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)
PREM = ("WOOL", "MILK", "EGG")


def stats(steps, seat):
    def bank(t):
        return steps[t][seat]["observation"]["farms"][seat]["money"]
    first_wool = first_milk = None
    for t in range(len(steps) - 1):
        o0, o1 = steps[t][seat]["observation"], steps[t + 1][seat]["observation"]
        if o1["farms"][seat]["money"] <= o0["farms"][seat]["money"]:
            continue
        for g, var in (("WOOL", "fw"), ("MILK", "fm")):
            p0, p1 = o0["private"], o1["private"]
            h0 = p0["shed"].get(g, 0) + sum(i.get(g, 0) for i in p0["inventories"])
            h1 = p1["shed"].get(g, 0) + sum(i.get(g, 0) for i in p1["inventories"])
            if h1 < h0:
                if g == "WOOL" and first_wool is None:
                    first_wool = o0["day"]
                if g == "MILK" and first_milk is None:
                    first_milk = o0["day"]
        if first_wool is not None and first_milk is not None:
            break
    # avg premium units in pockets at midnight over d4-20
    pk = 0.0
    for day in range(4, 21):
        t = min(day * 24 + 23, len(steps) - 1)
        p = steps[t][seat]["observation"]["private"]
        pk += sum(sum(i.get(g, 0) for g in PREM) for i in p["inventories"]) / 17
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
    o9 = steps[min(9 * 24, len(steps) - 1)][seat]["observation"]
    str9 = sum(1 for row in o9["farms"][seat]["tiles"] for x in row
               if isinstance(x, dict) and x.get("crop") == "STRAWBERRY")
    sold = 0
    for t in range(10 * 24, min(11 * 24 + 13, len(steps) - 1)):
        p0 = steps[t][seat]["observation"]["private"]
        p1 = steps[t + 1][seat]["observation"]["private"]
        h0 = p0["shed"].get("MELON", 0) + sum(i.get("MELON", 0) for i in p0["inventories"])
        h1 = p1["shed"].get("MELON", 0) + sum(i.get("MELON", 0) for i in p1["inventories"])
        if h1 < h0:
            sold += h0 - h1
    return dict(fw=first_wool, fm=first_milk, cash7=bank(min(7 * 24, len(steps) - 1)),
                pk=pk, unfed=100 * unfed / max(1, tot), str9=str9, sold11=sold)


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
    print(f"{'seed':>4s} | {'1stWOOLd':>9s} {'1stMILKd':>9s} {'cash@d7':>13s} "
          f"{'pocketPrem':>11s} {'unfed%':>10s} {'STR@d9':>8s} {'sold11':>10s} {'margin':>17s}")
    def n(v):
        return -1 if v is None else v
    for s in seeds:
        c, b = cand[s], base[s]
        print(f"{s:4d} | {n(b['fw']):3d}->{n(c['fw']):3d} {n(b['fm']):3d}->{n(c['fm']):3d} "
              f"{b['cash7']:5,.0f}->{c['cash7']:5,.0f} {b['pk']:4.1f}->{c['pk']:4.1f} "
              f"{b['unfed']:4.1f}->{c['unfed']:4.1f} {b['str9']:3d}->{c['str9']:3d} "
              f"{b['sold11']:4d}->{c['sold11']:4d} "
              f"{b['bank']-b['opp_bank']:+7,.0f}->{c['bank']-c['opp_bank']:+7,.0f}")


if __name__ == "__main__":
    main()
