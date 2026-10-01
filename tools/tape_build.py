"""tape_build.py — turn a live replay's OPPONENT action stream into a local
pool agent.

The reconstructed agent replays the recorded stream verbatim by obs.step —
faithful for open-loop tapes (the killer family is one; x-ray classified,
schedules byte-stable across copies).  Analysis tool only.

Convention (validated on live replays, 99.9%): the action deciding state steps[t+1]
is stored AT steps[t+1]; an agent called with obs.step == t must therefore
emit the action stored at steps[t+1].

Usage: python tools/tape_build.py <replay.json> <out.py> [me_name]
"""
import json, sys, zlib, base64, ast

import os
ME_DEFAULT = os.environ.get("TEAM_NAME", "Shane Thivaharraja")  # our team name as shown in replays

def main():
    rp, out = sys.argv[1], sys.argv[2]
    me = sys.argv[3] if len(sys.argv) > 3 else ME_DEFAULT
    rep = json.load(open(rp, encoding="utf-8"))
    teams = rep["info"].get("TeamNames")
    if isinstance(teams, str):
        teams = ast.literal_eval(teams)
    if me not in teams:
        raise SystemExit(f"{me!r} not in {teams}")
    opp = 1 - teams.index(me)
    steps = rep["steps"]
    table = []
    for t in range(len(steps) - 1):
        a = steps[t + 1][opp].get("action") or {}
        table.append({"farmer": a.get("farmer") or ["PASS"],
                      "hands": a.get("hands") or [],
                      "market": a.get("market") or []})
    blob = base64.b85encode(zlib.compress(
        json.dumps(table, separators=(",", ":")).encode())).decode()
    src = f'''"""AUTO-GENERATED tape agent — local analysis pool only.
Source: {rp.replace(chr(92), "/")}  opponent seat of {teams[opp]!r} (vs {me!r}).
Built by tools/tape_build.py.  Open-loop replay of the recorded
stream by obs.step; steps past the recording PASS."""
import json, zlib, base64

_TABLE = json.loads(zlib.decompress(base64.b85decode(
    "{blob}")))

def agent(obs, config=None):
    t = obs["step"]
    if 0 <= t < len(_TABLE):
        return _TABLE[t]
    return {{"farmer": ["PASS"], "hands": [], "market": []}}
'''
    open(out, "w", encoding="utf-8").write(src)
    print(f"wrote {out}: {len(table)} steps, opp={teams[opp]!r}, "
          f"{len(blob)//1024} KB blob")

if __name__ == "__main__":
    main()
