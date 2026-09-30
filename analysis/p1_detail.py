# PHASE 1 DETAIL  — one top-team recording vs our live agent in the
# recording's own world: print, for the first N steps, the recording's market
# orders with money/hands in the REAL game vs the MOVED game, so the first
# failed purchase and its cause are visible.  Local only.
# Usage: python -X utf8 p1_detail.py <episode> <seat> [last_step]
import ast
import json
import sys
from pathlib import Path

R = Path(r"C:\Kaggriculture")
sys.path.insert(0, str(R))
sys.dont_write_bytecode = True
DTRW = str(R / "work" / "build_a" / "grow" / "variants" / "dtrw.py")


def main():
    ep, seat = sys.argv[1], int(sys.argv[2])
    last = int(sys.argv[3]) if len(sys.argv) > 3 else 60
    from run_local import _silence_fds
    with _silence_fds():
        from kaggle_environments import make
    from tools import shop_pin
    from tools.arena import load_replay, tape_agent, shop_sequence
    rep = load_replay(str(R / "replays" / "top10" / f"ep_{ep}.json.gz"))
    teams = rep["info"].get("TeamNames")
    if isinstance(teams, str):
        teams = ast.literal_eval(teams)
    seed = rep.get("configuration", {}).get("seed") or rep["info"].get("seed")
    pair = [None, None]
    pair[seat] = tape_agent(rep, seat)
    pair[1 - seat] = DTRW
    shop_pin.install(shop_sequence(rep))
    try:
        with _silence_fds():
            env = make("kaggriculture",
                       configuration={"episodeSteps": 720, "seed": seed})
            env.run(pair)
            new = env.toJSON()["steps"]
    finally:
        shop_pin.uninstall()
    orig = rep["steps"]
    print(f"ep {ep} recording of {teams[seat]} (real opponent {teams[1-seat]}) "
          f"vs dtrw")
    for t in range(1, last + 1):
        a = orig[t][seat].get("action") or {}
        mk = a.get("market") or []
        ro = orig[t][1 - seat].get("action") or {}
        no = new[t][1 - seat].get("action") or {}
        of = orig[t][0]["observation"]["farms"][seat]
        nf = new[t][0]["observation"]["farms"][seat]
        if mk or len(of["hands"]) != len(nf["hands"]) and t % 24 in (0, 1, 2):
            print(f"t{t-1:3d} orders {json.dumps(mk)[:150]}")
            print(f"      after: money real {of['money']:9.1f} moved "
                  f"{nf['money']:9.1f} | hands real {len(of['hands'])} moved "
                  f"{len(nf['hands'])} | real-opp orders "
                  f"{json.dumps(ro.get('market') or [])[:90]} | dtrw orders "
                  f"{json.dumps(no.get('market') or [])[:90]}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
