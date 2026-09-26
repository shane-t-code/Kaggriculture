"""scan_str_worlds.py — find zero-str-shop-forecast worlds + measure forecast error.

For each seed, plays c23s vs c23s (natural world, no candidate perturbation)
and records the shop draws visible at day 10 (the swap/CP gate moment) and
the final draw list.  A world is GATE-OPEN when day-10 draws have >= 2 shops
and none is a strawberry shop; the forecast is WRONG when a strawberry shop
appears in a later draw anyway (the seed-7217 failure mode).

Usage: python tools/scan_str_worlds.py <start_seed> <n> <out.jsonl>
"""
import json, os, sys
from multiprocessing import Pool

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

STR_SHOPS = ("BRUNCH_SPOT", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP", "FARMERS_MARKET")
AGENT = r'fork\c23s.py'


def scan_one(seed):
    from run_local import _silence_fds
    from kaggle_environments import make
    with _silence_fds():
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed})
        env.run([AGENT, AGENT])
    obs10 = env.steps[252][0]["observation"]
    d10 = list(obs10["town"].get("unlocked_shops", []))
    final = list(env.steps[-1][0]["observation"]["town"].get("unlocked_shops", []))
    p_c10 = int(obs10["market"]["prices"].get("CARROT", 0))
    gate_open = len(d10) >= 2 and not any(s in STR_SHOPS for s in d10) and p_c10 >= 35
    wrong = gate_open and any(s in STR_SHOPS for s in final)
    return {"seed": seed, "d10_shops": d10, "final_shops": final, "p_c10": p_c10,
            "gate_open": gate_open, "forecast_wrong": wrong,
            "bank": float(env.steps[-1][0].reward or 0),
            "status": "/".join(s.status for s in env.steps[-1])}


def main():
    start, n, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    seeds = list(range(start, start + n))
    with Pool(max(1, (os.cpu_count() or 4) - 1)) as pool:
        rows = pool.map(scan_one, seeds)
    with open(out, "a", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    opened = [r for r in rows if r["gate_open"]]
    wrong = [r for r in rows if r["forecast_wrong"]]
    print(f"{len(rows)} worlds: gate-open {len(opened)} "
          f"({[r['seed'] for r in opened]}), forecast-wrong {len(wrong)} "
          f"({[r['seed'] for r in wrong]})")


if __name__ == "__main__":
    main()
