"""v87b/v88a live transfer battery.

Per game: opponent, rating, margin, first WOOL/MILK sale day, avg premium
units in pockets at midnight (d4-20), floor-sell units (price<=3) by good,
STR tiles @d9/@d24.  Summary: band records, transfer dials vs local
predictions (wool d6, milk d8, pocketPrem ~2-4, band margins).
Usage: python tools/live_v88_check.py <replay_dir> <lb_csv>
"""
import json, glob, os, sys, csv
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ME = "Shane Thivaharraja"
PREM = ("WOOL", "MILK", "EGG")


def hold(o, g):
    p = o["private"]
    return p["shed"].get(g, 0) + sum(i.get(g, 0) for i in p["inventories"])


def main():
    d, lbcsv = sys.argv[1], sys.argv[2]
    lb = {}
    for r in csv.reader(open(lbcsv, encoding="utf-8")):
        try:
            lb[r[2]] = float(r[4])
        except (ValueError, IndexError):
            pass
    rows = []
    for f in sorted(glob.glob(os.path.join(d, "*.json"))):
        try:
            blob = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        steps = blob.get("steps") or []
        if len(steps) < 700:
            continue
        names = blob["info"]["TeamNames"]
        if ME not in names:
            continue
        me = names.index(ME)
        opp = 1 - me
        oname = names[opp]
        orating = lb.get(oname)
        margin = (blob["rewards"][me] or 0) - (blob["rewards"][opp] or 0)
        fw = fm = None
        floor = defaultdict(int)
        for t in range(len(steps) - 1):
            o0 = steps[t][me]["observation"]
            o1 = steps[t + 1][me]["observation"]
            if o1["farms"][me]["money"] <= o0["farms"][me]["money"]:
                continue
            px = o0["market"]["prices"]
            for g in ("WOOL", "MILK", "STRAWBERRY", "MELON", "WHEAT", "FERTILIZER"):
                drop = hold(o0, g) - hold(o1, g)
                if drop > 0:
                    if g == "WOOL" and fw is None:
                        fw = o0["day"]
                    if g == "MILK" and fm is None:
                        fm = o0["day"]
                    if px.get(g, 99) <= 3:
                        floor[g] += drop
        pk = 0.0
        for day in range(4, 21):
            t = min(day * 24 + 23, len(steps) - 1)
            p = steps[t][me]["observation"]["private"]
            pk += sum(sum(i.get(g, 0) for g in PREM) for i in p["inventories"]) / 17
        o24 = steps[min(24 * 24, len(steps) - 1)][me]["observation"]
        str24 = sum(1 for row in o24["farms"][me]["tiles"] for x in row
                    if isinstance(x, dict) and x.get("crop") == "STRAWBERRY")
        o9 = steps[min(9 * 24, len(steps) - 1)][me]["observation"]
        str9 = sum(1 for row in o9["farms"][me]["tiles"] for x in row
                   if isinstance(x, dict) and x.get("crop") == "STRAWBERRY")
        rows.append(dict(opp=oname, rating=orating, margin=margin, fw=fw, fm=fm,
                         pk=pk, floor=dict(floor), str9=str9, str24=str24))
    rows.sort(key=lambda r: (r["rating"] is None, r["rating"] or 0))
    print(f"=== {len(rows)} games ===")
    for r in rows:
        rt = f"{r['rating']:.0f}" if r["rating"] else "?"
        fl = " ".join(f"{g[:3]}:{n}" for g, n in r["floor"].items() if n)
        print(f"{r['opp'][:22]:22s} {rt:>5s} {r['margin']:+9,.0f}  wool_d{r['fw']} milk_d{r['fm']}  "
              f"pkt{r['pk']:4.1f}  STR@d9 {r['str9']:2d} @d24 {r['str24']:2d}  floor[{fl}]")
    bands = [(0, 600), (600, 756), (756, 900), (900, 1200), (1200, 9999)]
    print("\nBAND RECORD:")
    for lo, hi in bands:
        g = [r for r in rows if r["rating"] and lo <= r["rating"] < hi]
        w = sum(1 for r in g if r["margin"] > 0)
        if g:
            mm = sum(r["margin"] for r in g) / len(g)
            print(f"  {lo}-{hi}: {w}W-{len(g)-w}L  mean margin {mm:+,.0f}")
    known = [r for r in rows if r["fw"] is not None]
    print(f"\nTRANSFER DIALS (predicted: wool d6, milk d8, pocket ~2-4):")
    print(f"  first wool sale day mean: {sum(r['fw'] for r in known)/len(known):.1f}")
    known_m = [r for r in rows if r["fm"] is not None]
    print(f"  first milk sale day mean: {sum(r['fm'] for r in known_m)/len(known_m):.1f}")
    print(f"  pocket premium @midnight mean: {sum(r['pk'] for r in rows)/len(rows):.1f}")
    print(f"  STR@d9 mean: {sum(r['str9'] for r in rows)/len(rows):.1f}  (v83a live was ~7-10)")
    tot_floor = defaultdict(int)
    for r in rows:
        for g, n in r["floor"].items():
            tot_floor[g] += n
    print(f"  floor sells/game: " + " ".join(f"{g}:{n/len(rows):.1f}" for g, n in tot_floor.items()))


if __name__ == "__main__":
    main()
