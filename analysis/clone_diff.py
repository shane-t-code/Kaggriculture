# CLONE DIFF  — what do the better copies of OUR family do differently?
# In a live game between us and a same-opening family variant both farms start
# identical, so the two seats' action streams are identical until THEIR private
# edit fires.  We diff the two streams of the SAME replay step by step.
# No games are played, no seeds spent.  Streams one replay at a time
# (download -> diff -> delete) because C: is nearly full.
# PREDECLARED READING: an edit is worth porting only if (a) it shows up in
# >= 3 different opponents' games and (b) the bank gap opens on the same days
# the edit fires.
# Usage: python -X utf8 clone_diff.py <episode_id> [<episode_id> ...]
import gzip
import json
import os
import subprocess
import sys
from collections import Counter

ROOT = r"C:\Kaggriculture"
TMP = ROOT + r"\work\build_a\arena\h2h\tmp_clone"
OUT = ROOT + r"\work\build_a\arena\clone_diff_rows.jsonl"
KAGGLE = ROOT + r"\.venv\Scripts\kaggle.exe"
ME = "Shane"


def fetch(ep):
    os.makedirs(TMP, exist_ok=True)
    for f in os.listdir(TMP):
        os.remove(os.path.join(TMP, f))
    subprocess.run([KAGGLE, "competitions", "replay", str(ep), "-p", TMP],
                   capture_output=True, text=True, timeout=600)
    fs = [os.path.join(TMP, f) for f in os.listdir(TMP)]
    if not fs:
        return None
    p = fs[0]
    op = gzip.open if p.endswith(".gz") else open
    with op(p, "rt", encoding="utf-8") as f:
        rep = json.load(f)
    os.remove(p)
    return rep


def norm_market(m):
    return [tuple(o) for o in (m or []) if o]


def main():
    for ep in sys.argv[1:]:
        rep = fetch(ep)
        if rep is None:
            print(ep, "DOWNLOAD FAILED")
            continue
        names = rep["info"].get("TeamNames", ["?", "?"])
        me = 0 if names[0].startswith(ME) else 1
        op = 1 - me
        steps = rep["steps"]
        shops = steps[-1][0]["observation"]["town"]["unlocked_shops"]
        first_unit = first_mkt = None
        n_unit = n_mkt = 0
        by_day_unit = Counter()
        by_day_mkt = Counter()
        mkt_examples = []
        unit_examples = []
        verb_delta = Counter()
        order_delta = Counter()
        bank_gap = {}
        for t in range(1, len(steps)):
            a = steps[t][me].get("action") or {}
            b = steps[t][op].get("action") or {}
            day = (t - 1) // 24
            ua = [a.get("farmer")] + list(a.get("hands") or [])
            ub = [b.get("farmer")] + list(b.get("hands") or [])
            if ua != ub:
                n_unit += 1
                by_day_unit[day] += 1
                if first_unit is None:
                    first_unit = t - 1
                if len(unit_examples) < 12:
                    unit_examples.append((t - 1, ua, ub))
            for x in ua:
                if x:
                    verb_delta["us:" + str(x[0] if isinstance(x, list) else x)] += 1
            for x in ub:
                if x:
                    verb_delta["them:" + str(x[0] if isinstance(x, list) else x)] += 1
            ma, mb = norm_market(a.get("market")), norm_market(b.get("market"))
            if ma != mb:
                n_mkt += 1
                by_day_mkt[day] += 1
                if first_mkt is None:
                    first_mkt = t - 1
                if len(mkt_examples) < 25:
                    mkt_examples.append((t - 1, ma, mb))
            for o in ma:
                order_delta[("us", o[0], o[1] if len(o) > 1 else "")] += \
                    (o[2] if len(o) > 2 and isinstance(o[2], (int, float)) else 1)
            for o in mb:
                order_delta[("them", o[0], o[1] if len(o) > 1 else "")] += \
                    (o[2] if len(o) > 2 and isinstance(o[2], (int, float)) else 1)
            if (t % 24) == 0:
                f = steps[t][0]["observation"]["farms"]
                bank_gap[t // 24] = round(f[me]["money"] - f[op]["money"])
        fin = steps[-1][0]["observation"]["farms"]
        row = {"ep": ep, "opp": names[op], "our_seat": me,
               "us": fin[me]["money"], "them": fin[op]["money"],
               "shops": shops, "first_unit_diff": first_unit,
               "first_mkt_diff": first_mkt, "n_unit_diff": n_unit,
               "n_mkt_diff": n_mkt,
               "unit_diff_by_day": dict(sorted(by_day_unit.items())),
               "mkt_diff_by_day": dict(sorted(by_day_mkt.items())),
               "bank_gap_by_day": bank_gap}
        with open(OUT, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(f"\n===== ep {ep} vs {names[op]} | us {fin[me]['money']:,.0f} "
              f"them {fin[op]['money']:,.0f} margin "
              f"{fin[me]['money'] - fin[op]['money']:+,.0f}")
        print("shops:", shops)
        print(f"first unit diff step {first_unit} (day "
              f"{None if first_unit is None else first_unit // 24}), "
              f"first market diff step {first_mkt}; unit-diff steps {n_unit}, "
              f"market-diff steps {n_mkt}")
        print("bank gap (us-them) at day starts:", bank_gap)
        print("market-diff steps by day:", dict(sorted(by_day_mkt.items())))
        print("unit-diff steps by day:", dict(sorted(by_day_unit.items())))
        # order totals both sides
        keys = sorted({(k[1], k[2]) for k in order_delta})
        print("ORDER TOTALS (requested qty)  us | them:")
        for k in keys:
            u = order_delta.get(("us",) + k, 0)
            th = order_delta.get(("them",) + k, 0)
            if u != th:
                print(f"   {k[0]:12} {k[1]:12} {u:>8} | {th:>8}  (them-us {th - u:+})")
        vk = sorted({k.split(":", 1)[1] for k in verb_delta})
        print("UNIT VERB TOTALS us | them (only differing):")
        for k in vk:
            u, th = verb_delta.get("us:" + k, 0), verb_delta.get("them:" + k, 0)
            if u != th:
                print(f"   {k:20} {u:>6} | {th:>6}  ({th - u:+})")
        print("first market differences (step: us || them):")
        for t, ma, mb in mkt_examples[:14]:
            print(f"   t{t} d{t // 24}h{t % 24}: {ma}  ||  {mb}")
        print("first unit differences:")
        for t, ua, ub in unit_examples[:6]:
            d = [(i, x, y) for i, (x, y) in enumerate(zip(ua, ub)) if x != y]
            print(f"   t{t} d{t // 24}h{t % 24}: n_us {len(ua)} n_them {len(ub)} "
                  f"diffs {d[:4]}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
