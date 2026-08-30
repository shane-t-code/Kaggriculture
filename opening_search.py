#!/usr/bin/env python3
"""opening_search.py — population search over the agent's OPENING SHAPE.

Runs ON the pod. Searches 14 opening dials (herd sizes/timing, seed mix,
caps, hires, land triggers, factory day) that were hand-reasoned but never
searched. Every stage is the paired A/B design; promotion to champion
requires a held-out gate — the exact protocol that debunked vSEARCH,
STR_CAP=30 and the gamble-dial mirage.

Stages per generation (seeds disjoint by stage):
  S1  screen : 16 seeds, mirror vs champion   (32 games/candidate)
  S2  confirm: 48 seeds, mirror + v12         (288 games/candidate, top 6)
  S3  gate   : 200 HELD-OUT seeds, mirror+v12 (1,200 games, best S2 only;
               champion replaced only on dWins >= +10)
Final: ultimate champion vs the ORIGINAL main.py on 300 fresh seeds.

Checkpoints search_state.json after every generation — a random cutoff
loses at most one generation. Self-terminates after MAX_HOURS.
"""
import json, os, random, re, sys, time
from multiprocessing import Pool

from pod_runner import _play   # (leg, p0, p1, seed) -> result dict

MAX_HOURS = 6.0
PROCS = 32
V12 = "versions/v12b.py"
V6A = "versions/v6a.py"
OPPS = (("v12", V12), ("v6a", V6A))   # mirror-law guard: mirror-only gates
                                      # reward market under-suppliers
TMP = "searchtmp"
STATE = "search_state.json"
LOG = "search_log.txt"

# gene: (lo, hi, current-champion value)
GENES = {
    "sheep":        (2, 6, 4),
    "cow":          (4, 9, 8),
    "cow_pause":    (3, 7, 5),
    "resume_day":   (8, 14, 11),
    "straw_need":   (8, 30, 20),
    "str_from_day": (2, 6, 4),
    "str_want":     (4, 9, 6),
    "melon_cap":    (6, 16, 12),
    "str_cap":      (28, 42, 35),
    "wheat_cap":    (10, 30, 20),
    "hands":        (5, 8, 6),
    "factory_day":  (12, 22, 18),
    "land1":        (4, 8, 6),
    "land2":        (6, 10, 8),
}

def apply_genome(src, g):
    subs = [
        (r'ANIMAL_TARGETS = \{"SHEEP": \d+, "COW": \d+\}',
         f'ANIMAL_TARGETS = {{"SHEEP": {g["sheep"]}, "COW": {g["cow"]}}}'),
        (r'owned\.get\("COW", 0\) >= \d+ and day < \d+',
         f'owned.get("COW", 0) >= {g["cow_pause"]} and day < {g["resume_day"]}'),
        (r'my_crops\.get\("STRAWBERRY", 0\) < \d+\)',
         f'my_crops.get("STRAWBERRY", 0) < {g["straw_need"]})'),
        (r'if day < \d+:\n                continue\n            want = \d+',
         f'if day < {g["str_from_day"]}:\n                continue\n'
         f'            want = {g["str_want"]}'),
        (r'("MELON":\s+\{"cost": 80,[^}]*"cap": )\d+',
         lambda m: m.group(1) + str(g["melon_cap"])),
        (r'("STRAWBERRY": \{"cost": 100,[^}]*"cap": )\d+',
         lambda m: m.group(1) + str(g["str_cap"])),
        (r'("WHEAT":\s+\{"cost": 10,[^}]*"cap": )\d+',
         lambda m: m.group(1) + str(g["wheat_cap"])),
        (r'TARGET_HANDS = \d+', f'TARGET_HANDS = {g["hands"]}'),
        (r'WHEAT_FACTORY_DAY = \d+', f'WHEAT_FACTORY_DAY = {g["factory_day"]}'),
        (r'>= \(\d+ if n_quadrants == 1 else \d+\)',
         f'>= ({g["land1"]} if n_quadrants == 1 else {g["land2"]})'),
    ]
    for pat, rep in subs:
        src, n = re.subn(pat, rep, src)
        if n != 1:
            raise ValueError(f"pattern applied {n}x: {pat[:50]}")
    return src

def valid(g):
    return (g["sheep"] + g["cow"] <= 12 and g["land2"] >= g["land1"]
            and all(GENES[k][0] <= v <= GENES[k][1] for k, v in g.items()))

def mutate(g, rng, n_genes=None):
    g = dict(g)
    for _ in range(200):
        cand = dict(g)
        for k in rng.sample(list(GENES), n_genes or rng.randint(1, 3)):
            lo, hi, _ = GENES[k]
            cand[k] = rng.randint(lo, hi)
        if valid(cand) and cand != g:
            return cand
    return g

def crossover(a, b, rng):
    for _ in range(50):
        c = {k: (a if rng.random() < 0.5 else b)[k] for k in GENES}
        if valid(c):
            return c
    return dict(a)

def write_candidate(src_champion, g, idx):
    path = os.path.join(TMP, f"cand_{idx}.py")
    code = apply_genome(src_champion, g)
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
    # dedupe champion-vs-v12 duplicates across candidates
    jobs = list(dict.fromkeys(jobs))
    results = run_games(jobs)
    return {path: score(results, path, champ_path) for path in cands}

def log(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")

def main():
    os.makedirs(TMP, exist_ok=True)
    t0 = time.time()
    rng = random.Random(1234)
    champion_genome = {k: v[2] for k, v in GENES.items()}
    champion_src = open("main.py").read()
    champ_path = os.path.join(TMP, "champion.py")
    with open(champ_path, "w") as f:
        f.write(champion_src)
    gen = 0
    history = []
    if os.path.exists(STATE):
        st = json.load(open(STATE))
        champion_genome = st["champion_genome"]
        gen = st["gen"]
        history = st["history"]
        rng.setstate(tuple(st["rng"][0:1] + [tuple(st["rng"][1])] + st["rng"][2:]))
        with open(champ_path, "w") as f:
            f.write(apply_genome(champion_src, champion_genome)
                    if champion_genome != {k: v[2] for k, v in GENES.items()}
                    else champion_src)
        log(f"RESUMED at gen {gen}")

    S1_SEEDS = list(range(0, 16))
    S2_SEEDS = list(range(100, 148))
    S3_SEEDS = list(range(500, 700))

    while (time.time() - t0) / 3600 < MAX_HOURS:
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
                paths[write_candidate(champion_src, g, i)] = g
            except ValueError as e:
                log(f"gen{gen} cand{i} genome rejected: {e}")
        # S1 screen (mirror + v6a: mirror alone rewards market under-suppliers)
        s1 = eval_stage(list(paths), champ_path, S1_SEEDS, ("mirror", "v6a"))
        top = sorted(s1.items(), key=lambda x: (-x[1][0], -x[1][1]))[:6]
        log(f"gen{gen} S1: best {[(os.path.basename(p), v[0]) for p, v in top[:3]]}")
        # S2 confirm
        s2 = eval_stage([p for p, _ in top], champ_path, S2_SEEDS,
                        ("mirror", "v12", "v6a"))
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
                            ("mirror", "v12", "v6a"))
            dw3, db3, dwm3 = s3[best_path]
            log(f"gen{gen} S3 HELD-OUT: dWins {dw3:+d} (mirror {dwm3:+d}, "
                f"field {dw3-dwm3:+d}) dBank {db3:+,.0f}")
            # Champion gate: wins AND bank AND field-legs non-negative.
            # Mirror-only wins with negative bank = market-starvation
            # artifact (mirror-law), not a better economy.
            if dw3 >= 10 and db3 > 0 and (dw3 - dwm3) >= 0:
                champion_genome = paths[best_path]
                champion_new = apply_genome(champion_src, champion_genome)
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

    # final: ultimate champion vs ORIGINAL main.py on fresh seeds
    if champion_genome != {k: v[2] for k, v in GENES.items()}:
        log("FINAL VALIDATION vs original main.py, seeds 700-999")
        final = eval_stage([champ_path], "main.py", list(range(700, 1000)),
                           ("mirror", "v12", "v6a"))
        dw, db, dwm = final[champ_path]
        log(f"FINAL: dWins {dw:+d} (mirror {dwm:+d}) dBank {db:+,.0f} "
            f"| genome {champion_genome}")
    else:
        log("FINAL: champion never displaced — hand-tuned opening stands")
    with open("SEARCH_DONE", "w") as f:
        f.write("done")

if __name__ == "__main__":
    main()
