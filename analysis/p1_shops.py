# SHOP DETERMINISM — is a top team's farm decided by the shops
# it has seen so far?  For every pair of games played by the SAME submission
# (replays already on disk, no games run) find
#   s_shop = first step where the two towns' shop lists differ
#   s_farm = first step where the two farms differ (tiles, land, hands)
#   s_move = first step where the recorded moves differ
# DECISION RULE (fixed in advance): if in >= 80% of pairs the farms stay identical until
# the towns differ (s_farm >= s_shop - 24), the team's build is a function of
# the shops and can be stored as a tree of plans that branches at each new
# shop.  If farms differ well before the towns do, the build also depends on
# the opponent / prices and a plain tree is not enough.
import ast
import gzip
import json
import sys
from collections import defaultdict
from pathlib import Path

R = Path(__file__).resolve().parents[1]


def tile_sig(t):
    if not isinstance(t, dict):
        return None
    return (t.get("kind"), t.get("crop") or t.get("animal"))


def main():
    man = {}
    for m in json.load(open(R / "replays" / "top10" / "manifest.json",
                            encoding="utf-8")):
        man[str(m["episode"])] = m
    games = defaultdict(list)
    for f in sorted((R / "replays" / "top10").glob("ep_*.json.gz")):
        ep = f.name[3:-8]
        if ep not in man or not man[ep].get("agents"):
            continue
        rep = json.load(gzip.open(f, "rt", encoding="utf-8"))
        teams = rep["info"].get("TeamNames")
        if isinstance(teams, str):
            teams = ast.literal_eval(teams)
        steps = rep["steps"]
        for s in (0, 1):
            sub = man[ep]["agents"][s].get("submissionId")
            shops, farm, moves = [], [], []
            for t in range(len(steps)):
                o = steps[t][0]["observation"]
                fm = o["farms"][s]
                shops.append(tuple(o["town"]["unlocked_shops"]))
                farm.append(json.dumps(
                    [[tile_sig(x) for x in row] for row in fm["tiles"]]
                    + [len(fm["unlocked_quadrants"]), len(fm["hands"])]))
                moves.append(json.dumps(steps[t][s].get("action")))
            games[(teams[s], sub)].append((ep, shops, farm, moves,
                                           steps[-1][s]["reward"]))
    for (tm, sub), g in sorted(games.items(), key=lambda kv: -len(kv[1])):
        if len(g) < 5:
            continue
        rows = []
        for i in range(len(g)):
            for j in range(i + 1, len(g)):
                a, b = g[i], g[j]
                n = min(len(a[1]), len(b[1]))

                def first(k):
                    for t in range(n):
                        if a[k][t] != b[k][t]:
                            return t
                    return n
                rows.append((first(1), first(2), first(3)))
        ok = sum(sf >= ss - 24 for ss, sf, sm in rows)
        sf_sorted = sorted(sf for ss, sf, sm in rows)
        sm_sorted = sorted(sm for ss, sf, sm in rows)
        ss_sorted = sorted(ss for ss, sf, sm in rows)
        print(f"{tm[:24]:24} sub {sub} games {len(g)} pairs {len(rows)} | "
              f"farms same until towns differ: {ok}/{len(rows)} | first farm "
              f"difference step min/median {sf_sorted[0]}/"
              f"{sf_sorted[len(rows)//2]} | first move difference "
              f"{sm_sorted[0]}/{sm_sorted[len(rows)//2]} | first town "
              f"difference {ss_sorted[0]}/{ss_sorted[len(rows)//2]}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
