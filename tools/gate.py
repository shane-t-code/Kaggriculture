"""gate.py — the repaired A/B gate contract .

Fixes over py_ab.py/ab_sum.py (all verified defects):
  * BOTH SEATS actually played: each seed produces TWO rows (seat 0 = candidate
    listed first, seat 1 = candidate second).  py_ab played one orientation.
  * Rows carry candidate/opponent file basenames + sha256[:8] so a summary can
    refuse to mix artifacts.
  * Explicit per-row status: "OK" or the engine's non-DONE status string.
    Invalid rows are NEVER counted as losses — they are reported and excluded.
  * Row key = (tag, seed, seat).  `sum` FAILS on duplicates and on missing
    seats instead of silently intersecting/overwriting.
  * Summary reports W/L/T, decided share q = W/(W+L), half-win score
    s = (W + 0.5T)/N  (ties count half — the rating-relevant statistic),
    with a seed-level bootstrap CI on s (both seats resampled together).

Usage:
  run:  python tools/gate.py run --a fork/cand.py --b external/cha22_main.py
            --seeds 12 --start-seed 6100 --tag cand_vs_cha22 --out results/gate_x.jsonl
  sum:  python tools/gate.py sum results/gate_x.jsonl cand_vs_cha22
        python tools/gate.py sum results/gate_x.jsonl tagA tagB   (paired compare)
"""
import argparse, hashlib, json, os, random, sys
from collections import defaultdict
from multiprocessing import Pool

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)


def _sha8(path):
    try:
        return hashlib.sha256(open(path, "rb").read()).hexdigest()[:8]
    except OSError:
        return "builtin"


def play_one(job):
    a_file, b_file, seed, seat, tag, ash, bsh = job
    from run_local import _silence_fds
    from kaggle_environments import make
    first, second = (a_file, b_file) if seat == 0 else (b_file, a_file)
    with _silence_fds():
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed})
        env.run([first, second])
    final = env.steps[-1]
    statuses = [s.status for s in final]
    me_i = 0 if seat == 0 else 1
    me, op = float(final[me_i].reward or 0), float(final[1 - me_i].reward or 0)
    ok = all(st == "DONE" for st in statuses)
    return {
        "tag": tag, "seed": seed, "seat": seat,
        "cand": os.path.basename(a_file), "opp": os.path.basename(b_file),
        "cand_sha": ash, "opp_sha": bsh,
        "me": me, "op": op,
        "res": ("X" if not ok else "W" if me > op else "L" if me < op else "T"),
        "status": "OK" if ok else "/".join(statuses),
    }


def cmd_run(args):
    ash, bsh = _sha8(args.a), _sha8(args.b)
    jobs = [(args.a, args.b, s, seat, args.tag, ash, bsh)
            for s in range(args.start_seed, args.start_seed + args.seeds)
            for seat in (0, 1)]
    with Pool(args.procs) as pool:
        rows = pool.map(play_one, jobs)
    with open(args.out, "a", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    bad = [r for r in rows if r["status"] != "OK"]
    w = sum(r["res"] == "W" for r in rows); l = sum(r["res"] == "L" for r in rows)
    t = sum(r["res"] == "T" for r in rows)
    print(f"{args.tag}: {len(rows)} games (seeds {args.start_seed}-"
          f"{args.start_seed + args.seeds - 1} x 2 seats)  W{w}-L{l}-T{t}"
          + (f"  !! {len(bad)} INVALID: " + ", ".join(
                f"seed {r['seed']} seat {r['seat']} {r['status']}" for r in bad)
             if bad else ""))


def _collect(path, tag):
    """Load one tag's rows; hard-fail on duplicates, mixed artifacts, missing seats."""
    rows, keys = [], set()
    for line in open(path, encoding="utf-8"):
        r = json.loads(line)
        if r.get("tag") != tag:
            continue
        k = (r["seed"], r["seat"])
        if k in keys:
            sys.exit(f"FAIL {tag}: duplicate row seed {k[0]} seat {k[1]} — refusing to summarize.")
        keys.add(k); rows.append(r)
    if not rows:
        sys.exit(f"FAIL: no rows for tag {tag!r} in {path}")
    if len({(r["cand_sha"], r["opp_sha"]) for r in rows}) > 1:
        sys.exit(f"FAIL {tag}: rows mix different artifact hashes — refusing to summarize.")
    seeds = {r["seed"] for r in rows}
    lame = [s for s in seeds if {r["seat"] for r in rows if r["seed"] == s} != {0, 1}]
    if lame:
        sys.exit(f"FAIL {tag}: seeds missing a seat: {sorted(lame)} — refusing to summarize.")
    return rows


def _score(rows):
    ok = [r for r in rows if r["status"] == "OK"]
    inv = len(rows) - len(ok)
    w = sum(r["res"] == "W" for r in ok); l = sum(r["res"] == "L" for r in ok)
    t = sum(r["res"] == "T" for r in ok); n = len(ok)
    q = w / (w + l) if w + l else float("nan")
    s = (w + 0.5 * t) / n if n else float("nan")
    return w, l, t, n, inv, q, s


def _boot_s(rows, iters=2000, seed=7):
    """Bootstrap CI on half-win score, resampling SEEDS (both seats travel together)."""
    by_seed = defaultdict(list)
    for r in rows:
        if r["status"] == "OK":
            by_seed[r["seed"]].append(r)
    seeds = list(by_seed)
    rng = random.Random(seed); vals = []
    for _ in range(iters):
        pick = [by_seed[rng.choice(seeds)] for _ in seeds]
        flat = [r for grp in pick for r in grp]
        w = sum(r["res"] == "W" for r in flat); t = sum(r["res"] == "T" for r in flat)
        vals.append((w + 0.5 * t) / len(flat))
    vals.sort()
    return vals[int(0.025 * iters)], vals[int(0.975 * iters)]


def cmd_sum(args):
    tags = args.tags
    for tag in tags:
        rows = _collect(args.path, tag)
        w, l, t, n, inv, q, s = _score(rows)
        lo, hi = _boot_s(rows)
        margins = sorted(r["me"] - r["op"] for r in rows if r["status"] == "OK")
        med = margins[len(margins) // 2] if margins else 0
        print(f"{tag}: {rows[0]['cand']}({rows[0]['cand_sha']}) vs "
              f"{rows[0]['opp']}({rows[0]['opp_sha']})  n={n}"
              + (f"  !! {inv} INVALID rows excluded" if inv else ""))
        print(f"  W{w}-L{l}-T{t}   decided share q={q:.3f}   "
              f"HALF-WIN s={s:.3f} [95% boot {lo:.3f},{hi:.3f}]   med margin {med:+,.0f}")
    if len(tags) == 2:
        ra, rb = _collect(args.path, tags[0]), _collect(args.path, tags[1])
        pa = {(r["seed"], r["seat"]): r for r in ra if r["status"] == "OK"}
        pb = {(r["seed"], r["seat"]): r for r in rb if r["status"] == "OK"}
        common = sorted(set(pa) & set(pb))
        if not common:
            print("paired: no common (seed,seat) rows"); return
        val = {"W": 1.0, "T": 0.5, "L": 0.0}
        d = [val[pa[k]["res"]] - val[pb[k]["res"]] for k in common]
        up = sum(x > 0 for x in d); dn = sum(x < 0 for x in d)
        print(f"paired {tags[0]} - {tags[1]}: {len(common)} common games, "
              f"half-win diff {sum(d)/len(d):+.3f}/game, flips +{up}/-{dn}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--a", required=True, help="CANDIDATE agent file")
    r.add_argument("--b", required=True, help="opponent agent file")
    r.add_argument("--seeds", type=int, required=True)
    r.add_argument("--start-seed", type=int, required=True)
    r.add_argument("--tag", required=True)
    r.add_argument("--out", required=True)
    r.add_argument("--procs", type=int, default=max(1, (os.cpu_count() or 4) - 1))
    r.set_defaults(fn=cmd_run)
    s = sub.add_parser("sum")
    s.add_argument("path")
    s.add_argument("tags", nargs="+", help="one tag to report, two to compare paired")
    s.set_defaults(fn=cmd_sum)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
