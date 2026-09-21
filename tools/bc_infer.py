#!/usr/bin/env python3
"""Numpy-only BC v2 inference: live observation -> per-unit (task, tile, crop).

No torch. Loads results/top10/bc2/bc_v2.npz weights and rebuilds features from
a live/replay observation dict via the SAME encoders used for training
(traj_encode.enc_tiles + bc_dataset2.board_summary/board_grid) so train and
inference cannot skew.

Self-test: python tools/bc_infer.py  -> parity check vs val.npz (verb/tile acc
must match bc_train2's last-epoch numbers).
"""
import sys, os, json
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from traj_encode import enc_tiles, MKT_PRODUCTS, PRODUCTS, CROPS  # noqa: E402
from bc_dataset2 import board_summary, board_grid, PRICE_BASE, WORK  # noqa: E402

BC2 = os.path.join("results", "top10", "bc2")


class BCNet:
    def __init__(self, path=os.path.join(BC2, "bc_v2.npz")):
        z = np.load(path)
        self.w = {k: z[k] for k in z.files}

    def forward(self, X):
        z = X @ self.w["body.0.weight"].T + self.w["body.0.bias"]
        np.maximum(z, 0, out=z)
        z = z @ self.w["body.2.weight"].T + self.w["body.2.bias"]
        np.maximum(z, 0, out=z)
        lv = z @ self.w["verb.weight"].T + self.w["verb.bias"]
        lt = z @ self.w["tile.weight"].T + self.w["tile.bias"]
        lc = z @ self.w["crop.weight"].T + self.w["crop.bias"]
        return lv, lt, lc


def softmax(x):
    e = np.exp(x - x.max(axis=-1, keepdims=True))
    return e / e.sum(axis=-1, keepdims=True)


def features_from_obs(obs, seat):
    """Build the 711-feature vector base (unit part filled per unit)."""
    farms = obs["farms"]
    pl = obs.get("player", seat)
    fs, fo = farms[pl], farms[1 - pl]
    day, hour = obs.get("day", 0), obs.get("hour", 0)
    step = obs.get("step", day * 24 + hour)
    ts = enc_tiles(fs, day, step).astype(np.int16)
    to = enc_tiles(fo, day, step).astype(np.int16)
    mk = obs.get("market", {})
    pr = np.array([mk.get("prices", {}).get(p, 0) for p in MKT_PRODUCTS],
                  dtype=np.float32)
    iv = np.array([mk.get("inventory", {}).get(p, 0) for p in MKT_PRODUCTS],
                  dtype=np.float32)
    pv = obs.get("private", {})
    seeds = np.array([min(pv.get("seeds", {}).get(c, 0), 9999)
                      for c in CROPS[1:]], dtype=np.float32)
    shed = np.array([min(pv.get("shed", {}).get(p, 0), 9999)
                     for p in PRODUCTS], dtype=np.float32)
    glob = np.concatenate([
        [day / 29.0, hour / 23.0,
         np.log1p(max(fs.get("money", 0), 0)) / 12.0,
         np.log1p(max(fo.get("money", 0), 0)) / 12.0,
         np.tanh((fs.get("money", 0) - fo.get("money", 0)) / 10000.0),
         len(fs.get("hands", [])) / 16.0, fs.get("hires_today", 0) / 16.0,
         len(fs.get("unlocked_quadrants", [])) / 4.0],
        pr / PRICE_BASE, np.log1p(np.maximum(iv - 9900, 0)) / 6.0,
        seeds / 20.0, shed / 50.0,
        board_summary(ts, day) / 20.0, board_summary(to, day) / 20.0,
    ]).astype(np.float32)                       # 74+31 = 105 (before unit + grid)
    grid = board_grid(ts)
    return glob, grid, fs, pv


def unit_features(glob, grid, fs, pv, uid):
    """uid 0 = farmer, 1.. = hands."""
    if uid == 0:
        pos = fs.get("farmer", [4, 4])
    else:
        hands = fs.get("hands", [])
        pos = hands[uid - 1] if uid - 1 < len(hands) else [4, 4]
    invs = pv.get("inventories") or []
    cinv = np.zeros(12, dtype=np.float32)
    if uid < len(invs):
        for p, q in (invs[uid] or {}).items():
            if p in PRODUCTS:
                cinv[PRODUCTS.index(p)] = min(q, 999)
    ufeat = np.array([uid == 0, pos[0] / 9.0, pos[1] / 9.0,
                      cinv.sum() / 10.0, cinv[3] / 5.0, cinv[10] / 5.0],
                     dtype=np.float32)
    return np.concatenate([glob, ufeat, grid])


def plan(net, obs, seat, units=None):
    """Return [(uid, verb, (x, y), crop, p_verb, p_tile)] for requested units."""
    glob, grid, fs, pv = features_from_obs(obs, seat)
    n_units = 1 + len(fs.get("hands", []))
    ids = units if units is not None else list(range(n_units))
    X = np.stack([unit_features(glob, grid, fs, pv, u) for u in ids])
    lv, lt, lc = net.forward(X)
    pvb, ptl, pcr = softmax(lv), softmax(lt), softmax(lc)
    out = []
    for i, u in enumerate(ids):
        vi = int(pvb[i].argmax()); ti = int(ptl[i].argmax())
        out.append((u, WORK[vi], (ti // 10, ti % 10),
                    CROPS[int(pcr[i].argmax())] if WORK[vi] == "PLANT" else "",
                    float(pvb[i][vi]), float(ptl[i][ti])))
    return out


def _selftest():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    net = BCNet()
    va = np.load(os.path.join(BC2, "val.npz"))
    X, v, t = va["X"], va["v"], va["t"]
    accs_v, accs_t, joint = [], [], []
    for i in range(0, len(v), 65536):
        lv, lt, _ = net.forward(X[i:i + 65536])
        pv, pt = lv.argmax(1), lt.argmax(1)
        accs_v.append(pv == v[i:i + 65536])
        accs_t.append(pt == t[i:i + 65536])
        joint.append((pv == v[i:i + 65536]) & (pt == t[i:i + 65536]))
    print(f"numpy parity: verb acc {np.concatenate(accs_v).mean():.3f} | "
          f"tile@1 {np.concatenate(accs_t).mean():.3f} | "
          f"joint {np.concatenate(joint).mean():.3f}")
    print("(must match bc_train2's final epoch — else train/infer skew)")


if __name__ == "__main__":
    _selftest()
