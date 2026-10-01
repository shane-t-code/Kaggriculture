"""cppsim (kagsim) trust-check: same seeds, same agents, both engines.
PASS = final rewards identical. Also times both paths."""
import importlib.util, time, os, sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

def load_agent(path, modname):
    spec = importlib.util.spec_from_file_location(modname, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.agent

A_PATH = r"C:\Kaggriculture\main.py"          # v56a
B_PATH = r"C:\Kaggriculture\versions\v55e.py"
SEEDS = [0, 1, 7]

# --- real engine ---
os.chdir(r"C:\Kaggriculture")
from run_local import play, _silence_fds
real = {}
t0 = time.time()
for seed in SEEDS:
    with _silence_fds():
        ra, rb, _ = play(A_PATH, B_PATH, seed)
    real[seed] = (ra, rb)
t_real = time.time() - t0

# --- kagsim step-mode ---
import kagsim
agent_a = load_agent(A_PATH, "agent_a_mod")
agent_b = load_agent(B_PATH, "agent_b_mod")
sim = {}
t0 = time.time()
for seed in SEEDS:
    # fresh module state per episode (our agents reset on step==0, as live)
    g = kagsim.Game(seed)
    while not g.done:
        oa = g.observe(0)
        ob = g.observe(1)
        g.step(agent_a(oa), agent_b(ob))
    sim[seed] = (g.reward(0), g.reward(1))
t_sim = time.time() - t0

print(f"real engine: {t_real:.1f}s for {len(SEEDS)} eps | kagsim step-mode: {t_sim:.1f}s")
ok = True
for seed in SEEDS:
    match = real[seed] == sim[seed]
    ok = ok and match
    print(f"seed {seed}: real {real[seed]}  kagsim {sim[seed]}  {'MATCH' if match else '*** MISMATCH ***'}")
print("TRUST-CHECK", "PASSED" if ok else "FAILED")
