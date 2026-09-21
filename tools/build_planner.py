#!/usr/bin/env python3
"""Generate fork/planner_layer.py (self-contained, weights embedded) and
fork/v105a.py = external/pipe16_main.py + layer.

Usage: python tools/build_planner.py [--don 24] [--tau 0.02]
"""
import sys, os, base64

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TEMPLATE = '''

# PLANNER layer v105a: BC-v2 macro clone drives all units from day {DON}.
# Model: results/top10/bc2/bc_v2.npz (trained on 197 top10-vs-top10 episodes,
# 605k macro segments). Numpy-only inference; hard per-unit fallback to the
# tape action on low confidence, illegal proposal, or any exception.
import base64 as _pl_b64, io as _pl_io, zlib as _pl_zlib
import numpy as _pl_np

_PL_DON = {DON}          # planner takeover day
_PL_TAU = {TAU}          # min joint prob (after masking) to override the tape
_PL_WORK = ["WATER", "HARVEST", "PLANT", "FERTILIZE", "DIG", "FEED", "CARE",
            "COLLECT_FERTILIZER", "PICKUP", "DROP", "BUILD_COOP",
            "BUILD_PASTURE", "PLACE"]
_PL_ALLOW = {{"WATER", "HARVEST", "PLANT", "FERTILIZE", "DIG", "FEED", "CARE",
             "COLLECT_FERTILIZER"}}
_PL_CROPS = ["", "CARROT", "MELON", "STRAWBERRY", "TOMATO", "WHEAT"]
_PL_PRODUCTS = ["CARROT", "COW", "EGG", "FERTILIZER", "GOOSE", "MELON",
                "MILK", "SHEEP", "STRAWBERRY", "TOMATO", "WHEAT", "WOOL"]
_PL_MKT = ["CARROT", "EGG", "FERTILIZER", "MELON", "MILK", "STRAWBERRY",
           "TOMATO", "WHEAT", "WOOL"]
_PL_PBASE = _pl_np.array([40, 55, 55, 130, 160, 120, 60, 20, 200], dtype=_pl_np.float32)
_PL_KINDS = ["EMPTY", "LOCKED", "PLANT", "COOP", "PASTURE", "OTHER"]
_PL_ANIMALS = ["", "COW", "GOOSE", "SHEEP"]

_PL_B64 = "{BLOB}"
_PL_W = {{k: v for k, v in _pl_np.load(_pl_io.BytesIO(_pl_zlib.decompress(
    _pl_b64.b64decode(_PL_B64)))).items()}}
_PL_TELEM = {{"steps": 0, "overrides": 0, "fallback_conf": 0, "fallback_verb": 0,
             "moves": 0, "plants": 0, "digs": 0, "buyseed": 0, "errors": 0}}


def _pl_enc_tiles(farm, day, step):
    g = _pl_np.zeros((100, 15), dtype=_pl_np.int16)
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
            g[i, 0] = _PL_KINDS.index(kind) if kind in _PL_KINDS else 5
            if "crop" in t:
                g[i, 1] = _PL_CROPS.index(t["crop"]) if t["crop"] in _PL_CROPS else 0
                g[i, 2] = t.get("planted_day", 0)
                g[i, 3] = 1 if t.get("watered_today") else 0
                g[i, 4] = min(t.get("consecutive_unwatered", 0), 99)
                fu = t.get("fertilized_until_day", -1)
                g[i, 5] = max(min(fu - day, 99), 0) if fu >= 0 else 0
                g[i, 6] = min(t.get("yield_units", 0), 999)
                g[i, 7] = max(min(t.get("max_lifespan_step", 0) - step, 999), 0)
            if "animal" in t:
                a = t["animal"]
                g[i, 8] = _PL_ANIMALS.index(a) if a in _PL_ANIMALS else 0
                g[i, 9] = 1 if t.get("fed_today") else 0
                g[i, 10] = 1 if t.get("cared_today") else 0
                g[i, 11] = min(t.get("consecutive_unfed", 0), 99)
                g[i, 12] = 1 if t.get("fertilizer_available") else 0
                g[i, 13] = min(t.get("pending_care_bonus", 0), 99)
                g[i, 14] = t.get("placed_day", 0)
    return g


def _pl_bsum(tiles, day):
    kind = tiles[:, 0]; crop = tiles[:, 1]
    out = []
    plant = kind == 2
    for c in range(1, 6):
        m = plant & (crop == c)
        out += [m.sum(), (m & (tiles[:, 3] == 0)).sum(),
                tiles[m, 6].sum() if m.any() else 0]
    out.append((plant & (tiles[:, 6] == 0) & (day - tiles[:, 2] > 6)).sum())
    out += [(kind == 0).sum(), (kind == 1).sum()]
    for a in range(1, 4):
        m = tiles[:, 8] == a
        out += [m.sum(), (m & (tiles[:, 9] == 0)).sum(),
                (m & (tiles[:, 10] == 0)).sum(),
                tiles[m, 6].sum() if m.any() else 0]
    out.append((tiles[:, 12] > 0).sum())
    return _pl_np.array(out, dtype=_pl_np.float32)


def _pl_bgrid(tiles):
    g = _pl_np.zeros((100, 6), dtype=_pl_np.float32)
    g[:, 0] = tiles[:, 0] / 5.0
    g[:, 1] = _pl_np.where(tiles[:, 0] == 2, tiles[:, 1], -tiles[:, 8]) / 5.0
    g[:, 2] = tiles[:, 3] + tiles[:, 9] * 0.5
    g[:, 3] = _pl_np.minimum(tiles[:, 4] + tiles[:, 11], 3) / 3.0
    g[:, 4] = _pl_np.minimum(tiles[:, 6], 6) / 6.0
    g[:, 5] = (tiles[:, 12] + tiles[:, 10]) / 2.0
    return g.ravel()


def _pl_forward(X):
    z = X @ _PL_W["body.0.weight"].T + _PL_W["body.0.bias"]
    _pl_np.maximum(z, 0, out=z)
    z = z @ _PL_W["body.2.weight"].T + _PL_W["body.2.bias"]
    _pl_np.maximum(z, 0, out=z)
    return (z @ _PL_W["verb.weight"].T + _PL_W["verb.bias"],
            z @ _PL_W["tile.weight"].T + _PL_W["tile.bias"],
            z @ _PL_W["crop.weight"].T + _PL_W["crop.bias"])


def _pl_soft(x):
    e = _pl_np.exp(x - x.max(axis=-1, keepdims=True))
    return e / e.sum(axis=-1, keepdims=True)


def _pl_legal(verb, tx, ty, ts, seeds_left, cinv, day):
    """Legality of doing `verb` at tile (tx,ty). ts rows are y*10+x."""
    t = ts[ty * 10 + tx]
    kind = t[0]
    if verb == "WATER":
        return kind == 2 and t[3] == 0
    if verb == "HARVEST":
        return (kind == 2 and t[6] > 0) or (t[8] > 0 and t[6] > 0)
    if verb == "DIG":
        # INERT tiles only: no yield left and past the productive window
        # (the exemplar behavior; a permissive DIG strip-mined the farm)
        return kind == 2 and t[6] == 0 and day - t[2] > 6
    if verb == "PLANT":
        return kind == 0 and any(v > 0 for v in seeds_left.values())
    if verb == "FERTILIZE":
        return kind == 2 and cinv.get("FERTILIZER", 0) > 0
    if verb == "FEED":
        return t[8] > 0 and t[9] == 0 and cinv.get("WHEAT", 0) > 0
    if verb == "CARE":
        return t[8] > 0 and t[10] == 0
    if verb == "COLLECT_FERTILIZER":
        return t[8] > 0 and t[12] > 0
    return False


_PL_PARENT = agent
def agent(observation, configuration=None):
    action = _PL_PARENT(observation, configuration)
    try:
        day = int(observation.get("day", 0))
        if day < _PL_DON:
            return action
        _PL_TELEM["steps"] += 1
        seat = int(observation.get("player", 0))
        hour = int(observation.get("hour", 0))
        step = int(observation.get("step", day * 24 + hour))
        farms = observation["farms"]
        fs, fo = farms[seat], farms[1 - seat]
        pv = observation.get("private", {{}})
        ts = _pl_enc_tiles(fs, day, step)
        to = _pl_enc_tiles(fo, day, step)
        mk = observation.get("market", {{}})
        pr = _pl_np.array([mk.get("prices", {{}}).get(p, 0) for p in _PL_MKT],
                          dtype=_pl_np.float32)
        iv = _pl_np.array([mk.get("inventory", {{}}).get(p, 0) for p in _PL_MKT],
                          dtype=_pl_np.float32)
        seeds_d = dict(pv.get("seeds", {{}}))
        seeds = _pl_np.array([min(seeds_d.get(c, 0), 9999) for c in _PL_CROPS[1:]],
                             dtype=_pl_np.float32)
        shed = _pl_np.array([min(pv.get("shed", {{}}).get(p, 0), 9999)
                             for p in _PL_PRODUCTS], dtype=_pl_np.float32)
        glob = _pl_np.concatenate([
            [day / 29.0, hour / 23.0,
             _pl_np.log1p(max(fs.get("money", 0), 0)) / 12.0,
             _pl_np.log1p(max(fo.get("money", 0), 0)) / 12.0,
             _pl_np.tanh((fs.get("money", 0) - fo.get("money", 0)) / 10000.0),
             len(fs.get("hands", [])) / 16.0, fs.get("hires_today", 0) / 16.0,
             len(fs.get("unlocked_quadrants", [])) / 4.0],
            pr / _PL_PBASE, _pl_np.log1p(_pl_np.maximum(iv - 9900, 0)) / 6.0,
            seeds / 20.0, shed / 50.0,
            _pl_bsum(ts, day) / 20.0, _pl_bsum(to, day) / 20.0,
        ]).astype(_pl_np.float32)
        grid = _pl_bgrid(ts)
        hands = fs.get("hands", [])
        invs = pv.get("inventories") or []
        n_units = 1 + len(hands)
        rows = []
        for u in range(n_units):
            pos = fs.get("farmer", [4, 4]) if u == 0 else hands[u - 1]
            cinv = _pl_np.zeros(12, dtype=_pl_np.float32)
            if u < len(invs):
                for p, q in (invs[u] or {{}}).items():
                    if p in _PL_PRODUCTS:
                        cinv[_PL_PRODUCTS.index(p)] = min(q, 999)
            uf = _pl_np.array([u == 0, pos[0] / 9.0, pos[1] / 9.0,
                               cinv.sum() / 10.0, cinv[3] / 5.0, cinv[10] / 5.0],
                              dtype=_pl_np.float32)
            rows.append(_pl_np.concatenate([glob, uf, grid]))
        lv, lt, lc = _pl_forward(_pl_np.stack(rows))
        pverb, ptile, pcrop = _pl_soft(lv), _pl_soft(lt), _pl_soft(lc)

        new_hands = [list(h) for h in (action.get("hands") or [])]
        while len(new_hands) < len(hands):
            new_hands.append(["PASS"])
        new_farmer = list(action.get("farmer") or ["PASS"])
        # seeds available for THIS turn's plants (collective validation!),
        # minus plants the tape's kept units already request
        seeds_left = {{c: int(seeds_d.get(c, 0)) for c in _PL_CROPS[1:]}}
        plant_wanted = {{}}
        # units whose TAPE action is logistics stay untouched — overriding
        # them starved the herd (couriers never delivered feed) in v105a
        _KEEP = {{"FEED", "CARE", "PICKUP", "DROP", "PLACE", "BUILD_COOP",
                 "BUILD_PASTURE", "COLLECT_FERTILIZER", "FERTILIZE"}}
        for u in range(n_units):
            tape_cmd = new_farmer if u == 0 else \
                (new_hands[u - 1] if u - 1 < len(new_hands) else ["PASS"])
            if tape_cmd and str(tape_cmd[0]) in _KEEP:
                continue
            # joint decode over allowed legal (verb, tile) pairs
            pos = fs.get("farmer", [4, 4]) if u == 0 else hands[u - 1]
            cinv = {{}}
            if u < len(invs):
                cinv = dict(invs[u] or {{}})
            best, bp = None, 0.0
            order_v = _pl_np.argsort(-pverb[u])[:6]
            order_t = _pl_np.argsort(-ptile[u])[:12]
            for vi in order_v:
                vname = _PL_WORK[int(vi)]
                if vname not in _PL_ALLOW:
                    continue
                for ti in order_t:
                    tx, ty = int(ti) // 10, int(ti) % 10
                    if not _pl_legal(vname, tx, ty, ts, seeds_left, cinv, day):
                        continue
                    p = float(pverb[u][vi] * ptile[u][ti])
                    if p > bp:
                        bp, best = p, (vname, tx, ty)
                    break                      # best legal tile for this verb
            if best is None or bp < _PL_TAU:
                _PL_TELEM["fallback_conf" if best else "fallback_verb"] += 1
                continue                        # keep tape's action for unit u
            vname, tx, ty = best
            x, y = int(pos[0]), int(pos[1])
            if (x, y) != (tx, ty):
                if tx > x:
                    cmd = ["EAST"]
                elif tx < x:
                    cmd = ["WEST"]
                elif ty > y:
                    cmd = ["SOUTH"]
                else:
                    cmd = ["NORTH"]
                _PL_TELEM["moves"] += 1
            else:
                if vname == "PLANT":
                    ci = int(pcrop[u].argmax())
                    crop = _PL_CROPS[ci] if ci > 0 else "WHEAT"
                    if seeds_left.get(crop, 0) <= 0:
                        crop = max(seeds_left, key=seeds_left.get)
                    if seeds_left.get(crop, 0) <= 0:
                        continue
                    seeds_left[crop] -= 1
                    plant_wanted[crop] = plant_wanted.get(crop, 0) + 1
                    cmd = ["PLANT", crop]
                    _PL_TELEM["plants"] += 1
                else:
                    cmd = [vname]
                    if vname == "DIG":
                        _PL_TELEM["digs"] += 1
            if u == 0:
                new_farmer = cmd
            else:
                new_hands[u - 1] = cmd
            _PL_TELEM["overrides"] += 1
        # market: keep tape's orders, top up seeds for tomorrow's replanting
        orders = [list(o) for o in (action.get("market") or [])]
        if day < 28:
            for crop in ("WHEAT", "CARROT"):
                held = int(seeds_d.get(crop, 0))
                if held < 8 and len(orders) < 10 and \
                        not any(o[:2] == ["BUY_SEED", crop] for o in orders):
                    orders.append(["BUY_SEED", crop, 8 - held])
                    _PL_TELEM["buyseed"] += 1
        return dict(action, farmer=new_farmer, hands=new_hands, market=orders)
    except Exception:
        _PL_TELEM["errors"] += 1
        return action
agent.telemetry = _PL_TELEM
agent = globals().pop("agent")
'''


def main():
    args = sys.argv[1:]
    don = int(args[args.index("--don") + 1]) if "--don" in args else 24
    tau = float(args[args.index("--tau") + 1]) if "--tau" in args else 0.02
    import zlib
    raw = open(os.path.join("results", "top10", "bc2", "bc_v2.npz"), "rb").read()
    blob = base64.b64encode(zlib.compress(raw, 6)).decode()
    layer = TEMPLATE.replace("{DON}", str(don)).replace("{TAU}", str(tau)) \
                    .replace("{BLOB}", blob).replace("{{", "\x00").replace("}}", "\x01") \
                    .replace("\x00", "{").replace("\x01", "}")
    os.makedirs("fork", exist_ok=True)
    with open(os.path.join("fork", "planner_layer.py"), "w", encoding="utf-8") as f:
        f.write(layer)
    base = open(os.path.join("external", "pipe16_main.py"), "rb").read()
    with open(os.path.join("fork", "v105a.py"), "wb") as f:
        f.write(base + b"\n\n" + layer.encode("utf-8"))
    print(f"planner_layer.py {len(layer):,} ch (blob {len(blob):,}); "
          f"v105a.py {os.path.getsize(os.path.join('fork', 'v105a.py')):,} B; "
          f"DON={don} TAU={tau}")


if __name__ == "__main__":
    main()
