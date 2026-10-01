# TEAM NOW — which submissions does a team run today, and how do they score?
# Read-only public API (same one tools/fetch_top_eps.py uses; ListEpisodes by
# submissionId only — teamId is rejected).  Bounded crawl: start from a known
# old submission of the team, walk to its strongest opponents' submissions,
# and look in THEIR newest games for the team's newer submissions.
# Usage: python -X utf8 team_now.py <teamId> <known_old_sub> [max_calls]
import json
import sys
import time
import urllib.request
from collections import defaultdict

URL = "https://www.kaggle.com/api/i/competitions.EpisodeService/ListEpisodes"


def post(body):
    req = urllib.request.Request(
        URL, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode())


def games(sub):
    d = post({"submissionId": int(sub)})
    out = []
    for e in d.get("episodes", []):
        ag = e.get("agents") or []
        if e.get("state") != "COMPLETED" or len(ag) != 2:
            continue
        out.append((e.get("endTime", ""), e["id"], ag))
    out.sort()
    return out


def report(tid, sub, g):
    rows = []
    for end, eid, ag in g:
        for i, a in enumerate(ag):
            if a.get("submissionId") == int(sub):
                o = ag[1 - i]
                rows.append((end, eid, a.get("reward"), o.get("reward"),
                             a.get("updatedScore"), o.get("submissionId"),
                             o.get("teamId"), o.get("updatedScore")))
    w = sum((x[2] or 0) > (x[3] or 0) for x in rows)
    l = sum((x[2] or 0) < (x[3] or 0) for x in rows)
    if not rows:
        print(f"  sub {sub}: no games")
        return
    print(f"  sub {sub}: games {len(rows)} W{w}-L{l}  {rows[0][0][:16]} .. "
          f"{rows[-1][0][:16]}  last rating {rows[-1][4]}")
    for x in rows[-8:]:
        print(f"     ep {x[1]} {x[0][:16]} margin {(x[2] or 0) - (x[3] or 0):+,.0f} "
              f"(us {x[2]}) opp team {x[6]} sub {x[5]} rating {x[7]}")


def main():
    tid, old = int(sys.argv[1]), int(sys.argv[2])
    max_calls = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    g = games(old)
    print(f"===== team {tid}, known sub {old}")
    report(tid, old, g)
    opp = defaultdict(float)
    for end, eid, ag in g:
        for a in ag:
            if a.get("teamId") != tid:
                opp[a.get("submissionId")] = max(opp[a.get("submissionId")],
                                                 a.get("updatedScore") or 0)
    found = {}
    calls = 0
    for osub, sc in sorted(opp.items(), key=lambda kv: -kv[1]):
        if calls >= max_calls:
            break
        calls += 1
        try:
            og = games(osub)
        except Exception as e:
            print("  crawl fail", osub, e)
            continue
        time.sleep(0.5)
        for end, eid, ag in og:
            for a in ag:
                if a.get("teamId") == tid and a.get("submissionId") != old:
                    s = a.get("submissionId")
                    if s not in found or end > found[s]:
                        found[s] = end
    print("  other submissions of this team seen:",
          {k: v[:16] for k, v in sorted(found.items())})
    for s in sorted(found)[-2:]:
        if s > old:
            try:
                report(tid, s, games(s))
            except Exception as e:
                print("  fail", s, e)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
