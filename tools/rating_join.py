"""Join live_decode records to leaderboard ratings: where does the rating bleed?"""
import json, csv, glob, statistics, sys
from collections import defaultdict

DECODE = sys.argv[1] if len(sys.argv) > 1 else r"C:\Kaggriculture\live_decode3.jsonl"
LB = sorted(glob.glob(r"C:\Kaggriculture\results\leaderboards\kaggriculture-publicleaderboard*.csv"))[-1]  # newest

lb = {}
for r in csv.DictReader(open(LB, encoding="utf-8-sig")):
    lb[r["TeamName"]] = float(r["Score"])

recs = [json.loads(l) for l in open(DECODE, encoding="utf-8")]
MY = 756.7

for sub in sorted({r["sub"] for r in recs}):
    rs = [r for r in recs if r["sub"] == sub]
    n = len(rs); w = sum(1 for r in rs if r["win"])
    banks = [r["my_bank"] for r in rs if r["my_bank"] is not None]
    print(f"\n===== {sub}: {n} eps, {w}W-{n-w}L ({w/max(1,n):.0%}) | my bank med {statistics.median(banks):,.0f} p10 {sorted(banks)[len(banks)//10]:,.0f} p90 {sorted(banks)[len(banks)*9//10]:,.0f} sd {statistics.pstdev(banks):,.0f}")
    # bucket by opponent rating
    buckets = defaultdict(lambda: [0, 0, []])
    unknown = 0
    for r in rs:
        sc = lb.get(r["opp_name"])
        if sc is None:
            unknown += 1
            continue
        b = ("<600" if sc < 600 else "600-756" if sc < MY else "756-900" if sc < 900
             else "900-1200" if sc < 1200 else "1200+")
        buckets[b][0] += r["win"]
        buckets[b][1] += 1
        buckets[b][2].append((sc, r["win"], r["margin"], r["episode"], r["opp_name"]))
    for b in ("<600", "600-756", "756-900", "900-1200", "1200+"):
        if b in buckets:
            w2, n2, det = buckets[b]
            print(f"  vs {b:>8}: {w2}W-{n2-w2}L  ({n2} games)")
    if unknown:
        print(f"  ({unknown} opponents not on leaderboard file)")
    # THE BLEED: losses to opponents rated below us
    print("  -- LOSSES to lower/equal-rated opponents (the rating bleed):")
    for r in sorted(rs, key=lambda r: r["margin"]):
        sc = lb.get(r["opp_name"])
        if not r["win"] and not r.get("tie") and sc is not None and sc <= MY + 50:
            o12 = r["opp12"]; an = "".join(f"{s[0]}{c}" for s, c in sorted(o12["animals"].items()))
            cr = "".join(f"{c[0]}{v}" for c, v in sorted(o12["crops"].items()) if v)
            print(f"    ep{r['episode']} opp {r['opp_name'][:22]:22} ({sc:6.0f}) "
                  f"margin {r['margin']:+9,.0f} my {r['my_bank']:>8,.0f} div_d{r['div_day']} "
                  f"opp12[{an}|{cr}]")
    # wins vs higher rated (what we do right)
    hi_w = [(lb.get(r["opp_name"]), r) for r in rs if r["win"] and lb.get(r["opp_name"], 0) > MY + 50]
    print(f"  -- wins vs higher-rated: {len(hi_w)}")
    for sc, r in sorted(hi_w, key=lambda x: x[0], reverse=True)[:8]:
        print(f"    ep{r['episode']} beat {r['opp_name'][:22]:22} ({sc:6.0f}) margin {r['margin']:+9,.0f}")
