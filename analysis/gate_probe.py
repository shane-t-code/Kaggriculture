# GATE PROBE  — in live games where a same-opening copy bought the
# third plot + tomato and we did not (or the reverse), print the public state
# both sides saw on day 18 so we can see WHICH condition of our own tomato
# project gate (dtrw.py ~1269-1285: money >= 12000, tomato price floor,
# >= 3 pizza/farmers-market shops unlocked, SE still locked) held us back.
# No games played, no seeds spent. download -> read -> delete.
# Usage: python -X utf8 gate_probe.py <episode_id> [...]
import json
import sys

sys.path.insert(0, r"C:\Kaggriculture\work\build_a\arena")
from clone_diff import fetch, ME  # noqa: E402

H2H = r"C:\Kaggriculture\work\build_a\arena\h2h\rows.jsonl"


def main():
    labels = {}
    for l in open(H2H, encoding="utf-8"):
        r = json.loads(l)
        labels[str(r["episode"])] = r.get("label")
    for ep in sys.argv[1:]:
        rep = fetch(ep)
        if rep is None:
            print(ep, "DOWNLOAD FAILED")
            continue
        names = rep["info"].get("TeamNames", ["?", "?"])
        me = 0 if names[0].startswith(ME) else 1
        op = 1 - me
        steps = rep["steps"]
        print(f"\n===== ep {ep} our agent={labels.get(str(ep))} vs {names[op]}")
        land = {me: [], op: []}
        tom = {me: [], op: []}
        for t in range(1, len(steps)):
            for s in (me, op):
                a = steps[t][s].get("action") or {}
                for o in a.get("market") or []:
                    if o and o[0] == "BUY_LAND":
                        land[s].append(t - 1)
                    if o and o[0] == "BUY_SEED" and o[1] == "TOMATO":
                        tom[s].append((t - 1, o[2]))
        print("  land buy steps  us", land[me], " them", land[op])
        print("  tomato seed buys us", tom[me], " them", tom[op])
        for t in (408, 432, 433, 434, 435, 436):
            o = steps[t][0]["observation"]
            f = o["farms"]
            shops = o["town"]["unlocked_shops"]
            pf = sum(s in ("PIZZA_SHOP", "FARMERS_MARKET") for s in shops)
            print(f"  obs step {o.get('step', t)}: money us {f[me]['money']:,.0f} "
                  f"them {f[op]['money']:,.0f} | tomato price "
                  f"{o['market']['prices']['TOMATO']:.1f} | shops {len(shops)} "
                  f"pizza+fm {pf} | hands us {len(f[me]['hands'])} "
                  f"them {len(f[op]['hands'])}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
