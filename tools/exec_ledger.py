"""Exact executed ledger for ONE game, both sides, days 0-N.

Attributes every bank delta step-by-step using bank + holdings + seeds +
board diffs simultaneously.  Categories:
  income:  sell:<GOOD> (holdings drop + bank rise, at market price)
  spend:   buy_animal:<KIND> (board placement or shed animal appears),
           buy_seed:<CROP> (seed inventory rise), buy_product:<GOOD>
           (holdings rise + bank drop), land (quadrant unlock), hire (hand
           count rise), residual (unexplained)
Prints per-day compact statement + d0-9 totals per side.
Usage: python tools/exec_ledger.py <replay.json> [--dmax 9]
"""
import json, sys
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
# Engine-verified (kaggriculture.py L20-22; static, quoted directly at L605):
ANIMAL_COST = {"COW": 400, "SHEEP": 500, "GOOSE": 300}
SEED_COST = {"MELON": 80, "STRAWBERRY": 100, "TOMATO": 50, "CARROT": 20, "WHEAT": 10}
GOODS = ["MELON", "STRAWBERRY", "TOMATO", "CARROT", "WHEAT", "MILK", "WOOL",
         "EGG", "FERTILIZER"]
LAND_PRICES = [1000, 2000, 4000]


def holdings(o, seat):
    p = o["private"]
    h = defaultdict(int)
    for g, n in p["shed"].items():
        if g in GOODS:
            h[g] += n
    for inv in p["inventories"]:
        for g, n in inv.items():
            if g in GOODS:
                h[g] += n
    return h


def animals_on_board(o, seat):
    a = defaultdict(int)
    for row in o["farms"][seat]["tiles"]:
        for t in row:
            if isinstance(t, dict) and t.get("animal"):
                a[t["animal"]] += 1
    # shed-held animals too
    for k, n in o["private"]["shed"].items():
        if k in ANIMAL_COST:
            a[k] += n
    return a


def main():
    path = sys.argv[1]
    dmax = 9
    if "--dmax" in sys.argv:
        dmax = int(sys.argv[sys.argv.index("--dmax") + 1])
    blob = json.load(open(path, encoding="utf-8"))
    steps = blob["steps"]
    names = blob["info"]["TeamNames"]
    for seat in (0, 1):
        led = defaultdict(lambda: defaultdict(float))   # day -> cat -> $
        tot = defaultdict(float)
        nquad = 1
        for t in range(min((dmax + 1) * 24, len(steps) - 1)):
            o0 = steps[t][seat]["observation"]
            o1 = steps[t + 1][seat]["observation"]
            day = o0["day"]
            px = o0["market"]["prices"]
            b0 = o0["farms"][seat]["money"]
            b1 = o1["farms"][seat]["money"]
            delta = b1 - b0
            if delta == 0:
                continue
            h0, h1 = holdings(o0, seat), holdings(o1, seat)
            s0, s1 = o0["private"]["seeds"], o1["private"]["seeds"]
            a0, a1 = animals_on_board(o0, seat), animals_on_board(o1, seat)
            q0 = len(o0["farms"][seat]["unlocked_quadrants"])
            q1 = len(o1["farms"][seat]["unlocked_quadrants"])
            n_h0 = len(o0["farms"][seat].get("hands") or [])
            n_h1 = len(o1["farms"][seat].get("hands") or [])
            inc = 0.0
            for g in GOODS:
                drop = h0[g] - h1[g]
                if drop > 0:
                    est = drop * max(1, px.get(g, 1))
                    inc += est
                    led[day][f"sell:{g}"] += est
            spend = 0.0
            for g, c in ANIMAL_COST.items():
                gain = a1.get(g, 0) - a0.get(g, 0)
                if gain > 0:
                    spend += gain * c
                    led[day][f"buy_animal:{g}"] -= gain * c
            for c, cost in SEED_COST.items():
                gain = s1.get(c, 0) - s0.get(c, 0)
                # planted this step also consumed seeds; planting is seed-neutral
                # for cash, so count only NET seed inventory rises as buys plus
                # plants that happened this step (planted_day == day found new)
                if gain > 0:
                    spend += gain * cost
                    led[day][f"buy_seed:{c}"] -= gain * cost
            for g in ("WHEAT", "FERTILIZER"):
                gain = h1[g] - h0[g]
                if gain > 0:
                    est = gain * px.get(g, 0)
                    spend += est
                    led[day][f"buy_product:{g}"] -= est
            if q1 > q0:
                cost = LAND_PRICES[q0 - 1]
                spend += cost
                led[day]["land"] -= cost
            if n_h1 > n_h0:
                led[day]["hire"] -= 0  # wage paid daily; hire itself cheap
            # planting consumes seeds without cash: adjust seed-buy detection —
            # a plant with simultaneous buy hides the buy; residual catches it.
            residual = delta - (inc - spend)
            if abs(residual) > 1:
                led[day]["residual"] += residual
        print(f"===== {names[seat]} (seat {seat}) =====")
        for day in sorted(led):
            items = "  ".join(f"{k}:{v:+,.0f}" for k, v in sorted(led[day].items())
                              if abs(v) >= 1)
            print(f" d{day}: {items}")
        for day in led:
            for k, v in led[day].items():
                tot[k] += v
        print(" TOTALS d0-{}: ".format(dmax)
              + "  ".join(f"{k}:{v:+,.0f}" for k, v in sorted(tot.items())
                          if abs(v) >= 1))
        inc_t = sum(v for k, v in tot.items() if k.startswith("sell:"))
        sp_t = -sum(v for k, v in tot.items() if not k.startswith("sell:")
                    and k != "residual")
        print(f" INCOME {inc_t:+,.0f}  SPEND {-sp_t:+,.0f}  RESIDUAL {tot['residual']:+,.0f}")
        print()


if __name__ == "__main__":
    main()
