# EXECUTOR SPEC — v108 (fork/executor_layer.py on pipe16 base)

The one remaining door to the top-10 second half (all additive doors measured
shut — see PLAN Exp 126-128). Complete-by-construction late-game owner.

## Core decisions (each paid for by a falsification)
- **PERMANENT takeover from D_ON=22** (config; try 22 first, then 20/18).
  Never hand back → positional-tape law can't bite (tape never resumes).
  Before D_ON: parent action passes through 100% untouched.
- **Keep the parent's MARKET list** (PREDICT2/SHEDROOM/ORDERPRI2/liquidation
  are state-reactive and stay valid; they also place the tape's own HIREs →
  labor level ~11 hands preserved for free). Executor only APPENDS:
  BUY_SEED (carrot/wheat for replants), BUY_PRODUCT WHEAT if feed short
  (< animals×2 days), emergency SELL if shed projected > 95 at day end.
- **Replace ALL unit actions (farmer + hands) from D_ON.**

## The hourly loop (rebuild plan from live obs every hour — no stored plan)
Priority tiers, greedy nearest-unit assignment, one unit per task-tile:
1. FEED every unfed animal — needs carried wheat: chain = PICKUP WHEAT n at
   shed → walk → FEED each animal tile (1 wheat each).
2. CARE every uncared animal (biggest per-op payoff, engine-verified).
3. WATER every plant tile not watered_today (HARD RULE: everything, daily —
   weeds impossible, window ticks guaranteed).
4. HARVEST: plant tiles yield>0 & age≥2; animal tiles nearing cap
   (cow/sheep 6, goose 4) before tonight's production (CAPHARV logic).
5. COLLECT_FERTILIZER where available; FERTILIZE young wheat/carrot if
   carrying fert.
6. RECYCLE (d≤26): DIG inert (yield 0, age>6, any crop) → next hour PLANT
   CARROT (WHEAT fallback) — respect PLANT collective validation
   (Σ plant cmds per crop ≤ seeds held THIS turn); plant only ≤ h19 and
   only if tier-3 capacity today has slack (never plant what we can't water).
7. Cargo: h≥21 walk carriers to shed + DROP (midnight auto-drop = backup).
8. Leftover units: PASS in place.

## Known traps (all previously hit — do not repeat)
- unwatered new plant weeds SAME night (cuw starts at 1): tier 6 slack rule.
- PLANT over-request voids ALL plants of that crop that turn.
- hands respawn at center each morning (h0), expire midnight; farmer persists.
- PICKUP args: ["PICKUP","WHEAT",n]; FEED consumes carried wheat.
- moves: NORTH=y-1 SOUTH=y+1 EAST=x+1 WEST=x-1; pos=(x,y); tiles[y][x].
- ✅ ENGINE-VERIFIED (L132-139, L343-375): shed access = EXACTLY the four
  tiles (4,4),(5,4),(4,5),(5,5) on a 10-board (3 of the 4 start LOCKED —
  (4,4) is the NW one, always usable). DROP dumps the unit's WHOLE inventory
  (capped by shed room, excess DELETED from inventory — don't drop more than
  room!). PICKUP = ["PICKUP", item, n] (n defaults 1, capped by shed stock).
  Both are silent no-ops if not standing on an access tile.
- market append only, never reorder parent slots (ORDERPRI2 lockstep).

## Validation ladder (in order, stop at first failure and autopsy)
1. Fingerprint seed 102: unfed=0 all days, weeds=0, every-tile watered %,
   digs/replants counts, bank curve vs pipe16 day by day d20-29.
2. Fingerprint seeds 103-104 (cost-driver spread — mistake 17).
3. Gate A: h2h vs pipe16, 39 fresh seeds (4594-4632).
4. Gate B: vs tetsu 39 paired on 4398-4436 (baseline pipe16_tetsu in
   results/ab_metav4.jsonl, ab_sum <NEW> <BASE>).
5. Positive → D_ON sweep 20/18; negative → per-day bank-curve autopsy
   (which tier underperforms the tape: sells? harvest volume? care?).

## Success bar
Gate B ≥ +500 mean margin-diff or wins +3 flips net → submit-candidate
v108 as 2nd active. The top-10 reference: their d24-28 bank slope ≈
2x ours (gap ledger); even half of that ≈ +5k/game vs field.
