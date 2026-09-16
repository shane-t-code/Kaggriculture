"""Band-loss ledger: deep per-game decode of every 756-900 loss in a live set.

For each loss vs a 756-900 rated opponent:
  - opponent archetype: d0 melon cohort, animals (cows/sheep/geese), STR tiles d24,
    quadrants owned, hands
  - revenue by good BOTH sides (true market sells: shed+pocket outflow during a
    step where a SELL landed is unreliable -> use bank delta attribution via
    market trades in obs if present, else per-step holdings drop w/ price*qty
    from the market log)  -- here: sum coin inflows from sells via bank increases
    matched to holdings decreases per good (same approach as live_ledger.py).
  - margin trajectory: bank differential at d5/d10/d15/d20/d25/end -> which
    phase lost the game.
  - our labor: work/move/idle %, ops/stop.
Usage: python tools/band_loss_ledger.py replays/live_v83a results/leaderboards/lb_2026-09-16.csv
"""
import json, glob, os, sys, csv
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ME = "Shane Thivaharraja"
WORK = {"HARVEST", "FEED", "CARE", "WATER", "PLANT", "FERTILIZE",
        "COLLECT_FERTILIZER", "BUILD_COOP", "BUILD_PASTURE", "PICKUP",
        "PLACE", "DROP", "DIG"}
GOODS = ["MELON", "STRAWBERRY", "TOMATO", "CARROT", "WHEAT", "MILK", "WOOL",
         "EGG", "FERTILIZER"]


def holdings(obs, side_priv):
    h = defaultdict(int)
    for g, n in side_priv["shed"].items():
        h[g] += n
    for inv in side_priv["inventories"]:
        for g, n in inv.items():
            h[g] += n
    return h


def sell_revenue(steps, seat):
    """Per-good revenue: when holdings of good drop AND bank rises same step,
    attribute min(drop*price, ...) -- we use the market price at that step."""
    rev = defaultdict(float)
    spend = defaultdict(float)  # bank drops matched to holdings RISES (buys)
    consumed = defaultdict(int)  # holdings drops with no bank rise (feed/fert use)
    for t in range(len(steps) - 1):
        o0 = steps[t][seat]["observation"]
        o1 = steps[t + 1][seat]["observation"]
        p0, p1 = o0.get("private"), o1.get("private")
        if not p0 or not p1:
            continue
        b0 = o0["farms"][seat]["money"]
        b1 = o1["farms"][seat]["money"]
        h0, h1 = holdings(o0, p0), holdings(o1, p1)
        prices = o0.get("market", {}).get("prices", {})
        gained = max(0, b1 - b0)
        for g in GOODS:
            drop = h0[g] - h1[g]
            if drop <= 0:
                continue
            px = prices.get(g, 0)
            est = drop * px
            if gained > 0 and px > 1:
                take = min(est, gained)
                rev[g] += take
                gained -= take
            elif px <= 1 and gained > 0:
                take = min(drop * 1, gained)
                rev[g] += take
                gained -= take
            else:
                consumed[g] += drop
        # buys: only WHEAT/FERTILIZER are buyable; holdings rise + bank fell
        lost = max(0, b0 - b1)
        for g in ("WHEAT", "FERTILIZER"):
            gain = h1[g] - h0[g]
            if gain > 0 and lost > 0:
                px = prices.get(g, 0)
                take = min(gain * px, lost)
                spend[g] += take
                lost -= take
    return rev, spend, consumed


def opp_view(steps, me, opp):
    """Public info about opponent from my obs."""
    o5 = steps[min(5 * 24, len(steps) - 1)][me]["observation"]
    farm5 = o5["farms"][opp]["tiles"]
    coh = sum(1 for row in farm5 for t in row if isinstance(t, dict)
              and t.get("crop") == "MELON" and t.get("planted_day", 99) <= 1)
    o24 = steps[min(24 * 24, len(steps) - 1)][me]["observation"]
    farm24 = o24["farms"][opp]["tiles"]
    animals = defaultdict(int)
    strn = 0
    for row in farm24:
        for t in row:
            if not isinstance(t, dict):
                continue
            a = t.get("animal")
            if a:
                animals[a] += 1
            if t.get("crop") == "STRAWBERRY":
                strn += 1
    return coh, dict(animals), strn


def labor(steps, seat):
    work = move = idle = 0
    for t in range(len(steps)):
        st = steps[t][seat]
        act = st.get("action") or {}
        for v in [act.get("farmer")] + list(act.get("hands") or []):
            if v is None:
                continue
            op = v[0] if isinstance(v, list) and v else v
            if isinstance(op, list):
                op = op[0] if op else "PASS"
            if op in WORK:
                work += 1
            elif op == "MOVE":
                move += 1
            else:
                idle += 1
    tot = max(1, work + move + idle)
    return 100 * work / tot, 100 * move / tot, 100 * idle / tot


def main():
    d, lbcsv = sys.argv[1], sys.argv[2]
    lb = {}
    for r in csv.reader(open(lbcsv, encoding="utf-8")):
        try:
            lb[r[2]] = float(r[4])
        except (ValueError, IndexError):
            pass
    losses = []
    for f in sorted(glob.glob(os.path.join(d, "*.json"))):
        blob = json.load(open(f, encoding="utf-8"))
        steps = blob.get("steps") or []
        if len(steps) < 700:
            continue
        names = blob["info"]["TeamNames"]
        if ME not in names:
            continue
        me = names.index(ME)
        opp = 1 - me
        oname = names[opp]
        orating = lb.get(oname)
        margin = (blob["rewards"][me] or 0) - (blob["rewards"][opp] or 0)
        if orating is None or not (756 <= orating <= 900) or margin >= 0:
            continue
        ep = os.path.basename(f).split("-")[1]
        coh, animals, strn = opp_view(steps, me, opp)
        my_rev, my_spend, my_cons = sell_revenue(steps, me)
        # opponent private not visible from my obs; use their seat obs
        op_rev, op_spend, op_cons = sell_revenue(steps, opp)
        # margin trajectory
        traj = []
        for day in (5, 10, 15, 20, 25, 29):
            t = min(day * 24, len(steps) - 1)
            o = steps[t][me]["observation"]
            traj.append((day, o["farms"][me]["money"] - o["farms"][opp]["money"]))
        w, m, i = labor(steps, me)
        ow, om, oi = labor(steps, opp)
        losses.append(dict(ep=ep, opp=oname, rating=orating, margin=margin,
                           coh=coh, animals=animals, strn=strn, traj=traj,
                           my_rev=dict(my_rev), op_rev=dict(op_rev),
                           my_spend=dict(my_spend), op_spend=dict(op_spend),
                           labor=(w, m, i), olabor=(ow, om, oi)))
    losses.sort(key=lambda x: x["margin"])
    print(f"=== BAND 756-900 LOSSES: {len(losses)} games ===\n")
    for L in losses:
        print(f"--- ep{L['ep']} vs {L['opp']} ({L['rating']:.0f})  margin {L['margin']:+,.0f} ---")
        print(f"  opp: d0-mel-cohort={L['coh']}  animals={L['animals']}  STR@d24={L['strn']}")
        print(f"  margin traj (day,diff): " + "  ".join(f"d{d}:{v:+,.0f}" for d, v in L['traj']))
        mr, orv = L["my_rev"], L["op_rev"]
        line = "  rev  " + " ".join(
            f"{g[:4]}:{mr.get(g,0):,.0f}/{orv.get(g,0):,.0f}" for g in GOODS
            if mr.get(g, 0) > 100 or orv.get(g, 0) > 100)
        print(line)
        ms, os_ = L["my_spend"], L["op_spend"]
        print(f"  NET wheat us {mr.get('WHEAT',0)-ms.get('WHEAT',0):+,.0f} / them "
              f"{orv.get('WHEAT',0)-os_.get('WHEAT',0):+,.0f}   NET fert us "
              f"{mr.get('FERTILIZER',0)-ms.get('FERTILIZER',0):+,.0f} / them "
              f"{orv.get('FERTILIZER',0)-os_.get('FERTILIZER',0):+,.0f}")
        w, m, i = L["labor"]; ow, om, oi = L["olabor"]
        print(f"  labor us w/m/i {w:.0f}/{m:.0f}/{i:.0f}%  them {ow:.0f}/{om:.0f}/{oi:.0f}%")
        print()
    # aggregate: which good loses the band, which phase
    print("=== AGGREGATE over losses ===")
    agg_my, agg_op = defaultdict(float), defaultdict(float)
    for L in losses:
        for g in GOODS:
            agg_my[g] += L["my_rev"].get(g, 0) - L["my_spend"].get(g, 0)
            agg_op[g] += L["op_rev"].get(g, 0) - L["op_spend"].get(g, 0)
    n = max(1, len(losses))
    print(f"(NET of buys) {'good':12s} {'us/game':>10s} {'them/game':>10s} {'diff':>10s}")
    for g in GOODS:
        du, dt = agg_my[g] / n, agg_op[g] / n
        print(f"{g:12s} {du:10,.0f} {dt:10,.0f} {dt-du:+10,.0f}")
    # phase attribution
    phase = defaultdict(float)
    for L in losses:
        prev = 0
        for dday, v in L["traj"]:
            phase[dday] += (v - prev) / n
            prev = v
    print("\nmargin lost per phase (avg delta of bank-diff):")
    for dday in (5, 10, 15, 20, 25, 29):
        print(f"  ..d{dday}: {phase[dday]:+,.0f}")


if __name__ == "__main__":
    main()
