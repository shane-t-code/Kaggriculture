#!/usr/bin/env python3
"""Train BC v2: (task verb, target tile, crop) from macro segments.

MLP 711 -> 1024 -> 1024 -> {13 verb, 100 tile, 6 crop}. Weighted CE on verbs.
Reports verb acc, tile top-1/top-3, joint acc, d24+ cuts, DIG recall.
Exports numpy weights (results/top10/bc2/bc_v2.npz) for torch-free inference.

Usage: python tools/bc_train2.py [--epochs 12] [--bs 4096] [--h 1024]
"""
import sys, os, time
import numpy as np
import torch
import torch.nn as nn

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BC = os.path.join("results", "top10", "bc2")
WORK = ["WATER", "HARVEST", "PLANT", "FERTILIZE", "DIG", "FEED", "CARE",
        "COLLECT_FERTILIZER", "PICKUP", "DROP", "BUILD_COOP",
        "BUILD_PASTURE", "PLACE"]


class Net(nn.Module):
    def __init__(self, nin, h=1024):
        super().__init__()
        self.body = nn.Sequential(nn.Linear(nin, h), nn.ReLU(),
                                  nn.Linear(h, h), nn.ReLU())
        self.verb = nn.Linear(h, len(WORK))
        self.tile = nn.Linear(h, 100)
        self.crop = nn.Linear(h, 6)

    def forward(self, x):
        z = self.body(x)
        return self.verb(z), self.tile(z), self.crop(z)


def main():
    a = sys.argv[1:]
    epochs = int(a[a.index("--epochs") + 1]) if "--epochs" in a else 12
    bs = int(a[a.index("--bs") + 1]) if "--bs" in a else 4096
    h = int(a[a.index("--h") + 1]) if "--h" in a else 1024
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    tr = np.load(os.path.join(BC, "train.npz"))
    va = np.load(os.path.join(BC, "val.npz"))
    Xt = tr["X"]; vt = tr["v"].astype(np.int64)
    tt = tr["t"].astype(np.int64); ct = tr["c"].astype(np.int64)
    Xv = va["X"]; vv = va["v"].astype(np.int64)
    tv = va["t"].astype(np.int64); cv = va["c"].astype(np.int64)
    print(f"train {Xt.shape} val {Xv.shape} device {dev} h={h}")
    freq = np.bincount(vt, minlength=len(WORK)).astype(np.float64)
    w = 1.0 / np.sqrt(np.maximum(freq, 1)); w = w / w.sum() * len(WORK)
    net = Net(Xt.shape[1], h).to(dev)
    opt = torch.optim.Adam(net.parameters(), lr=1e-3)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=epochs)
    ce_v = nn.CrossEntropyLoss(weight=torch.tensor(w, dtype=torch.float32, device=dev))
    ce_t = nn.CrossEntropyLoss(); ce_c = nn.CrossEntropyLoss()
    Xt_t = torch.tensor(Xt, device=dev); vt_t = torch.tensor(vt, device=dev)
    tt_t = torch.tensor(tt, device=dev); ct_t = torch.tensor(ct, device=dev)
    n = len(vt); plant = WORK.index("PLANT")
    for ep in range(epochs):
        net.train(); perm = torch.randperm(n, device=dev); t0 = time.time(); tot = 0.0
        for i in range(0, n, bs):
            idx = perm[i:i + bs]
            lv, lt, lc = net(Xt_t[idx])
            loss = ce_v(lv, vt_t[idx]) + ce_t(lt, tt_t[idx])
            m = vt_t[idx] == plant
            if m.any():
                loss = loss + 0.3 * ce_c(lc[m], ct_t[idx][m])
            opt.zero_grad(); loss.backward(); opt.step()
            tot += float(loss.detach()) * len(idx)
        sched.step()
        net.eval()
        with torch.no_grad():
            pv, pt3, pt1 = [], [], []
            for i in range(0, len(vv), 65536):
                lv, lt, _ = net(torch.tensor(Xv[i:i + 65536], device=dev))
                pv.append(lv.argmax(1).cpu().numpy())
                top3 = lt.topk(3, dim=1).indices.cpu().numpy()
                pt1.append(top3[:, 0]); pt3.append(top3)
            pv = np.concatenate(pv); pt1 = np.concatenate(pt1)
            pt3 = np.concatenate(pt3)
        vacc = (pv == vv).mean()
        t1 = (pt1 == tv).mean()
        t3 = (pt3 == tv[:, None]).any(1).mean()
        joint = ((pv == vv) & (pt1 == tv)).mean()
        day = Xv[:, 0] * 29.0; late = day >= 24
        jl = ((pv == vv) & (pt1 == tv))[late].mean() if late.any() else float("nan")
        dig = vv == WORK.index("DIG")
        digr = (pv[dig] == vv[dig]).mean() if dig.any() else float("nan")
        print(f"ep {ep+1}: loss {tot/n:.3f} | verb {vacc:.3f} | tile@1 {t1:.3f} "
              f"@3 {t3:.3f} | joint {joint:.3f} (d24+ {jl:.3f}) | DIG {digr:.3f} "
              f"| {time.time()-t0:.0f}s")
    print("\nper-verb recall (val):")
    for i, vname in enumerate(WORK):
        m = vv == i
        if m.any():
            print(f"  {vname:<20}{(pv[m] == i).mean():6.3f}  (n={m.sum():,})")
    sd = {k: p.detach().cpu().numpy() for k, p in net.state_dict().items()}
    np.savez_compressed(os.path.join(BC, "bc_v2.npz"), **sd)
    print("saved", os.path.join(BC, "bc_v2.npz"))


if __name__ == "__main__":
    main()
