# PLAN FOLLOWER v0  — a top team's whole recorded game used as a
# PLAN (not replayed blindly).  Local research tool for Phase 1; it answers
# one question: are the breaks of a moved recording the repairable kind?
# The plan carries, per step: the recorded moves AND the money the real game
# had at that step.  Reflexes:
#   R1 plant trim  — PLANT requests per crop are cut down to the seeds we
#                    hold (engine rule: if requests exceed seeds, ALL fail).
#   R2 cash guard  — top teams spend to their last coins.  If we are D coins
#                    poorer than the real game was, and the real game's
#                    lowest balance in the next HORIZON steps is below D (+
#                    SAFETY), some planned purchase ahead would fail (usually
#                    the next morning's hires).  We give up the cheapest
#                    optional purchases now (seeds first, then bought wheat /
#                    fertilizer) until the gap is covered.
#   R3 hire match  — top teams ask for more hires than they can pay for and
#                    let their empty purse cap it.  We hire exactly as many
#                    hands as the real game ended up with at that step, and
#                    catch up later in the day if a hire was missed.
# LOCAL ONLY — never submitted as is.
import json

from kaggle_environments.envs.kaggriculture.kaggriculture import CROPS

HORIZON = 30
SAFETY = 3


def build_plan(rep, seat):
    steps = rep["steps"]
    table, money, hands = [], [], []
    for t in range(len(steps)):
        hands.append(len(steps[t][0]["observation"]["farms"][seat]["hands"]))
    for t in range(len(steps) - 1):
        a = steps[t + 1][seat].get("action") or {}
        table.append({"farmer": a.get("farmer") or ["PASS"],
                      "hands": [list(h) if isinstance(h, list) else h
                                for h in (a.get("hands") or [])],
                      "market": [list(o) for o in (a.get("market") or []) if o]})
        money.append(steps[t][0]["observation"]["farms"][seat]["money"])
    money.append(steps[-1][0]["observation"]["farms"][seat]["money"])
    return table, money, hands


def follower(rep, seat, r1=True, r2=True, r3=False, log=None):
    return follower_from(build_plan(rep, seat), seat, r1, r2, r3, log)


def splice(plans, switch_steps):
    """plans = [(table, money, hands), ...]; plan i runs until switch_steps[i]."""
    table, money, hands = [], [], []
    start = 0
    for i, (tb, mo, ha) in enumerate(plans):
        end = switch_steps[i] if i < len(switch_steps) else len(tb)
        table += tb[start:end]
        money += mo[start:end]
        hands += ha[start:end]
        start = end
    money.append(plans[-1][1][-1])
    hands.append(plans[-1][2][-1])
    return table, money, hands


def follower_from(plan, seat, r1=True, r2=True, r3=False, log=None):
    table, money, hands = plan
    n = len(table)

    def agent(obs, config=None):
        t = obs["step"]
        if not (0 <= t < n):
            return {"farmer": ["PASS"], "hands": [], "market": []}
        me = obs.get("player", seat)
        farm = obs["farms"][me]
        act = json.loads(json.dumps(table[t]))
        market = act["market"]
        if r2:
            d = money[t] - farm["money"]
            floor = min(money[t + 1:t + 1 + HORIZON] or [money[-1]])
            need = d - floor + SAFETY
            if d > 0 and need > 0:
                # give up optional purchases, cheapest kind first
                for kind in ("BUY_SEED", "BUY_PRODUCT"):
                    for o in market:
                        if need <= 0:
                            break
                        if o[0] != kind or len(o) < 3:
                            continue
                        if kind == "BUY_SEED":
                            unit = CROPS.get(o[1], {}).get("seed", 10)
                        else:
                            unit = float(obs["market"]["prices"].get(o[1], 40))
                        cut = min(int(o[2]), int(-(-need // unit)))
                        if cut > 0:
                            o[2] = int(o[2]) - cut
                            need -= cut * unit
                            if log is not None:
                                log.append((t, kind, o[1], cut))
                act["market"] = [o for o in market
                                 if not (o[0] in ("BUY_SEED", "BUY_PRODUCT")
                                         and len(o) > 2 and int(o[2]) <= 0)]
        if r3:
            want = hands[t + 1] - len(farm["hands"])
            rest = [o for o in act["market"] if o[0] != "HIRE"]
            first_hire = next((i for i, o in enumerate(act["market"])
                               if o[0] == "HIRE"), len(rest))
            first_hire = min(first_hire, len(rest))
            act["market"] = (rest[:first_hire] + [["HIRE"]] * max(0, want)
                             + rest[first_hire:])[:10]
        if r1:
            seeds = dict((obs.get("private") or {}).get("seeds") or {})
            # seeds bought THIS step arrive before units act? keep it safe:
            # only count seeds already held.
            units = [("farmer", None)] + [("hands", i)
                                          for i in range(len(act["hands"]))]
            for who, i in units:
                a = act["farmer"] if who == "farmer" else act["hands"][i]
                if isinstance(a, list) and a and a[0] == "PLANT" and len(a) > 1:
                    c = a[1]
                    if seeds.get(c, 0) > 0:
                        seeds[c] -= 1
                    else:
                        if who == "farmer":
                            act["farmer"] = ["PASS"]
                        else:
                            act["hands"][i] = ["PASS"]
        return act
    return agent
