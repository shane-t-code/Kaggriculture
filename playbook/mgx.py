# MGX  — "borrowed playbook" agent.
# Carries a library of complete recorded games of one top team (the donor,
# Mother-Goose) and FOLLOWS one of them, switching to a better-matching game
# each time the town reveals a new shop (steps 72, 144, ... 576).  Reflexes
# keep the plan on track when the world differs from the recording:
#   R1 plant trim   never request more plantings of a crop than seeds held
#   R2 cash guard   if we are poorer than the recording was, give up the
#                   cheapest optional purchases so the plan's next essential
#                   purchase (hires, animals, land) still goes through
#   R3 hire match   hire exactly as many hands as the recording had
#   R4 buy retry    an animal / land purchase we could not afford is retried
#                   on later steps while money allows (48-step window)
#   R5 end guard    no new investments on the last day, no product buys in
#                   the last 3 steps, sell everything left at the end
# Plan choice: longest match of the town's shops so far; ties broken by the
# recorded farm closest to ours on that day; switch only when the match gets
# longer.  Opening (before any shop): the plan in the biggest cluster of
# identical day-3 farms (most switch partners later).
# Everything is self-contained: no network, no engine import needed.
import base64
import copy
import gzip
import json
import os
import time
import zlib

SEED_COST = {"WHEAT": 10, "CARROT": 20, "TOMATO": 50, "STRAWBERRY": 100,
             "MELON": 80}
ANIMAL_COST = {"GOOSE": 300, "COW": 400, "SHEEP": 500}
LAND_PRICES = [1000, 2000, 4000]
HORIZON = 30
SAFETY = 3
RETRY_WINDOW = 48
SHOP_PRODUCTS = {"BAKERY": ["EGG", "WHEAT"], "PIZZA_SHOP": ["MILK", "TOMATO", "WHEAT"],
                 "BRUNCH_SPOT": ["EGG", "WHEAT", "STRAWBERRY"], "YARN_STORE": ["WOOL"],
                 "ICE_CREAM_SHOP": ["STRAWBERRY", "MILK", "WHEAT"], "PET_CAFE": ["CARROT"],
                 "SMOOTHIE_SHOP": ["STRAWBERRY", "MILK"], "FARMERS_MARKET": ["CARROT", "MELON", "TOMATO", "STRAWBERRY", "WHEAT"]}
MATCH_BY = os.environ.get("MGX_MATCH", "shop")     # shop = exact names; demand = products bought


def _demand(shops):
    d = {}
    for sh in shops:
        for pr in SHOP_PRODUCTS.get(sh, []):
            d[pr] = d.get(pr, 0) + 1
    return d


def _demand_sim(a, b):
    keys = set(a) | set(b)
    if not keys:
        return 1.0
    inter = sum(min(a.get(k, 0), b.get(k, 0)) for k in keys)
    union = sum(max(a.get(k, 0), b.get(k, 0)) for k in keys)
    return inter / union


ROLLOUT = os.environ.get("MGX_ROLLOUT", "0") == "1"   # look-ahead plan choice
ROLLOUT_CANDS = int(os.environ.get("MGX_CANDS", "4"))
ROLLOUT_BUDGET = float(os.environ.get("MGX_BUDGET", "0.45"))   # seconds of simulation per step
ROLLOUT_MIN_GAIN = 1500
ROLLOUT_DELAY = int(os.environ.get("MGX_DELAY", "40"))   # the switch is evaluated AND executed this many steps after the reveal
LAST_SWITCH_STEP = int(os.environ.get("MGX_LAST_SWITCH", "144"))   # no plan switch after this step
MAX_SWITCH_DIST = int(os.environ.get("MGX_MAX_DIST", "6"))         # or onto a farm further than this

_BLOB = ""          # filled in by build_agent.py for the submission file


def _fib(n):
    a, b = 1, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def _load_plans():
    if _BLOB:
        raw = zlib.decompress(base64.b85decode(_BLOB))
        return json.loads(raw.decode("utf-8"))
    here = os.path.dirname(os.path.abspath(__file__))
    with gzip.open(os.path.join(here, "plans.json.gz"), "rt",
                   encoding="utf-8") as fh:
        return json.load(fh)


def _distance(a, b):
    keys = set(a) | set(b)
    d = 0
    for k in keys:
        w = 10 if k == "LAND" else 1
        d += w * abs(a.get(k, 0) - b.get(k, 0))
    return d


def _grid(farm):
    out = []
    for row in farm["tiles"]:
        for t in row:
            if isinstance(t, dict):
                out.append(t.get("crop") or t.get("animal") or t.get("kind") or "")
            else:
                out.append("")
    return out


def _grid_distance(a, b, la, lb):
    return sum(x != y for x, y in zip(a, b)) + 10 * abs(la - lb)


def _census(farm):
    c = {}
    for row in farm["tiles"]:
        for t in row:
            if isinstance(t, dict):
                k = t.get("crop") or t.get("animal") or t.get("kind")
                if k:
                    c[k] = c.get(k, 0) + 1
    c["LAND"] = len(farm["unlocked_quadrants"])
    return c


class MGX:
    def __init__(self, plans):
        self.plans = plans
        self.cur = None
        self.match = 0
        self.pending = []      # (deadline_step, order, cost)
        self.log = []
        self.seen_shops = 0
        self.sims = []
        self.frozen = False
        self._pick_opening()

    # ---- plan choice -------------------------------------------------
    def _pick_opening(self):
        clusters = {}
        for i, p in enumerate(self.plans):
            key = json.dumps(p["grid"][3])
            clusters.setdefault(key, []).append(i)
        best = max(clusters.values(), key=len)
        # inside the biggest cluster take the median-bank game (typical town)
        best.sort(key=lambda i: self.plans[i]["bank"])
        self.cur = best[len(best) // 2]
        self.match = 0

    def _maybe_switch(self, shops, day, my_grid, my_land, my_money=0):
        k = len(shops)
        cur = self.plans[self.cur]
        if cur["shops"][:k] == shops:
            self.match = k
            return
        best = None
        want = _demand(shops)
        for i, p in enumerate(self.plans):
            m = 0
            while m < k and m < len(p["shops"]) and p["shops"][m] == shops[m]:
                m += 1
            if MATCH_BY == "demand":
                sim = _demand_sim(want, _demand(p["shops"][:k]))
                m = k if sim >= 0.999 else (k - 1 if sim >= 0.66 else m)
            if m <= self.match:
                continue
            di = min(day, len(p["grid"]) - 1)
            d = _grid_distance(p["grid"][di], my_grid, p["census"][di].get("LAND", 1), my_land)
            key = (m, -d, -abs(p["money"][day * 24] - my_money), -abs(p["bank"] - 105000))
            if d > MAX_SWITCH_DIST and day > 0:
                continue
            # twin rule: only jump to a game that was in the same state as
            # ours (same tiles, money within 25 coins) when the shop appeared
            if day > 0 and abs(p["money"][day * 24] - my_money) > 25:
                continue
            if best is None or key > best[0]:
                best = (key, i)
        if best is not None and best[0][0] > self.match:
            self.log.append((day, "switch", self.cur, best[1], best[0]))
            self.cur = best[1]
            self.match = best[0][0]

    # ---- look-ahead: candidates and incremental rollouts ---------------
    def _candidates(self, shops, day, my_grid, my_land, my_money):
        k = len(shops)
        want = _demand(shops)
        scored = []
        for i, p in enumerate(self.plans):
            if i == self.cur:
                continue
            m = 0
            while m < k and m < len(p["shops"]) and p["shops"][m] == shops[m]:
                m += 1
            sim = _demand_sim(want, _demand(p["shops"][:k]))
            di = min(day, len(p["grid"]) - 1)
            d = _grid_distance(p["grid"][di], my_grid, p["census"][di].get("LAND", 1), my_land)
            if d > 12:
                continue
            scored.append(((m + sim, -d, -abs(p["money"][day * 24] - my_money)), i))
        scored.sort(reverse=True)
        return [i for _, i in scored[:ROLLOUT_CANDS]]

    def _start_rollouts(self, obs, t, cands):
        import rollout as _ro
        seed = 1000 + t   # same imagined future for every candidate
        self.sims = []
        for c in [self.cur] + cands:
            twin = copy.copy(self)
            twin.pending = list(self.pending)
            twin.log = []
            twin.sims = []
            twin.target = c
            twin.switch_at = t + ROLLOUT_DELAY
            twin.frozen = True
            try:
                ro = _ro.Rollout(obs, obs["player"], twin.act, seed=seed)
            except Exception as e:
                self.log.append((t, "rollout_fail", repr(e)))
                continue
            self.sims.append((c, ro))
        self.sim_started = t

    def _run_rollouts(self, t, t0):
        for c, ro in self.sims:
            while not ro.done and time.perf_counter() - t0 < ROLLOUT_BUDGET:
                ro.advance(12)
            if not ro.done:
                return
        # all done: decide
        results = [(ro.final, c) for c, ro in self.sims if ro.final is not None]
        self.sims = []
        if not results:
            return
        base = next((f for f, c in results if c == self.cur), None)
        best_f, best_c = max(results)
        self.log.append((t, "lookahead", self.cur, base, best_c, best_f,
                         [(c, round(f)) for f, c in results]))
        if (best_c != self.cur and base is not None and best_f - base >= ROLLOUT_MIN_GAIN
                and t <= self.sim_started + ROLLOUT_DELAY):
            self.target = best_c
            self.switch_at = self.sim_started + ROLLOUT_DELAY
            self.log.append((t, "switch_planned", self.cur, best_c, self.switch_at, round(best_f - base)))

    # ---- one step ----------------------------------------------------
    def act(self, obs):
        t0 = time.perf_counter()
        t = obs.get("step")
        if t is None:
            t = obs["day"] * 24 + obs["hour"]
        me = obs["player"]
        farm = obs["farms"][me]
        shops = list(obs["town"]["unlocked_shops"])
        if len(shops) > self.seen_shops:
            self.seen_shops = len(shops)
            if ROLLOUT and not getattr(self, "frozen", False):
                cands = self._candidates(shops, t // 24, _grid(farm),
                                         len(farm["unlocked_quadrants"]), farm["money"])
                if cands and t < 660:
                    self._start_rollouts(obs, t, cands)
            elif t <= LAST_SWITCH_STEP:
                self._maybe_switch(shops, t // 24, _grid(farm),
                                   len(farm["unlocked_quadrants"]), farm["money"])
        if getattr(self, "sims", None) and not getattr(self, "frozen", False):
            self._run_rollouts(t, t0)
        if getattr(self, "switch_at", None) == t and getattr(self, "target", None) is not None:
            self.log.append((t, "switch", self.cur, self.target, "scheduled"))
            self.cur = self.target
            self.target = None
        p = self.plans[self.cur]
        if t >= len(p["table"]):
            return {"farmer": ["PASS"], "hands": [], "market": []}
        farmer, hands, market = p["table"][t]
        farmer = list(farmer) if farmer else ["PASS"]
        hands = [list(h) if isinstance(h, list) else h for h in hands]
        market = [list(o) for o in market]
        money = farm["money"]
        prices = obs["market"]["prices"]

        # R5 end guard
        if t >= 696:
            market = [o for o in market
                      if o[0] not in ("BUY_ANIMAL", "BUY_LAND", "BUY_SEED")]
        if t >= 717:
            market = [o for o in market if o[0] != "BUY_PRODUCT"]

        # R2 cash guard: protect only the plan's HIRES within the horizon
        # (animals / land are handled by R4).  Cut = what the next hires
        # cost minus the money we will have then if we follow the plan.
        rec_money = p["money"]
        rec_hands = p["hands"]
        need = 0
        deficit = rec_money[t] - money          # how much poorer we are
        if deficit > 0:
            for s in range(t, min(t + HORIZON, len(rec_money) - 1)):
                gained = rec_hands[s + 1] - (rec_hands[s] if s % 24 else 0)
                if gained > 0:
                    cost = sum(_fib(i) for i in range(gained))
                    projected = money + (rec_money[s] - rec_money[t])
                    need = max(need, cost - projected)
            need = min(need, deficit)
        if need > 0:
            for kind in ("BUY_SEED", "BUY_PRODUCT"):
                for o in market:
                    if need <= 0:
                        break
                    if o[0] != kind or len(o) < 3:
                        continue
                    unit = (SEED_COST.get(o[1], 10) if kind == "BUY_SEED"
                            else float(prices.get(o[1], 40)))
                    cut = min(int(o[2]), int(-(-need // unit)))
                    if cut > 0:
                        o[2] = int(o[2]) - cut
                        need -= cut * unit
                        self.log.append((t, "cut", kind, o[1], cut))
            market = [o for o in market
                      if not (o[0] in ("BUY_SEED", "BUY_PRODUCT")
                              and len(o) > 2 and int(o[2]) <= 0)]

        # R3 hire match (+ catch-up)
        want = p["hands"][t + 1] - len(farm["hands"])
        rest = [o for o in market if o[0] != "HIRE"]
        first_hire = next((i for i, o in enumerate(market) if o[0] == "HIRE"),
                          len(rest))
        first_hire = min(first_hire, len(rest))
        market = rest[:first_hire] + [["HIRE"]] * max(0, want) + rest[first_hire:]
        # keep the hands action list the size of our real crew
        hands = hands[:len(farm["hands"])]
        while len(hands) < len(farm["hands"]):
            hands.append(["PASS"])

        # R4 buy retry: essential purchases we cannot afford now are deferred
        hire_cost = sum(_fib(farm.get("hires_today", 0) + i)
                        for i in range(max(0, want)))
        avail = money - hire_cost
        kept = []
        for o in market:
            if o[0] == "BUY_ANIMAL" and len(o) > 2:
                cost = ANIMAL_COST.get(o[1], 400) * int(o[2])
            elif o[0] == "BUY_LAND":
                n = len(farm["unlocked_quadrants"]) - 1
                cost = LAND_PRICES[n] if 0 <= n < 3 else 0
            else:
                kept.append(o)
                continue
            if cost <= avail:
                avail -= cost
                kept.append(o)
            else:
                self.pending.append((t + RETRY_WINDOW, o, cost))
                self.log.append((t, "defer", o, cost, round(money)))
        market = kept
        still = []
        for dl, o, cost in self.pending:
            if t > dl:
                continue
            if cost <= avail and len(market) < 10:
                avail -= cost
                market.insert(0, o)
                self.log.append((t, "retry", o))
            else:
                still.append((dl, o, cost))
        self.pending = still

        # R1 plant trim
        seeds = dict((obs.get("private") or {}).get("seeds") or {})
        units = [("f", None)] + [("h", i) for i in range(len(hands))]
        for who, i in units:
            a = farmer if who == "f" else hands[i]
            if isinstance(a, list) and a and a[0] == "PLANT" and len(a) > 1:
                if seeds.get(a[1], 0) > 0:
                    seeds[a[1]] -= 1
                elif who == "f":
                    farmer = ["PASS"]
                else:
                    hands[i] = ["PASS"]

        # R5 final liquidation
        if t >= 717:
            shed = dict((obs.get("private") or {}).get("shed") or {})
            have = {o[1] for o in market if o[0] == "SELL" and len(o) > 1}
            for item, n in sorted(shed.items(), key=lambda kv: -kv[1]):
                if n > 0 and item not in have and len(market) < 10:
                    market.append(["SELL", item, int(n)])
        return {"farmer": farmer, "hands": hands, "market": market[:10]}


_STATE = {}


def agent(obs, config=None):
    st = _STATE.get("mgx")
    step = obs.get("step")
    if step is None:
        step = obs["day"] * 24 + obs["hour"]
    if st is None or step == 0:
        if "plans" not in _STATE:
            _STATE["plans"] = _load_plans()
        st = _STATE["mgx"] = MGX(_STATE["plans"])
    try:
        return st.act(obs)
    except Exception as e:           # never crash: a crash forfeits the game
        st.log.append((step, "error", repr(e)))
        return {"farmer": ["PASS"], "hands": [], "market": []}
