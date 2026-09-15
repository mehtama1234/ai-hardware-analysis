# Training-observed ADC range comparison

This experiment asks whether the conservative partial-sum range wastes useful
converter resolution in the numerical GPT-2 projection. It is a validation-set
development comparison. It does not replace the completed test-set decision or
qualify physical converter hardware.

## Frozen experiment

- Same GPT-2 revision, first MLP projection, 128×128 tiling, weight8 and DAC10
  as the preceding WikiText experiment.
- Same pinned WikiText revision `b08601e04326c79dfdd32d625aee71d232d685c3`.
- Calibration uses the same 16 training contexts, capturing 2,064 projection
  input vectors. The tensor, token selections and source snapshots are saved.
- Evaluation uses 16 evenly spaced, nonoverlapping **validation** contexts:
  128 next-token targets each, 2,048 targets per candidate.
- Candidate set: conservative ADC8/ADC12 and calibrated ADC8/ADC12, plus the
  ideal tiled control. All candidates are noiseless to isolate range choice.
- Per-tile ranges use the maximum absolute partial observed after weight and
  DAC quantization, multiplied by fixed 1.1 headroom and capped by the original
  conservative bound. Unexcited tiles retain their conservative range.
- Numerical controls and provisional quality thresholds are unchanged from
  the documented v2 protocol. Inference cannot update calibration ranges.

The pre-evaluation ranges are 16.82–49.11 times narrower than their conservative
bounds (median 34.59). That is an observed numerical calibration result, not a
measurement of physical gain or converter performance.

## Completed validation result

All 16 contexts passed the numerical control and exact digital fallback checks.

| Candidate | NLL increase, nats/token | Baseline argmax agreement | Screen |
| --- | ---: | ---: | --- |
| Conservative ADC8 | 0.058162 | 82.8125% | Fail |
| Conservative ADC12 | 0.000994 | 98.3887% | Fail |
| Calibrated ADC8 | 0.001194 | 98.9258% | Fail |
| Calibrated ADC12 | 0.000769 | 99.3164% | Pass |

Both calibrated profiles recorded 27 clipped ADC partials across 2,064 input
vectors; conservative profiles recorded none. All DAC clipping counters were
zero. The smaller range substantially improves ADC8 agreement, but it still
falls short of the unchanged 99% requirement. Calibrated ADC12 is the sole
nonideal validation candidate passing the joint screen.

Verification checked 13 artifact hashes and 80 rows. Six mutation checks
rejected corrupted metrics, numerical controls, analog claims, source changes,
range refitting and relabeling validation as test data. A separate negative
check confirmed that the decision builder refuses validation promotion before
creating an output directory.

## Frozen follow-up test

`holdout-plans/20260909-calibrated-adc12/plan.json` selects the lowest-bit
calibrated candidate passing validation: ADC12. It freezes the exact training
activation tensor, calibrated ranges, model files, numerical controls and
quality thresholds. Its 32 test contexts do not overlap any of the earlier
32 test contexts, and contain 4,096 next-token targets. This means disjoint
token contexts, not necessarily unseen articles or absent model pretraining.

The dedicated runner reconstructs the profile only from the saved training
tensor, requires its complete contract to match the frozen plan, then executes
the selected profile and ideal control against native GPT-2. No held-out input
can update the ranges. Commands from `software-architecture`:

```bash
python3 scripts/run_gpt2_adc_holdout.py --plan experiments/gpt2-hybrid-v1/holdout-plans/20260909-calibrated-adc12 --output experiments/gpt2-hybrid-v1/runs/new-calibrated-adc12-holdout
python3 scripts/check_gpt2_adc_holdout.py experiments/gpt2-hybrid-v1/runs/new-calibrated-adc12-holdout
```

The completed execution directory is `runs/20260909-calibrated-adc12-holdout/`.
The process exited successfully and its package passed verification.

### Held-out result

Calibrated ADC12 passed the unchanged joint screen across 4,096 scored targets:
99.3164% baseline argmax agreement (4,068 matches, 28 mismatches), NLL increase
0.00072734 nats/token, and sampled perplexity 64.28212 versus native 64.23538.
This is a sample-level screen pass, not perfect output parity or general task
acceptance. All 32 ideal controls and exact native fallback checks passed.

Maximum ideal projection error was 2.86e−6, maximum log-probability error
0.00012205 and maximum absolute per-context mean target NLL change 1.17e−6.
The candidate processed 4,128 vectors, with zero DAC clipping and 82 clipped ADC
partials. Those clips remain in the evidence and were not used to refit ranges.

Verification checked 13 hashes, context exclusion, the frozen profile,
selection provenance, metrics and control measurements. Seven mutation checks
rejected overlapping contexts, changed profiles, a failed candidate selection,
numerical failures, inconsistent metrics, analog authorization and changed
source. The [combined decision](decisions/20260909-calibrated-adc12-holdout/README.md)
has 12 verified artifact hashes and still retains native digital execution:
the noiseless quality screen passes, but physical calibration, range settings,
controller support and actual analog execution remain unqualified.

## Reproduction and evidence

From `software-architecture`, use a new output directory:

```bash
python3 scripts/run_gpt2_wikitext_projection.py --range-study --windows 16 --output experiments/gpt2-hybrid-v1/runs/new-adc-range-validation
python3 scripts/test_wikitext_package_rejection.py experiments/gpt2-hybrid-v1/runs/new-adc-range-validation
```

The saved run is `runs/20260909-adc-range-validation-v1/`. Its
`pre_evaluation_contracts.json` records the ranges before inference. The verifier
checks that the final contracts match, calibration tensor identity and shape,
headroom/range arithmetic, split identity, controls, quality arithmetic and
artifact hashes. The decision-package builder rejects validation data as a
replacement for test-set evidence.

## Physical interpretation

The implementation requires per-tile programmable analog gain or ADC reference
settings; their support, switch time, settling, area and energy are unverified.
Model partial-sum units have not been bound to array current and converter volts.
Thus a numerically useful ADC8 profile does not by itself establish an 8-bit
physical converter requirement or relax the existing comparator qualification.

Noiseless comparison also does not establish robustness to device noise. A
noise fraction expressed relative to a new range would change the absolute
noise assumption; it must not be interpreted as a demonstrated reduction in
physical noise. Any candidate selected here still requires independent
evaluation, a matched physical error profile and actual target execution.

The EDA sibling now contains the controller follow-up in
`docs/roadmaps/calibrated-range-controller-contract-2026-09-09.md` and
`evidence/aimc-hardware-lab/calibrated-range-controller/20260909-v2/`.
It binds all 144 ranges to a descriptor table, checks readiness and binding
epochs, and rejects unsupported analog lowering in the compiler. Physical
scaling remains unresolved; the emitted command uses digital fallback.
