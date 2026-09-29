# GROW SHADOW TRANCHE — EXP 180 stage 3 (Sep 28 ~10:55pm).
#
# Builds variants/shadow.py from review11's exact4.py (the sticky-acceptance
# smart-forecast tranche): the daily worst-case forecast is COMPUTED AND
# LOGGED once per eligible day, but acceptance is DISABLED — the agent's
# behavior must be byte-identical to candidate (the screen asserts margin ==
# census control margin on every cell; any mismatch = bug, not data).
#
# Purpose: the review-11 open question ("early-entry rule with disaster
# veto — thin separation, needs fresh worlds, not tuning") gets its fresh
# worlds: forecast distributions on every census world where the first
# cohort commits, at zero behavioral risk. The rule threshold is then
# chosen from this data and confirmed on a held-out block.
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, r"C:\Kaggriculture")
sys.dont_write_bytecode = True
from run_local import _silence_fds
with _silence_fds():
    from kaggle_environments.agent import get_last_callable

SRC = Path(r"C:\Kaggriculture\work\\review11\exact4.py")
OUT = Path(r"C:\Kaggriculture\work\build_a\grow\variants\shadow.py")

OLD = ("  if state.get('r11_value_day') is None and "
       "_r11_second_value(obs,native):state['r11_value_day']=day\n"
       "  if state.get('r11_value_day') is None:return result")
NEW = ("  if state.get('r11_shadow_day')!=day:\n"
       "   state['r11_shadow_day']=day;_r11_second_value(obs,native)\n"
       "  return result")

ENTRY = """

# GROW SHADOW: exact4 tranche forecast logged daily, acceptance DISABLED
# . Must be behavior-identical to candidate.
_GROW_PARENT_ENTRY=agent
def grow_variant_agent(observation,configuration=None):
    return _GROW_PARENT_ENTRY(observation,configuration)
agent=grow_variant_agent
kaggle_submission_agent=grow_variant_agent
"""

text = SRC.read_text(encoding="utf-8")
assert text.count(OLD) == 1, text.count(OLD)
text = text.replace(OLD, NEW) + ENTRY
OUT.write_text(text, encoding="utf-8")
with _silence_fds():
    fn = get_last_callable(text, path=str(OUT))
assert fn.__name__ == "grow_variant_agent", fn.__name__
print("shadow OK entry=grow_variant_agent sha="
      + hashlib.sha256(OUT.read_bytes()).hexdigest()[:12])
