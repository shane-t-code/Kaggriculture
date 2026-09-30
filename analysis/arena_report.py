# ARENA REPORT — our agent vs the top-10 team it replaced, same world.
import json, glob, sys
from collections import defaultdict
from pathlib import Path
label = sys.argv[1] if len(sys.argv) > 1 else "dtrw"
A = Path(r"C:\Kaggriculture\work\build_a\arena")
DEC = Path(r"C:\Kaggriculture\work\\review12\decoded")
rows = [json.loads(l) for f in A.glob(f"rows_{label}_*.jsonl") for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]
bad = [r for r in rows if r.get("error")]
rows = [r for r in rows if not r.get("error")]
print(f"games {len(rows)}  errors {len(bad)}  non-DONE {sum(1 for r in rows if any('DONE' not in s for s in r['statuses']))}")
n = len(rows)
w = sum(r["margin"] > 0 for r in rows); l = sum(r["margin"] < 0 for r in rows)
rw = sum(r["ref_margin"] > 0 for r in rows)
print(f"\nOUR RECORD vs the top-10 tapes: W{w}-L{l}-T{n-w-l}   (the replaced top-10 teams went W{rw}-L{n-rw} in those same games)")
print(f"mean margin: ours {sum(r['margin'] for r in rows)/n:+,.0f}   theirs {sum(r['ref_margin'] for r in rows)/n:+,.0f}")
print(f"mean bank:   ours {sum(r['our_bank'] for r in rows)/n:,.0f}   theirs (same seat/world) {sum(r['ref_bank'] for r in rows)/n:,.0f}   gap {sum(r['our_bank']-r['ref_bank'] for r in rows)/n:+,.0f}")
gaps = sorted(r["our_bank"] - r["ref_bank"] for r in rows)
print(f"gap distribution: worst {gaps[0]:+,.0f}  25% {gaps[n//4]:+,.0f}  median {gaps[n//2]:+,.0f}  75% {gaps[3*n//4]:+,.0f}  best {gaps[-1]:+,.0f}   (we out-bank them in {sum(g>0 for g in gaps)}/{n})")
print(f"opponent tape bank: in our run {sum(r['opp_bank_run'] for r in rows)/n:,.0f} vs original {sum(r['opp_bank_orig'] for r in rows)/n:,.0f}  (how much we HELP/HURT the opponent)")

print("\nBANK BY DAY (mean): day  ours  theirs  gap")
for d in ("6","9","12","15","18","21","24","27"):
    o = sum(r["our_curve"][d]["bank"] for r in rows)/n; t = sum(r["ref_curve"][d]["bank"] for r in rows)/n
    print(f"   d{d:>2}  {o:>9,.0f}  {t:>9,.0f}  {o-t:>+9,.0f}")
print("\nFARM CENSUS (mean) ours / theirs")
for d in ("6","9","12","15","18","24"):
    line = f"   d{d:>2} "
    for k in ("STRAWBERRY","WHEAT","TOMATO","MELON","CARROT","SHEEP","COW","GOOSE","QUADS","HANDS"):
        o = sum(r["our_curve"][d]["census"].get(k,0) for r in rows)/n; t = sum(r["ref_curve"][d]["census"].get(k,0) for r in rows)/n
        line += f"{k[:4]} {o:4.1f}/{t:4.1f}  "
    print(line)

# product revenue: ours from run ledger; theirs from 's decoded replay ledgers
ours = defaultdict(float); theirs = defaultdict(float); ours_n = defaultdict(float); theirs_n = defaultdict(float); joined = 0
PH = ((0,9),(10,15),(16,23),(24,29))
for r in rows:
    p = DEC / f"ep_{r['episode']}.json.summary.json"
    if not p.exists(): continue
    d = json.load(open(p, encoding="utf-8"))
    pl = next((x for x in d["players"] if x["seat"] == r["seat"]), None)
    if not pl: continue
    joined += 1
    for k, v in r["our_sales"].items():
        item, ph = k.split(":")
        if ph.startswith("n"): ours_n[(item, int(ph[1:]))] += v
        else: ours[(item, int(ph))] += v
    for k, v in pl["ledger"].items():
        day, op, item = k.split(":")
        if op != "SELL": continue
        ph = next(i for i,(a,b) in enumerate(PH) if a <= int(day) <= b)
        theirs[(item, ph)] += v[1]; theirs_n[(item, ph)] += v[0]
print(f"\nSALES PER GAME (mean over {joined} joined games): product | ours $ (units @avg) | theirs $ (units @avg) | gap")
for item in ("STRAWBERRY","MILK","WOOL","WHEAT","EGG","TOMATO","CARROT","MELON","FERTILIZER"):
    o = sum(ours[(item,p)] for p in range(4))/joined; t = sum(theirs[(item,p)] for p in range(4))/joined
    on = sum(ours_n[(item,p)] for p in range(4))/joined; tn = sum(theirs_n[(item,p)] for p in range(4))/joined
    print(f"   {item:10} ours {o:>8,.0f} ({on:5.0f}u @{o/on if on else 0:5.0f})   theirs {t:>8,.0f} ({tn:5.0f}u @{t/tn if tn else 0:5.0f})   gap {o-t:>+8,.0f}")
    print("        by phase d0-9/d10-15/d16-23/d24-29: ours " + " ".join(f"{ours[(item,p)]/joined:>7,.0f}" for p in range(4)) + "  | theirs " + " ".join(f"{theirs[(item,p)]/joined:>7,.0f}" for p in range(4)))
# by team replaced
bt = defaultdict(list)
for r in rows: bt[r["ref_team"]].append(r)
print("\nBY TEAM REPLACED: team | games | our W-L vs their opponent | their W-L | bank gap")
for t, v in sorted(bt.items(), key=lambda kv: -len(kv[1])):
    if len(v) < 3: continue
    print(f"   {t[:24]:24} {len(v):3}  ours W{sum(x['margin']>0 for x in v)}-L{sum(x['margin']<0 for x in v)}  theirs W{sum(x['ref_margin']>0 for x in v)}-L{sum(x['ref_margin']<0 for x in v)}  gap {sum(x['our_bank']-x['ref_bank'] for x in v)/len(v):+,.0f}")
# by shop class
def cls(sh):
    s = set(sh[:3])
    return "yarn-early" if "YARN_STORE" in s else "pizza/FM-early" if s & {"PIZZA_SHOP","FARMERS_MARKET"} else "berry/other"
bc = defaultdict(list)
for r in rows: bc[cls(r["shops"])].append(r)
print("\nBY WORLD TYPE (first 3 shops):")
for k, v in bc.items():
    print(f"   {k:16} {len(v):3} games  ours W{sum(x['margin']>0 for x in v)}-L{sum(x['margin']<0 for x in v)}  bank gap {sum(x['our_bank']-x['ref_bank'] for x in v)/len(v):+,.0f}")
