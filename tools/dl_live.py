#!/usr/bin/env python3
"""Download missing live replays for a submission id into a target dir.
Usage: python dl_live.py <SUB_ID> <target_dir>"""
import subprocess, sys, os, re, glob

KAGGLE = os.path.join(".venv", "Scripts", "kaggle.exe")

def main():
    sub_id, target = sys.argv[1], sys.argv[2]
    os.makedirs(target, exist_ok=True)
    out = subprocess.run([KAGGLE, "competitions", "episodes", sub_id],
                         capture_output=True, text=True)
    ids = re.findall(r"^\s*(\d{6,})\s", out.stdout + out.stderr, re.M)
    have = set()
    for f in glob.glob(os.path.join(target, "*.json")):
        m = re.search(r"(\d{6,})", os.path.basename(f))
        if m:
            have.add(m.group(1))
    missing = [i for i in ids if i not in have]
    print(f"{len(ids)} episodes listed, {len(have)} present, {len(missing)} to fetch")
    ok = 0
    for i, ep in enumerate(missing):
        r = subprocess.run([KAGGLE, "competitions", "replay", ep, "-p", target],
                           capture_output=True, text=True)
        if r.returncode == 0:
            ok += 1
        else:
            print(f"FAIL {ep}: {(r.stderr or r.stdout)[:120]}")
    print(f"downloaded {ok}/{len(missing)}")

if __name__ == "__main__":
    main()
