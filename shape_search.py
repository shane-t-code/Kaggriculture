#!/usr/bin/env python3
"""shape_search.py — population search over the v37 MONSTER SHAPE.

Runs ON the pod. Unlike opening_search.py (which tuned the old herd
family's dials), this searches the monster skeleton's STRUCTURAL genes:
the day-0 all-in basket, herd size and mix (cow-heavy vs sheep-heavy —
SHALWIN won with 10 sheep), the berry-flood threshold, conversion day,
reserve philosophy, land clock. Base agent: versions/v37d.py.

Gate reform : champion promotion is dWins-primary on a
REPRESENTATIVE pool (v31b flagship + meta tape + v12) — dBank is logged
but no longer gates (it rejected win-positive/bank-negative adversarial
play). Field legs must still be non-negative (mirror-law guard).

Stages per generation (seeds disjoint by stage):
  S1  screen : 16 seeds, mirror(vs champ) + v31b
  S2  confirm: 48 seeds, mirror + v31b + tape
  S3  gate   : 200 HELD-OUT seeds, mirror + v31b + tape + v12
Final: ultimate champion vs versions/v37d.py AND main.py on seeds 700-999.

Checkpoints search_state_shape.json each generation. Self-terminates
after --hours (default 5.0).
"""
import argparse, json, os, random, re, sys, time
from multiprocessing import Pool

from pod_runner import _play   # (leg, p0, p1, seed) -> result dict

PROCS = 32
BASE = "versions/v37d.py"
OPPS = (("v31b", "main.py"),
        ("tape", "versions/meta_boatlee.py"),
        ("v12", "versions/v12b.py"))
TMP = "searchtmp_shape"
STATE = "search_state_shape.json"
LOG = "shape_search_log.txt"

# gene: (lo, hi, current-champion value)
GENES = {
    "d0_sheep":    (1, 4, 2),
    "d0_cow":      (1, 3, 2),
    "d0_melon":    (6, 14, 10),
    "d0_feed":     (4, 14, 8),
    "sheep":       (2, 10, 4),
    "cow":         (6, 12, 11),
    "str_cap":     (32, 45, 40),
    "flood":       (2000, 5000, 3000),
    "convert_day": (15, 24, 18),
    "feed_mult10": (10, 30, 15),
    "hands":       (6, 9, 8),
    "factory_day": (16, 24, 22),
    "land1":       (5, 8, 6),
    "land2":       (8, 13, 10),
    "res":         (0, 400, 150),
}

def apply_genome(src, g):
    # (pattern, replacement, expected substitution count)
    subs = [
        (r'ANIMAL_TARGETS = \{"SHEEP": \d+, "COW": \d+\}',
         f'ANIMAL_TARGETS = {{"SHEEP": {g["sheep"]}, "COW": {g["cow"]}}}', 1),
        (r'D0_SHEEP = \d+', f'D0_SHEEP = {g["d0_sheep"]}', 1),
        (r'D0_COW = \d+', f'D0_COW = {g["d0_cow"]}', 1),
        (r'D0_MELON = \d+', f'D0_MELON = {g["d0_melon"]}', 1),
        (r'D0_FEED = \d+', f'D0_FEED = {g["d0_feed"]}', 1),
        (r'("STRAWBERRY": \{"cost": 100,[^}]*"cap": )\d+',
         lambda m: m.group(1) + str(g["str_cap"]), 1),
        (r'money >= 3000', f'money >= {g["flood"]}', 4),  # 3 gates + STATUS doc
        (r'ENDGAME_CONVERT_DAY = \d+', f'ENDGAME_CONVERT_DAY = {g["convert_day"]}', 1),
        (r'\* wheat_price \* 1\.5\)', f'* wheat_price * {g["feed_mult10"] / 10})', 1),
        (r'TARGET_HANDS = \d+', f'TARGET_HANDS = {g["hands"]}', 1),
        (r'WHEAT_FACTORY_DAY = \d+', f'WHEAT_FACTORY_DAY = {g["factory_day"]}', 1),
        (r'day >= \(\d+ if n_quadrants == 1 else \d+\)',
         f'day >= ({g["land1"]} if n_quadrants == 1 else {g["land2"]})', 1),
        (r'_res = \d+ if', f'_res = {g["res"]} if', 1),
    ]
    for pat, rep, want in subs:
        src, n = re.subn(pat, rep, src)
        if n != want:
            raise ValueError(f"pattern applied {n}x (want {want}): {pat[:50]}")
    return src

def valid(g):
    basket = (g["d0_sheep"] * 500 + g["d0_cow"] * 400 + g["d0_melon"] * 80
              + 70 + g["d0_feed"] * 30)
    return (basket <= 2950
            and g["sheep"] + g["cow"] <= 15          # ANIMAL_SLOTS
            and g["d0_sheep"] <= g["sheep"] and g["d0_cow"] <= g["cow"]
            and g["land2"] > g["land1"]
            and all(GENES[k][0] <= v <= GENES[k][1] for k, v in g.items()))

def mutate(g, rng, n_genes=None):
    g = dict(g)
    for _ in range(200):
        cand = dict(g)
        for k in rng.sample(list(GENES), n_genes or rng.randint(1, 3)):
            lo, hi, _ = GENES[k]
            step = max(1, (hi - lo) // 8)
            cand[k] = rng.randint(lo, hi) if rng.random() < 0.5 else \
                max(lo, min(hi, cand[k] + rng.choice((-step, step))))
        if valid(cand) and cand != g:
            return cand
    return g

def crossover(a, b, rng):
    for _ in range(50):
        c = {k: (a if rng.random() < 0.5 else b)[k] for k in GENES}
        if valid(c):
            return c
    return dict(a)

def write_candidate(src_base, g, idx):
    path = os.path.join(TMP, f"cand_{idx}.py")
    code = apply_genome(src_base, g)
    compile(code, path, "exec")
    with open(path, "w") as f:
        f.write(code)
    return path

def run_games(jobs):
    with Pool(PROCS) as pool:
        return list(pool.imap_unordered(_play, jobs, chunksize=4))

def score(results, a_path, b_path):
    """Paired dWins/dBank for candidate a vs baseline b from mixed results."""
    def bank(r, p):
        return r["banks"][0] if r["p0"] == p else r["banks"][1]
    dw = 0; db = 0.0; n = 0
    mir = [r for r in results if r["leg"] == "mirror"
           and a_path in (r["p0"], r["p1"])]
    for r in mir:
        a, b = bank(r, a_path), bank(r, b_path)
        if a > b: dw += 1
        elif a < b: dw -= 1
        db += a - b; n += 1
    dw_mirror = dw
    for leg, opp in OPPS:
        A = {}; B = {}
        for r in results:
            if r["leg"] != leg: continue
            for me, d in ((a_path, A), (b_path, B)):
                if me in (r["p0"], r["p1"]):
                    d[(r["seed"], 0 if r["p0"] == me else 1)] = (
                        bank(r, me) - bank(r, opp))
        ks = set(A) & set(B)
        for k in ks:
            dw += (1 if A[k] > 0 else 0) - (1 if B[k] > 0 else 0)
            db += A[k] - B[k]; n += len(ks) and 1
    return dw, (db / max(1, n)), dw_mirror

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
    with open(LOG, "a") as f:
        f.write(line + "\n")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hours", type=float, default=5.0)
    ap.add_argument("--procs", type=int, default=32)
    args = ap.parse_args()
    global PROCS
    PROCS = args.procs

    os.makedirs(TMP, exist_ok=True)
    t0 = time.time()
    rng = random.Random(4321)
    champion_genome = {k: v[2] for k, v in GENES.items()}
    base_src = open(BASE).read()
    champ_path = os.path.join(TMP, "champion.py")
    with open(champ_path, "w") as f:
        f.write(base_src)
    gen = 0
    history = []
    if os.path.exists(STATE):
        st = json.load(open(STATE))
        champion_genome = st["champion_genome"]
        gen = st["gen"]
        history = st["history"]
        rng.setstate(tuple(st["rng"][0:1] + [tuple(st["rng"][1])] + st["rng"][2:]))
        with open(champ_path, "w") as f:
            f.write(apply_genome(base_src, champion_genome)
                    if champion_genome != {k: v[2] for k, v in GENES.items()}
                    else base_src)
        log(f"RESUMED at gen {gen}")

    S1_SEEDS = list(range(0, 16))
    S2_SEEDS = list(range(100, 148))
    S3_SEEDS = list(range(500, 700))

    while (time.time() - t0) / 3600 < args.hours:
        gen += 1
        pop = [mutate(champion_genome, rng) for _ in range(18)]
        elites = [h["genome"] for h in history[-4:] if h.get("genome")]
        for i in range(4):
            if len(elites) >= 2:
                pop.append(crossover(rng.choice(elites), rng.choice(elites), rng))
            else:
                pop.append(mutate(champion_genome, rng, n_genes=4))
        paths = {}
        for i, g in enumerate(pop):
            try:
                paths[write_candidate(base_src, g, i)] = g
            except ValueError as e:
                log(f"gen{gen} cand{i} genome rejected: {e}")
        # S1 screen: candidate-vs-champion + the flagship leg
        s1 = eval_stage(list(paths), champ_path, S1_SEEDS, ("mirror", "v31b"))
        top = sorted(s1.items(), key=lambda x: (-x[1][0], -x[1][1]))[:6]
        log(f"gen{gen} S1: best {[(os.path.basename(p), v[0]) for p, v in top[:3]]}")
        # S2 confirm (adds the tape leg)
        s2 = eval_stage([p for p, _ in top], champ_path, S2_SEEDS,
                        ("mirror", "v31b", "tape"))
        best_path, (best_dw, best_db, best_dwm) = sorted(
            s2.items(), key=lambda x: (-x[1][0], -x[1][1]))[0]
        log(f"gen{gen} S2: best {os.path.basename(best_path)} "
            f"dWins {best_dw:+d} (mirror {best_dwm:+d}) dBank {best_db:+,.0f} "
            f"genome {paths[best_path]}")
        history.append({"gen": gen, "genome": paths[best_path],
                        "s2": [best_dw, best_db]})
        # S3 held-out gate
        if best_dw >= 6:
            s3 = eval_stage([best_path], champ_path, S3_SEEDS,
                            ("mirror", "v31b", "tape", "v12"))
            dw3, db3, dwm3 = s3[best_path]
            log(f"gen{gen} S3 HELD-OUT: dWins {dw3:+d} (mirror {dwm3:+d}, "
                f"field {dw3-dwm3:+d}) dBank {db3:+,.0f}")
            # Gate reform : dWins-primary; dBank logged, not gating.
            # Field legs non-negative stays (mirror-law guard).
            if dw3 >= 10 and (dw3 - dwm3) >= 0:
                champion_genome = paths[best_path]
                champion_new = apply_genome(base_src, champion_genome)
                with open(champ_path, "w") as f:
                    f.write(champion_new)
                log(f"gen{gen} *** NEW CHAMPION *** {champion_genome}")
        st = {"gen": gen, "champion_genome": champion_genome,
              "history": history,
              "rng": [rng.getstate()[0], list(rng.getstate()[1]),
                      rng.getstate()[2]]}
        with open(STATE, "w") as f:
            json.dump(st, f)
        elapsed = (time.time() - t0) / 3600
        log(f"gen{gen} done | elapsed {elapsed:.2f}h")

    # final: ultimate champion vs the v37d base AND the flagship
    log("FINAL VALIDATION, seeds 700-999")
    final = eval_stage([champ_path], BASE, list(range(700, 1000)),
                       ("mirror", "v31b", "tape"))
    dw, db, dwm = final[champ_path]
    log(f"FINAL vs v37d-base: dWins {dw:+d} (mirror {dwm:+d}) dBank {db:+,.0f} "
        f"| genome {champion_genome}")
    with open("SEARCH_DONE", "w") as f:
        f.write("done")

if __name__ == "__main__":
    main()
