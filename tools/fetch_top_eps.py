"""fetch_top_eps.py — pull recent top-10 episodes via the PUBLIC replay API
.  Read-only: ListEpisodes POST + kaggleusercontent GET, no
credentials, no account actions.  Saves gzipped replays to replays/top10/.

Usage: python tools/fetch_top_eps.py [per_team]
"""
import gzip, json, os, sys, time, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
OUT = r"replays\top10"
os.makedirs(OUT, exist_ok=True)

PER_TEAM = int(sys.argv[1]) if len(sys.argv) > 1 else 3
subs = json.load(open(r"work\\review2\top_submissions_expanded.json", encoding="utf-8"))

# one (the newest) submission per team
by_team = {}
for sid, meta in subs.items():
    t = meta["team"]
    if t not in by_team or int(sid) > int(by_team[t]):
        by_team[t] = sid


def post(url, body):
    req = urllib.request.Request(
        url, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json",
                 "User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


manifest = []
for team, sid in sorted(by_team.items()):
    try:
        d = post("https://www.kaggle.com/api/i/competitions.EpisodeService/ListEpisodes",
                 {"submissionId": int(sid)})
    except Exception as e:
        print(f"{team}: ListEpisodes failed: {e}")
        continue
    eps = [e for e in d.get("episodes", []) if e.get("state") == "COMPLETED"]
    eps.sort(key=lambda e: e.get("endTime", ""), reverse=True)
    took = 0
    for ep in eps:
        if took >= PER_TEAM:
            break
        eid = ep["id"]
        path = os.path.join(OUT, f"ep_{eid}.json.gz")
        if os.path.exists(path):
            took += 1
            manifest.append({"team": team, "submission": sid, "episode": eid,
                             "agents": ep.get("agents"), "cached": True})
            continue
        try:
            raw = get(f"https://www.kaggleusercontent.com/episodes/{eid}.json")
        except Exception as e:
            print(f"{team}: ep {eid} download failed: {e}")
            continue
        with gzip.open(path, "wb") as fh:
            fh.write(raw)
        took += 1
        manifest.append({"team": team, "submission": sid, "episode": eid,
                         "agents": ep.get("agents"), "cached": False})
        print(f"{team}: saved ep {eid} ({len(raw) // 1024} KB raw)")
        time.sleep(1.0)
json.dump(manifest, open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8"), indent=1)
print(f"done: {len(manifest)} episodes across {len(by_team)} teams -> {OUT}")
