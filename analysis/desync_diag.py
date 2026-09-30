# Why do top-team tapes break when the opponent changes? First failed action per game.
import ast, json, sys, glob
from collections import Counter
from pathlib import Path
R = Path(r"C:\Kaggriculture"); sys.path.insert(0, str(R)); sys.dont_write_bytecode = True
from run_local import _silence_fds
with _silence_fds():
    from kaggle_environments import make
    from kaggle_environments.agent import get_last_callable
from tools import shop_pin
from tools.arena import load_replay, tape_agent, shop_sequence
stride, offset = int(sys.argv[1]), int(sys.argv[2])
D = str(R / "work/build_a/grow/variants/dtrw.py")
rows = [json.loads(l) for f in glob.glob(r"C:Kaggricultureworkbuild_arenaows_dtrwB_*.jsonl") for l in open(f, encoding="utf-8") if l.strip()]
def intact(r):
    a = r['opp_curve_run']['18']['census']; b = r['opp_curve_orig']['18']['census']
    return all(abs(a.get(k,0)-b.get(k,0))<=1 for k in ('STRAWBERRY','WHEAT','SHEEP','COW','GOOSE','QUADS','TOMATO'))
bad = sorted((r['episode'], r['seat']) for r in rows if not r.get('error') and not intact(r))
def cen(f):
    c = Counter()
    for row in f["tiles"]:
        for t in row:
            if isinstance(t, dict): c[t.get("animal") or t.get("crop") or t.get("kind")] += 1
    c["Q"] = len(f["unlocked_quadrants"]); c["H"] = len(f["hands"])
    return c
out = open(rf"C:Kaggricultureworkbuild_arenadesync_{offset}.jsonl", "a", encoding="utf-8")
for i, (ep, seat) in enumerate(bad):
    if i % stride != offset: continue
    rep = load_replay(str(R / f"replays/top10/ep_{ep}.json.gz")); ts = 1 - seat
    agents = [tape_agent(rep, 0), tape_agent(rep, 1)]
    agents[seat] = get_last_callable(open(D, encoding="utf-8").read(), path=D)
    shop_pin.install(shop_sequence(rep))
    try:
        with _silence_fds():
            env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": rep.get("configuration", {}).get("seed") or rep["info"]["seed"]})
            env.run(agents)
    finally:
        shop_pin.uninstall()
    first_money = first_farm = None; detail = None
    for t in range(1, min(len(env.steps), len(rep["steps"]))):
        fo = rep["steps"][t][0]["observation"]["farms"][ts]; fr = env.steps[t][0]["observation"]["farms"][ts]
        if first_money is None and fo["money"] != fr["money"]:
            first_money = (t, fr["money"] - fo["money"])
        co, cr = cen(fo), cen(fr)
        if co != cr:
            diff = {k: (cr.get(k, 0), co.get(k, 0)) for k in set(co) | set(cr) if co.get(k, 0) != cr.get(k, 0)}
            act = rep["steps"][t][ts].get("action") or {}
            first_farm = t; detail = {"diff_run_vs_orig": diff, "orders": act.get("market"), "money_run_before": env.steps[t-1][0]["observation"]["farms"][ts]["money"], "money_orig_before": rep["steps"][t-1][0]["observation"]["farms"][ts]["money"]}
            break
    row = {"episode": ep, "tape_seat": ts, "first_money_diff": first_money, "first_farm_diff_step": first_farm, "detail": detail}
    out.write(json.dumps(row, default=str) + "\n"); out.flush()
    print(json.dumps(row, default=str)[:400], flush=True)
print("DIAG DONE")
