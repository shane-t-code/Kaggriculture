# BUILD DIAL SWEEP — _CA_MARGIN beyond the public frontier (EXP 182b,
# Sep 29 ~12:20am, queued behind the knob screens).
#
# The carrot dial is the proven WITHIN-PLAN reallocation lever (zero new
# land, zero new hires): more negative = more wheat->carrot planting swaps
# inside the native labor budget. Public frontier: -15 (s1009r) -> -22
# (ca22/candidate, +certified live). Nobody public has gone past -22.
# Variants: ca30 (-30), ca40 (-40). Control = candidate (-22).
# PREDECLARED gates: standard grower gates (screen.py header): KEEP iff
# mean paired > 0, zero losing flips, majkel stratum >= -250 scoreD >= 0.
# Panel: full census seed list (the dial can bite in any near-threshold
# price world); dial-bite worlds are not enumerable a priori.
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, r"C:\Kaggriculture")
sys.dont_write_bytecode = True
from run_local import _silence_fds
with _silence_fds():
    from kaggle_environments.agent import get_last_callable

SRC = Path(r"C:\Kaggriculture\work\\review10\candidate.py")
OUT = Path(r"C:\Kaggriculture\work\build_a\grow\variants")

ENTRY = """

# GROW VARIANT {name}: _CA_MARGIN {val} (dial sweep beyond public -22).
_GROW_PARENT_ENTRY=r9_scaled_agent
def grow_variant_agent(observation,configuration=None):
    return _GROW_PARENT_ENTRY(observation,configuration)
agent=grow_variant_agent
kaggle_submission_agent=grow_variant_agent
"""

text = SRC.read_text(encoding="utf-8")
OLD = "_CA_MARGIN = -22.0"
assert text.count(OLD) == 1
for name, val in (("ca30", "-30.0"), ("ca40", "-40.0")):
    out_text = text.replace(OLD, f"_CA_MARGIN = {val}") + ENTRY.format(
        name=name, val=val)
    p = OUT / f"{name}.py"
    p.write_text(out_text, encoding="utf-8")
    with _silence_fds():
        fn = get_last_callable(out_text, path=str(p))
    assert fn.__name__ == "grow_variant_agent", (name, fn.__name__)
    print(f"{name}: OK sha="
          + hashlib.sha256(p.read_bytes()).hexdigest()[:12])

# panel = every census seed (dial-bite worlds not enumerable a priori)
import glob
seeds = sorted({json.loads(l)["seed"]
                for f in glob.glob(str(OUT.parent / "census_rows_*.jsonl"))
                for l in open(f, encoding="utf-8") if l.strip()})
(OUT.parent / "seeds_dials.json").write_text(json.dumps(seeds))
print(f"dial panel: {len(seeds)} seeds -> seeds_dials.json")
