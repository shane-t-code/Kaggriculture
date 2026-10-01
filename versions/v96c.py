"""
main.py — Kaggriculture agent.  ENTRY POINT (must be at archive root, must be named main.py).

STATUS: v96c — BENCHED: -730±257 t=-2.85, own -814, flips +2/-4.  Even free-
labor CARE on floored-product animals nets negative here: the +1
units clog the shed and floor-dump.  WITH v96a's verdict this
closes the IDLE-TIER EMISSION design on this chassis: our
care_skip/water rules were already right for OUR economy — the
top's extra ops only pay inside THEIR economy.  The op-gap table
stands as measurement; remaining neutral lanes = fert throughput
38->62 (live-proven machine, friction list) and pickup/express
88 vs 207.  (was) CANDIDATE: v93d +
CARE-ONLY idle tier.  The one v96a organ with NO glut pathway.
(v93d layer:) PROMOTED.
GATE (78/leg, seeds 2740-2895, vs v92b): Amitesh +2,154±915 t=2.35
flips +22/−9 (wins 33→46, 42%→59% vs THE band-killer class) |
holdpx +2,291±1,046 t=2.19 own-bank +3,225 (78-0 saturated).
Pooled ≈ +2,223 t≈3.2 — strongest margin gate since v83a.
CONTENTS: v92b (fert window→26 + P prio + keep 8 + px gate 100)
+ tick-day PARITY application (no age-7/8 exemption), carrier-
first FERTILIZE pass right after the urgent tier, fert+pickup at
P_CHAIN, pickup threshold 1.  = Artyom's measured recipe (98%
on-tick / 96% watered-same-night / 1.85 ticks-per-op vs our old
0.8), production-reconciled.  Fingerprint: on-tick 83-96%,
watered-same 89-91%, coverage 44% (base 35%), unfed BETTER
(1.3-3.1% vs 8.4).  Occupancy changes (parity defers plantings).
(v92b layer:) STATUS: v92b — PROMOTED .  GATE
(4 blocks × 39 paired, seeds 2506-2661): ami reused +134 / ami
FRESH +1,547 t=1.48 flips +6/−4 / hold reused +351 own +1,496 /
hold FRESH +338 own +1,854 flips +1/−0.  POOLED n=156: +592±551
t=1.08, own-bank +578, flips +11/−10.  ALL legs non-negative +
fresh replication both tapes + live-decoded mechanism (coverage
36%→44-54%, field 70%, killers 83%).  = v92a + PRICE
GATE (FERT_STR_MIN_PX 100): the coverage machine runs only while
live STR px >= 100; below it = exact v89c (window 7-15, P_FERT,
keep 0, day cap 26) and the fert sells.  v92a blanket verdict at
n=39: wash both legs BUT own-bank split −1,248 flooded / +1,270
non-flooded → coverage is market-conditional; double into markets
worth doubling into.  (v92a layer:) v89c + STR FERT
COVERAGE COMPLETION.  Live decode (40 v89b + 40 v89c replays, both
x-rays, lb_2026-09-18): fert-covered STR production ticks 36% us vs
70% field / 83% band-killers = ~+40 u/game ~ +$4-6k forfeited — the
756-900 band's whole mean deficit.  Three compounding causes, one
mechanism: (1) FERT_CROPS STR max_age 15->26 (the (7,15) window
predates the v83a hold — tiles kept to d26-29 had their last 4-5
ticks uncovered BY DESIGN); (2) STR FERTILIZE rides at P_WATER (the
P3 tier measurably starves); (3) FERT_KEEP 0->8 (supply was sold out
from under the tasks); + day cap 26->27.  v89b/v89c live verdict:
SAME BOT (731 vs 723 = pairing mix: v89c drew ELEVEN 1200-2666
games incl Khanh-2628 x6, and beat 3 of them); transfer 14-for-14.
(was) STATUS: v89c — PROMOTED, SUBMIT-FLAGGED : v89b +
SHED_FORCE_SELL 80->92.  Gate: Amitesh no-harm +106±194 (latched
+243±452), 0 flips — waste-removal bar passed (live evidence: ~5
floor-units/game dumped at $1-3 with shed 80-94).  CONTAINS v89b's
dig guard + v87/v88 (express + chain).  = tonight's submission.
(orig:) v89b + SHED_FORCE_SELL
80->92 (the express-induced panic-dump fix; ~5 floor-units/game at
shed 80-94 measured live).  WOOL CHASSIS (v90a/b) FALSIFIED 5th and
FINAL time same day — fully functional (12 placed, fed, 3rd carrier
built) and still loses to BOTH the wool-mirror tape and Amitesh
(6/8 seeds each; the sheep bill guts the STR cohort).  The lane
needs Bharath's WHOLE economy (bought feed, no hands, matchup luck)
= a rewrite, not a dial.  (v90 experimental code NOT carried — v89c
is exactly v89b + this one constant; the 3rd-carrier split lives in
versions/v90b.py if the herd ever scales.)
--- v89b layer: ---
(was) STATUS: v89b — PROMOTED, SUBMIT-FLAGGED : STR
CRASH-BRANCH CONFIRM GUARD.  GATE: killer NULL (−10±143 — true
crashes still dig); holdpx tape (built from the live Samuel game
where we dug 27 tiles at ~$200) +169±115 / latched +387±260;
Amitesh −229±128 (its SCHEDULED late flood is the one class where
holding costs — accepted).  Local pooled ≈ wash BECAUSE local worlds
rarely arm the trap; THE DECISIVE EVIDENCE IS LIVE: 23/40 v88a games
dug 15-30 producing tiles at $150-260 (wins included; 5 losses in
this sample within the recovered range).  Digging a $200-producing
tile for a $10 wheat replant is value-destruction at the moment it
happens; the guard blocks it only when the live price contradicts
the crash forecast.  (original candidate header:)
GUARD (the real live leak) + late-hold dials.  Live v88a band-loss
trace: str_dead fired ~d25 and DUG 19 STR tiles/game AT LIVE PRICES
$164-221 (samples: 16@164, 29 tiles across d25-28 @ ~220) — the
crash projection counts our own doubled capacity (35-38 tiles, the
seed-cohort success) as supply and predicts crashes live towns
absorb.  v83a's 17-tile farms never armed it: THIS is why v87/88
tiles@d24 = 26.6 vs v83a's 33.6.  FIX: str_dead now ALSO requires
live price <= STR_DEAD_CONFIRM_PX (60) — a $200 market is not dead.
Plus v89a's dials (CONVERT 24->26, KEEP 34->38; byte-null vs tapes —
they bind live when str_dead stays off).  True-crash worlds
(px <= 60) keep the old behavior exactly.  GATE: Amitesh+infill
(str_dead rarely fires vs tapes -> expect small/no diff; the change
targets LIVE non-tape worlds — waste-guard bar: no-harm + the live
trace) fresh 1765+.
--- v88a layer: ---
(was) STATUS: v88a — PROMOTED, SUBMIT-FLAGGED : CHAIN
EVERYWHERE.  GATE at protocol-n for an occupancy-changing candidate
(78 seeds per live leg, 195 total): Amitesh 78 = **+2,433±976 t=2.49
flips +19/−10 (23→32 wins)** | infill 78 = +572±864 t=0.66 flips
+11/−15 (lottery-flat; first block's −926 erased by the second — 26
flips/78 = re-roll churn, decoded seeds incl. boom→yarn re-rolls) |
killer 39 = exact null BY CONSTRUCTION (chain already ran in
detonator games).  Pooled live legs ≈ +1,503/game.  The v82c
detonator-gate is overturned: its −8-flip evidence was decoded as
shop-draw lottery (3/3 biggest flips; own revenue UP in 2).
Fingerprint: STR@d9 17→23, caravan sold11 up to 58-64, unfed tail
mild (3/16 seeds 6.7-8.0%, mean +0.5pp — priced into the gate).
(prior CANDIDATE header:)
EVERYWHERE.  = v87b + the zero-walk feed-chain's _MEL_RACE gate
removed (slack guard kept).  The v82c detonator-gating is overturned
by archaeology: all 3 decoded Amitesh "damage" flips were shop-draw
re-rolls (own revenue UP in 2/3; ops/unfed identical), judged on a
n.s. margin.  The band chains CARE+COLL+FEED stops in EVERY class
(1.53 v 1.34 ops/stop = +311 ops/game, re-based on v83a live).
GATE: fingerprint (chain stops up in NON-detonator games, unfed <=
baseline — v82a's 9.4% was the failure mode, slack guard must hold)
→ 3 legs fresh 1570+.  ⚠ SUBMITTED VERSION = v87b (sub 56267346).
--- v87b layer: ---
(was) STATUS: v87b — PROMOTED, SUBMIT-FLAGGED : BUSY-UNIT
PREMIUM BANK-RUN.  = v87a + PREM_BANK_BUSY=6 override (non-FEED only;
feeds sacred; feed-wheat carriers exempt).  GATE (fresh 1453-1569,
117 seeds) — ALL THREE LEGS POSITIVE, 2nd-strongest gate ever:
Amitesh +2,206±1,289 t=1.71 flips +7/−4 | killer +1,748±1,546 t=1.13
+3/−2 | infill +766±1,332 +10/−7.  Pooled ≈ +1,573/game, flips
+20/−13 net +7.  Fingerprint: pocketPrem@midnight 8→2.3-4.5, first
milk sale d9→d8 all seeds, STR@d9 +2 (starved worlds 7→11), unfed
flat, caravan intact.  SUPERSEDES the v87a flag — v87b contains
v87a + v84c: ONE submission covers all three.
--- v87a layer: ---
(was) STATUS: v87a — PROMOTED, SUBMIT-FLAGGED :
PREMIUM-GOODS EXPRESS.  GATE (fresh 1336-1452, 117 seeds, 3 legs, no
failing leg): Amitesh +116±1,428 flips **+8/−4 (16→20 wins)** |
killer +1,306±1,336 t=0.98 flips +2/−3 | infill −170±1,366 flips
+7/−6.  Pooled ≈ +417/game, flips +17/−13 net +4.  Trace-verified
(exec_ledger seed 0): the d6 wool sale now funds STR seeds AND the
land buy the same day — the whole d7 pipeline runs a day earlier.
Contains v84c (yarn slot fix) — submitting this covers both.
= v84c + ONE LINE: the idle-unit cargo express (v54d fert / v58c
melon pattern) gains a WOOL+MILK+EGG >= 4 trigger.  DECODED FROM THE
BAND-LOSS LEDGER: SELL draws from the shed only (L653); our sheared
wool rode the carer's pocket 19h (ep109133507 d6 h5, 5u @ $221) and
sold a day late — EVERY animal product, ALL game.  The band sells
shear-day; that d6 wool sale funds their d7-8 STR seed cohort (they
hold $1,638 at d7, we held $831).  UNLOAD_AT=8 and the fert/melon
triggers never covered a 5-7u premium load.  Idle-units-only (no
feed-routing risk).  GATE: fingerprint (wool sale d7->d6, cash@d7 up,
unfed flat, chain/caravan intact) -> Amitesh+killer+infill fresh
seeds 1336+, flips primary.  Lineage: v85a/b + v86a falsified same
day (honest headers in versions/) — allocation surgery died, the
cash was in the pockets all along.
--- v84c layer: ---
(was) STATUS: v84c — CANDIDATE : YARN-TOWN SLOT BUMP
ONLY.  = v83a + _SLOT_NEED includes max(0, _shp_t − 4) — a pure BUGFIX:
yarn towns have wanted YARN_SHEEP=6 against a 13-slot budget since
v57b, stranding sheep 5-6 in the shed (v54f dead-capital disease;
fingerprint seeds 12-13 showed "+2 shed" for 12+ days).  Non-yarn
worlds: bump = 0, byte-identical v83a.  Base sheep stays 4 — v84b
RE-FALSIFIED sheep-6 honestly (Amitesh wins 16→10, flips +2/−8, fresh
seeds, stranding fixed; 4th and final sheep falsification).
Bar: waste-removal layer → yarn-town fingerprint + no-harm leg.
BASE RE-GATE.  = v83a + _DYN_SHEEP else-branch 4->6 (non-yarn worlds;
yarn towns keep YARN_SHEEP=6).  v72b's close = same pinned-screen
pattern as v72a; live WOOL −$3,254/game = last big real ledger line.
GATE: fingerprint (6 sheep placed, cows 9 intact, unfed stable) then
Amitesh + killer + Infill, fresh seeds 1102+.  ⚠ SUBMITTED VERSION =
v83a (versions/v83a.py) — Shane submitted Sep 15 eve.
--- v83a layer: ---
(was) STATUS: v83a — PROMOTED, SUBMIT-FLAGGED : STR WIND-DOWN
RE-GATE — THE STRONGEST FULL GATE IN PROJECT HISTORY.  = v82c +
STR_CONVERT_DAY 22->24 + STR_ENDGAME_KEEP 18->34 (v72a's dials; its
close was one pinned killer money-cell −1,138 = a screen by our own
later law; live ledger STR −$3,276/game was the real line).  GATE
(fresh paired seeds, natural worlds): Amitesh 1024-1062 +2,525±428
t=5.90 flips +3/−0 | killer 1024-1062 +1,554±373 t=4.16 +1/−0 |
Infill 1063-1101 +2,298±379 t=6.07 +5/−0.  POOLED 117 seeds ≈ +2,100,
flips +9/−0.  The early STR exit was subsidizing the field's late
monopoly EVERYWHERE, including vs the killer.  str_dead crash branch
unchanged (d18/keep 6).  Supersedes the separate v82c flag — v82c's
chain is inside this version.
--- v82c layer: ---
(was) STATUS: v82c — PROMOTED, SUBMIT-FLAGGED : ZERO-WALK
CHAIN, slack-guarded + detonator-gated.  FINAL GATE: killer 946-984
+254±1,790 flips +4/−2, killer 985-1023 REPLICATION +1,044±1,065 flips
+2/−1 — POOLED 78 seeds flips +6/−3, margin ≈ +650; Amitesh byte-v80b
exact 0 (banks verified to the dollar); Utkarsh −1,011 wash confined to
0-flip 40k blowouts (wins-only scoring); unfed 4.4-5.5% = baseline.
(prior header below)
(was) STATUS: v82c — CANDIDATE : ZERO-WALK CHAIN, SLACK-
GUARDED + DETONATOR-GATED.  = v82b + chain fires only when _MEL_RACE
latched (family games).  Killer leg carries over from v82b (+4/−2 flips,
wins 2->4, margin +254±1,790); Amitesh = byte-v80b exact 0 (chain
measured −8/+2 flips there ungated); Utkarsh leg = v82b_u (pending at
build time).  Unfed 4.4-5.5% = baseline (slack guard).
--- v82b layer: ---
(was) STATUS: v82b — CANDIDATE, GATING : ZERO-WALK CHAIN +
FEED-SLACK GUARD.  = v82a + chain allowed only while the feed round
still fits the day (2*pending_feeds + 2 <= hours left) — v82a's
unguarded chain DOUBLED unfed (9.4% vs 4.4% same seeds) yet STILL
flipped +6/−2 wins vs the killer (2->6 of 39, margin +499±1,893, own
+4,326); capture the flips without the starvation tax.
--- v82a layer: ---
(was) STATUS: v82a — CANDIDATE, GATING : ZERO-WALK CHAIN.
= v80b + ONE LINE: the focused-feeder veto (eligible(), v11e) no longer
blocks tasks on the unit's OWN TILE — the stickiness pass can then chain
FEED -> CARE -> COLLECT in one stop, the family's signature stop
(CARE+COLL+FEED 87/game + CARE+FEED 47 vs our FEED-alone 250; their
ops/stop 1.59 vs our 1.33 = +273 work ops/game, live decode of 43 v80b
games, tools/live_ledger.py + stop-composition scan).  Every walk-needing
task still vetoed while feeds pend.  GATE: fingerprint (multi-op stop
share up, feeds NOT delayed, unfed unchanged) then py_ab killer +
Amitesh + Utkarsh fresh seeds 946+.
--- v80b layer (LIVE: 741.4 day 1, caravan transfer CONFIRMED 41.5u by
h13 / $240 / 0 pockets in all 23 latch games): ---
(was) STATUS: v80b — PROMOTED CANDIDATE, SUBMIT-FLAGGED :
D10 MELON CARAVAN, DETONATOR-GATED.  = v80a + _MEL_RACE latch (opp melons
with planted_day<=1 >= 10, latched d4-8 — DAY-0 COHORT, because Amitesh
replants to 10-11 TILES but its d0 cohort is 7 and the ungated caravan
measured −1,079±879 there; the family plants 10-12 all on d0).  Latch
fires in 69/94 live detonator games incl 15/16 of the FAST class that
beats us 88%.  FINAL GATE (paired margin-diff, all fresh seeds, natural
worlds): Utkarsh 712-750 +733±1,207 | killer 712-750 +1,453±1,056 |
killer 790-828 +481±1,047 (replication) | Utkarsh 829-867 +1,235±1,005
(replication) | POOLED n=156: +976±536 t=1.82 | Amitesh = EXACTLY 0
(byte-identical v71c, 4 banks verified to the dollar).  All four
detonator legs positive, both tapes replicated, worst leg zero.
--- v80a layer: ---
(was) STATUS: v80a — CANDIDATE : D10 MELON CARAVAN, the
first family-CHOREOGRAPHY port under the existence-proof rule.  = v71c +
ONE mechanism (their d10 pipeline, decoded from 94 live detonator games,
results/decodes/choreo_melon.jsonl + tools/choreo_melon.py):
 (1) dawn caravan — d10 h0-9 ripe-melon HARVESTs assigned FIRST, nearest
     unit per tile (wheat carriers last), before feeds/stickiness/zones;
 (2) bank-run >=6 -> >=1 melon (one tile per trip, straight home);
 (3) same-turn sell — melon SELL order includes pocket cargo d10-11
     (deposits resolve before market orders inside a step; oversell no-ops).
WHY: fast copies beat us 88% (slow only 49%); same layout/distance/hands —
they sell 45.8u by h13 @ wavg $231, we sold 9.0u, and 17u died in hands'
pockets at midnight.  GATE: 4-pillar (fingerprint d10 timeline, then py_ab
killer + Utkarsh fresh seeds 712+, margin-diff + win flips).
--- v71c layer below: ---
(was) STATUS: v71c — PROMOTED to main.py Sep 13 .
= v70c + ONE change: care_skip gates on OBSERVED price (<= CARE_FLOOR_NOW=$8)
  instead of the falsified glut projection (comment at the care_skip line).
EVIDENCE (the strongest gate this project has run — paired natural-world
py_ab on real live-opponent tapes): vs Amitesh(801) 77 seeds margin-diff
+1,155±596, wins 27%→32%; vs Infill(804) FRESH seeds 596-634 +1,281±889,
wins 33%→36%; pooled +1,195±495 t≈2.4; vs killer tape(2400-class) +180±510
no-harm; boom unfed 4.1% @16 animals; care 74% of animal-days (live was
~55-60%; the old projection had care silently ~OFF in thin worlds).
Falsified siblings for the record: v71a (P_CARE 1.5 starved waters −1.5/
−1.8k; demand gate = no-op, town center drains 1/day of everything);
v71b (blanket-on: floored milk eats labor + sell slots, YARN2 −3,537);
v74d (hinge stack: pinned cells +1.6k but 77-seed OOS wash — pinned
money-cells are screens, never gates).
--- v70c layer below: ---
(was) STATUS: v70c — PROMOTED to main.py Sep 12 early .
= v67c (berry-forward + capital reallocation + milk-rich release)
  + v68a WHEAT SUSTAIN (last_plant 24→27, factory day 22→13; field
    +1.2-1.6k own bank vs king AND band tape, all fresh cells)
  + v70c YARN RELEASE (sheep pause 2→4 when a YARN_STORE revealed;
    YARN2 vs v66c 6-0 +1,664 — the holdout 2-14 regression closed;
    exact no-op in yarn-less worlds; king YARN2 delta +4,467 bank).
Gates all passed: fresh-seed field cells, boom unfed 8.2-8.6% =
baseline, mirror-artifact rule applied (field legs decide).
--- v67c layer below (Sep 11): ---
= v66c + berry window opens DAY 2 (was 4): seed gate d4→d2,
_berry_first 4-9→2-9 (COW>=3 kept), window-days STR plants at
P_WATER pre-herd.  WHY (measured, 110 live games): d15-21 loss
gap is 63-79% strawberry VOLUME; our tiles enter ground d9-13
(first yield d17-19) vs killers by d8 (d14-18); selling clears
<=1 day after harvest — planting date is the whole lag.
Gate: pinned-world cells MILK0/MILK1 must improve vs v66c AND
v61e; MILK3 boom must not regress.

Base was: v66c — PROMOTED to main.py 2026-09-10.
= v61e + land_hold persists post-clock (Q2 d9→d6, 4/4) + berry
window d4-9 / cap 24 / sheep tail pauses (the tail's dollars =
the cohort's seed money; each alone failed — v55a seed-cash law
+ 86b solo — the PAIR pays, v55e precedent).  GAUNTLET:
**HELD-OUT 154: 115W-39L (74.7%) +2,321 μ/σ 0.69** (halves
70.5/78.9 — 2nd-strongest full confirm ever, behind v58c);
screen 68.8%; boom-scale unfed gate PASSED (9.5% vs 11.9% at
16-herd); legs: wool 32-0 +26.8k RECORD, frontier HOLDOUT
−27,431 NEW BEST EVER, router −45.1k (+2k), MR −44.3k (+1k),
goose −35.8k (noise), king −49.1k (worst leg, logged).
Mechanism = the live loss anatomy: STR cohort planted ~d7-9 on
d6 Q2 tiles pays INSIDE d15-21 (the band battle week where
losses ran us +20k vs their +38k).  NOT SUBMITTED — flag Shane:
-m "v66c" (displaces broken v62a 734 → actives v61e 766 + v66c;
supersedes the v61e-r re-file flag).
Lineage …v61c→v61d→v61e→v66c.  v61e base:  v61e + ONE edit: land_hold persists
while a clocked quadrant is pending (was: 1 pre-clock day only),
so sheep 5-7 stop eating the $1,000 for 3 days — live Q2 was d9
[9,9] tight vs all 3 band killers' d8 and the ref #1's d5; the
d15-21 income week is planted on those fresh tiles.  Ledger
proof: $1,083 on d6 morning, clock fired, spent on sheep+wheat.
PRE-REGISTERED RISKS: herd tail +1 day; d6-7 seed dip (berry
window overlaps).  FINGERPRINT GATES: Q2 day 9→6-7; STR@d10 up;
unfed not worse; herd complete ≤ +1 day.  Baseline v61e.
Lineage …v61d→v61e→v66b.  v61e base:
milk-boom (fired lane 20W-6L 77% +2,141) + feed completeness (held-out
64.9% +1,385) + v60a STR wind-down + hire-last (v61b2 held-out 89W-65L
57.8% n=154, measured WITH a handicap — no boom — and still won).
Legs: wool 30W-2L +24.7k (+7k), frontier −31,230 NEW BEST EVER, goose
+0.9k; MR/router flat; king margin −5.2k (all-loss leg, logged).  NOT
YET SUBMITTED — flag Shane: -m "v61e".
Lineage …v58c→v60a→v61c→v61d→v61e.  = v61c (tick-day feed P_SAVE + 2nd wheat
carrier) + the milk-boom (3-milk-shop towns, milk ≥ $200 at d10-13 →
cow target 9→12, +3 slots, fallow pastures; Wei Han decode = the
adaptivity thesis).  HELD-OUT 77 vs v61c: +361 μ/σ 0.179 overall,
**FIRED LANE 20W-6L (77%) +2,141 σ4,010**.  Legs: MR/king/router
byte-identical to v61c (latch never fires vs the front — clean
gating); wool 29W-3L +17.7k; frontier −33,763; goose −34.4k (noise).
NOT YET SUBMITTED — flag Shane: -m "v61d" (contains v61c feed fix +
v60a wind-down).  Lineage …v58c→v60a→v61c→v61d.  NET-flow
loss forensics (Sep 7, churn-corrected): in v58c's losses our OWN d15-21 net
drops 25.4k -> 19.8k — the shared-market squeeze: their bigger flood kills
our STR price and we keep producing into the corpse.  The d22 conversion's
STATIC keep-18 then makes the measured 84-120 floor-sell units at $1-2
d22-28 (3-4 losses) plus shed-pressure force-dumps.  v60a: when the STR
market projects DEEP-dead (5-day glut projection <= $5 — transient dips
project far higher because STR has the game's biggest town drain, v15e
protection) from day 18, the keep drops 18 -> 6 and digging may remove
plants with pending (worthless) yield.  Healthy towns byte-identical.
NOT v15e (mid-game abandonment, rejected) and NOT v53 care (closed): this
fires only d18+, only at deep-floor projections, only beyond 6 keepers.
FALSIFICATION: fired lane = dead-STR games only (fingerprint: floor sells
100 -> ~30, digs up, elsewhere byte-identical); screen + legs + held-out.

Was: v58c — PROMOTED to main.py 2026-09-06 evening.  HELD-OUT 77: 149W-5L (96.8%) +6,008 μ/σ 1.783 = strongest
confirm in project history; all field legs project bests (wool 32-0 +21.4k,
multi_route −27.9k, frontier −36.1k, tape −28.9k).  Engine truth L438-443: one-shot yield grows ONLY on watered
window days, +1 plain / +2 fertilized; melon window = ages 6-12, max_yield 6,
harvest gate age 10.  Measured (melon_race probe, 8/8 seeds): the multi_route
family fertilizes its melons → maxed 6/tile by d9, harvests at the d10 gate,
dumps 256-264 at $272→220; OUR unfertilized melons reach 5/tile, unload at
nightfall, and sell at 265-267 into the crater ($214→158) — the x-ray's six
crater-sells.  Fix (universal, no opponent gating): (1) melon fert window
(6,8) engine-aligned, (2) fert applies to MELONS allowed d6-9 (flywheel
FERT_APPLY_FROM_DAY=10 made the old (5,7) entry DEAD CODE —'s
"fert is cash" was right for STR, wrong for melons: $85 fert covers 3 window
days = +3 melon units ~$600), (3) melon express-unload (≥4 carried) so the
d10-morning harvest sells d10 morning, before everyone's wave.
FALSIFICATION: fingerprint = fert applies d6-8 ≈ 9-11, melon sells ≤ step
255 at ≥$240, ~6/tile; cow ramp must NOT slip (fert cash −~$800 d6-8);
16-seed screen + field legs, then held-out 77.

Was: v57d — CANDIDATE BUNDLE (v57a fert pipeline + v57b yarn sheep [fired 19W-5L 79%] + v57c melon sustain [screen 81.2%];).
= v50a + one line: from day 28, sell batch caps are OFF (n = stock).
Live close-loss decode: 4 of 11 sub-8k losses stranded MORE shed
value than the losing margin (d29 harvests arrive with 1-2 market
turns left; milk batch 3/turn cannot clear 6-9 units). 
(ℓ-aware lock-in) tested INERT — 8k+ leads at d24 are already-won
games; close games never reach the trigger — dropped.
FALSIFICATION: leftover shed value at step 719 must go to ~0 on
replays; 16-seed A/B must not regress (margins should tick up in
close games; big-seed games mostly unchanged).

Was: v50a — CANDIDATE 2026-09-03 (ANTI-TAPE COUNTER-SCHEDULE).
= v47b + fighting-phase module vs the tape class (top of board; we
are 0-16 vs it, and every tape-class live opponent is an auto-loss).
A tape is OPEN-LOOP: its complete sell schedule is embedded in its
own file and identical every game.  TAPE_SELLS = every 5+-unit sell
it will ever make.  Counters (ALL gated on tape_mode → non-tape
games byte-identical = free control): (1) generic FRONT-RUN — a
scheduled wave >= 8 units within 10 turns triggers our dump first at
0.4x threshold; (2) STR cap 24 + seed want 4 in tape games (their
300-unit d16-29 flood makes marginal berries worthless); (3) wheat
liquidation from d22 (their 196-unit d25-29 dump).  FALSIFICATION:
tape-leg margin must improve >= 5k from v47b's −38,620 with our own
bank UP (not just theirs down); 8-seed vs main must be BYTE-IDENTICAL
(detector self-exclusion) or the gating leaks.

Was: v47b — CANDIDATE 2026-09-02 (= v47a + DYNAMIC CARROT CAP).
v47a 16-seed screen 21W-11L (65.6%) +3,745; losses cluster in weak
towns.  Seed-12 autopsy: 3x PET_CAFE = 36 carrots/day and v47a
plants ZERO carrots (blueprint default) while v45a's 12 carrots won
the town.  Fix: _DYN_CARROT_CAP 12 when carrot drain >= 8/day, else
0 — blueprint stays the default, carrots return where they pay.

Was: v47a — CANDIDATE 2026-09-02 (BLUEPRINT PORT).
= v45a + the live 150-165k winners' coordinated shape, decoded from
99 live episodes (0W-14L vs the 120k+ class; 4 exact copies of one
public blueprint at 110-164k).  The bundle — deliberately coordinated,
our single-dial searches proved each piece loses ALONE:
 1. D0 basket: 2 sheep + 2 cows + 12 MELON + 7 wheat (their NW fill).
 2. MELON = one-shot detonation: last_plant 6, no replants (our old
    replants sold at $146->$31 into the post-spike glut), sell batch
    15 @ min 60 -> dump all ~72 fertilized units d10-11 (they got
    $266-214 as first mover; we arrived a day late at $202 falling).
 3. Melon tiles ARE the future pastures: slot reservation now DYNAMIC
    (placed+2 headroom, min 4) — melons detonate d10 exactly as cows
    5-9 arrive to take those tiles; old code sterilized 13 tiles from
    day 0.  Melon cluster anchor moved onto the ring.
 4. Herd: sheep 4, cows 9 (dead-milk guard to 6 kept).
 5. STR ramp EARLY: pre-herd want 12, reserve 0 (their 38 plants pay
    from d15-16; ours paid d20+ = -19k pure timing).
 6. WHEAT engine ~20 sustained (feeds 13 animals + sells; their
    wheat rev 15k vs our 3k): SEED_WANT 8, CARROT cap -> 0.
 7. Hands 12 for real: v44a machinery (wave hiring + payroll
    pre-sell + evening hold) — dead heat on the SMALL farm, retest
    at this scale.
FINGERPRINTS REQUIRED before any A/B: d0 orders = 2s/2c/12mel/7whe;
d10 bank >= 8k; >=50 melon units sold by end d11; d12 = C8-9/S4/
STR>=30/WHE>=12/h12; STR revenue from d16.  FALSIFICATION: gauntlet
vs v45a, proxy_meta150, tape, 4 archetypes; if the bundle loses to
v45a the blueprint needs OUR adaptive base more than we need its
scale — decompose before discarding.

Was: v45a — PROMOTED 2026-09-01 night (layout clustering).
VALIDATION: vs v43a 16-seed 21W-11L (65.6%); **77-seed 93W-61L
(60.4%) +1,427 mu/sigma 0.36** (occupancy unchanged -> town is a
control, so these are clean).  FIELD GATE: 4 proxy legs paired vs
v43a on same seeds — v45a 120W-8L vs v43a 120W-8L (identical wins,
margins up on 3/4: wool +2.4k strglut +1.2k eggmilk +1.0k, wheat
-1.9k).  Tape leg: own bank +3,566 but tape banks +7,508 MORE
(harvest bursts lump our sells -> market headroom gifted) — costs
zero wins vs proxies; SELL-SIDE DE-LUMPING is the flagged follow-up.
Fingerprint: day-12 map shows solid per-crop blocks vs raster
scatter; walk audit n=2 inconclusive (1.89/1.57 vs 1.75/1.69
moves/job), pass share +2.5pp — the win came anyway.

Was: CANDIDATE 2026-09-01 (layout clustering).
= v43a + CLUSTERED PLANT ASSIGNMENT.  The v40b autopsy showed walking
sits at the density floor of a SCATTERED layout (2.3 moves/job is the
geometry, not the assignment) — the remaining walking budget is WHERE
we plant.  Mechanism: the per-turn plant multiset is computed exactly
as before (the cap/budget loop never reads tile position, so counts
are order-independent), then crops are assigned to empty tiles by
Manhattan distance to each crop's anchor — centroid of its live
plants, else a fixed zone seed (melon W of the herd, wheat SW below
it, strawberry NE, carrot NW top, tomato deep NE).  Same counts, same
tile OCCUPANCY -> the town shop draw stays a control (cheap A/B).
Harvest/replant/fertilize passes then sweep contiguous blocks, which
is what v40a sticky routing wants.  FALSIFICATION: if the day-12 farm
map shows no contiguous blocks, or moves/job does not drop, mechanism
is inert -> discard.  If banks are byte-identical to v43a the reorder
never fired -> bug.

Was: v43a — PROMOTED 2026-09-01 (round-2 search champion).
= v42b base (dynamic demand STR cap VALIDATED at scale: STRdead towns
4-0 +8,774, STRweak 64W-33L +1,070, no-harm elsewhere, 1,500-game
Stage A; goose plumbing present but default-off after adaptive geese
measured -3,490) + the gen-1 genome: d0_feed 8 -> 6.  Pod S3 held-out
(150 seeds x 7 field legs incl. meta tape + 4 live-archetype proxies):
field +414, dBank +4,857.  Local gauntlet: vs v40a 77 seeds
**133W-21L (86.4%) +4,750 mu/sigma 1.01**; tape leg flat (-813 = noise).
Scale bundles all NEGATIVE (hands dial proven INERT - hiring machinery
is the bottleneck, see PLAN); SE land and early geese confirmed
losses.  Was:
ROUTING, ported from v33a).  VALIDATION (field-primary): vs v39a 77
seeds both seats **122W-32L (79.2%), +3,227, mu/sigma 0.76**; vs tape
seeds 8-23 (32 games) margin −30,657 vs v39a's −37,718 = **+7,061
better**; vs v12 16-0 +14,037 (flat vs v39a's +14,499).  Mechanism:
ping-pongs −76%, U-turns −77%, 10+-hauls −54% on replay.  The v33a
idle-up side effect did not sink it on the all-in shape (pass 9.1→
10.6% but bank up everywhere).  Original candidate rationale:  Walk audit of v39a: move 57-59% / work 32-34% / pass 9%,
2.24 moves per work action, 169-229 ping-pongs + 185-239 mid-walk
U-turns per game — walking units get re-dealt every turn as the task
list re-sorts.  Port adds: (1) _STICKY cross-turn target memory (keep
a still-valid routine target), (2) 2-tile incumbent discount in greedy.
v33a measured −85% thrash on the v25 shape but parked on idle-up
(15W-17L); the all-in v39a shape always has surplus jobs, so idle-up
should not recur — that is the hypothesis under test.

Was: v39a — PROMOTED 2026-08-31 (pod shape-search champion).
= v37d base + the gen-10 genome from the 24-generation field-primary
evolutionary search (32-vCPU pod, ~4,300 games/gen, 3-stage filter,
promotion gate = field wins >= +8 on 200 held-out seeds vs v31b/tape/
v12).  Six gene edits vs v37d: herd 4s/11c -> 5s/6c; day-0 basket
2s/2c/10melon -> 1s/3c/6melon (feed 8 kept); ENDGAME_CONVERT 18->19;
feed_hold x1.5 -> x1.3; berry reserve $150 -> $21.
VALIDATION (all field-primary): vs v31b 77 seeds both seats
**128W-26L (83.1%), mean +5,131, mu/sigma 0.93** — banks median
83.9k / p75 99.2k / max 126.2k (v31b same seeds: 78.8k / 93.8k /
117.1k); vs tape seeds 0-7 margin −35,301 vs v31b's −43,163
(+7,862); vs v12 both 16-0, margins +43% bigger; 300 FRESH seeds
final: dWins +712, field +232, dBank +6,480.  Zero crashes in 500+
games.  Full search log: search_runs/2026-08-31_shape/.

Was: v37d — PROTOTYPE iteration 4.  v37c at 16 seeds: 10W-22L mean
−1,162 (vs v37b's 4W-28L −8,341 — leaner reserves confirmed).  Seed-0
decode: deficit is diffuse (TOM −7k, STR timing −4k, WOO −3k; the 11th
cow adds no milk in poor-absorption towns — town-dependent, fine).
v37d closes the TOMATO leak: both tomato gates keyed on herd_complete/
ramp_fast, which the 11-cow target pushes to d12-13 (v31b enters d9
and banks ~7k).  Fix: the gates also open when money >= 3000 — in this
shape "economy ramped" = herd done OR detonation landed.

Was: v37c — PROTOTYPE iteration 3.  v37b jumped +30-44k/game over
v37a (banks 75-98k, margins −0.2k to −10k vs v31b) — but the decode
shows the farm sits nearly EMPTY days 5-9 (10 melons + nothing): the
4-day feed_hold (~$900) plus the $550 berry reserve block ALL seed
purchases at monster-economy cash levels.  The blueprint holds nothing
and feeds day-to-day.  v37c: feed_hold 4 days -> 1.5, berry reserve
550 -> 150.  Same reserve-philosophy bug, third location.

Was: v37b — PROTOTYPE iteration 2.  v37a probe (0-6, −10 to −22k)
leak-decoded against the blueprint: (1) both day-0 cows STARVED by day
2 ($800 lost — basket left $24 and wheat seeds don't yield until d2)
→ feed bridge: basket buys 8 market wheat, melons 12→10; (2) STR
fatally late (18@d14 vs blueprint 40@d12; last_plant 17) — berry ramp
was gated on herd_complete which an 11-cow target pushes to d13 →
decoupled: berries plant from day 4 alongside the cow ramp (the melon
money funds both); (3) land was animal-gated and the cow deaths
delayed it → day-clock gates (q2 from d6, q3 from d10).  The melon
detonation WORKED in the probe ($368@d10 → $9,155@d11, cows 4→11 in
two days) — the engine is alive, the plumbing killed it.

Was: v37a — PROTOTYPE: MONSTER-NATIVE ECONOMY (from the/54
blueprints, built as SHAPE — no actions copied).  The decoded 115-160k
farms run a day-0 ALL-IN (start money is $3,000, engine L252): Prashant
d0 = 2 cows + 2 sheep + 12 melons + 7 wheat + 5 hands, ending day 0
with $21 — zero reserves ever, cow +1 every ~2 days to 10-11 by d10-12,
funded by the day-10 melon detonation (12 x ~$260), STR to 40 by d12,
q2 day 6 / q3 day 10, 12-13 hands, late conversion + full liquidation.
Four dial-nudges toward this shape FAILED on our base (v31a/v33a/v35a/
v36a) — this is the other hill built natively, our adaptive branches
carried.  Changes vs v31b: day-0 override basket; COW target 11 (+3
slots); cow pause REMOVED; feed cushion halved; MONEY_RESERVE 150->50;
STR cap 40; late dig-conversion organ.

Underlying: v31b — Phase 6 fix #12 (PROMOTED, = v25 + CONDITIONAL DEAD-TOWN
REALLOCATION).  Pod-validated at scale : 74/2000 towns fire
(3.7%), fired A/B 115W-33L (78%), mean +6,144/game, 61/74 towns
net-positive, zero crashes; field legs clean (tape/v6a/v12 dWins +0,
direct H2H vs v25 +8 wins); non-fired games byte-identical to v25.
v31a (early factory alone) was REJECTED 2W-8L on fired seeds: the wheat
cap was never binding (v25 runs 12-16 wheat tiles vs cap 22) — tiles,
not caps, are the constraint, and premium crops keep taking them.  v31b
does the real reallocation: on latch, STRAWBERRY cap drops 35 -> 15
(stop new premium planting; freed tiles flow to wheat via PLANT_ORDER)
and strawberry seed purchases stop.  Check moved day 6 -> 9 (3 draws):
the observed false-positive class (2 bakeries then a premium run,
probe seed 0) no longer fires; day-9 fire set is a strict subset.
-49 found the herd family's worst towns are dead-premium draws
(no strawberry/milk-eating shop early) — exactly where the wheat-native
v30a prototype WINS (wheat demand never gluts: 6 shop types eat it).
The shop draw is public, one shop unlocks every 3 days, and the day-6
draw separates these towns cleanly (seed 2: BAKERY+BAKERY vs seeds 0/1:
FARMERS_MARKET/ICE_CREAM/BRUNCH).  So: when the draw shows no premium
eater and at least one wheat eater, start the existing day-22 wheat
factory at the latch day instead.  Trigger reads shops only; games
where it never fires are byte-identical to v25.

Underlying: v25 — Phase 6 fix #11 (PROMOTED, = v24 + SEARCHED OPENING).  The
first search-discovered shape change.  Six genes moved vs v24: cow_pause
5->3, resume_day 11->9, str_want 6->7, wheat_cap 20->22, TARGET_HANDS
6->8 (= 12 hands at 3 quadrants — the elite labor level), factory_day
18->22.  The shape story: berries interleave from the 3rd cow (not 5th),
two more hands carry the bigger premium workload, wheat conversion waits
4 more days because the labor now sustains premium tiles longer.
hands=7 ALONE failed twice historically — the synergy needed joint
search.  Evidence: pod FINAL vs v24 on fresh seeds 700-999: +159 dWins
(field +87, mirror +72), dBank +1,173; local full-pool 4 batches: +9/256
with the v12 leg positive ALL FOUR batches (+3/+1/+2/+3, 63/64 games)
and NO harm on the tape leg (which the search never saw).  Below: the
v24 header this build inherits everything else from.
--- v24 (prior) ---  Validation:  Four pool batches (256 games): v12 leg +2 dWins / +737
dBank; every other leg 0 dWins; mirror = 5W-5L-6T with seat-symmetric
banks = FULLY INERT (pool_ab's mirror "-10" was tie-counting artifact —
HARNESS NOTE: mirror ties count as A-losses in POOL TOTAL; check margins
+0 -> run run_local for the true W-L-T).  Stratified probe vs v12 (16
seeds, replays): fired 10/16 games at d16-18, deficits -5.5k..-11.2k,
tomato 70-72 -> 8/10 WINS FROM BEHIND; counterfactual on both fired
losses: baseline lost those games WORSE (-4,915 -> -3,037 and -2,640 ->
-328).  Zero measured downside anywhere.  First live bank-differential
mechanism (destbreso sign-flip).  Original design below.
--- design --- BANK-DIFFERENTIAL TOMATO GAMBLE (first ell-aware
mechanism).  Theory (destbreso, RESEARCH 3): ratings count wins only, so
Pr[win] = Phi(mu/sigma) — extra VARIANCE helps when behind (ell + mu < 0)
and hurts when ahead.  Both banks are public every turn.  Evidence for the
lever: v22c measured that "day>=15, tomato >=70" planting is ~EV-neutral in
bank (dBank -205/+560) but swingy — i.e. A FAIR COIN.  Unconditionally a
fair coin is worthless (v22c rejected, dWins -3/-4); flipped ONLY WHEN
LOSING it buys win probability with variance we'd otherwise waste.
Mechanism: if bank deficit >= 5,000 at day >= 15 and tomato >= 70, fire the
(validated) tomato machinery at the lower bar; the >=85 confirmed-hinge
trigger stays unconditional.  Sticky once fired (a started batch gets
finished even if ell recovers).  Byte-identical when never behind — the
stratified decode must show: fired games = losing positions converted at
above-baseline rate; unfired games identical.  Base: v21 (below).  Confirmation battery: mirror vs v18
47/64 (73%), margin positive ALL FOUR batches (+2,473/+1,210/+1,217/+2,312);
pool dWins +5/-1/+6/+9 = +19 over 256; v12-leg counterweight -9 (stable, known,
from the wheat component; outweighed by its +13 pool dWins alone).  THE STACK: v18 + WHEAT UNBLOCK + TOMATO HINGE
REACTION + seat-1 step robustness.  Components, each separately validated:
(1) WHEAT unblock (= v19i: SELL min 30->18 — was above wheat's $25 base so we
never sold in non-scarce markets; feed reserve 2->1 day): battery mirror
44/64 (69%), margin positive all 4 batches, pool +13 dWins (v12 leg −9 noted;
v19j's season-reserve variant changed nothing and was dropped).  (2) TOMATO
pure hinge reaction (v20e): fired 5/48 seeds, 5W-0L mean +9,680; with v20d's
confirmed-stage games the branch is 8W-0L ≈ +10k; byte-identical when
unfired.  (3) obs["step"] can be None in seat 1 (community find): guarded.
Base: v20e CANDIDATE — v20d MINUS the speculation stage (pure hinge
reaction).  Stratified decode over 19 fired games: speculation-only games
(peak 4 toms, hinge never confirmed) went 3W-7L mean −1,201 — the spec
plants displace better crops and sell at break-even; hinge-confirmed games
(full 10-12 toms) went 3W-0L mean +10,483 (+357/+8,982/+22,109).  So: plant
NOTHING until price >= 85 proves the hinge, then commit fully.  Rare, large,
and byte-identical everywhere else.
Base: v20d CANDIDATE — v20c + STAGED REACTION (fixed premature trigger).
v20b/c autopsy: MIN_SIGNAL 55 is BELOW base-price noise (tomato idles 60-72
all game), so 12 speculative tomatoes went in at d6-12 — displacing the
strawberry ramp's tiles, labor, and seed money in the game's most valuable
window — while the actual hinge fired at d19+.  Staging: NOTHING before the
herd completes (ramp_fast); with 2+ tomato shops drawn, a small 4-plant
speculation; full 6-per-shop commitment (and fast-plant priority) only when
price >= 85 CONFIRMS the hinge.  React to the hinge, don't front-run base.
Base: v20c CANDIDATE — v20b + tomato REPLANT cycle (last_plant 18 -> 20).
Tile-tracking autopsy + engine L786-802: "ongoing" crops die after exactly
max_yield(=4) production ticks — tomatoes complete at age ~12 (ticks at ages
8-11) and weed out; they were never thirsty.  (Same rule explains our
late-season strawberry decline 35->29: lifespan, not neglect.)  Tomato is a
REPLANT-CYCLE crop: $50 -> 4 units/cycle, ~$240-280 at median scarcity and
$600+ in hinge towns; last_plant 18 forbade replacing the died-off first wave
exactly as prices peaked (12 plants -> 1 while price ran 106 -> 248).  A d20
plant still ticks twice by d29 — +EV at scarcity prices; triage still stops
planting when the price sags.
Base: v20b CANDIDATE — v20a + labor budget for the tomatoes.  v20a seed-1
autopsy: mechanism fired perfectly (12 toms by d12, +$5.5k, ahead at d16-18)
then the tomatoes DIED OF THIRST as the hinge fired (12 -> 1 plants while
price ran 106 -> 248; the one survivor showed the lost prize: $144-248/unit
through the endgame).  12 extra daily waters had no budget.  Fix: (1) CARROT
cap shrinks by the tomato cap (tomatoes take the filler niche's water share,
~8/day freed vs 12 needed); (2) TOMATO gets fast-plant prio while the signal
is live (same v18c logic).
Base: v20a CANDIDATE — v18 + REACTIVE TOMATO (the disclosed white space).
Three independent sources (host Bovard 735311; destbreso; Georgy Mamarin
33/37,343 episodes): the 1.32.7 scarcity hinge fires for TOMATO in ~50% of
games (p99 $786, base $60) and the field measurably has NOT adapted ("zero
flipped whether they plant carrots").  Engine: TOMATO seed $50, first yield
day 8, ONGOING with interval 1 — a DAILY producer (2x strawberry cadence);
eaten by PIZZA_SHOP + FARMERS_MARKET (2/8 draws, visible days 2-8 — the info
timeline works, unlike cow-depth conditioning).  Mechanism (redirect-form,
per our conditional laws): plant tomatoes ONLY when a tomato shop is drawn
AND price >= ~base; cap 6 per tomato shop (max 12); they take the CARROT
filler niche (carrot yields to tomato in PLANT_ORDER when the signal fires);
triage covers TOMATO like melon/carrot.  Tape-proof: a replay tape cannot
condition on the shop draw.
Base: v18 — Phase 6 fix #8: v17 + EARLY-INTERLEAVED STRAWBERRY RAMP
(the staged-herd family: v18c fast-ramp planting prio + v18d parity seeds +
v18e staged herd).  Cows pause at 5 until 20 strawberries are planted (or day
11); from day 4 surplus cash buys berry seeds with the next cow's $550 always
reserved; post-herd, STRAWBERRY planting runs at P_WATER and the seed buffer
is 8.  Cows 6-8 arrive d11-14 and still repay ($450 vs ~$40-70/day milk to
d29); ~20 strawberries gain 4-6 producing days each.
A/B (4-batch 64-seed pool battery, the hardened occupancy protocol):
head-to-head vs v17 55/64 (86%), margin positive EVERY batch (+3,290/+3,245/
+1,875/+3,800); pool dWins +12/+12/+8/+12 = +44 over 256 games (never
negative); mean dBank +1,804.  Strongest promotion since v15.
Source: day-4 field audit (101 live games, every 110k+ opponent dissected):
winners hold 5-7 animals + ~20 strawberries at day 8 on the same 75 tiles; we
held 10 animals + 2 berries.  Their strawberry revenue 43-104k vs our 22-43k
was the single biggest line item separating us from the winning field.
Base: v18c CANDIDATE — v17 + FAST STRAWBERRY RAMP (post-herd).
Field audit (101 live games; every 110k+ opponent economy dissected): winners
sit on the SAME 75 tiles with the SAME 12-19 animals, but have 25-42
strawberries in the ground by day 12 vs our 9 — their ramp runs 6-7 plants/day,
ours 4, and each week earlier a strawberry exists is ~7 producing days x
~$25/day.  Their strawberry revenue: 43-104k; ours 22-43k — the single biggest
line item separating us from the winning field.  Root cause measured: planting
sits at P_PLANT(3) BEHIND watering(2), so it runs only in afternoon slack;
watering only matters by end-of-day (tasks regenerate hourly) while planting
today starts the 10-day clock today.  Change (post-herd_complete ONLY — the
cows-before-berries law stays untouched): STRAWBERRY planting tasks run at
P_WATER, and the post-herd seed buffer rises 5 -> 8.  Base: v17 — Phase 6 fix #7: v16 + DEMAND-CONDITIONED HERD TAIL.  First true
shop-draw-adaptive production decision (the margin a replay tape cannot copy).  Variance decomp of
77 live games: our bank swings ~$20k on the MILK SHOP DRAW alone (0 outlets: 55.7k,
1: 77.2k, 2: 81.7k, 3: 94.2k) because the herd is fixed while market capacity is
rolled per game.  Engine (L867-891, verified): one shop unlocks every 3 days, drawn
with replacement from 8 types (3 serve milk -> expectation 3 outlets); by cow-tail
purchase time (days 6-12) 2-4 draws are visible.  Change: cows #7-8 require
projected final milk outlets >= 2.0 (seen instances + remaining draws x 3/8);
otherwise the herd caps at 6 cows and the cash flows to strawberry seeds (existing
herd-gated ramp logic).  First true shop-draw-adaptive PRODUCTION decision — the
margin a replay tape structurally cannot copy.
A/B: conditional mechanism — fired in 9/48 towns (~19%); in fired games
15W-3L (83.3%), mean +2,022 (pre-stated criterion: positive record AND margin in
fired games; unfired games are byte-identical mirrors). p~0.004 binomial.
Base: v16 — Phase 6 fix #6: v15 + DOOMED-CROP TRIAGE (MELON+CARROT only).
Action-mix diff vs the strongest live loss (Hem, 116.8k, same walk share, same
productive-action count, +$30k revenue): we spent 105 more WATERS — 11 melons
watered daily days 17-24 into a $1 market.  When melon/carrot's 3-day projected
price <= $15, generate no water/rescue tasks and stop planting them; harvests
continue (free the tile).  STRAWBERRY deliberately excluded: its gluts are
transient (biggest drain in the game) and v15e, which could skip it, lost its
out-of-sample batch (53.1%, fat tails) to strawberry abandonment.
A/B: v15f beat v15 41-23 over 64 (64.1%: 65.6% +461 seeds 0-15, 62.5% +596 fresh
16-31 — both batches positive).  Action-mix diff vs the Hem loss (their 116.8k, same walk share 59-60%,
nearly same productive actions, +$30k revenue): we spent 105 MORE waters — measured
destination: 11 melons watered daily through days 17-24 into a FLOORED melon market
($1).  Watering, rescuing, replanting crops whose product is dead is the labor leak
that starves care (5-8/12) and fertilize (56 vs their 103).  Fix: when a crop's
3-day projected price <= $15 (same forecast as care-skip), generate NO water/rescue
tasks for its plants and stop planting it; harvests continue (they free the tile
for a live crop).  Labor-only reallocation.
Base: v15 — Phase 6 fix #5: v14 + DAY-0 FOURTH SHEEP.  Opening decode (tape vs
v12, same game, days 0-8): tape out-earns us $9.2k to $5.9k; biggest single cause is
sheep timing — tape owns 4 sheep at hour 0, we bought #4 on day 4.  Sheep first-tick
is 6 days, so all four of theirs pay days 5-6 (the $4.6k wool spike that funds cows
3-8) while ours started day 10.  We missed it because day 0 spent $380 on
strawberry+carrot seeds that yield nothing before day 10 anyway.  Fix: on day 0,
defer STRAWBERRY/CARROT seed buys until the day-0 herd (4 sheep + 1 cow) is owned.
A/B: v14b beat v14 56-8 over 64 (87.5%!! — 84.4% +3.0k seeds 0-15, 90.6% +3.4k
fresh 16-31; STRONGEST promotion in the project).
Base: v14 — Phase 6 fix #4: v13 + HERD-GATED STRAWBERRY RAMP.  PLANT_ORDER puts
STRAWBERRY ahead of WHEAT for tiles (cap 35) but STR seed buying stays at 3/turn
until herd_complete, 5/turn after — cows always outrank berries for cash.  Found by
falsifying two wrong forms first: v13b (cap raise alone, 56.2% — cap was never the
constraint) and v13c (priority + early seed burst, 37.5% — the $500+/turn day-0 seed
spend delayed every cow 1-2 days and marginal strawberry revenue at 35 mirror-plants
is ~$385/tile net, not the $1,100 average at 23).
A/B: v13d beat v13 42-22 over 64 (65.6% BOTH batches: +2.5k seeds 0-15, +1.2k fresh
16-31).
Base: v13 — v12 + endgame wheat factory (62.5% both batches over 64).  Live-loss analysis of
all 64 v10/v11 Kaggle episodes: floored WOOL/MILK games bank 68k vs 88k clean; ~25%
of our wool+milk sold at <=$5.  v12a (sell-timing rules) was a 50.0% wash and proved
the leak is NOT timing — we already sell on arrival; the back half of production
lands after the market dies.  CARE multiplies output (cared = 1+interval units vs 1),
so when the product's projected price ~3 days out (glut curve, combined inflow vs
town drain) is <=$15, the care turn buys nearly nothing and deepens the glut.  Skip
CARE for that species while doomed (FEED/COLLECT/HARVEST unchanged); care resumes on
recovery; freed unit-turns flow to crops.  Labor-only -> occupancy unchanged.
A/B: v12b beat v11 46-18 over 64 (71.9%; 71.9% seeds 0-15 +1.7k, 71.9% fresh 16-31
+2.2k — held out-of-sample).
Base: v11 — Phase 6 fix #1: v10 + FOCUSED FEEDERS (found by direct measurement).
Audit of v10: from day 12 on, only 2-8 of 12 animals got fed daily while CARE stayed
~12 — and an animal unfed on its production day produces base 1 and its WHOLE banked
care bonus is WIPED (engine B.4), so the care labor was being thrown away exactly in
the day-18-27 window where our live losses show us being overtaken.  Trace: the farmer
picks up ALL the feed wheat at hour 0, then greedy assignment sends him across the map
for P_SAVE crop rescues (prio 0 beats FEED's 1; he wins distance ties as unit 0) —
13-hour round trips carrying 20 wheat while the 12 FEED tasks only he could perform
sat waiting.  FIX: while FEED tasks are pending, wheat-carrying units are eligible for
FEED tasks ONLY (hands handle plant rescues).  Audit after: 10-12/12 fed daily.
A/B: v11e beat v10 49-15 over 64 (76.6%; 75.0% seeds 0-15, 78.1% fresh 16-31).
Base (v10) = v9 + faster herd (cushion 4 -> 2 days, none on days 0-1; 65.6% over 64).
Base (v9) = v8 rational thresholds + tape-family counter:
  * MELON: its day-20 wave kills the melon market permanently (measured: $246 -> $16 -> $1).
    Sell everything before it lands (threshold 60 from day 15, dump from day 18) and stop
    planting melons after day 8 (a melon maturing past ~day 18 will be worth $1).
  * WOOL: its wool dump floors the market from day ~10.  Sell wool at anything >= 35
    through day 12 rather than hold stock the market will never pay for again.
Verified byte-identical vs non-tape opponents (4-seed exact-mirror check).  Vs the tape:
margin -48.5k (v8: -54.0k, v7: -59.5k), sd 10.5k (was 16.0k); still 0-16 — the rest of
the gap is production, targeted next (strawberry volume, opening speed).
A/B record: v7a beat v7 51-13 over 64 (79.7%) | v6a beat v6 46-18 (71.9%) | v5b beat
v5 31-1 | v5a beat v4 27-5 | v4c beat v3 28-4 | v3a beat v2 30-2 | v2a beat v1 32-0 |
v1 beat v0 32-0.  Bank-diff risk (v7b): WASH, shelved for Phase 6.

Everything from v1 (task list, greedy assignment, stickiness, 4 hands, melon-12 + carrot mix,
day-29 endgame) plus the livestock pipeline:

  BUY_ANIMAL (-> shed) -> BUILD_PASTURE (free, 1 action) -> PICKUP animal at shed -> carry ->
  PLACE -> daily FEED (1 wheat from the unit's own inventory) + CARE + HARVEST + COLLECT_FERTILIZER.

Engine facts this file leans on (verified, docs/ENGINE_NOTES.md B):
  * FEED consumes WHEAT from the acting unit's PERSONAL inventory, not the shed (B.3) —
    someone must PICKUP wheat before walking the animal circuit.
  * BUY_ANIMAL / BUY_PRODUCT deliver into the shed and fail if it is full (B.3).
  * fertilizer_available is set for every SURVIVING animal every end-of-day, fed or not;
    it does not accumulate — collect daily or lose $98/day (B.7 / A).
  * Animal production ticks at the end of day t = placed_day + first_yield - 1 + k*interval.
    The LAST refresh of the game is end of day 28 (B.4): feeding/caring only pays if the
    animal still has a tick <= 28.  CARE banked on day d pays on the first tick STRICTLY
    after d (production is checked before the day's care is banked, B.4).
  * An animal unfed 2 consecutive days escapes BEFORE producing or making fertilizer (B.4).
  * Structures are free (no money check in BUILD_COOP/BUILD_PASTURE, engine L493-503).
"""
from __future__ import annotations

import math

DEBUG = False

# ----------------------------------------------------------------------------------
# Tunables
# ----------------------------------------------------------------------------------
TARGET_HANDS = 8         # scale retest: 10 hands at 3 quadrants ($143/day fib)
HANDS_PER_EXTRA_QUADRANT = 2
LAND_MAX_QUADRANTS = 4
LAND_DAYS = [6, 10, 99]   # v5b: retry the 3rd quadrant now that fert + cash bugs are fixed
LAND_PRICES = [1000, 2000, 4000]   # engine LAND_PRICES (ENGINE_NOTES B.1); order NE->SW->SE
# (crop mix now lives in CROP_INFO caps + PLANT_ORDER + SEED_WANT below)
LIQUIDATE_FROM_DAY = 28  # unsold inventory is worth $0 at the end — sell everything late
SHED_FORCE_SELL = 92     # v89c: was 80.  The express (v87) fills the shed
                         # same-day, so the any-price panic-dump fired
                         # chronically 20 slots early — live: ~5 floor-units/
                         # game sold at $1-3 with shed at 80-94 (cap is 100
                         # and overflow only destroys at end-of-day).
UNLOAD_AT = 8            # a unit carrying this many items runs them to the shed (sellable today)
PREM_BANK_BUSY = 6       # v87b: premium load (wool+milk+egg) that overrides a
                         # busy unit's non-FEED task for a shed run (idle bar is 4)

# Livestock plan: sheep first (slowest payout -> place earliest, CARE stacks highest on it),
# cows are the meta-proven workhorse. 6 animals ring the shed on one quadrant.
ANIMAL_TARGETS = {"SHEEP": 4, "COW": 9}   # v47a blueprint: cow-heavy (dead-milk guard -> 6 kept)
# v61a/v61d MILK-BOOM : in towns with THREE actual
# milk shops whose milk price is still >= $200 at d10-13, extend the cow
# target 9 -> 12.  Gate calibrated on 91 live replays (23% of towns; milk
# held $150-278 through d24 in ALL of them).  UP-side only .
COW_BOOM_FROM_DAY = 10
COW_BOOM_UNTIL_DAY = 13
COW_BOOM_PRICE = 200
COW_BOOM_TARGET = 12
# Day-0 all-in basket (v37d refactor: named so the shape search can move them).
D0_SHEEP = 2   # v47a blueprint basket: 2s+2c+12mel+7whe = $2,830 of $3,000
D0_COW = 2
D0_MELON = 8   # v55e: tiles leg — the 12-block squats the early quadrant (v55c/d fingerprints)
D0_WHEAT_SEED = 7
D0_FEED = 4    # v47a: basket+hires must clear $3,000 (2,942+12 with feed 4)
BUY_PRIORITY = ["GOOSE", "COW", "SHEEP"]   # v47a: cows first — milk from d8 IS the early engine
ANIMAL_INFO = {
    "GOOSE": {"cost": 300, "build": "BUILD_COOP", "first": 4, "interval": 1, "product": "EGG"},
    "COW":   {"cost": 400, "build": "BUILD_PASTURE", "first": 8, "interval": 2, "product": "MILK"},
    "SHEEP": {"cost": 500, "build": "BUILD_PASTURE", "first": 6, "interval": 3, "product": "WOOL"},
}
# Ring around the shed-access tile (4,4): FEED/CARE/HARVEST/COLLECT all happen standing ON
# the animal tile and the wheat lives at the shed, so clustering minimizes walking.
ANIMAL_SLOTS = [(3, 4), (4, 3), (3, 3), (2, 4), (4, 2), (2, 3), (3, 2), (2, 2),
                (4, 5), (3, 5), (2, 5), (4, 6),
                (3, 6), (2, 6), (4, 7)]   # +7 SW slots (v37a: 15-animal herd)
# v42b geese: slots are species-aware; adaptive target set per game in agent()
# once an egg shop is seen.  D0_GOOSE > 0 = blind day-0 goose bet (search gene;
# first egg day 4) — day-0 geese take the FRONT slots (nothing built yet),
# late-latched geese take the unbuilt TAIL (front pastures already stand).
D0_GOOSE = 0
_GOOSE_TARGET = {0: 0, 1: 0}
def _slot_species():
    order = ("GOOSE", "SHEEP", "COW") if D0_GOOSE else ("SHEEP", "COW", "GOOSE")
    out = []
    for _sp in order:
        n = _GOOSE_TARGET.get(_CUR_SEAT, 0) if _sp == "GOOSE" else ANIMAL_TARGETS.get(_sp, 0)
        out += [_sp] * n
    return out
def _slot_build(x, y):
    sl = _slot_species()
    i = ANIMAL_SLOTS.index((x, y)) if (x, y) in ANIMAL_SLOTS else 99
    return ANIMAL_INFO[sl[i] if i < len(sl) else "COW"]["build"]
def _home_kind(sp):
    return "COOP" if sp == "GOOSE" else "PASTURE"
MONEY_RESERVE = 50       # v37a: monsters hold zero reserves — assets compound, cash doesn't

# (batch, min_price, liquidation_day). Wheat doubles as animal feed: a reserve is held back
# (see WHEAT_FEED_RESERVE_DAYS) and the min price 30 (> base 25) means surplus only sells
# into scarcity, never at a loss against our own feed needs.
SELL_RULES = {
    "MELON":      (15, 60, 28),   # v47a: dump the whole d10 detonation as first mover
    "CARROT":     (10, 25, 28),
    "STRAWBERRY": (4, 100, 28),
    "MILK":       (3, 90, 28),
    "WOOL":       (3, 90, 28),
    "FERTILIZER": (5, 40, 28),
    "WHEAT":      (6, 18, 29),
    "TOMATO":     (4, 50, 28),
    "EGG":        (4, 30, 28),
}
NEVER_FORCE_SELL = {"WHEAT"}

# cap = max concurrent plants (market- or purpose-bound, not space-bound).
# Window (0,-1) = "watering never adds instant yield" (ongoing crops bonus only via fertilizer).
CROP_INFO = {
    "MELON":      {"cost": 80,  "first": 10, "ready": 10, "last_plant": 14, "window": (6, 12), "cap": 12},  # v57c: was last_plant 6 (one-shot); wave 2 gated below
    "WHEAT":      {"cost": 10,  "first": 2,  "ready": 4,  "last_plant": 27, "window": (2, 4),  "cap": 26},  # v68a: 24->27 — king replants wheat to d26-27 (his d26 board: 40 wheat vs our 20; our 24 fallow tiles d25-29 vs his 13); a d27 wheat still pays 1-2u x ~$40 for a $10 seed
    "STRAWBERRY": {"cost": 100, "first": 10, "ready": 10, "last_plant": 17, "window": (0, -1), "cap": 40},
    "CARROT":     {"cost": 20,  "first": 2,  "ready": 3,  "last_plant": 26, "window": (2, 3),  "cap": 0},
    "TOMATO":     {"cost": 50,  "first": 8,  "ready": 8,  "last_plant": 20, "window": (0, -1), "cap": 0},
}
TOMATO_SHOPS = ("PIZZA_SHOP", "FARMERS_MARKET")
TOMATO_CAP_PER_SHOP = 6      # cap = 6 per drawn tomato shop (max 12)
TOMATO_MIN_SIGNAL_PRICE = 55 # speculation floor (with 2+ shops drawn)
TOMATO_HINGE_CONFIRM = 85    # full commitment only above clear base-noise
# Bank-differential gamble (v24a): when losing by this much, take the
# EV-neutral tomato coin-flip that v22c measured (day>=15, price>=70).
BEHIND_GAMBLE_DEFICIT = 5000
BEHIND_TOMATO_DAY = 15
BEHIND_TOMATO_PRICE = 70
_GAMBLE_ON = {}              # per-seat sticky latch, reset at step 0

# Conditional early wheat factory (v31a).  The shop draw is public and one shop
# unlocks every 3 days (engine L867-891).  When the visible draw has NO
# strawberry eater and NO milk eater but at least one wheat eater, this is a
# dead-premium town — the herd family's worst bucket and exactly where the
# wheat-native prototype won .  Latch and start the wheat factory
# now instead of day 22.  Drain units: town center 1/day, multi-product shop
# 6/day, single-product 12/day — so <=1 means "no shop eats it at all" and
# >=7 means "at least one shop eats it".
WHEAT_TOWN_CHECK_DAY = 9     # first evaluation (3 draws visible; v31b — day 6
                             # fired on 2-bakery towns that turned premium)
WHEAT_TOWN_STR_CAP = 15      # latched: stop NEW strawberry planting above this
                             # (v30a evidence: freed tiles -> wheat is the win)
_WHEAT_TOWN = {}             # per-seat sticky latch, reset at step 0
_FACTORY_NOW = False         # set per agent() call: wheat factory active this turn
_DEAD_TOWN_NOW = False       # set per agent() call: dead-town latch this turn
_MEL_RACE = {}               # v80b: per-seat latch — opp melon tiles >=10 seen d4-8
                             # (91% d10-dump predictor, 64/91 live opponents).  The
                             # caravan pays vs detonators (+733/+1,453 killer/fast,
                             # seeds 712-750) and cost −1,079 vs Amitesh(mel7) —
                             # dawn labor buys nothing when the price holds all day.
_STICKY = {}                 # v40a: per-seat {unit_index: (x, y, op0)}, reset at step 0
_CUR_SEAT = 0                # v40a: set per agent() call so _assign can key _STICKY
# Planting priority when a tile opens up: melon (highest $/tile-day, tiny cap), wheat (feeds
# the herd — replaces market buys at scarcity prices), strawberry (biggest town demand:
# ~426/season median), carrot (fast filler, capped so we stop glutting our own market).
PLANT_ORDER = ["MELON", "STRAWBERRY", "TOMATO", "WHEAT", "CARROT"]

# v45a zone seeds: where a crop's FIRST plant anchors (afterwards the anchor is
# the centroid of its live plants, so blocks grow onto themselves).  The herd
# ring owns (2-4, 2-4) + (2-4, 5-6) + (4,7); melon sits W of it (fertilizer
# walks stay short), wheat below toward SW (feed flows to the shed), strawberry
# owns NE (unlocks d6, exactly when the ramp starts), carrot NW top, tomato
# deep NE beside the strawberries.
CROP_SEED_ANCHOR = {
    "MELON":      (3, 3),   # v47a: the wave sits ON the slot ring = future pastures
    "WHEAT":      (1, 6),
    "STRAWBERRY": (7, 2),
    "CARROT":     (1, 0),
    "TOMATO":     (9, 2),
}

def _crop_anchor(crop, crop_pos):
    pts = crop_pos.get(crop)
    if pts:
        return (sum(p[0] for p in pts) / len(pts),
                sum(p[1] for p in pts) / len(pts))
    return CROP_SEED_ANCHOR.get(crop, SHED_TILE)
SEED_WANT = {"MELON": 3, "WHEAT": 8, "STRAWBERRY": 8, "CARROT": 0, "TOMATO": 4}  # v47a: wheat engine
WHEAT_FEED_RESERVE_DAYS = 1   # hold animals*this much wheat before selling any surplus

# Endgame wheat factory (v13a).  Milestone diff vs the tape: it sells ~479 wheat at
# ~$40 ($19.4k) by converting freed premium tiles to wheat wall-to-wall late-game;
# wheat demand never gluts (6 shop types).  From this day, wheat stops being
# feed-sized and becomes the default cash crop for open land.
# Late premium->wheat conversion (v35a organ): dig dead-market premium
# plants from this day so the tile earns wheat/carrot instead.
ENDGAME_CONVERT_DAY = 19
ENDGAME_CONVERT_CROPS = ("STRAWBERRY", "MELON")
# v54i : the 2k class digs STR 30->15 across d22-26 and refills with
# wheat (40 tiles by d24) for the late wheat ramp; we held 33-36 STR to d26.
# From STR_CONVERT_DAY, idle (yield 0), old STR beyond the keep-count is dug
# so the d22 wheat factory (cap 45) has tiles to fill.
STR_CONVERT_DAY = 26   # v89a : 24 -> 26.  Live v87/v88 band losses:
                       # their d22-29 STR = 135u vs our 108, tiles@d28 10-11
                       # vs our 7-9 — the band's best hold LONGER than our
                       # d24 exit.  Same lane as v83a's 22->24 (strongest
                       # gate ever).  str_dead crash branch unchanged.
                       # (v83a history: was 22 — re-gate of v72a's wind-down)
STR_ENDGAME_KEEP = 38  # v89a: was 34 (v83a; orig 18).  v72a was closed on ONE pinned killer
# money-cell (−1,138) before the modern pipeline existed — a screen, not a
# gate, by our own later law.  Live ledger (43 v80b games): STR −$3,276/game
# is the biggest REAL remaining line (no consumption path — genuine sells),
# and the band keeps selling STR after our d22 exit.  str_dead branch
# (floored market: d18 / keep 6) UNCHANGED — the crash case stays covered.
STR_DEAD_FROM_DAY = 18   # v60a: market-aware wind-down may start here...
STR_DEAD_PRICE = 5       # ...when the 5-day glut projection is at/below this
STR_DEAD_CONFIRM_PX = 60 # v89b: AND the live price already confirms the crash —
                         # a projection-only trigger dug $164-221 plantations
STR_DEAD_KEEP = 6        # keepers in a dead market (was a static 18)

WHEAT_FACTORY_DAY = 13   # v68a : was 22.  King decode
# (4 pinned worlds): he sustains 22-40 wheat tiles d11-26 vs our 15-22 and
# NETS +$9.6k/game on wheat (404u sold at ~$40/u realized — 5/8 shops drain
# wheat into scarcity pricing; band tapes churned wheat at a loss, the king
# FARMS it).  d13 start: the STR cohort is fully planted by d12-13 and the
# melon detonation frees its tiles d10-12, so the factory takes leftovers,
# not cohort ground.
WHEAT_FACTORY_CAP = 45        # replaces CROP_INFO cap 20 from factory day
WHEAT_FACTORY_SEED_WANT = 10  # replaces SEED_WANT 4 from factory day

# Fertilize-only addition (v4c): a $90 fertilizer applied to a STRAWBERRY doubles its
# production ticks while watered (engine-verified) — ~$200+ of berries. Melon: reaches its
# 6-cap ~2 days earlier. Everything else is byte-identical to v3a.
FERT_STR_MIN_PX = 100    # v92b: STR fert coverage runs only while live STR px
                         # >= this (base 120; a flooded market runs 30-90 —
                         # doubling production there is doubling into a crash).
_FERT_STR_ON = False     # set per agent() call next to _FACTORY_NOW
# v92a : STR max_age
# 15 -> 26.  The (7,15) cap predates the v83a late-STR hold — tiles we now
# keep producing to d26-29 had their last 4-5 ticks UNCOVERED by design.
# Measured live: our fert-covered STR ticks 36% vs field 70% / band-killers
# 83%; each covered tick = +1 unit (engine L799-800, +2 vs +1) ~ $150-200.
# One op covers 3 days (L481) and STR ticks every 2 -> ANY in-window
# application covers >=1 tick.  ~+40 u/game ~ +$4-6k = the 756-900 band's
# whole mean deficit (-6,945).
FERT_CROPS = {"STRAWBERRY": (7, 26), "MELON": (6, 8)}   # crop -> (min_age, max_age)
# v58c: melon window ENGINE-ALIGNED — window_start = (12+1)//2 = 6, so an
# age-6 application covers ages 6-8 (fert lasts day..day+2) = 3 full +2 growth
# days = maxed 6 units by end of age 8, harvestable at the age-10 gate.
MELON_W2_FROM = 10       # v57c: second melon wave opens (berry flood already placed)
MELON_W2_CAP = 6
FERT_KEEP = 8            # v92a: was 0 (v57a) — with the window extended to age 26
                         # the application demand is ~13 ops/day at 40 tiles; keeping
                         # 0 sold the supply out from under the FERTILIZE tasks.
                         # (v57a original note: was 6 — the shed keep was redundant (crop applies
# are fed by the fert the circuit crews carry) and pinned 6 units out of the
# market while the price decayed; sell everything that reaches the shed
# v54a FERT FLYWHEEL : the 2k Prashant class applies ZERO fertilizer
# before day 10 and sells everything collected (45.9 units d5-9 vs our 3.9) —
# ~$98/unit is the cash that funds their cow-per-day ramp, and every new cow
# compounds it ($98/day more fert).  We were feeding melons instead (11 applies
# d5-9).  Fert is CASH during the ramp, an input after.
FERT_APPLY_FROM_DAY = 10

# Opponent-pressure-aware selling (Phase 5, v6a). The opponent's farm is PUBLIC every
# turn. When their visible capacity in a premium product is large, their dump is coming:
# the first seller gets the better price and a crashed market hurts the later seller more
# (measured by a competitor: selling harder cost them $4k and the opponent $11.8k). So
# under pressure we sell earlier (lower threshold) and faster (bigger batch); with no
# opposing capacity we hold for full price as usual. Tapes cannot respond to this.
OPP_PRESSURE = {
    #            how to count opponent capacity      trigger  threshold x  batch +
    "MILK":       ("animal", "COW",        4),
    "WOOL":       ("animal", "SHEEP",      3),
    "STRAWBERRY": ("crop",   "STRAWBERRY", 8),
    "MELON":      ("crop",   "MELON",      8),
}
PRESSURE_THRESHOLD_MULT = 0.65
PRESSURE_BATCH_BONUS = 3

# Doomed-market care skip (v12b).  A cared animal yields 1+interval units vs 1 —
# but if the product's market is projected at/near the floor when those units
# land (~3 days out), the care action is labor spent deepening a glut.  Skip CARE
# for that species while the projection stays doomed; everything else (FEED,
# COLLECT_FERTILIZER, HARVEST) continues.  Checked fresh every turn, so care
# resumes the moment the market recovers.
CARE_SKIP_PRICE = 15     # projected price at/below this = care not worth the turn
CARE_SKIP_HORIZON = 3    # days until a banked care bonus typically pays out
CARE_FLOOR_NOW = 8       # v71c: observed-price care gate — skip a species only
                         # while its product's CURRENT price is at/near the $1
                         # floor (units then realize ~nothing and cost labor +
                         # sell slots).  No projection (that model is falsified
                         # 4x); town drain lifts price -> care resumes same turn.

# Tape-family counter (v7c).  Fingerprint: the meta tape places exactly 4 SHEEP and
# its first COW on day 0 (visible from day 1); we field 3 sheep and no cow then, so
# there is no self-detection.  Checked on days 1-3 and latched for the episode.
# STALENESS WARNING: the wave timings below are decoded from the CURRENT public tape
# (2026-08-24).  If the meta shifts openings the latch simply stops firing (fail-safe),
# but a NEW tape with the same opening and a different sell schedule would make these
# timed dumps wrong — re-verify weekly against fresh top-ladder replays.
TAPE_MELON_LAST_PLANT = 8    # a melon maturing after ~day 18 sells into their wave's wreckage
TAPE_WOOL_SALVAGE_UNTIL = 12
TAPE_WOOL_SALVAGE = 35
TAPE_MELON_SOFT_DAY = 15     # sell melons at >= 60 from here...
TAPE_MELON_SOFT = 60
TAPE_MELON_DUMP_DAY = 18     # ...and at any price from here (their wave lands day 20)
TAPE_MELON_DUMP = 10
_TAPE_SEEN = {}              # player -> latched?  (reset at step 0 each episode)

# v50a : the tape's COMPLETE sell schedule, extracted from its embedded
# action list (open-loop => identical every game).  (step, units) for every
# sell order of 5+ units.  Front-run rule: if a wave of >= TAPE_FR_MIN units
# lands within TAPE_FR_HORIZON turns, dump our stock of that item NOW at a
# deep-discount threshold — any price before their wave beats any price after.
TAPE_SELLS = {
    "FERTILIZER": ((48,5), (72,5), (96,5), (120,5), (144,5), (192,7), (216,10), (241,16), (276,12), (299,10), (316,16), (341,9), (411,7), (422,14), (527,14), (534,8), (558,5), (588,5), (598,10), (608,5), (617,6), (626,9), (648,5), (649,7), (662,6), (672,5), (687,5), (690,8), (696,5), (701,5), (718,5)),
    "MELON": ((252,10), (255,6), (257,11), (260,6), (262,6), (486,6), (488,6), (490,12), (492,6), (493,10), (495,6), (496,6), (502,15), (503,6), (504,14)),
    "MILK": ((302,6), (358,13), (362,6), (377,12), (406,24), (431,7), (451,8), (455,9), (480,6), (484,7), (502,9), (523,14), (551,13), (553,8), (555,9), (587,10), (599,12), (618,8), (638,10), (648,7), (665,12), (666,9), (690,8), (702,18), (703,18), (715,18)),
    "STRAWBERRY": ((400,8), (405,14), (432,28), (472,12), (479,16), (480,20), (504,18), (522,10), (528,30), (552,24), (575,13), (594,20), (609,17), (615,13), (645,16), (651,11), (701,22)),
    "WHEAT": ((1,9), (150,17), (211,6), (222,7), (278,11), (308,12), (312,24), (405,5), (467,19), (503,5), (522,7), (543,12), (596,20), (597,9), (609,31), (624,30), (632,7), (668,10), (672,46), (694,6), (696,53), (713,16), (715,26), (716,22), (717,36), (718,7)),
    "WOOL": ((160,9), (168,17), (240,18), (361,8), (380,8), (419,12), (427,13), (453,12), (568,8), (583,8), (634,6), (661,10), (669,17), (682,8)),
}
TAPE_FR_HORIZON = 10    # turns of look-ahead
TAPE_FR_MIN = 8         # units of incoming wave that trigger the front-run
TAPE_STR_CAP = 24       # tape floods 300 STR units d16-29 (~21/day) — never
                        # plant into it beyond this
TAPE_WHEAT_ENDGAME = 22 # their 196-unit wheat dump lands d25-29; liquidate
                        # surplus wheat from d22 at threshold 20

def _tape_wave_within(item, step):
    tot = 0
    for s, n in TAPE_SELLS.get(item, ()):
        if step < s <= step + TAPE_FR_HORIZON:
            tot += n
    return tot

# ---------------------------------------------------------------------------
# Rational sell thresholds (v7a).  The engine's glut-side price curve, verbatim
# (ENGINE_NOTES B.1, engine L41-74): price = base - target*base*f(x)/f(T),
# floored at $1, where x = market_inventory - I0 (I0 = 10,000).
# If even the town's full drain until liquidation day cannot lift the price back
# above our static threshold, the static threshold is a fantasy — accept the best
# still-reachable price instead of holding the stock down to the $1 floor.
# ---------------------------------------------------------------------------
MARKET_I0 = 10000
MARKET_ABOVE = {
    #             base   T    func      target
    "WOOL":       (200, 105, "sq",     3.2),
    "MILK":       (160, 122, "linear", 1.6),
    "MELON":      (250, 300, "sq",     3.6),
    "STRAWBERRY": (120, 100, "linear", 1.6),
    "CARROT":     (35,  450, "sqrt",   0.7),
    "TOMATO":     (60,  200, "sqrt",   0.6),
    "FERTILIZER": (100, 200, "linear", 0.4),
}

# Engine SHOPS map (verified verbatim vs source).  Single-product shops consume
# 2x.  Each instance ticks every 4 turns (6x/day); the town center additionally
# eats 1/day of everything except fertilizer.
SHOP_DEMAND = {
    "BAKERY":         ("EGG", "WHEAT"),
    "PIZZA_SHOP":     ("MILK", "TOMATO", "WHEAT"),
    "BRUNCH_SPOT":    ("EGG", "WHEAT", "STRAWBERRY"),
    "YARN_STORE":     ("WOOL",),
    "ICE_CREAM_SHOP": ("STRAWBERRY", "MILK", "WHEAT"),
    "PET_CAFE":       ("CARROT",),
    "SMOOTHIE_SHOP":  ("STRAWBERRY", "MILK"),
    "FARMERS_MARKET": ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY"),
}


def _glut_price(item, x):
    """Engine price at net glut x units past I0 (above branch only)."""
    base, T, func, target = MARKET_ABOVE[item]
    if x <= 0:
        return base
    if func == "linear":
        f = x / T
    elif func == "sq":
        f = (x / T) ** 2
    elif func == "sqrt":
        f = (x / T) ** 0.5
    else:  # log
        f = math.log1p(x) / math.log1p(T)
    return max(1, int(round(base * (1.0 - target * f))))


def _town_drain_per_day(item, shops):
    d = 0 if item == "FERTILIZER" else 1          # town center, 1/day
    for s in shops:
        prods = SHOP_DEMAND.get(s, ())
        if item in prods:
            d += 6 * (2 if len(prods) == 1 else 1)
    return d



# v42a: expected FUTURE demand.  Any future shop is a uniform draw over the 8
# types (with replacement, engine L891), so E[drain gain] per remaining unlock
# for item P = (types carrying P / 8) * 6 * multiplier.  This is what stops the
# premature kills v41a showed: at day 9 five shops are still unseen and a
# strawberry buyer arrives later with prob 1-(1-4/8)^5.
_PROJ_GAIN = {}   # item -> expected drain/day contributed by ONE future unlock
for _it in ("WHEAT", "STRAWBERRY", "MILK", "EGG", "TOMATO", "CARROT", "WOOL", "MELON"):
    _g = 0.0
    for _prods in SHOP_DEMAND.values():
        if _it in _prods:
            _g += 6 * (2 if len(_prods) == 1 else 1)
    _PROJ_GAIN[_it] = _g / 8.0

def _proj_drain_per_day(item, shops, day):
    remaining = max(0, min(8, (30 - day) // 3 + (0 if day % 3 else 0)) )
    remaining = min(remaining, 8 - len(shops))
    return _town_drain_per_day(item, shops) + remaining * _PROJ_GAIN.get(item, 0)

# Dynamic STR cap: scale the tuned default (40 @ typical projected drain ~25/day)
# by this town's projection.  Ratchet: only recomputed at hour 0; never above 48
# (search bound), never below 12; and it can only DROP from day 6 (2+ shops seen).
def _dyn_str_cap(shops, day):
    proj = _proj_drain_per_day("STRAWBERRY", shops, day)
    cap = int(round(40 * proj / 25.0))
    cap = max(12, min(40, cap))
    if day < 6:
        cap = max(cap, 40)
    return cap
_DYN_STR_CAP = {0: 40, 1: 40}   # per seat, refreshed at hour 0
# v47b: the blueprint drops carrots by DEFAULT (most towns barely drain them),
# but a PET_CAFE town eats 12-36/day — seed-12 disaster: 3x PET_CAFE, we
# planted zero carrots, v45a monetized the town's only demand and won.
_DYN_CARROT_CAP = {0: 0, 1: 0}  # per seat, refreshed at hour 0
# v47b: YARN_STORE towns (12-24 wool/day) reward a bigger flock than the
# blueprint's 4 — all three remaining screen losses were yarn towns.
_DYN_SHEEP = {0: 4, 1: 4}       # per seat, refreshed at hour 0
YARN_SHEEP = 6                  # v57b: sheep target in latched yarn towns
_YARN_TOWN = {0: False, 1: False}
_COW_BOOM = {0: False, 1: False}   # v61d: sticky milk-boom latch, reset at step 0
_SLOT_NEED = {0: 13, 1: 13}     # live cow+sheep+goose target sum, set per call

def _inflow_per_day(item, crops, animals):
    """Rough units/day BOTH-farms production feeding this market (cared/watered rates)."""
    if item == "WOOL":
        return animals.get("SHEEP", 0) * 1.33     # cared sheep: 4 wool / 3 days
    if item == "MILK":
        return animals.get("COW", 0) * 1.5        # cared cow: 3 milk / 2 days
    if item == "FERTILIZER":
        return float(sum(animals.values()))       # 1/animal/day, fed or not
    if item == "MELON":
        return crops.get("MELON", 0) * 0.6        # 6 units / ~10-day cycle
    if item == "STRAWBERRY":
        return crops.get("STRAWBERRY", 0) * 0.75  # fertilized ongoing ~1.5 / 2 days
    if item == "CARROT":
        return crops.get("CARROT", 0) * 1.0       # 3 units / 3-day cycle
    return 0.0


def _opp_capacity(opp_tiles):
    """Count the opponent's visible production sources by kind."""
    crops = {}
    animals = {}
    for row in opp_tiles:
        for t in row:
            if isinstance(t, dict):
                if t.get("kind") == "PLANT":
                    crops[t.get("crop")] = crops.get(t.get("crop"), 0) + 1
                elif t.get("animal"):
                    animals[t["animal"]] = animals.get(t["animal"], 0) + 1
    return crops, animals

SHED_TILE = (4, 4)
LAST_DAY = 29
LAST_TICK_DAY = 28       # the game's final end-of-day refresh (ENGINE_NOTES B.4)

# Task priorities (lower = more urgent)
P_SAVE = 0     # plant/animal that is lost tonight if ignored
P_FEED = 1
P_HARVEST = 1
P_CHAIN = 1    # supply-chain steps: PICKUP wheat/animal, PLACE animal
P_WATER = 2
P_CARE = 2
P_COLLECT = 3  # fertilizer: $98/day, but re-offered tomorrow if missed
P_FERT = 3     # apply fertilizer to a strawberry/melon in its payoff window
P_PLANT = 3
P_BUILD = 3
P_UNLOAD = 3
P_DIG = 4
P_IDLE = 5   # v96c: idle tier, CARE-ONLY (no glut pathway)


def _step_toward(fx, fy, tx, ty):
    if fx < tx:
        return "EAST"
    if fx > tx:
        return "WEST"
    if fy < ty:
        return "SOUTH"
    if fy > ty:
        return "NORTH"
    return None


def _next_tick_day(placed_day, first, interval, after_day):
    """First production tick day STRICTLY after `after_day`, or None if past day 28."""
    first_tick = placed_day + first - 1
    if first_tick > after_day:
        t = first_tick
    else:
        t = first_tick + interval * ((after_day - first_tick) // interval + 1)
    return t if t <= LAST_TICK_DAY else None


CROP_SKIP_PRICE = 15     # crop's 3-day projected price at/below this = its labor
                         # (water/rescue/replant) is spent on worthless goods

def _crop_skip(tiles, opp_tiles, market_inv, shops):
    """Crops whose market is projected dead — stop watering/planting them."""
    skip = set()
    my_crops, my_animals = _opp_capacity(tiles)
    opp_crops, opp_animals = _opp_capacity(opp_tiles)
    # MELON/CARROT only: melon's town drain is ~1/day so a floored melon market
    # never recovers (safe to abandon); carrot is cheap filler.  STRAWBERRY is
    # excluded — its drain is the biggest in the game, gluts PASS, and v15e
    # (which could skip it) lost its out-of-sample batch 17-15 with -1.2k/5.6k sd:
    # abandoning 35 strawberries during a transient dip is catastrophic.
    for crop in ("MELON", "CARROT", "TOMATO"):
        if crop not in MARKET_ABOVE:
            continue
        x = market_inv.get(crop, MARKET_I0) - MARKET_I0
        net = (_town_drain_per_day(crop, shops)
               - _inflow_per_day(crop, my_crops, my_animals)
               - _inflow_per_day(crop, opp_crops, opp_animals))
        proj = _glut_price(crop, max(0, x - net * CARE_SKIP_HORIZON))
        if proj <= CROP_SKIP_PRICE:
            skip.add(crop)
    return skip


def _care_skip_species(tiles, opp_tiles, market_inv, shops):
    """Species whose product market is projected dead when a care bonus would land."""
    skip = set()
    my_crops, my_animals = _opp_capacity(tiles)
    opp_crops, opp_animals = _opp_capacity(opp_tiles)
    for sp, info in ANIMAL_INFO.items():
        item = info["product"]
        if item not in MARKET_ABOVE:
            continue
        x = market_inv.get(item, MARKET_I0) - MARKET_I0
        net = (_town_drain_per_day(item, shops)
               - _inflow_per_day(item, my_crops, my_animals)
               - _inflow_per_day(item, opp_crops, opp_animals))
        proj = _glut_price(item, max(0, x - net * CARE_SKIP_HORIZON))
        if proj <= CARE_SKIP_PRICE:
            skip.add(sp)
    return skip


def _build_tasks(tiles, day, seeds, tape_mode=False, care_skip=(), crop_skip=(),
                 ramp_fast=False, tomato_cap=0, str_dead=False):
    """Scan the farm -> the turn's task list. Returns (tasks, n_feed_needed)."""
    tasks = []
    # v54i endgame conversion budget (see STR_CONVERT_DAY above)
    # v60a: in a projected-dead STR market the wind-down starts earlier and
    # keeps fewer producers (their units sell at the floor; the keep-18 made
    # the measured 84-120 $1-2 floor sells d22-28).
    _str_digs_left = 0
    _convert_from = STR_DEAD_FROM_DAY if str_dead else STR_CONVERT_DAY
    _keep = STR_DEAD_KEEP if str_dead else STR_ENDGAME_KEEP
    if day >= _convert_from and day < LAST_DAY:
        _str_now = sum(1 for _row in tiles for _t in _row
                       if isinstance(_t, dict) and _t.get("kind") == "PLANT"
                       and _t.get("crop") == "STRAWBERRY")
        _str_digs_left = max(0, _str_now - _keep)
    crop_counts = {}
    crop_pos = {}      # v45a: live plant positions per crop -> cluster centroids
    empty_tiles = []
    n_feed = 0
    # v47a DYNAMIC reservation: only hold slots ~2 ahead of animals actually
    # here — the old full-target reservation sterilized 13 tiles from day 0.
    # Blueprint choreography: day-0 melons PLANT on the unreserved tail slots
    # and detonate d10 exactly as cows 5-9 arrive to take those tiles (a slot
    # still carrying a plant simply defers its build until the harvest).
    _n_slots_total = _SLOT_NEED.get(_CUR_SEAT,
                                    sum(ANIMAL_TARGETS.values()) + _GOOSE_TARGET.get(_CUR_SEAT, 0))
    _placed_now = sum(1 for row in tiles for t in row
                      if isinstance(t, dict)
                      and (t.get("animal") or t.get("kind") in ("COOP", "PASTURE")))
    # v54f: floor raised 4 -> 8.  The v54e fert-flywheel ramp buys cows 3-8 on
    # d3-8, but melons anchored on the ring stranded them in the shed until the
    # d10 detonation (measured: 8 in-shed animal-days by d9 = dead capital).
    # 8 clear slots hold the whole early wave; melons shift to non-ring tiles.
    reserved = set(ANIMAL_SLOTS[:min(_n_slots_total, max(8, _placed_now + 2))])

    for y, row in enumerate(tiles):
        for x, t in enumerate(row):
            if t == "LOCKED":
                continue
            if t is None:
                if (x, y) in reserved:
                    # Animal slot without a structure yet: build it (free, 1 action).
                    if day < LAST_DAY:
                        tasks.append({"prio": P_BUILD, "x": x, "y": y, "op": [_slot_build(x, y)]})
                else:
                    empty_tiles.append((x, y))
                continue
            if not isinstance(t, dict):
                continue
            kind = t.get("kind")

            if kind == "WEED":
                if day < LAST_DAY:
                    tasks.append({"prio": P_DIG, "x": x, "y": y, "op": ["DIG"]})
                continue

            # ---------------- animals (any tile dict carrying an "animal" key) ----------
            if "animal" in t and t["animal"]:
                info = ANIMAL_INFO.get(t["animal"])
                if info is None:
                    continue
                placed = t.get("placed_day", 0)
                cu = t.get("consecutive_unfed", 0)

                if t.get("yield_units", 0) > 0:
                    tasks.append({"prio": P_HARVEST, "x": x, "y": y, "op": ["HARVEST"]})

                if t.get("fertilizer_available", False):
                    tasks.append({"prio": P_COLLECT, "x": x, "y": y,
                                  "op": ["COLLECT_FERTILIZER"]})

                if not t.get("fed_today", False) and day <= LAST_TICK_DAY:
                    # Feed only while it still pays: a tick today-or-later, or the animal
                    # would escape tonight and cut off the daily fertilizer stream.
                    tick_ahead = _next_tick_day(placed, info["first"], info["interval"], day - 1)
                    if tick_ahead is not None or cu >= 1:
                        n_feed += 1
                        # v61c : a TICK-DAY feed gates that tick's whole
                        # payout (engine L813: unfed = no production; L826: unfed
                        # also burns the stacked care bonus), yet it competed at
                        # P_FEED=1 against the tick day's own harvest burst and
                        # lost (measured seed 144: 16 feeds on off-days, 10-11 on
                        # tick days, same 6 cows starved nightly).  Same fix
                        # class as v58c's melon-day priority.
                        _feed_prio = P_SAVE if (cu >= 1 or tick_ahead == day) else P_FEED
                        tasks.append({"prio": _feed_prio, "x": x, "y": y,
                                      "op": ["FEED"], "require": "WHEAT"})

                if not t.get("cared_today", False):
                    # CARE banked on day d pays on the first tick AFTER d (must be <= 28).
                    if _next_tick_day(placed, info["first"], info["interval"], day) is not None:
                        # v96c: floored-product animals CARE at P_IDLE
                        # instead of dropping (cared tick = +1 unit; joins
                        # liquidation).  No crop supply added -> no self-
                        # glut pathway, unlike v96a's waters.
                        _cp = P_IDLE if t["animal"] in care_skip else P_CARE
                        tasks.append({"prio": _cp, "x": x, "y": y, "op": ["CARE"]})
                continue

            # Empty structure (no animal yet): nothing to do here; PLACE is handled by
            # the carrier override in _assign.
            if kind in ("COOP", "PASTURE"):
                continue

            # ---------------- plants (same rules as v1) --------------------------------
            if kind == "PLANT":
                crop = t.get("crop")
                info = CROP_INFO.get(crop)
                age = day - t.get("planted_day", day)
                dying = t.get("consecutive_unwatered", 0) >= 1 and not t.get("watered_today", False)
                crop_counts[crop] = crop_counts.get(crop, 0) + 1
                crop_pos.setdefault(crop, []).append((x, y))

                ready_age = info["ready"] if info else 10
                first_age = info["first"] if info else ready_age
                harvestable = t.get("yield_units", 0) > 0 and (
                    age >= ready_age or (day == LAST_DAY and age >= first_age)
                )
                if harvestable:
                    _hprio = P_SAVE if dying else P_HARVEST
                    if crop == "MELON" and day == 10:
                        # v58c: win the day-10 melon race — at shared prio 1
                        # the ring's feed/care tasks starved the harvests
                        # until h14-18 (traced), landing the crop in the
                        # h16 field-wide dump.
                        _hprio = P_SAVE
                    tasks.append({"prio": _hprio, "x": x, "y": y,
                                  "op": ["HARVEST"]})
                    continue

                # v54i: endgame STR->WHEAT conversion — dig idle old strawberries
                # beyond the keep-count so wheat can take the tile.
                if (crop == "STRAWBERRY" and _str_digs_left > 0
                        and (t.get("yield_units", 0) == 0 or str_dead)
                        and age >= 14):
                    tasks.append({"prio": P_DIG, "x": x, "y": y, "op": ["DIG"]})
                    _str_digs_left -= 1
                    continue

                # Doomed-crop triage (v15e): its market is projected dead, so its
                # water/rescue labor buys $1 goods — spend those unit-turns on live
                # crops and animals instead.  Harvests above still run (they free
                # the tile); the plant may weed and gets dug at leisure (P_DIG).
                if crop in crop_skip:
                    # Late conversion (v35a organ): dig the abandoned plant
                    # now instead of letting it weed out over days.
                    if (day >= ENDGAME_CONVERT_DAY and day < LAST_DAY
                            and crop in ENDGAME_CONVERT_CROPS):
                        tasks.append({"prio": P_DIG, "x": x, "y": y, "op": ["DIG"]})
                    continue

                if not t.get("watered_today", False):
                    if day == LAST_DAY:
                        if info and info["window"][0] <= age <= info["window"][1]:
                            tasks.append({"prio": P_WATER, "x": x, "y": y, "op": ["WATER"]})
                    else:
                        # v56a ALTERNATE-DAY WATERING (engine verified):
                        # base production NEVER requires water — ongoing crops
                        # tick on pure day arithmetic (L789-800, water only
                        # gates the fert +2), one-shot crops grow ONLY on
                        # watered window-days (L438-443), and a plant weeds
                        # only at 2 consecutive dry days (L783).  Water only:
                        #  (a) dying (unwatered==1) — P_SAVE, dies tonight;
                        #  (b) one-shot inside its bonus window (water=yield);
                        #  (c) ongoing with active fert on a tick night
                        #      (tick at END of day D when (age+1-first) %
                        #      interval == 0; keep the +2).
                        _needed = dying
                        if not _needed and info:
                            _w0, _w1 = info["window"]
                            if _w1 >= _w0:
                                _needed = _w0 <= age <= _w1   # one-shot growth day
                            elif t.get("fertilized_until_day", -1) >= day:
                                _ivl = 2 if crop == "STRAWBERRY" else 1
                                _needed = (age + 1 - first_age >= 0
                                           and (age + 1 - first_age) % _ivl == 0)
                        if _needed:
                            tasks.append({"prio": P_SAVE if dying else P_WATER,
                                          "x": x, "y": y, "op": ["WATER"]})

                if crop in FERT_CROPS and (
                        FERT_APPLY_FROM_DAY <= day < (27 if _FERT_STR_ON else 26)   # v92a/b: d26 op covers d26-28 ticks; v89c cap when gate off
                        # v58c: melons are the exception to the fert flywheel —
                        # their whole growth window (ages 6-8 for the d0 wave)
                        # closes before day 10, and one $85 fert there buys +3
                        # units (~$600) plus a pre-wave d10 sell.
                        or (crop == "MELON" and 6 <= day < FERT_APPLY_FROM_DAY)):
                    lo, hi = FERT_CROPS[crop]
                    _fp = P_FERT
                    _parity_ok = True
                    if crop == "STRAWBERRY":
                        # v92b price gate: coverage machine (window to 26,
                        # P_WATER prio — the P3 tier measurably starves) only
                        # while the STR market is worth doubling into; else
                        # exact v89c behavior (window 7-15, P_FERT).
                        if _FERT_STR_ON:
                            # v93d2: P_CHAIN — with tick-day-only emission the
                            # demand is ~10 ops on alternate days, each worth
                            # $150-400 (>= any same-tier op); at P_WATER the
                            # urgent tier kept carriers busy and only 2.7/day
                            # executed (need ~10 on tick days).  Harvests it
                            # outranks by distance re-offer next hour.
                            _fp = P_CHAIN
                            # v93d TICK-DAY PARITY (Artyom's measured recipe:
                            # 98% of his 80 applications land ON tick days,
                            # watered same night 96% -> 1.85 ticks/op vs our
                            # 0.8).  Apply only when the tile ticks TONIGHT;
                            # the 3-day cover then catches tonight + day+2.
                            _dsf = age + 1 - 10
                            # (no pre-production exemption: an age-7/8 op
                            # is 1-tick value, lands 'off-tick', and its
                            # 3-day cover suppresses the first true tick-day
                            # application — measured: it ate most of the ON-
                            # window ops.  Artyom: 98% pure tick-day.)
                            _parity_ok = _dsf >= 0 and _dsf % 2 == 0
                        else:
                            hi = 15
                    if (lo <= age <= hi and _parity_ok
                            and t.get("fertilized_until_day", -1) < day):
                        tasks.append({"prio": _fp, "x": x, "y": y,
                                      "op": ["FERTILIZE"], "require": "FERTILIZER"})
                continue

    # v61d: boom pastures on fallow tiles (ring holds 15 slots and its tail
    # slots carry strawberries until d22 — without this the boom cows
    # shed-strand; latch-gated so unfired games stay byte-identical).
    if _COW_BOOM.get(_CUR_SEAT, False) and day < LAST_DAY:
        _deficit = _n_slots_total - _placed_now
        if _deficit > 0 and empty_tiles:
            _ax, _ay = ANIMAL_SLOTS[0]
            empty_tiles.sort(key=lambda p: abs(p[0] - _ax) + abs(p[1] - _ay))
            for _ in range(min(_deficit, len(empty_tiles))):
                _bx, _by = empty_tiles.pop(0)
                tasks.append({"prio": P_BUILD, "x": _bx, "y": _by,
                              "op": ["BUILD_PASTURE"]})

    # ---------------- planting: fill empty tiles by PLANT_ORDER, respecting caps --------
    # Caps are market-bound (melon/carrot glut their price) or purpose-bound (wheat = feed),
    # so extra land raises variety, not just volume. Capped by seeds actually held (the
    # PLANT collective-validation trap) so no unit ever walks to an unplantable tile.
    if day < LAST_DAY:
        budget = dict(seeds)
        planned = dict(crop_counts)
        want = []              # this turn's plant multiset — the conditions
        for _ in empty_tiles:  # below never read tile coords, so the multiset
            crop = None        # is identical to the old raster-order loop's
            for c in PLANT_ORDER:
                info = CROP_INFO[c]
                cap = info["cap"]
                if c == "WHEAT" and _FACTORY_NOW:
                    cap = WHEAT_FACTORY_CAP
                if c == "MELON" and day > 6:
                    # v57c MELON SUSTAIN: small 2nd wave d10-14 (after the
                    # berry flood takes its tiles) into the recovered price;
                    # the band banks ~$2k/game d15-21 melons where we sold 0.
                    cap = MELON_W2_CAP if day >= MELON_W2_FROM else 0
                if c == "STRAWBERRY":
                    cap = min(cap, _DYN_STR_CAP.get(_CUR_SEAT, 40))
                    if tape_mode:
                        # v50a: never plant into their 300-unit d16-29 flood
                        cap = min(cap, TAPE_STR_CAP)
                if c == "TOMATO":
                    cap = tomato_cap
                if c == "CARROT":
                    cap = max(0, _DYN_CARROT_CAP.get(_CUR_SEAT, 0) - tomato_cap)
                if (planned.get(c, 0) < cap and day <= info["last_plant"]
                        and budget.get(c, 0) > 0
                        and c not in crop_skip
                        and not (tape_mode and c == "MELON"
                                 and day > TAPE_MELON_LAST_PLANT)):
                    crop = c
                    break
            if crop is None:
                continue
            planned[crop] = planned.get(crop, 0) + 1
            budget[crop] -= 1
            want.append(crop)
        # v45a CLUSTERED ASSIGNMENT: each crop takes the free tiles nearest its
        # anchor (centroid of its live plants, else its zone seed), so same-crop
        # plants grow as contiguous blocks and replants land back inside their
        # own block (a harvested tile is nearest its own crop's centroid).
        free = list(empty_tiles)
        # v47a: ONGOING crops never sit on future animal slots — a strawberry
        # there squats forever and deadlocks the build (found: sheep 3-4 stuck
        # in the shed all game).  Self-clearing crops (melon/wheat) are the
        # choreography and stay welcome.
        _full_slots = set(ANIMAL_SLOTS[:_n_slots_total])
        for c in PLANT_ORDER:
            n = sum(1 for w in want if w == c)
            if n == 0 or not free:
                continue
            pool = ([p for p in free if p not in _full_slots]
                    if c in ("STRAWBERRY", "TOMATO") else free)
            if not pool:
                continue
            ax, ay = _crop_anchor(c, crop_pos)
            pool.sort(key=lambda p: abs(p[0] - ax) + abs(p[1] - ay))
            # Fast ramp (v18c): post-herd, a strawberry planted this hour starts
            # its 10-day clock this hour; watering only matters by nightfall.
            # v67a: window-days STR plants ride at P_WATER even pre-herd — a
            # seed in hand is a 10-day clock not yet started; every hour it
            # waits is an hour of d15-21 income lost.
            prio = (P_WATER if (((ramp_fast or 2 <= day <= 9) and c == "STRAWBERRY")
                                or (c == "TOMATO" and tomato_cap > 4))
                    else P_PLANT)
            taken = pool[:n]
            for (x, y) in taken:
                tasks.append({"prio": prio, "x": x, "y": y, "op": ["PLANT", c]})
            _tk = set(taken)
            free = [p for p in free if p not in _tk]

    return tasks, n_feed


def _supply_tasks(tasks, n_feed, units, inventories, shed, tiles, day):
    """Shed-side chain steps: PICKUP wheat for feeders, PICKUP a bought animal."""
    if day >= LAST_DAY:
        return

    carried_wheat = sum(inv.get("WHEAT", 0) for inv in inventories)
    _feed_deficit = n_feed - carried_wheat
    if _feed_deficit > 0 and shed.get("WHEAT", 0) > 0:
        n = min(_feed_deficit + 2, shed["WHEAT"])
        # v61c : SECOND wheat carrier when the deficit is large.
        # One pickup task = one feeder walking the whole circuit; measured
        # (seed 144, 16 animals): the same far cows starved EVERY night while
        # wheat sat in the shed — the single carrier is a hard feed ceiling
        # (~10-11 feeds/day).  Two tasks = two carriers on parallel
        # sub-circuits; the focused-feeder rule already makes both
        # feed-exclusive while feeds are open.
        if _feed_deficit >= 6 and n >= 4:
            _h1 = n // 2
            tasks.append({"prio": P_CHAIN, "x": SHED_TILE[0], "y": SHED_TILE[1],
                          "op": ["PICKUP", "WHEAT", _h1]})
            tasks.append({"prio": P_CHAIN, "x": SHED_TILE[0], "y": SHED_TILE[1],
                          "op": ["PICKUP", "WHEAT", n - _h1]})
        else:
            tasks.append({"prio": P_CHAIN, "x": SHED_TILE[0], "y": SHED_TILE[1],
                          "op": ["PICKUP", "WHEAT", n]})

    # Fertilizer for FERTILIZE tasks: circuit units already carry some from
    # COLLECT_FERTILIZER; top up from the shed only when several plants are waiting.
    # PRIORITY MATTERS: at P_CHAIN(1) this errand outranked WATER(2) and the scheduler
    # yo-yoed units to the shed while crops died — measured: WATER 800->609, wheat
    # weeded out, 26 melon replants. Fertilizing is a luxury; restock at P_FERT(3).
    n_fert = sum(1 for t in tasks if t["op"][0] == "FERTILIZE")
    carried_fert = sum(inv.get("FERTILIZER", 0) for inv in inventories)
    # v93d: threshold 3->1 and P_FERT->P_CHAIN — carriers pocket only 1-3
    # units, so after ~7 tick-day applications the on-person supply is dry
    # and the P3 restock never executed (the choke measured at ~5 of ~10
    # needed ops per tick day, FERT_KEEP 8 sitting unused in the shed).
    if n_fert - carried_fert >= 1 and shed.get("FERTILIZER", 0) > 0:
        n = min(n_fert - carried_fert, shed["FERTILIZER"])
        tasks.append({"prio": P_CHAIN, "x": SHED_TILE[0], "y": SHED_TILE[1],
                      "op": ["PICKUP", "FERTILIZER", n]})

    # One animal-pickup per turn: an animal sits in the shed and an empty structure waits.
    _empties = set(t.get("kind") for row in tiles for t in row
                   if isinstance(t, dict) and t.get("kind") in ("PASTURE", "COOP")
                   and not t.get("animal"))
    if _empties:
        carrying = any(any(sp in inv for sp in ANIMAL_INFO) for inv in inventories)
        if not carrying:
            for sp in BUY_PRIORITY:
                if shed.get(sp, 0) > 0 and _home_kind(sp) in _empties:
                    tasks.append({"prio": P_CHAIN, "x": SHED_TILE[0], "y": SHED_TILE[1],
                                  "op": ["PICKUP", sp, 1]})
                    break


def _assign(units, tasks, inventories, tiles, day, hour):
    """{unit_index: task}. Carrier overrides, then stickiness, then greedy (prio, dist)."""
    assignment = {}
    taken = [False] * len(tasks)

    def inv_of(ui):
        return inventories[ui] if ui < len(inventories) else {}

    # Override 1: a unit carrying an animal delivers it to the nearest empty pasture.
    for ui, (ux, uy) in enumerate(units):
        inv = inv_of(ui)
        species = next((sp for sp in ANIMAL_INFO if inv.get(sp, 0) > 0), None)
        if species is None:
            continue
        best, best_d = None, 10**9
        for y, row in enumerate(tiles):
            for x, t in enumerate(row):
                if isinstance(t, dict) and t.get("kind") == _home_kind(species) and not t.get("animal"):
                    d = abs(x - ux) + abs(y - uy)
                    if d < best_d:
                        best, best_d = (x, y), d
        if best:
            assignment[ui] = {"prio": P_CHAIN, "x": best[0], "y": best[1],
                              "op": ["PLACE", species]}

    # v80a D10 MELON CARAVAN: the fast
    # copies (they beat us 88%; slow copies only 49%) put ONE unit on each ripe
    # melon tile by h5, clear all ~12 tiles by h9, and run every load straight
    # home — 45.8u sold by h13 at wavg $231 vs our 9.0u (same 12 tiles, same
    # 3-7 tile distance, same 0 hands at h0).  Our greedy gave the near animal
    # tasks to everyone first and the focused-feeder rule locked wheat carriers
    # out of harvests, so tiles cleared ONE PER HOUR h0-h22 and hands died at
    # midnight carrying 17u (auto-deposit sold d11 h0 at $156 vs $265 peak).
    # Husbandry legally shifts to the afternoon: fed/cared/watered are day-level
    # flags, and the family runs care/water heavy h16-23 on d10 (same decode).
    if day == 10 and hour <= 9 and _MEL_RACE.get(_CUR_SEAT, False):
        remembered0 = _STICKY.get(_CUR_SEAT, {})
        pairs = []
        for ti, t in enumerate(tasks):
            if taken[ti] or t["op"][0] != "HARVEST":
                continue
            tl = tiles[t["y"]][t["x"]] if 0 <= t["y"] < len(tiles) else None
            if not (isinstance(tl, dict) and tl.get("crop") == "MELON"):
                continue
            for ui, (ux, uy) in enumerate(units):
                # loaded units are the return leg (bank-run override below);
                # wheat carriers go last so dawn feeds keep one feeder.
                if ui in assignment or inv_of(ui).get("MELON", 0) > 0:
                    continue
                d = abs(t["x"] - ux) + abs(t["y"] - uy)
                if remembered0.get(ui) == (t["x"], t["y"], "HARVEST"):
                    d -= 2   # incumbent bias: keep walkers walking
                pairs.append((1 if inv_of(ui).get("WHEAT", 0) > 0 else 0,
                              d, t["y"] * 16 + t["x"], ui, ti))
        pairs.sort()
        for _w, _d, _, ui, ti in pairs:
            if ui in assignment or taken[ti]:
                continue
            assignment[ui] = tasks[ti]
            taken[ti] = True

    # Override 2 (day 29 only): loaded units must reach the shed and DROP by hour 22 or
    # their cargo is worth $0 (no end-of-day drop ever runs again). Leave just in time.
    if day == LAST_DAY:
        for ui, (ux, uy) in enumerate(units):
            if ui in assignment:
                continue
            inv = inv_of(ui)
            load = sum(inv.values())
            if load <= 0:
                continue
            dist = abs(ux - SHED_TILE[0]) + abs(uy - SHED_TILE[1])
            if hour >= 21 - dist:  # 1-turn safety margin before the hour-22 cutoff
                assignment[ui] = {"prio": P_SAVE, "x": SHED_TILE[0], "y": SHED_TILE[1],
                                  "op": ["DROP"]}

    def feeds_open():
        return any(t["op"][0] == "FEED" and not taken[ti]
                   for ti, t in enumerate(tasks))

    def eligible(ui, task):
        req = task.get("require")
        if req is not None and inv_of(ui).get(req, 0) <= 0:
            return False
        # FOCUSED FEEDER (v11e): while FEED tasks are pending, wheat carriers do
        # feeds ONLY.  Measured failure: the sole wheat carrier was assigned P_SAVE
        # crop rescues across the map and fed 2-6 of 12 animals/day from day 12 on —
        # an animal unfed on its production day wipes its whole banked care bonus.
        # Hands can rescue plants; only wheat carriers can feed.
        # v82a ZERO-WALK EXCEPTION: the family's signature stop is CARE+COLLECT+FEED
        # in ONE visit (87+47/game); ours was FEED alone (250/game) because
        # this veto blocked the care/collect task ON THE TILE THE FEEDER
        # STANDS ON — a second unit then re-walked the same tile.  A task at
        # the unit's own square costs zero movement and delays feeds by one
        # op only (we idle 11.9%); the veto stays for every task that needs
        # a walk.  Their ops/stop 1.59 vs our 1.33 is this line.
        # v82b FEED-SLACK GUARD: v82a's unconditional zero-walk chain doubled
        # unfed animal-days (9.4% vs 4.4%, seeds 8-11 both measured) — the
        # feeder chained care/collect mid-round and distant animals starved
        # past midnight (v61c law: an unfed tick-day burns the whole banked
        # bonus).  Chain only while the round still fits in the day:
        # ~2 turns per remaining feed (op + walk) + 2 margin.
        # v82c DETONATOR GATE on the chain: measured split — chain flips
        # +4/−2 wins vs the killer family but −8/+2 vs Amitesh(band)
        # (39 paired seeds each, 946-984).  Same asymmetry as the caravan,
        # same fix: family games only (_MEL_RACE, opp d0-cohort >=10);
        # band games revert to byte-v80b, where we already win 14/39.
        if (task["op"][0] != "FEED" and inv_of(ui).get("WHEAT", 0) > 0
                and feeds_open()):
            same_tile = (task["x"] == units[ui][0] and task["y"] == units[ui][1])
            pend = sum(1 for _ti, _t in enumerate(tasks)
                       if _t["op"][0] == "FEED" and not taken[_ti])
            # v88a : _MEL_RACE gate REMOVED — the chain runs in ALL
            # games.  The v82b close (+2/−8 flips vs Amitesh, 946-984) was
            # re-decoded seed-by-seed: the 3 biggest flips (971/948/983,
            # swings −11k to −22k) were ALL shop-draw re-rolls (tomato-
            # jackpot town lost, yarn town gained; own revenue UP in 2 of 3;
            # ops/unfed near-identical) — world lottery, not chain damage,
            # judged on a n.s. margin (−1,585±1,335).  The band runs chained
            # CARE+COLL+FEED stops everywhere (1.53 ops/stop vs our 1.34 =
            # +311 ops/game, re-based on v83a live).  Slack guard stays.
            if not (same_tile and 2 * pend + 2 <= 24 - hour):
                return False
        return True

    # Stickiness: finish the tile you stand on.
    for ui, (ux, uy) in enumerate(units):
        if ui in assignment:
            continue
        best = None
        for ti, task in enumerate(tasks):
            if taken[ti] or task["x"] != ux or task["y"] != uy or not eligible(ui, task):
                continue
            if best is None or task["prio"] < tasks[best]["prio"]:
                best = ti
        if best is not None:
            assignment[ui] = tasks[best]
            taken[best] = True

    remembered = _STICKY.get(_CUR_SEAT, {})

    def greedy(candidate_tis):
        """Most urgent first, nearest eligible unit wins, stable tie-break.
        Incumbent bias (v40a, from v33a): the unit already walking to a task
        gets a 2-tile discount, so another unit steals it only on a real win."""
        pairs = []
        for ti in candidate_tis:
            if taken[ti]:
                continue
            task = tasks[ti]
            for ui, (ux, uy) in enumerate(units):
                if ui in assignment or not eligible(ui, task):
                    continue
                d = abs(task["x"] - ux) + abs(task["y"] - uy)
                if remembered.get(ui) == (task["x"], task["y"], task["op"][0]):
                    d -= 2
                pairs.append((task["prio"], d, task["y"] * 16 + task["x"], ui, ti))
        pairs.sort()
        for prio, d, _, ui, ti in pairs:
            if ui in assignment or taken[ti]:
                continue
            assignment[ui] = tasks[ti]
            taken[ti] = True

    # Urgent work (saves, feeds, harvests, supply chains) is assigned globally — a dying
    # plant doesn't care about zones.
    greedy([ti for ti, t in enumerate(tasks) if t["prio"] < P_WATER])

    # v93d: FERTILIZE tasks matched to their carriers RIGHT AFTER the
    # urgent tier — before sticky-remembered re-glues carriers to
    # yesterday's routes and before zones deal them water anyone could do.
    # With tick-day parity above, each op lands the night it pays.
    greedy([ti for ti, t in enumerate(tasks)
            if not taken[ti] and t.get("require") and t["prio"] <= P_FERT])

    # STICKY TARGETS (v40a, from v33a): keep a still-valid routine target from
    # last turn.  Without this, the serpentine chunk boundaries shift every turn
    # as the task list changes and walking units get re-dealt mid-stride —
    # measured on v39a: 169-229 ping-pongs + 185-239 mid-walk U-turns per game,
    # 2.24 moves walked per work action.
    for ui in range(len(units)):
        if ui in assignment or ui not in remembered:
            continue
        tx, ty, top = remembered[ui]
        for ti, task in enumerate(tasks):
            if (not taken[ti] and task["x"] == tx and task["y"] == ty
                    and task["op"][0] == top and task["prio"] >= P_WATER
                    and eligible(ui, task)):
                assignment[ui] = task
                taken[ti] = True
                break

    # ZONED SWEEP for routine work (water/care/collect/plant/dig): order the remaining
    # tasks along a serpentine (row-by-row, alternating direction) and carve them into one
    # contiguous chunk per free unit, matched to units by the same ordering. Each worker
    # sweeps its own strip of farm instead of crisscrossing the whole board — walking was
    # 52-54% of unit-turns under pure global-greedy (reported competitive floor ~33%).
    def serp(x, y):
        return (y, x if y % 2 == 0 else 15 - x)

    low = [ti for ti, t in enumerate(tasks) if not taken[ti] and t["prio"] >= P_WATER]
    free = [ui for ui in range(len(units)) if ui not in assignment]
    if low and free:
        low.sort(key=lambda ti: serp(tasks[ti]["x"], tasks[ti]["y"]))
        free.sort(key=lambda ui: serp(units[ui][0], units[ui][1]))
        chunk = (len(low) + len(free) - 1) // len(free)
        for k, ui in enumerate(free):
            part = low[k * chunk:(k + 1) * chunk]
            ux, uy = units[ui]
            best, best_key = None, None
            for ti in part:
                if taken[ti] or not eligible(ui, tasks[ti]):
                    continue
                t = tasks[ti]
                key = (t["prio"], abs(t["x"] - ux) + abs(t["y"] - uy), t["y"] * 16 + t["x"])
                if best_key is None or key < best_key:
                    best, best_key = ti, key
            if best is not None:
                assignment[ui] = tasks[best]
                taken[best] = True

    # Cleanup: anything still unmatched (require-filtered tasks, empty chunks) falls back
    # to plain global greedy so no unit idles while work exists.
    greedy(range(len(tasks)))

    # v52b : FINAL-EVENING BANK RUN — from d29 h14, any loaded unit
    # overrides its task and runs its cargo in.  Goods deposited after ~h21
    # miss the remaining market turns and are DESTROYED at step 720; live
    # decode found 4 of 11 close losses stranded more value than the margin.
    # Units shuttle naturally: deposit -> empty -> harvest -> override again.
    if day >= LAST_DAY and hour >= 14:
        for ui, (ux, uy) in enumerate(units):
            if sum(inv_of(ui).values()) > 0:
                assignment[ui] = {"prio": P_UNLOAD, "x": SHED_TILE[0],
                                  "y": SHED_TILE[1], "op": ["DROP"]}

    # v58c MELON BANK-RUN, v80a tightened >=6 -> >=1: ANY melon in a pocket on
    # d10 runs home now (family cadence: one tile per trip, PLACE+SELL on
    # arrival).  The >=6 bar let a 5-load hand plant/water for hours and die
    # at midnight still carrying it (live trace ep108610904: 17u auto-
    # deposited at h24, sold d11 h0 at $156 vs the $265 peak).
    if day == 10 or (day == 11 and hour < 4):
        _melmin = 1 if _MEL_RACE.get(_CUR_SEAT, False) else 6  # v80b gate
        for ui, (ux, uy) in enumerate(units):
            if inv_of(ui).get("MELON", 0) >= _melmin:
                assignment[ui] = {"prio": P_UNLOAD, "x": SHED_TILE[0],
                                  "y": SHED_TILE[1], "op": ["DROP"]}

    # Idle-but-loaded units bank their cargo (sellable today instead of tomorrow),
    # but never while still carrying feed wheat for pending FEED tasks.
    feeds_pending = any(t.get("op", [None])[0] == "FEED" for ti, t in enumerate(tasks)
                        if not taken[ti])
    # v87b BUSY-UNIT PREMIUM BANK-RUN: milk rounds are never idle mid-game,
    # so v87a's idle-only express left 164 milk unit-nights/game riding
    # pockets overnight ($1,773/game of next-day price drop; wool $498;
    # measured across the 19 live band games).  A HEAVY premium load (>=6,
    # above the idle bar of 4 — the walk costs real hours) overrides any
    # non-FEED assignment; feeds stay sacred, and the hourly task re-emit
    # hands the carrier's dropped work to other units.
    for ui, (ux, uy) in enumerate(units):
        _inv = inv_of(ui)
        if ((_inv.get("WOOL", 0) + _inv.get("MILK", 0) + _inv.get("EGG", 0))
                >= PREM_BANK_BUSY
                and (assignment.get(ui, {}).get("op") or [None])[0] != "FEED"
                and not (feeds_pending and _inv.get("WHEAT", 0) > 0)):
            assignment[ui] = {"prio": P_UNLOAD, "x": SHED_TILE[0],
                              "y": SHED_TILE[1], "op": ["DROP"]}
    for ui, (ux, uy) in enumerate(units):
        if ui in assignment:
            continue
        inv = inv_of(ui)
        if ((sum(inv.values()) >= UNLOAD_AT
             or inv.get("FERTILIZER", 0) >= 1
             # v58c melon express: the whole field's d0 melons detonate d10
             # and the big families dump at h16 (steps 256-264, measured);
             # melons that ride in pockets until the nightly drop sell d11
             # into the crater — measured $214->158 vs $272 pre-wave.
             or inv.get("MELON", 0) >= 4
             # v87a premium-goods express : SELL
             # draws from the SHED only (engine L653), and wool/milk/eggs
             # sheared into pockets sat there until the midnight auto-drop —
             # measured hour-by-hour (ep109133507): 5 wool sheared d6 h5 at
             # $221 rode the pocket 19h and sold d7 — EVERY animal product
             # reached the market a day late, all game (~$1.1-2.2k of
             # working capital, and the band's d6 wool sale funds its d7-8
             # STR cohort while ours waits).  Same pattern as the fert
             # (v54d) and melon (v58c) expresses: bank at >=4 premium units.
             or (inv.get("WOOL", 0) + inv.get("MILK", 0)
                 + inv.get("EGG", 0)) >= 4)
                and not (feeds_pending and inv.get("WHEAT", 0) > 0)):
            # v54d fert express: collected fert rode in pockets until the nightly
            # drop and sold NEXT morning - the ramp's cash lagged ~20h every day.
            # v57a: express ALL GAME (was day<=12) — after d12 the circuit crews
            # accumulated 10-20 fert in pockets permanently while the price
            # decayed 75→19 (fert never recovers: zero town drain).  Measured
            # in the band losses: opponents execute ~103 fert units/game to
            # our ~40-60 .
            assignment[ui] = {"prio": P_UNLOAD, "x": SHED_TILE[0], "y": SHED_TILE[1],
                              "op": ["DROP"]}

    _STICKY[_CUR_SEAT] = {ui: (t["x"], t["y"], t["op"][0])
                          for ui, t in assignment.items()}
    return assignment


def _unit_action(unit_pos, task):
    if task is None:
        return ["PASS"]
    ux, uy = unit_pos
    if (ux, uy) == (task["x"], task["y"]):
        return list(task["op"])
    mv = _step_toward(ux, uy, task["x"], task["y"])
    return [mv] if mv else ["PASS"]


def _market_orders(day, hour, money, seeds, shed, inventories, prices, hires_today,
                   n_hands, tiles, n_quadrants, opp_tiles, market_inv, shops, tape_mode,
                   gamble=False):
    opp_crops, opp_animals = _opp_capacity(opp_tiles)
    my_crops, my_animals = _opp_capacity(tiles)
    """Queue order: SELL (income), HIRE, wheat, animals, LAND, seeds. Engine cap: 10."""
    orders = []

    placed_animals = sum(
        1 for row in tiles for t in row
        if isinstance(t, dict) and t.get("animal") in ANIMAL_INFO
    )

    # HIREs first: with 7 sellable products the 10-order cap could starve hour-0 hiring,
    # and a lost hand costs a whole day of labor while a delayed sale costs one turn.
    hands_target = TARGET_HANDS + HANDS_PER_EXTRA_QUADRANT * (n_quadrants - 1)
    if day <= 8:
        # v47a staged staffing: v44b PROVED early hands are idle wage-burners
        # (37.5% forcing 8 on the empty farm) — run lean until the melon
        # detonation, then the machinery fills 12 for the big-farm phase.
        hands_target = min(hands_target, 6)
    if hour <= 2 and day <= LAST_DAY:
        # v54j: hire on d29 as well — the 2k class runs 11 hands through the
        # final day's harvest+haul; we ran the complete liquidation with ZERO
        # hands (hands expire nightly and the old gate skipped d29 rehiring).
        # v44a machinery (retest at blueprint scale — dead heat on the small
        # farm): WAVE hiring hours 0-2 (queue caps at 10 orders/turn; the fib
        # ladder keys on hires_today so waves cost the same), want counts only
        # n_hands (subtracting hires_today double-counted filled hires).
        want_hires = max(0, hands_target - n_hands)
        if day == 0 and hour == 0:
            # v37a: leave order slots for the day-0 basket below (10-order cap).
            want_hires = min(want_hires, 5)
        # Payroll pre-sell: orders run IN LIST ORDER, so HIREs placed first are
        # judged on overnight cash — pre-sell shed stock ahead of them (wheat
        # excluded, feed is sacred).
        _FIB_CUM = [0, 1, 2, 4, 7, 12, 20, 33, 54, 88, 143, 232, 376, 609, 986]
        payroll_need = _FIB_CUM[min(hires_today + want_hires, 14)] \
            - _FIB_CUM[min(hires_today, 14)] - max(0, money)
        if payroll_need > 0 and day > 0:
            for it in ("FERTILIZER", "MILK", "WOOL", "EGG"):
                if payroll_need <= 0 or len(orders) >= 2:
                    break
                stock = shed.get(it, 0)
                if stock <= 0:
                    continue
                px = max(1, prices.get(it, 1))
                n = min(stock, payroll_need // px + 1)
                orders.append(["SELL", it, n])
                payroll_need -= int(n * px * 0.8)   # conservative vs slippage
        for _ in range(min(want_hires, 10 - len(orders))):
            orders.append(["HIRE"])

    # v37a day-0 all-in (monster blueprint): deploy nearly all
    # $3,000 starting cash into compounding assets in the first hour —
    # the 12 melons detonate at day 10-12 and fund the cow tail.
    if day == 0 and hour == 0:
        if D0_GOOSE:
            orders.append(["BUY_ANIMAL", "GOOSE", D0_GOOSE])
            money -= 300 * D0_GOOSE
        orders.append(["BUY_ANIMAL", "SHEEP", D0_SHEEP])
        orders.append(["BUY_ANIMAL", "COW", D0_COW])
        orders.append(["BUY_SEED", "MELON", D0_MELON])
        orders.append(["BUY_SEED", "WHEAT", D0_WHEAT_SEED])
        # Feed bridge (v37b): planted wheat yields from day 2; without it
        # the day-0 cows starved by day 2 in the v37a probe ($800 lost).
        orders.append(["BUY_PRODUCT", "WHEAT", D0_FEED])
        money -= (D0_SHEEP * 500 + D0_COW * 400 + D0_MELON * 80
                  + D0_WHEAT_SEED * 10
                  + D0_FEED * max(1, prices.get("WHEAT", 25)))

    shed_total = sum(shed.values())
    for item, (batch, min_price, liq_day) in SELL_RULES.items():
        stock = shed.get(item, 0)
        if item == "WHEAT" and day < LAST_DAY:
            # Never sell the herd's next few days of feed.  v54d: during the
            # ramp the reserve must sit ABOVE the feed top-up want (animals+2)
            # or the two rules oscillate - measured churn: SELL 2 @28 h7,
            # BUY 2 @30 h8, all day, spread paid to the market maker.
            stock -= (placed_animals + 6) if day <= 12 else placed_animals + 4  # v54h: post-ramp reserve also sits above top-up want (animals+2) - reserve below it re-churned; surplus above it SELLS (2k class moves 85+177 wheat units d10-21 vs our 16+12)
        if item == "FERTILIZER" and FERT_APPLY_FROM_DAY <= day < LAST_DAY:
            # Hold stock for crop fertilizing — but ONLY once the farm is liquid. In the
            # $0-bank opening, fertilizer sales are the survival cash that buys feed;
            # hoarding them starved the sheep that produce them (measured: 0-32 vs v3a).
            # v92b: the keep exists for the coverage machine — when the STR
            # price gate is off, sell the fertilizer (v89c behavior, keep 0).
            stock -= FERT_KEEP if _FERT_STR_ON else 0
        if item == "MELON" and 10 <= day <= 11 and _MEL_RACE.get(_CUR_SEAT, False):
            # v80a SAME-TURN SELL: unit deposits resolve BEFORE market orders
            # inside one engine step (kaggriculture.py interpreter: unit
            # actions L935-939, then _process_market L941), and per-unit SELL
            # commits stop harmlessly at an empty shed (L653-655).  So order
            # the caravan's incoming pockets too — a load sells the hour it
            # lands instead of the hour after (family cadence, ep108610904:
            # dep 24 / sell 24 in the same step).  Unarrived pockets no-op.
            stock += sum(inv.get("MELON", 0) for inv in inventories)
        if stock <= 0:
            continue
        price = prices.get(item, 0)
        force = shed_total >= SHED_FORCE_SELL and item not in NEVER_FORCE_SELL
        threshold, n = min_price, batch
        if item in MARKET_ABOVE and day < liq_day:
            # Rational threshold: once a market is glutted (x > 0), project where its
            # price can still go before liquidation day.  Net recovery = town drain
            # minus BOTH farms' ongoing production (ours + the opponent's public
            # capacity).  If the best still-reachable price is below our static
            # threshold, that threshold is a fantasy — accept the reachable price
            # now and dump faster (the first seller gets the better price).
            x = market_inv.get(item, MARKET_I0) - MARKET_I0
            if x > 0:
                net = (_town_drain_per_day(item, shops)
                       - _inflow_per_day(item, my_crops, my_animals)
                       - _inflow_per_day(item, opp_crops, opp_animals))
                reachable = _glut_price(item, x - net * (liq_day - day))
                if reachable < threshold:
                    threshold = max(3, reachable)
                    n = batch + PRESSURE_BATCH_BONUS
        if item in OPP_PRESSURE and day < liq_day:
            kind, source, trigger = OPP_PRESSURE[item]
            count = (opp_animals if kind == "animal" else opp_crops).get(source, 0)
            if count >= trigger:
                # Their dump is coming — sell first, sell faster.
                threshold = max(2, int(threshold * PRESSURE_THRESHOLD_MULT))
                n = batch + PRESSURE_BATCH_BONUS
        if tape_mode and day < liq_day:
            # We know the tape's decoded sell schedule; it cannot know ours.
            # v50a FRONT-RUN : a scheduled wave lands within the
            # horizon — any price now beats any price after 8-30 units hit
            # this market.  Fires from the full schedule, not hand-picked days.
            if _tape_wave_within(item, day * 24 + hour) >= TAPE_FR_MIN and stock > 0:
                threshold = min(threshold, max(3, int(min_price * 0.4)))
                n = batch + 8
                dump_boost = True
            if item == "WHEAT" and day >= TAPE_WHEAT_ENDGAME:
                # v50a: beat their 196-unit d25-29 wheat dump out the door
                # (feed reserve already excluded from `stock` above).
                threshold = min(threshold, 20)
                n = batch + 8
                dump_boost = True
            if item == "WOOL" and day <= TAPE_WOOL_SALVAGE_UNTIL:
                threshold = min(threshold, TAPE_WOOL_SALVAGE)
                n = batch + 5
            elif item == "MELON" and day >= TAPE_MELON_DUMP_DAY:
                threshold = min(threshold, TAPE_MELON_DUMP)
                n = batch + 5
            elif item == "MELON" and day >= TAPE_MELON_SOFT_DAY:
                threshold = min(threshold, TAPE_MELON_SOFT)
        if item == "MELON" and 10 <= day <= 11 and _MEL_RACE.get(_CUR_SEAT, False):
            # v80a: no batch cap on the detonation — the first seller gets
            # $265, the second gets the crater (fast copies sell 24/turn).
            n = stock
        if day >= 28:
            # v52b : COMPLETE liquidation — live close-loss decode
            # found 4 of 11 sub-8k losses had MORE value stranded in the shed
            # than the losing margin (day-29 harvests land with 1-2 market
            # turns left; batch 3/turn physically cannot clear them).  From
            # d28, batch caps are off: sell the whole stock every turn.
            n = stock
        if day >= liq_day or force or price >= threshold:
            orders.append(["SELL", item, min(n, stock)])

    # Wheat feed top-up from the market only if growing hasn't covered it. Bought wheat
    # lands in the shed after this turn's unit actions, so buy ahead of need.
    wheat_price = max(1, prices.get("WHEAT", 25))
    if day <= LAST_TICK_DAY and placed_animals > 0:
        wheat_stock = shed.get("WHEAT", 0) + sum(inv.get("WHEAT", 0) for inv in inventories)
        want = placed_animals + 2
        if wheat_stock < want and money > 0:
            # FEED IS SACRED: feed buys bypass every reserve (the reserve exists FOR feed).
            n = min(want - wheat_stock, int(money // wheat_price))
            if n > 0:
                orders.append(["BUY_PRODUCT", "WHEAT", n])
                money -= n * wheat_price

    # How many of each animal we own anywhere (placed + shed + carried) — used for both
    # the animal buys and the land trigger below.
    owned = {sp: shed.get(sp, 0) for sp in ANIMAL_INFO}
    for inv in inventories:
        for sp in ANIMAL_INFO:
            owned[sp] += inv.get(sp, 0)
    for row in tiles:
        for t in row:
            if isinstance(t, dict) and t.get("animal") in owned:
                owned[t["animal"]] += 1
    # (v16c) milk projection must precede herd_complete: a capped herd (6 cows
    # on a poor milk draw) counts as COMPLETE so the strawberry ramp still opens.
    milk_seen = sum(1 for s in shops if s in ("PIZZA_SHOP", "ICE_CREAM_SHOP",
                                              "SMOOTHIE_SHOP"))
    milk_proj = milk_seen + max(0, 8 - len(shops)) * 0.375
    # v47b NOTE: a d8+ REAL-drain cow cut was tried and REVERTED — cutting
    # 9 -> 6 cows in a dead-milk town raised our bank +12k but gifted the
    # 6-cow opponent +21.8k (milk market recovered for THEM;
    # principle).  Head-to-head, the 9-cow dump keeps mutual pressure.
    cow_target = 6 if milk_proj < 2.0 else ANIMAL_TARGETS["COW"]
    if _COW_BOOM.get(_CUR_SEAT, False):
        cow_target = COW_BOOM_TARGET   # v61d: healthy-milk town, extend the tail
    if _YARN_TOWN.get(_CUR_SEAT, False):
        cow_target = min(cow_target, 8)   # v57b: 6 sheep + 8 cows fit the 15-slot ring
    sheep_target = _DYN_SHEEP.get(_CUR_SEAT, ANIMAL_TARGETS["SHEEP"])
    herd_complete = (owned["SHEEP"] >= sheep_target
                     and owned["COW"] >= cow_target)

    # Animals: buy toward targets (sheep first), one per turn — ONLY if the bank can also
    # carry ~4 days of feed for the herd this animal joins (pre-income starvation destroyed
    # ~$1.7k of animals in v4a before this gate existed). Each arrives with a wheat dowry.
    # v47a: the unlock-day land buy is SACRED (blueprint: NE on d6 exactly —
    # our d9-10 slip was the root of the 2-3 day strawberry-ramp lag).  Save
    # toward the price from 2 days out; animals and seeds wait behind it.
    # v55c BERRY-FIRST WINDOW : the band
    # killers plant 20-26 strawberries d4-8 and buy the cow tail d7-10 with
    # wool/milk money — the inverse of our order.  A d5 berry earns its whole
    # d15-29 life (the measured d15-21 income hole); a d5-vs-d8 cow earns 3
    # extra days.  While the window is open, cow buys wait and the cow fund
    # flows to seeds.
    _str_committed = (seeds.get("STRAWBERRY", 0)
                      + sum(1 for _row in tiles for _t in _row
                            if isinstance(_t, dict) and _t.get("kind") == "PLANT"
                            and _t.get("crop") == "STRAWBERRY"))
    # v66c : the berry window now covers the post-land days too —
    # v66b bought Q2 at d6 (9→6, all fingerprint seeds) but STR@d10 FELL:
    # the $1,000 leaving 3 days earlier starved the d6-8 seed budget and
    # the fresh tiles sat empty (the v55a law: the cohort is SEED-CASH
    # bound).  The killers fund d7-8 cohort seeds from mid-week income we
    # don't have; ours comes from the animal TAIL instead — the window
    # extends d7→d9 and widens 15→24 committed, and the SHEEP tail joins
    # the cow tail in the pause (below).  Cows 6-8 at d11-14 still repay
    # (v18e measurement); the melon detonation refills everything at d10.
    # v67a : the window opens at DAY 2, not 4.
    # Measured cause (str_timing.py, 3 worst band losses): our STR tiles enter
    # the ground d9-13 -> first yield d17-19 (plant+10), missing half of the
    # d15-21 deciding week; killers plant by d8 -> harvest d14-18.  The d15-21
    # loss-week gap is 63-79% strawberry volume in BOTH live samples (110
    # games, realization.py).  Cows 1-3 still come first (v47a early engine);
    # the day-0/1 cow+sheep core is untouched.
    # v67b : v67a's day-2 window never
    # fired — early_ledger.py showed day-end money $26-371 through d8; the
    # herd ate the capital (our 3C+4S = $3,200 by d4 vs the killers' decoded
    # 2C+2S = $1,800 + 12 melons whose d10-12 detonation funds their tails).
    # The window now opens at COW>=2 and pauses BOTH tails at the killer core
    # (2 cows + 2 sheep); tails resume d10+ on melon-detonation money.
    # v67c: MILK-RICH RELEASE — when 2+ of the revealed shops are milk shops
    # (knowable at d3/d6, before the tail money is committed), the window
    # closes and the cow tail buys immediately (v66c boom behavior).  v67b's
    # A/B: thin cells crushed (8-0 +3.4k / 7-1 +2.7k vs v66c; 8-0 vs v61e
    # MILK0) but MILK3 washed (4-4, -957) — the paused tail costs boom lead.
    _berry_first = (2 <= day <= 9 and owned.get("COW", 0) >= 2
                    and _str_committed < 24 and milk_seen < 2)
    _next_land_day = LAND_DAYS[min(n_quadrants - 1, 2)]
    land_ready = day >= _next_land_day
    land_hold = 0
    if (n_quadrants < LAND_MAX_QUADRANTS and day <= 12
            and _next_land_day - 1 <= day):
        # v54b: hold from 1 day out (2-day hold froze $1,000 across d4-5 —
        # exactly the cow-per-day window; Prashant class buys land d6 AND a
        # cow daily, funded by the fert flywheel)
        # v66b : the hold now PERSISTS while the CLOCKED land is
        # still pending — live ledger (vs Amr, ep106615748): we sat at
        # $1,083 on d6 morning with the d6 land clock fired and spent it on
        # sheep+wheat because ANIMALS OUTRANK LAND in this queue; Q2 then
        # slipped to d9 [9,9] every game (x-ray) while all 3 decoded band
        # killers unlock d8 and plant their STR cohort on the fresh tiles —
        # the d15-21 income week.  Post-clock ordering is NOT v54b's
        # pre-clock freeze nor v55a's seed-starving hold: seeds are gated
        # by feed_hold, not land_hold, and the hold dies at d12.
        land_hold = LAND_PRICES[n_quadrants - 1]
    if day <= 20 and not herd_complete:
        # v54b: morning-only window removed — the 2k class completes the herd
        # by d8 buying whenever cash allows; afternoon cash was buying seeds
        # while cows waited overnight
        # v18d parity window: from day 4, animal buys fire only in the morning
        # third of the day.  Field audit: winners hold 5-7 animals at day 8 but
        # ~20 strawberries; we held 10 animals and 2 strawberries.  Cows still
        # complete by d10-12; afternoon cash buys berries instead of waiting.
        herd_after = sum(owned.values()) + 1
        # 2-day cushion (feed buys are already sacred; 4 days double-protected and
        # delayed the herd ~6 days).  Days 0-1: no cushion — the fertilizer stream
        # (~$98/animal/day) starts before the first feed bill can hurt.
        feed_cushion = 0 if day <= 1 else herd_after * wheat_price // 2  # v54b: halved again (2k class runs ~zero cash while ramping; feed top-up buys are already sacred)
        for sp in BUY_PRIORITY:
            # v18e staged herd: the field audit's winners hold 5-7 animals at
            # day 8 with ~20 strawberries planted; cows 6-8 arrive d11-14 and
            # still repay (~$450 vs ~$40-70/day milk to d29).  Pause the cow
            # tail so its cash plants the berries 4-6 days earlier.
            # v37a: staged-herd pause REMOVED — the monster ramp buys a cow
            # whenever cash allows; the day-0 melon block funds the tail.
            cost = ANIMAL_INFO[sp]["cost"]
            if sp == "COW" and owned["COW"] >= cow_target:
                continue
            if sp == "COW" and _berry_first:
                continue   # v55c: cow tail waits while the berry wave commits
            if (sp == "SHEEP" and _berry_first
                    and owned.get("SHEEP", 0) >= (4 if "YARN_STORE" in shops else 2)):
                continue   # v67b: sheep tail pauses at 2 (was 4) — sheep 3+4's
                           # $1,000 at d1-3 IS the missing cohort seed money.
                           # v70c YARN RELEASE: a revealed YARN_STORE (d3/d6,
                           # 13 wool/day drain at $150-200/u) outbids the
                           # cohort for sheep 3-4 — the holdout's YARN2 2-14
                           # and MIXED 2-14 losses to v66c were exactly the
                           # paused sheep; gates run on FRESH seeds (516+),
                           # never re-judged on the spent 500-507 block.
            sp_target = (_GOOSE_TARGET.get(_CUR_SEAT, 0) if sp == "GOOSE"
                         else sheep_target if sp == "SHEEP"
                         else cow_target)
            if owned.get(sp, 0) < sp_target and money >= cost + MONEY_RESERVE + feed_cushion + land_hold:
                orders.append(["BUY_ANIMAL", sp, 1])
                money -= cost
                orders.append(["BUY_PRODUCT", "WHEAT", 3])
                money -= 3 * wheat_price
                break

    # Land: NE after 6 animals owned, SW after 8 (waiting for the full 12-herd would
    # deadlock — animals 9-12 place on SW slots that need the land first).
    # v37b: day-clock land (blueprint: q2 day 6, q3 day 10) — the old
    # animal-count gate deadlocked when day-0 losses slowed the herd.
    if (n_quadrants < LAND_MAX_QUADRANTS and day <= 20 and land_ready):
        land_cost = LAND_PRICES[n_quadrants - 1]
        if money >= land_cost + (0 if day <= _next_land_day + 1 else MONEY_RESERVE + 200):
            orders.append(["BUY_LAND"])
            money -= land_cost

    # Seeds spend only what the herd's feed budget doesn't claim (the day-0 seed burst
    # once drained the bank to $0 and freshly placed sheep starved before any income).
    feed_hold = int(sum(owned.values()) * wheat_price * 1.3)  # v37c: was *4
    # v44a: evening payroll hold — tomorrow's hire ladder must survive tonight
    # as CASH (shed often empty at dawn).  From hour 16 so daytime stays all-in.
    _FIBC = [0, 1, 2, 4, 7, 12, 20, 33, 54, 88, 143, 232, 376, 609, 986]
    payroll_hold = _FIBC[min(hands_target, 14)] if hour >= 16 else 0
    # v54c COW FUND: while the herd is incomplete, the next animal's price is
    # reserved from seed spending — seeds were eating the $400 cow fund every
    # afternoon and stretching the ramp to d12 (2k class: C4 by d4, then the
    # STR flood; sequencing, not interleaving).
    cow_hold = 0
    if owned["COW"] < 6 and day >= 1 and not _berry_first:  # v55c: fund flows to seeds in-window
        # v54d: release at 6 cows - full-herd gating starved the berry flood
        # to d10+ (2k pattern: C4 by d4, STR flood from d5 alongside cow tail)
        cow_hold = 450
    spendable = money - feed_hold - payroll_hold - land_hold - cow_hold
    for crop in PLANT_ORDER:
        info = CROP_INFO[crop]
        if day > info["last_plant"]:
            continue
        if crop == "TOMATO":
            _tpx = prices.get("TOMATO", 0)
            _bar = BEHIND_TOMATO_PRICE if gamble else TOMATO_HINGE_CONFIRM
            if not (herd_complete or money >= 3000) or _tpx < _bar:
                continue  # v37d: detonation cash also opens the tomato gate
        elif crop == "CARROT":
            if _DYN_CARROT_CAP.get(_CUR_SEAT, 0) <= 0:
                continue   # v47b: carrots exist only in towns that drain them
        elif info["cap"] <= 0:
            continue
        want = SEED_WANT[crop]
        if crop == "MELON" and 6 < day < MELON_W2_FROM:
            continue   # v57c: no melon seeds in the dead window between waves
        if crop == "CARROT":
            want = 4
        if crop == "WHEAT" and _FACTORY_NOW:
            want = WHEAT_FACTORY_SEED_WANT
        if crop == "STRAWBERRY" and _DYN_STR_CAP.get(_CUR_SEAT, 40) <= 20:
            continue
        if crop == "STRAWBERRY" and tape_mode:
            want = min(SEED_WANT[crop], 4)   # v50a: cap 24 needs few seeds
        if crop == "STRAWBERRY" and not herd_complete:
            # v67a: seed gate d4 -> d2 (the old "days 0-3 cow-only" law was
            # measured on the pre-Exp-89 biased instrument; re-derived under
            # pinned worlds).  Day 0-1 stays cow/sheep-only via the day-0 gate
            # below and the COW>=3 window gate above.
            if day < 2:
                continue
            # v47a: flood the pipeline pre-herd too — the 165k blueprint's 38
            # strawberries pay from d15-16 (planted at the d6 NE unlock) while
            # our herd-throttled ramp paid d20+ = -19k of pure timing.
            want = 12
        if (day == 0 and crop in ("STRAWBERRY", "CARROT")
                and (owned["SHEEP"] < ANIMAL_TARGETS["SHEEP"] or owned["COW"] < 1)):
            # Day-0 fourth sheep (v14b): premium seeds yield nothing before day
            # 10, but a sheep bought day 0 vs day 4 moves its whole wool stream
            # up 4 days — the tape's day-0 allocation, decoded and copied.
            continue
        have = seeds.get(crop, 0)
        _res = 0  # v47a: no berry throttle — cows and berries ramp TOGETHER (blueprint)
        if have < want and spendable - _res >= info["cost"]:
            n = min(want - have, int((spendable - _res) // info["cost"]))
            if n > 0:
                orders.append(["BUY_SEED", crop, n])
                spendable -= n * info["cost"]

    # v61e : HIREs move to
    # the BACK of the queue — the engine executes slots in list order
    # with HIRE committed first within its slot (engine L562-581), so an
    # early HIRE drains the cash a later BUY_ANIMAL/BUY_LAND/BUY_SEED
    # needed (incl. the milk-boom's cow buys).  Stable partition: same
    # orders, same counts, hires last.  Held-out evidence: v61b2
    # (= v61c + this, NO boom) beat v61d 89W-65L (57.8%) — winning
    # despite conceding the boom lane.
    orders = ([o for o in orders if not (o and o[0] == "HIRE")]
              + [o for o in orders if o and o[0] == "HIRE"])
    return orders[:10]


def agent(obs):
    player = obs["player"]
    me = obs["farms"][player]
    private = obs["private"]

    tiles = me["tiles"]
    day = obs["day"]
    hour = obs["hour"]
    money = me["money"]
    seeds = private.get("seeds", {}) or {}
    shed = private.get("shed", {}) or {}
    inventories = private.get("inventories", []) or []
    prices = (obs.get("market", {}) or {}).get("prices", {}) or {}

    units = [tuple(me["farmer"])] + [tuple(h) for h in me.get("hands", [])]

    # Tape-family fingerprint: evaluated on days 1-3, latched for the episode.
    opp = obs["farms"][1 - player]
    step = obs.get("step")
    if step is None:          # seat-1 bug: key present with value None
        step = day * 24 + hour
    if step == 0:
        _TAPE_SEEN[player] = False
        _GAMBLE_ON[player] = False
        _WHEAT_TOWN[player] = False
        _YARN_TOWN[player] = False   # v57b
        _COW_BOOM[player] = False    # v61d
        _GOOSE_TARGET[player] = D0_GOOSE
        _MEL_RACE[player] = False    # v80b
        _STICKY[player] = {}
    if not _TAPE_SEEN.get(player, False) and 1 <= day <= 2:
        _oc, _oa = _opp_capacity(opp.get("tiles", []))
        # Self-exclusion (v15 copies the tape's 4-sheep opening): the tape shows
        # 4 SHEEP + COW + exactly 5 MELONS from day 1 (byte-identical opening);
        # our lineage has no placed cow on days 1-2 and at most 3 melons before
        # day 3.  Both extra conditions + the day-2 cutoff keep us from false-
        # latching tape counters against our own versions in self-matches.
        if (_oa.get("SHEEP", 0) == 4 and _oa.get("COW", 0) >= 1
                and _oc.get("MELON", 0) in (5, 8)):
            # v54k: the current top tape (V16-RC5, salemali7 "2900+" lineage)
            # opens 8 melons, not 5 — same sell schedule byte-for-byte
            # (verified vs extracted _ACTIONS), so only the detector changes.
            _TAPE_SEEN[player] = True
    tape_mode = _TAPE_SEEN.get(player, False)
    if not _MEL_RACE.get(player, False) and 4 <= day <= 8:
        # v80b caravan gate — DAY-0 COHORT, not tile count: Amitesh(801)
        # replants to 10-11 melon tiles but its d0 cohort is 7 (staggered
        # maturities, no d10 detonation, caravan measured −1,079 there);
        # the family plants 10-12 ALL on d0 (decode: fast 11.4, slow 10.2
        # tiles at planted_day 0) → simultaneous d10 detonation, caravan
        # +733/+1,453.  planted_day is public in the opponent farm.
        _oppmel0 = sum(1 for row in (opp.get("tiles") or []) for t in (row or [])
                       if isinstance(t, dict) and t.get("crop") == "MELON"
                       and t.get("planted_day", 99) <= 1)
        if _oppmel0 >= 10:
            _MEL_RACE[player] = True

    market_inv = (obs.get("market", {}) or {}).get("inventory", {}) or {}
    shops = (obs.get("town", {}) or {}).get("unlocked_shops", []) or []
    # v71c : care_skip = OBSERVED-PRICE gate, replacing the glut
    # PROJECTION (falsified: live care completeness fell to 71% mid / 34%
    # late — off in worlds where the killers care 94-99% and realize
    # ~$106/u milk).  Blanket-on (v71b) was falsified the other way:
    # YARN2 −3,537 / MILK3 −847 vs v70c — in no-milk-shop worlds milk
    # really floors, and cared milk then eats harvest/haul labor and
    # 10-cap sell slots that wool needed.  The projection was right THERE
    # and wrong everywhere else, so gate on the observed price NOW, no
    # forecast: skip a species only while its product actually sits at
    # the floor; the town's 1/day drain lifts it and care resumes the
    # same turn (banked bonuses still pay at the next tick).  Engine
    # L829-830: +1 product unit per cared+fed day.  P_CARE stays 2
    # (1.5 measured −1.5/−1.8k: starved waters).
    care_skip = {sp for sp, info in ANIMAL_INFO.items()
                 if prices.get(info["product"], 999) <= CARE_FLOOR_NOW}
    crop_skip = _crop_skip(tiles, opp.get("tiles", []), market_inv, shops)
    # v60a: is the STR market deep-dead for the rest of the game?  5-day
    # projection with both farms' inflow; STR's town drain is the game's
    # biggest, so transient dips project far above the $5 bar (v15e guard).
    str_dead = False
    if day >= STR_DEAD_FROM_DAY:
        _sx = market_inv.get("STRAWBERRY", MARKET_I0) - MARKET_I0
        if _sx > 0:
            _mc, _ma = _opp_capacity(tiles)
            _oc2, _oa2 = _opp_capacity(opp.get("tiles", []))
            _snet = (_town_drain_per_day("STRAWBERRY", shops)
                     - _inflow_per_day("STRAWBERRY", _mc, _ma)
                     - _inflow_per_day("STRAWBERRY", _oc2, _oa2))
            # v89b : the projection alone is NOT enough — it counts
            # our own (now doubled, 35-38 tile) capacity as incoming supply
            # and predicted crashes that live towns absorbed.  Live v88a band
            # losses: str_dead fired ~d25 and dug 19 tiles/game AT $164-221
            # (v83a's 17-tile farms never triggered it — the seed-cohort
            # success armed this trap).  A market selling at $200 TODAY is
            # not dead today: require the CURRENT price to already confirm
            # the crash before abandoning producers.
            if (_glut_price("STRAWBERRY", max(0, _sx - _snet * 5)) <= STR_DEAD_PRICE
                    and prices.get("STRAWBERRY", 0) <= STR_DEAD_CONFIRM_PX):
                str_dead = True

    # ramp_fast (v18c): same herd-complete test the market code uses (total owned
    # animals vs sheep target + demand-conditioned cow target).
    _owned_n = sum(1 for row in tiles for t in row
                   if isinstance(t, dict) and t.get("animal") in ANIMAL_INFO)
    _owned_n += sum(inv.get(sp, 0) for inv in inventories for sp in ANIMAL_INFO)
    _owned_n += sum(shed.get(sp, 0) for sp in ANIMAL_INFO)
    _milk_seen = sum(1 for s in shops if s in ("PIZZA_SHOP", "ICE_CREAM_SHOP",
                                               "SMOOTHIE_SHOP"))
    _milk_proj = _milk_seen + max(0, 8 - len(shops)) * 0.375
    # v61d milk-boom latch (gate v2): sticky; requires THREE actual milk
    # shops (drain that absorbs a 12-cow herd) + price still >= $200.
    if (not _COW_BOOM.get(player, False)
            and COW_BOOM_FROM_DAY <= day <= COW_BOOM_UNTIL_DAY
            and _milk_seen >= 3
            and not _YARN_TOWN.get(player, False)
            and prices.get("MILK", 0) >= COW_BOOM_PRICE):
        _COW_BOOM[player] = True
    _cow_t = 6 if _milk_proj < 2.0 else ANIMAL_TARGETS["COW"]
    if _COW_BOOM.get(player, False):
        _cow_t = COW_BOOM_TARGET
    _shp_t = _DYN_SHEEP.get(player, ANIMAL_TARGETS["SHEEP"])
    # v47b: _SLOT_NEED stays STATIC — feeding the live (guarded) targets in
    # shrank the ongoing-crop ban to 10 slots in weak towns and chaotically
    # reshaped whole games (seed-12 flip-flop).  Layout stability wins.
    _SLOT_NEED[player] = (sum(ANIMAL_TARGETS.values()) + _GOOSE_TARGET.get(player, 0)
                          + (COW_BOOM_TARGET - ANIMAL_TARGETS["COW"]
                             if _COW_BOOM.get(player, False) else 0)
                          # v84b: + the sheep bump, same pattern as the boom
                          # bump (constant per game — no v47b flip-flop; the
                          # chaos then came from _cow_t moving mid-game).
                          # Without it sheep 5-6 sat IN THE SHED 12+ days
                          # (fingerprint seeds 12-13: "+2 shed" at d24 —
                          # the v54f dead-capital disease); slots were still
                          # planned for ANIMAL_TARGETS' sheep 4.
                          + max(0, _shp_t - ANIMAL_TARGETS["SHEEP"]))
    ramp_fast = (_owned_n >= _shp_t + _cow_t
                 or money >= 3000)  # v37d: detonation counts as ramped

    # Reactive tomato (v20d, staged): none pre-herd; small speculation on a
    # 2+-shop draw; full commitment only when price >= 85 confirms the hinge.
    _tom_shops = sum(1 for s in shops if s in TOMATO_SHOPS)
    _tom_px = prices.get("TOMATO", 0)
    # Bank-differential gamble (v24a): when clearly losing, flip the
    # EV-neutral late-tomato coin (variance buys win probability only from
    # behind).  Sticky once latched so a started batch gets finished.
    if (not _GAMBLE_ON.get(player, False)
            and day >= BEHIND_TOMATO_DAY
            and money - opp.get("money", 0) <= -BEHIND_GAMBLE_DEFICIT
            and _tom_px >= BEHIND_TOMATO_PRICE):
        _GAMBLE_ON[player] = True
    gamble = _GAMBLE_ON.get(player, False)
    # Dead-premium town -> early wheat factory (v31a).  Sticky once latched
    # (a started conversion gets finished even if a premium shop lands later).
    global _FACTORY_NOW, _DEAD_TOWN_NOW, _CUR_SEAT
    _CUR_SEAT = player   # v40a: key for _assign's cross-turn sticky memory
    if (not _WHEAT_TOWN.get(player, False)
            and day >= WHEAT_TOWN_CHECK_DAY
            and _town_drain_per_day("STRAWBERRY", shops) <= 1
            and _town_drain_per_day("MILK", shops) <= 1
            and _town_drain_per_day("WHEAT", shops) >= 7):
        _WHEAT_TOWN[player] = True
    if hour == 0:
        _DYN_STR_CAP[player] = _dyn_str_cap(shops, day)
        _DYN_CARROT_CAP[player] = 12 if _town_drain_per_day("CARROT", shops) >= 8 else 0
        # v47b: a yarn-town sheep 4 -> 6 bump was tried and REVERTED — wool's
        # market is the game's smallest (T=105, sq glut curve): 2 extra sheep
        # crashed the price for both sides and cost us 8k on the yarn seed.
        # v57b RETRY with the missing piece: a YARN_STORE drains 12 wool/day
        # (single-product shop = double drain) — volume that a yarn town
        # absorbs without crashing.  The band's sheep-10 family sizes its
        # whole herd to this (its router keys on YARN_STORE) and
        # takes ~$7k/game off us in yarn towns.  v47b's revert predates
        # care-complete labor (v56a freed ~250 actions) and the fert/wool
        # express (v57a).  Latch is sticky, d<=9; unfired towns identical.
        if "YARN_STORE" in shops and day <= 9:
            _YARN_TOWN[player] = True
        # v84b RE-FALSIFIED base sheep 6 : modern
        # pipeline, fresh seeds 1102-1140, stranding fixed — Amitesh margin
        # wash but WINS 16→10 (flips +2/−8, primary estimator).  4th sheep
        # falsification (v19a, v47b, v72b, v84b); the band's sheep-10
        # families are a different CHASSIS, not ours +2 sheep.  Base stays 4.
        _DYN_SHEEP[player] = YARN_SHEEP if _YARN_TOWN.get(player, False) else 4
        if (_GOOSE_TARGET.get(player, 0) < 1 and day <= 10
                and _town_drain_per_day("EGG", shops) >= 7):
            _GOOSE_TARGET[player] = 0
    _DEAD_TOWN_NOW = _WHEAT_TOWN.get(player, False)
    _FACTORY_NOW = day >= WHEAT_FACTORY_DAY or _DEAD_TOWN_NOW
    # v92b : the fert-coverage machine is PRICE-GATED.  v92a's
    # blanket coverage was a wash at n=39 with a clean own-bank SPLIT:
    # −1,248 vs the Amitesh flood (extra units into a crashed price +
    # fert withheld from sale) but +1,270 vs holdpx.  Coverage doubles
    # STR ticks — double into a market worth doubling into; when STR is
    # crashed, fall back to v89c exactly (window 7-15, P_FERT, keep 0)
    # and sell the fertilizer instead.
    global _FERT_STR_ON
    _FERT_STR_ON = prices.get("STRAWBERRY", 0) >= FERT_STR_MIN_PX
    if ramp_fast and (_tom_px >= TOMATO_HINGE_CONFIRM
                      or (gamble and _tom_px >= BEHIND_TOMATO_PRICE)):
        tomato_cap = min(12, TOMATO_CAP_PER_SHOP * max(1, _tom_shops))
    else:
        tomato_cap = 0

    tasks, n_feed = _build_tasks(tiles, day, seeds, tape_mode, care_skip, crop_skip,
                                 ramp_fast, tomato_cap, str_dead)
    _supply_tasks(tasks, n_feed, units, inventories, shed, tiles, day)
    assignment = _assign(units, tasks, inventories, tiles, day, hour)

    actions = [_unit_action(units[ui], assignment.get(ui)) for ui in range(len(units))]

    # PLANT collective-validation guard (unchanged from v1).
    plant_counts = {}
    for i, a in enumerate(actions):
        if a and a[0] == "PLANT":
            crop = a[1]
            plant_counts[crop] = plant_counts.get(crop, 0) + 1
            if plant_counts[crop] > seeds.get(crop, 0):
                actions[i] = ["PASS"]

    market = _market_orders(day, hour, money, seeds, shed, inventories, prices,
                            me.get("hires_today", 0), len(me.get("hands", [])), tiles,
                            len(me.get("unlocked_quadrants", ["NW"])),
                            opp.get("tiles", []), market_inv, shops, tape_mode,
                            gamble)

    if DEBUG:
        print(f"d{day} h{hour} units={len(units)} tasks={len(tasks)} market={market}")

    return {"farmer": actions[0], "hands": actions[1:], "market": market}
