#!/usr/bin/env python3
"""Phase 1: the exact-gap ledger — top-10 corpus vs our pipe16 tape, day by day.

Side A: 394 top-10 seat-trajectories (results/top10/traj/*.npz).
Side B: pipe16 mirror games played locally (seeds from --seeds list).
Per day d12-29: work ops by verb, PASS unit-hours, board mix at noon,
bank delta. Output: results/gap_ledger.txt + stdout table.

Usage: python tools/gap_ledger.py [--games 3]
"""
import sys, os, glob, json, io, contextlib
import numpy as np
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
CROPS = ["", "CARROT", "MELON", "STRAWBERRY", "TOMATO", "WHEAT"]
WORKV = ["WATER", "HARVEST", "PLANT", "FERTILIZE", "DIG", "FEED", "CARE",
         "COLLECT_FERTILIZER", "PICKUP", "DROP"]
DAYS = list(range(12, 30))


def blank():
    return {d: defaultdict(float) for d in DAYS}


def add_top10(agg):
    files = sorted(glob.glob("results/top10/traj/*.npz"))
    n = 0
    for f in files:
        z = np.load(f, allow_pickle=True)
        vocab = list(z["vocab"])
        scal, act_f, act_h, tiles = z["scal"], z["act_f"], z["act_h"], z["tiles_self"]
        n += 1
        for t in range(len(scal)):
            d = int(scal[t, 0])
            if d not in agg:
                continue
            nh = int(scal[t, 4])
            for a in [act_f[t]] + list(act_h[t][:nh]):
                v = vocab[a[0]] if a[0] < len(vocab) else ""
                if v in WORKV:
                    agg[d][v] += 1
                elif v == "PASS":
                    agg[d]["PASS"] += 1
            if t % 24 == 12:
                ts = tiles[t]
                plant = ts[:, 0] == 2
                for c in range(1, 6):
                    agg[d]["tile_" + CROPS[c]] += (plant & (ts[:, 1] == c)).sum()
                agg[d]["tile_inert"] += (plant & (ts[:, 6] == 0)
                                         & (d - ts[:, 2] > 6)).sum()
            if t % 24 == 23:
                nxt = min(t + 24, len(scal) - 1)
                agg[d]["bank_delta"] += float(scal[nxt, 2] - scal[t - 23, 2])
    return n


def add_ours(agg, games):
    from kaggle_environments import make
    for seed in range(100, 100 + games):
        env = make("kaggriculture", configuration={"seed": seed, "actTimeout": 60,
                                                   "runTimeout": 100000})
        with contextlib.redirect_stdout(io.StringIO()):
            env.run(["external/pipe16_main.py", "external/pipe16_main.py"])
        for t in range(len(env.steps)):
            d = t // 24
            if d not in agg:
                continue
            st = env.steps[t][0]
            obs = st["observation"]
            act = st.get("action") or {}
            farm = obs["farms"][0]
            cmds = [act.get("farmer") or ["PASS"]] + list(act.get("hands") or [])
            for i, a in enumerate(cmds):
                if i > len(farm.get("hands", [])):
                    break
                v = a[0] if a else "PASS"
                if v in WORKV:
                    agg[d][v] += 1
                elif v == "PASS":
                    agg[d]["PASS"] += 1
            if t % 24 == 12:
                for row in farm["tiles"]:
                    for x in row:
                        if isinstance(x, dict) and x.get("kind") == "PLANT":
                            c = x.get("crop", "")
                            if c in CROPS:
                                agg[d]["tile_" + c] += 1
                            if x.get("yield_units", 1) == 0 and \
                                    d - x.get("planted_day", 0) > 6:
                                agg[d]["tile_inert"] += 1
            if t % 24 == 23:
                m_now = farm["money"]
                m_start = env.steps[t - 23][0]["observation"]["farms"][0]["money"]
                agg[d]["bank_delta"] += m_now - m_start
        print(f"  our seed {seed} done", flush=True)
    return games


def main():
    args = sys.argv[1:]
    games = int(args[args.index("--games") + 1]) if "--games" in args else 3
    top, ours = blank(), blank()
    print("aggregating top-10 corpus...", flush=True)
    n_top = add_top10(top)
    print(f"  {n_top} seats", flush=True)
    print(f"playing {games} local pipe16 mirror games...", flush=True)
    n_our = add_ours(ours, games)
    keys = (WORKV + ["PASS", "bank_delta", "tile_CARROT", "tile_WHEAT",
                     "tile_STRAWBERRY", "tile_TOMATO", "tile_MELON", "tile_inert"])
    lines = [f"{'day':>4} | " + " | ".join(f"{k[:11]:>11}" for k in keys),
             "     (each cell: top10_mean / ours_mean, per farm-day)"]
    for d in DAYS:
        cells = []
        for k in keys:
            a = top[d][k] / max(n_top, 1)
            b = ours[d][k] / max(n_our, 1)
            cells.append(f"{a:6.1f}/{b:6.1f}")
        lines.append(f" d{d:>2} | " + " | ".join(cells))
    out = "\n".join(lines)
    print(out)
    with open(os.path.join("results", "gap_ledger.txt"), "w", encoding="utf-8") as f:
        f.write(out + "\n")
    print("\nsaved results/gap_ledger.txt")


if __name__ == "__main__":
    main()
