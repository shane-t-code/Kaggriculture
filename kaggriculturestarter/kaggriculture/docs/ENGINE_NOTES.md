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

## B. OUR findings — fill this in

Read the engine and record what you actually verified. Template:

### B.1 Constants (verify against MARKET_PARAMS / CROPS / SHOPS in the source)
- [ ] `MARKET_PARAMS` matches the published price table?
- [ ] `HINGE_GAIN` value
- [ ] `LAND_ORDER`
- [ ] `TOWN_CENTER_PRODUCTS`
- [ ] `SHOPS` → product map

### B.2 The RNG / shop-draw coupling (critical for benchmarking)
Claimed by Yusuke Hayashi: `_end_of_day` builds `random.Random((seed * 1_000_003) ^ day)`, calls
`_spawn_weeds` for player 0 then player 1, and only then draws the shop — so **the shop draw sits at a
stream offset equal to the two farms' combined bare-tile count.**
- [ ] Verified in source? (line ref: ______)
- [ ] Implication confirmed: a change that alters tile occupancy invalidates the seed as a control.

### B.3 Action validation
- [ ] Confirm PLANT collective validation (over-requesting a crop converts **all** that crop's PLANT
      requests to PASS that turn, counting requests even from units on occupied tiles)
- [ ] Confirm invalid actions are silent no-ops
- [ ] Confirm exact action string formats accepted by the parser

### B.4 Episode length
- [ ] Does step 719 (day 29, turn 23) execute? Does the final turn's market order settle?

### B.5 Timing
- [ ] Measure our own per-turn time. (Reported by a competitor: median turn **0.017 ms** against a
      1 s actTimeout plus ~60 s overage — i.e. we have enormous headroom for search.)
