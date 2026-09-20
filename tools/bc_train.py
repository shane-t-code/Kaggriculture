#!/usr/bin/env python3
"""Train the v1 behavioral-clone net on results/top10/bc/{train,val}.npz.

Small MLP (92 -> 512 -> 512 -> 18 verbs, + 6-way crop head for PLANT rows).
Class-weighted CE for the heavy verb imbalance. Prints overall/late-game
accuracy and per-verb recall; saves weights as numpy npz (results/top10/bc/
bc_v1.npz) so inference needs NO torch (Kaggle = numpy-only forward pass).

Usage: python tools/bc_train.py [--epochs 4] [--bs 4096]
"""
import sys, os, time
import numpy as np
import torch
import torch.nn as nn

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BC = os.path.join("results", "top10", "bc")
VERBS = ["PASS", "NORTH", "SOUTH", "EAST", "WEST", "WATER", "HARVEST", "PLANT",
         "FERTILIZE", "DIG", "FEED", "CARE", "COLLECT_FERTILIZER", "PICKUP",
         "DROP", "BUILD_COOP", "BUILD_PASTURE", "PLACE"]


class Net(nn.Module):
    def __init__(self, nin, nverb=18, ncrop=6, h=512):
        super().__init__()
        self.body = nn.Sequential(
            nn.Linear(nin, h), nn.ReLU(),
            nn.Linear(h, h), nn.ReLU(),
        )
        self.verb = nn.Linear(h, nverb)
        self.crop = nn.Linear(h, ncrop)

    def forward(self, x):
        z = self.body(x)
        return self.verb(z), self.crop(z)


def main():
    args = sys.argv[1:]
    epochs = int(args[args.index("--epochs") + 1]) if "--epochs" in args else 4
    bs = int(args[args.index("--bs") + 1]) if "--bs" in args else 4096
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    tr = np.load(os.path.join(BC, "train.npz"))
    va = np.load(os.path.join(BC, "val.npz"))
    Xt, yt, ct = tr["X"], tr["y"].astype(np.int64), tr["crop"].astype(np.int64)
    Xv, yv, cv = va["X"], va["y"].astype(np.int64), va["crop"].astype(np.int64)
    print(f"train {Xt.shape}, val {Xv.shape}, device {dev}")
    freq = np.bincount(yt, minlength=len(VERBS)).astype(np.float64)
    w = 1.0 / np.sqrt(np.maximum(freq, 1))
    w = w / w.sum() * len(VERBS)
    net = Net(Xt.shape[1]).to(dev)
    opt = torch.optim.Adam(net.parameters(), lr=1e-3)
    ce_v = nn.CrossEntropyLoss(weight=torch.tensor(w, dtype=torch.float32, device=dev))
    ce_c = nn.CrossEntropyLoss()
    Xt_t = torch.tensor(Xt, device=dev)
    yt_t = torch.tensor(yt, device=dev)
    ct_t = torch.tensor(ct, device=dev)
    n = len(yt)
    plant_id = VERBS.index("PLANT")
    for ep in range(epochs):
        net.train()
        perm = torch.randperm(n, device=dev)
        t0, tot = time.time(), 0.0
        for i in range(0, n, bs):
            idx = perm[i:i + bs]
            xb, yb, cb = Xt_t[idx], yt_t[idx], ct_t[idx]
            lv, lc = net(xb)
            loss = ce_v(lv, yb)
            mask = yb == plant_id
            if mask.any():
                loss = loss + 0.3 * ce_c(lc[mask], cb[mask])
            opt.zero_grad(); loss.backward(); opt.step()
            tot += float(loss) * len(idx)
        # validation
        net.eval()
        with torch.no_grad():
            pv = []
            for i in range(0, len(yv), 65536):
                lv, _ = net(torch.tensor(Xv[i:i + 65536], device=dev))
                pv.append(lv.argmax(1).cpu().numpy())
            pv = np.concatenate(pv)
        acc = (pv == yv).mean()
        day = Xv[:, 0] * 29.0
        late = day >= 24
        acc_late = (pv[late] == yv[late]).mean() if late.any() else float("nan")
        dig = yv == VERBS.index("DIG")
        dig_rec = (pv[dig] == yv[dig]).mean() if dig.any() else float("nan")
        print(f"epoch {ep+1}: loss {tot/n:.4f} | val acc {acc:.3f} | "
              f"d24+ acc {acc_late:.3f} | DIG recall {dig_rec:.3f} | {time.time()-t0:.0f}s")
    # per-verb recall table
    print("\nper-verb recall (val):")
    for i, v in enumerate(VERBS):
        m = yv == i
        if m.any():
            print(f"  {v:<20}{(pv[m] == i).mean():6.3f}  (n={m.sum():,})")
    # export weights as plain numpy for engine-side inference
    sd = {k: p.detach().cpu().numpy() for k, p in net.state_dict().items()}
    np.savez_compressed(os.path.join(BC, "bc_v1.npz"), **sd)
    print("saved", os.path.join(BC, "bc_v1.npz"))


if __name__ == "__main__":
    main()
