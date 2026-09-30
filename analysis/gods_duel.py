# Duel: public "God's mode" engine (Farming Score V2 + shop overlay) vs our live dtrw.
import sys, json, importlib.util, time
sys.path.insert(0, r"C:\Kaggriculture"); sys.dont_write_bytecode = True
G = r"C:\Kaggriculture\work\pulls\sep29\god-s-mode-hacked-stores\agent\gods_mode_hacked_stores"
sys.path.insert(0, G)
from run_local import _silence_fds
with _silence_fds():
    from kaggle_environments import make
    from kaggle_environments.agent import get_last_callable
def load_gods():
    for m in ("base_agent", "shop_overlay", "shop_predictor", "gods_main"):
        sys.modules.pop(m, None)
    spec = importlib.util.spec_from_file_location("gods_main", G + r"\main.py")
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod.agent
D = r"C:\Kaggriculture\work\build_a\grow\variants\dtrw.py"
with open(r"C:\Kaggriculture\work\build_a\grow\SEEDS.jsonl", "a") as f:
    f.write(json.dumps({"tool": "gods_duel", "start": 8537, "count": 6, "ts": time.strftime("%Y-%m-%d %H:%M:%S")}) + "\n")
w = l = t = 0
for seed in range(8537, 8543):
    for pid in (0, 1):
        ags = [None, None]
        with _silence_fds():
            ags[pid] = load_gods()
        ags[1 - pid] = get_last_callable(open(D, encoding="utf-8").read(), path=D)
        with _silence_fds():
            env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}); env.run(ags)
        rw = [s.reward for s in env.steps[-1]]; m = rw[1 - pid] - rw[pid]
        w += m > 0; l += m < 0; t += m == 0
        print(f"seed {seed} dtrw seat{1-pid}: dtrw {rw[1-pid]:,.0f} gods {rw[pid]:,.0f} margin {m:+,.0f} {[str(s.status) for s in env.steps[-1]]}", flush=True)
print(f"dtrw vs gods: W{w}-L{l}-T{t}")
