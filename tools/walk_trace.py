#!/usr/bin/env python3
"""walk_trace.py — Exp 83b: WHY the walking — path anatomy per seat.

From a local paired game, tracks every unit's position each step and
segments its day into walks (runs of MOVE) ending in either a work
action or another walk (abandoned = re-target thrash).  Reports per
seat: walk-length distribution, walks per work action, abandoned-walk
rate (direction flips mid-walk), shed round-trips, and mean same-tile
work streak (stickiness).  Positions come from obs.farms[seat]
(farmer + hands, refreshed each step; hands respawn daily).

Usage: python tools/walk_trace.py <agentA> <agentB> <seed>
"""
import sys
from collections import Counter
from kaggle_environments import make

MOVES = {"NORTH", "SOUTH", "EAST", "WEST"}
SHED = (0, 0)  # placeholder; real shed tile read from first farmer pos at d0h0


def op_of(act, ui):
    ops = [act.get("farmer")] + list(act.get("hands") or [])
    if ui < len(ops) and isinstance(ops[ui], list) and ops[ui]:
        return ops[ui][0]
    return "PASS"


def trace(a, b, seed):
    env = make("kaggriculture", configuration={"seed": seed}, debug=False)
    env.run([a, b])
    st = env.steps
    out = {}
    for seat in (0, 1):
        walk_lens = Counter()      # length -> count (walks that END IN WORK)
        abandoned = 0              # walk interrupted by a NEW direction after a non-move gap or reversal
        reversals = 0              # N<->S or E<->W flip inside one walk
        works = 0
        shed_trips = 0
        streaks = []               # consecutive work actions on the same tile
        # Exp 84a: ANIMAL-STOP anatomy — one "stop" = consecutive work actions
        # on one animal tile; the King's canonical stop is FEED+CARE+COLLECT
        # (2.48 ops/stop vs our greedy's 1.41, Exp 83b).
        animal_stops = []          # list of tuple(sorted ops) per stop
        stop_state = {}            # ui -> {"pos": (x,y), "ops": [..]} current stop
        cur = {}                   # ui -> {"len": int, "last": op, "streak": int, "pos": (x,y)}

        def flush_stop(ui):
            s = stop_state.pop(ui, None)
            if s and s["ops"]:
                animal_stops.append(tuple(sorted(s["ops"])))

        for si in range(1, len(st)):
            day = (si - 1) // 24
            act = st[si][seat].get("action") or {}
            farm = st[si - 1][0]["observation"]["farms"][seat]
            tiles = farm.get("tiles") or []
            poss = [tuple(farm.get("farmer") or (0, 0))] + [
                tuple(p) for p in (farm.get("hands") or []) if isinstance(p, list)]
            hour = (si - 1) % 24
            if hour == 0:
                # hands respawn: reset per-unit walk state each dawn
                for ui in list(stop_state):
                    flush_stop(ui)
                cur = {}
            n_units = len([act.get("farmer")] + list(act.get("hands") or []))
            for ui in range(n_units):
                op = op_of(act, ui)
                state = cur.setdefault(ui, {"len": 0, "last": None, "streak": 0, "pos": None})
                pos = poss[ui] if ui < len(poss) else None
                # animal-stop tracking: work on an animal tile joins the current
                # stop; anything else (move/pass/tile change) closes it.
                on_animal = False
                if pos is not None and op not in MOVES and op != "PASS":
                    try:
                        t = tiles[pos[1]][pos[0]]
                        on_animal = isinstance(t, dict) and bool(t.get("animal"))
                    except (IndexError, TypeError):
                        pass
                if on_animal:
                    s = stop_state.get(ui)
                    if s is None or s["pos"] != pos:
                        flush_stop(ui)
                        stop_state[ui] = {"pos": pos, "ops": [op]}
                    else:
                        s["ops"].append(op)
                else:
                    flush_stop(ui)
                if op in MOVES:
                    if state["streak"]:
                        streaks.append(state["streak"])
                        state["streak"] = 0
                    if state["last"] in MOVES:
                        opp = {"NORTH": "SOUTH", "SOUTH": "NORTH",
                               "EAST": "WEST", "WEST": "EAST"}
                        if op == opp.get(state["last"]):
                            reversals += 1
                    state["len"] += 1
                    if pos == (2, 1) or pos == (1, 1):
                        pass
                elif op == "PASS":
                    if state["len"]:
                        abandoned += 1  # walked then stopped without working
                        state["len"] = 0
                else:
                    works += 1
                    if state["len"]:
                        walk_lens[state["len"]] += 1
                        state["len"] = 0
                    state["streak"] += 1
                state["last"] = op
                if pos is not None and pos == (2, 2):
                    pass
                state["pos"] = pos
        for ui in list(stop_state):
            flush_stop(ui)
        total_walked = sum(l * c for l, c in walk_lens.items())
        n_walks = sum(walk_lens.values())
        combo_ct = Counter(animal_stops)
        out[seat] = {
            "animal_stops": len(animal_stops),
            "animal_ops_per_stop": (sum(len(c) for c in animal_stops)
                                    / max(1, len(animal_stops))),
            "animal_top_combos": combo_ct.most_common(6),
            "works": works,
            "walks_ending_in_work": n_walks,
            "mean_walk_len": total_walked / max(1, n_walks),
            "walk_len_dist": {k: walk_lens[k] for k in sorted(walk_lens)[:12]},
            "long_walks_6plus": sum(c for l, c in walk_lens.items() if l >= 6),
            "abandoned_walks": abandoned,
            "reversals": reversals,
            "mean_work_streak": sum(streaks) / max(1, len(streaks)),
        }
    banks = [s.get("reward") for s in st[-1]]
    return out, banks


def main():
    a, b, seed = sys.argv[1], sys.argv[2], int(sys.argv[3])
    out, banks = trace(a, b, seed)
    print(f"seed {seed}: A={a.split('/')[-1]} {banks[0]:,.0f}  vs  B={b.split('/')[-1]} {banks[1]:,.0f}")
    for seat, label in ((0, "A"), (1, "B")):
        o = out[seat]
        print(f"\n  {label}: work actions {o['works']:,}; walks ending in work {o['walks_ending_in_work']:,} "
              f"(mean len {o['mean_walk_len']:.2f}, 6+ tiles: {o['long_walks_6plus']})")
        print(f"     abandoned walks (walk->PASS) {o['abandoned_walks']:,}; mid-walk reversals {o['reversals']:,}")
        print(f"     mean same-tile work streak {o['mean_work_streak']:.2f}")
        print(f"     ANIMAL stops {o['animal_stops']:,}; ops/stop {o['animal_ops_per_stop']:.2f}")
        for combo, n in o["animal_top_combos"]:
            print(f"        {n:4d} x {'+'.join(combo)}")
        print(f"     walk length dist: {o['walk_len_dist']}")


if __name__ == "__main__":
    main()
