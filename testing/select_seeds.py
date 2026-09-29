# GROW SEED SELECTOR — EXP 180. Reads the census and, per variant knob,
# selects the seeds where that knob CAN bind (denominators lesson: measure
# activation and effect separately; don't waste games on worlds where the
# variant is provably byte-identical to control).
#
# Selection rules (a seed qualifies if ANY of its 4 cells qualifies):
#   yarn1    max yarn count over capture steps == 1 and control never fired
#   wool120/wool100  yarn >= 2 at some capture, control never fired
#   wheat80  yarn >= 2 at some capture, control never fired
#   win12_19 yarn >= 2 at some capture, control never fired
#   win11_19 yarn >= 2 at some capture (fired seeds INCLUDED: may fire a
#            day earlier and diverge)
#   net500   any recorded forecast decision with 500 <= net < 1000
#            (else identical); plus control-nonfired with decisions logged
# Output: seeds_<variant>.json per variant + selection_summary printed.
import json
from pathlib import Path

GROW = Path(r"C:\Kaggriculture\work\build_a\grow")

seeds = {}
for f in GROW.glob("census_rows_*.jsonl"):
    for line in f.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        s = seeds.setdefault(r["seed"], {"yarn_max": 0, "fired": 0,
                                         "nets": [], "cells": 0,
                                         "committed": 0})
        s["cells"] += 1
        s["fired"] += r["fired"]
        s["committed"] += r.get("committed", 0)
        for cap in r.get("features", {}).values():
            s["yarn_max"] = max(s["yarn_max"], cap.get("yarn", 0))
        for d in r.get("decisions", []):
            s["nets"].append(d.get("margin_forecast"))

sel = {v: [] for v in ("yarn1", "wool120", "wool100", "wheat80",
                       "win12_19", "win11_19", "net500", "shadow")}
for seed, s in sorted(seeds.items()):
    if s["cells"] < 4:
        continue  # census incomplete for this seed
    if s["yarn_max"] == 1 and not s["fired"]:
        sel["yarn1"].append(seed)
    if s["yarn_max"] >= 2 and not s["fired"]:
        for v in ("wool120", "wool100", "wheat80", "win12_19"):
            sel[v].append(seed)
    if s["yarn_max"] >= 2:
        sel["win11_19"].append(seed)
    if any(n is not None and 500 <= n < 1000 for n in s["nets"]):
        sel["net500"].append(seed)
    if s.get("committed"):
        sel["shadow"].append(seed)  # first cohort commits somewhere -> tranche forecast data

total = len([s for s in seeds.values() if s["cells"] >= 4])
fired = len([s for s in seeds.values() if s["cells"] >= 4 and s["fired"]])
print(f"census seeds complete: {total}  control-fired seeds: {fired}")
for v, lst in sel.items():
    (GROW / f"seeds_{v}.json").write_text(json.dumps(lst))
    print(f"{v}: {len(lst)} seeds -> seeds_{v}.json")
