# LINEAGE — which top teams open exactly like our family, and which
# replay one fixed opening?  Pure table work on the public dataset
# georgymamarin/kaggriculture-episodes (no games, no seeds, no replays).
#   stream_hNN = sha256 of a seat's action stream through turn NN.
#   Same h48 on two seats = byte-identical actions through turn 48.
# DECISION RULE (fixed before the data was looked at):
#   "same family as us"  = a submission whose MODAL h48 equals our modal h48.
#   "fixed opening"      = one h48 value covers >= 80% of that submission's games.
#   Donor-compatible     = top-30 team, newest submission, same family as us.
# Usage: python -X utf8 lineage.py
import csv
import os
import glob
import sys
from collections import Counter, defaultdict

DS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "kaggriculture-episodes")
LB = sorted(glob.glob(os.path.join(os.path.dirname(DS), "leaderboard", "*.csv")))[-1]
OUR_TEAM = os.environ.get("TEAM_NAME", "Shane Thivaharraja")  # team name as shown on the leaderboard
CUTS = ["stream_h24", "stream_h48", "stream_h100", "stream_h136", "stream_h200"]


def main():
    teams = {}
    name2id = {}
    with open(DS + r"\teams.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            teams[r["team_id"]] = r["team_name"]
            name2id[r["team_name"]] = r["team_id"]
    # episode -> per seat (sub, team, rating, bank, time)
    seat = {}
    with open(DS + r"\episodes.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["type"] != "EPISODE_TYPE_PUBLIC":
                continue
            for s in ("0", "1"):
                seat[(r["episode_id"], s)] = (
                    r["sub_" + s], r["team_" + s], r["rating_" + s],
                    r["bank_" + s], r["create_time"])
    by_sub = defaultdict(list)
    with open(DS + r"\stream_hashes.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            k = (r["episode_id"], r["seat"])
            if k not in seat:
                continue
            sub, team, rating, bank, t = seat[k]
            by_sub[sub].append((t, team, r, bank, rating))
    sub_team = {s: v[0][1] for s, v in by_sub.items()}
    team_subs = defaultdict(list)
    for s, tm in sub_team.items():
        newest = max(x[0] for x in by_sub[s])
        team_subs[tm].append((newest, s))

    def modal(sub, cut):
        c = Counter(x[2][cut] for x in by_sub[sub] if x[2][cut])
        if not c:
            return None, 0.0, 0
        v, n = c.most_common(1)[0]
        return v, n / sum(c.values()), len(c)

    # our family fingerprints (every submission of ours in the dataset)
    ours = name2id.get(OUR_TEAM)
    print(f"our team id {ours}; our submissions in dataset:")
    our_h = defaultdict(Counter)
    for newest, s in sorted(team_subs.get(ours, []))[-8:]:
        row = [f"  sub {s} games {len(by_sub[s]):4d} newest {newest[:16]}"]
        for cut in CUTS:
            v, share, nd = modal(s, cut)
            row.append(f"{cut[7:]}:{(v or '-')[:6]}({share:.0%},{nd})")
            if v:
                our_h[cut][v] += 1
        print(" ".join(row))
    fam = {cut: set(c) for cut, c in our_h.items()}
    print("our family hashes:", {k[7:]: [x[:6] for x in v]
                                 for k, v in fam.items()})

    # leaderboard top 30
    top = []
    with open(LB, encoding="utf-8-sig") as f:
        rd = csv.DictReader(f)
        cols = rd.fieldnames
        for r in rd:
            top.append(r)
    print("LB columns:", cols)
    namecol = [c for c in cols if "name" in c.lower()][0]
    scorecol = [c for c in cols if "score" in c.lower()][0]
    top.sort(key=lambda r: -float(r[scorecol] or 0))
    print(f"\n{'rk':>3} {'team':28} {'LB':>7} | newest sub, games, "
          f"h24 h48 h100 h136 (modal share, distinct) | family?")
    for i, r in enumerate(top[:40], 1):
        nm = r[namecol]
        tid = name2id.get(nm)
        if tid is None or tid not in team_subs:
            print(f"{i:>3} {nm[:28]:28} {float(r[scorecol]):7.1f} | not in dataset")
            continue
        subs = sorted(team_subs[tid])[-2:]
        for newest, s in subs[::-1]:
            g = by_sub[s]
            parts = []
            same = []
            for cut in CUTS[:4]:
                v, share, nd = modal(s, cut)
                parts.append(f"{(v or '-')[:6]}({share:.0%},{nd})")
                same.append("Y" if v in fam.get(cut, ()) else "n")
            banks = sorted(float(x[3] or 0) for x in g)
            rat = [float(x[4] or 0) for x in g]
            print(f"{i:>3} {nm[:28]:28} {float(r[scorecol]):7.1f} | {s} "
                  f"n={len(g):3d} {newest[5:16]} " + " ".join(parts)
                  + f" | fam {''.join(same)} medbank "
                  f"{banks[len(banks)//2]:,.0f} maxrat {max(rat):.0f}")

    # who else (any rating) shares OUR h48 and is rated high?
    print("\nHIGHEST-RATED submissions sharing our h24 AND h48 family:")
    rows = []
    for s, g in by_sub.items():
        if len(g) < 8:
            continue
        v24, s24, _ = modal(s, "stream_h24")
        v48, s48, _ = modal(s, "stream_h48")
        if v24 in fam.get("stream_h24", ()) and v48 in fam.get("stream_h48", ()):
            last = sorted(g)[-10:]
            rr = sum(float(x[4] or 0) for x in last) / len(last)
            bk = sorted(float(x[3] or 0) for x in g)
            rows.append((rr, s, teams.get(sub_team[s], sub_team[s]), len(g),
                         bk[len(bk)//2], max(x[0] for x in g)[:16]))
    rows.sort(reverse=True)
    print(f"  {len(rows)} submissions share our opening through turn 48")
    for rr, s, nm, n, bk, newest in rows[:30]:
        print(f"  rating~{rr:7.1f} sub {s} {nm[:28]:28} n={n:3d} "
              f"medbank {bk:,.0f} newest {newest}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
