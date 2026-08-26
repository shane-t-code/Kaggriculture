#!/usr/bin/env python3
"""pool_ab.py — multi-opponent paired A/B.

Why: mirror A/B structurally understates changes that add supply to a market the
mirror also supplies (recorded law, v13/v15 era). The live field is not a mirror.
This runs candidate A and baseline B against each member of an opponent POOL on
the same seed list and reports, per opponent and pooled: whose win rate is higher
and the margin delta (A_bank - B_bank vs that opponent, paired by seed+seat).

Usage:
    python pool_ab.py --a versions/vXX.py [--b main.py] [--seeds 8] [--start-seed 0]
Pool is defined in POOL below; edit deliberately, keep it stable across compares.
"""
from __future__ import annotations
import argparse, json, os, subprocess, sys, re

POOL = [
    ("mirror", None),                       # None -> baseline B itself
    ("tape", "versions/meta_boatlee.py"),
    ("v6a", "versions/v6a.py"),
    ("v12", "versions/v12b.py"),
]

def run(a, b, seeds, start):
    cmd = [sys.executable, "run_local.py", "--a", a, "--b", b,
           "--seeds", str(seeds), "--start-seed", str(start)]
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    games = []
    for line in out.splitlines():
        m = re.match(r"\s+seed\s+(\d+)\s+seat0: A\s+([\d,]+) vs B\s+([\d,]+)"
                     r"\s+seat1: A\s+([\d,]+) vs B\s+([\d,]+)", line)
        if m:
            s = int(m.group(1))
            v = [int(x.replace(",", "")) for x in m.groups()[1:]]
            games.append((s, 0, v[0], v[1]))
            games.append((s, 1, v[2], v[3]))
    return games  # (seed, seat, our_bank, opp_bank)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True)
    ap.add_argument("--b", default="main.py")
    ap.add_argument("--seeds", type=int, default=8)
    ap.add_argument("--start-seed", type=int, default=0)
    args = ap.parse_args()

    print(f"POOL A/B: A={args.a}  B={args.b}  seeds={args.seeds} from {args.start_seed}")
    tot_dw = tot_n = 0
    tot_dm = 0.0
    for name, opp in POOL:
        opp_file = opp or args.b
        ga = run(args.a, opp_file, args.seeds, args.start_seed)
        gb = ([] if opp is None else run(args.b, opp_file, args.seeds, args.start_seed))
        if opp is None:
            # mirror: A vs B directly IS the paired comparison
            wa = sum(1 for _, _, x, y in ga if x > y)
            n = len(ga)
            dm = sum(x - y for _, _, x, y in ga) / max(1, n)
            print(f"  {name:<8} A-vs-B direct: {wa}/{n} wins ({wa/max(1,n):.0%}), margin {dm:+,.0f}")
            tot_dw += wa - (n - wa); tot_n += n; tot_dm += dm * n
            continue
        A = {(s, st): (x, y) for s, st, x, y in ga}
        B = {(s, st): (x, y) for s, st, x, y in gb}
        keys = sorted(set(A) & set(B))
        dwins = 0; dmarg = 0.0
        aw = sum(1 for k in keys if A[k][0] > A[k][1])
        bw = sum(1 for k in keys if B[k][0] > B[k][1])
        for k in keys:
            dmarg += A[k][0] - B[k][0]
        n = len(keys)
        dmarg /= max(1, n)
        print(f"  {name:<8} A: {aw}/{n} wins vs opp | B: {bw}/{n} | dWins {aw-bw:+d} | dBank {dmarg:+,.0f}")
        tot_dw += aw - bw; tot_n += n; tot_dm += dmarg * n
    print(f"\nPOOL TOTAL: dWins {tot_dw:+d} over {tot_n} games/opponent-pairs, "
          f"mean dBank {tot_dm/max(1,tot_n):+,.0f}")

if __name__ == "__main__":
    main()
