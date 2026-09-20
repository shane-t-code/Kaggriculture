# ---------------------------------------------------------------------------
#  GLUTGATE layer (Shane Thivaharraja fork, Exp 123): don't sell into a
# deep glut — the live-proven mirror edge.
#
# Live decode (episode 110978823/110977722, Sep 19): "NineThree" runs the
# byte-identical 2945 farm physically (unit ops EXACT to the single op) and
# beat it +487 purely in the market stream: on d18-26 the base dumps MILK at
# $3-28 (base 160), WOOL at $55 (base 200), STRAWBERRY at $62 (base 120) —
# they prune those sells and let the stock go later, after town drain lifts
# the gutted book (every book except FERTILIZER recovers; the terminal
# liquidation at steps 712+ catches anything left).  Steady ~+20-40/day drip,
# exactly the floor-sale leak our Sep-11 review flagged.
# Rule: DROP a SELL order when the product's current price is below
# _GG_FRAC x its engine base price.  Never touch FERTILIZER (price only
# decays — selling now is always right) or WHEAT (feed engine, log book).
# Coupling guards: never prune at hour >= 21 (SHEDROOM's overflow-rescue
# window), when the shed is near capacity (pruned goods must never cause
# midnight overflow destruction), or from day 29 (endgame flow untouched).
# Own implementation, Apache-2.0 like the chassis it wraps.
# ---------------------------------------------------------------------------
_GG_FRAC = 0.30
# v102b: EXEMPLAR-CONFORMANT scope.  v102a pruned all 7 books and lost the
# mirror 13W-26L: melon under $75 is the route's own deliberate caravan dump
# (blocking a designed dump = coupling damage).  NineThree's observed edits
# touch ONLY milk/wool/strawberry, and partially (a 6-8 unit/day trickle
# still flows).  Port the behavior, not the generalization.
_GG_BASE = {"STRAWBERRY": 120, "MILK": 160, "WOOL": 200}
_GG_TRICKLE = 8               # units/day/product still allowed through
_GG_SHED_MAX = 85
_GG_REPORT = {"gg_pruned": 0, "gg_turns": 0, "gg_errors": 0}
_GG_DAY = {}

_GG_PARENT = agent
del agent


def agent(observation, configuration=None):
    action = _GG_PARENT(observation, configuration)
    try:
        step = int(observation["step"])
        day, hour = step // 24, step % 24
        if day >= 29 or hour >= 21 or not isinstance(action, dict):
            return action
        market = action.get("market") or []
        if not market:
            return action
        shed = observation["private"]["shed"]
        if sum(int(v) for v in shed.values()) >= _GG_SHED_MAX:
            return action
        prices = observation["market"]["prices"]
        seat = int(observation["player"])
        st = _GG_DAY.setdefault(seat, {"day": -1, "sold": {}})
        if st["day"] != day:
            st["day"] = day
            st["sold"] = {}
        kept = []
        pruned = 0
        for o in market:
            if (isinstance(o, (list, tuple)) and len(o) >= 3 and o[0] == "SELL"
                    and o[1] in _GG_BASE
                    and int(prices.get(o[1], 10**9)) < _GG_FRAC * _GG_BASE[o[1]]):
                allow = max(0, _GG_TRICKLE - st["sold"].get(o[1], 0))
                q = min(int(o[2]), allow)
                if q > 0:
                    st["sold"][o[1]] = st["sold"].get(o[1], 0) + q
                    kept.append([o[0], o[1], q])
                    if q < int(o[2]):
                        pruned += 1
                else:
                    pruned += 1
                continue
            st_q = int(o[2]) if (isinstance(o, (list, tuple)) and len(o) >= 3
                                 and o[0] == "SELL" and o[1] in _GG_BASE) else 0
            if st_q:
                st["sold"][o[1]] = st["sold"].get(o[1], 0) + st_q
            kept.append(o)
        if pruned:
            _GG_REPORT["gg_pruned"] += pruned
            _GG_REPORT["gg_turns"] += 1
            action = dict(action)
            action["market"] = kept
    except Exception:
        _GG_REPORT["gg_errors"] += 1
    return action


agent.telemetry = _GG_REPORT
agent = globals().pop('agent')
