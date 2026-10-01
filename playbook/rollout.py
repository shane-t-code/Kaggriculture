# ROLLOUT — simulate the rest of the game from the CURRENT
# observation, inside the episode, using the real engine (kaggle_environments
# is present at runtime; no network).  Used by the look-ahead plan chooser:
# for each candidate plan, roll the game to the end from our exact farm and
# read the bank.  The opponent is modelled as PASS (no market pressure) —
# the same for every candidate, so the ranking is fair even if absolute
# banks are optimistic.  Rollouts are incremental (a few engine steps per
# call) so they fit inside the per-step time budget.
import copy
import random

# phantom opponent: their visible farm produces this many units per day per
# tile (rough physical rates from the engine tables); they sell it all daily,
# so prices in the rollout feel the same pressure as in the real game.
PROD_RATE = {"GOOSE": ("EGG", 1.0), "COW": ("MILK", 1.2), "SHEEP": ("WOOL", 1.3),
             "STRAWBERRY": ("STRAWBERRY", 1.0), "TOMATO": ("TOMATO", 1.5),
             "WHEAT": ("WHEAT", 1.2), "CARROT": ("CARROT", 1.0), "MELON": ("MELON", 0.5)}


def phantom_production(farm, day):
    out = {}
    for row in farm["tiles"]:
        for t in row:
            if not isinstance(t, dict):
                continue
            k = t.get("animal") or t.get("crop")
            if k in PROD_RATE:
                prod, rate = PROD_RATE[k]
                if t.get("crop") and day - t.get("planted_day", day) < 3:
                    continue          # not mature yet
                out[prod] = out.get(prod, 0) + rate
    return out


def _deep(x):
    return copy.deepcopy(x)


class Rollout:
    def __init__(self, obs, me, act_fn, seed=None, opp_fn=None):
        from kaggle_environments import make
        self.me = me
        self.act_fn = act_fn
        self.opp_fn = opp_fn
        self.env = make("kaggriculture",
                        configuration={"episodeSteps": 720,
                                       "seed": seed if seed is not None
                                       else random.randrange(1, 10 ** 9)})
        self.env.reset()
        st = self.env.state
        shared = st[0].observation
        for k in ("farms", "market", "town", "step", "day", "hour"):
            if k in obs:
                shared[k] = _deep(obs[k])
        for i in range(2):
            st[i].observation["private"] = (_deep(obs["private"]) if i == me
                                            else st[i].observation["private"])
            st[i].observation["player"] = i
            if "remainingOverageTime" in obs:
                st[i].observation["remainingOverageTime"] = obs["remainingOverageTime"]
        # the engine numbers steps by len(env.steps): pad so the next step is
        # obs.step + 1 and the day/hour clock stays right
        base = int(obs.get("step", shared.get("step", 0)))
        while len(self.env.steps) < base + 1:
            self.env.steps.append(self.env.state)
        shared["step"] = base
        self.done = False
        self.final = None

    def _phantom_step(self):
        st = self.env.state
        shared = st[0].observation
        step = int(shared["step"])
        opp = 1 - self.me
        shed = st[opp].observation["private"]["shed"]
        if step % 24 == 0:
            self._carry = getattr(self, "_carry", {})
            for prod, rate in phantom_production(shared["farms"][opp], step // 24).items():
                self._carry[prod] = self._carry.get(prod, 0) + rate
            for prod in list(self._carry):
                n = int(self._carry[prod])
                if n > 0:
                    shed[prod] = shed.get(prod, 0) + n
                    self._carry[prod] -= n
        market = []
        if step % 24 == 12:
            for item, n in list(shed.items()):
                if n > 0 and len(market) < 10:
                    market.append(["SELL", item, int(n)])
        return {"farmer": ["PASS"], "hands": [], "market": market}

    def obs_for(self, i):
        st = self.env.state
        o = _deep(st[0].observation)
        o["private"] = st[i].observation["private"]
        o["player"] = i
        return o

    def advance(self, n):
        """Run up to n engine steps; return True when the game is over."""
        for _ in range(n):
            if self.env.done:
                break
            a_me = self.act_fn(self.obs_for(self.me))
            if self.opp_fn is not None:
                a_op = self.opp_fn(self.obs_for(1 - self.me))
            else:
                a_op = self._phantom_step()
            acts = [None, None]
            acts[self.me] = a_me
            acts[1 - self.me] = a_op
            self.env.step(acts)
        if self.env.done:
            self.done = True
            self.final = float(self.env.state[self.me].reward or 0)
        return self.done
