# BREAK STUDY — what happens to a top team's
# whole recorded game when it is moved?  The recording plays the top team's
# seat; nothing of ours is bolted on.
#   mode F  same world, same opponent recording   (harness check: must
#           reproduce the real bank exactly)
#   mode O  same world (same seed, same shops), DIFFERENT opponent = our live
#           playing for real in the other seat
#   mode W  DIFFERENT world (fresh seed, natural shops), opponent = our agent
# For every run we compare the recording's farm, step by step, with the farm
# in the real game and report: bank kept, first step the farm differs, what
# differs there (weed / missing plant / missing animal / missing land / fewer
# hands), and the money gap by day.
# DECISION RULE (fixed before any run):
#   "repairable"  = in mode O the median recording keeps >= 85% of its real
#                   bank, or the first farm differences are of ONE or TWO
#                   kinds that a reflex can fix (weed on a tile, purchase
#                   one or two turns late).
#   "not storable" = in mode W the median recording keeps < 60% of its bank
#                   even before any farm difference matters (wrong town).
# Analysis tool; not part of the submission.
# Usage: python -X utf8 p1_break.py <mode F|O|W> <per_team> <procs> [first_seed]
import ast
import json
import sys
import time
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R))
sys.dont_write_bytecode = True
OUT = R / "data" / "break_study_rows.jsonl"
AGENT = str(R / "agent" / "main.py")
TOP = ["DSM", "M & M & P & Q", "Boey", "Vadim Vasilenko", "Unknown Mother-Goose",
       "Fourth Quadrant", "DECEM", "THIRD FARM CLUB", "Smackaveli", "TheEggman"]


def tile_sig(t):
    if not isinstance(t, dict):
        return None
    return (t.get("kind"), t.get("crop") or t.get("animal"))


def farm_sig(farm):
    return ([[tile_sig(t) for t in row] for row in farm["tiles"]],
            len(farm["unlocked_quadrants"]), len(farm["hands"]))


def classify(o, n):
    """o, n = tile signatures (real game, moved game)."""
    if n is not None and n[0] and "WEED" in str(n[0]).upper():
        return "weed_on_tile"
    if o is not None and n is None:
        if o[1] and str(o[0]).upper() == "PLANT":
            return "plant_missing"
        return "animal_or_build_missing"
    if o is None and n is not None:
        return "extra_thing"
    return "different_thing"


def run(job):
    f, seat, mode, seed_new = job
    from run_local import _silence_fds
    with _silence_fds():
        from kaggle_environments import make
    from tools import shop_pin
    from tools.arena import load_replay, tape_agent, shop_sequence
    rep = load_replay(str(f))
    teams = rep["info"].get("TeamNames")
    if isinstance(teams, str):
        teams = ast.literal_eval(teams)
    seed = rep.get("configuration", {}).get("seed") or rep["info"].get("seed")
    seq = shop_sequence(rep)
    real = [rep["steps"][-1][i]["reward"] for i in range(2)]
    pair = [None, None]
    base = mode[0]
    if len(mode) > 1:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import p1_follow
        pair[seat] = p1_follow.follower(rep, seat, r3=(mode[1] >= "g"))
    else:
        pair[seat] = tape_agent(rep, seat)
    pair[1 - seat] = tape_agent(rep, 1 - seat) if base == "F" else AGENT
    use_seed = seed if base in ("F", "O") else seed_new
    t0 = time.time()
    # S = new seed, recording's whole town; A/B/C = new seed, only the first
    # 2/3/4 shops are the recording's, the rest come from another town.
    pin = None
    if base in ("F", "O", "S"):
        pin = list(seq)
    elif base in ("A", "B", "C"):
        k = {"A": 2, "B": 3, "C": 4}[base]
        other = None
        for l in OUT.read_text(encoding="utf-8").splitlines():
            r = json.loads(l)
            if (r["mode"] == "W" and r["episode"] == f.name[3:-8]
                    and r["seat"] == seat):
                other = r["shops_now"]
        pin = list(seq[:k]) + list(other[k:])
    if pin:
        shop_pin.install(pin)
    try:
        with _silence_fds():
            env = make("kaggriculture",
                       configuration={"episodeSteps": 720, "seed": use_seed})
            env.run(pair)
            new = env.toJSON()["steps"]
    finally:
        if pin:
            shop_pin.uninstall()
    orig = rep["steps"]
    first_money = first_struct = None
    what = []
    kinds = Counter()
    gap_day = {}
    n = min(len(orig), len(new))
    for t in range(n):
        of = orig[t][0]["observation"]["farms"][seat]
        nf = new[t][0]["observation"]["farms"][seat]
        if first_money is None and abs(of["money"] - nf["money"]) > 1:
            first_money = t
        if t % 24 == 0:
            gap_day[t // 24] = round(nf["money"] - of["money"])
        osig, nsig = farm_sig(of), farm_sig(nf)
        if osig != nsig:
            if first_struct is None:
                first_struct = t
                if osig[1] != nsig[1]:
                    what.append(("land", osig[1], nsig[1]))
                if osig[2] != nsig[2]:
                    what.append(("hands", osig[2], nsig[2]))
                for y, (ro, rn) in enumerate(zip(osig[0], nsig[0])):
                    for x, (a, b) in enumerate(zip(ro, rn)):
                        if a != b and len(what) < 6:
                            what.append((classify(a, b), [x, y], a, b))
            if t % 24 == 12:
                if osig[1] != nsig[1]:
                    kinds["land"] += 1
                if osig[2] != nsig[2]:
                    kinds["hands"] += 1
                for ro, rn in zip(osig[0], nsig[0]):
                    for a, b in zip(ro, rn):
                        if a != b:
                            kinds[classify(a, b)] += 1
    fin = new[-1]
    shops_new = fin[0]["observation"]["town"]["unlocked_shops"]
    row = {"mode": mode, "episode": f.name[3:-8], "seat": seat,
           "ref_team": teams[seat], "real_opp": teams[1 - seat],
           "seed": use_seed, "shops_real": seq, "shops_now": shops_new,
           "real_bank": real[seat], "real_opp_bank": real[1 - seat],
           "bank_now": fin[seat]["reward"], "opp_now": fin[1 - seat]["reward"],
           "first_money_step": first_money, "first_farm_step": first_struct,
           "first_farm_what": what, "midday_diff_kinds": dict(kinds),
           "gap_by_day": gap_day,
           "status": [s["status"] for s in fin], "secs": round(time.time() - t0)}
    return row


def main():
    mode, per_team, procs = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    seed0 = int(sys.argv[4]) if len(sys.argv) > 4 else None
    import gzip
    files = sorted((R / "replays" / "top10").glob("ep_*.json.gz"))
    done = set()
    if OUT.exists():
        for l in OUT.read_text(encoding="utf-8").splitlines():
            if l.strip():
                r = json.loads(l)
                done.add((r["mode"], r["episode"], r["seat"]))
    picked = defaultdict(list)
    for f in files:
        rep = json.load(gzip.open(f, "rt", encoding="utf-8"))
        teams = rep["info"].get("TeamNames")
        if isinstance(teams, str):
            teams = ast.literal_eval(teams)
        for s in (0, 1):
            if teams[s] in TOP and len(picked[teams[s]]) < per_team:
                picked[teams[s]].append((f, s))
    jobs = []
    k = 0
    for tm in TOP:
        for f, s in picked[tm]:
            sd = None
            if mode[0] in "WSABC":
                sd = seed0 + k
                k += 1
            if (mode, f.name[3:-8], s) not in done:
                jobs.append((f, s, mode, sd))
    print(f"mode {mode}: {len(jobs)} games to run on {procs} processes", flush=True)
    if mode == "W" and jobs:  # follower reruns reuse the same seeds (paired)
        with open(R / "data" / "SEEDS.jsonl", "a",
                  encoding="utf-8") as fh:
            fh.write(json.dumps({"tool": "p1_break", "mode": "W", "start": seed0,
                                 "count": k,
                                 "ts": time.strftime("%Y-%m-%d %H:%M:%S")}) + "\n")
    with Pool(procs) as pool:
        for row in pool.imap_unordered(run, jobs):
            with open(OUT, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
            keep = row["bank_now"] / row["real_bank"] if row["real_bank"] else 0
            print(f"{row['mode']} {row['ref_team'][:18]:18} ep {row['episode']} "
                  f"real {row['real_bank']:>9,.0f} now {row['bank_now']:>9,.0f} "
                  f"kept {keep:5.0%} vs opp now {row['opp_now']:>9,.0f} | "
                  f"money differs t{row['first_money_step']} farm differs "
                  f"t{row['first_farm_step']} {row['first_farm_what'][:2]} "
                  f"{row['secs']}s", flush=True)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
