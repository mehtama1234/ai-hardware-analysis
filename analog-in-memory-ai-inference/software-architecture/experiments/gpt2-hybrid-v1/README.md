# Real GPT-2 to hybrid hardware evaluation

The program goal is one real pretrained transformer through a measured digital
baseline, explicit analog/digital placement, array/converter-informed model
execution, guarded fallback, and a fair task-quality/latency/energy decision.
Physical completion requires the same workload on actual analog compute
hardware. Simulator success cannot close that requirement.

## First connected model result

The [saved run](runs/20260909-recovery-projection/README.md) replaces
`transformer.h.0.mlp.c_fc` in pinned pretrained GPT-2 with a numerical tiled
projection. Calibration uses three authored sentences; evaluation uses four
separate sentences (63 teacher-forced prediction positions) and eight-token
greedy generation. This is an engineering sensitivity fixture, not final
task-level acceptance or a representative language benchmark.

| Assumed profile | NLL increase, nats/token | Top-token agreement | Exact generated sequences |
| --- | ---: | ---: | ---: |
| Ideal tiled control | approximately zero | 100% | 4/4 |
| 10-bit DAC, 8-bit weights, 8-bit ADC | 0.025967 | 82.54% | 3/4 |
| 10-bit DAC, 8-bit weights, 12-bit ADC | 0.004654 | 100% | 4/4 |
| Same 12-bit ADC with read noise at 0.1% of tile range | 0.028013 | 96.83% | 3/4 |

The noiseless 12-bit profile passes the provisional screen; the other two
nonideal profiles fail it. This does not establish that 12 bits is necessary or
sufficient for GPT-2 generally. ADC range is a conservative tile-wide bound;
different range calibration, tiling, and device errors may change the result.
Native digital fallback reproduces logits and generated tokens exactly.

The selected 768×3072 matrix maps to 144 logical 128×128 tiles, or 288 arrays
under the assumed differential-pair representation. Each input vector requires
18,432 DAC conversions without column-tile broadcast and 18,432 ADC conversions
after assumed analog differential subtraction. Digital partial accumulation,
bias, boundary traffic, attention, KV cache, nonlinearities and other layers
remain explicit. Effective multilevel weight precision and signed input driving
are assumptions, not implemented array technology.

The package links saved measured GPT-2/T4 serving evidence as context, with an
explicit different-workload/device boundary. CPU emulator timing is not hybrid
latency and must not be compared with T4 timing to claim a speedup. Physical
energy coefficients remain missing rather than being filled with arbitrary pJ.

## Physical evidence that constrains the next step

**Latest update:** The [contact/routing rebuild](../../../../analog-digital-chip-design-eda/docs/roadmaps/converter-drc-closure-2026-09-09.md)
passes the completed full-cell Magic DRC check with zero reports and preserves
the repaired connections and 13 transistor instances. Output swings of +222 mV
and −321 mV still fail the 0.9 V margin requirement. The
[updated physical gate](physical-gate-drc-clean/physical_converter_gate_import.json)
imports this matched evidence and keeps analog blocked on electrical qualification.
The subsequent [active-transistor LVS and regeneration diagnosis](../../../../analog-digital-chip-design-eda/docs/roadmaps/converter-regeneration-diagnosis-2026-09-09.md)
adds a schematic match and shows that longer settling/precharge does not fix
the tested failure. The [latest gate](physical-gate-active-lvs/physical_converter_gate_import.json)
records that progress while retaining the electrical block.
The following paragraphs describe the earlier recovery baseline.

The latest imported [physical gate](physical-gate-recovery/physical_converter_gate_import.json)
rejects the recorded preamp-routing claim after checking the final simulated
netlist. Intermediate extraction aliases had claimed connection while the
actual preamp gates/outputs remained separate nodes.

The corrected bounded transient at EDA
`active-converter-macro-transient/20260909T163021586419Z/result.json` still
produces the same output polarity for −100, 0 and +100 mV. Zero input is no
longer counted as a polarity pass. The runner now measures both VDD and
VDD_EXT: about 0.483 pJ over 20 ns, excluding input/clock drivers and bias
generation. The earlier approximately 0.00343 pJ counted only the inactive
boundary rail. Neither quantity is a complete ADC conversion cost.

The intermediate recovery run `20260909T162820686780Z` contains a measurement
parser suffix collision and is superseded by `20260909T163021586419Z`.
Its logs remain preserved; do not use its doubled supply-energy value.

## Reproduce and verify

With cached model revision `607a30d783dfa663caf39e06633721c8d4cfcd7e` and the
recorded Python/Torch/Transformers environment, from `software-architecture`:

```bash
HF_HUB_OFFLINE=1 python3 scripts/run_gpt2_hybrid_evaluation.py --output experiments/gpt2-hybrid-v1/runs/new-run
python3 scripts/check_gpt2_hybrid_evaluation.py --package experiments/gpt2-hybrid-v1/runs/new-run
python3 scripts/check_tiled_projection_model.py
```

The output directory must be new. Each result preserves fixture, runner,
numerical model and pretrained snapshot hashes. The checker requires those
sources to remain available and unchanged; archive matching source revisions
alongside a result before changing them. The recorded environment is Torch
2.4.1+cu121 and Transformers 5.12.1 on CPU with two Torch threads.

## Remaining program gates

The [current combined decision](decisions/20260909-calibrated-adc12-holdout/README.md)
records a noiseless calibrated-ADC12 quality pass on 4,096 additional test
predictions: 99.3164% baseline argmax agreement and NLL increase 0.00072734
nats/token. The profile was selected on validation data, then frozen before
testing on contexts disjoint from the earlier 32 test contexts. The earlier
conservative-range profiles failed their quality screens and remain preserved
in the [original decision](decisions/20260909-wikitext-v2/README.md).

The [range calibration study](adc-range-validation.md) does not establish
physical gain/reference support, noise robustness, timing/energy benefit or
general task acceptance. The new quality pass therefore retains digital
execution while the physical and controller requirements remain open.

The [shared compiler/runtime integration](compiled-runtime.md) now lowers the
selected real GPT-2 projection into the existing review bytecode and executes
its digital fallback through checked SRAM offsets. It also defines converter
sharing and movement counts for a separate candidate analog schedule.

1. Extend the [pinned WikiText sample evaluation](wikitext-evaluation.md) to
   representative workload coverage and task-level acceptance criteria. Its
   32 test contexts broaden the authored fixture; provisional thresholds do
   not supersede prior Optdigits or portfolio acceptance contracts.
2. Specify a realizable array, signed representation, cell/slice precision,
   voltage/conductance ranges and converter-sharing schedule. Bind the frozen
   calibrated ranges to realizable gain/reference settings and test a fixed
   physical noise profile across those settings and additional projections.
3. Qualify complete converter transfer, settling, PVT/mismatch/noise and
   calibration. The repaired preamp path now has full-cell DRC and active
   transistor LVS evidence, but electrical margin still fails. Bind future
   converter evidence to the same array/profile rather than borrowing a
   comparator margin.
4. Feed matched converter/array errors and costs into this real-model execution
   and the common compiler/runtime contract. Include transfer, calibration,
   programming, scheduling and fallback overhead in the comparison.
5. Run on an identified analog compute target with controller and synchronized
   instrumentation. Report same-task accuracy, latency, energy and reliability.

Current decision: **hybrid hardware benefit unproven; native digital execution
remains authoritative.** The new result closes a real-model sensitivity gap,
not the overall program.
