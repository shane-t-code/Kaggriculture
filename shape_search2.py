#!/usr/bin/env python3
"""shape_search2.py — round-2 evolutionary shape search on the v42b base.

Round-1 lessons BAKED IN (do not regress these):
  - FIELD-PRIMARY everywhere: S1/S2 rank by field dWins (vs real opponents);
    the promotion gate is field-only; mirror is logged, never decides.
  - S3-rejected genomes are BANNED from future generations; elites are
    confirmed champions only.
  - Gene ranges must COVER what live winners do (hands to 14, SE quadrant,
    geese — round 1's hands cap of 9 was below the observed 12-16).
  - Opponent pool contains the 4 live-decoded archetype proxies + the meta
    tape, not just our own lineage.

Usage (pod):  nohup python3.13 shape_search2.py --hours 5.0 &
       local: python shape_search2.py --hours 2 --procs 8 --base versions/v42b.py
"""
from __future__ import annotations
import argparse, json, os, random, re, time

from pod_runner import _play   # (leg, p0, p1, seed) -> result dict

PROCS = 32
BASE = "versions/v42b.py"
OPPS = (("v40a",  "versions/v40a.py"),
        ("tape",  "versions/meta_boatlee.py"),
        ("wheat", "versions/proxy_wheatfarm.py"),
        ("straw", "versions/proxy_strglut.py"),
        ("egg",   "versions/proxy_eggmilk.py"),
        ("wool",  "versions/proxy_wool.py"),
        ("v12",   "versions/v12b.py"))
STATE = "search_state_shape2.json"
LOG = "shape_search2_log.txt"
TMP = "searchtmp_shape2"

# name: (lo, hi, default) — all verified to hit EXACTLY one site in v42b
GENES = {
    "d0_sheep":    (0, 4, 1),
    "d0_cow":      (1, 4, 3),
    "d0_melon":    (4, 12, 6),
    "d0_feed":     (5, 12, 8),
    "d0_goose":    (0, 3, 0),
    "sheep":       (2, 9, 5),
    "cow":         (4, 10, 6),
    # geese measured NET-NEGATIVE when latched late (30-seed sweep: 8W-22L
    # -3,490; latch d3 but SW slots open d10 -> ~15 egg-days < cost+feed).
    # Default OFF; the search may re-enable with an earlier latch it tunes.
    "goose_max":   (0, 4, 0),
    "goose_day":   (3, 14, 10),
    "egg_bar":     (5, 13, 7),
    "str_base":    (30, 48, 40),
    "str_typ":     (18, 32, 25),
    "hands":       (8, 14, 8),
    "hands_q":     (1, 3, 2),
    "land1":       (4, 8, 6),
    "land2":       (8, 13, 10),
    "land3":       (11, 26, 26),   # 26 == never buy SE (kept as 99 in code)
    "feed_mult10": (10, 25, 13),
    "res":         (0, 200, 21),
    "convert_day": (15, 24, 19),
    "factory_day": (16, 24, 22),
    "care_skip":   (5, 25, 15),
    "seed_mel":    (2, 6, 3),
}

def _edits(g):
    land3 = 99 if g["land3"] >= 26 else g["land3"]
    return [
        (r'D0_SHEEP = 1', 'D0_SHEEP = %d' % g["d0_sheep"], 1),
        (r'D0_COW = 3', 'D0_COW = %d' % g["d0_cow"], 1),
        (r'D0_MELON = 6', 'D0_MELON = %d' % g["d0_melon"], 1),
        (r'D0_FEED = 8', 'D0_FEED = %d' % g["d0_feed"], 1),
        (r'D0_GOOSE = 0', 'D0_GOOSE = %d' % g["d0_goose"], 1),
        (r'ANIMAL_TARGETS = \{"SHEEP": 5, "COW": 6\}',
         'ANIMAL_TARGETS = {"SHEEP": %d, "COW": %d}' % (g["sheep"], g["cow"]), 1),
        (r'_GOOSE_TARGET\[player\] = 4', '_GOOSE_TARGET[player] = %d' % g["goose_max"], 1),
        (r'\.get\(player, 0\) < 4', '.get(player, 0) < %d' % max(1, g["goose_max"]), 1),
        (r'day <= 14\n                and _town_drain_per_day\("EGG", shops\) >= 7',
         'day <= %d\n                and _town_drain_per_day("EGG", shops) >= %d'
         % (g["goose_day"], g["egg_bar"]), 1),
        (r'int\(round\(40 \* proj / 25\.0\)\)',
         'int(round(%d * proj / %d.0))' % (g["str_base"], g["str_typ"]), 1),
        (r'max\(12, min\(48, cap\)\)', 'max(12, min(%d, cap))' % max(20, g["str_base"] + 0), 1),
        (r'TARGET_HANDS = 8', 'TARGET_HANDS = %d' % g["hands"], 1),
        (r'HANDS_PER_EXTRA_QUADRANT = 2', 'HANDS_PER_EXTRA_QUADRANT = %d' % g["hands_q"], 1),
        (r'LAND_DAYS = \[6, 10, 99\]',
         'LAND_DAYS = [%d, %d, %d]' % (g["land1"], g["land2"], land3), 1),
        (r'wheat_price \* 1\.3', 'wheat_price * %.1f' % (g["feed_mult10"] / 10.0), 1),
        (r'_res = 21 if', '_res = %d if' % g["res"], 1),
        (r'ENDGAME_CONVERT_DAY = 19', 'ENDGAME_CONVERT_DAY = %d' % g["convert_day"], 1),
        (r'WHEAT_FACTORY_DAY = 22', 'WHEAT_FACTORY_DAY = %d' % g["factory_day"], 1),
        (r'CARE_SKIP_PRICE = 15', 'CARE_SKIP_PRICE = %d' % g["care_skip"], 1),
        (r'"MELON": 3', '"MELON": %d' % g["seed_mel"], 1),
    ]

def apply_genome(src, g):
    for pat, rep, n in _edits(g):
        src, cnt = re.subn(pat, rep, src)
        if cnt != n:
            raise ValueError(f"pattern {pat!r} matched {cnt}, expected {n}")
    return src

def valid(g):
    basket = (g["d0_sheep"] * 500 + g["d0_cow"] * 400 + g["d0_goose"] * 300
              + g["d0_melon"] * 80 + 70 + g["d0_feed"] * 25)
    if basket > 2950:
        return False
    if g["sheep"] + g["cow"] + g["goose_max"] > 15:      # ANIMAL_SLOTS
        return False
    if g["d0_goose"] > g["goose_max"]:
        return False
    if g["d0_sheep"] > g["sheep"] or g["d0_cow"] > g["cow"]:
        return False
    if not (g["land1"] < g["land2"]):
        return False
    if g["land3"] < 26 and g["land3"] <= g["land2"]:
        return False
    if g["str_typ"] >= g["str_base"] + 10:
        return False
    return True

def mutate(champ, rng, n_genes=None):
    for _ in range(200):
        g = dict(champ)
        for k in rng.sample(list(GENES), n_genes or rng.choice((1, 2, 2, 3))):
            lo, hi, _ = GENES[k]
            g[k] = rng.randint(lo, hi)
        if g != champ and valid(g):
            return g
    return dict(champ)

def crossover(a, b, rng):
    g = {k: (a if rng.random() < 0.5 else b)[k] for k in GENES}
    return g if valid(g) else dict(a)

def write_candidate(base_src, g, i):
    path = os.path.join(TMP, f"cand_{i}.py")
    src = apply_genome(base_src, g)
    with open(path, "w", encoding="utf-8") as f:
        f.write(src)
    compile(src, path, "exec")
    return path

def run_games(jobs):
    from multiprocessing import Pool
    with Pool(PROCS) as pool:
        return list(pool.imap_unordered(_play, jobs, chunksize=4))

def score(results, a_path, b_path):
    """(field_dw, total_dw, dbank, mirror_dw) — FIELD FIRST."""
    def bank(r, p):
        return r["banks"][0] if r["p0"] == p else r["banks"][1]
    dw_mirror = 0
    db = 0.0
    n = 0
    for r in results:
        if r["leg"] != "mirror" or a_path not in (r["p0"], r["p1"]):
            continue
        a, b = bank(r, a_path), bank(r, b_path)
        dw_mirror += (1 if a > b else 0) - (1 if a < b else 0)
        db += a - b
        n += 1
    dw_field = 0
    for leg, opp in OPPS:
        A = {}
        B = {}
        for r in results:
            if r["leg"] != leg:
                continue
            for me, d in ((a_path, A), (b_path, B)):
                if me in (r["p0"], r["p1"]):
                    d[(r["seed"], 0 if r["p0"] == me else 1)] = (
                        bank(r, me) - bank(r, opp))
        ks = set(A) & set(B)
        for k in ks:
            dw_field += (1 if A[k] > 0 else 0) - (1 if B[k] > 0 else 0)
            db += A[k] - B[k]
            n += 1
    return dw_field, dw_field + dw_mirror, (db / max(1, n)), dw_mirror

def eval_stage(cands, champ_path, seeds, legs):
    jobs = []
    for path in cands:
        for s in seeds:
            if "mirror" in legs:
                jobs.append(("mirror", path, champ_path, s))
                jobs.append(("mirror", champ_path, path, s))
            for lname, opp in OPPS:
                if lname in legs:
                    for me in (path, champ_path):
                        jobs.append((lname, me, opp, s))
                        jobs.append((lname, opp, me, s))
    jobs = list(dict.fromkeys(jobs))
    results = run_games(jobs)
    return {path: score(results, path, champ_path) for path in cands}

def log(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def main():
    global PROCS, BASE
    ap = argparse.ArgumentParser()
    ap.add_argument("--hours", type=float, default=5.0)
    ap.add_argument("--procs", type=int, default=32)
    ap.add_argument("--base", default=BASE)
    args = ap.parse_args()
    PROCS = args.procs
    BASE = args.base

    os.makedirs(TMP, exist_ok=True)
    t0 = time.time()
    rng = random.Random(20260901)
    champion_genome = {k: v[2] for k, v in GENES.items()}
    base_src = open(BASE, encoding="utf-8").read()
    champ_path = os.path.join(TMP, "champion.py")
    with open(champ_path, "w", encoding="utf-8") as f:
        f.write(base_src)
    gen = 0
    history = []
    rejected = []
    if os.path.exists(STATE):
        st = json.load(open(STATE))
        champion_genome = st["champion_genome"]
        gen = st["gen"]
        history = st["history"]
        rejected = st.get("rejected", [])
        rng.setstate(tuple(st["rng"][0:1] + [tuple(st["rng"][1])] + st["rng"][2:]))
        with open(champ_path, "w", encoding="utf-8") as f:
            f.write(apply_genome(base_src, champion_genome)
                    if champion_genome != {k: v[2] for k, v in GENES.items()}
                    else base_src)
        log(f"RESUMED at gen {gen}")

    S1_SEEDS = list(range(0, 16))
    S2_SEEDS = list(range(100, 140))
    S3_SEEDS = list(range(500, 650))

    while (time.time() - t0) / 3600 < args.hours:
        gen += 1
        banned = rejected + [champion_genome]
        pop = []
        tries = 0
        while len(pop) < 18 and tries < 400:
            g = mutate(champion_genome, rng)
            tries += 1
            if g not in banned and g not in pop:
                pop.append(g)
        elites = [h["genome"] for h in history[-4:] if h.get("champ")]
        for i in range(4):
            if len(elites) >= 2:
                g = crossover(rng.choice(elites), rng.choice(elites), rng)
            else:
                g = mutate(champion_genome, rng, n_genes=4)
            if g not in banned and g not in pop:
                pop.append(g)
        paths = {}
        for i, g in enumerate(pop):
            try:
                paths[write_candidate(base_src, g, i)] = g
            except ValueError as e:
                log(f"gen{gen} cand{i} genome rejected: {e}")
        # S1 screen: cheap field legs (flagship + the two biggest live gaps)
        s1 = eval_stage(list(paths), champ_path, S1_SEEDS, ("mirror", "v40a", "wheat"))
        top = sorted(s1.items(), key=lambda x: (-x[1][0], -x[1][1]))[:6]
        log(f"gen{gen} S1 best(field): {[(os.path.basename(p), v[0]) for p, v in top[:3]]}")
        # S2 confirm: add tape + egg + straw
        s2 = eval_stage([p for p, _ in top], champ_path, S2_SEEDS,
                        ("mirror", "v40a", "tape", "egg", "straw"))
        best_path, (best_f, best_t, best_db, best_m) = sorted(
            s2.items(), key=lambda x: (-x[1][0], -x[1][1]))[0]
        log(f"gen{gen} S2 best {os.path.basename(best_path)} field {best_f:+d} "
            f"(mirror {best_m:+d}) dBank {best_db:+,.0f} genome {paths[best_path]}")
        promoted = False
        if best_f >= 4:
            s3 = eval_stage([best_path], champ_path, S3_SEEDS,
                            ("mirror", "v40a", "tape", "wheat", "straw", "egg", "wool", "v12"))
            f3, t3, db3, m3 = s3[best_path]
            log(f"gen{gen} S3 HELD-OUT: field {f3:+d} (mirror {m3:+d}) dBank {db3:+,.0f}")
            if f3 >= 10:
                promoted = True
                champion_genome = paths[best_path]
                with open(champ_path, "w", encoding="utf-8") as f:
                    f.write(apply_genome(base_src, champion_genome))
                log(f"gen{gen} *** NEW CHAMPION *** {champion_genome}")
            else:
                rejected.append(paths[best_path])
                log(f"gen{gen} S3 gate FAILED -> genome banned")
        history.append({"gen": gen, "genome": paths[best_path],
                        "s2": [best_f, best_db], "champ": promoted})
        st = {"gen": gen, "champion_genome": champion_genome,
              "history": history, "rejected": rejected,
              "rng": [rng.getstate()[0], list(rng.getstate()[1]),
                      rng.getstate()[2]]}
        with open(STATE, "w") as f:
            json.dump(st, f)
        log(f"gen{gen} done | elapsed {(time.time() - t0) / 3600:.2f}h")

    log("FINAL VALIDATION, seeds 700-900")
    final = eval_stage([champ_path], BASE, list(range(700, 900)),
                       ("mirror", "v40a", "tape", "wheat", "straw", "egg", "wool", "v12"))
    f3, t3, db3, m3 = final[champ_path]
    log(f"FINAL vs v42b-base: field {f3:+d} (mirror {m3:+d}) dBank {db3:+,.0f} "
        f"| genome {champion_genome}")
    with open("SEARCH2_DONE", "w") as f:
        f.write("done")

if __name__ == "__main__":
    main()
