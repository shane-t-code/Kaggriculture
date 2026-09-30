# MGX + TAKEOVER  — follow a Mother-Goose plan until step T, then a
# live controller (review-10 takeover body _ta_action: plans every unit and
# order from the observed farm each step) runs the farm for the rest of the
# game.  Probe: does a live caretaker on a top-team-built farm beat
# following a plan for the wrong town?
import os, sys
from pathlib import Path
R = Path(r"C:\Kaggriculture")
sys.path.insert(0, str(R / "work" / "build_a" / "mgx"))
sys.path.insert(0, str(R / "work" / "" / "review10"))
import mgx
T = int(os.environ.get("MGX_TK_STEP", "288"))
_tk = None
_ST = {}

def agent(obs, config=None):
    global _tk
    step = obs.get("step")
    if step is None:
        step = obs["day"] * 24 + obs["hour"]
    if step == 0:
        _ST.clear()
    if step < T:
        return mgx.agent(obs, config)
    if _tk is None:
        from run_local import _silence_fds
        with _silence_fds():
            import takeover_ws6_forced as _m
        _tk = _m
    st = _ST.setdefault("st", {"step": step, "active": True, "off": False})
    try:
        return _tk._ta_action(obs, st)
    except Exception as e:
        _ST.setdefault("errors", []).append((step, repr(e)))
        return {"farmer": ["PASS"], "hands": [], "market": []}
