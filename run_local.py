#!/usr/bin/env python3
"""
run_local.py — Kaggriculture local evaluation harness.

Why this exists: submissions are the scarce resource (5/day, only latest 2 active).
Local games are free and unlimited. Every hypothesis should be tested here first.

Design follows the measurement protocol in .md:
  * PAIRED same-seed A/B (unpaired is ~67x noisier)
  * BOTH SEATS (seat 0 and seat 1) for every seed
  * Reports WIN RATE as the headline number, not mean bank
    (ratings move on win/loss only; margin is irrelevant)

Usage:
    python run_local.py                          # main.py vs built-in "starter"
    python run_local.py --a main.py --b starter  # explicit
    python run_local.py --seeds 16               # more seeds = tighter
    python run_local.py --replay                 # dump replays/replay_seed<N>.json

Built-in opponents available by name: "pass", "random", "starter".
"""
from __future__ import annotations

import argparse
import json
import os
import re
import statistics
import sys
import time

# kaggle-environments bundles open_spiel, which prints harmless "Unknown game 'universal_poker'"
# warnings on import for poker variants absent from this build. They do not affect Kaggriculture.
# open_spiel prints from C++, straight to the OS file descriptors, so contextlib.redirect_stdout
# (which only rebinds Python's sys.stdout) does NOT catch it -- we have to dup2 the real fds.
import contextlib


@contextlib.contextmanager
def _silence_fds():
    """Silence C-level stdout/stderr. Works on Windows and POSIX."""
    devnull = saved_out = saved_err = None
    try:
        sys.stdout.flush()
        sys.stderr.flush()
        devnull = os.open(os.devnull, os.O_WRONLY)
        saved_out, saved_err = os.dup(1), os.dup(2)
        os.dup2(devnull, 1)
        os.dup2(devnull, 2)
        yield
    finally:
        try:
            sys.stdout.flush()
            sys.stderr.flush()
        except Exception:
            pass
        if saved_out is not None:
            os.dup2(saved_out, 1)
            os.close(saved_out)
        if saved_err is not None:
            os.dup2(saved_err, 2)
            os.close(saved_err)
        if devnull is not None:
            os.close(devnull)


try:
    with _silence_fds():
        from kaggle_environments import make
except ImportError:
    sys.exit("kaggle-environments not installed.  pip install -U 'kaggle-environments>=1.32.7'")


def check_version() -> None:
    """The engine changed twice mid-competition. Benchmarks across versions are not comparable."""
    v = "unknown"
    try:
        from importlib.metadata import version as _pkg_version
        v = _pkg_version("kaggle-environments")
    except Exception:
        try:
            import kaggle_environments as ke
            v = str(getattr(ke, "__version__", "unknown"))
        except Exception:
            pass
    print(f"kaggle-environments version: {v}")
    nums = re.findall(r"\d+", v)
    if len(nums) >= 3 and tuple(int(n) for n in nums[:3]) < (1, 32, 7):
        print("  !! WARNING: need >= 1.32.7 (1.32.6 and 1.32.7 were balance changes).")
        print("     pip install -U kaggle-environments")


def play(agent_a, agent_b, seed: int, steps: int = 720, debug: bool = False):
    """Run one episode. Returns (bank_a, bank_b, env)."""
    env = make(
        "kaggriculture",
        configuration={"episodeSteps": steps, "seed": seed},
        debug=debug,
    )
    env.run([agent_a, agent_b])
    final = env.steps[-1]
    # A crashed agent silently PASSes forever and its bank sits at starting money —
    # that is a broken measurement, not a loss. Shout about it. (Learned the hard way:
    # a UTF-8 BOM from PowerShell Set-Content made an agent die on import and 'lose' 0-32.)
    for i, s in enumerate(final):
        if s.status != "DONE":
            print(f"  !! WARNING seed {seed}: agent {i} ended with status {s.status!r} "
                  f"(reward {s.reward}) — RESULT INVALID, agent likely crashed. "
                  f"Re-run with --debug to see the error.")
    return final[0].reward, final[1].reward, env


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", default="main.py", help="agent A (file path or builtin name)")
    ap.add_argument("--b", default="starter", help="agent B (file path or builtin name)")
    ap.add_argument("--seeds", type=int, default=8, help="number of seeds (each played both seats)")
    ap.add_argument("--start-seed", type=int, default=0)
    ap.add_argument("--steps", type=int, default=720)
    ap.add_argument("--replay", action="store_true", help="dump replay JSON per seed")
    ap.add_argument("--debug", action="store_true", help="engine debug output (shows invalid actions!)")
    args = ap.parse_args()

    check_version()
    print(f"\nA = {args.a}\nB = {args.b}")
    print(f"{args.seeds} seeds x 2 seats = {args.seeds * 2} games\n")

    os.makedirs("replays", exist_ok=True)

    a_wins = b_wins = ties = 0
    margins: list[float] = []          # A bank - B bank, from A's perspective
    per_seed: list[tuple] = []
    t0 = time.time()

    for i in range(args.seeds):
        seed = args.start_seed + i

        # Seat 0: A first.  Seat 1: A second.  Both seats matter - seat asymmetry is real.
        a0, b0, env0 = play(args.a, args.b, seed, args.steps, args.debug)
        b1, a1, env1 = play(args.b, args.a, seed, args.steps, args.debug)

        for (abank, bbank) in ((a0, b0), (a1, b1)):
            margins.append(abank - bbank)
            if abank > bbank:
                a_wins += 1
            elif bbank > abank:
                b_wins += 1
            else:
                ties += 1

        per_seed.append((seed, a0, b0, a1, b1))
        print(
            f"  seed {seed:>3}  seat0: A {a0:>9,.0f} vs B {b0:>9,.0f}   "
            f"seat1: A {a1:>9,.0f} vs B {b1:>9,.0f}"
        )

        if args.replay:
            with open(f"replays/replay_seed{seed}_seat0.json", "w") as f:
                json.dump(env0.toJSON(), f)

    n = a_wins + b_wins + ties
    winrate = a_wins / n if n else 0.0
    mean_margin = statistics.mean(margins) if margins else 0.0
    sd_margin = statistics.pstdev(margins) if len(margins) > 1 else 0.0
    # mu/sigma is the quantity that actually predicts win probability (see .md)
    mu_over_sigma = (mean_margin / sd_margin) if sd_margin else float("nan")

    print("\n" + "=" * 62)
    print(f"  WIN RATE (A)      {winrate:>8.1%}     <-- the number that matters")
    print(f"  record            {a_wins}W - {b_wins}L - {ties}T   (n={n})")
    print(f"  mean margin       {mean_margin:>+10,.0f}   (informative, NOT the objective)")
    print(f"  sd of margin      {sd_margin:>10,.0f}")
    print(f"  mu/sigma          {mu_over_sigma:>10.3f}   (Pr[win] ~= Phi(mu/sigma))")
    print(f"  wall clock        {time.time() - t0:>10.1f}s")
    print("=" * 62)

    if n and winrate > 0.5 and mean_margin < 0:
        print("\n  NOTE: A wins more often but loses on average margin.")
        print("        That is GOOD on this ladder - ratings ignore margin.")
    if args.seeds < 8:
        print("\n  NOTE: <8 seeds is a smoke test, not evidence. Use 16+ before believing a result.")
    print("\n  Reminder: if your change alters TILE OCCUPANCY (hands, land, plant count),")
    print("  the town shop draw changes too and the seed is no longer a control (~77 seeds needed).")


if __name__ == "__main__":
    main()