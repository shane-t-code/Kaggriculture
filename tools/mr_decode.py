#!/usr/bin/env python3
"""mr_decode.py — measure multi_route's EXECUTED sell schedule per route, locally.

Why: the per-route counter (queue item 2) needs (step, units) wave tables like
TAPE_SELLS, but the order-level schedules extracted from the notebook blob
(results/decodes/route_sells.json) are spam-inflated — the engine clips sell
orders silently against held inventory and market absorption.  Ground truth =
market-inventory deltas attributed to the seat that ordered the sell that step
(same method as tools/true_sells.py, validated in Exp 78).

Runs main.py vs the pool multi_route agent on N seeds x both seats on the REAL
engine, decodes each game in-process (no giant replay dumps), and writes one
JSON line per game to results/decodes/mr_games.jsonl:
  seed, mr_seat, route timeline (their router replicated byte-for-byte),
  executed opp sells per (item, step), opp day-1 farm fingerprint, banks.

Alignment gotcha (mistakes ledger): kaggle env.steps may record actions at a
+1 index vs the acting step.  Rather than assume, each game tries both
alignments and keeps the one with fewer UNEXPLAINED positive inventory deltas
(positive delta with no SELL order = misalignment; only sells add inventory).

Usage:
    ./.venv/Scripts/python.exe tools/mr_decode.py --seeds 32 --workers 4
"""
from __future__ import annotations
import argparse, contextlib, json, os, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MR = os.path.join(ROOT, "versions", "pool_kaggriculture_multi_route_farming_agent.py")
OUT = os.path.join(ROOT, "results", "decodes", "mr_games.jsonl")

ITEMS = ("WHEAT", "FERTILIZER", "WOOL", "MILK", "MELON", "STRAWBERRY", "CARROT",
         "TOMATO", "EGG")

_KAWA_MILK_SUPPORT = {"PIZZA_SHOP", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP"}


def route_label(shops):
    """Byte-for-byte replication of the pool file's _kawa_route_label."""
    shops = list(shops or [])
    if shops[:1] == ["YARN_STORE"]:
        return "6c12s_4q_first_yarn"
    if "YARN_STORE" in shops[:2]:
        return "6c12s_4q_second_yarn"
    if "YARN_STORE" in shops[:3]:
        return "6c8s_3q"
    if _KAWA_MILK_SUPPORT.intersection(shops[:3]):
        return "10c4s_3q"
    return "8c6s_3q"


@contextlib.contextmanager
def _silence_fds():
    devnull = saved_out = saved_err = None
    try:
        sys.stdout.flush(); sys.stderr.flush()
        devnull = os.open(os.devnull, os.O_WRONLY)
        saved_out, saved_err = os.dup(1), os.dup(2)
        os.dup2(devnull, 1); os.dup2(devnull, 2)
        yield
    finally:
        try:
            sys.stdout.flush(); sys.stderr.flush()
        except Exception:
            pass
        if saved_out is not None: os.dup2(saved_out, 1); os.close(saved_out)
        if saved_err is not None: os.dup2(saved_err, 2); os.close(saved_err)
        if devnull is not None: os.close(devnull)


def _obs(step_row):
    o = step_row[0]["observation"] if isinstance(step_row[0], dict) else step_row[0].observation
    return o


def _act(step_row, seat):
    a = step_row[seat]["action"] if isinstance(step_row[seat], dict) else step_row[seat].action
    return a or {}


def _sell_orders(action, item):
    total = 0
    for o in (action.get("market") or []):
        if isinstance(o, (list, tuple)) and len(o) >= 3 and o[0] == "SELL" and o[1] == item:
            try:
                total += int(o[2])
            except Exception:
                pass
    return total


def decode_game(steps, mr_seat):
    """Returns decoded dict for one finished episode's steps list."""
    n = len(steps)

    # --- pick action alignment: a in {0, +1}; actions at si+a explain delta si->si+1
    unexplained = {0: 0, 1: 0}
    for a in (0, 1):
        for si in range(n - 1 - a):
            inv0 = _obs(steps[si])["market"]["inventory"]
            inv1 = _obs(steps[si + 1])["market"]["inventory"]
            act0 = _act(steps[si + a], 0)
            act1 = _act(steps[si + a], 1)
            for item in ITEMS:
                d = (inv1.get(item, 0) or 0) - (inv0.get(item, 0) or 0)
                if d > 0 and not (_sell_orders(act0, item) or _sell_orders(act1, item)):
                    unexplained[a] += d
    align = 0 if unexplained[0] <= unexplained[1] else 1

    # --- route timeline from shared town (what the opponent's router computes)
    timeline = []  # [(step, label)] on change
    last = None
    for si in range(n):
        shops = ((_obs(steps[si]).get("town") or {}).get("unlocked_shops") or [])
        lbl = route_label(shops)
        if lbl != last:
            timeline.append((si, lbl))
            last = lbl

    # --- executed sells for the multi_route seat (exclusive-delta attribution)
    sells = {}       # item -> {step: units}
    ambiguous = {}   # item -> units lost to both-sold-same-step
    for si in range(n - 1 - align):
        inv0 = _obs(steps[si])["market"]["inventory"]
        inv1 = _obs(steps[si + 1])["market"]["inventory"]
        act_me = _act(steps[si + align], 1 - mr_seat)
        act_mr = _act(steps[si + align], mr_seat)
        for item in ITEMS:
            d = (inv1.get(item, 0) or 0) - (inv0.get(item, 0) or 0)
            if d <= 0:
                continue
            mr_q = _sell_orders(act_mr, item)
            me_q = _sell_orders(act_me, item)
            if mr_q and not me_q:
                sells.setdefault(item, {})[si] = sells.setdefault(item, {}).get(si, 0) + d
            elif mr_q and me_q:
                ambiguous[item] = ambiguous.get(item, 0) + d
            # me-only deltas ignored (we're decoding the opponent)

    # --- opp farm fingerprint at day 1 noon (step 36) and day 2 noon (step 60)
    def farm_counts(si):
        farm = _obs(steps[si])["farms"][mr_seat]
        counts = {}
        for row in (farm.get("tiles") or []):
            for t in (row or []):
                if isinstance(t, dict):
                    k = t.get("crop") or t.get("animal")
                    if k:
                        counts[k] = counts.get(k, 0) + 1
        return {"tiles": counts, "money": farm.get("money", None)}

    fp = {str(si): farm_counts(si) for si in (36, 60) if si < n}

    final = _obs(steps[n - 1])["farms"]
    return {
        "align": align,
        "unexplained": unexplained,
        "route_timeline": timeline,
        "final_route": timeline[-1][1] if timeline else None,
        "sells": {k: sorted(v.items()) for k, v in sells.items()},
        "ambiguous": ambiguous,
        "fingerprint": fp,
        "mr_bank": final[mr_seat].get("money", None),
        "me_bank": final[1 - mr_seat].get("money", None),
    }


def run_one(task):
    seed, mr_seat, agent_path = task
    with _silence_fds():
        from kaggle_environments import make
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed})
        agents = [agent_path, MR]
        if mr_seat == 0:
            agents = [MR, agent_path]
        env.run(agents)
    statuses = [s.status for s in env.steps[-1]]
    rec = decode_game(env.steps, mr_seat)
    rec.update({"seed": seed, "mr_seat": mr_seat, "statuses": statuses})
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=32)
    ap.add_argument("--start-seed", type=int, default=0)
    ap.add_argument("--seed-list", default=None,
                    help="comma-separated explicit seed list (overrides --seeds)")
    ap.add_argument("--agent", default=None,
                    help="our agent file (default: main.py)")
    ap.add_argument("--out", default=None, help="output jsonl (default mr_games.jsonl)")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--append", action="store_true",
                    help="append to the output jsonl instead of overwriting")
    args = ap.parse_args()

    global OUT
    if args.out:
        OUT = os.path.join(ROOT, args.out) if not os.path.isabs(args.out) else args.out
    agent_path = os.path.join(ROOT, args.agent) if args.agent else os.path.join(ROOT, "main.py")
    if args.seed_list:
        seed_iter = [int(s) for s in args.seed_list.split(",")]
    else:
        seed_iter = [args.start_seed + i for i in range(args.seeds)]
    tasks = [(s, seat, agent_path) for s in seed_iter for seat in (0, 1)]
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    mode = "a" if args.append else "w"
    t0 = time.time()
    done = 0
    from concurrent.futures import ProcessPoolExecutor, as_completed
    with open(OUT, mode, encoding="utf-8") as f, \
            ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(run_one, t): t for t in tasks}
        for fut in as_completed(futs):
            seed, seat = futs[fut][0], futs[fut][1]
            try:
                rec = fut.result()
            except Exception as e:
                print(f"  !! seed {seed} mr_seat {seat}: {e!r}", flush=True)
                continue
            f.write(json.dumps(rec) + "\n")
            f.flush()
            done += 1
            print(f"  [{done}/{len(tasks)}] seed {seed} mr_seat {seat} "
                  f"route={rec['final_route']} align={rec['align']} "
                  f"mr_bank={rec['mr_bank']:,.0f} me_bank={rec['me_bank']:,.0f} "
                  f"({time.time()-t0:,.0f}s)", flush=True)
    print(f"\nwrote {done} games -> {OUT}  ({time.time()-t0:,.0f}s)")


if __name__ == "__main__":
    main()
