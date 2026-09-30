# MGX DEBUG  — one game, our money vs the followed plan's money by day.
import json, sys
from pathlib import Path
R = Path(r"C:\Kaggriculture"); sys.path.insert(0, str(R)); sys.path.insert(0, str(R / "work" / "build_a" / "mgx")); sys.dont_write_bytecode = True
from run_local import _silence_fds
with _silence_fds():
    from kaggle_environments import make
import mgx
seed, seat = int(sys.argv[1]), int(sys.argv[2])
opp = sys.argv[3] if len(sys.argv) > 3 else str(R / "work" / "build_a" / "grow" / "variants" / "dtrw.py")
trace = []
orig_act = mgx.MGX.act
def act(self, obs):
    t = obs.get("step")
    if t is not None and t % 24 == 0:
        p = self.plans[self.cur]
        farm = obs["farms"][obs["player"]]
        trace.append((t // 24, self.cur, round(farm["money"]), p["money"][t], len(farm["hands"]), p["hands"][t], mgx._distance(p["census"][t // 24], mgx._census(farm)), len(self.pending)))
    return orig_act(self, obs)
mgx.MGX.act = act
mgx._STATE.clear()
pair = [None, None]; pair[seat] = mgx.agent; pair[1 - seat] = opp
with _silence_fds():
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}); env.run(pair)
    fin = env.toJSON()["steps"][-1]
sys.stdout.reconfigure(encoding="utf-8")
print("shops", fin[0]["observation"]["town"]["unlocked_shops"], "us", fin[seat]["reward"], "them", fin[1-seat]["reward"])
print("day plan  money  plan_money  hands plan_hands  farm_dist pending")
for r in trace: print(*r)
st = mgx._STATE["mgx"]
print("log:", [l for l in st.log if l[1] != "retry"][:25])
