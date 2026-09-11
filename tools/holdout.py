"""holdout.py — frozen promotion-gate runner .

THE RULE: seeds 500-539 x the five preset worlds are the FROZEN HOLDOUT.
Run this ONCE per promotion decision, never to tune. Screens/tuning live on
seeds 0-99. (Selection on a held-out block un-freezes it — the +2,301/-1,259
lesson from the Sep 11 sweep.)

Runs candidate vs each opponent across world cells via run_local --shops,
reports per-cell and pooled: win rate, margin, mu/sigma.

Usage:
    python tools/holdout.py --a versions/vXX.py [--seeds 8] [--start-seed 500]
        [--worlds MILK0,MILK1,MILK3,YARN2,MIXED] [--opps main.py,versions/v61e.py]
"""
import argparse, re, subprocess, sys, os, statistics

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable

def run(a, b, seeds, start, world):
    cmd = [PY, os.path.join(ROOT, "run_local.py"), "--a", a, "--b", b,
           "--seeds", str(seeds), "--start-seed", str(start), "--shops", world]
    out = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT).stdout
    games = []
    for line in out.splitlines():
        m = re.match(r"\s+seed\s+(\d+)\s+seat0: A\s+([\d,]+) vs B\s+([\d,]+)"
                     r"\s+seat1: A\s+([\d,]+) vs B\s+([\d,]+)", line)
        if m:
            v = [int(x.replace(",", "")) for x in m.groups()[1:]]
            games.append((v[0], v[1]))
            games.append((v[2], v[3]))
    return games

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True)
    ap.add_argument("--seeds", type=int, default=8)
    ap.add_argument("--start-seed", type=int, default=500)
    ap.add_argument("--worlds", default="MILK0,MILK1,MILK3,YARN2,MIXED")
    ap.add_argument("--opps", default="main.py,versions/v61e.py")
    args = ap.parse_args()

    worlds = args.worlds.split(",")
    opps = args.opps.split(",")
    print(f"HOLDOUT: A={args.a}  seeds {args.start_seed}-{args.start_seed+args.seeds-1}"
          f"  worlds {worlds}  opps {opps}")
    all_m = []
    tot_w = tot_n = 0
    for opp in opps:
        for w in worlds:
            g = run(args.a, opp, args.seeds, args.start_seed, w)
            wins = sum(1 for a, b in g if a > b)
            n = len(g)
            marg = [a - b for a, b in g]
            mm = statistics.mean(marg) if marg else 0.0
            print(f"  vs {os.path.basename(opp):<12} {w:<6}: {wins}/{n}"
                  f" ({wins/max(1,n):.0%})  margin {mm:+,.0f}")
            all_m += marg
            tot_w += wins
            tot_n += n
    mu = statistics.mean(all_m) if all_m else 0.0
    sd = statistics.pstdev(all_m) if len(all_m) > 1 else 0.0
    print(f"\nPOOLED: {tot_w}/{tot_n} ({tot_w/max(1,tot_n):.1%})  "
          f"margin {mu:+,.0f}  mu/sigma {mu/sd if sd else float('nan'):.3f}")

if __name__ == "__main__":
    main()
