"""killer_detect.py — offline validation of the killer-family detector .

The detector must run INSIDE the agent from public obs only. Candidate signal,
evaluated at end of day D (D = 5..8) from the opponent's public farm:
    cows == 2 and sheep == 2 and melon_tiles >= MEL_MIN
The family plants 12 melons early and holds exactly 2C+2S through the opening.

This script replays every live episode, computes the signal day by day, and
scores it against the ground-truth label (opp_open startswith C2S2G0+mel12,
measured at d16 by live_decode). Reports: detection day histogram, precision,
recall, and every false positive/negative with its opening string.

Usage: python tools/killer_detect.py
"""
import json, os, ast, glob
from collections import Counter

ME = "Shane Thivaharraja"
MEL_MIN = 12          # melon tiles required (they plant 12; some harvested later)
DAYS = (4, 5, 6, 7, 8)

def farm_counts(farm):
    animals = Counter()
    mel = 0
    for row in farm["tiles"]:
        for t in row:
            if not isinstance(t, dict):
                continue
            k = t.get("kind")
            if k in ("COOP", "PASTURE") and t.get("animal"):
                animals[t["animal"]] += 1
            elif k == "PLANT" and t.get("crop") == "MELON":
                mel += 1
    return animals, mel

def main():
    truth = {}   # epid -> (is_family, opp_open, res, margin, opp, rating)
    for label in ("v67c_sep12", "v70c_sep12"):
        for l in open(f"results/decodes/live_decode_{label}.jsonl", encoding="utf-8"):
            r = json.loads(l)
            truth[r["ep"]] = (r["opp_open"].startswith("C2S2G0+mel12"), r["opp_open"],
                              r["res"], r["margin"], r["opp"], r["opp_rating"])

    rows = []
    for d in ("replays/live_v67c", "replays/live_v70c"):
        for f in sorted(glob.glob(os.path.join(d, "*.json"))):
            rep = json.load(open(f, encoding="utf-8"))
            epid = rep["info"].get("EpisodeId")
            if epid not in truth:
                continue
            teams = rep["info"].get("TeamNames")
            if isinstance(teams, str):
                teams = ast.literal_eval(teams)
            my = teams.index(ME)
            steps = rep["steps"]
            det_day = None
            per_day = {}
            for day in DAYS:
                si = min(day * 24 + 23, len(steps) - 1)
                farm = steps[si][0]["observation"]["farms"][1 - my]
                animals, mel = farm_counts(farm)
                sig = mel >= MEL_MIN
                per_day[day] = (animals.get("COW", 0), animals.get("SHEEP", 0), mel, sig)
                if sig and det_day is None:
                    det_day = day
            rows.append((epid, truth[epid], det_day, per_day))

    fam = [r for r in rows if r[1][0]]
    oth = [r for r in rows if not r[1][0]]
    tp = [r for r in fam if r[2] is not None]
    fn = [r for r in fam if r[2] is None]
    fp = [r for r in oth if r[2] is not None]
    print(f"{len(rows)} episodes | family {len(fam)}, others {len(oth)}")
    print(f"detector (C==2 & S==2 & melon_tiles>={MEL_MIN}, days {DAYS[0]}-{DAYS[-1]}):")
    print(f"  recall  {len(tp)}/{len(fam)}  precision {len(tp)}/{len(tp)+len(fp)}")
    print(f"  detection day histogram: {Counter(r[2] for r in tp)}")
    if fn:
        print("\n  FALSE NEGATIVES (family, undetected):")
        for epid, t, _, pd in fn:
            print(f"    ep{epid} vs {t[4][:20]} open {t[1]}  per-day {pd}")
    if fp:
        print("\n  FALSE POSITIVES (non-family, detected):")
        for epid, t, dd, pd in fp:
            print(f"    ep{epid} vs {t[4][:20]} ({t[5]}) open {t[1]} res {t[2]} {t[3]:+,.0f} det d{dd}")

if __name__ == "__main__":
    main()
