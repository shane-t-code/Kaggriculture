# WS GAP MEASUREMENT  — does the ws6 takeover beat the PARENT it
# replaces, in the same world vs the same opponent? And where does the
# difference come from, day by day?
# Arms: parent = s1009r (what b2/ws6 wrap and fall back to), ws6.
# Opponent: r6 (main.py). Worlds: yarn-first naturals 8381/8477/8480/8426
# (seeds already spent tonight on the same question; development reuse).
import json
import os
import sys

sys.path.insert(0, r"C:\Kaggriculture")
sys.dont_write_bytecode = True
from run_local import _silence_fds
with _silence_fds():
    from kaggle_environments import make
    from kaggle_environments.agent import get_last_callable

R10 = r"C:\Kaggriculture\work\\review10"
ARMS = {
    "parent": r"C:\Kaggriculture\work\build_a\step1009r.py",
    "ws6": os.path.join(R10, "takeover_ws6_forced.py"),
}
OPP = r"C:\Kaggriculture\main.py"
MOVE = {"NORTH", "SOUTH", "EAST", "WEST"}


def load(p):
    return get_last_callable(open(p, encoding="utf-8").read(), path=p)


def profile(env, me):
    out = {}
    for d in (3, 6, 9, 12, 15, 18, 21, 24, 27, 29):
        t = min(d * 24, len(env.steps) - 1)
        o = env.steps[t][0]["observation"]
        f = o["farms"][me]
        herd = {"S": 0, "C": 0, "G": 0}
        crops = {}
        for row in f["tiles"]:
            for x in row:
                if isinstance(x, dict) and x.get("animal"):
                    herd[x["animal"][0]] += 1
                elif isinstance(x, dict) and x.get("kind") == "PLANT":
                    crops[x["crop"][:3]] = crops.get(x["crop"][:3], 0) + 1
        out[d] = {"$": int(f["money"]), "herd": herd, "crops": crops,
                  "quads": len(f["unlocked_quadrants"])}
    idle = work = 0
    for t in range(72, len(env.steps)):
        a = env.steps[t][me].get("action") or {}
        for c in [a.get("farmer") or ["PASS"]] + list(a.get("hands") or []):
            op = c[0] if c else "PASS"
            if op == "PASS":
                idle += 1
            elif op not in MOVE:
                work += 1
    return out, idle, work


for seed in (8381, 8477, 8480, 8426):
    res = {}
    for arm, path in ARMS.items():
        agents = [load(path), load(OPP)]
        with _silence_fds():
            env = make("kaggriculture",
                       configuration={"episodeSteps": 720, "seed": seed})
            env.run(agents)
        rw = [s.reward for s in env.steps[-1]]
        prof, idle, work = profile(env, 0)
        res[arm] = (rw[0], rw[0] - rw[1], prof, idle, work)
    p, w = res["parent"], res["ws6"]
    print(f"\n==== seed {seed}: PARENT bank {p[0]:,.0f} margin {p[1]:+,.0f} | "
          f"WS6 bank {w[0]:,.0f} margin {w[1]:+,.0f} | "
          f"ws6-parent {w[0]-p[0]:+,.0f}")
    print(f"   idle turns parent {p[3]} ws6 {w[3]} | work parent {p[4]} ws6 {w[4]}")
    for d in (3, 6, 9, 12, 15, 18, 21, 24, 27, 29):
        a, b = p[2][d], w[2][d]
        print(f"   d{d:2}  $ {a['$']:>7,} vs {b['$']:>7,}  herd {a['herd']} vs "
              f"{b['herd']}  crops {a['crops']} vs {b['crops']}  "
              f"quads {a['quads']}/{b['quads']}")
