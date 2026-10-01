"""kagsim PINNED-WORLD trust-check : same agents, same seed, same
pinned shop sequence, both engines.  PASS = final rewards identical.
kagsim.Game(seed, steps, shops=[...]) vs the python engine + tools/shop_pin.

Usage: python tools/kagsim_pin_check.py [preset] [seed]
"""
import importlib.util, time, os, sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.chdir(r"C:\Kaggriculture")

PRESET = sys.argv[1].upper() if len(sys.argv) > 1 else "MILK1"
SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 2
A_PATH = r"C:\Kaggriculture\main.py"
B_PATH = r"C:\Kaggriculture\versions\pool_band_killer.py"

from tools.shop_pin import PRESETS
seq = PRESETS[PRESET]

def load_agent(path, modname):
    spec = importlib.util.spec_from_file_location(modname, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.agent

# --- python engine, shop_pin harness (exactly what run_local --shops does) ---
from run_local import play, _silence_fds
from tools import shop_pin
shop_pin.install(PRESET)
t0 = time.time()
with _silence_fds():
    ra, rb, _ = play(A_PATH, B_PATH, SEED)
t_real = time.time() - t0
shop_pin.uninstall()

# --- kagsim with shops kwarg (fresh agent modules = fresh episode state) ---
import kagsim
agent_a = load_agent(A_PATH, "agent_a_pin")
agent_b = load_agent(B_PATH, "agent_b_pin")
t0 = time.time()
g = kagsim.Game(SEED, 720, shops=seq)
while not g.done:
    g.step(agent_a(g.observe(0)), agent_b(g.observe(1)))
t_sim = time.time() - t0
sa, sb = g.reward(0), g.reward(1)

print(f"preset {PRESET} seed {SEED}")
print(f"  python+shop_pin: ({ra}, {rb})  in {t_real:.1f}s")
print(f"  kagsim shops=  : ({sa}, {sb})  in {t_sim:.1f}s  ({t_real/max(t_sim,1e-9):.1f}x faster)")
print("PIN TRUST-CHECK", "PASSED" if (ra, rb) == (sa, sb) else "*** FAILED ***")
