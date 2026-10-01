# PLAN STORE BUILDER — turn every public game of the
# donor team (Mother-Goose) into a compact PLAN: the team's recorded moves,
# its money and hand-count curves (for the cash guard / hire match), the
# town's shop sequence, and a per-day farm census (for choosing the plan
# whose farm is closest to ours when we must switch).
# Output: playbook/plans.json.gz  (one list; loaded by the agent
# builder, which embeds it into the submission file).
# Usage: python -X utf8 build_store.py [replay_dir] [team]
import ast
import gzip
import json
import sys
from collections import Counter
from pathlib import Path

R = Path(__file__).resolve().parents[1]
OUT = R / "playbook" / "plans.json.gz"


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
            elif s and s[0]:
                c[s[0]] += 1          # bare COOP / PASTURE / WEED tiles
    c["LAND"] = len(fm["unlocked_quadrants"])
    return dict(c)


def main():
    rdir = R / "replays" / (sys.argv[1] if len(sys.argv) > 1 else "mg")
    team = sys.argv[2] if len(sys.argv) > 2 else "Unknown Mother-Goose"
    idx = json.load(open(rdir / "index.json", encoding="utf-8"))
    plans = []
    for f in sorted(rdir.glob("ep_*.json.gz")):
        ep = f.name[3:-8]
        rep = json.load(gzip.open(f, "rt", encoding="utf-8"))
        teams = rep["info"].get("TeamNames")
        if isinstance(teams, str):
            teams = ast.literal_eval(teams)
        if team not in teams:
            continue
        s = teams.index(team)
        steps = rep["steps"]
        if len(steps) < 720 or steps[-1][s]["status"] != "DONE":
            continue
        table, money, hands, cens, grids = [], [], [], [], []
        for t in range(len(steps)):
            fm = steps[t][0]["observation"]["farms"][s]
            money.append(round(fm["money"]))
            hands.append(len(fm["hands"]))
            if t % 24 == 0:
                cens.append(census(fm))
                grids.append(["" if tile_sig(x) is None else
                              (tile_sig(x)[1] or tile_sig(x)[0])
                              for row in fm["tiles"] for x in row])
            if t + 1 < len(steps):
                a = steps[t + 1][s].get("action") or {}
                table.append([a.get("farmer") or ["PASS"],
                              a.get("hands") or [],
                              [o for o in (a.get("market") or []) if o]])
        shops = steps[-1][0]["observation"]["town"]["unlocked_shops"]
        sub = None
        if ep in idx and idx[ep].get("agents"):
            sub = idx[ep]["agents"][s].get("submissionId")
        plans.append({"ep": ep, "sub": sub, "seat": s, "shops": shops,
                      "bank": steps[-1][s]["reward"],
                      "opp_bank": steps[-1][1 - s]["reward"],
                      "opp": teams[1 - s], "money": money, "hands": hands,
                      "census": cens, "grid": grids, "table": table})
    with gzip.open(OUT, "wt", encoding="utf-8") as fh:
        json.dump(plans, fh, separators=(",", ":"))
    subs = Counter(p["sub"] for p in plans)
    print(f"{len(plans)} plans -> {OUT} ({OUT.stat().st_size // 1024} KB); "
          f"subs {dict(subs)}; median bank "
          f"{sorted(p['bank'] for p in plans)[len(plans) // 2]:,.0f}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
