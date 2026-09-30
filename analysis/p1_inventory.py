# PHASE 1 inventory  — what top-team replays do we already hold, per
# team and submission, and what does one replay look like (seed present?
# engine version? tile kinds?).  Read-only, no games.
import ast
import gzip
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

R = Path(r"C:\Kaggriculture")
files = sorted((R / "replays" / "top10").glob("ep_*.json.gz"))
man = {}
mp = R / "replays" / "top10" / "manifest.json"
if mp.exists():
    for m in json.load(open(mp, encoding="utf-8")):
        man[str(m["episode"])] = m
sys.stdout.reconfigure(encoding="utf-8")
print("files", len(files), "manifest rows", len(man))
by_team = defaultdict(list)
kinds = Counter()
first = True
for f in files:
    rep = json.load(gzip.open(f, "rt", encoding="utf-8"))
    teams = rep["info"].get("TeamNames")
    if isinstance(teams, str):
        teams = ast.literal_eval(teams)
    seed = rep.get("configuration", {}).get("seed") or rep["info"].get("seed")
    fin = rep["steps"][-1]
    ep = f.name[3:-8]
    subs = None
    if ep in man and man[ep].get("agents"):
        subs = [a.get("submissionId") for a in man[ep]["agents"]]
    shops = fin[0]["observation"]["town"]["unlocked_shops"]
    for s in (0, 1):
        by_team[teams[s]].append((ep, s, fin[s]["reward"], fin[1 - s]["reward"],
                                  teams[1 - s], subs[s] if subs else None,
                                  bool(seed), shops[:2]))
    if first:
        first = False
        print("version", rep.get("version"), "config keys",
              list(rep.get("configuration", {}).keys())[:12], "seed", seed)
        o = rep["steps"][300][0]["observation"]
        print("obs keys", list(o.keys()))
        print("farm keys", list(o["farms"][0].keys()))
        for row in o["farms"][0]["tiles"]:
            for t in row:
                if isinstance(t, dict):
                    kinds[json.dumps(sorted(t.keys()))] += 1
        print("tile key sets", kinds.most_common(6))
        print("hand sample", o["farms"][0]["hands"][:1], "farmer",
              o["farms"][0].get("farmer"))
        print("inventory", o["farms"][0].get("inventory"))
for tm, g in sorted(by_team.items(), key=lambda kv: -len(kv[1])):
    if len(g) < 3:
        continue
    w = sum((x[2] or 0) > (x[3] or 0) for x in g)
    bk = sorted(x[2] or 0 for x in g)
    print(f"{tm[:28]:28} games {len(g):3d} W{w} medbank {bk[len(bk)//2]:,.0f} "
          f"subs {dict(Counter(x[5] for x in g))} seeds_ok "
          f"{sum(x[6] for x in g)}")
