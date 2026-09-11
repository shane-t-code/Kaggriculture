"""realization.py — realized-vs-quoted price instrument .

WHY: our floor-sell count (median 5/ep) is the visible tip of a suspected
"realization gap": selling in bunches walks the price down unit by unit inside
one turn (engine _process_market: per-unit lockstep, each unit quoted at
current inventory). This tool reconstructs every market fill in a replay by
replaying the ENGINE'S OWN pairing loop (queue-position pairing, same
pre-commit snapshot, floor sales add no inventory) and reports, per seat:

    quoted$   = units_sold x price at the turn's OPENING inventory
    realized$ = sum of actual per-unit prices
    ratio     = quoted / realized   (1.00 = perfect monetization; big = dumping)

VALIDATION: reconstructed market inventory after each step must equal the
observed inventory at the next step (town consumption included). Steps that
don't match are excluded and counted; the match rate is printed. This is the
Lê-Quang-Cảnh self-check applied to fills.

Usage:
    python tools/realization.py <replay_dir> <label> [me_name]
Writes results/decodes/realization_<label>.jsonl and prints the aggregate.
"""
import json, os, sys, ast
from collections import defaultdict

sys.path.insert(0, r"C:\Kaggriculture\.venv\Lib\site-packages")
from kaggle_environments.envs.kaggriculture.kaggriculture import (
    MARKET_PARAMS, PRODUCTS, CROPS, ANIMALS, SHOPS, market_price,
    _resolve_market_params,
)

TOWN_CENTER_PRODUCTS = [p for p in PRODUCTS if p != "FERTILIZER"]
ME_DEFAULT = "Shane Thivaharraja"


def phase_of(day):
    return ("d0-4" if day < 5 else "d5-9" if day < 10 else "d10-14" if day < 15
            else "d15-21" if day < 22 else "d22-29")


def simulate_step(inv, queues, params, max_orders):
    """Replay _process_market on `inv` (mutated). Returns per-seat fills:
    {seat: {item: [per-unit prices]}} for SELLs and BUY_PRODUCT inventory moves.
    Money/shed constraints are NOT simulated (validated via inventory match)."""
    fills = [defaultdict(list), defaultdict(list)]
    qs = [list(q[:max_orders]) for q in queues]
    # parse
    parsed = []
    for q in qs:
        pq = []
        for o in q:
            if not isinstance(o, list) or not o:
                pq.append(None); continue
            op = o[0]
            if op in ("HIRE", "BUY_LAND"):
                pq.append({"type": op})
            elif op in ("BUY_SEED", "BUY_PRODUCT", "BUY_ANIMAL", "SELL") and len(o) >= 3:
                try:
                    n = int(o[2])
                except (TypeError, ValueError):
                    pq.append(None); continue
                pq.append({"type": op, "item": o[1], "remaining": n} if n > 0 else None)
            else:
                pq.append(None)
        parsed.append(pq)
    max_len = max(len(p) for p in parsed) if parsed else 0
    for i in range(max_len):
        ostates = [parsed[s][i] if i < len(parsed[s]) else None for s in (0, 1)]
        for s in (0, 1):
            if ostates[s] and ostates[s]["type"] in ("HIRE", "BUY_LAND"):
                ostates[s] = None  # atomic, no inventory effect
        guard = 0
        while True:
            guard += 1
            if guard > 100_000:
                break
            quoted = [None, None]
            for s in (0, 1):
                o = ostates[s]
                if o is None or o.get("remaining", 0) <= 0:
                    continue
                op, item = o["type"], o.get("item")
                if op == "SELL" and item in PRODUCTS:
                    quoted[s] = ("SELL", item, market_price(item, inv[item], params), o)
                elif op == "BUY_PRODUCT" and item in ("WHEAT", "FERTILIZER"):
                    quoted[s] = ("BUY_PRODUCT", item, market_price(item, inv[item] - 1, params), o)
                elif op == "BUY_SEED" and item in CROPS:
                    quoted[s] = ("BUY_SEED", item, CROPS[item]["seed"], o)
                elif op == "BUY_ANIMAL" and item in ANIMALS:
                    quoted[s] = ("BUY_ANIMAL", item, ANIMALS[item]["cost"], o)
                else:
                    ostates[s] = None
            if all(q is None for q in quoted):
                break
            committed = False
            for s in (0, 1):
                q = quoted[s]
                if q is None:
                    continue
                op, item, price, o = q
                if op == "SELL":
                    if price > 1:
                        inv[item] += 1
                    fills[s][("SELL", item)].append(price)
                elif op == "BUY_PRODUCT":
                    inv[item] -= 1
                    fills[s][("BUY", item)].append(price)
                # seeds/animals: no inventory effect
                o["remaining"] -= 1
                committed = True
            if not committed:
                break
    return fills


def town_consume(inv, town, step, shop_interval, center_interval):
    if step % shop_interval == 0:
        for shop_name in town.get("unlocked_shops", []):
            prods = SHOPS[shop_name]
            mult = 2 if len(prods) == 1 else 1
            for item in prods:
                inv[item] -= mult
    if step % center_interval == 0:
        for item in TOWN_CENTER_PRODUCTS:
            inv[item] -= 1


def decode_episode(path, me_name):
    rep = json.load(open(path, encoding="utf-8"))
    teams = (rep.get("info") or {}).get("TeamNames")
    if isinstance(teams, str):
        teams = ast.literal_eval(teams)
    if teams and me_name in teams:
        my = teams.index(me_name)
    else:
        my = 0  # local replay: seat 0 = agent A ("ME"), seat 1 = opponent
        teams = ["seat0(A)", "seat1(B)"]
    conf = rep.get("configuration", {})
    params = _resolve_market_params(conf.get("marketParams"))
    max_orders = int(conf.get("maxMarketOrdersPerTurn", 10))
    shop_iv = max(1, int(conf.get("townShopSellInterval", 4)))
    center_iv = max(1, int(conf.get("townCenterSellInterval", 24)))
    steps = rep["steps"]

    # per seat-role accumulators
    acc = {w: defaultdict(lambda: {"units": 0, "quoted": 0.0, "realized": 0.0, "floor": 0, "buy_units": 0, "buy_cost": 0.0})
           for w in ("ME", "OPP")}
    ok = bad = 0
    for si in range(len(steps) - 1):
        obs0 = steps[si][0]["observation"]
        step = obs0.get("step", si)
        day = step // 24
        ph = phase_of(day)
        inv0 = dict(obs0["market"]["inventory"])
        inv = dict(inv0)
        town = obs0.get("town", {}) or {}
        # CONVENTION (validated 99.9% vs 65.6%): the actions that transform
        # state si -> si+1 are stored at steps[si+1] ("action decided at turn t
        # is stored at steps[t+1]" -- the x-ray caveat, confirmed empirically).
        queues = []
        for seat in (0, 1):
            a = steps[si + 1][seat].get("action") or {}
            m = a.get("market", []) if isinstance(a, dict) else []
            queues.append(m if isinstance(m, list) else [])
        fills = simulate_step(inv, queues, params, max_orders)
        town_consume(inv, town, step, shop_iv, center_iv)
        inv_next = steps[si + 1][0]["observation"]["market"]["inventory"]
        if all(inv.get(k, 0) == inv_next.get(k, 0) for k in inv_next):
            ok += 1
        else:
            bad += 1
            continue  # exclude unvalidated steps from the stats
        for seat in (0, 1):
            who = "ME" if seat == my else "OPP"
            for (kind, item), prices in fills[seat].items():
                a = acc[who][(ph, item)]
                if kind == "SELL":
                    open_quote = market_price(item, inv0[item], params)
                    a["units"] += len(prices)
                    a["quoted"] += open_quote * len(prices)
                    a["realized"] += sum(prices)
                    a["floor"] += sum(1 for p in prices if p <= 1)
                elif kind == "BUY":
                    a["buy_units"] += len(prices)
                    a["buy_cost"] += sum(prices)
    margin = None
    try:
        last = steps[-1]
        banks = [last[s]["observation"] for s in (0,)]
        farms = last[0]["observation"]["farms"]
        margin = farms[my]["money"] - farms[1 - my]["money"]
    except Exception:
        pass
    return {
        "ep": os.path.basename(path),
        "opp": teams[1 - my] if len(teams) > 1 else "?",
        "match_ok": ok, "match_bad": bad,
        "margin": margin,
        "acc": {w: {f"{ph}|{item}": v for (ph, item), v in acc[w].items()} for w in acc},
    }


def main():
    d = sys.argv[1]
    label = sys.argv[2] if len(sys.argv) > 2 else "run"
    me = sys.argv[3] if len(sys.argv) > 3 else ME_DEFAULT
    files = sorted(f for f in os.listdir(d) if f.endswith(".json"))
    out_path = os.path.join("results", "decodes", f"realization_{label}.jsonl")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    tot = {w: defaultdict(lambda: {"units": 0, "quoted": 0.0, "realized": 0.0, "floor": 0, "buy_units": 0, "buy_cost": 0.0})
           for w in ("ME", "OPP")}
    # split ME by game result too
    tot_res = {r: defaultdict(lambda: {"units": 0, "quoted": 0.0, "realized": 0.0, "floor": 0, "buy_units": 0, "buy_cost": 0.0})
               for r in ("ME-W", "ME-L", "OPP-inW", "OPP-inL")}
    ok = bad = 0
    n = 0
    with open(out_path, "w", encoding="utf-8") as fh:
        for f in files:
            try:
                rec = decode_episode(os.path.join(d, f), me)
            except Exception as e:
                print(f"  !! {f}: {e}")
                continue
            n += 1
            ok += rec["match_ok"]; bad += rec["match_bad"]
            fh.write(json.dumps(rec) + "\n")
            res = "ME-W" if (rec["margin"] or 0) > 0 else "ME-L"
            for w in ("ME", "OPP"):
                for key, v in rec["acc"][w].items():
                    ph, item = key.split("|")
                    t = tot[w][(ph, item)]
                    for k2 in v:
                        t[k2] += v[k2]
                    if w == "ME":
                        t2 = tot_res[res][(ph, item)]
                        for k2 in v:
                            t2[k2] += v[k2]
                    elif w == "OPP":
                        t3 = tot_res["OPP-inL" if res == "ME-L" else "OPP-inW"][(ph, item)]
                        for k2 in v:
                            t3[k2] += v[k2]

    print(f"\n===== realization {label}: {n} games, step validation "
          f"{ok}/{ok+bad} ({ok/max(1,ok+bad):.1%}) =====")
    print(f"(ratio = quoted$/realized$; 1.00 = perfect monetization, higher = price walked down)\n")

    def show(t, title, ngames):
        print(f"-- {title} (per-game means over {ngames}) --")
        q = sum(v["quoted"] for v in t.values()); r = sum(v["realized"] for v in t.values())
        u = sum(v["units"] for v in t.values()); fl = sum(v["floor"] for v in t.values())
        bc = sum(v["buy_cost"] for v in t.values())
        g = max(1, ngames)
        print(f"  TOTAL: sell {u/g:,.0f}u ${r/g:,.0f}  buys ${bc/g:,.0f}  NET ${(r-bc)/g:,.0f}  "
              f"ratio {q/max(1,r):.2f}  floor {fl/g:.0f}u ({fl/max(1,u):.1%})")
        for ph in ("d0-4", "d5-9", "d10-14", "d15-21", "d22-29"):
            q2 = sum(v["quoted"] for (p, _), v in t.items() if p == ph)
            r2 = sum(v["realized"] for (p, _), v in t.items() if p == ph)
            u2 = sum(v["units"] for (p, _), v in t.items() if p == ph)
            b2 = sum(v["buy_cost"] for (p, _), v in t.items() if p == ph)
            fl2 = sum(v["floor"] for (p, _), v in t.items() if p == ph)
            if u2 or b2:
                print(f"  {ph:>7}: sell {u2/g:>6,.0f}u ${r2/g:>8,.0f}  buys ${b2/g:>8,.0f}  "
                      f"NET ${(r2-b2)/g:>8,.0f}  ratio {q2/max(1,r2):.2f}  floor {fl2/g:>4,.0f}u")
        items = sorted({i for (_, i) in t})
        for it in items:
            q2 = sum(v["quoted"] for (_, i2), v in t.items() if i2 == it)
            r2 = sum(v["realized"] for (_, i2), v in t.items() if i2 == it)
            u2 = sum(v["units"] for (_, i2), v in t.items() if i2 == it)
            b2 = sum(v["buy_cost"] for (_, i2), v in t.items() if i2 == it)
            bu2 = sum(v["buy_units"] for (_, i2), v in t.items() if i2 == it)
            fl2 = sum(v["floor"] for (_, i2), v in t.items() if i2 == it)
            print(f"    {it:>11}: sell {u2/g:>5,.0f}u ${r2/g:>7,.0f}  buy {bu2/g:>5,.0f}u ${b2/g:>7,.0f}  "
                  f"NET ${(r2-b2)/g:>7,.0f}  ratio {q2/max(1,r2):>4.2f}  floor {fl2/g:>3,.0f}u")
        print()

    n_w = sum(1 for _ in open(out_path, encoding="utf-8")
              if json.loads(_).get("margin", 0) and json.loads(_)["margin"] > 0)
    n_l = n - n_w
    show(tot["ME"], "ME (all games)", n)
    show(tot["OPP"], "OPP (all games)", n)
    show(tot_res["ME-W"], "ME in WINS", n_w)
    show(tot_res["OPP-inW"], "OPP in my WINS", n_w)
    show(tot_res["ME-L"], "ME in LOSSES", n_l)
    show(tot_res["OPP-inL"], "OPP in my LOSSES", n_l)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
