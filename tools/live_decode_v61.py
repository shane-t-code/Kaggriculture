#!/usr/bin/env python3
"""Full live decode for the v61e/v58c submissions .

Per episode: opponent + rating (fresh leaderboard join), W/L, banks,
net d15-21 flows, opponent opening fingerprint, and OUR live mechanism
checks: milk-boom fired (cows>9 + milk shops), unfed animal-nights %,
hire-last partition present, STR wind-down.  Writes JSONL + prints
aggregate tables (band records, means, loss anatomy).

Usage: python tools/live_decode_v61.py <replay_dir> <label> [<lb_csv>]
"""
import json, glob, os, sys, ast, csv, statistics
from collections import Counter

ME = "Shane Thivaharraja"
MILK_SHOPS = ("PIZZA_SHOP", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP")


def money(steps, si, seat):
    return steps[si][0]["observation"]["farms"][seat].get("money", 0)


def count_tiles(farm, key):
    n = 0
    for row in farm.get("tiles") or []:
        for t in row or []:
            if isinstance(t, dict) and t.get(key):
                n += 1
    return n


def animal_counts(farm):
    c = Counter()
    for row in farm.get("tiles") or []:
        for t in row or []:
            if isinstance(t, dict) and t.get("animal"):
                c[t["animal"]] += 1
    return c


def decode_ep(path, ratings):
    rep = json.load(open(path, encoding="utf-8"))
    teams = rep["info"].get("TeamNames")
    if isinstance(teams, str):
        teams = ast.literal_eval(teams)
    if ME not in teams:
        return None
    my = teams.index(ME)
    opp_name = teams[1 - my]
    steps = rep["steps"]
    if len(steps) < 700:
        return None
    rw = rep.get("rewards") or [s.get("reward") for s in steps[-1]]
    my_bank, opp_bank = rw[my], rw[1 - my]
    res = "W" if my_bank > opp_bank else ("L" if my_bank < opp_bank else "T")

    # town + milk shops at d12
    obs12 = steps[12 * 24][0]["observation"]
    shops = (obs12.get("town", {}) or {}).get("unlocked_shops", []) or []
    nmilk = sum(1 for s in shops if s in MILK_SHOPS)

    # our mechanism checks
    f16 = steps[16 * 24][0]["observation"]["farms"][my]
    my_cows16 = animal_counts(f16).get("COW", 0)
    boom = my_cows16 > 9

    unfed = nights = 0
    for d in range(13, 29):
        si = min(d * 24 + 23, len(steps) - 1)
        for row in steps[si][0]["observation"]["farms"][my].get("tiles") or []:
            for t in row or []:
                if isinstance(t, dict) and t.get("animal"):
                    nights += 1
                    if not t.get("fed_today"):
                        unfed += 1

    hire_mixed = hire_viol = 0
    for si in range(len(steps) - 1):
        mk = (steps[si + 1][my].get("action") or {}).get("market") or []
        ops = [o[0] for o in mk if isinstance(o, list) and o]
        if "HIRE" in ops and any(o != "HIRE" for o in ops):
            hire_mixed += 1
            if not all(o == "HIRE" for o in ops[ops.index("HIRE"):]):
                hire_viol += 1

    # net flows
    def net(seat, d0, d1):
        s0, s1 = d0 * 24, min(d1 * 24, len(steps) - 1)
        return money(steps, s1, seat) - money(steps, s0, seat)

    # opponent opening fingerprint (d2 dawn)
    fo = steps[2 * 24][0]["observation"]["farms"][1 - my]
    oa = animal_counts(fo)
    ocrops = Counter()
    for row in fo.get("tiles") or []:
        for t in row or []:
            if isinstance(t, dict) and t.get("kind") == "PLANT":
                ocrops[t.get("crop")] += 1
    open_fp = (f"C{oa.get('COW',0)}S{oa.get('SHEEP',0)}G{oa.get('GOOSE',0)}"
               f"+mel{ocrops.get('MELON',0)}whe{ocrops.get('WHEAT',0)}")

    o16 = animal_counts(steps[16 * 24][0]["observation"]["farms"][1 - my])
    return {
        "ep": rep["info"].get("EpisodeId"), "opp": opp_name,
        "opp_rating": ratings.get(opp_name), "res": res,
        "my_bank": my_bank, "opp_bank": opp_bank, "margin": my_bank - opp_bank,
        "nmilk": nmilk, "boom": boom, "my_cows16": my_cows16,
        "opp_cows16": o16.get("COW", 0),
        "unfed_pct": round(100 * unfed / max(1, nights)),
        "hire_mixed": hire_mixed, "hire_viol": hire_viol,
        "my_net_15_21": net(my, 15, 22), "opp_net_15_21": net(1 - my, 15, 22),
        "my_net_22_29": net(my, 22, 30), "opp_net_22_29": net(1 - my, 22, 30),
        "opp_open": open_fp,
    }


def main():
    rdir, label = sys.argv[1], sys.argv[2]
    lb = sys.argv[3] if len(sys.argv) > 3 else sorted(
        glob.glob("results/leaderboards/kaggriculture-publicleaderboard-*.csv"))[-1]
    ratings = {}
    for r in csv.DictReader(open(lb, encoding="utf-8")):
        ratings[r["TeamName"]] = float(r["Score"])
    rows = []
    for f in sorted(glob.glob(os.path.join(rdir, "*.json"))):
        try:
            row = decode_ep(f, ratings)
            if row:
                rows.append(row)
        except Exception as e:
            print(f"skip {os.path.basename(f)}: {type(e).__name__} {e}")
    out = f"results/decodes/live_decode_{label}.jsonl"
    with open(out, "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")

    print(f"\n===== {label}: {len(rows)} games ({out}) =====")
    w = sum(1 for r in rows if r["res"] == "W")
    l = sum(1 for r in rows if r["res"] == "L")
    print(f"record {w}W-{l}L-{len(rows)-w-l}T | mean bank {statistics.mean(r['my_bank'] for r in rows):,.0f} "
          f"| mean margin {statistics.mean(r['margin'] for r in rows):+,.0f}")

    print("\n-- band record (opponent live rating) --")
    for lo, hi in ((0, 756), (756, 900), (900, 1100), (1100, 9999)):
        sub = [r for r in rows if r["opp_rating"] is not None and lo <= r["opp_rating"] < hi]
        if not sub:
            continue
        bw = sum(1 for r in sub if r["res"] == "W")
        print(f"  {lo:>4}-{hi:<4}: {bw}W-{len(sub)-bw}L ({100*bw/len(sub):.0f}%) "
              f"med margin {statistics.median(r['margin'] for r in sub):+,.0f}")
    unrated = [r for r in rows if r["opp_rating"] is None]
    if unrated:
        print(f"  (unrated/name-miss: {len(unrated)})")

    print("\n-- mechanisms live --")
    boom_games = [r for r in rows if r["boom"]]
    bg3 = [r for r in rows if r["nmilk"] >= 3]
    print(f"  boom fired: {len(boom_games)}/{len(rows)} games "
          f"(3-milk-shop towns present: {len(bg3)})")
    for r in boom_games:
        print(f"    ep{r['ep']} vs {r['opp'][:20]:<20} ({r['opp_rating']}) {r['res']} "
              f"{r['margin']:+,.0f} cows {r['my_cows16']} vs {r['opp_cows16']} milkshops {r['nmilk']}")
    print(f"  unfed% mean {statistics.mean(r['unfed_pct'] for r in rows):.0f}% "
          f"(max {max(r['unfed_pct'] for r in rows)}%)")
    viol = sum(r["hire_viol"] for r in rows)
    print(f"  hire-last violations: {viol} across {sum(r['hire_mixed'] for r in rows)} mixed turns")

    print("\n-- net flows (means) --")
    for k in ("my_net_15_21", "opp_net_15_21", "my_net_22_29", "opp_net_22_29"):
        print(f"  {k}: {statistics.mean(r[k] for r in rows):+,.0f}")
    lsub = [r for r in rows if r["res"] == "L"]
    if lsub:
        print(f"  LOSSES d15-21: us {statistics.mean(r['my_net_15_21'] for r in lsub):+,.0f} "
              f"vs them {statistics.mean(r['opp_net_15_21'] for r in lsub):+,.0f}")
        wsub = [r for r in rows if r["res"] == "W"]
        if wsub:
            print(f"  WINS   d15-21: us {statistics.mean(r['my_net_15_21'] for r in wsub):+,.0f} "
                  f"vs them {statistics.mean(r['opp_net_15_21'] for r in wsub):+,.0f}")

    print("\n-- losses, worst first --")
    for r in sorted(lsub, key=lambda r: r["margin"])[:15]:
        print(f"  ep{r['ep']} {r['margin']:>+9,.0f} vs {r['opp'][:22]:<22} ({r['opp_rating']}) "
              f"open {r['opp_open']} oppcows16 {r['opp_cows16']} milkshops {r['nmilk']} boom {r['boom']}")


if __name__ == "__main__":
    main()
