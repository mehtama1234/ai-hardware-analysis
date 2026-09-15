# Validation of finite reference settings

This study evaluates the static range discretization imposed by the nominal
SKY130 switched-reference DAC in the sibling EDA project. It compares the
original training-calibrated ADC12 profile with a profile using the frozen
finite reference settings. Both run within real GPT-2; an ideal tiled control
and exact restored digital fallback are checked for every context.

The study uses the same sixteen validation contexts as the prior range study,
not test contexts. It reproduces the original training calibration and requires
an exact match with its frozen contract before applying reference settings.
No ranges are fitted on validation inputs. The finite setting is used for
clipping, ADC quantization and digital reconstruction together. All profiles
remain noiseless except for their numerical quantization/discretization;
this study does not include physical noise or dynamic reference settling.

Inputs:

- `holdout-plans/20260909-calibrated-adc12/`: original training calibration,
  model identity and unchanged quality screen; its test windows are not used.
- `runs/20260909-adc-range-validation-v1/`: validation context selection.
- EDA `evidence/aimc-hardware-lab/switched-reference-ranges/20260909-v1/`:
  144 frozen reference settings derived from the nominal 1 TΩ DC curve.

The output is `runs/20260909-finite-reference-validation/`. Inputs, source code
and protocol are recorded before execution; variant rows are flushed as they
finish. The evaluation completed with exit code zero and wrote its result and
manifest. No model process remains active for this run.

| Profile | Predictions | NLL increase, nats/token | Baseline argmax agreement | ADC clipped partials | Screen |
| --- | --- | --- | --- | --- | --- |
| Original calibrated ADC12 | 2,048 | 0.000769094 | 99.3164% | 27 | Pass |
| Finite-reference ADC12 | 2,048 | 0.000793248 | 99.3652% | 27 | Pass |

Both profiles had zero DAC clips. All ideal numerical controls and exact
fallback checks passed. The original profile reproduced all sixteen prior
validation contexts' baseline losses, candidate losses and argmax counts
exactly. The one-prediction agreement difference does not establish superiority.

```bash
python3 scripts/check_gpt2_reference_validation.py experiments/gpt2-hybrid-v1/runs/20260909-finite-reference-validation
```

The checker passed input hashes, all 48 rows, context/variant coverage, aggregate
metrics, numerical control measurements, restored fallback and all 144
effective bounds. Six mutation checks rejected false test qualification,
false hardware qualification, relabeled test split, altered agreement,
stale effective range and missing fallback. To reproduce the rejection checks:

```bash
python3 scripts/test_reference_validation_rejection.py experiments/gpt2-hybrid-v1/runs/20260909-finite-reference-validation
```

A focused numerical check has already verified that changed bounds affect
clipping and reconstruction and that stale calibration bindings are rejected.

Any validation pass is development evidence. Separate held-out evaluation,
full converter/array qualification and measured hardware execution costs remain
required. The prior test-quality pass applies to the original range profile.

## Separate finite-reference holdout started

`holdout-plans/20260909-finite-reference/` freezes the exact validated finite
contract, model/dataset identities, unchanged quality screen and 32 new test
contexts. Selection excludes all 64 previously scored test contexts: the
original conservative-range test's 32 and the original calibrated-profile
holdout's 32. All selected and excluded token IDs are checked against the pinned
test token stream. This is context disjointness, not unseen-article or
pretraining-exclusion evidence.

`scripts/freeze_reference_holdout.py` produced and checked the plan. Four
negative checks rejected a reused test context, removed exclusion, changed
effective range and changed reference-binding hash. No inference was used to
select these contexts or modify the profile.

The shared runner now accepts `--test-plan` and requires its selected contract
to match the reproduced finite-reference projection exactly. It uses a distinct
`circuit_reference_disjoint_holdout.v1` schema and labels the evaluation as test;
validation packages retain their original schema and snapshots. The output is
`runs/20260909-finite-reference-holdout/`, with 32 contexts and 4,096 predictions.

The holdout completed with exit code zero. Its 16 artifact hashes, 96 rows,
32 disjoint contexts, exact digital fallback, ideal numerical controls and all
144 effective scales verified. All six result mutation checks passed.

| Profile | Predictions | NLL increase, nats/token | Baseline argmax agreement | ADC clipped partials | Screen |
| --- | --- | --- | --- | --- | --- |
| Original calibrated ADC12 control | 4,096 | 0.000613160 | 99.4141% | 60 | Pass |
| Finite-reference ADC12 | 4,096 | 0.000603370 | 99.4385% | 61 | Pass |

Both had zero DAC clips. The finite-reference profile has 23 mismatched
next-token decisions; the original-profile control has 24 on these same
contexts. Neither this one-decision difference nor the small loss difference
establishes statistical superiority. The finite profile passes the unchanged
sampled quality screen on contexts not used in prior testing.

There is no running model process for this package. The circuit sequence
experiment remains separate: its first invocation hit a runtime limit and
its recovery package preserves the completed evidence while finishing the
remaining cases. Neither this quality pass nor a reference-component settling
pass qualifies the full array, ADC or hardware executor.

```bash
python3 scripts/test_reference_validation_rejection.py experiments/gpt2-hybrid-v1/runs/20260909-finite-reference-holdout
```

The combined decision builder now accepts this distinct held-out schema and
retains the separate physical and compiler evidence boundaries. A negative
check rejected finite-reference validation as test evidence before creating
an output directory. The new build targets
`decisions/20260909-finite-reference-holdout/` and completed with exit code zero.
The joined decision remains **retain native digital execution**: both numerical
profiles pass, while full converter/array qualification, a bound analog executor
and matched hardware latency/energy are absent. Its artifact and linked-source
hashes were verified; nominal static reference evidence is explicitly distinct
from a circuit-calibrated array error model.
