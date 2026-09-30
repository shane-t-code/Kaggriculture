# H2H DECODE : our real live games vs HIGHER-RATED opponents.
# Exact both-seat ledgers ('s autopsy.analyze, engine-reconciled),
# streamed (download -> analyze -> keep compact row -> delete).
import csv, glob, json, subprocess, sys
from collections import defaultdict
from pathlib import Path
sys.path.insert(0, r"C:\Kaggriculture\work\\review12")
import autopsy
KAGGLE = r"C:\Kaggriculture\.venv\Scripts\kaggle.exe"
A = Path(r"C:\Kaggriculture\work\build_a\arena")
TMP = A / "h2h" / "tmp"; TMP.mkdir(parents=True, exist_ok=True)
OUT = A / "h2h" / "rows.jsonl"
lb = list(csv.DictReader(open(glob.glob(str(A / "lb" / "*.csv"))[0], encoding="utf-8-sig")))
score = {r["TeamName"]: float(r["Score"]) for r in lb if r["Score"]}
targets = []
for label in ("dt", "dtrw"):
    for l in open(rf"C:\Kaggriculture\work\build_a\live_decode\{label}_rows.jsonl", encoding="utf-8"):
        if not l.strip(): continue
        r = json.loads(l)
        if "res" in r and score.get(r["opp"], 0) >= 2100:
            targets.append((r["episode"], label, r["opp"], score[r["opp"]], r["clone_open60"]))
done = set()
if OUT.exists():
    done = {json.loads(l)["episode"] for l in OUT.read_text(encoding="utf-8").splitlines() if l.strip()}
print(len(targets), "target games;", len(done), "done", flush=True)
PH = ((0, 9), (10, 15), (16, 23), (24, 29))
for ep, label, opp, sc, clone in targets:
    if ep in done: continue
    for f in TMP.glob("*"): f.unlink()
    subprocess.run([KAGGLE, "competitions", "replay", str(ep), "-p", str(TMP)], capture_output=True, text=True)
    files = list(TMP.glob("*.json"))
    if not files: print(ep, "download failed", flush=True); continue
    try:
        res = autopsy.analyze(files[0], "h2h")
        row = {"episode": ep, "label": label, "opp": opp, "opp_score": sc, "clone60": clone, "errors": len(res["errors"]), "players": []}
        for pl in res["players"]:
            sales = defaultdict(float); units = defaultdict(float); spend = defaultdict(float)
            for k, v in pl["ledger"].items():
                day, op, item = k.split(":")
                ph = next(i for i, (a, b) in enumerate(PH) if a <= int(day) <= b)
                if op == "SELL": sales[f"{item}:{ph}"] += v[1]; units[f"{item}:{ph}"] += v[0]
                else: spend[f"{op}:{item}"] += v[1]
            daily = {d["day"]: {"bank": d["bank_open"], "hands": d["max_hands"], "census": dict(d["census"]), "quads": len(d["land"] or [])} for d in pl["daily"] if d["day"] in (3, 6, 9, 12, 15, 18, 21, 24, 27)}
            cmds = pl["commands"]; tot = sum(cmds.values())
            row["players"].append({"team": pl["team"], "seat": pl["seat"], "bank": pl["own_bank"], "margin": pl["margin"],
                                   "sales": dict(sales), "units": dict(units), "spend": dict(spend), "daily": daily,
                                   "pass_share": cmds.get("PASS", 0) / tot, "move_share": sum(cmds.get(m, 0) for m in ("NORTH", "SOUTH", "EAST", "WEST")) / tot,
                                   "land": [e["t"] / 24 for e in pl["land_events"]]})
    except Exception as e:
        row = {"episode": ep, "label": label, "opp": opp, "opp_score": sc, "error": repr(e)[:200]}
    for f in TMP.glob("*"): f.unlink()
    with OUT.open("a", encoding="utf-8") as fh: fh.write(json.dumps(row, default=str) + "\n")
print("H2H DONE", flush=True)
