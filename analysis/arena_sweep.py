# ARENA SWEEP  — our live agent dropped into the
# TOP-10 teams' real games: same world (pinned shop sequence, same seed),
# same opponent (the other seat's recorded actions), we replace one seat.
# Key numbers per game: our bank vs the bank the top team made IN THAT SAME
# SEAT/WORLD (gap_vs_ref), and our margin vs the opponent tape.
# Caveat (known, documented): a tape opponent does not react to us.
# Usage: python arena_sweep.py <agent_label> <agent_path> <stride> <offset>
import ast, gzip, json, sys, time
from collections import defaultdict
from pathlib import Path
R = Path(r"C:\Kaggriculture"); sys.path.insert(0, str(R)); sys.dont_write_bytecode = True
from run_local import _silence_fds
with _silence_fds():
    from kaggle_environments import make
    from kaggle_environments.agent import get_last_callable
    import kaggle_environments.envs.kaggriculture.kaggriculture as K
from tools import shop_pin
from tools.arena import load_replay, tape_agent, shop_sequence

label, apath, stride, offset = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
OUT = R / "work" / "build_a" / "arena" / f"rows_{label}_{offset}.jsonl"
done = set()
for f in (R / "work" / "build_a" / "arena").glob(f"rows_{label}_*.jsonl"):
    for l in f.read_text(encoding="utf-8").splitlines():
        if l.strip():
            r = json.loads(l); done.add((r["episode"], r["seat"]))
files = sorted((R / "replays" / "top10").glob("ep_*.json.gz"))
PHASES = ((0, 9), (10, 15), (16, 23), (24, 29))

def census(farm):
    c = defaultdict(int)
    for row in farm["tiles"]:
        for t in row:
            if isinstance(t, dict):
                if t.get("animal"): c[t["animal"]] += 1
                elif t.get("kind") == "PLANT": c[t["crop"]] += 1
    c["QUADS"] = len(farm["unlocked_quadrants"]); c["HANDS"] = len(farm["hands"])
    return dict(c)

def curve(steps, seat, getter):
    out = {}
    for d in (6, 9, 12, 15, 18, 21, 24, 27):
        t = min(d * 24 + 12, len(steps) - 1)
        o = getter(steps[t])
        out[d] = {"bank": o["farms"][seat]["money"], "census": census(o["farms"][seat])}
    return out

jobs = [(f, s) for f in files for s in (0, 1)]
_only = R / "work" / "build_a" / "arena" / "intact.json"
if label.endswith("C") and _only.exists():
    keep = {tuple(x) for x in json.load(open(_only))}
    jobs = [(f, s) for f, s in jobs if (int(f.name.split("_")[1].split(".")[0]), s) in keep]
for idx, (f, seat) in enumerate(jobs):
    if idx % stride != offset: continue
    ep = int(f.name.split("_")[1].split(".")[0])
    if (ep, seat) in done: continue
    try:
        rep = load_replay(str(f))
        names = rep["info"]["TeamNames"]
        names = ast.literal_eval(names) if isinstance(names, str) else names
        seed = rep.get("configuration", {}).get("seed") or rep["info"]["seed"]
        seq = shop_sequence(rep)
        ref_rw = [s["reward"] for s in rep["steps"][-1]]
        agents = [tape_agent(rep, 0), tape_agent(rep, 1)]
        agents[seat] = get_last_callable(Path(apath).read_text(encoding="utf-8"), path=apath)
        ledger = [defaultdict(float), defaultdict(float)]; ctx = {}
        pm0, cu0 = K._process_market, K._commit_unit
        def pm(st, env):
            ctx.update(ids={id(x): i for i, x in enumerate(st[0].observation.farms)}, day=int(st[0].observation.step) // 24)
            return pm0(st, env)
        def cu(op, item, price, fm, pr, m, cap=100):
            cash = fm["money"]; ok = cu0(op, item, price, fm, pr, m, cap)
            if ok:
                ph = next(i for i, (a, b) in enumerate(PHASES) if a <= ctx["day"] <= b)
                key = item if op == "SELL" else op + "_" + item
                ledger[ctx["ids"][id(fm)]][f"{key}:{ph}"] += fm["money"] - cash
                ledger[ctx["ids"][id(fm)]][f"{key}:n{ph}"] += 1
            return ok
        K._process_market, K._commit_unit = pm, cu
        shop_pin.install(seq)
        try:
            with _silence_fds():
                env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed})
                env.run(agents)
        finally:
            K._process_market, K._commit_unit = pm0, cu0
            shop_pin.uninstall()
        rw = [s.reward for s in env.steps[-1]]
        row = {"episode": ep, "seat": seat, "ref_team": names[seat], "opp_team": names[1 - seat],
               "our_bank": rw[seat], "ref_bank": ref_rw[seat], "opp_bank_run": rw[1 - seat],
               "opp_bank_orig": ref_rw[1 - seat], "margin": rw[seat] - rw[1 - seat],
               "ref_margin": ref_rw[seat] - ref_rw[1 - seat],
               "statuses": [str(s.status) for s in env.steps[-1]],
               "shops": list(env.steps[-1][0].observation.town["unlocked_shops"]),
               "our_sales": dict(ledger[seat]),
               "our_curve": curve(env.steps, seat, lambda st: st[0]["observation"] if isinstance(st[0], dict) else st[0].observation),
               "ref_curve": curve(rep["steps"], seat, lambda st: st[0]["observation"]),
               "opp_curve_run": curve(env.steps, 1 - seat, lambda st: st[0]["observation"] if isinstance(st[0], dict) else st[0].observation),
               "opp_curve_orig": curve(rep["steps"], 1 - seat, lambda st: st[0]["observation"]),
               "opp_sales_run": dict(ledger[1 - seat])}
    except Exception as e:
        row = {"episode": ep, "seat": seat, "error": repr(e)[:300]}
    with OUT.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, default=str) + "\n")
    print(json.dumps({k: row.get(k) for k in ("episode", "seat", "ref_team", "our_bank", "ref_bank", "margin", "ref_margin", "error")}), flush=True)
print("ARENA DONE", label, offset, flush=True)
