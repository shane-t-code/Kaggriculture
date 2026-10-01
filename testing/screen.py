# GROW SCREEN — experiment stage 2 (Sep 28). Runs ONE variant on a selected
# seed list, paired cell-for-cell against the census control games.
#
# PREDECLARED GATES (set before any stage-2 game ran — see also driver notes):
#   KEEP a knob iff, on its evaluated panel:
#     mean paired margin (variant - candidate) > 0
#     AND zero losing flips (score_delta < 0 cells)
#     AND tape stratum (majkel) mean >= -250 with stratum score_delta >= 0
#     AND on cells where NEITHER arm fired beyond control, paired == 0
#         (any nonzero there = unintended coupling -> investigate, no KEEP)
#   KILL iff mean paired margin < 0 on the panel.
#   Combos are built ONLY from KEEPs; nothing is promoted to a submission
#   candidate without the full battery (both seats, full roster) tomorrow.
#
# Usage: python screen.py <variant_name> <seeds_json_path>
# Output: screen_rows_<variant>.jsonl (resumable).
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, r"C:\Kaggriculture")
sys.dont_write_bytecode = True
from run_local import _silence_fds
with _silence_fds():
    from kaggle_environments import make
    from kaggle_environments.agent import get_last_callable

GROW = Path(r"C:\Kaggriculture\work\build_a\grow")
OPP_PATHS = {
    "ca22": Path(r"C:\Kaggriculture\work\build_a\s1009r_ca22.py"),
    "majkel": Path(r"C:\Kaggriculture\work\\review9\majkel.py"),
}

def load_file(p):
    return get_last_callable(p.read_text(encoding="utf-8"), path=str(p))

def census_cells():
    cells = {}
    for f in GROW.glob("census_rows_*.jsonl"):
        for line in f.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            cells[(r["seed"], r["opp"], r["pid"])] = r
    return cells

def main():
    name, seeds_path = sys.argv[1], sys.argv[2]
    vpath = GROW / "variants" / f"{name}.py"
    seeds = json.loads(Path(seeds_path).read_text(encoding="utf-8"))
    out = GROW / f"screen_rows_{name}.jsonl"
    done = set()
    if out.exists():
        for line in out.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                done.add((r["seed"], r["opp"], r["pid"]))
    ctrl = census_cells()
    for seed in seeds:
        for opp in ("ca22", "majkel"):
            for pid in (0, 1):
                if (seed, opp, pid) in done:
                    continue
                c = ctrl.get((seed, opp, pid))
                assert c is not None, f"no census control {seed} {opp} {pid}"
                vfn = load_file(vpath)
                assert vfn.__name__ == "grow_variant_agent"
                agents = [None, None]
                agents[pid] = vfn
                agents[1 - pid] = load_file(OPP_PATHS[opp])
                t0 = time.time()
                with _silence_fds():
                    env = make("kaggriculture",
                               configuration={"episodeSteps": 720,
                                              "seed": seed})
                    env.run(agents)
                last = env.steps[-1]
                rewards = [s.reward for s in last]
                r9 = vfn.__globals__.get("_R9_REPORT", {})
                vm = (None if None in rewards
                      else rewards[pid] - rewards[1 - pid])
                cm = c["margin"]
                paired = None if vm is None else vm - cm
                sc = ((1 if vm > 0 else -1 if vm < 0 else 0)
                      - (1 if cm > 0 else -1 if cm < 0 else 0)
                      if vm is not None else None)
                r11 = vfn.__globals__.get("_R11_SECOND_REPORT", {})
                t8 = vfn.__globals__.get("_T8_REPORT")
                row = {"variant": name, "seed": seed, "opp": opp, "pid": pid,
                       "margin": vm, "ctrl_margin": cm, "paired": paired,
                       "score_delta": sc,
                       "fired": int(r9.get("accepted", 0)),
                       "ctrl_fired": c["fired"],
                       "decisions": r9.get("decisions", []),
                       "r11": {k: r11.get(k) for k in
                               ("checks", "requested", "days", "decisions")
                               if k in r11},
                       "t8": t8,
                       "sp": vfn.__globals__.get("_SP_REPORT"),
                       "bd": vfn.__globals__.get("_BD_REPORT"),
                       "statuses": [str(s.status) for s in last],
                       "secs": round(time.time() - t0, 1)}
                with out.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(row) + "\n")
                print(json.dumps({k: row[k] for k in
                                  ("variant", "seed", "opp", "pid", "paired",
                                   "score_delta", "fired", "ctrl_fired",
                                   "secs")}), flush=True)
    print(f"SCREEN {name} COMPLETE", flush=True)

if __name__ == "__main__":
    main()
