"""Build fork/c28.py = c23s + the compiled strawberry-takeover programs
.  The offline table (fork/cv_programs.json, from
tools/route_compiler.py) is embedded; the runtime executes a program only
when EVERY live precondition holds: str_bad world (c23s's proven gate),
day >= 10, tile actually holds the expected strawberry, actor stands where
the compiler predicted, seeds available under the atomic-PLANT rule.
Planted tiles are registered into the existing _CA machinery, which does
rescue-harvesting, credit and sells (proven, zero plant deaths to date).
"""
import json, sys

TABLE = sys.argv[1] if len(sys.argv) > 1 else r'fork\cv_programs.json'
OUT = sys.argv[2] if len(sys.argv) > 2 else r'fork\c29.py'
CAP = int(sys.argv[3]) if len(sys.argv) > 3 else 6

programs = json.load(open(TABLE, encoding='utf-8'))
# v1 safety: both the clear and the plant must be at day >= 10 (the tested
# forecast boundary — c27 died at day 6 decisions).
filtered = {}
kept = 0
for rid, plist in programs.items():
    out = [p for p in plist if p['clear']['step'] // 24 >= 10 and p['plant']['step'] // 24 >= 10]
    if out:
        filtered[rid] = out
        kept += len(out)
print(f'programs kept after day-10 filter: {kept}')

blob = json.dumps(filtered, separators=(',', ':'))

LAYER = '''

# ---------------------------------------------------------------------------
# CP LAYER: compiled strawberry-takeover programs .
# Offline compiler: tools/route_compiler.py; spec: docs/COMPILER_PLAN.md;
# mechanism proof: work//review2/splice_proof.json ( review 2).
# ---------------------------------------------------------------------------
import json as _cp_json
_CP_TABLE = _cp_json.loads(%r)
# ATTACH PER THE FILE'S OWN CONVENTION (note): the live chain head is
# cha20_entry_agent/kaggle_agent, NOT the stale name `agent` (which stops
# being the head ~1,200 lines before EOF — grabbing it amputates the tail
# layers: T62A terminal liquidation, PIPE EarlyCycle opening, mirror
# classifier, WB3, e402, merge, IG).
_CP_PARENT = cha20_entry_agent
_CP_STATES = {}
_CP_MAX_TAKEOVERS = %d
_CP_REPORT = {"cp_digs": 0, "cp_plants": 0, "cp_skips": 0, "cp_naked": 0,
              "cp_reserve_blocks": 0, "cp_errors": 0}


def _cp_index(rid):
    """(step -> list of (kind, program)) for one route id."""
    idx = {}
    for p in _CP_TABLE.get(str(rid), []):
        idx.setdefault(p["clear"]["step"], []).append(("clear", p))
        idx.setdefault(p["plant"]["step"], []).append(("plant", p))
    return idx


def cp_agent(observation, configuration=None):
    action = _CP_PARENT(observation, configuration)
    try:
        step = int(observation["step"]); seat = int(observation["player"])
        if step == 0:
            for k in _CP_REPORT:
                _CP_REPORT[k] = 0
        st = _CP_STATES.get(seat)
        if st is None or step <= st.get("last", -1):
            st = _CP_STATES[seat] = {"last": step, "idx": None, "armed": {},
                                     "reserved": 0, "done": 0}
        st["last"] = step
        # expire armed digs whose plant step passed without planting
        for xy in [xy for xy, ps in st["armed"].items() if ps < step]:
            del st["armed"][xy]
            st["reserved"] = max(0, st["reserved"] - 1)
            _CP_REPORT["cp_naked"] += 1
        if not isinstance(action, dict) or step // 24 < 10:
            return action
        if configuration is not None and any(configuration.get(k, v) != v for k, v in
                (("boardSize", 10), ("turnsPerDay", 24), ("shedCapacity", 100),
                 ("maxMarketOrdersPerTurn", 10))):
            return action
        if st["idx"] is None:
            native = _IMPL.chassis.players.get(seat)
            if not native:
                return action
            st["idx"] = _cp_index(native["route"])
        hits = st["idx"].get(step)
        if not hits:
            return action
        farm = observation["farms"][seat]
        shops = observation["town"].get("unlocked_shops", [])
        prices = observation["market"]["prices"]
        str_bad = (len(shops) >= 2
                   and not any(s in _CA_STR_SHOPS for s in shops)
                   and int(prices.get("CARROT", 0)) >= 35)
        if not str_bad:
            _CP_REPORT["cp_skips"] += len(hits)
            return action
        positions = [tuple(farm["farmer"])] + [tuple(h) for h in farm["hands"]]
        units = [list(action.get("farmer") or ["PASS"])] + [list(c) for c in (action.get("hands") or [])]
        priv = observation["private"]
        changed = False
        for kind, p in hits:
            tile_xy = tuple(p["tile"])
            actor = p[kind]["actor"]
            if actor >= len(positions) or actor >= len(units):
                _CP_REPORT["cp_skips"] += 1
                continue
            if positions[actor] != tile_xy:
                _CP_REPORT["cp_skips"] += 1
                continue
            tile = farm["tiles"][tile_xy[1]][tile_xy[0]]
            if kind == "clear":
                planned = sum(1 for c in units if c and c[:2] == ["PLANT", "CARROT"])
                seeds = int(priv["seeds"].get("CARROT", 0))
                if st["done"] + len(st["armed"]) >= _CP_MAX_TAKEOVERS:
                    _CP_REPORT["cp_skips"] += 1
                elif seeds - planned - st["reserved"] < 1:
                    # never dig without a reservable seed (naked-dig guard)
                    _CP_REPORT["cp_reserve_blocks"] += 1
                elif (isinstance(tile, dict) and tile.get("kind") == "PLANT"
                        and tile.get("crop") == "STRAWBERRY"
                        and units[actor] and units[actor][0] == p["clear"]["orig"]):
                    units[actor] = ["DIG"]
                    st["armed"][tile_xy] = p["plant"]["step"]
                    st["reserved"] += 1
                    _CP_REPORT["cp_digs"] += 1
                    changed = True
                else:
                    _CP_REPORT["cp_skips"] += 1
            else:  # plant
                if st["armed"].pop(tile_xy, None) is None:
                    _CP_REPORT["cp_skips"] += 1
                    continue
                st["reserved"] = max(0, st["reserved"] - 1)
                planned = sum(1 for c in units if c and c[:2] == ["PLANT", "CARROT"])
                seeds = int(priv["seeds"].get("CARROT", 0))
                if tile is not None or seeds - planned <= 0:
                    _CP_REPORT["cp_naked"] += 1
                    continue
                units[actor] = ["PLANT", "CARROT"]
                st["done"] += 1
                _CP_REPORT["cp_plants"] += 1
                changed = True
                try:
                    ca = _CA_STATE.get(seat)
                    if ca is not None:
                        ca["tiles"][tile_xy] = step // 24
                        if ca.get("spare_carrot", 0) > 0:
                            ca["spare_carrot"] -= 1
                except Exception:
                    pass
        if changed:
            action = dict(action)
            action["farmer"] = units[0]
            action["hands"] = units[1:]
        return action
    except Exception:
        _CP_REPORT["cp_errors"] += 1
        return action


import collections as _cp_coll
cp_agent.telemetry = _cp_coll.ChainMap(_CP_REPORT, _CP_PARENT.telemetry)
cha20_entry_agent = cp_agent
kaggle_agent = cha20_entry_agent
''' % (blob, CAP)

src = open(r'fork\c23s.py', encoding='utf-8').read()
assert '_CP_TABLE' not in src
out = src.rstrip('\n') + '\n' + LAYER
import ast
ast.parse(out)
open(OUT, 'w', encoding='utf-8', newline='\n').write(out)
print(f'wrote {OUT} ({len(out):,} chars, cap {CAP}), syntax OK')
