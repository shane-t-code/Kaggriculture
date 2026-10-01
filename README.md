# Kaggriculture — a farm-economy agent for Kaggle's two-player simulation

An agent, a paired-evaluation harness and a replay-forensics toolkit built over six weeks for
the **Kaggriculture** competition (Kaggle × Google, 2026): a 30-day, 720-turn farming game in
which two bots plant crops, raise animals, hire hands, buy land and trade on a shared market
whose prices react to both players. The winner is the farm with more money at the final bell.

- Competition: **[Kaggriculture on Kaggle](https://www.kaggle.com/competitions/kaggriculture/overview)**
- Final standing: Finalized 10/15/26
- Author: **Shane Thivaharraja**

## By the numbers

| | |
|---|---|
| Experiments logged | 212, each with a pass/kill rule written before it ran |
| Submissions | 33 over the competition; peak live rating 2,666 |
| Local evaluation | tens of thousands of paired games; single batteries of up to 2,666 games, run on a 12-core workstation and a 32-vCPU cloud pod |
| Replays decoded | 239 of our own live games and 88 top-team games reconciled to the coin; 577 recorded top-team games compiled into a plan library |
| Submitted agent | one 10.5k-line standard-library file; 3 ms per turn on average, under 400 ms worst case against a 1 s budget |
| Engine simulator | rebuilds the live game state and reproduces a real episode exactly, at ~2 ms per turn |

## The game in one paragraph

Each player manages a private 10×10 farm (four quadrants, one unlocked at the start) for
720 turns. Every turn you issue one action per unit (the farmer plus any hired hands) and up
to ten market orders. Eight shop types open in the town on a fixed schedule (one every three
days) and decide which products have demand. Ratings move on win/loss only, and both banks
are public every turn, so the objective is win probability against the field, not money.

## Constraints the agent runs under

Submissions are a single `main.py` with no network access, executed on 1.6 vCPUs with about
one second per turn (plus a 60 s overage bank for the whole episode) and a 100 MiB size
cap. Five submissions a day are allowed and only the newest two play, so local measurement
had to be trusted over live scores: live ratings settle only to ±25–50 points, and
byte-identical agents have finished 1,400 points apart.

## Approach

**Recorded plans with reflexes.** The agent follows a library of complete, pre-computed
game plans (one per shop configuration, chosen once the first two shops are revealed) and
keeps them on track with small reactive layers that read the live state each turn:

| Layer | Purpose |
|---|---|
| hand alignment / weed repair | keep the plan valid when the crew or the board differs from the recording |
| sell lead | sell the next turn's lots a turn early, ahead of same-plan rivals |
| room guard | sell overflow at hour 23 so the end-of-day drop does not destroy goods |
| conditional projects | a late third-plot tomato project, opened only when a value estimate **or** the original shop/price rule says the market will pay |
| deep terminal | a last-day plan that converts exact ties into one-coin wins against copies |

The plan library and the chassis derive from public, Apache-2.0 agents (attribution notices
are kept inside `agent/main.py`); the layers, the conditional projects, the testing method and
the analysis tools are this project's work.

Alternatives were built and measured before being rejected on paired results: a from-scratch
daily planner with a work-stealing scheduler, a behaviour-cloning policy trained on 1.74 M
state-action samples from top-team replays, and a plan-library agent that chooses among
577 recorded top-team games by simulating each candidate to the end of the game inside the
episode (`playbook/`). None beat the recorded-plan agent in natural worlds; the measurements
that killed them are as much a part of the method as the ones that shipped.

## How changes were tested

Every change had to pass the same measurement before it was allowed into a submission:

1. **Paired worlds.** Candidate and incumbent play the *same seeds*, both seats. Unpaired
   comparison is ~67× noisier (standard error 8.7 vs 584 coins, measured) because the shop
   draw shares a random stream with weed spawning, so any change in tile occupancy re-rolls
   the town.
2. **Real opponents, natural worlds.** Opponents are real agents (or reconstructed recordings
   of top teams) in freshly drawn worlds, never a single fixture.
3. **Margin and win/loss flips first.** The report leads with the paired margin change and
   the count of ties/losses turned into wins (and the reverse); own bank is secondary.
4. **Gates fixed in advance.** Pass/kill rules are written before a measurement runs, with an
   explicit falsifier. Changes that raised mean bank but added flips against were rejected.
5. **No-harm screens** against unrelated agents, 0 errors and a per-step time budget
   (< 900 ms, measured single-process) before anything is submitted.

Two findings from this loop: a “courier” reflex that brought wool home three hours earlier
looked like a +1.8k/day edge in one replay and lost in 16 of 16 paired cells, so it was
killed; a one-line change to the tomato project's gate turned dead ties into wins (+646 to
+3,681) in the exact price band where copies had been beating us, and shipped.

## Replay analysis tools

The competition publishes every replay, so most of the research was forensic:

- `analysis/clone_diff.py` — in a game against a same-opening copy both farms start identical,
  so a turn-by-turn diff of the two action streams isolates the rival's edit and the day the
  bank gap opens.
- `analysis/gate_probe.py`, `analysis/p1_detail.py` — what each side saw at a decision point
  and the first purchase that failed when a recording is moved to a new game.
- `analysis/p1_break.py`, `analysis/p1_follow.py`, `analysis/p1_switch.py`,
  `analysis/p1_shops.py`, `analysis/p1_mg.py` — the *break study*: how far a top team's whole
  recorded game survives a different opponent, a different seed, or a different town, with and
  without repair reflexes (a 5-coin price difference on day 0 cost one recording 56% of its
  final bank; three reflexes turned 5 wins in 20 into 14), and whether a team's build is a
  function of the shops it has seen.
- `analysis/lineage.py`, `analysis/best_copy.py`, `analysis/team_now.py` — which teams share an
  opening, how a given submission actually scored, and what a team runs today (public episode
  service, no credentials).
- `playbook/rollout.py` — rebuilds the engine state from a live observation and simulates the
  rest of the game *inside* the episode with the real engine (reproduces a game to the coin
  from any mid-game step); `playbook/mgx.py` is the experimental plan-library agent built on it.
- `tools/shop_pin.py`, `tools/arena.py`, `tools/tape_build.py` — pin a town's shop sequence,
  drop our agent into a top team's recorded game, and turn a replay into a local opponent.
- `testing/family_duel.py`, `testing/variant_test.py`, `testing/tomato_test.py` — the paired
  duel harnesses used for every gate above. `run_local.py` is the general paired A/B runner.

## Repository layout

```
agent/main.py        the submitted agent (single file, standard library only)
run_local.py         paired A/B runner: same seeds, both seats, win rate first
testing/             paired duel harnesses and gates
analysis/            replay forensics (clone diff, break study, lineage, …)
playbook/            in-episode engine rollouts and the plan-library agent
tools/               shop pinning, arena fixtures, replay-to-agent conversion
docs/                engine notes, competition spec, sourced research
```

Experiment scratch work, replays, downloaded datasets and working notes are kept out of the
repository (see `.gitignore`); this README describes the method they fed.

## Running it

```bash
pip install -U "kaggle-environments>=1.32.7"
python run_local.py --a agent/main.py --b starter --seeds 16      # paired A/B, both seats
python testing/family_duel.py final path/to/other_agent.py 100 10  # duel on seeds 100-109
python -X utf8 analysis/clone_diff.py <episode_id>                 # needs the Kaggle CLI
```

Tools that identify “our” seat in a replay read the team name from the `TEAM_NAME`
environment variable.

## License

Apache License 2.0 (see `LICENSE`). The agent embeds and extends public Apache-2.0 code;
the original notices are retained in `agent/main.py`.
