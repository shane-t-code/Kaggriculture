# ENGINE_NOTES.md — What the engine actually does

> **Rule: the engine is the source of truth, not the docs.**
> Confirmed by Kaggle staff (Domino Weir): *"TLDR: engine is the source of truth."*
>
> Engine file (after `pip install -U kaggle-environments`):
> ```
> python -c "import kaggle_environments,os;print(os.path.join(os.path.dirname(kaggle_environments.__file__),'envs','kaggriculture','kaggriculture.py'))"
> ```
> GitHub: https://github.com/Kaggle/kaggle-environments/blob/master/kaggle_environments/envs/kaggriculture/kaggriculture.py
>
> This file has two sections: **(A) documented discrepancies found by others** (sourced), and
> **(B) OUR OWN findings** — empty until we read the source ourselves. Fill in (B) before trusting (A).

---

## A. Discrepancies others found (source: SIDHAARTH SHREE, thread 732450, staff-confirmed)

https://www.kaggle.com/competitions/kaggriculture/discussion/732450

> "If you are building strategies based strictly on the documentation, please note that the underlying
> game engine executes several mechanics differently. **Where the docs and the engine disagree, the engine wins.**"

Most of these have since been corrected in the docs, but they show *where the docs were unreliable*:

| Item | Reality |
|---|---|
| Animal care bonus | Engine is **+1 per day** (docs once said +2) |
| Fertilizer selling | Market **accepts SELL for fertilizer** (a README once said buy-only) — staff confirmed: "Yes! Readme has been updated" |
| DIG on structures | "**DIG fails on occupied structures**; it only works on empty ones" |
| Planting-day watering | "the end-of-day increment runs before the weed check, **an unwatered seed turns into a weed that exact same night**" |
| Melon bonus window | "yield reaches the maximum of 6 units at age 10, **the last two days of the documented 6–12 window are dead turns**" |
| Strawberry | "produces exactly **4 times (ages 10, 12, 14, 16)** … **It is not an indefinite producer.**" |
| Yield-per-day | "the actual per-day yield for **Tomato is 1**, and for **Strawberry it is 0.5**" |
| Shed | "**the shed does not exist as a tile object in the tiles array**, so a starter script searching the array for it will find nothing. Its access points are strictly **(4,4), (5,4), (4,5), (5,5)**" |
| Notebook submission | "if you are using a Kaggle Notebook and strictly writing `%%writefile main.py`, the notebook's 'Submit to Competition' feature **produces no submission artifact and fails at scoring**" |

**Staff clarifications (Domino Weir, thread 731953):**
- "**Can fertilizer be sold?** Yes!"
- "**Does an animal need CARE to produce fertilizer?** No, it does not… **fertilizer does not accumulate**, a new unit is not yielded until the previous one is picked up."
- Market orders do **not** require standing on a shed tile: "they can be executed regardless of where you are."

**Open / unanswered:** Akul Sareen asked whether the last turn of the last day counts — a logging agent
"only printed 719 values up to day 29 turn 22 (0-indexed)"; referenced
[kaggriculture.py#L945](https://github.com/Kaggle/kaggle-environments/blob/master/kaggle_environments/envs/kaggriculture/kaggriculture.py#L945).
**Not answered by staff.** → *We should verify this ourselves; a day-29 liquidation strategy depends on it.*

---

## B. OUR findings — verified 2026-08-23 against the installed engine source

> Source read in full: `.venv\Lib\site-packages\kaggle_environments\envs\kaggriculture\kaggriculture.py`
> (1,086 lines). Line numbers below refer to that file. Empirical items were measured with
> `main.py` vs built-in `starter`, seeds 0–3, engine ≥ 1.32.7.

### B.1 Constants — ALL match the published tables

- [x] `MARKET_PARAMS` (L41–51) matches COMP_INFO's price table **exactly**, all 9 resources
      (base / I0=10,000 / T / below & above func+target). `PRICE_FLOOR = 1` (L39).
- [x] `HINGE_GAIN = 8.0` (L58). `_shape` (L61–74): log is `ln(1+x)`; hinge = `u + 8·max(0,u−1)²`
      with `u = x/T`, degenerating to linear if T ≤ 0. `amp = target·base/f(T)` and price is
      floored at $1 and rounded via `int(round(...))` (L192–206).
- [x] `LAND_ORDER = ["NE","SW","SE"]`, `LAND_PRICES = [1000, 2000, 4000]` (L96–97). Order fixed;
      `_do_buy_land` (L712–725) just indexes by how many extra quadrants you own.
- [x] `TOWN_CENTER_PRODUCTS` = all products except FERTILIZER (L114).
- [x] `SHOPS` map (L103–112) matches boatlee's embedded map verbatim. Single-product shops
      (YARN_STORE, PET_CAFE) consume 2× (L741). `MAX_SHOP_INSTANCES = 8` (L118).
- [x] `CROPS` (L11–17): wheat 10/2/4/cap6, carrot 20/2/3/cap4, tomato 50/8/int1/cap4,
      strawberry 100/10/int2/cap4, melon 80/10/**max_yield_day 12**/cap6. Melon's documented
      "max at age 10" is emergent: bonus window is ages 6–12 (`window_start = (12+1)//2 = 6`,
      L440), 1 base + 5 watered days hits the cap of 6 at age 10.
- [x] `ANIMALS` (L19–23): goose 300/coop/first 4/int 1/held 4; cow 400/pasture/8/2/6;
      sheep 500/pasture/6/3/6. Products EGG/MILK/WOOL.
- [x] Hire cost `mult · fib(n)`, fib = 1,1,2,3,5,8,13… (L690–699); counter `hires_today` resets
      at end of day (L881).

### B.2 RNG / shop-draw coupling — CONFIRMED, exactly as Hayashi described

- [x] `_end_of_day` (L860–891): builds `rng = random.Random((seed * 1_000_003) ^ day)` (L871)
      with `seed = env.info["seed"]`, then loops **player 0 then player 1**: refresh plants →
      refresh animals → `_spawn_weeds` → drop inventories → reset farmer/hands to spawn. Only
      **after both players** does it draw the shop: `rng.choice(sorted(SHOPS))` (L891).
- [x] `_spawn_weeds` (L836–840): `if tile is None and rng.random() < weed_chance` — the
      short-circuit means **one `rng.random()` call per empty (None) unlocked tile**, LOCKED and
      occupied tiles consume nothing. So the shop draw sits at a stream offset equal to the two
      farms' combined bare-tile count that evening. **Implication confirmed: any change that
      alters tile occupancy (hands→no, but plants/land/weeds→yes) shifts the town draw and the
      seed is no longer a control.** (Hand count itself does not consume RNG — but hands change
      what gets planted/dug, which does.)
- [x] Weeds spawn on both farms even for empty-tile-free strategies only if tiles are None; a
      fully-planted farm consumes zero draws.
- [x] Shop unlocks fire at end of day `d` when `(d+1) % townShopUnlockInterval == 0` (L884–891):
      with the default 3, that is end of days 2,5,8,…,23 — the 8-instance cap is reached exactly
      at end of day 23. Draw is `rng.choice(sorted(SHOPS))` — **uniform over the 8 alphabetically
      sorted names, with replacement**.

### B.3 Action validation — CONFIRMED silent no-ops + exact parser formats

- [x] **PLANT collective validation** (interpreter L921–933): counts every unit action of the form
      `["PLANT", crop]` this turn — **regardless of whether that unit's tile is occupied or
      locked** — and if the count exceeds `seeds[crop]`, **every** PLANT of that crop becomes
      `["PASS"]`. Confirmed trap: requests count even from units that couldn't have planted.
- [x] Invalid unit actions are silent no-ops: every branch of `_apply_unit_action` (L312–530)
      `return`s without effect on failure. A non-list action is ignored (L314). Moves off-board
      are no-ops (L326); LOCKED tiles are passable (L323–331) but all tile ops no-op on them
      (L414) **except** shed ops DROP/PICKUP/PLACE-into-shed which resolve before the LOCKED
      guard (L343–410).
- [x] **Unit action formats** (list form): `["NORTH"|"SOUTH"|"EAST"|"WEST"|"PASS"|"WATER"|
      "HARVEST"|"FERTILIZE"|"DIG"|"BUILD_COOP"|"BUILD_PASTURE"|"FEED"|"COLLECT_FERTILIZER"|
      "CARE"|"DROP"]`, `["PLANT", crop]`, `["PICKUP", item, n?]`, `["PLACE", item, n?]`.
- [x] **Market order formats** (`_parse_order`, L631–649): `["HIRE"]`, `["BUY_LAND"]`, and
      `["BUY_SEED"|"BUY_PRODUCT"|"BUY_ANIMAL"|"SELL", item, n]` — **the quantity is REQUIRED**
      (len < 3 → order dropped as None) and must int() to > 0. Queue truncated to 10
      (L559–560) silently.
- [x] Market processing (L544–628): orders resolve **queue-index by queue-index**; at each index,
      HIRE/BUY_LAND are atomic (player 0 first, L571–581), then SELL/BUY_* run in per-unit
      lockstep — both players quoted off the same pre-commit inventory each unit. Prices
      refreshed after each queue index (L628). A malformed sub-op kills that one order, not the
      queue (L607). Safety valve at 100k iterations (L586–588).
- [x] SELL at the $1 floor pays $1 but does **not** add to market inventory (L656–660).
      BUY_PRODUCT is quoted at post-buy inventory `inv − 1` (L601) — buy-then-sell round-trip
      nets zero, as documented.
- [x] **BUY_PRODUCT and BUY_ANIMAL deliver into the shed and FAIL if the shed is full**
      (L662–686). BUY_SEED bypasses the shed (seeds slot, uncapped, L673–677).
- [x] **FEED consumes 1 WHEAT from the acting unit's personal inventory** — not the shed
      (L505–513). Same for FERTILIZE: 1 FERTILIZER from unit inventory (L475–481). A unit must
      PICKUP wheat/fertilizer before walking out. Fertilize sets `fertilized_until_day =
      max(old, day+2)` — 3 days inclusive.
- [x] **DROP destroys overflow** past shed capacity (L343–356) while **PLACE-into-shed keeps the
      excess in inventory** (L393–409). Near a full shed, PLACE is safe and DROP is destructive.
- [x] DIG (L484–491): removes plant, weed, or **empty** structure; no-ops on an occupied
      coop/pasture; yields nothing.
- [x] HARVEST (L446–473): blocked before `first_yield_day` even if `yield_units > 0` (one-time
      crops carry 1 from planting); one-time crops are removed from the map on harvest; animals
      keep the tile and reset `yield_units` to 0.
- [x] WATER (L431–444): the one-time-crop bonus (+1, or +2 if fertilized-and-active) is applied
      **at watering time**, immediately, if `window_start ≤ age ≤ max_yield_day`.
- [x] Hand spawn (L533–541): shed-access tile with fewest occupants, NWSE tie-break — first hire
      of a day lands on locked (5,4) while the farmer stands on (4,4), as documented.

### B.4 Episode length — ANSWERED (this settles the open question in §A)

- [x] `interpreter` (L960–963): DONE fires when `step >= episodeSteps − 2`, i.e. while processing
      **step 718**. Measured: our agent is called exactly **719 times, obs.step 0…718** (seeds
      0–3, byte-counted via a wrapped agent). **Step 719 (day 29, hour 23) never reaches the
      agent. The last actionable turn is step 718 = day 29, hour 22.** Matches Akul Sareen's
      unanswered observation.
- [x] **The final turn's market orders DO settle**: `_process_market` (L941) runs before the DONE
      branch in the same interpreter pass, and reward = `farm["money"]` is read after (L963).
      A day-29 hour-22 liquidation is fully paid.
- [x] **Day 29 has NO end-of-day refresh**: `_end_of_day` fires when `(step+1) % 24 == 0`
      (L945), last firing while processing step 695 (end of day 28). Consequences:
      - The last animal production tick is **end of day 28**.
      - FEED / CARE / WATER on day 29 produce **zero** future value (escape/weed checks never
        run again). Day-29 wheat is better sold than fed.
      - CARE on day 28 banks a bonus that can never pay out → **last useful CARE day is 27**
        (explains the meta's `LAST_CARE_DAY = 27`), and only for animals whose production
        schedule ticks at end of day 28.
      - Fertilizer set available at end of day 28 is still collectable throughout day 29.
- [x] Care/production ordering inside `_daily_refresh_animals` (L805–834): production check runs
      **before** the cared+fed banking, so a bonus banked on day X first applies to the next
      production tick after day X. On an unfed production day the base 1 is produced and the bank
      resets to 0 unpaid (L826–828). Cap is `max_held` on `yield_units`.
- [x] Ongoing-crop production (L769–803) happens at end-of-day **even on an unwatered day** (as
      long as the plant survives the 2-day weed check); fertilizer doubles the tick (+2) only if
      the plant was watered that day. `max_lifespan_step` is set when the production count hits
      `max_yield`; decay (L752–766) then removes 1 yield every 2 **steps** (turns, not days)
      until 0 → weed.

### B.5 Timing — enormous headroom

- [x] Measured (in-process, seeds 0–3): v0 median **0.007–0.009 ms** per call, max 0.204 ms,
      vs `actTimeout: 1` second per step + `remainingOverageTime: 60` s (kaggriculture.json
      L9, L128). ~5 orders of magnitude of headroom for search.

### B.6 Baseline instrumentation of v0 (Phase 1 measurement)

Seeds 0–3 vs built-in `starter`, seat 0 (719 unit-turns each):

| seed | bank | starter | moving % |
|---|---|---|---|
| 0 | 20,290 | 3,596 | 44.6% |
| 1 | 20,690 | 3,460 | 45.3% |
| 2 | 20,290 | 3,550 | 44.8% |
| 3 | 21,550 | 3,670 | 44.5% |

Seed-0 farmer op mix: WATER 318, moves 321 (N120/W103/E64/S34), PLANT 47, HARVEST 19, DIG 13,
PASS 2. **v0 movement ≈ 45%** — already below the reported 55% "tripled my bank" level and well
above the ~33% reported floor; note this is a 1-unit, 1-quadrant agent, so the number will move
when hands/animals/land arrive.

### B.7 Other engine facts worth knowing (not in the docs checklist)

- The built-in **"random" agent is unseeded** (`random.Random()` fresh per call, L1028) — it is
  nondeterministic even with a fixed episode seed. **Never benchmark against "random".**
  `starter` (L1054–1083) is a deterministic single-tile carrot loop — safe as a paired control.
- `resolve_episode_seed(env)` stores the seed on `env.info["seed"]` and clears it from config, so
  the seed is not visible in agent observations (but is in the replay).
- Town consumption (L728–749): shops tick at `step % 4 == 0`, town center at `step % 24 == 0` —
  both **include step 0** (before any player can own product; it just drains market inventory
  and nudges prices up from the first turn).
- End-of-day resets the farmer to (4,4) and wipes hands/inventories (L879–882) — anything a unit
  carries at end of day auto-drops to the shed (overflow destroyed, L843–857).
- Newly unlocked land is always clean `None` tiles (L722–725) — weeds never exist on LOCKED
  tiles, and unlocking converts only `"LOCKED"` entries.
- `PLACE <animal>` on a matching empty structure places exactly 1 and ignores `n` (L377–391);
  the animal's `placed_day` (and thus its production schedule) is set at PLACE time, not
  BUY_ANIMAL time.
- If market overrides are supplied via `marketParams`, they leak into the shared observation as
  `market["params"]` (L178–185) — competition play uses defaults, so absent there.
