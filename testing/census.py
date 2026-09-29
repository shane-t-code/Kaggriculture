# GROW CENSUS — stage 1 of the EXP 180 overnight grower search (Sep 28 ~10:25pm).
#
# For each fresh seed: run the 4 CONTROL cells (candidate vs ca22 & majkel,
# both seats), capturing world features (shop draw / wool / wheat / quadrants
# at day boundaries 11,12,14,17,19) plus whether the certified sheep project
# fired and its internal profit forecasts. These cells are the SHARED CONTROLS
# for every variant screened tonight — variants later cost 4 games/world.
#
# Usage: python census.py <TAG> <START_SEED> <COUNT> [STRIDE OFFSET]
#   Stride mode: worker takes seeds START+OFFSET, START+OFFSET+STRIDE, ...
#   within [START, START+COUNT) — lets N workers share one range disjointly.
# Output: census_rows_<TAG>.jsonl  (resumable: skips (seed,opp,pid) cells
# already present in ANY census_rows_*.jsonl in this directory).
# Seeds ledgered to grow/SEEDS.jsonl (range record per invocation).
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
PATHS = {
    "candidate": Path(r"C:\Kaggriculture\work\\review10\candidate.py"),
    "ca22": Path(r"C:\Kaggriculture\work\build_a\s1009r_ca22.py"),
    "majkel": Path(r"C:\Kaggriculture\work\\review9\majkel.py"),
}
CAP_STEPS = (264, 288, 336, 408, 456)  # day 11,12,14,17,19 at hour 0
OPPS = ("ca22", "majkel")

def load(name):
    p = PATHS[name]
    return get_last_callable(p.read_text(encoding="utf-8"), path=str(p))

def wrap_probe(fn, cap):
    def probe(obs, cfg=None):
        s = int(obs["step"])
        if s in CAP_STEPS:
            cap[str(s)] = {
                "yarn": obs["town"]["unlocked_shops"].count("YARN_STORE"),
                "shops": list(obs["town"]["unlocked_shops"]),
                "wool": obs["market"]["prices"]["WOOL"],
                "wheat": obs["market"]["prices"]["WHEAT"],
                "quads": sorted(obs["farms"][obs["player"]]["unlocked_quadrants"]),
            }
        return fn(obs, cfg)
    return probe

def done_cells():
    got = set()
    for f in GROW.glob("census_rows_*.jsonl"):
        for line in f.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            got.add((r["seed"], r["opp"], r["pid"]))
    return got

def main():
    tag, start, count = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    stride = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    offset = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    with (GROW / "SEEDS.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps({"tool": "grow_census", "tag": tag,
                            "start": start, "count": count,
                            "stride": stride, "offset": offset,
                            "ts": time.strftime("%Y-%m-%d %H:%M:%S")}) + "\n")
    out = GROW / f"census_rows_{tag}.jsonl"
    got = done_cells()
    for seed in range(start + offset, start + count, stride):
        for opp in OPPS:
            for pid in (0, 1):
                if (seed, opp, pid) in got:
                    continue
                cand_fn = load("candidate")
                assert cand_fn.__name__ == "r9_scaled_agent", cand_fn.__name__
                cap = {}
                agents = [None, None]
                agents[pid] = wrap_probe(cand_fn, cap)
                agents[1 - pid] = load(opp)
                t0 = time.time()
                with _silence_fds():
                    env = make("kaggriculture",
                               configuration={"episodeSteps": 720, "seed": seed})
                    env.run(agents)
                last = env.steps[-1]
                rewards = [s.reward for s in last]
                r9 = cand_fn.__globals__.get("_R9_REPORT", {})
                v233 = cand_fn.__globals__.get("_V233_REPORT", {})
                margin = (None if None in rewards
                          else rewards[pid] - rewards[1 - pid])
                row = {"seed": seed, "opp": opp, "pid": pid,
                       "rewards": rewards,
                       "statuses": [str(s.status) for s in last],
                       "margin": margin,
                       "fired": int(r9.get("accepted", 0)),
                       "committed": int(v233.get("sheep_committed", 0)),
                       "eligible_checks": int(r9.get("eligible_checks", 0)),
                       "declines": int(r9.get("economic_declines", 0)),
                       "decisions": r9.get("decisions", []),
                       "features": cap,
                       "secs": round(time.time() - t0, 1)}
                with out.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(row) + "\n")
                print(json.dumps({k: row[k] for k in
                                  ("seed", "opp", "pid", "margin", "fired",
                                   "committed", "secs")}), flush=True)
    print(f"CENSUS {tag} COMPLETE", flush=True)

if __name__ == "__main__":
    main()
