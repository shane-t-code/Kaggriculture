# Kaggriculture — competition project

Agent for the Kaggle **Kaggriculture** simulation competition (Kaggle + Google, $50,000, top 10 paid).

```
.md            <- project instructions for  Code (read automatically)
main.py              <- THE SUBMISSION. Must be named main.py, at archive root.
run_local.py         <- paired A/B harness (free, unlimited - use instead of submissions)
docs/COMP_INFO.md    <- official spec, verbatim
docs/RESEARCH.md     <- competitive intel: meta, economy, measurement traps (sourced)
docs/ENGINE_NOTES.md <- engine-vs-docs discrepancies + our own findings
replays/             <- downloaded / dumped replay JSON
```

## Setup

```bash
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -U "kaggle-environments>=1.32.7" kaggle
```

Verify the engine version (two balance changes shipped mid-competition; <1.32.7 is stale):

```bash
python -c "import kaggle_environments as k; print(k.version)"
```

Locate the engine source — **this is the source of truth, not the docs**:

```bash
python -c "import kaggle_environments,os;print(os.path.join(os.path.dirname(kaggle_environments.__file__),'envs','kaggriculture','kaggriculture.py'))"
```

## Run a game

```bash
python run_local.py --seeds 2 --debug      # smoke test, shows invalid actions
python run_local.py --seeds 16             # real paired A/B vs built-in "starter"
python run_local.py --a main.py --b starter --replay
```

## Submit

```bash
kaggle competitions submit kaggriculture -f main.py -m "v1: description"
kaggle competitions submissions kaggriculture
```

5 submissions/day. **Only the latest 2 are active, and those 2 are what the final ranking uses.**
