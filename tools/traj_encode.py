#!/usr/bin/env python3
"""Streaming top-10 trajectory corpus builder.

Reads results/top10/crawl.json (from top10_scrape.py), selects episodes,
downloads each replay from the public CDN into SCRATCH, encodes every
top-10-team seat into a compact .npz under results/top10/traj/, and deletes
the raw 31MB JSON immediately. Aborts if free disk < 2 GB (mistake 19).

Usage: python tools/traj_encode.py <max_episodes> [--all-vs]
  default selection: top10-vs-top10 episodes only, newest first.
  --all-vs: any episode with >=1 top-10 seat (newest first).
"""
import sys, os, json, time, shutil
import numpy as np
import requests

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TOP10 = {
    16732748: "DSM", 16718819: "Majkel1337", 16681125: "MMPQ",
    16730612: "UnknownMotherGoose", 16730524: "ThirdFarmClub",
    16640510: "SpaTaro", 16817528: "QQ", 16675778: "OrbitalTerraformer",
    16760701: "YannikSchiffner", 16760569: "OtterVibe",
}
OUT = os.path.join("results", "top10", "traj")
SCRATCH = os.environ.get("TRAJ_SCRATCH") or os.path.join(
    os.environ.get("TEMP", "."), "traj_raw")
CDN = "https://www.kaggleusercontent.com/episodes/{}.json"

CROPS = ["", "CARROT", "MELON", "STRAWBERRY", "TOMATO", "WHEAT"]
ANIMALS = ["", "COW", "GOOSE", "SHEEP"]
KINDS = ["EMPTY", "LOCKED", "PLANT", "COOP", "PASTURE", "OTHER"]
PRODUCTS = ["CARROT", "COW", "EGG", "FERTILIZER", "GOOSE", "MELON",
            "MILK", "SHEEP", "STRAWBERRY", "TOMATO", "WHEAT", "WOOL"]
MKT_PRODUCTS = ["CARROT", "EGG", "FERTILIZER", "MELON", "MILK",
                "STRAWBERRY", "TOMATO", "WHEAT", "WOOL"]
MAXH = 16   # hand slots kept
T = 720

# tile fields (per farm): see schema probe 2026-09-20
TFIELDS = ["kind", "crop", "planted_day", "watered", "cuw", "fert_left",
           "yield_units", "life_left", "animal", "fed", "cared", "cunf",
           "fert_avail", "care_bonus", "placed_day"]


def enc_tiles(farm, day, step):
    g = np.zeros((100, len(TFIELDS)), dtype=np.int16)
    tiles = farm["tiles"]
    for r in range(10):
        for c in range(10):
            t = tiles[r][c]
            i = r * 10 + c
            if t is None:
                continue
            if isinstance(t, str):
                g[i, 0] = 1 if t == "LOCKED" else 5
                continue
            kind = t.get("kind", "")
            g[i, 0] = KINDS.index(kind) if kind in KINDS else 5
            if "crop" in t:
                g[i, 1] = CROPS.index(t["crop"]) if t["crop"] in CROPS else 0
                g[i, 2] = t.get("planted_day", 0)
                g[i, 3] = 1 if t.get("watered_today") else 0
                g[i, 4] = min(t.get("consecutive_unwatered", 0), 99)
                fu = t.get("fertilized_until_day", -1)
                g[i, 5] = max(min(fu - day, 99), 0) if fu >= 0 else 0
                g[i, 6] = min(t.get("yield_units", 0), 999)
                g[i, 7] = max(min(t.get("max_lifespan_step", 0) - step, 999), 0)
            if "animal" in t:
                a = t["animal"]
                g[i, 8] = ANIMALS.index(a) if a in ANIMALS else 0
                g[i, 9] = 1 if t.get("fed_today") else 0
                g[i, 10] = 1 if t.get("cared_today") else 0
                g[i, 11] = min(t.get("consecutive_unfed", 0), 99)
                g[i, 12] = 1 if t.get("fertilizer_available") else 0
                g[i, 13] = min(t.get("pending_care_bonus", 0), 99)
                g[i, 14] = t.get("placed_day", 0)
    return g


def encode_seat(rep, seat):
    steps = rep["steps"]
    vocab = {"": 0}

    def vid(s):
        s = str(s)
        if s not in vocab:
            vocab[s] = len(vocab)
        return vocab[s]

    n = len(steps)
    tiles_self = np.zeros((n, 100, len(TFIELDS)), dtype=np.int16)
    tiles_opp = np.zeros_like(tiles_self)
    scal = np.zeros((n, 8), dtype=np.float32)   # day,hour,money_s,money_o,nhands_s,nhands_o,hires_s,quads_s
    prices = np.zeros((n, 9), dtype=np.float32)
    minv = np.zeros((n, 9), dtype=np.float32)
    fpos = np.full((n, 2), -1, dtype=np.int8)
    hpos = np.full((n, MAXH, 2), -1, dtype=np.int8)
    opp_fpos = np.full((n, 2), -1, dtype=np.int8)
    opp_hpos = np.full((n, MAXH, 2), -1, dtype=np.int8)
    seeds = np.zeros((n, 5), dtype=np.int16)
    shed = np.zeros((n, 12), dtype=np.int16)
    carry = np.zeros((n, MAXH + 1, 12), dtype=np.int16)
    act_f = np.zeros((n, 3), dtype=np.int16)
    act_h = np.zeros((n, MAXH, 3), dtype=np.int16)
    act_m = np.zeros((n, 10, 3), dtype=np.int16)

    for si, s in enumerate(steps):
        me, opp = s[seat], s[1 - seat]
        obs = me.get("observation") or {}
        farms = obs.get("farms")
        if not farms:
            continue
        day, hour = obs.get("day", 0), obs.get("hour", 0)
        pl = obs.get("player", seat)
        fs, fo = farms[pl], farms[1 - pl]
        tiles_self[si] = enc_tiles(fs, day, si)
        tiles_opp[si] = enc_tiles(fo, day, si)
        scal[si] = [day, hour, fs.get("money", 0), fo.get("money", 0),
                    len(fs.get("hands", [])), len(fo.get("hands", [])),
                    fs.get("hires_today", 0), len(fs.get("unlocked_quadrants", []))]
        mk = obs.get("market", {})
        pr, iv = mk.get("prices", {}), mk.get("inventory", {})
        for j, p in enumerate(MKT_PRODUCTS):
            prices[si, j] = pr.get(p, 0)
            minv[si, j] = iv.get(p, 0)
        fpos[si] = fs.get("farmer", [-1, -1])[:2]
        for j, h in enumerate(fs.get("hands", [])[:MAXH]):
            hpos[si, j] = h[:2]
        opp_fpos[si] = fo.get("farmer", [-1, -1])[:2]
        for j, h in enumerate(fo.get("hands", [])[:MAXH]):
            opp_hpos[si, j] = h[:2]
        pv = obs.get("private", {})
        sd = pv.get("seeds", {})
        for j, cnm in enumerate(CROPS[1:]):
            seeds[si, j] = min(sd.get(cnm, 0), 9999)
        sh = pv.get("shed", {})
        for j, p in enumerate(PRODUCTS):
            shed[si, j] = min(sh.get(p, 0), 9999)
        for j, invd in enumerate((pv.get("inventories") or [])[:MAXH + 1]):
            for p, q in (invd or {}).items():
                if p in PRODUCTS:
                    carry[si, j, PRODUCTS.index(p)] = min(q, 999)
        a = me.get("action") or {}
        fa = a.get("farmer") or []
        for k in range(min(len(fa), 3)):
            act_f[si, k] = vid(fa[k])
        for j, h in enumerate((a.get("hands") or [])[:MAXH]):
            for k in range(min(len(h or []), 3)):
                act_h[si, j, k] = vid(h[k])
        for j, m in enumerate((a.get("market") or [])[:10]):
            m = m or []
            for k in range(min(len(m), 3)):
                if k == 2 and isinstance(m[2], (int, float)):
                    act_m[si, j, 2] = min(int(m[2]), 9999)
                else:
                    act_m[si, j, k] = vid(m[k])

    inv_vocab = [""] * len(vocab)
    for k, v in vocab.items():
        inv_vocab[v] = k
    return dict(tiles_self=tiles_self, tiles_opp=tiles_opp, scal=scal,
                prices=prices, minv=minv, fpos=fpos, hpos=hpos,
                opp_fpos=opp_fpos, opp_hpos=opp_hpos, seeds=seeds, shed=shed,
                carry=carry, act_f=act_f, act_h=act_h, act_m=act_m,
                vocab=np.array(inv_vocab, dtype=object))


def main():
    max_eps = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    all_vs = "--all-vs" in sys.argv
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(SCRATCH, exist_ok=True)
    crawl = json.load(open(os.path.join("results", "top10", "crawl.json"),
                           encoding="utf-8"))
    eps = [e for e in crawl["episodes"] if e.get("state") == "COMPLETED"]
    need = 1 if all_vs else 2
    eps = [e for e in eps
           if sum(1 for a in e.get("agents", []) if a.get("teamId") in TOP10) >= need]
    eps.sort(key=lambda e: e.get("createTime", ""), reverse=True)
    done_ids = {f.split("_")[0][2:] for f in os.listdir(OUT) if f.endswith(".npz")}
    todo = [e for e in eps if str(e["id"]) not in done_ids][:max_eps]
    print(f"{len(eps)} candidate episodes, {len(todo)} to encode")
    n_ok = n_fail = 0
    for i, e in enumerate(todo):
        if shutil.disk_usage("C:\\").free < 2 * 1024**3:
            print("ABORT: <2GB free disk")
            break
        eid = e["id"]
        raw = os.path.join(SCRATCH, f"{eid}.json")
        try:
            r = requests.get(CDN.format(eid), timeout=180)
            r.raise_for_status()
            with open(raw, "wb") as f:
                f.write(r.content)
            rep = json.load(open(raw, encoding="utf-8"))
            rewards = rep.get("rewards", [None, None])
            for a in e.get("agents", []):
                tid = a.get("teamId")
                if tid not in TOP10:
                    continue
                seat = a.get("index", 0)
                data = encode_seat(rep, seat)
                meta = dict(episodeId=eid, seat=seat, teamId=tid,
                            team=TOP10[tid], submissionId=a.get("submissionId"),
                            score=a.get("updatedScore"), rewards=rewards,
                            seed=(rep.get("info") or {}).get("seed"),
                            createTime=e.get("createTime"))
                data["meta"] = np.array(json.dumps(meta))
                np.savez_compressed(
                    os.path.join(OUT, f"ep{eid}_s{seat}_{TOP10[tid]}.npz"),
                    **data)
            n_ok += 1
        except Exception as ex:
            n_fail += 1
            print(f"ep {eid}: FAILED {type(ex).__name__} {ex}")
        finally:
            try:
                if os.path.exists(raw):
                    os.remove(raw)
            except OSError:
                pass
        if (i + 1) % 10 == 0:
            free = shutil.disk_usage("C:\\").free / 1024**3
            print(f"[{i+1}/{len(todo)}] ok {n_ok} fail {n_fail} | free {free:.1f} GB")
        time.sleep(0.4)
    print(f"DONE: {n_ok} episodes encoded, {n_fail} failed -> {OUT}")


if __name__ == "__main__":
    main()
