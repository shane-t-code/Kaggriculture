"""Distillation rung 1 : the CROP-MIX HEAD.

Question: does the visible day-start state predict what a TOP TEAM plants
that day, beyond dumb baselines?  If yes, the head wires into r1v5's
planting quotas (car_target/whe_target) — learned judgment on top of the
repaired safe executor.

Design per the review-4 blueprint:
  - 29 UNIQUE episodes (manifest has one duplicate) split BY EPISODE
    18 train / 5 val / 6 test, rng seed 42, predeclared here.
  - Teachers = seats with initialScore >= 2900 (top-vs-top games teach both
    seats).  Teacher/team id kept per row for leave-team-out diagnostics.
  - Features: ONLY what the acting player sees at day start (public farms,
    prices, market inventories, revealed shops, own private seeds/shed).
    No future, no outcome, no replay/teacher identity as a feature.
  - Target: crops PLANTED that day that physically LAND (unit stands on an
    empty owned tile when the PLANT command executes — request-level counts
    inflate; note discipline).
  - Baselines: global mean; day-only; shops+day.  The model must beat both
    on held-out EPISODES or the head is not learned judgment.
Model: multi-output ridge regression, closed form, numpy only (runtime
budget: this is linear algebra, trivially <1ms on 1.6 vCPU).

Usage: python tools/mk_distill.py            (extract + train + report)
Artifacts: results/distill/day_samples.npz, split.json, report.json,
           ridge_weights.npz
"""
import glob
import gzip
import json
import os

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

CROPS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON"]
PRODUCTS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON",
            "EGG", "MILK", "WOOL", "FERTILIZER"]
SHOPS = ["BAKERY", "PIZZA_SHOP", "BRUNCH_SPOT", "YARN_STORE",
         "ICE_CREAM_SHOP", "PET_CAFE", "SMOOTHIE_SHOP", "FARMERS_MARKET"]
ANIMALS = ["GOOSE", "COW", "SHEEP"]
MOVES = {"NORTH", "SOUTH", "EAST", "WEST"}
D0, D1 = 10, 28
TEACHER_BAR = 2900.0


def farm_counts(farm):
    crop_n = {c: 0 for c in CROPS}
    ani_n = {a: 0 for a in ANIMALS}
    empt = weed = 0
    for row in farm["tiles"]:
        for t in row:
            if t is None:
                empt += 1
            elif isinstance(t, dict):
                if t.get("kind") == "PLANT":
                    crop_n[t["crop"]] = crop_n.get(t["crop"], 0) + 1
                elif t.get("kind") == "WEED":
                    weed += 1
                elif "animal" in t:
                    ani_n[t["animal"]] = ani_n.get(t["animal"], 0) + 1
    return crop_n, ani_n, empt, weed


def extract():
    man = json.load(open(r"replays/top10/manifest.json", encoding="utf-8"))
    scores = {}
    for row in man:
        eid = row["episode"]
        if eid in scores:
            continue
        scores[eid] = [a.get("initialScore", 0) or 0 for a in row["agents"]]
        scores[eid + 10**9] = [a.get("teamId") for a in row["agents"]]
    X, Y, meta = [], [], []
    files = sorted(glob.glob(r"replays/top10/ep_*.json.gz"))
    eps = []
    for f in files:
        eid = int(os.path.basename(f).split("_")[1].split(".")[0])
        if eid in {m[0] for m in eps}:
            continue
        eps.append((eid, f))
    for eid, f in eps:
        rep = json.load(gzip.open(f, "rt", encoding="utf-8"))
        steps = rep["steps"]
        if len(steps) < 700 or eid not in scores:
            continue
        for seat in (0, 1):
            if scores[eid][seat] < TEACHER_BAR:
                continue
            team = scores[eid + 10**9][seat]
            for d in range(D0, D1 + 1):
                t0 = d * 24
                obs = steps[t0][seat].get("observation") or steps[t0][0]["observation"]
                farm = obs["farms"][seat]
                opp = obs["farms"][1 - seat]
                priv = obs.get("private") or {}
                prices = obs["market"]["prices"]
                inv = obs["market"]["inventory"]
                shops = obs["town"].get("unlocked_shops", [])
                cn, an, empt, weed = farm_counts(farm)
                on, oan, oempt, _ = farm_counts(opp)
                prev_crew = len(steps[max(0, t0 - 12)][0]["observation"]
                                ["farms"][seat]["hands"])
                x = ([d, 29 - d]
                     + [shops.count(s) for s in SHOPS]
                     + [int(prices.get(p, 0)) for p in PRODUCTS]
                     + [int(inv.get(p, 0)) / 1000.0 for p in PRODUCTS]
                     + [float(farm.get("money", 0)) / 1000.0, prev_crew,
                        len(farm.get("unlocked_quadrants", []))]
                     + [int((priv.get("shed") or {}).get(p, 0)) for p in PRODUCTS]
                     + [int((priv.get("seeds") or {}).get(c, 0)) for c in CROPS]
                     + [cn[c] for c in CROPS] + [an[a] for a in ANIMALS]
                     + [empt, weed]
                     + [float(opp.get("money", 0)) / 1000.0]
                     + [on[c] for c in CROPS] + [oan[a] for a in ANIMALS]
                     + [oempt])
                # target: PHYSICAL plant births + hand-count increases (
                # review 5 §4: request-level counting was wrong on 50/760 rows
                # — seed contention, competing workers, silent fails; count the
                # tile transition None -> PLANT born this day instead)
                y = {c: 0 for c in CROPS}
                hires = 0
                for t in range(t0, min(t0 + 24, len(steps) - 1)):
                    fnow = steps[t][0]["observation"]["farms"][seat]
                    fnext = steps[t + 1][0]["observation"]["farms"][seat]
                    for y_ in range(len(fnow["tiles"])):
                        for x_, told in enumerate(fnow["tiles"][y_]):
                            tnew = fnext["tiles"][y_][x_]
                            if (told is None and isinstance(tnew, dict)
                                    and tnew.get("kind") == "PLANT"
                                    and tnew.get("planted_day") == d
                                    and tnew.get("crop") in y):
                                y[tnew["crop"]] += 1
                    hires += max(0, len(fnext["hands"]) - len(fnow["hands"]))
                X.append(x)
                Y.append([y[c] for c in CROPS] + [hires])
                meta.append({"episode": eid, "seat": seat, "team": team,
                             "day": d, "score": scores[eid][seat]})
    return np.array(X, dtype=np.float64), np.array(Y, dtype=np.float64), meta


FEATURE_NAMES = (["day", "days_left"] + [f"shop_{s}" for s in SHOPS]
                 + [f"p_{p}" for p in PRODUCTS] + [f"minv_{p}" for p in PRODUCTS]
                 + ["money", "prev_crew", "quads"]
                 + [f"shed_{p}" for p in PRODUCTS] + [f"seed_{c}" for c in CROPS]
                 + [f"my_{c}" for c in CROPS] + [f"my_{a}" for a in ANIMALS]
                 + ["my_empty", "my_weed", "opp_money"]
                 + [f"op_{c}" for c in CROPS] + [f"op_{a}" for a in ANIMALS]
                 + ["opp_empty"])


def ridge_fit(X, Y, lam=10.0):
    mu, sd = X.mean(0), X.std(0) + 1e-9
    Xs = (X - mu) / sd
    Xb = np.hstack([Xs, np.ones((len(Xs), 1))])
    A = Xb.T @ Xb + lam * np.eye(Xb.shape[1])
    W = np.linalg.solve(A, Xb.T @ Y)
    return mu, sd, W


def ridge_pred(mu, sd, W, X):
    Xs = (X - mu) / sd
    return np.hstack([Xs, np.ones((len(Xs), 1))]) @ W


def mae(a, b):
    return float(np.abs(a - b).mean(0).mean())


def main():
    os.makedirs(r"results/distill", exist_ok=True)
    X, Y, meta = extract()
    eps = sorted({m["episode"] for m in meta})
    rng = np.random.default_rng(42)
    order = list(rng.permutation(eps))
    n_tr = max(1, int(len(eps) * 0.6))
    n_va = max(1, int(len(eps) * 0.2))
    tr_e = set(order[:n_tr])
    va_e = set(order[n_tr:n_tr + n_va])
    te_e = set(order[n_tr + n_va:])
    grp = np.array([0 if m["episode"] in tr_e else 1 if m["episode"] in va_e
                    else 2 for m in meta])
    np.savez(r"results/distill/day_samples.npz", X=X, Y=Y, grp=grp)
    json.dump({"train": sorted(int(e) for e in tr_e),
               "val": sorted(int(e) for e in va_e),
               "test": sorted(int(e) for e in te_e), "n_rows": len(X),
               "features": FEATURE_NAMES,
               "targets": CROPS + ["HIRES"]},
              open(r"results/distill/split.json", "w"), indent=1)
    print(f"rows {len(X)} (episodes {len(eps)}: {len(tr_e)}/{len(va_e)}/{len(te_e)})"
          f"  features {X.shape[1]}")

    # --- iteration 2: 3-DAY FORWARD targets (teachers plant in bursts —
    # exact-day counts are noise; quotas need the coming days anyway) and
    # RESIDUAL-on-day-mean modeling (the head must explain state BEYOND the
    # calendar, so give the calendar away for free) ---
    series = {}
    for i, m in enumerate(meta):
        series.setdefault((m["episode"], m["seat"]), []).append(i)
    Y3 = np.zeros_like(Y)
    for key, idx in series.items():
        idx = sorted(idx, key=lambda i: meta[i]["day"])
        for k, i in enumerate(idx):
            Y3[i] = Y[idx[k:k + 3]].sum(0)
    Y = Y3

    tr, va, te = grp == 0, grp == 1, grp == 2
    rep = {}
    # baselines
    base_mean = Y[tr].mean(0)
    rep["baseline_mean"] = {"val": mae(Y[va], base_mean), "test": mae(Y[te], base_mean)}
    day_col = X[:, 0].astype(int)
    day_mean = {d: Y[tr][day_col[tr] == d].mean(0) if (day_col[tr] == d).any()
                else base_mean for d in range(D0, D1 + 1)}
    pv = np.array([day_mean[d] for d in day_col[va]])
    pt = np.array([day_mean[d] for d in day_col[te]])
    rep["baseline_day"] = {"val": mae(Y[va], pv), "test": mae(Y[te], pt)}
    shops_cols = list(range(0, 10))          # day, days_left + 8 shop counts
    Xs_ = X[:, shops_cols]
    mu, sd, W = ridge_fit(Xs_[tr], Y[tr])
    rep["baseline_shops_day"] = {
        "val": mae(Y[va], ridge_pred(mu, sd, W, Xs_[va])),
        "test": mae(Y[te], ridge_pred(mu, sd, W, Xs_[te]))}
    # the full-state head: ridge on the RESIDUAL from the train day-mean.
    # Iteration 3 (closed-loop screen 1W-6L): (a) DROP consequence features —
    # teachers' seed holdings are effects of their plan, and at runtime they
    # feed back (few seeds -> low prediction -> few buys); (b) pick lambda
    # PER TARGET (a single lam=1000 compressed the carrot head's range).
    drop = [i for i, n in enumerate(FEATURE_NAMES) if n.startswith("seed_")]
    keep = [i for i in range(X.shape[1]) if i not in drop]
    Xk = X[:, keep]
    dm_tr = np.array([day_mean[d] for d in day_col])
    R = Y - dm_tr
    lams = (1.0, 10.0, 30.0, 100.0, 300.0, 1000.0)
    fits = {}
    for lam in lams:
        mu, sd, W = ridge_fit(Xk[tr], R[tr], lam)
        fits[lam] = (mu, sd, W,
                     np.abs(Y[va] - (dm_tr[va] + ridge_pred(mu, sd, W, Xk[va]))).mean(0))
    lam_j = [min(lams, key=lambda l: fits[l][3][j]) for j in range(Y.shape[1])]
    mu, sd, _, _ = fits[lams[0]]
    W = np.column_stack([fits[lam_j[j]][2][:, j] for j in range(Y.shape[1])])
    P = dm_tr[te] + ridge_pred(mu, sd, W, Xk[te])
    v = mae(Y[va], dm_tr[va] + ridge_pred(mu, sd, W, Xk[va]))
    rep["ridge_full"] = {"val": v, "lam_per_target": dict(zip(CROPS + ["HIRES"],
                                                              lam_j)),
                         "test": mae(Y[te], P)}
    X = Xk                                  # downstream export uses kept set
    FN = [FEATURE_NAMES[i] for i in keep]
    # interpretability: strongest state features per crop head
    tops = {}
    for j, n in enumerate(CROPS):
        w = W[:-1, j]
        ix = np.argsort(-np.abs(w))[:6]
        tops[n] = {FN[i]: round(float(w[i]), 3) for i in ix}
    rep["top_weights"] = tops
    # per-target test MAE + correlation
    per = {}
    names = CROPS + ["HIRES"]
    for j, n in enumerate(names):
        c = (np.corrcoef(P[:, j], Y[te][:, j])[0, 1]
             if Y[te][:, j].std() > 0 else 0.0)
        bd = np.array([day_mean[d][j] for d in day_col[te]])
        per[n] = {"mae_model": float(np.abs(P[:, j] - Y[te][:, j]).mean()),
                  "mae_day": float(np.abs(bd - Y[te][:, j]).mean()),
                  "corr": round(float(c), 3),
                  "mean_true": round(float(Y[te][:, j].mean()), 2)}
    rep["per_target_test"] = per
    np.savez(r"results/distill/ridge_weights.npz", mu=mu, sd=sd, W=W,
             lam=np.array([lam]))
    json.dump(rep, open(r"results/distill/report.json", "w"), indent=1)
    print(json.dumps(rep, indent=1))

    # --- runtime export: refit on train+val at the chosen lambda (test
    # episodes stay untouched), dump plain-Python literals for the layer
    # (a 65-float dot product needs no numpy at inference) ---
    tv = tr | va
    day_mean_tv = {d: (Y[tv][day_col[tv] == d].mean(0)
                       if (day_col[tv] == d).any() else Y[tv].mean(0))
                   for d in range(D0, D1 + 1)}
    dmtv = np.array([day_mean_tv[d] for d in day_col])
    cols = [CROPS.index("WHEAT"), CROPS.index("CARROT")]
    mu2 = sd2 = None
    W2cols = []
    for j in cols:
        m_, s_, Wj = ridge_fit(X[tv], (Y - dmtv)[tv][:, [j]], lam_j[j])
        mu2, sd2 = m_, s_
        W2cols.append(Wj[:, 0])
    W2 = np.column_stack(W2cols)
    cols = [0, 1]                       # W2 now has exactly the two heads
    lit = {
        "feature_names": FN,
        "mu": [round(float(v), 6) for v in mu2],
        "sd": [max(round(float(v), 6), 1e-6) for v in sd2],
        "W_wheat": [round(float(v), 6) for v in W2[:, cols[0]]],
        "W_carrot": [round(float(v), 6) for v in W2[:, cols[1]]],
        "day_mean_wheat": {int(d): round(float(day_mean_tv[d][cols[0]]), 3)
                           for d in range(D0, D1 + 1)},
        "day_mean_carrot": {int(d): round(float(day_mean_tv[d][cols[1]]), 3)
                            for d in range(D0, D1 + 1)},
    }
    json.dump(lit, open(r"results/distill/head_lit.json", "w"))
    print("runtime literals -> results/distill/head_lit.json")


if __name__ == "__main__":
    main()
