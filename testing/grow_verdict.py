# GROW VERDICT — experiment. Evaluates every screen_rows_*.jsonl against the
# PREDECLARED gates (screen.py header, set before any stage-2 game ran):
#   KEEP  iff mean paired > 0 AND zero losing flips AND majkel stratum
#         mean >= -250 with stratum score_delta >= 0 AND paired == 0 on
#         every cell where neither arm fired beyond control.
#   KILL  iff mean paired < 0.
#   Shadow variant instead asserts margin identity (paired == 0 everywhere)
#   and reports its harvested forecast distribution.
import json
from collections import defaultdict
from pathlib import Path

GROW = Path(r"C:\Kaggriculture\work\build_a\grow")

for f in sorted(GROW.glob("screen_rows_*.jsonl")):
    name = f.stem.replace("screen_rows_", "")
    rows = [json.loads(l) for l in
            f.read_text(encoding="utf-8").splitlines() if l.strip()]
    if not rows:
        continue
    errs = [r for r in rows if any(s != "DONE" for s in r["statuses"])
            or r["paired"] is None]
    ok = [r for r in rows if r not in errs]
    if name == "shadow":
        bad = [r for r in ok if r["paired"] != 0]
        nets = []
        for r in ok:
            for d in r.get("r11", {}).get("decisions") or []:
                nets.append((r["seed"], r["opp"], r["pid"],
                             d["step"] // 24, d["net"]))
        print(f"\n== shadow: cells {len(ok)} errors {len(errs)} "
              f"NON-IDENTICAL cells {len(bad)} "
              f"forecast logs {len(nets)}")
        for b in bad[:10]:
            print(f"   MISMATCH seed {b['seed']} {b['opp']} s{b['pid']} "
                  f"paired {b['paired']:+,.0f}")
        continue
    n = len(ok)
    mean = sum(r["paired"] for r in ok) / n if n else 0.0
    flips_down = [r for r in ok if r["score_delta"] < 0]
    flips_up = sum(1 for r in ok if r["score_delta"] > 0)
    strata = defaultdict(list)
    for r in ok:
        strata[r["opp"]].append(r)
    mj = strata.get("majkel", [])
    mj_mean = sum(r["paired"] for r in mj) / len(mj) if mj else 0.0
    mj_sc = sum(r["score_delta"] for r in mj)
    inert = [r for r in ok if r["fired"] == r["ctrl_fired"] == 0]
    inert_bad = [r for r in inert if r["paired"] != 0]
    newly = [r for r in ok if r["fired"] and not r["ctrl_fired"]]
    keep = (n > 0 and not errs and mean > 0 and not flips_down
            and mj_mean >= -250 and mj_sc >= 0 and not inert_bad)
    kill = n > 0 and mean < 0
    verdict = "KEEP" if keep else "KILL" if kill else "ITERATE"
    print(f"\n== {name}: {verdict}  cells {n} errors {len(errs)}")
    print(f"   MEAN PAIRED {mean:+.1f}  flips up {flips_up} "
          f"DOWN {len(flips_down)}  newly-fired cells {len(newly)}")
    print(f"   majkel mean {mj_mean:+.1f} scoreD {mj_sc:+d}  "
          f"inert cells {len(inert)} nonzero {len(inert_bad)}")
    for o, v in sorted(strata.items()):
        m = sum(r['paired'] for r in v) / len(v)
        print(f"   {o:8} mean {m:+.1f} scoreD "
              f"{sum(r['score_delta'] for r in v):+d} n={len(v)}")
    for r in sorted(newly, key=lambda r: r["paired"])[:6]:
        print(f"   fired seed {r['seed']} {r['opp']} s{r['pid']} "
              f"paired {r['paired']:+,.0f} scoreD {r['score_delta']:+d}")
    for r in flips_down[:6]:
        print(f"   LOSING FLIP seed {r['seed']} {r['opp']} s{r['pid']} "
              f"paired {r['paired']:+,.0f}")
