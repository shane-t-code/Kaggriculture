#!/usr/bin/env python3
"""Crawl Kaggle's public EpisodeService for top-team episodes.

Modes:
  crawl  — BFS from seed submission IDs over episode agent records until all
           target teams' submissions are visited. Writes results/top10/crawl.json
           (episode metadata, dedup by id) + prints per-team submission map.

Usage: python tools/top10_scrape.py crawl
Dev-time tool only (network is legal outside episodes; §2.12 applies in-episode).
"""
import sys, json, os, time
import requests

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BASE = "https://www.kaggle.com/api/i/competitions.EpisodeService/"
OUT = os.path.join("results", "top10")

# Current top-10 team ids (public LB 2026-09-20 16:29 UTC, scores 3245.2..3005.3)
TOP10 = {
    16732748: "DSM",
    16718819: "Majkel1337",
    16681125: "M & M & P & Q",
    16730612: "Unknown Mother-Goose",
    16730524: "THIRD FARM CLUB",
    16640510: "SpaTaro",
    16817528: "QQ",
    16675778: "Orbital Terraformer",
    16760701: "Yannik Schiffner",
    16760569: "Otter Vibe",
}
# seeds: mtmr_s1's live sub (from our decoded loss) + our metav4 sub
SEEDS = [56380330, 56400540]
SCORE_FLOOR = 2900.0  # also expand through any sub rated this high


def list_episodes(sub_id):
    r = requests.post(BASE + "ListEpisodes", json={"submissionId": int(sub_id)}, timeout=90)
    r.raise_for_status()
    return r.json()


def main():
    os.makedirs(OUT, exist_ok=True)
    episodes = {}          # id -> episode dict
    sub_team = {}          # subId -> (teamId, best updatedScore seen)
    visited, queue = set(), list(SEEDS)
    calls = 0
    while queue and calls < 60:
        sub = queue.pop(0)
        if sub in visited:
            continue
        visited.add(sub)
        try:
            data = list_episodes(sub)
        except Exception as e:
            print(f"sub {sub}: FAILED {e}")
            continue
        calls += 1
        eps = data.get("episodes") or []
        for e in eps:
            episodes[e["id"]] = e
            for a in e.get("agents", []):
                sid, tid = a.get("submissionId"), a.get("teamId")
                sc = a.get("updatedScore") or a.get("initialScore") or 0
                if sid is None:
                    continue
                old = sub_team.get(sid)
                if old is None or sc > old[1]:
                    sub_team[sid] = (tid, sc)
                # expand: target-team subs always; strong subs too
                if sid not in visited and sid not in queue:
                    if tid in TOP10 or (sc and sc >= SCORE_FLOOR):
                        queue.append(sid)
        print(f"sub {sub}: {len(eps)} eps | total eps {len(episodes)} | queue {len(queue)}")
        time.sleep(0.6)

    with open(os.path.join(OUT, "crawl.json"), "w", encoding="utf-8") as f:
        json.dump({"episodes": list(episodes.values()),
                   "sub_team": {str(k): v for k, v in sub_team.items()}}, f)

    print("\n=== per-team submissions found ===")
    for tid, name in TOP10.items():
        subs = sorted((s for s, (t, _) in sub_team.items() if t == tid),
                      key=lambda s: -sub_team[s][1])
        tags = [f"{s}({sub_team[s][1]:.0f})" for s in subs]
        print(f"{name:24} team {tid}: {tags}")
    n_toptop = sum(1 for e in episodes.values()
                   if sum(1 for a in e.get("agents", []) if a.get("teamId") in TOP10) == 2)
    print(f"\nepisodes total {len(episodes)}, top10-vs-top10 {n_toptop}")


if __name__ == "__main__":
    main()
