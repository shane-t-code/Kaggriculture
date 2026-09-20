# ---------------------------------------------------------------------------
#  MIRRORSORT layer (Shane Thivaharraja fork, Exp 123): steepest book
# first — the intra-turn market race.
#
# Engine (kaggriculture.py L545-628): market lists execute slot-by-slot, and
# within a slot unit-by-unit at a shared pre-commit quote.  So when both
# players sell the same product in the same TURN, the one whose order sits in
# the EARLIER slot sells at pre-crash prices and the other dumps into the
# glut.  The edge per unit is the book's crash steepness; melon and wool are
# quadratic (above_func sq, targets 3.6 / 3.2), wheat/egg are logarithmic
# (queue position worth ~nothing).  The chassis's own _v224_sales_first puts
# SELLs ahead of other orders but keeps ROUTE order within them — so against
# the 149 byte-copies (identical lists every turn) sorting our SELL block
# steepest-first wins the steep books and concedes only the flat ones.
# A pure permutation of the same orders: solo-neutral by construction (books
# are independent; same-book totals unchanged), occupancy and production
# untouched.  Guard: a SELL never jumps ahead of a non-SELL naming the same
# item (buy-then-sell order preserved) — we only permute within each
# contiguous run of SELLs.
# Own implementation, Apache-2.0 like the chassis it wraps.
# ---------------------------------------------------------------------------
# steepest first: sq books, then linear, then hinge-above-sqrt, then log
_MS_RANK = {"MELON": 0, "WOOL": 1, "MILK": 2, "STRAWBERRY": 3, "TOMATO": 4,
            "CARROT": 5, "EGG": 6, "WHEAT": 7, "FERTILIZER": 8}
_MS_REPORT = {"ms_turns": 0, "ms_errors": 0}

_MS_PARENT = agent
del agent


def agent(observation, configuration=None):
    action = _MS_PARENT(observation, configuration)
    try:
        if not isinstance(action, dict):
            return action
        market = action.get("market") or []
        if len(market) < 2:
            return action
        out = []
        run = []
        def flush():
            if len(run) > 1:
                run.sort(key=lambda o: _MS_RANK.get(o[1], 9))
            out.extend(run)
            del run[:]
        for o in market:
            if (isinstance(o, (list, tuple)) and len(o) >= 3 and o[0] == "SELL"
                    and o[1] in _MS_RANK):
                run.append(list(o))
            else:
                flush()
                out.append(list(o) if isinstance(o, (list, tuple)) else o)
        flush()
        if out != [list(o) if isinstance(o, (list, tuple)) else o for o in market]:
            _MS_REPORT["ms_turns"] += 1
            action = dict(action)
            action["market"] = out
    except Exception:
        _MS_REPORT["ms_errors"] += 1
    return action


agent.telemetry = _MS_REPORT
agent = globals().pop('agent')
