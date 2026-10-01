# BEST COPY — how do the HIGHEST-rated copies of our opening family
# earn their rating?  Pure table work on the public dataset (no games, no
# seeds, no replays).  For each target submission: record vs same-opening
# opponents ("copy games") and vs everyone else, split by opponent rating, and
# the list of copy-game episode ids (for clone_diff-style decoding).
# DECISION RULE (fixed before the data was looked at):
#   If a target wins >= 75% of its copy games, its rating comes from beating
#   copies -> its post-opening edits are what we must port.
#   If it wins < 60% of copy games but is rated high, the rating comes from
#   elsewhere (luck / few games) and it is NOT a model to copy.
# Usage: python -X utf8 best_copy.py
import csv
import os
import sys
from collections import defaultdict

DS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "kaggriculture-episodes")
TARGETS = {"56591730": "E. Honda (new)", "56571320": "E. Honda (old)",
           "56502673": "Anton Tikhonov", "56371926": "Artyom Lyan"}
CUTS = ["stream_h24", "stream_h48", "stream_h100", "stream_h136",
        "stream_h200", "stream_h300", "stream_h400", "stream_h719"]
BANDS = [(0, 1900), (1900, 2100), (2100, 2300), (2300, 2600), (2600, 9999)]


def main():
    teams = {}
    with open(DS + r"\teams.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            teams[r["team_id"]] = r["team_name"]
    eps = {}
    with open(DS + r"\episodes.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["type"] != "EPISODE_TYPE_PUBLIC":
                continue
            if r["sub_0"] in TARGETS or r["sub_1"] in TARGETS:
                eps[r["episode_id"]] = r
    hs = defaultdict(dict)
    with open(DS + r"\stream_hashes.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["episode_id"] in eps:
                hs[r["episode_id"]][r["seat"]] = r
    for sub, label in TARGETS.items():
        games = []
        for ep, r in eps.items():
            for s in ("0", "1"):
                if r["sub_" + s] != sub:
                    continue
                o = "1" if s == "0" else "0"
                try:
                    mb, ob = float(r["bank_" + s]), float(r["bank_" + o])
                    orat = float(r["rating_" + o] or 0)
                except ValueError:
                    continue
                h = hs.get(ep, {})
                same_until = None
                if s in h and o in h:
                    same_until = 0
                    for c in CUTS:
                        if h[s][c] and h[s][c] == h[o][c]:
                            same_until = int(c[8:])
                        else:
                            break
                games.append((r["create_time"], ep, teams.get(r["team_" + o], "?"),
                              orat, mb, ob, same_until, r["sub_" + o]))
        games.sort()
        print(f"\n===== {label} sub {sub}: {len(games)} games, "
              f"{games[0][0][:16] if games else ''} .. "
              f"{games[-1][0][:16] if games else ''}")
        for kind, test in (("COPY games (same moves through turn 48+)",
                            lambda g: g[6] is not None and g[6] >= 48),
                           ("OTHER games", lambda g: not (g[6] is not None
                                                           and g[6] >= 48))):
            sel = [g for g in games if test(g)]
            w = sum(g[4] > g[5] for g in sel)
            l = sum(g[4] < g[5] for g in sel)
            t = len(sel) - w - l
            mar = sorted(g[4] - g[5] for g in sel)
            med = mar[len(mar) // 2] if mar else 0
            print(f"  {kind}: W{w}-L{l}-T{t}  median margin {med:+,.0f}")
            for lo, hi in BANDS:
                b = [g for g in sel if lo <= g[3] < hi]
                if b:
                    bw = sum(g[4] > g[5] for g in b)
                    bl = sum(g[4] < g[5] for g in b)
                    print(f"      opp rating {lo}-{hi}: W{bw}-L{bl}-T{len(b)-bw-bl}")
        cg = [g for g in games if g[6] is not None and g[6] >= 48]
        print("  newest copy games (ep, opp, opp rating, margin, "
              "identical through turn):")
        for g in cg[-14:]:
            print(f"    {g[1]} {g[2][:24]:24} {g[3]:7.0f} {g[4]-g[5]:+9,.0f} "
                  f"same<= {g[6]} oppsub {g[7]}")
        og = sorted((g for g in games if not (g[6] is not None and g[6] >= 48)),
                    key=lambda g: -g[3])[:10]
        print("  strongest OTHER opponents faced:")
        for g in og:
            print(f"    {g[1]} {g[2][:24]:24} {g[3]:7.0f} {g[4]-g[5]:+9,.0f} "
                  f"bank {g[4]:,.0f}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
