# Calibrated ADC quality checkpoint

The full model-to-hardware goal remains active. A validation-selected numerical
profile now passes a separate test-context quality screen; physical execution
and measured hybrid benefit remain unproven.

## Completed evidence

The software project captured 2,064 training projection inputs and froze per-tile
ADC ranges with 10% headroom. The ranges are roughly 17–49 times narrower than
the conservative bounds. On 2,048 validation targets, calibrated ADC12 passed
the unchanged joint screen; calibrated ADC8 did not. The experiment was
noiseless and fitted no ranges on validation inputs.

The selected ADC12 profile and training tensor were then frozen in a plan for
32 test contexts disjoint from the earlier 32 test contexts. The held-out run
completed with exit code zero. On 4,096 predictions it achieved 99.3164% baseline
argmax agreement and NLL increase 0.00072734 nats/token. All numerical controls
and exact digital fallback checks passed. There were 82 clipped ADC partials
and no DAC clipping; ranges were not changed after observing those results.

Validation verification passed 13 hashes/80 rows and six mutation checks.
Held-out verification passed 13 hashes/32 contexts and seven mutation checks.
The combined decision's 12 artifact hashes also verified.

All artifact paths below are within the sibling software project's
`software-architecture/experiments/gpt2-hybrid-v1/`:

- `runs/20260909-adc-range-validation-v1/`
- `holdout-plans/20260909-calibrated-adc12/`
- `runs/20260909-calibrated-adc12-holdout/`
- `decisions/20260909-calibrated-adc12-holdout/`
- `adc-range-validation.md` for protocol, results and reproduction.

No run from this checkpoint remains active. Historical evidence and the failed
conservative-range decision are preserved.

## Required next work

The decision remains **retain native digital execution**. The quality pass is
noiseless, specific to one projection and sampled language-model contexts.
It does not establish general task acceptance, generation robustness or
physical converter precision.

The calibrated profile creates concrete hardware/controller obligations:
per-tile gain or ADC reference settings, mapping model partial-sum units to
array currents and converter volts, switching/settling costs, fixed physical
noise across settings, and compiler/controller support. The existing circuit
still lacks electrical qualification despite its DRC and active-transistor
LVS evidence. The array technology/target and matched timing/energy measurements
remain unbound.

Next work should turn these range obligations into a concrete execution and
physical mapping contract, then supply qualified circuit/target evidence.
Do not promote the numerical pass into physical authorization or invent costs.

The [controller follow-up](calibrated-range-controller-contract-2026-09-09.md)
now provides a 144-entry descriptor table, checked bank/readiness ordering and
compiler rejection of unsupported calibrated analog lowering. Use its v2
artifact package. Physical gain/reference values remain unresolved and the
generated route remains digital fallback.

The [normalized scaling follow-up](normalized-array-scaling-2026-09-09.md)
derives the tile-specific gain/reference ratios from all 2,359,296 real weight
codes and the frozen DAC/range profile. Its v2 package verifies numerical
mapping and rounding bounds; it does not assign or qualify physical components.
