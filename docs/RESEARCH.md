# RESEARCH.md — Kaggriculture Competitive Intelligence

> **Captured:** 2026-08-25 (leaderboard read 2026-08-23–25). **Engine:** 1.32.7.
> **Everything here is sourced.** Each claim carries an author, their leaderboard rank at the time,
> a date, and a URL. Tags: `[HOST]` = Kaggle staff/organizer · `[PARTICIPANT]` = competitor claim,
> often with their own measurements · `[OURS]` = our inference, not sourced.
>
> **Treat participant claims as evidence, not gospel.** Several have been independently replicated
> (noted where so); a few contradict each other (noted where so).

---

## 1. Leaderboard & field size

**Participation (2026-08-23):** 15,041 Entrants · 6,486 Participants · **6,060 Teams** · 11,431 Submissions.

**Top 30:**

| # | Team | Score | Last sub |
|---|---|---|---|
| 1 | Ryo Hasegawa | 3133.7 | 5d |
| 2 | Subramanya N | 3020.2 | 5d |
| 3 | Crop Dusta | 2972.4 | 10h |
| 4 | MiMi | 2940.9 | 2d |
| 5 | Arman Tuganbaev | 2938.6 | 5d |
| 6 | Kaito Fukami | 2913.3 | 2h |
| 7 | ActiveMusyoku | 2888.4 | 1d |
| 8 | Izzoudine Mohamed KANTA | 2884.5 | 4d |
| 9 | Kobe BRYANT | 2876.7 | 2d |
| 10 | peikopon | 2828.9 | 4d |
| 11 | satoooh | 2827.3 | 6h |
| 12 | カワシギ | 2819.4 | 6d |
| 13 | Kaan Dınız | 2790.1 | 2d |
| 14 | Sarthak Sharma | 2786.4 | 1d |
| 15 | fufufukakaka | 2782.6 | 1d |
| 16 | Napier1550 | 2775.7 | 2h |
| 17 | Lucien de Rubempre | 2772.3 | 3d |
| 18 | Ömer Faruk Yüce | 2771.0 | 3h |
| 19 | Egor Trushin | 2765.2 | 3h |
| 20 | Xiaowenhao404 | 2742.1 | 3h |
| 21 | ReCurSiON | 2737.4 | 9d |
| 22 | tetsuya | 2735.4 | 1d |
| 23 | XW | 2727.2 | 8h |
| 24 | Victor @ Tufa Labs | 2720.3 | 4d |
| 25 | Wiz | 2718.5 | 2d |
| 26 | SaiKushal185 | 2711.2 | 5h |
| 27 | shiiin9 | 2700.3 | 1d |
| 28 | StackKnight | 2698.6 | 3d |
| 29 | QQ Farming | 2695.6 | 16h |
| 30 | ebisu_ya | 2694.5 | 14h |

**Scale:** Elo-style; **a new submission starts at 600**. Rank 1 = 3133.7, rank 49 = 2629.1 — the whole
top 50 spans ~505 points, and **ranks 10→30 span only 134 points**. Per the #1 player, residual noise
is ±25–50 even after 200 games, so **the top ~15 are statistically indistinguishable.**

**Medal thresholds** (Kaggle standard for 1000+ teams, at 6,060 teams):
Bronze ≈ top 10% ≈ **rank 606** · Silver ≈ top 5% ≈ **rank 303** · Gold ≈ top 10 + 0.2% ≈ **rank ~22**.
Prizes: top 10 only, $5,000 each.

---

## 2. ⭐ The rating system — how the ladder actually works

**Source:** Ryo Hasegawa **(1st)**, "1st Place Currently - Submission Strategy for beginners",
4 days ago, 51 votes — https://www.kaggle.com/competitions/kaggriculture/discussion/736219 `[PARTICIPANT]`

This is the highest-value post in the forum. Verbatim:

> "A new submission starts at 600 and is ~90% converged after ~60 games, usually within the first ~5 hours. New submissions initially play ~15 games/hour, then slow to ~1–2/hour."

> "After that, the score grows only logarithmically—roughly +50–70 per 100 games, or per 3–4 days—and residual noise remains around ±25–50 points. **Differences of only a few dozen points are more likely luck than skill.**"

> "**The live leaderboard is not the final ranking.** … Your live rating's history, its lucky start, and its 'age' count for nothing at the end—only how your last 2 submissions actually fare against the field."

> "Only your 2 most recent submissions are active, and each new submission starts again at 600. Re-submitting an unchanged bot to 're-roll' its trajectory only moves the live number (and costs you the older copy); it changes nothing about the final ranking. **Submit only genuine improvements.**"

> "The score counts wins and losses only and matches you against opponents near your current rating. **Optimize win rate against the bots around you, not average coin totals.**"

Rating mechanics:
> "The update factor K is large at first and shrinks as the number of games, n, increases: roughly **K ≈ 200·e^(−n/26)**, plus a small floor."
> "the median curve is close to **μ(n) ≈ a + b·ln(n)**. Here, b depends mainly on your win rate (~50–190 in my fits), while a reflects the luck of your first ~40 opponents (approximately ±130 in my fits; others in this thread report byte-identical copies ending 300–1400 apart…)"

Convergence table (verbatim):

| games n | share of 400-game trajectory | spread (≈ ±1 SD) | time since submission |
|---|---|---|---|
| 20 | ~60% | ±160 | ~1.5 h |
| 40 | ~80% | ±140 | ~3 h |
| 60 | ~87% | ±105 | ~4–5 h (end of burst) |
| 96 | ~92% | ±80 | ~1 day |
| 150 | ~95% | ±65 | ~2–3 days |
| 200 | ~97% | ±50 | ~4 days |
| 300 | ~99% | ±35 | ~1 week |

On offline evaluation — **this is the most actionable paragraph in the competition:**
> "Optimize win probability against the bots near your target rating, not mean coin totals. **A bot that wins 70% of its games by small margins outrates one that wins 60% by huge margins.** Most 'improvements' that raise your average coin total but increase variance are rating-negative."
> "Judge a change by its win rate against each strong opponent, not by the pooled mean. A change that adds +3k coins on average but turns two wins into losses against the #2 bot is a loss on the ladder."
> "The opponents that matter are the ones that will be on the ladder during the two post-deadline weeks. The population drifts … **re-check your agent against the current meta every week or so.**"

**Contradicting measurement** — Syed Asad Ali (481st), same thread `[PARTICIPANT]`:
> "From (updated − initial)/(actual − expected) on our own episodes, **K doesn't decay smoothly**: it sits flat at ~220 for the first ~10 games, then cliffs to ~45–55 by game 20, and floors at ~8.5 by game 80. Your 200·e^(−n/26) is gentler in the middle."
> "Two of our fresh submissions were at ~98% of their current rating by game 60 and the burst rate was 16–17 games/hour for the first 4 hours."

### Path dependence — the ladder is noisy in a big way
**Rayk Kretzschmar (53rd)**, 14 days ago, 26 votes — https://www.kaggle.com/competitions/kaggriculture/discussion/734000 `[PARTICIPANT]`
> "I submitted two byte-identical agents approximately two hours apart. The first submission is currently around 1700, while the second, submitted 2h later, has climbed >3000. … A gap of roughly **1400 points between identical agents** suggests that the current rating may be highly path-dependent."

- Victor Mercklé (25th): "'In particular, early losses seem to make subsequent climbing extremely slow.' I think this is the biggest factor. … Also a big part of the pool currently is stale agents (for the old engine)."
- evnchn (1174th): "I have a gap of 300 for identical agents… I've seen 3k drop into 2k over the span of 4 days." And on notebook claims: "all the false 'this notebook gets a 3k score' in the Code section, which is **wildly over-claimed**."
- Belati Jagad Bintang Syuhada (1085th): "once the competition's submission deadline has passed, all of the agents will start over from 600 ELO and have to climb back up."

**[OURS] Implication:** live rank is a weak signal. Do not chase it. Build offline evidence, submit only real improvements, and remember the final board is a fresh Bradley-Terry fit.

---

## 3. ⭐⭐ The objective function: win probability, not money

**Source:** destbreso (617th), notebook "Wins, not money" —
https://www.kaggle.com/code/destbreso/wins-not-money `[PARTICIPANT]`
Fitted on **32,570 public completed episodes / 267 submissions with ≥30 episodes.**

**Does margin buy rating?** Median rating gained by a win, narrowest vs widest margin quartile:

| games played | narrow | wide | ratio |
|---|---|---|---|
| 1 to 14 | +23.49 | +74.78 | **3.2x** |
| 15 to 39 | +16.38 | +14.22 | 0.9x |
| 40 to 99 | +5.47 | +5.69 | 1.0x |
| 100 or more | +4.40 | +4.14 | 0.9x |

> "The effect exists only in a submission's first fourteen games and is gone by its fifteenth. … A new submission's rating moves by a median of **54.8 points per game** and a seasoned one by **4.3**."
> "**The margin buys nothing directly.** It is worth measuring … because it estimates the same thing with far less noise; it is not worth maximising."

**Proposition 2:** "Under the location-scale assumption, maximising Pr[M>0] is equivalent to maximising **μ/σ**, whereas maximising E[M] maximises μ. The two orderings coincide … if and only if σ is constant across policies."
> "the two objectives disagree exactly when a policy buys extra mean at a more than proportional cost in dispersion. **Growing a farm larger does precisely that**, because a larger farm's revenue depends more heavily on a market whose depth it is itself consuming."

**Corollary 3 (signed risk preference) — the actionable rule:**
> "Additional dispersion increases the probability of winning when **ℓ + μ < 0** and decreases it when **ℓ + μ > 0**. A player who expects to finish behind should seek variance; one who expects to finish ahead should avoid it."
> "**ℓ is observable at every single turn, because both banks are public.** The adjustment flips sign at ℓ+μ = 0, so a risk term applied with a fixed sign is wrong half the time."

Calibration: `Pr[win] = Φ(μ/σ)` fits public episodes at **MAE 0.068**.

**[OURS] This is the single most important strategic insight available.** Both banks are public every
turn. Almost nobody is using the sign-flip. An agent that plays safe when ahead and takes variance when
behind is strictly better on the ladder than one that always maximizes expected money.

---

## 4. ⭐⭐ The economy — what actually pays

### 4.1 The town's appetite sets the price, not the price table
**Luka Duvanov (3611th)**, 12 days ago — https://www.kaggle.com/competitions/kaggriculture/discussion/734412
Notebook: https://www.kaggle.com/code/nekkon/strawberry-pays-24x-what-the-price-table-says `[PARTICIPANT]`

Season revenue if sold into town demand ("into the hole") vs dumped flat:

| product | base | town eats | into the hole | dumped flat |
|---|---|---|---|---|
| STRAWBERRY | 120 | 426 | $100,445 | $4,173 |
| MILK | 160 | 327 | $86,662 | $6,432 |
| WOOL | 200 | 228 | $54,340 | $8,097 |
| WHEAT | 25 | 525 | $21,152 | $10,813 |
| TOMATO | 60 | 228 | $16,812 | $7,861 |
| CARROT | 35 | 327 | $13,246 | $6,904 |
| EGG | 50 | 228 | $12,972 | $9,658 |
| MELON | 250 | 30 | $8,184 | $7,416 |

> "**Strawberry … is worth 24× more sold late than sold early, and it is the biggest market in the game.** Melon, the most expensive, is the smallest — no shop buys melon."
> "**Per tile, animals dominate and strawberry does not.** A strawberry plant yields four units in seventeen days; a cow yields 1.5 milk a day for twenty-two days once you count the CARE bonus, plus a free fertilizer daily. Allocating tiles greedily by marginal revenue, **the first fifteen are all cows and sheep**, melon enters around tile sixteen, and strawberry only earns about thirteen tiles out of a hundred. **It is the best thing to sell and a mediocre thing to grow.**"
> "**Labour is not a constraint.** HIRE costs fib(n) and the counter resets every morning, so ten hands cost $143 for 230 extra actions. **What is a constraint is walking:** my first agent spent **83% of all unit-turns moving**, because it recomputed each hand's target every turn and they thrashed. **Making a unit finish the tile it stands on before moving** — FEED, CARE, HARVEST, COLLECT_FERTILIZER are all done from the same square — took that to 55% and **roughly tripled the final bank.**"

**Independent confirmation** — destbreso (617th), same thread:
> "I get the same nine numbers you do: 525 wheat, 426 strawberry, 327 carrot and milk, 228 tomato, egg and wool, 30 melon, 0 fertilizer. … shops unlock at the end of day d when (d+1) % 3 == 0 and cap at 8, which comes to **132 shop-instance-days over a 30 day season**."
> "a closed-form ceiling on the total money in an episode: about **$703k at median demand for both players combined**, and across 32,570 public episodes none exceeds it, with the best game on record collecting 48% of it."
> "`_daily_refresh_animals` sets fertilizer_available = True on every surviving animal every day whether or not you fed it … so the stream is worth about **$2,900 a season against $1,300 to $1,760 for the milk, eggs or wool** the animal is named for. **Pricing fertilizer as a by-product undervalues livestock roughly threefold.**"
> "Fertilizer is the one product with a town drain of exactly zero … every unit prices on the glut branch, about $98 and degrading slowly."
> "Selling harder costs me about $4k and costs the opponent about $11.8k in my own measurements."

### 4.2 Profit per tile-day at base prices
**Georgy Mamarin (2569th)**, notebook "Kaggriculture, Visualized: What Every Crop Pays", 80 votes —
https://www.kaggle.com/code/georgymamarin/kaggriculture-visualized-what-every-crop-pays `[PARTICIPANT]`

| crop | seed $ | tile-days | units | base | revenue | profit | profit/tile-day |
|---|---|---|---|---|---|---|---|
| MELON | 80 | 10 | 6 | 250 | 1500 | 1420 | **142.0** |
| CARROT | 20 | 3 | 3 | 35 | 105 | 85 | 28.3 |
| STRAWBERRY | 100 | 16 | 4 | 120 | 480 | 380 | 23.8 |
| WHEAT | 10 | 4 | 4 | 25 | 100 | 90 | 22.5 |
| TOMATO | 50 | 11 | 4 | 60 | 240 | 190 | 17.3 |

> "the humble carrot turns over in 3 days, which makes it **the best cash-flow engine of the early game**, and wheat's real job is animal feed."

**Animals + CARE (measured):**
> "Goose end of season: **+1,675 cared / +275 fed only**; Cow: **+4,635 cared / +635**; Sheep: **+5,575 cared / +375**"
> "a cared animal produces **1 + interval** units instead of 1, once it settles: double for a goose, triple for a cow, quadruple for a sheep. … **The longer the gap between production days, the more time the counter has to build, so care is worth most on the animal that pays out least often.**"
> "an uncollected cared goose is already at its 4-unit cap on its first production day and earns nothing after that."

**Fertilizer asymmetry:** "wheat physically cannot reach its 6-unit cap without fertilizer (1 base + 3 watered window days = 4 units max), while melon hits its cap on water alone."

**Market slippage (measured):**
> "melon hits the $1 floor after **158 units net-sold**. Wheat after 400 units still sells at $20."
> "A full shed of 100 melons, sold in one go: **$21,721 kept out of the $25,000 the first price promised (87%)**. Keep going to 200 and it is **$26,527 of $50,000 (53%)**; melon number 200 sells for $1."
> "**sales at the $1 floor do not even add to market inventory, so dumping at the bottom is pure loss.**"

**Land:** `LAND_ORDER = ["NE", "SW", "SE"]` at $1,000 / $2,000 / $4,000 — fixed order, "the only land
decision you actually make is **when** to buy." "Even the $4,000 quadrant pays back in under a week at a
modest $25/tile-day."

**Labor:** "Five hands cost 12 coins and add up to 115 turns … the most complete public baseline hires
**seven every day**." But: "**Extra hands are extra actions, not extra judgement.**" — hands wired to run
the same job list as the farmer *did worse* (44 plantings in one day, −58 coins on seed 0).

**Ladder yardstick:** "Ladder median bank: **85,048 coins**, across 2949 teams."

### 4.3 Shop draw distribution
**Georgy Mamarin** + **Yusuke Hayashi (210th)** `[PARTICIPANT]`
> "Eight shops, uniform with replacement, so the median season opens **5 distinct types out of 8**. Median season demand: wheat 504, strawberry 396, milk 288, carrot 270, and 180 each for tomato, wool and egg."
> "Wool sits on one menu, so **34% of seasons have no wool buyer at all**. Carrot is zero in 10% of seasons."
> "the sheep herd's season median was about **$39k with a yarn store and about $11k without**, and among those three herds **the cow herd ranked first in 70% of towns**."
> "**the clearest adaptive margin is not the herd you pick — it is what you sell and when**, which is the thing a replayed trajectory cannot adjust."

---

## 5. ⭐⭐ Measurement methodology — READ BEFORE BENCHMARKING

**The single biggest trap in this competition.**

**Yusuke Hayashi (210th)** — https://www.kaggle.com/competitions/kaggriculture/discussion/732613
Notebook: https://www.kaggle.com/code/yhay81/your-seed-does-not-fix-the-town `[PARTICIPANT]`

> "**The shop draw is not fully exogenous — it shares an RNG stream with weed spawning**, so it moves with how many empty tiles each farm has."
> "At `_end_of_day` the engine builds `random.Random((seed * 1_000_003) ^ day)`, calls `_spawn_weeds` for player 0 and then player 1, and only afterwards draws the shop. `_spawn_weeds` consumes one `rng.random()` per empty unlocked tile. **So the shop is drawn at a stream offset equal to the two farms' combined bare-tile count that evening.**"
> "Over 12 seeds the shop schedule differed on 12/12, and player 0's final bank differed on 12/12, with all 720 of player 0's actions recorded and identical across each pair."
> "Reordering market orders only (strawberry sell batch 3 to 4): the same town on 16/16 seeds, paired sd 1 … **Dropping one hired hand (five to four): the same town on 0/16 seeds** … paired sd 1,322, and detecting the observed +342 effect at 80% power takes roughly **77 seeds**."

**Georgy Mamarin** confirms independently:
> "**The shop draw is not independent of play.** … Same 12 seeds, two different bots: the unlocked shop list differed on all 12. Two versions of my own bot: identical on all 12. **Editing your own bot usually keeps the town as a control. Benchmarking against somebody else's loses it.**"
> "one shared seed list → standard error 8.67 / fresh seeds for each → standard error **584.20 (67.4x wider)**"
> "seeds 0-2, seat 0 against seat 1: 8,554 vs 8,554, 9,394 vs 9,394, 8,755 vs 8,755 → **same both ways, so one seat is enough**" (for his deterministic bot vs the built-in starter)

**[OURS] Rules that follow — bake these into every experiment:**
1. **Always paired same-seed A/B.** Unpaired is ~67× noisier.
2. **If your change alters tile occupancy (hands, land, crop count), the town draw changes too** — it is no longer a control, and you need ~77 seeds to detect a few-hundred-coin effect.
3. Changes that only reorder market actions keep the town fixed → cheap to test.
4. Benchmarking against *someone else's* bot loses the town as a control.

---

## 6. ⭐ The current meta — what the top of the board is actually doing

### 6.1 It is an open-loop replay tape
**onlysmrtsumx (1112th)**, 18 days ago — https://www.kaggle.com/competitions/kaggriculture/discussion/733055 `[PARTICIPANT]`
> "the best meta/approach is **not a dynamic agent**. But rather a fixed asset development strategy. That completely ignores/disregards the market, and achieves an **81% win rate**."
> "The meta hard-codes **LAST_CARE_DAY=27** and a **day-29 liquidation**."
> "the **top 150 Players are all Byte Identical to either Variant 1 or Variant 2** of the current meta."

Same author, in thread 732902:
> "I did an analysis on the most recent 50 games, for the Top players … **Turns 1–51 are byte-identical across 13 player-instances and 8 different seeds**, the same actions and same quantities despite different prices, cash, and opponents. Their crop mix doesn't change even when the wool shop unlocks on day 9 vs day 24. **They are not price-responsive at all.**"

**Russell Kirk (5823rd):** "the best strategy currently is 'I WILL DO THIS NO MATTER WHAT HAPPENS.' **They don't adapt to their opponents at all.**"

### 6.2 The public meta agent (what to study, with a caveat)
**boatlee**, "V16-RC5 | High-Score 8C/4S Premium Market Lead", 239 votes, public score 2913.3 —
https://www.kaggle.com/code/boatlee/v16-rc5-high-score-8c-4s-premium-market-lead `[PARTICIPANT]`

It is a **replay tape, not a reasoning agent**: `_ACTIONS` is a zlib+base85-compressed list of 720
pre-baked `{farmer, hands, market}` dicts, replayed by step index.

> "The production schedule was **reconstructed from three publicly available Kaggriculture replays of Nikita Lugovoy's high-ranking submission 55440039**: episodes 92165990, 92185587, and 92223213. Across those traces, the field schedule was identical and the market schedule matched at **99.91%** of decision steps."

The route it encodes:
> "expands to **three unlocked quadrants**; reaches **4 SHEEP** immediately and **8 COW** by step 192; maintains a mixed WHEAT, STRAWBERRY, and MELON crop program; coordinates daily HIRE, FEED, CARE, harvest, and fertilizer work; releases produce in repeated **premium-goods market waves**."

Livestock schedule: `step 0: COW 1, SHEEP 4 | step 120: COW 2 | step 161: COW 4 | step 168: COW 6 | step 192: COW 8 | step 719: COW 8, SHEEP 4`

Its only two adaptive additions on top of the tape:
1. **Weed repair** — if a unit stands on a WEED and its scripted action is `BUILD_PASTURE`/`PLANT`, substitute `DIG`, replay the intended action one step later, re-sync via `_WEED_REPLAY_STEPS = 8`.
2. **Premium market front-run** — for `('MELON','MILK','STRAWBERRY','WOOL')`, if next turn's tape has a SELL and this turn has zero town demand and the shed has stock, move part of the sale one turn earlier.

Its embedded shop→product map (a useful reference):
```
BAKERY: (EGG, WHEAT)          | PIZZA_SHOP: (MILK, TOMATO, WHEAT)
BRUNCH_SPOT: (EGG, WHEAT, STRAWBERRY) | YARN_STORE: (WOOL,)
ICE_CREAM_SHOP: (STRAWBERRY, MILK, WHEAT) | PET_CAFE: (CARROT,)
SMOOTHIE_SHOP: (STRAWBERRY, MILK) | FARMERS_MARKET: (WHEAT, CARROT, TOMATO, STRAWBERRY)
```
Town demand calc it uses: `demand = 1 if item != FERTILIZER and step % 24 == 0`; plus if `step % 4 == 0`,
`+2` for single-product shops, `+1` otherwise.

> `[OURS] ⚠️ ETHICS + STRATEGY NOTE.` Copying a compressed action tape reconstructed from another
> competitor's replays is *legal* under §2.11 (replays are public), and it is what much of the top 150
> is doing. **We are not doing that**, for two reasons. (1) Strategically it is a dead end: a tape cannot
> adapt, the final Bradley-Terry board runs 2 weeks against a drifting field, and a tape's edge is exactly
> the thing every other copier also has. (2) It produces nothing you can honestly claim as your own work —
> which defeats the entire point of entering. **Read these agents as intelligence about the route; write our
> own agent.** There is even an active thread (`736568`) about competitors deliberately obfuscating replays
> to defeat copying.

### 6.3 Open questions the meta has NOT solved
- **Nobody adapts to the opponent.** hengck23 (1346th): "**Most solutions so far are not really fighting against opponent agent yet.**"
- **Nobody is price-responsive** in the opening 51 turns.
- **The 4th quadrant is contested.** Steve421471 (109th): "I've tried it but the ROI isn't there… I have seen someone near the top of the leaderboard use it and **leave the outer perimeter empty to reduce walking**." Victor Mercklé (24th): "My max money strat did use all 4 quadrant, however **almost everyone will dump the market before you if you do that**."
- **Selling order matters.** Russell Kirk: "If you both are trying to sell the same thing, both your profits will suffer -- and **the first to sell gets the better price**."

---

## 7. RL / ML attempts — the honest scoreboard

Threads 734952 (NNMax, 21st) and 736567 (dzjiann, 29th). `[PARTICIPANT]`

| Approach | Reported result |
|---|---|
| Rule-based (public meta) | **~150k** bank |
| Hybrid rule-based + PPO (Phương Doan, 1588th) | **~100k** |
| Pure self-play PPO in JAX on TPU (Shubham Phapale) | **20–22k** — "gave up :(" |
| PPO (Mahog, 5666th) | "stuck around 20k" |
| PPO (LuvGoel, 2131st) | "stuck under **5k**" |

Failure modes, verbatim:
- **Cold start / homogeneous replays** — dzjiann (29th): "I tried behavior cloning first, and although there are plenty of available replays, **most of them are highly similar**."
- **Generalization across plots** — "the agent learned to manage the first plot of land reasonably well, but it failed to generalize … successful harvest rate was only around **20%–40%**. … from the agent's perspective, **buying additional land appeared to have negative expected value**. As training continued, the policy gradually stopped purchasing land altogether."
- **Gradient cancellation** — Michael Timbs (66th): "**Swapping one crop to another or swapping to a different animal just completely tanks the entire rest of the play and destroys any gradient.**"
- **Scale required** — Sahaj Deep Singh (1783rd): "you realistically need at least **10M+ games** of experience."

**Meta-level RL (selecting among strategies) works better** — dzjiann, thread 736439:
Held-out outcome-prediction accuracy: majority baseline 54.2% → opponent only 56.5% → opening branch only
56.5% → **opponent AND opening branch 67.5%**.
Reported **intransitive cycle** over 960 games: "Public B85 vs Andrews 2883 → 30-2; Andrews 2883 vs Kaito
v35 → 21-11; Kaito v35 vs Public B85 → 24-8." → "**the pairwise payoff matrix is more informative than
average win rate.**"

**[OURS] Conclusion: do not attempt end-to-end RL.** The evidence is unanimous and includes people with
TPUs. A strong rule-based/scheduling agent with selective adaptation is the tractable path.

---

## 8. Engineering discipline — from a top-10 player

**Kaito Fukami (6th)**, 13 days ago — https://www.kaggle.com/competitions/kaggriculture/discussion/734212 `[PARTICIPANT]`
> "In Kaggriculture, one inventory bug, seat mismatch, illegal queue, or slipped worker action can destroy an otherwise strong strategy. **Meticulous engineering is part of strategic strength.**"
> "My loop is: **Real losses → identify one failure mechanism → build challengers → test multiple teams and both seats → reject most candidates → freeze the winner → test on later episodes**"
> "I also retain representative strategies from earlier stages. **Optimizing only against the latest Top-30 can lose to older meta generations still active on the leaderboard.**"
> "The better prompt is not: *Build the optimal agent.* but: ***Where does this agent lose, and what experiment could disprove the proposed improvement?***"
> "**The submitted agent may be open-loop, but the research process must be closed-loop.**"

**wenyuan Guo (936th)**, thread 733173: "the strongest long-run design is a **static production backbone with selective, hysteresis-based adaptation** for weeds, hiring order, market pressure, and terminal sales."

---

## 9. Host announcements & balance changes

| Date | Who | What |
|---|---|---|
| 17d ago | **Bovard Doerschuk-Tiberi, KAGGLE STAFF** — [733431](https://www.kaggle.com/competitions/kaggriculture/discussion/733431) | "we're reducing the overall demand for products from the town"; "shops will now be sampled **WITH replacement**"; Town Center cut from 2x/day + late multipliers to **1x/day flat**. PR [#1394](https://github.com/Kaggle/kaggle-environments/pull/1394). "**upgrade to >= 1.32.6**" |
| 9d ago | **Bovard, KAGGLE STAFF** — [735311](https://www.kaggle.com/competitions/kaggriculture/discussion/735311) | hinge scarcity curves for **eggs, tomatoes, carrots**: "their price will increase significantly if there is a large shop demand and no production." Expected to trigger: tomatoes 50% / carrot 26% / eggs 22% of games. PR [#1399](https://github.com/Kaggle/kaggle-environments/pull/1399). "**This should be the last change, excepting game breaking bugs.** … update to >=1.32.7" |
| 23d ago | **María Cruz, KAGGLE STAFF** — [731215](https://www.kaggle.com/competitions/kaggriculture/discussion/731215) | Final evaluation: 2 weeks of post-deadline episodes, then "a single **Bradley-Terry Tournament**, which will determine the final leaderboard rankings. … we believe this change reduces any 'hot streaks'" |
| 24d ago | **Bovard, KAGGLE STAFF** — [731587](https://www.kaggle.com/competitions/kaggriculture/discussion/731587) | **Daily Top Episodes dataset**: "Each day we order episodes by the average rating of the agents playing … download up to 20 GB of replays and make a new daily dataset! … helpful for everyone trying IL/BC, bootstrapping RL, or just gathering statistics." → https://www.kaggle.com/datasets/kaggle/kaggriculture-episodes-index |

**Independent verification of the 1.32.7 change** — destbreso (617th) `[PARTICIPANT]`:
> "games cross the new knee for tomato **55.0%**, carrot **28.3%** and egg **25.8%**, against your 50 / 26 / 22."
> "**Carrot's below_target also moved, 0.20 to 1.00, which the post does not mention**"
> "Holding agent, seed and opponent fixed and switching only the build moved **118 of 224 banks and changed 0 of 224 winners**."

Luka Duvanov's recomputation: CARROT $13,246→$15,614 (+18%); TOMATO +0.2%; EGG unchanged.
> "**The hinge alone is worth minus one dollar. The whole move is the below_target change.**"

---

## 10. Public code & notebooks

https://www.kaggle.com/competitions/kaggriculture/code?sortBy=voteCount

| Title | Author | Votes | Score | Type |
|---|---|---|---|---|
| 📌 Kaggriculture: Getting Started | bovard (Kaggle) | 766 | 270.2 | **Official starter** ("Melon Maxxer") |
| V16-RC5 \| High-Score 8C/4S Premium Market Lead | boatlee | 239 | 2913.3 | ⭐ Public meta tape |
| 25/27 Strict-Future \| v27 Midgame Meta Reset | kaitofukami | 170 | 2149.5 | Agent (rank-6 player) |
| 🌾Adaptive Farming Strategy | tetsutani | 131 | 1982.4 | Agent |
| Kaggriculture \| Hamburger 🍔 | romantamrazov | 128 | 1421 | Agent |
| 15/16 Strict-Future \| v25 Meta Reset | kaitofukami | 116 | 2905.7 | Agent |
| Kaggriculture: Structured Economic Policy | pilkwang | 97 | 962.5 | Agent/analysis |
| Kaggriculture: Findings from Zero to Top Meta | raykkretzschmar | 96 | 2837 | Agent + writeup |
| Kaggriculture Rank Your Agent | raykkretzschmar | 92 | 2563.4 | ⭐ Tooling |
| Kaggriculture \| Multi-Route Farming Agent | flexonafft | 86 | 2290 | Agent |
| **Kaggriculture, Visualized: What Every Crop Pays** | georgymamarin | 80 | — | ⭐⭐ **Best economy guide** |
| Kaggriculture: What the Top Farms Do — a Live Meta | cjlcjlcjl | 74 | — | Meta analysis |

⚠️ **Notebook "Public Score" fields are widely regarded as inflated/path-dependent** (evnchn, §2).

**The official starter** (`bovard/Kaggriculture: Getting Started`) is **"Melon Maxxer"**: buys one melon
seed at a time, walks to nearest open tile, plants/waters/harvests, sells only when
`melon_price >= SELL_THRESHOLD = 200`. Scored `reward=6099.0` vs random. Its stated flaws:
> "It never hires farm hands or buys more land … It only grows melons … It never fertilizes its plants … When it does sell, it dumps the entire inventory in one order, which can crash the melon price below the threshold partway through the sale."

`[NOTE]` That notebook writes `submission.py`, **not `main.py`** — a known documentation trap.

---

## 11. Datasets & external resources

**Engine (source of truth):**
- https://github.com/Kaggle/kaggle-environments
- `kaggle_environments/envs/kaggriculture/kaggriculture.py` — the interpreter (~1,000 lines).
  Contains `MARKET_PARAMS`, `CROPS`, `SHOPS`, `TOWN_CENTER_PRODUCTS`, `LAND_ORDER`, `HINGE_GAIN = 8.0`
- PR [#1394](https://github.com/Kaggle/kaggle-environments/pull/1394) (→1.32.6), PR [#1399](https://github.com/Kaggle/kaggle-environments/pull/1399) (→1.32.7)

**Replay datasets:**
- Official daily: https://www.kaggle.com/datasets/kaggle/kaggriculture-episodes-index (CSV contains download URLs)
- Community: `georgymamarin/kaggriculture-episodes`; destbreso top-10 replay streams

**Key community notebooks:**
- https://www.kaggle.com/code/georgymamarin/kaggriculture-visualized-what-every-crop-pays
- https://www.kaggle.com/code/nekkon/strawberry-pays-24x-what-the-price-table-says
- https://www.kaggle.com/code/yhay81/your-seed-does-not-fix-the-town
- https://www.kaggle.com/code/destbreso/wins-not-money
- destbreso's series: `a-dna-test-for-agents`, `dissecting-the-top-two`, `everyone-is-playing-the-same-opening`, `six-checks-before-you-waste-a-submission`, `kaggriculture-know-your-noise`

**Discord:** discord.gg/kaggle — "Discord Competition Channels are **Not Monitored by Staff**"

---

## 12. Synthesis — where the edge is

**[OURS]** Reading all of the above together, the field's blind spots are:

1. **Nobody uses the public bank differential.** Both banks are visible every turn, and destbreso proved
   the optimal risk posture *flips sign* on `ℓ + μ`. Almost every top agent is a fixed tape that cannot
   respond to being ahead or behind. **This is the largest unexploited edge in the competition.**
2. **Nobody adapts selling to the actual shop draw.** The town is 34% likely to have no wool buyer,
   10% likely to have no carrot buyer, and "what you sell and when" is the *only* adaptive margin a
   replay tape structurally cannot copy (Yusuke Hayashi's words).
3. **Walking is the real resource.** 83% → 55% unit-turns-moving tripled one competitor's bank. A third
   is reportedly the floor. Routing/scheduling is a classic search problem and it is under-optimized.
4. **Fertilizer is underpriced ~3× by the field** and has *zero* town drain (so it always sells on the
   glut branch, ~$98 and slowly degrading).
5. **The final board is a fresh Bradley-Terry fit against a drifting 2-week field.** Beating today's
   top-30 is not the same as beating the October field. Keep older meta generations in the test set.

**Where the edge is NOT:** end-to-end RL (unanimous failure), copying the tape (no adaptation, no
ownership), or chasing live rating (±50 noise, up to 1400 path-dependence).

## 13. ⭐⭐ Top-of-ladder anatomy — official daily dump, 2026-08-27 (top 120 games)

**[OURS]** Scanned the 120 highest-avg-score episodes of the official daily dump
(`kaggle/kaggriculture-episodes-2026-08-27`, in-zip manifest is sorted by avg_score desc; ~3070
avg ≈ the 2,900+ band). Method: exact money-delta revenue attribution + tile-count timelines
(scan_top_dump.py / rps_analysis.py / dusta_decode.py in the session scratchpad). Order counts
are UNUSABLE — top teams spam ~284-310 HIRE orders per game as silent no-ops; real hand counts
come from `farms[i]["hands"]`.

**The elite profile (games ≥5 in sample):** median banks 81-104k; **every team ends at 3
quadrants** (nobody buys SE — consistent with our two rejections); final hands 8-12; openings are
near-deterministic per team (the "S4C0-mel7str2-whe11" family is shared by ≥6 different teams —
the cloned meta-tape).

**Crop Dusta (#1, 28W-8L in sample, median 103.8k) decoded — 36 games:**
- **The economy is a wheat plantation.** WHEAT is their top revenue product: $57k-121k per game
  (money-delta attributed), from a 13-wheat opening scaled all game across 3 quadrants, worked
  by hands ramping 4 → ~9-10 (day 10) → 12 (day 15) in every single game.
- **Conditional tomato: 10/36 games, ALWAYS at day 17 exactly,** at tomato price 69-80 two days
  prior, planting 11-22 at once (8W-2L fired). By day 17 the strawberry ramp is done, so the
  displacement cost that kills early tomato speculation is gone.
- **Conditional carrot: 23/36 games, ALWAYS day 22-27,** expanding 0 → 8-55 concurrent carrots at
  carrot price 43-66 (21W-2L fired). Reading: endgame tile conversion — carrot matures in 3 days
  at base $35 vs wheat 4 days at $25, so freed premium tiles convert to carrots while the carrot
  market still has demand.
- **Conditional goose: 10/36 games, day 7-12, at egg price 50-53 = AT base** (9W-1L fired). The
  trigger is therefore the egg OUTLET drawn (BAKERY/BRUNCH_SPOT), not price scarcity. 1-10 geese.
- Adoption across all 240 elite seats: tomato ever planted 30/240, geese 28/240, carrot >12
  expansions ~60/240 — **conditional play exists at the very top but is thin**; the middle of the
  top-150 (our band) has none of it. Our reactive-hinge line (v21) is the right race.

Candidates derived: v23a (wheat factory day 18→12), v22c (tomato day-15/≥70 second trigger),
v22d (late carrot conversion), v22b (shop-triggered goose). See PLAN.md experiments.
