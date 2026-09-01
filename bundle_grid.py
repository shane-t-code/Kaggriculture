#!/usr/bin/env python3
"""bundle_grid.py — designed test of the SCALE-SYNERGY hypothesis.

Evolution tests 1-3 knob changes; the scale hypothesis (more hands + 4th
quadrant + more plants, possibly + geese) needs 3-4 coordinated changes.
This evaluates a hand-designed grid of coordinated bundles against the
current search champion with the same field-primary S2 -> S3 gate.

Run on pod:  python3.13 bundle_grid.py --procs 32
"""
from __future__ import annotations
import argparse, json, os, time

import shape_search2 as S

CHAMP_GENOME = {
    "d0_sheep": 1, "d0_cow": 3, "d0_melon": 6, "d0_feed": 6, "d0_goose": 0,
    "sheep": 5, "cow": 6, "goose_max": 0, "goose_day": 10, "egg_bar": 7,
    "str_base": 40, "str_typ": 25, "hands": 8, "hands_q": 2,
    "land1": 6, "land2": 10, "land3": 26, "feed_mult10": 13, "res": 21,
    "convert_day": 19, "factory_day": 22, "care_skip": 15, "seed_mel": 3,
}

def bundles():
    out = {}
    # scale bundles: hands x SE-day x plant depth move TOGETHER
    for hands in (10, 12, 14):
        for land3 in (12, 14):
            for str_base in (40, 46):
                g = dict(CHAMP_GENOME, hands=hands, land3=land3,
                         str_base=str_base)
                out[f"h{hands}_se{land3}_s{str_base}"] = g
    # goose-enabled variants of the two most plausible scale points
    for hands, land3 in ((10, 12), (12, 12)):
        g = dict(CHAMP_GENOME, hands=hands, land3=land3, str_base=46,
                 d0_goose=2, d0_melon=4, goose_max=4, goose_day=6)
        out[f"h{hands}_se{land3}_goose"] = g
    return {k: g for k, g in out.items() if S.valid(g)}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--procs", type=int, default=32)
    args = ap.parse_args()
    S.PROCS = args.procs

    os.makedirs(S.TMP, exist_ok=True)
    base_src = open(S.BASE, encoding="utf-8").read()
    champ_path = os.path.join(S.TMP, "champion.py")
    with open(champ_path, "w", encoding="utf-8") as f:
        f.write(S.apply_genome(base_src, CHAMP_GENOME))

    cands = bundles()
    S.log(f"BUNDLE GRID: {len(cands)} coordinated bundles vs champion")
    paths = {}
    for i, (name, g) in enumerate(cands.items()):
        p = os.path.join(S.TMP, f"bundle_{name}.py")
        src = S.apply_genome(base_src, g)
        with open(p, "w", encoding="utf-8") as f:
            f.write(src)
        compile(src, p, "exec")
        paths[p] = (name, g)

    # S2-equivalent screen: 40 seeds, 5 legs, field-primary
    s2 = S.eval_stage(list(paths), champ_path, list(range(100, 140)),
                      ("mirror", "v40a", "tape", "egg", "straw"))
    ranked = sorted(s2.items(), key=lambda x: (-x[1][0], -x[1][1]))
    for p, (f2, t2, db, m2) in ranked:
        S.log(f"  {paths[p][0]:<18} field {f2:+4d} (mirror {m2:+4d}) dBank {db:+,.0f}")

    # S3 gate on the top 2
    for p, (f2, t2, db, m2) in ranked[:2]:
        if f2 < 4:
            S.log(f"BUNDLE {paths[p][0]}: below S3 bar (field {f2:+d}), skipping")
            continue
        s3 = S.eval_stage([p], champ_path, list(range(500, 650)),
                          ("mirror", "v40a", "tape", "wheat", "straw", "egg", "wool", "v12"))
        f3, t3, db3, m3 = s3[p]
        verdict = "PASSES GATE" if f3 >= 10 else "gate FAILED"
        S.log(f"BUNDLE S3 {paths[p][0]}: field {f3:+d} (mirror {m3:+d}) "
              f"dBank {db3:+,.0f} -> {verdict}")
        if f3 >= 10:
            with open("BUNDLE_WINNER.json", "w") as fo:
                json.dump({"name": paths[p][0], "genome": paths[p][1],
                           "s3": [f3, m3, db3]}, fo)
    with open("BUNDLE_DONE", "w") as f:
        f.write("done")
    S.log("BUNDLE GRID DONE")

if __name__ == "__main__":
    main()
