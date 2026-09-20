#!/usr/bin/env python3
"""Build BC training tensors from results/top10/traj/*.npz.

One sample per (step, unit) for days D_MIN..29: features describe what that
unit and its farm see; the label is the verb the top-10 team issued to that
unit (moves collapsed to 4 move classes), plus a crop sub-label for PLANT.

Split is BY EPISODE (val = episodes whose id % 10 == 0) so the net is never
graded on steps of games it trained on.

Usage: python tools/bc_dataset.py [--dmin 12] [--out results/top10/bc]
"""
import sys, os, json, glob
import numpy as np

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TRAJ = os.path.join("results", "top10", "traj")
CROPS = ["", "CARROT", "MELON", "STRAWBERRY", "TOMATO", "WHEAT"]
# label vocabulary: index = class id
VERBS = ["PASS", "NORTH", "SOUTH", "EAST", "WEST", "WATER", "HARVEST", "PLANT",
         "FERTILIZE", "DIG", "FEED", "CARE", "COLLECT_FERTILIZER", "PICKUP",
         "DROP", "BUILD_COOP", "BUILD_PASTURE", "PLACE"]
V2I = {v: i for i, v in enumerate(VERBS)}
PRICE_BASE = np.array([40, 55, 55, 130, 160, 120, 60, 20, 200], dtype=np.float32)
# tile field indices (tools/traj_encode.py TFIELDS)
F_KIND, F_CROP, F_PLANTED, F_WATERED, F_CUW, F_FERT, F_YIELD, F_LIFE, \
    F_ANIMAL, F_FED, F_CARED, F_CUNF, F_FAVAIL, F_CBONUS, F_PLACED = range(15)


def board_summary(tiles, day):
    """Aggregate features of one farm's 100-tile board at one step."""
    kind = tiles[:, F_KIND]
    crop = tiles[:, F_CROP]
    out = []
    plant = kind == 2
    for c in range(1, 6):
        m = plant & (crop == c)
        out.append(m.sum())
        out.append((m & (tiles[:, F_WATERED] == 0)).sum())
        out.append(tiles[m, F_YIELD].sum() if m.any() else 0)
    # inert = plant with yield 0 and old
    out.append((plant & (tiles[:, F_YIELD] == 0) & (day - tiles[:, F_PLANTED] > 6)).sum())
    out.append((kind == 0).sum())            # empty tiles
    out.append((kind == 1).sum())            # locked
    for a in range(1, 4):
        m = tiles[:, F_ANIMAL] == a
        out.append(m.sum())
        out.append((m & (tiles[:, F_FED] == 0)).sum())
        out.append((m & (tiles[:, F_CARED] == 0)).sum())
        out.append(tiles[m, F_YIELD].sum() if m.any() else 0)
    out.append((tiles[:, F_FAVAIL] > 0).sum())
    return np.array(out, dtype=np.float32)    # 5*3+3+3*4+1 = 31


def episode_samples(path, dmin):
    z = np.load(path, allow_pickle=True)
    meta = json.loads(str(z["meta"]))
    vocab = list(z["vocab"])
    scal, prices, minv = z["scal"], z["prices"], z["minv"]
    tiles_s = z["tiles_self"]
    fpos, hpos = z["fpos"], z["hpos"]
    seeds, shed, carry = z["seeds"], z["shed"], z["carry"]
    act_f, act_h = z["act_f"], z["act_h"]
    n = len(scal)
    X, y, ycrop, tstep = [], [], [], []
    for t in range(n):
        day = scal[t, 0]
        if day < dmin:
            continue
        ts = tiles_s[t]
        bsum = board_summary(ts, day)
        pn = prices[t] / PRICE_BASE
        glob_feat = np.concatenate([
            [day / 29.0, scal[t, 1] / 23.0,
             np.log1p(max(scal[t, 2], 0)) / 12.0, np.log1p(max(scal[t, 3], 0)) / 12.0,
             np.tanh((scal[t, 2] - scal[t, 3]) / 10000.0),
             scal[t, 4] / 16.0, scal[t, 6] / 16.0, scal[t, 7] / 4.0],
            pn, np.log1p(np.maximum(minv[t] - 9900, 0)) / 6.0,
            seeds[t] / 20.0, shed[t] / 50.0, bsum / 20.0,
        ]).astype(np.float32)                  # 8+9+9+5+12+31 = 74
        # units: farmer (index 0) + hands
        nh = int(scal[t, 4])
        units = [(0, fpos[t], act_f[t], carry[t, 0])]
        for j in range(min(nh, 16)):
            units.append((j + 1, hpos[t, j], act_h[t, j], carry[t, j + 1]))
        for uid, pos, act, cinv in units:
            vs = vocab[act[0]] if act[0] < len(vocab) else ""
            if vs not in V2I:
                continue
            xx, yy = int(pos[0]), int(pos[1])
            if xx < 0:
                continue
            tile = ts[xx * 10 + yy] if 0 <= xx < 10 and 0 <= yy < 10 else np.zeros(15, np.int16)
            local = np.array([
                uid == 0, xx / 9.0, yy / 9.0,
                (abs(xx - 4.5) + abs(yy - 4.5)) / 9.0,
                tile[F_KIND] == 2, tile[F_CROP] / 5.0, tile[F_WATERED],
                tile[F_CUW] / 2.0, tile[F_FERT] / 3.0, tile[F_YIELD] / 4.0,
                min(tile[F_LIFE], 200) / 200.0, tile[F_ANIMAL] / 3.0,
                tile[F_FED], tile[F_CARED], tile[F_FAVAIL],
                cinv.sum() / 10.0, cinv[3] / 5.0, cinv[10] / 5.0,
            ], dtype=np.float32)               # 18
            X.append(np.concatenate([glob_feat, local]))
            y.append(V2I[vs])
            c = 0
            if vs == "PLANT":
                arg = vocab[act[1]] if act[1] < len(vocab) else ""
                c = CROPS.index(arg) if arg in CROPS else 0
            ycrop.append(c)
            tstep.append(t)
    if not X:
        return None
    return (np.stack(X), np.array(y, np.int16), np.array(ycrop, np.int8),
            np.array(tstep, np.int16), meta)


def main():
    dmin = 12
    outdir = os.path.join("results", "top10", "bc")
    args = sys.argv[1:]
    if "--dmin" in args:
        dmin = int(args[args.index("--dmin") + 1])
    if "--out" in args:
        outdir = args[args.index("--out") + 1]
    os.makedirs(outdir, exist_ok=True)
    files = sorted(glob.glob(os.path.join(TRAJ, "*.npz")))
    print(f"{len(files)} trajectory files, dmin={dmin}")
    tr, va = {"X": [], "y": [], "c": []}, {"X": [], "y": [], "c": []}
    counts = {}
    for i, f in enumerate(files):
        r = episode_samples(f, dmin)
        if r is None:
            continue
        X, y, c, tstep, meta = r
        bucket = va if meta["episodeId"] % 10 == 0 else tr
        bucket["X"].append(X); bucket["y"].append(y); bucket["c"].append(c)
        counts[meta["team"]] = counts.get(meta["team"], 0) + len(y)
        if (i + 1) % 50 == 0:
            print(f"  [{i+1}/{len(files)}]")
    for name, b in (("train", tr), ("val", va)):
        X = np.concatenate(b["X"]); y = np.concatenate(b["y"]); c = np.concatenate(b["c"])
        np.savez_compressed(os.path.join(outdir, f"{name}.npz"), X=X, y=y, crop=c)
        print(f"{name}: {X.shape[0]:,} samples, {X.shape[1]} features")
    print("per-team samples:", counts)
    dist = np.bincount(np.concatenate(tr["y"] + va["y"]), minlength=len(VERBS))
    for v, n in sorted(zip(VERBS, dist), key=lambda t: -t[1]):
        print(f"  {v:<20}{n:>10,}")


if __name__ == "__main__":
    main()
