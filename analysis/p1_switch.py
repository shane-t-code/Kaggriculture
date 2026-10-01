# PLAN SWITCH TEST — can we follow plan A and switch to plan B
# (same team, same first shops, different game) when the town says so?
# Runs in B's world (B's seed and B's shops) against our agent:
#   control = B alone;  test = A until the switch step, then B.
# DECISION RULE (fixed in advance): switching is usable if the test keeps >= 90% of the
# control's bank in the median pair.
# Usage: python -X utf8 p1_switch.py <tag> <team> <switch_step> <n_pairs> <procs>
import ast, gzip, json, sys, time
from collections import defaultdict
from multiprocessing import Pool
from pathlib import Path
R = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(R)); sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
AGENT = str(R / "agent" / "main.py")
OUT = R / "data" / "switch_test_rows.jsonl"

def load(tag, ep):
    return json.load(gzip.open(R / "replays" / tag / f"ep_{ep}.json.gz", "rt", encoding="utf-8"))

def run(job):
    tag, team, epa, epb, sw = job
    from run_local import _silence_fds
    with _silence_fds():
        from kaggle_environments import make
    from tools import shop_pin
    from tools.arena import shop_sequence
    import p1_follow
    ra, rb = load(tag, epa), load(tag, epb)
    ta = ast.literal_eval(ra["info"]["TeamNames"]) if isinstance(ra["info"]["TeamNames"], str) else ra["info"]["TeamNames"]
    tb = ast.literal_eval(rb["info"]["TeamNames"]) if isinstance(rb["info"]["TeamNames"], str) else rb["info"]["TeamNames"]
    sa, sb = ta.index(team), tb.index(team)
    pa, pb = p1_follow.build_plan(ra, sa), p1_follow.build_plan(rb, sb)
    seed = rb.get("configuration", {}).get("seed") or rb["info"].get("seed")
    out = {}
    for name, plan in (("control", pb), ("test", p1_follow.splice([pa, pb], [sw]))):
        pair = [None, None]
        pair[sb] = p1_follow.follower_from(plan, sb, r3=True)
        pair[1 - sb] = AGENT
        shop_pin.install(shop_sequence(rb))
        try:
            with _silence_fds():
                env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed})
                env.run(pair)
                fin = env.toJSON()["steps"][-1]
        finally:
            shop_pin.uninstall()
        out[name] = (fin[sb]["reward"], fin[1 - sb]["reward"])
    row = {"team": team, "a": epa, "b": epb, "switch": sw, "b_real": rb["steps"][-1][sb]["reward"],
           "control": out["control"], "test": out["test"], "shops": shop_sequence(rb)}
    return row

def main():
    tag, team, sw, npairs, procs = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
    k = max(1, sw // 72)          # shops known at the switch step
    by = defaultdict(list)
    for f in sorted((R / "replays" / tag).glob("ep_*.json.gz")):
        rep = load(tag, f.name[3:-8])
        shops = tuple(rep["steps"][-1][0]["observation"]["town"]["unlocked_shops"])
        by[shops[:k]].append(f.name[3:-8])
    jobs = []
    for pref, eps in sorted(by.items(), key=lambda kv: -len(kv[1])):
        for i in range(0, len(eps) - 1, 2):
            jobs.append((tag, team, eps[i], eps[i + 1], sw))
    jobs = jobs[:npairs]
    print(f"{len(jobs)} pairs, switch at step {sw} ({k} shops known)", flush=True)
    with Pool(procs) as pool:
        for row in pool.imap_unordered(run, jobs):
            with open(OUT, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(row) + "\n")
            c, t = row["control"], row["test"]
            print(f"A {row['a']} -> B {row['b']} | B real {row['b_real']:>9,.0f} | control {c[0]:>9,.0f} vs agent {c[1]:>9,.0f} | "
                  f"test {t[0]:>9,.0f} vs agent {t[1]:>9,.0f} | test/control {t[0]/max(c[0],1):5.0%}", flush=True)

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
