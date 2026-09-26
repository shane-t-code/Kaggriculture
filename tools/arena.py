"""arena.py — the Top-10 Margin Matrix .

Turns a public replay into a coin-faithful local fixture (seed + pinned shop
sequence + opponent tape, per Exp 89/93 conventions) and plays OUR agent in
the seat of the reference team, against the reconstructed opponent.

The row's key number is our_bank - ref_bank: how much less we make than the
top team IN THE SAME WORLD against THE SAME OPPONENT.  Margin vs the tape is
secondary (the tape can't adapt to us; the world is what's controlled).

LOCAL ONLY: reconstructed tapes are never submitted (.md).

Usage:
  python tools/arena.py run <replay.json> <ref_team_name> <agent.py> [tag] [out.jsonl]
  python tools/arena.py sum <out.jsonl>
"""
import ast, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
os.chdir(ROOT)


def load_replay(path):
    if path.endswith(".gz"):
        import gzip
        return json.load(gzip.open(path, "rt", encoding="utf-8"))
    return json.load(open(path, encoding="utf-8"))


def shop_sequence(rep):
    seq, prev = [], 0
    for t in range(0, len(rep["steps"]), 24):
        cur = rep["steps"][t][0]["observation"]["town"]["unlocked_shops"]
        if len(cur) > prev:
            seq += cur[prev:]
            prev = len(cur)
    return seq


def tape_agent(rep, seat):
    steps = rep["steps"]
    table = []
    for t in range(len(steps) - 1):
        a = steps[t + 1][seat].get("action") or {}
        table.append({"farmer": a.get("farmer") or ["PASS"],
                      "hands": a.get("hands") or [],
                      "market": a.get("market") or []})

    def agent(obs, config=None):
        t = obs["step"]
        if 0 <= t < len(table):
            return table[t]
        return {"farmer": ["PASS"], "hands": [], "market": []}
    return agent


def cmd_run(args):
    rp, ref_team, agent_file = args[0], args[1], args[2]
    tag = args[3] if len(args) > 3 else os.path.basename(agent_file)
    out = args[4] if len(args) > 4 else r"results\arena.jsonl"
    save = args[5] if len(args) > 5 else None
    rep = load_replay(rp)
    teams = rep["info"].get("TeamNames")
    if isinstance(teams, str):
        teams = ast.literal_eval(teams)
    if ref_team not in teams:
        raise SystemExit(f"{ref_team!r} not in {teams}")
    ref_seat = teams.index(ref_team)
    opp_seat = 1 - ref_seat
    seed = rep.get("configuration", {}).get("seed") or rep["info"].get("seed")
    if not seed:
        raise SystemExit("no seed in replay")
    rewards = [rep["steps"][-1][i]["reward"] for i in range(2)]
    seq = shop_sequence(rep)

    from run_local import _silence_fds
    import shop_pin
    shop_pin.install(seq)
    try:
        from kaggle_environments import make
        with _silence_fds():
            env = make("kaggriculture",
                       configuration={"episodeSteps": 720, "seed": seed})
            #  review-4 fix (note): the candidate must sit in the
            # REFERENCE team's actual seat — weed RNG consumes farm 0's empty
            # tiles first, so seats are not interchangeable.
            pair = [None, None]
            pair[ref_seat] = agent_file
            pair[opp_seat] = tape_agent(rep, opp_seat)
            env.run(pair)
        final = env.steps[-1]
    finally:
        shop_pin.uninstall()
    if save:
        import gzip
        with gzip.open(save, "wt", encoding="utf-8") as fh:
            fh.write(env.toJSON() if isinstance(env.toJSON(), str)
                     else json.dumps(env.toJSON()))
    row = {
        "tag": tag, "episode": os.path.basename(rp),
        "world_shops": seq, "seed": seed, "seat": ref_seat,
        "ref_team": teams[ref_seat], "opp_team": teams[opp_seat],
        "ref_bank": float(rewards[ref_seat] or 0),
        "opp_bank_real": float(rewards[opp_seat] or 0),
        "our_bank": float(final[ref_seat].reward or 0),
        "tape_bank_now": float(final[opp_seat].reward or 0),
        "gap_vs_ref": float(final[ref_seat].reward or 0) - float(rewards[ref_seat] or 0),
        "margin_vs_tape": float(final[ref_seat].reward or 0) - float(final[opp_seat].reward or 0),
        "statuses": [s.status for s in final],
    }
    with open(out, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row) + "\n")
    print(f"{tag} vs {teams[opp_seat]} (world of ep {os.path.basename(rp)}):")
    print(f"  ref {teams[ref_seat]} scored {row['ref_bank']:,.0f}; we scored "
          f"{row['our_bank']:,.0f}  GAP {row['gap_vs_ref']:+,.0f}")
    print(f"  tape scored {row['tape_bank_now']:,.0f} now vs {row['opp_bank_real']:,.0f} real "
          f"(fidelity {row['tape_bank_now'] - row['opp_bank_real']:+,.0f})")


def cmd_sum(args):
    path = args[0] if args else r"results\arena.jsonl"
    rows = [json.loads(l) for l in open(path, encoding="utf-8")]
    by_tag = {}
    for r in rows:
        by_tag.setdefault(r["tag"], []).append(r)
    for tag, rs in by_tag.items():
        gaps = sorted(r["gap_vs_ref"] for r in rs)
        med = gaps[len(gaps) // 2]
        fid = sorted(abs(r["tape_bank_now"] - r["opp_bank_real"]) for r in rs)
        print(f"{tag}: n={len(rs)}  gap_vs_ref med {med:+,.0f} "
              f"[{gaps[0]:+,.0f}..{gaps[-1]:+,.0f}]  "
              f"tape-fidelity med abs {fid[len(fid) // 2]:,.0f}")
        for r in sorted(rs, key=lambda r: r["gap_vs_ref"]):
            print(f"   {r['gap_vs_ref']:+9,.0f} vs {r['ref_team']:<22} "
                  f"(opp {r['opp_team']:<22} ep {r['episode']})")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "run":
        cmd_run(sys.argv[2:])
    elif cmd == "sum":
        cmd_sum(sys.argv[2:])
    else:
        raise SystemExit("run|sum")
