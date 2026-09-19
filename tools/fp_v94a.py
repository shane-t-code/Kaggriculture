"""Fingerprint for v94a — the full-plan port (tuning seeds only).

One dial per organ, cand vs base, same seed, same opponent:
  strN@d14/24 (cap 33 lock; base ~40), oddSTR% (parity cohort),
  wheat@d14/18/24 (engine 20-25 sustained; base collapses),
  hands@d12h12 (13 vs 12 — h12: hands expire at midnight),
  geese@d13 (4 vs 0), carrot@d26 (>0 vs ~0),
  fertApps + onTick% (throughput at volume, efficiency held),
  unfed% (labor sanity), margin.
Usage: python tools/fp_v94a.py --cand main.py --base versions/v93d.py \
           --opp versions/pool_band_amitesh.py --seeds 7,8 [--procs 4]
"""
import argparse, os, sys
from multiprocessing import Pool

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)


def crop_n(o, seat, crop, want_animal=None):
    n = 0
    for row in o["farms"][seat]["tiles"]:
        for t in row:
            if not isinstance(t, dict):
                continue
            if crop is not None and t.get("crop") == crop:
                n += 1
            if want_animal is not None and t.get("animal") == want_animal:
                n += 1
    return n


def stats(steps, seat):
    def obs(t):
        return steps[min(t, len(steps) - 1)][seat]["observation"]

    o14, o18, o24, o26 = obs(14 * 24 + 12), obs(18 * 24 + 12), obs(24 * 24 + 12), obs(26 * 24 + 12)
    str14, str24 = crop_n(o14, seat, "STRAWBERRY"), crop_n(o24, seat, "STRAWBERRY")
    whe14, whe18, whe24 = (crop_n(o14, seat, "WHEAT"), crop_n(o18, seat, "WHEAT"),
                           crop_n(o24, seat, "WHEAT"))
    car26 = crop_n(o26, seat, "CARROT")
    geese13 = crop_n(obs(13 * 24 + 12), seat, None, want_animal="GOOSE")
    hands12 = len(obs(12 * 24 + 12)["farms"][seat].get("hands", []))
    odd = tot_p = 0
    for row in o14["farms"][seat]["tiles"]:
        for t in row:
            if isinstance(t, dict) and t.get("crop") == "STRAWBERRY":
                tot_p += 1
                if t.get("planted_day", 0) % 2 == 1:
                    odd += 1
    # fert apps on STR + on-tick% (fertilized_until_day rises; dsf parity)
    apps = on_tick = 0
    prev = {}
    for t in range(len(steps) - 1):
        o = steps[t][seat]["observation"]
        d = o["day"]
        for y, row in enumerate(o["farms"][seat]["tiles"]):
            for x, tile in enumerate(row):
                if not (isinstance(tile, dict) and tile.get("crop") == "STRAWBERRY"):
                    prev.pop((x, y), None)
                    continue
                fud = tile.get("fertilized_until_day", -1)
                if (x, y) in prev and fud > prev[(x, y)]:
                    apps += 1
                    dsf = (d + 1) - tile.get("planted_day", 0) - 10
                    if dsf >= 0 and dsf % 2 == 0:
                        on_tick += 1
                prev[(x, y)] = fud
    unfed = tot = 0
    for day in range(1, 29):
        o = obs(day * 24 + 23)
        for row in o["farms"][seat]["tiles"]:
            for t in row:
                if isinstance(t, dict) and t.get("animal"):
                    tot += 1
                    if not t.get("fed_today", True):
                        unfed += 1
    return dict(str14=str14, str24=str24, oddp=100 * odd / max(1, tot_p),
                whe14=whe14, whe18=whe18, whe24=whe24, car26=car26,
                geese=geese13, hands=hands12, apps=apps,
                ontick=100 * on_tick / max(1, apps),
                unfed=100 * unfed / max(1, tot))


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
    ap.add_argument("--procs", type=int, default=4)
    args = ap.parse_args()
    seeds = [int(s) for s in args.seeds.split(",")]
    jobs = ([(args.cand, args.opp, s) for s in seeds]
            + [(args.base, args.opp, s) for s in seeds])
    with Pool(args.procs) as pool:
        rows = pool.map(run_one, jobs)
    cand = {r["seed"]: r for r in rows[:len(seeds)]}
    base = {r["seed"]: r for r in rows[len(seeds):]}
    for s in seeds:
        c, b = cand[s], base[s]
        print(f"seed {s}:  (base->cand)")
        print(f"  STR@d14 {b['str14']}->{c['str14']}  @d24 {b['str24']}->{c['str24']}"
              f"  odd-planted% {b['oddp']:.0f}->{c['oddp']:.0f}")
        print(f"  WHEAT@d14 {b['whe14']}->{c['whe14']}  @d18 {b['whe18']}->{c['whe18']}"
              f"  @d24 {b['whe24']}->{c['whe24']}")
        print(f"  hands@d12 {b['hands']}->{c['hands']}  geese@d13 {b['geese']}->{c['geese']}"
              f"  carrot@d26 {b['car26']}->{c['car26']}")
        print(f"  fertApps {b['apps']}->{c['apps']}  onTick% {b['ontick']:.0f}->{c['ontick']:.0f}"
              f"  unfed% {b['unfed']:.1f}->{c['unfed']:.1f}")
        print(f"  own bank {b['bank']:,.0f}->{c['bank']:,.0f}"
              f"  margin {b['bank']-b['opp_bank']:+,.0f}->{c['bank']-c['opp_bank']:+,.0f}")


if __name__ == "__main__":
    main()
