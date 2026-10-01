# SHOP DETERMINISM (many games of one submission) — one top submission, many games: is its
# farm decided by the shops seen so far?  Shops appear at steps 72, 144, 216,
# 288 ... (every 3 days, up to 8).  For every pair of games that share the
# first k shops, check whether the two farms are identical until the (k+1)th
# shop appears.  Also: how many distinct shop prefixes the games cover.
# DECISION RULE (fixed in advance): >= 80% of same-prefix pairs identical (strict) or
# >= 90% identical at census level (counts of each crop/animal, land, hands)
# => the build is a function of the shops => a tree of stored plans works.
# Usage: python -X utf8 p1_mg.py <tag> <team_name>
import ast
import gzip
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

R = Path(__file__).resolve().parents[1]


def tile_sig(t):
    if not isinstance(t, dict):
        return None
    return (t.get("kind"), t.get("crop") or t.get("animal"))


def census(fm):
    c = Counter()
    for row in fm["tiles"]:
        for t in row:
            s = tile_sig(t)
            if s and s[1]:
                c[s[1]] += 1
    return (tuple(sorted(c.items())), len(fm["unlocked_quadrants"]))


def main():
    tag, team = sys.argv[1], sys.argv[2]
    games = []
    for f in sorted((R / "replays" / tag).glob("ep_*.json.gz")):
        rep = json.load(gzip.open(f, "rt", encoding="utf-8"))
        teams = rep["info"].get("TeamNames")
        if isinstance(teams, str):
            teams = ast.literal_eval(teams)
        if team not in teams:
            continue
        s = teams.index(team)
        steps = rep["steps"]
        shops = steps[-1][0]["observation"]["town"]["unlocked_shops"]
        strict, cens = [], []
        for t in range(0, len(steps), 24):
            fm = steps[t][0]["observation"]["farms"][s]
            strict.append(json.dumps([[tile_sig(x) for x in row]
                                      for row in fm["tiles"]]
                                     + [len(fm["unlocked_quadrants"])]))
            cens.append(json.dumps(census(fm)))
        games.append((f.name[3:-8], tuple(shops), strict, cens,
                      steps[-1][s]["reward"], steps[-1][1 - s]["reward"],
                      teams[1 - s]))
    print(f"{team}: {len(games)} games; W{sum(g[4] > g[5] for g in games)}")
    for k in (1, 2, 3, 4):
        pref = Counter(g[1][:k] for g in games)
        print(f"  distinct first-{k} shop sequences: {len(pref)} "
              f"(games in the biggest: {pref.most_common(1)[0][1]})")
    # same first k shops -> farms identical (by day) until day 3(k+1)?
    for k in (0, 1, 2, 3):
        by = defaultdict(list)
        for g in games:
            by[g[1][:k]].append(g)
        pairs = strict_ok = cens_ok = 0
        day_end = 3 * (k + 1)   # the (k+1)th shop appears at day 3(k+1)
        for grp in by.values():
            for i in range(len(grp)):
                for j in range(i + 1, len(grp)):
                    a, b = grp[i], grp[j]
                    pairs += 1
                    if all(a[2][d] == b[2][d] for d in range(day_end + 1)):
                        strict_ok += 1
                    if all(a[3][d] == b[3][d] for d in range(day_end + 1)):
                        cens_ok += 1
        if pairs:
            print(f"  same first {k} shops: {pairs} pairs; farms identical "
                  f"through day {day_end}: strict {strict_ok/pairs:.0%}, "
                  f"census {cens_ok/pairs:.0%}")
    # where do same-prefix games first differ (census, by day)?
    by = defaultdict(list)
    for g in games:
        by[g[1][:2]].append(g)
    firsts = Counter()
    for grp in by.values():
        for i in range(len(grp)):
            for j in range(i + 1, len(grp)):
                a, b = grp[i], grp[j]
                d = next((d for d in range(30) if a[3][d] != b[3][d]), 30)
                firsts[d] += 1
    print("  same first-2 shops: first day the census differs ->",
          dict(sorted(firsts.items())))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
