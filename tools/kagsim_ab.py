"""kagsim_ab.py — big UNPINNED paired A/B on the C++ engine .

Natural shop draws (the live condition; the shop re-roll trap is inherent and
identical to the ladder).  Each seed plays both seats.  Parity: kagsim
unpinned was trust-checked reward-identical to the python engine; re-verify
any 2 seeds against a python run before believing a verdict (--parity prints
banks per seed for eyeball diff).

Usage:
  python tools/kagsim_ab.py --a versions/v74d.py --b versions/pool_band_killer.py
      --seeds 77 --start-seed 519 [--procs 8]
"""
import argparse, importlib.util, os, statistics, sys
from multiprocessing import Pool

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.agent

def play_seed(args):
    a_path, b_path, seed = args
    import kagsim
    res = []
    for seat_a in (0, 1):
        agent_a = _load(a_path, f"a{seed}{seat_a}")
        agent_b = _load(b_path, f"b{seed}{seat_a}")
        g = kagsim.Game(seed)
        agents = (agent_a, agent_b) if seat_a == 0 else (agent_b, agent_a)
        while not g.done:
            g.step(agents[0](g.observe(0)), agents[1](g.observe(1)))
        ra = g.reward(seat_a)
        rb = g.reward(1 - seat_a)
        res.append((seed, seat_a, ra, rb))
    return res

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True)
    ap.add_argument("--b", required=True)
    ap.add_argument("--seeds", type=int, default=77)
    ap.add_argument("--start-seed", type=int, default=519)
    ap.add_argument("--procs", type=int, default=max(1, os.cpu_count() - 1))
    ap.add_argument("--parity", action="store_true", help="print per-game banks")
    args = ap.parse_args()

    jobs = [(args.a, args.b, s)
            for s in range(args.start_seed, args.start_seed + args.seeds)]
    with Pool(args.procs) as pool:
        out = pool.map(play_seed, jobs)
    games = [g for pair in out for g in pair]
    margins = [ra - rb for (_, _, ra, rb) in games]
    w = sum(1 for m in margins if m > 0)
    l = sum(1 for m in margins if m < 0)
    if args.parity:
        for (seed, seat, ra, rb) in games:
            print(f"  seed {seed} seatA={seat}: A {ra:,.0f} vs B {rb:,.0f}")
    mu = statistics.mean(margins)
    sd = statistics.stdev(margins) if len(margins) > 1 else 0
    print(f"A={args.a} vs B={args.b}  n={len(games)} games "
          f"(seeds {args.start_seed}-{args.start_seed+args.seeds-1}, both seats)")
    print(f"  record {w}W-{l}L-{len(games)-w-l}T  win% {100*w/len(games):.1f}")
    print(f"  mean A bank {statistics.mean(g[2] for g in games):,.0f} | "
          f"mean margin {mu:+,.0f}  sd {sd:,.0f}  mu/sigma {mu/max(sd,1e-9):.3f}")

if __name__ == "__main__":
    main()
