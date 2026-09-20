# ---------------------------------------------------------------------------
#  VARIANCE layer (Shane Thivaharraja fork, Exp 123): bank-differential
# risk.  Rating counts WINS only (Pr[win]=Phi(mu/sigma), destbreso), and both
# banks are public every turn — so when we are BEHIND late, extra variance is
# free win-probability, and when ahead it is poison.  The 2945 base's games
# vs top routers land within +-2.5k on 30/39 seeds = coin-flip distance.
# Mechanism (market-orders ONLY — no hires, no land, no tiles: the fib wage
# law and the shop-RNG re-roll never touch this layer):
#   BEHIND (bank gap <= -1500) from day 20: defer the route's SELLs of
#   spike-capable goods (hold in shed), remembering the price at first hold.
#   RELEASE (our own appended SELL) on: price spike >= 130% of ref | we take
#   the lead (de-risk, lock it) | step 684 = d28 h12 (ahead of the final-day
#   dump crush and the terminal planner's 712-718 window) | shed pressure
#   (never let held goods burn in the midnight overflow; also never defer at
#   hour >= 21 = SHEDROOM's hours, or when shed > 80).
#   v99a (d24 / -2000 / 1.15 / 696) gated +16 +- 17, 0 flips: safe but
#   toothless — too little volume, releases inside the d29 crush.
#   AHEAD or close: byte-identical passthrough — the layer cannot touch a
#   game we are winning.
# Own implementation, Apache-2.0 like the chassis it wraps.
# ---------------------------------------------------------------------------
_VL_FROM_DAY = 20
_VL_BEHIND = -1500            # bank gap at/below this = "behind, gamble"
_VL_SPIKE = 1.30              # release on px >= ref * this
_VL_SHED_MAX = 80             # never defer when shed holds more than this
_VL_LAST_STEP = 684           # d28 h12: release before the final-day dump crush
_VL_HOLD = {"STRAWBERRY", "TOMATO", "CARROT", "MELON", "EGG", "MILK", "WOOL"}
# (FERTILIZER: price only decays — holding is pure loss.  WHEAT: log book,
#  no spike upside.  Both always flow through untouched.)
_VL_STATE = {}
_VL_REPORT = {"vl_deferred": 0, "vl_rel_spike": 0, "vl_rel_ahead": 0,
              "vl_rel_time": 0, "vl_rel_shed": 0, "vl_turns_active": 0,
              "vl_errors": 0}

_VL_PARENT = agent
del agent


def agent(observation, configuration=None):
    action = _VL_PARENT(observation, configuration)
    try:
        step = int(observation["step"])
        seat = int(observation["player"])
        st = _VL_STATE.get(seat)
        if step == 0 or st is None or step <= st["step"]:
            st = _VL_STATE[seat] = {"step": -1, "ref": {}, "held": {}}
            if step == 0:
                for k in _VL_REPORT:
                    _VL_REPORT[k] = 0
        st["step"] = step
        if not isinstance(action, dict):
            return action
        day, hour = step // 24, step % 24
        if day < _VL_FROM_DAY or step >= 712:
            return action
        farm = observation["farms"][seat]
        ell = farm.get("money", 0) - observation["farms"][1 - seat].get("money", 0)
        prices = observation["market"]["prices"]
        shed = observation["private"]["shed"]
        shed_total = sum(int(v) for v in shed.values())
        market = [list(o) for o in (action.get("market") or [])]
        held = st["held"]
        changed = False

        # ---- releases first: sell held goods when a release condition hits
        release_all = (ell >= 0) or (step >= _VL_LAST_STEP)
        for p in list(held):
            if held[p] <= 0:
                held.pop(p)
                continue
            px = int(prices.get(p, 0))
            ref = st["ref"].get(p, px)
            rel = None
            if release_all:
                rel = "vl_rel_ahead" if ell >= 0 else "vl_rel_time"
            elif px >= ref * _VL_SPIKE:
                rel = "vl_rel_spike"
            elif shed_total >= _VL_SHED_MAX + 10:
                rel = "vl_rel_shed"
            if rel and len(market) < 10:
                q = min(held[p], int(shed.get(p, 0)))
                if q > 0:
                    market.append(["SELL", p, q])
                    _VL_REPORT[rel] += q
                    changed = True
                held.pop(p, None)

        # ---- deferral: only while clearly behind, with shed headroom,
        # and never in SHEDROOM's overflow-rescue hours
        if (ell <= _VL_BEHIND and step < _VL_LAST_STEP and hour < 21
                and shed_total <= _VL_SHED_MAX):
            active = False
            for o in market:
                if (len(o) >= 3 and o[0] == "SELL" and o[1] in _VL_HOLD
                        and int(o[2]) > 0):
                    p = o[1]
                    st["ref"].setdefault(p, int(prices.get(p, 0)))
                    # requested qty can exceed real stock (liquidation spam
                    # like SELL x999) — account at most the shed's truth
                    q = min(int(o[2]), int(shed.get(p, 0)))
                    if q > held.get(p, 0):
                        _VL_REPORT["vl_deferred"] += q - held.get(p, 0)
                        held[p] = q
                    o[2] = 0
                    changed = True
                    active = True
            if active:
                _VL_REPORT["vl_turns_active"] += 1
            market = [o for o in market
                      if not (o[0] == "SELL" and len(o) >= 3 and int(o[2]) <= 0)]

        if changed:
            action = dict(action)
            action["market"] = market
    except Exception:
        _VL_REPORT["vl_errors"] += 1
    return action


agent.telemetry = _VL_REPORT
agent = globals().pop('agent')
