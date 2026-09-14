"""Paired A/B summary over py_ab jsonl rows.

Usage: python tools/ab_sum.py <jsonl> <tag_new> <tag_base> [--nonzero]
Pairs rows by seed, reports within-game MARGIN-DIFF (new vs base) mean/SE/t,
own-bank diff (confounded under natural draws — reference only), win flips.
--nonzero: latched-subset split — only seeds where the pair differs at all
(byte-identical unfired games diff exactly 0).
"""
import json, sys, math
from collections import defaultdict


def load(path):
    rows = defaultdict(dict)
    for line in open(path):
        r = json.loads(line)
        rows[r["tag"]][r["seed"]] = r
    return rows


def main():
    path, tag_new, tag_base = sys.argv[1], sys.argv[2], sys.argv[3]
    nonzero = "--nonzero" in sys.argv
    rows = load(path)
    A, B = rows[tag_new], rows[tag_base]
    seeds = sorted(set(A) & set(B))
    diffs, own, flips_up, flips_dn = [], [], 0, 0
    for s in seeds:
        mn = A[s]["a"] - A[s]["b"]
        mb = B[s]["a"] - B[s]["b"]
        d = mn - mb
        if nonzero and d == 0:
            continue
        diffs.append(d)
        own.append(A[s]["a"] - B[s]["a"])
        wn, wb = A[s]["a"] > A[s]["b"], B[s]["a"] > B[s]["b"]
        if wn and not wb:
            flips_up += 1
        if wb and not wn:
            flips_dn += 1
    n = len(diffs)
    if not n:
        print("no paired seeds"); return
    m = sum(diffs) / n
    sd = math.sqrt(sum((d - m) ** 2 for d in diffs) / max(1, n - 1))
    se = sd / math.sqrt(n)
    mo = sum(own) / n
    wins_new = sum(1 for s in seeds if A[s]["a"] > A[s]["b"])
    wins_base = sum(1 for s in seeds if B[s]["a"] > B[s]["b"])
    print(f"{tag_new} vs {tag_base}: n={n} paired seeds"
          + (" (nonzero-diff subset)" if nonzero else ""))
    print(f"  margin-diff {m:+,.0f} ± {se:,.0f} (t={m/se if se else 0:.2f})")
    print(f"  own-bank diff {mo:+,.0f} (reference only)")
    print(f"  wins {wins_base}->{wins_new} (flips +{flips_up}/-{flips_dn})")


if __name__ == "__main__":
    main()
