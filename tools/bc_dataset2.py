#!/usr/bin/env python3
"""BC v2 dataset: macro (task, target-tile) segments instead of per-step verbs.

For each unit, each WORK action (non-move, non-PASS) ends a segment. The
sample's features are taken at the segment's FIRST step (the decision moment,
right after the previous work action); the label is the work verb (13-way),
the tile where it executes (100-way), and the crop for PLANT (6-way).

Fixes vs v1: move classes gone (~55% of samples), per-team cap, full-board
per-tile features + opponent board summary. Split BY EPISODE (id%10==0=val).

Usage: python tools/bc_dataset2.py [--dmin 12] [--cap 150000]
"""
import sys, os, json, glob
import numpy as np

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TRAJ = os.path.join("results", "top10", "traj")
CROPS = ["", "CARROT", "MELON", "STRAWBERRY", "TOMATO", "WHEAT"]
WORK = ["WATER", "HARVEST", "PLANT", "FERTILIZE", "DIG", "FEED", "CARE",
        "COLLECT_FERTILIZER", "PICKUP", "DROP", "BUILD_COOP",
        "BUILD_PASTURE", "PLACE"]
W2I = {v: i for i, v in enumerate(WORK)}
MOVES = {"NORTH", "SOUTH", "EAST", "WEST"}
PRICE_BASE = np.array([40, 55, 55, 130, 160, 120, 60, 20, 200], dtype=np.float32)
F_KIND, F_CROP, F_PLANTED, F_WATERED, F_CUW, F_FERT, F_YIELD, F_LIFE, \
    F_ANIMAL, F_FED, F_CARED, F_CUNF, F_FAVAIL, F_CBONUS, F_PLACED = range(15)


def board_summary(tiles, day):
    kind = tiles[:, F_KIND]; crop = tiles[:, F_CROP]
    out = []
    plant = kind == 2
    for c in range(1, 6):
        m = plant & (crop == c)
        out += [m.sum(), (m & (tiles[:, F_WATERED] == 0)).sum(),
                tiles[m, F_YIELD].sum() if m.any() else 0]
    out.append((plant & (tiles[:, F_YIELD] == 0) & (day - tiles[:, F_PLANTED] > 6)).sum())
    out += [(kind == 0).sum(), (kind == 1).sum()]
    for a in range(1, 4):
        m = tiles[:, F_ANIMAL] == a
        out += [m.sum(), (m & (tiles[:, F_FED] == 0)).sum(),
                (m & (tiles[:, F_CARED] == 0)).sum(),
                tiles[m, F_YIELD].sum() if m.any() else 0]
    out.append((tiles[:, F_FAVAIL] > 0).sum())
    return np.array(out, dtype=np.float32)          # 31


def board_grid(tiles):
    """Per-tile compact features, 100 x 6 flattened."""
    g = np.zeros((100, 6), dtype=np.float32)
    g[:, 0] = tiles[:, F_KIND] / 5.0
    g[:, 1] = np.where(tiles[:, F_KIND] == 2, tiles[:, F_CROP],
                       -tiles[:, F_ANIMAL]) / 5.0     # crop + / animal -
    g[:, 2] = tiles[:, F_WATERED] + tiles[:, F_FED] * 0.5
    g[:, 3] = np.minimum(tiles[:, F_CUW] + tiles[:, F_CUNF], 3) / 3.0
    g[:, 4] = np.minimum(tiles[:, F_YIELD], 6) / 6.0
    g[:, 5] = (tiles[:, F_FAVAIL] + tiles[:, F_CARED]) / 2.0
    return g.ravel()                                  # 600


def episode_samples(path, dmin):
    z = np.load(path, allow_pickle=True)
    meta = json.loads(str(z["meta"]))
    vocab = list(z["vocab"])
    scal, prices, minv = z["scal"], z["prices"], z["minv"]
    tiles_s, tiles_o = z["tiles_self"], z["tiles_opp"]
    fpos, hpos = z["fpos"], z["hpos"]
    seeds, shed, carry = z["seeds"], z["shed"], z["carry"]
    act_f, act_h = z["act_f"], z["act_h"]
    n = len(scal)

    # per-step decoded verb per unit (0=farmer, 1..16=hands)
    def verb_at(t, u):
        a = act_f[t] if u == 0 else act_h[t, u - 1]
        v = vocab[a[0]] if a[0] < len(vocab) else ""
        arg = vocab[a[1]] if len(a) > 1 and a[1] < len(vocab) else ""
        return v, arg

    def pos_at(t, u):
        p = fpos[t] if u == 0 else hpos[t, u - 1]
        return int(p[0]), int(p[1])

    X, yv, yt, yc = [], [], [], []
    max_units = 17
    seg_start = [0] * max_units
    for t in range(n):
        day = int(scal[t, 0])
        if int(scal[t, 1]) == 0:                     # new day: hands respawn
            for u in range(max_units):
                seg_start[u] = t
        nh = int(scal[t, 4])
        for u in range(0, min(nh + 1, max_units)):
            v, arg = verb_at(t, u)
            if v in MOVES or v in ("", "PASS"):
                continue
            if v not in W2I:
                seg_start[u] = t + 1
                continue
            if day >= dmin:
                s0 = max(seg_start[u], 0)
                d0 = scal[s0, 0]
                ts = tiles_s[s0]
                pn = prices[s0] / PRICE_BASE
                xx, yy = pos_at(s0, u)
                cinv = carry[s0, u] if u < 17 else np.zeros(12, np.int16)
                glob = np.concatenate([
                    [d0 / 29.0, scal[s0, 1] / 23.0,
                     np.log1p(max(scal[s0, 2], 0)) / 12.0,
                     np.log1p(max(scal[s0, 3], 0)) / 12.0,
                     np.tanh((scal[s0, 2] - scal[s0, 3]) / 10000.0),
                     scal[s0, 4] / 16.0, scal[s0, 6] / 16.0, scal[s0, 7] / 4.0],
                    pn, np.log1p(np.maximum(minv[s0] - 9900, 0)) / 6.0,
                    seeds[s0] / 20.0, shed[s0] / 50.0,
                    board_summary(ts, d0) / 20.0,
                    board_summary(tiles_o[s0], d0) / 20.0,
                    [u == 0, (xx if xx >= 0 else 4) / 9.0, (yy if yy >= 0 else 4) / 9.0,
                     cinv.sum() / 10.0, cinv[3] / 5.0, cinv[10] / 5.0],
                    board_grid(ts),
                ]).astype(np.float32)                # 8+9+9+5+12+31+31+6+600 = 711
                ex, ey = pos_at(t, u)
                if 0 <= ex < 10 and 0 <= ey < 10:
                    X.append(glob)
                    yv.append(W2I[v])
                    yt.append(ex * 10 + ey)
                    yc.append(CROPS.index(arg) if v == "PLANT" and arg in CROPS else 0)
            seg_start[u] = t + 1
    if not X:
        return None
    return np.stack(X), np.array(yv, np.int16), np.array(yt, np.int16), \
        np.array(yc, np.int8), meta


def main():
    args = sys.argv[1:]
    dmin = int(args[args.index("--dmin") + 1]) if "--dmin" in args else 12
    cap = int(args[args.index("--cap") + 1]) if "--cap" in args else 150000
    outdir = os.path.join("results", "top10", "bc2")
    os.makedirs(outdir, exist_ok=True)
    files = sorted(glob.glob(os.path.join(TRAJ, "*.npz")))
    print(f"{len(files)} trajectory files, dmin={dmin}, per-team cap {cap:,}")
    rng = np.random.default_rng(0)
    tr = {"X": [], "v": [], "t": [], "c": []}
    va = {"X": [], "v": [], "t": [], "c": []}
    team_n = {}
    for i, f in enumerate(files):
        r = episode_samples(f, dmin)
        if r is None:
            continue
        X, yv, yt, yc, meta = r
        team = meta["team"]
        if team_n.get(team, 0) > cap and meta["episodeId"] % 10 != 0:
            continue                                  # cap applies to train only
        team_n[team] = team_n.get(team, 0) + len(yv)
        b = va if meta["episodeId"] % 10 == 0 else tr
        b["X"].append(X); b["v"].append(yv); b["t"].append(yt); b["c"].append(yc)
        if (i + 1) % 50 == 0:
            print(f"  [{i+1}/{len(files)}]")
    for name, b in (("train", tr), ("val", va)):
        X = np.concatenate(b["X"]); v = np.concatenate(b["v"])
        t = np.concatenate(b["t"]); c = np.concatenate(b["c"])
        np.savez_compressed(os.path.join(outdir, f"{name}.npz"), X=X, v=v, t=t, c=c)
        print(f"{name}: {X.shape[0]:,} samples, {X.shape[1]} features")
    print("per-team (post-cap):", team_n)
    dist = np.bincount(np.concatenate(tr["v"] + va["v"]), minlength=len(WORK))
    for w, nn in sorted(zip(WORK, dist), key=lambda p: -p[1]):
        print(f"  {w:<20}{nn:>10,}")


if __name__ == "__main__":
    main()
