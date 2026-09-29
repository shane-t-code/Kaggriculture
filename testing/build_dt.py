# BUILD DT — deep terminal search .
# Candidate's step-712 INITIAL plan runs plan_terminal(128,1,8); its own
# certified deviation-replan already runs (256,2,12) (candidate.py:10169).
# DT raises the initial plan to the same caps. The acceptance rules are
# untouched (physical-dominance certificates), so DT can only accept MORE
# certified improvements; risks are step-712 planning time (<900ms gate)
# and nothing else. Clone-war rationale: mirror games are deterministic —
# each tie flipped at step 712-718 is +0.5 score vs the family, which is
# a large fraction of the finals field.
# PREDECLARED gates: mirror duels dt-vs-candidate both seats — KEEP iff
# (wins - losses) > 0 with ZERO new losses vs candidate; field screen
# (screen.py, ca22+majkel strata) standard gates; max planning callback
# < 900ms on every game.
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, r"C:\Kaggriculture")
sys.dont_write_bytecode = True
from run_local import _silence_fds
with _silence_fds():
    from kaggle_environments.agent import get_last_callable

SRC = Path(r"C:\Kaggriculture\work\\review10\candidate.py")
OUT = Path(r"C:\Kaggriculture\work\build_a\grow\variants\dt.py")

OLD = ("plan=_PLANNER_NS['plan_terminal'](observation,configuration,baseline,"
       "max_simulations=128,passes=1,proposals_per_actor=8)")
NEW = ("plan=_PLANNER_NS['plan_terminal'](observation,configuration,baseline,"
       "max_simulations=256,passes=2,proposals_per_actor=12)")

ENTRY = """

# GROW VARIANT dt: initial step-712 plan at (256,2,12) instead of (128,1,8).
_GROW_PARENT_ENTRY=r9_scaled_agent
def grow_variant_agent(observation,configuration=None):
    return _GROW_PARENT_ENTRY(observation,configuration)
agent=grow_variant_agent
kaggle_submission_agent=grow_variant_agent
"""

text = SRC.read_text(encoding="utf-8")
n = text.count(OLD)
assert n == 1, n
out_text = text.replace(OLD, NEW) + ENTRY
OUT.write_text(out_text, encoding="utf-8")
with _silence_fds():
    fn = get_last_callable(out_text, path=str(OUT))
assert fn.__name__ == "grow_variant_agent", fn.__name__
print("dt OK sha=" + hashlib.sha256(OUT.read_bytes()).hexdigest()[:12])
