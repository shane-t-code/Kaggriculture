"""op_diff.py — the execution-gap table .

Plays one game of --agent vs --opp (a tape agent) and prints, per day,
op counts by type for BOTH sides: what they DO each day vs what we do.
A port is only done when these columns match.  Walk share included.

Usage: python tools/op_diff.py --agent versions/v93d.py \
           --opp versions/pool_top_allai.py --seed 7 [--days 0-29]
"""
import argparse, os, sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

OPS = ["PLANT", "WATER", "FERTILIZE", "HARVEST", "FEED", "CARE",
       "COLLECT_FERTILIZER", "MOVE", "PICKUP", "DROP", "PLACE",
       "BUILD", "DIG", "PASS"]
SHORT = {"COLLECT_FERTILIZER": "COLL", "FERTILIZE": "FERT", "HARVEST": "HARV",
         "PICKUP": "PICK", "BUILD": "BULD", "PLACE": "PLAC"}


def day_ops(steps, seat):
    """day -> Counter(op), day -> unit_turns, day -> market Counter."""
    ops = defaultdict(Counter)
    turns = defaultdict(int)
    mkt = defaultdict(Counter)
    sell_u = defaultdict(int)
    for t, step in enumerate(steps):
        d = t // 24
        a = step[seat].get("action") or {}
        if not isinstance(a, dict):
            continue
        acts = [a.get("farmer")] + list(a.get("hands") or [])
        for v in acts:
            if not v:
                continue
            op = v[0] if isinstance(v, (list, tuple)) else str(v)
            if op.startswith("BUILD"):
                op = "BUILD"
            ops[d][op] += 1
            turns[d] += 1
        for o in (a.get("market") or []):
            if not o:
                continue
            mkt[d][o[0]] += 1
            if o[0] == "SELL" and len(o) >= 3:
                try:
                    sell_u[d] += int(o[2])
                except (TypeError, ValueError):
                    pass
    return ops, turns, mkt, sell_u


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", required=True)
    ap.add_argument("--opp", required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--days", default="0-29")
    args = ap.parse_args()
    d0, d1 = (int(x) for x in args.days.split("-"))

    from run_local import play, _silence_fds
    with _silence_fds():
        ra, rb, env = play(args.agent, args.opp, args.seed)
    steps = env.steps
    A, At, Am, As = day_ops(steps, 0)
    B, Bt, Bm, Bs = day_ops(steps, 1)

    print(f"banks: us {ra:,.0f}  opp {rb:,.0f}   (each cell: us/them)")
    cols = ["PLANT", "WATER", "FERTILIZE", "HARVEST", "FEED", "CARE",
            "COLLECT_FERTILIZER", "PICKUP", "DROP", "BUILD", "PLACE",
            "DIG", "MOVE", "PASS"]
    hdr = " d | " + " ".join(f"{SHORT.get(c, c)[:5]:>9s}" for c in cols) \
          + " |  turns  walk%  |  SELL# selU HIRE BUY"
    print(hdr)
    totA, totB = Counter(), Counter()
    for d in range(d0, d1 + 1):
        row = f"{d:2d} | "
        for c in cols:
            row += f"{A[d][c]:4d}/{B[d][c]:<4d} "
            totA[c] += A[d][c]
            totB[c] += B[d][c]
        wa = 100 * A[d]["MOVE"] / max(1, At[d])
        wb = 100 * B[d]["MOVE"] / max(1, Bt[d])
        row += (f"| {At[d]:3d}/{Bt[d]:<3d} {wa:3.0f}/{wb:<3.0f} "
                f"| {Am[d]['SELL']:2d}/{Bm[d]['SELL']:<2d} "
                f"{As[d]:3d}/{Bs[d]:<3d} "
                f"{Am[d]['HIRE']:2d}/{Bm[d]['HIRE']:<2d} "
                f"{Am[d]['BUY_PRODUCT']+Am[d]['BUY_SEED']+Am[d]['BUY_ANIMAL']:2d}/"
                f"{Bm[d]['BUY_PRODUCT']+Bm[d]['BUY_SEED']+Bm[d]['BUY_ANIMAL']:<2d}")
        print(row)
    row = "TT | "
    for c in cols:
        row += f"{totA[c]:4d}/{totB[c]:<4d} "
    ta, tb = sum(At.values()), sum(Bt.values())
    row += (f"| {ta:3d}/{tb:<3d} {100*totA['MOVE']/max(1,ta):3.0f}/"
            f"{100*totB['MOVE']/max(1,tb):<3.0f} |")
    print(row)


if __name__ == "__main__":
    main()
