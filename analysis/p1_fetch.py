# PHASE 1 FETCH  — pull every public game of ONE top submission via
# the public replay API (same read-only endpoints as tools/fetch_top_eps.py;
# no credentials, no account actions).  Gzipped replays -> replays/<tag>/.
# Usage: python -X utf8 p1_fetch.py <submission_id> <tag> [max_games]
import gzip
import json
import sys
import time
import urllib.request
from pathlib import Path

R = Path(r"C:\Kaggriculture")
sys.path.insert(0, str(R / "work" / "build_a" / "arena"))
from team_now import games  # noqa: E402


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def main():
    sub, tag = int(sys.argv[1]), sys.argv[2]
    mx = int(sys.argv[3]) if len(sys.argv) > 3 else 10 ** 6
    out = R / "replays" / tag
    out.mkdir(parents=True, exist_ok=True)
    g = games(sub)
    g.sort(reverse=True)
    idx_path = out / "index.json"
    idx = json.load(open(idx_path, encoding="utf-8")) if idx_path.exists() else {}
    n = 0
    for end, eid, ag in g:
        if n >= mx:
            break
        p = out / f"ep_{eid}.json.gz"
        if str(eid) in idx and p.exists():
            n += 1
            continue
        try:
            raw = get(f"https://www.kaggleusercontent.com/episodes/{eid}.json")
        except Exception as e:
            print("fail", eid, e, flush=True)
            continue
        with gzip.open(p, "wb") as fh:
            fh.write(raw)
        idx[str(eid)] = {"end": end, "agents": ag}
        n += 1
        if n % 20 == 0:
            print(f"{n} saved", flush=True)
            json.dump(idx, open(idx_path, "w", encoding="utf-8"))
        time.sleep(0.4)
    json.dump(idx, open(idx_path, "w", encoding="utf-8"))
    print(f"done: {n} games of sub {sub} in {out}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
