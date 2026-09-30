# VARIANT TEST  — <var> vs <opp> paired with dtrw vs <opp> in the same
# worlds, both seats.  Optional pinned town preset (tools/shop_pin presets or
# 'TOMATO3' = three tomato-buying shops in the first six).  Margin first.
# Usage: python -X utf8 variant_test.py <var> <opp> <seed_start> <n_seeds> <procs> [preset]
import json, os, sys, time
from multiprocessing import Pool
from pathlib import Path
sys.path.insert(0, r"C:\Kaggriculture"); sys.dont_write_bytecode = True
GROW = Path(r"C:\Kaggriculture\work\build_a\grow")
OUT = GROW / "variant_rows.jsonl"

def game(var, opp, seed, pid, preset):
    from run_local import _silence_fds
    with _silence_fds():
        from kaggle_environments import make
        from kaggle_environments.agent import get_last_callable
    sys.path.insert(0, str(GROW))
    from family_duel import FAM, load, timed
    for v in ("dtrwt", "dtrwtc", "dtrwc", "dtrwtr", "dtrwtl", "dtrwtd", "dtrwtcs", "dtrwtb"):
        FAM[v] = GROW / "variants" / f"{v}.py"
    FAM["majkel"] = Path(r"C:\Kaggriculture") / "work" / "" / "review9" / "majkel.py"
    rec = [0.0]
    fn = load(FAM[var])
    ags = [None, None]; ags[pid] = timed(fn, rec); ags[1 - pid] = load(FAM[opp])
    pin = None
    if preset:
        from tools import shop_pin
        if preset == "TOMATO3":
            from tomato_test import pinned_town
            pin = pinned_town(seed)
        else:
            pin = shop_pin.PRESETS[preset]
        shop_pin.install(pin)
    try:
        with _silence_fds():
            env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}); env.run(ags)
    finally:
        if pin:
            shop_pin.uninstall()
    rw = [s.reward for s in env.steps[-1]]
    diag = {}
    try:
        ch = fn.__globals__.get("_CHASSIS") or fn.__globals__.get("chassis")
        diag = dict(getattr(ch, "diagnostics", {}) or {})
    except Exception:
        pass
    return {"var": var, "opp": opp, "seed": seed, "pid": pid, "preset": preset, "us": rw[pid], "them": rw[1 - pid],
            "margin": rw[pid] - rw[1 - pid], "max_ms": round(rec[0]),
            "statuses": [str(s.status) for s in env.steps[-1]], "diag": diag,
            "shops": list(env.steps[-1][0].observation["town"]["unlocked_shops"])}

def job(j):
    return game(*j)

def main():
    var, opp, s0, n, procs = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
    preset = sys.argv[6] if len(sys.argv) > 6 else None
    with (GROW / "SEEDS.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps({"tool": "variant_test", "var": var, "opp": opp, "start": s0, "count": n, "preset": preset, "ts": time.strftime("%Y-%m-%d %H:%M:%S")}) + "\n")
    ctrl = os.environ.get("VT_CONTROL", "dtrw")
    jobs = [(v, opp, s, p, preset) for s in range(s0, s0 + n) for p in (0, 1) for v in (var, ctrl)]
    res = {}
    with Pool(procs) as pool:
        for r in pool.imap_unordered(job, jobs):
            with OUT.open("a", encoding="utf-8") as f: f.write(json.dumps(r) + "\n")
            res[(r["var"], r["seed"], r["pid"])] = r
    print(f"{var} vs {opp} (preset {preset}); paired with {ctrl} vs {opp}; margin = us - them")
    diffs = []
    for s in range(s0, s0 + n):
        for p in (0, 1):
            a, b = res.get((var, s, p)), res.get((ctrl, s, p))
            if not a or not b: continue
            d = a["margin"] - b["margin"]; diffs.append(d)
            flip = ("W" if a["margin"] > 0 else "L" if a["margin"] < 0 else "T") + "<-" + ("W" if b["margin"] > 0 else "L" if b["margin"] < 0 else "T")
            print(f"  seed {s} seat {p} | {var} {a['margin']:>+9,.0f} | dtrw {b['margin']:>+9,.0f} | change {d:>+8,.0f} {flip} | fired {a['diag'].get('wool_courier', a['diag'])} | {a['max_ms']}ms {a['statuses']} shops {a['shops'][:4]}")
    if diffs:
        diffs.sort()
        print(f"cells {len(diffs)}: change mean {sum(diffs)/len(diffs):+,.0f} median {diffs[len(diffs)//2]:+,.0f} worst {diffs[0]:+,.0f} best {diffs[-1]:+,.0f}; better {sum(d>0 for d in diffs)} worse {sum(d<0 for d in diffs)} same {sum(d==0 for d in diffs)}")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8"); main()
