# GROW VARIANT FACTORY — EXP 180 (Sep 28 ~10:35pm).
#
# Generates single-knob variants of the CERTIFIED sheep project inside
# candidate.py (the _r9_* scaled1000 layer) by exact-string substitution.
# Safety rails (note): every substitution asserts its exact expected
# occurrence count; every variant gets a NEW uniquely-named entry function
# appended LAST and is load-verified via get_last_callable().__name__.
#
# Knob semantics (control values in parentheses):
#   yarn1    world admission: allow 1 yarn store        (needs >=2)
#   wool120  wool price bar 120                          (150)
#   wool100  wool price bar 100                          (150)
#   wheat80  wheat cost tolerance 80                     (65)
#   win12_19 start window day 12-19                      (12-17)
#   win11_19 start window day 11-19                      (12-17)
#   net500   profit-forecast admission bar 500           (1000)
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
OUT.mkdir(exist_ok=True)

L_GATE = ("    if obs['town']['unlocked_shops'].count('YARN_STORE')<2 "
          "or prices['WOOL']<150 or prices['WHEAT']>65:return False")
L_WIN = "12<=day<=17"
L_NET = "    if net<1000:_R9_REPORT['economic_declines']+=1;return False"

# name -> list of (old, new, expected_count)
VARIANTS = {
    "yarn1": [(L_GATE, L_GATE.replace("count('YARN_STORE')<2",
                                      "count('YARN_STORE')<1"), 1)],
    "wool120": [(L_GATE, L_GATE.replace("prices['WOOL']<150",
                                        "prices['WOOL']<120"), 1)],
    "wool100": [(L_GATE, L_GATE.replace("prices['WOOL']<150",
                                        "prices['WOOL']<100"), 1)],
    "wheat80": [(L_GATE, L_GATE.replace("prices['WHEAT']>65",
                                        "prices['WHEAT']>80"), 1)],
    "win12_19": [(L_WIN, "12<=day<=19", 2)],
    "win11_19": [(L_WIN, "11<=day<=19", 2)],
    "net500": [(L_NET, L_NET.replace("net<1000", "net<500"), 1)],
}

ENTRY = """

# GROW VARIANT {name}: single-knob widening of the certified sheep project
# . Parent entry preserved below.
_GROW_PARENT_ENTRY=r9_scaled_agent
def grow_variant_agent(observation,configuration=None):
    return _GROW_PARENT_ENTRY(observation,configuration)
agent=grow_variant_agent
kaggle_submission_agent=grow_variant_agent
"""

def main():
    base = SRC.read_text(encoding="utf-8")
    manifest = {"src_sha": hashlib.sha256(
        SRC.read_bytes()).hexdigest(), "variants": {}}
    for name, subs in VARIANTS.items():
        text = base
        for old, new, count in subs:
            found = text.count(old)
            assert found == count, (name, found, count, old[:60])
            assert old != new
            text = text.replace(old, new)
        text += ENTRY.format(name=name)
        p = OUT / f"{name}.py"
        p.write_text(text, encoding="utf-8")
        with _silence_fds():
            fn = get_last_callable(text, path=str(p))
        assert fn.__name__ == "grow_variant_agent", (name, fn.__name__)
        sha = hashlib.sha256(p.read_bytes()).hexdigest()
        manifest["variants"][name] = {"sha256": sha, "subs": len(subs)}
        print(f"{name}: OK entry=grow_variant_agent sha={sha[:12]}")
    (OUT / "MANIFEST.json").write_text(json.dumps(manifest, indent=2))
    print("ALL VARIANTS BUILT")

if __name__ == "__main__":
    main()
