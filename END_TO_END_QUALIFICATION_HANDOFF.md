# End-to-End Model-to-Chip Qualification Handoff

Date: 2026-09-11

## Authoritative goal

Build an evidence-first AI hardware verification product that takes one frozen
transformer workload through:

```text
model contract -> reference execution -> Colab GPU baseline -> digital fallback
-> analog/hybrid mapping -> converter/circuit qualification -> compiler/runtime
-> matched accuracy/latency/energy comparison -> bounded ship/no-ship decision
```

An independent reviewer must be able to identify the model operation, tensor
and precision contract, backend and hardware representation, measured result,
cost, failure behavior, and provenance. A negative result is valid; an
unsupported analog advantage is not.

## Repository handoff

| Area | Owner | Handoff artifact |
| --- | --- | --- |
| Model/workload | `DeepSeek-From-Scratch` | frozen model contract, inputs, reference outputs, seeds, hashes |
| GPU baseline | `gpu-mode-curriculum` and DeepSeek Colab | fresh T4 receipt, latency/resource data, CUDA artifacts, output hashes |
| Hybrid mapping | `analog-in-memory-ai-inference` and analysis | placement, ADC/DAC assumptions, calibration, data movement, fallback, task error |
| Circuit qualification | `analog-digital-chip-design-eda` | code-map, legal-node, timing, PVT, mismatch, waveform, and failure receipts |
| Product evidence | `ai-hardware-analysis` | joined manifests, hashes, claim boundaries, and release decision |

Repositories remain independently runnable. They are joined only through
versioned, hash-bound manifests and receipts.

## Frozen qualification slice

Use one unchanged GPT-2-style transformer projection/MLP layer and held-out
inputs. Freeze the model/source revision, tokenizer or input encoding,
checkpoint hash, tensor shapes, batch/sequence lengths, precision, seeds,
reference-output hashes, calibration/evaluation split, and accuracy/latency/
energy/legal-node/timeout/fallback thresholds.

Run the same contract in:

1. authoritative digital/reference execution;
2. profile-driven hybrid simulation using a circuit-derived transfer/timing
   profile; and
3. compiler/runtime execution whose trace agrees with the workload plan.

The GPU run is a separate baseline and must not be confused with circuit or
silicon measurement.

## Hard gates

1. **Model:** deterministic outputs and shape/precision contract.
2. **GPU:** fresh Colab T4 receipt, output hash, latency/resource data, and
   downloaded artifacts matching the receipt hashes.
3. **Digital:** identical-scope fallback output and complete transfer,
   accumulation, memory, latency, and energy accounting.
4. **Circuit:** all requested codes converge, transfer is monotonic, every
   internal node is within its declared legal range, and exact reset,
   acquisition, capture, and retention waveforms are stored.
5. **Robustness:** declared PVT, mismatch/noise, repeated-history, and
   numerical/functional-failure populations are separately classified.
6. **Workload:** digital and hybrid held-out results report accuracy, latency,
   energy scope, data movement, calibration, and fallback fraction.
7. **Claim:** every headline claim points to evidence of the correct kind;
   `analog_authorized` stays `false` unless every declared gate passes.

## Current verified state

The plumbing is substantially complete: bridge validation passes 16 artifacts,
integration validation passes 22 deliverables, the hybrid transformer slice
passes with 16 operators and 76 schedule events, simulator replay passes its
stated fixture comparison, and the circuit evidence audit passes 21/21
implemented checks.

The physical converter is not qualified. The latest complete 4 um active-hold
16-code campaign with a 250-ps transistor handoff measured only 5/16 codes;
the remaining codes hit the declared numerical-convergence timeout, and the
measured subset still produced code-dependent rail excursions. Earlier
common-resolution campaigns also measured 15/16 codes and produced illegal
high-code bottom-plate values. Active-hold,
device-bank, slew, keeper, re-clamp, and isolated-rail diagnostics did not
close the legal-node contract. The consolidated active-hold decision is in
`analog-digital-chip-design-eda/evidence/aimc-simulator-adapters/sky130-transistor-dac-active-hold-sweep.json`.
The isolated one-bit follow-up at 0.9 V common mode timed out before a
measurement at both 5 ps and an explicit 50 ps transient step. The latest
receipt is therefore a reproducible convergence failure, and the next
topology revision must restore a convergent one-bit cell before rebuilding the
array. An 8-device high-side bank at 1.5 V also timed out with the explicit
50 ps step, so device banking is not currently a reproducible repair.
Finite gate rise and explicit `uic` initialization also timed out, closing the
current solver/control-parameter screen and pointing the next experiment at a
netlist-level one-bit cell redesign.
The first bounded-edge cell revision (50 ps low-side release and high-side
rise) now converges, but transfers only `0.472123 V` by 2.5 ns and `0.8239104 V`
by 3.5 ns for a 1.8 V target. This narrows the next repair to high-side charge
transfer speed/holding, without authorizing the cell.
The parallel NMOS high-side assist also timed out, rejecting device-parallel
charge transfer as the next fix; the next revision must change the isolated
charge-transfer/hold cell topology itself.
An isolated 64 um high-side PMOS with the bounded edges also timed out, so
high-side width alone is rejected as a repair.
The first explicitly isolated precharge/transfer/hold netlist also timed out
before measurement, so its phase sequence is not yet a usable cell. The next
redesign must simplify or decompose that topology while retaining separate
rail-arrival and stored-plate measurements. The simplified single-PMOS
isolated transfer variant also timed out, so the intermediate precharge/hold
sequence remains unqualified.
Adding bounded 100 ohm precharge-source damping also timed out, so passive
precharge damping is not currently a sufficient repair.
The 10 pF intermediate-rail reservoir with early precharge also failed: the
rail was only `0.6887266 V` at the precharge check and the stored plate only
`0.01036779 V` at 2.5 ns. Reservoir sizing is therefore not a substitute for
a faster isolated transfer/hold topology.
At a longer 180-second diagnostic bound the damped isolated PMOS eventually
measured, but its rail fell to `1.269928 V` and the stored plate reached only
`0.2602481 V` at 2.5 ns. The topology is therefore convergent-but-transfer
failing, not qualified. At a longer 7.9 ns acquisition point the same cell
improved to `1.670877 V` with a `129.123 mV` rail error, confirming a strong
timing dependency while remaining outside the 2.5 ns decision contract.

The current circuit-derived profile explicitly remains bounded with
`analog_authorized: false`. The retained Colab CUDA receipt also requires a
fresh GPU rerun because local artifacts were overwritten by a CPU run.

The local profile-to-workload package is now complete as bounded software
evidence. It joins the frozen GPT-2 projection, 162 held-out tensor vectors,
disjoint affine calibration, threshold governance, compiler/runtime trace,
per-vector cost/timing ledger, calibration amortization, break-even
sensitivity, and fail-closed stress coverage for all three open profile
receipts. Its decision audit passes 4/9 declared gates and remains
`analog_candidate_authorized: false`; modeled pJ/cycles are not measured
energy or latency. The package and its decision are hash-bound into the
product manifest under the workload gate. Its `claim_ledger.json` is the
review surface for distinguishing locally proven, bounded, modeled-only,
blocked, and unauthorized claims.

The next local extension has begun in the GPT-2 qualification worktree: a
simultaneous replay of `mlp.c_fc`, `mlp.c_proj`, and `attn.c_attn`. Its ideal
control passes. The authoritative calibrated receipt reaches only `0.952381`
teacher-forced argmax agreement and `3/4` exact generations, below the
provisional `0.99` screen; the uncalibrated receipt is retained at `0.936508`
and `4/4`. The multi-module decision package now has bounded per-module
calibration, governed fallback-trace, and modeled matched-cost evidence. It
passes 6/8 local gates. The joint quality gate remains closed, the cost
coefficients are not measured energy or latency, and it does not promote the
single-module result or authorize analog execution.

The local sensitivity follow-up is recorded in
`analog-in-memory-ai-inference/software-architecture/experiments/gpt2-hybrid-v1/runs/20260911-local-multimodule-sensitivity-v2/sensitivity_report.json`.
It covers ADC8/10/12/14/16, module isolation/ablation, and activation-bound
stress. Only isolated `c_fc` and `c_attn` pass the provisional screen; the
complete three-module route fails even at ADC16, and isolated `c_proj` is the
weakest module. The next local action is to attribute that accumulation to
module boundaries and test guarded per-module precision/fallback policy.
The first guarded policy was tested and rejected: analog `c_fc` plus
`attn.c_attn` with digital `c_proj` still reached only `0.984127`, so the
enforced policy is full-slice digital fallback. Its decision is recorded in
`local-multimodule-fallback-policy-v1/fallback_policy.json`.

The error-attribution receipt shows that `c_proj` has the largest isolated
output and final-logit disturbance, while the full route is non-additive
(full/isolated-sum final-logit error ratio `0.763`). This supports a focused
module-boundary and interaction investigation rather than a blanket ADC-bit
increase; the result remains local CPU evidence only.

The profile-aware governor is recorded in
`analog-in-memory-ai-inference/software-architecture/experiments/gpt2-hybrid-v1/qualification/local-multimodule-profile-governor-v5/profile_governor_report.json`.
It distinguishes numerically eligible isolated candidates from an authorized
route, but currently enforces full digital fallback for every evaluation case.
The subsequent six-text disjoint stress validation invalidated the isolated
recommendation: `attn.c_attn` reached only `0.986301` agreement and the full
route `0.931507`. With expanded calibration, `c_proj` and the full route
improved to `0.958904` but still failed. Governor v5 therefore recommends no analog modules and
requires full digital fallback until a route generalizes.

The numerical error-budget receipt is at
`analog-in-memory-ai-inference/software-architecture/experiments/gpt2-hybrid-v1/runs/20260911-local-error-budget-v1/error_budget_report.json`.
Weight quantization alone passes the workload screen, while DAC-only,
ADC-only, and combined profiles fail. ADC/readout resolution is therefore
the dominant current numerical failure contributor, with DAC quantization
secondary; this remains CPU replay evidence, not hardware qualification.

The stateful transfer profile is the first tested profile to pass both the
original and disjoint stress workloads: `1.0` agreement with `4/4` and `6/6`
generations respectively. It uses a calibrated previous-provisional-output
term under `weight16/DAC16/ADC14` and `1.25x` range. The stateful governor and
162-row route/cost trace are recorded under
`analog-in-memory-ai-inference/software-architecture/experiments/gpt2-hybrid-v1/qualification/local-stateful-profile-governor-v1/`.
This is numerical CPU evidence; the enforced route remains digital fallback
until physical authorization gates pass.

The third six-text holdout invalidates broad stateful-profile generalization:
the stateful route reaches only `0.975309` agreement there, despite passing
the original and earlier stress splits. The implementation scopes previous-row
history to each projection call, so this is a profile-generalization failure
within the tested run rather than evidence of cross-request state leakage. The
full result is retained at
`analog-in-memory-ai-inference/software-architecture/experiments/gpt2-hybrid-v1/runs/20260911-local-stateful-third-holdout-v1/stateful_transfer_report.json`.

The profile-design sweep and disjoint redesigned-profile stress receipt are
also retained in the manifest. `weight16/DAC16/ADC14` and `all16` pass the
original four-text screen, but `weight16/DAC16/ADC14` reaches only `0.958904`
on the six-text stress set. The current quality gap therefore remains after
precision redesign and requires converter range/transfer-model investigation.

Per-module range allocation was also tested. The strongest candidate assigns
`1.25x` range to `attn.c_attn` under `weight16/DAC16/ADC14`: the full stress
route reaches `0.972603`, still below `0.99`, although the isolated attention
route reaches `1.0`. Simple range allocation therefore does not solve the
multi-module transfer/interaction gap.

The conservative three-context matrix is retained at
`analog-in-memory-ai-inference/software-architecture/experiments/gpt2-hybrid-v1/qualification/local-multicontext-matrix-v1/multicontext_matrix.json`.
It requires all context families to pass; two pass and the third fails, so the
stateful profile is not promoted and full digital fallback remains enforced.

The dedicated stateful multi-module decision package is at
`analog-in-memory-ai-inference/software-architecture/experiments/gpt2-hybrid-v1/qualification/local-stateful-multimodule-decision-v1/decision_audit.json`.
It passes 6/8 bounded local gates, with the third-holdout generalization gate
and analog authorization intentionally failed.

The next fully local end-to-end goal is now explicit: establish activation
distribution coverage before changing the transfer model again. The runner
measures all three transformer boundaries over the disjoint calibration,
original, prior-stress, and third-holdout text families, and reports min/max,
percentiles, per-text maxima, and held-out-to-calibration coverage ratios. The
receipt is at
`analog-in-memory-ai-inference/software-architecture/experiments/gpt2-hybrid-v1/runs/20260911-local-activation-coverage-v1/activation_coverage_report.json`;
its checker is
`analog-in-memory-ai-inference/software-architecture/scripts/check_multicontext_activation_coverage.py`.
This is CPU distribution evidence only: it can identify calibration holes and
guide a bounded profile redesign, but it does not authorize analog execution
or claim hardware latency, energy, yield, or model quality.

The coverage-aware governor now consumes that receipt at
`analog-in-memory-ai-inference/software-architecture/experiments/gpt2-hybrid-v1/qualification/local-coverage-aware-profile-governor-v4/coverage_aware_profile_governor.json`.

A genuinely different second-order stateful correction was then tested using
the two previous provisional output rows. It passed only the original split;
prior stress fell to `0.986301` and the third holdout remained `0.987654`.
This rejects both tested sequence-history profile orders as generalized
routes. The complete comparison is retained at
`analog-in-memory-ai-inference/software-architecture/experiments/gpt2-hybrid-v1/runs/20260911-local-second-order-stateful-v1/stateful_transfer_report.json`.

An independent per-module residual correction conditioned on incoming
activation L2 energy was also tested. It reached `0.984127` on original,
`0.986301` on stress, and `0.987654` on the third holdout, so it fails all
three screens. This closes the tested affine, output-history, and input-energy
correction families as generalized routes; the receipt is at
`analog-in-memory-ai-inference/software-architecture/experiments/gpt2-hybrid-v1/runs/20260911-local-input-energy-residual-v1/context_transfer_report.json`.

The staged local error decomposition now joins the error-budget and boundary
intervention receipts. `c_proj` is the dominant output-error boundary under
weight, DAC, ADC, and combined profiles; ADC-only error is its largest isolated
stage (`0.076766` relative L2), and perturbations at that boundary grow
monotonically into final logits. The next constrained local experiment is
therefore `c_proj` ADC/readout mitigation, not another global transfer
correction. The joined report is at
`analog-in-memory-ai-inference/software-architecture/experiments/gpt2-hybrid-v1/runs/20260911-local-module-error-decomposition-v1/module_error_decomposition_report.json`.

The first constrained mitigation raised ADC resolution only for `c_proj` from
14 to 16 bits while retaining the stateful calibration and all other module
settings. It passed the original split, but stress fell to `0.986301` and the
third holdout remained `0.987654`. The targeted report is retained at
`analog-in-memory-ai-inference/software-architecture/experiments/gpt2-hybrid-v1/runs/20260911-local-targeted-cproj-adc-v1/targeted_cproj_adc_report.json`.
This rejects ADC resolution alone as a general solution; the next local
experiment must address the `c_proj` transfer/boundary behavior itself.

The first constrained boundary correction used a per-channel quadratic transfer
model at `c_proj`, while retaining stateful calibration elsewhere. It passed
the original split but failed stress (`0.986301`) and the third holdout
(`0.987654`). The receipt is at
`analog-in-memory-ai-inference/software-architecture/experiments/gpt2-hybrid-v1/runs/20260911-local-targeted-cproj-transfer-v1/targeted_cproj_adc_report.json`.
This closes the tested software-side `c_proj` corrections; the next local
experiment should model the converter/readout stage explicitly and preserve
digital fallback unless all three splits pass.

The explicit readout-trajectory test added a first-order settling/leak term at
the `c_proj` ADC partial-output stage, resetting state at each sequence. Small
fractions (`0.001` and `0.01`) preserved original and stress but still failed
the third holdout at `0.987654`; `0.05` degraded all splits. Simple settling
leak therefore does not generalize. The sweep is retained at
`analog-in-memory-ai-inference/software-architecture/experiments/gpt2-hybrid-v1/runs/20260911-local-cproj-settling-sweep-v1/targeted_cproj_adc_report.json`.

The explicit reset/charge/settle state-machine variant was then tested. Full
charge with `0.01` settling reproduced the original/stress passes but still
failed the third holdout at `0.987654`; reducing charge to `0.95` degraded all
three splits. The result is retained at
`analog-in-memory-ai-inference/software-architecture/experiments/gpt2-hybrid-v1/runs/20260911-local-cproj-state-machine-v1/targeted_cproj_adc_report.json`.
Simple converter trajectory assumptions therefore remain insufficient; the
next local step is to construct a circuit-derived transfer table or preserve
the digital fallback boundary.

The retained circuit receipts were assembled into a transfer-table intake. It
contains measured rows for only 6 of the required 16 four-bit codes; codes
`0, 2, 3, 4, 5, 6, 7, 9, 11, 12` are absent. The adapter therefore refuses to
bind the partial table to `c_proj`, and analog authorization remains closed.
The intake is recorded at
`analog-in-memory-ai-inference/software-architecture/experiments/gpt2-hybrid-v1/runs/20260912-local-circuit-transfer-table-v1/circuit_transfer_table.json`.

The first isolated source-follower latch candidate was also exercised as a
bounded physical diagnostic. All four polarity and follower-size/bias cases
timed out before measurement (`0/4` measured, `0/4` passing), so this
candidate is rejected at the convergence gate and cannot be promoted into the
converter or workload profile. Its receipt is
`analog-digital-chip-design-eda/evidence/aimc-simulator-adapters/sky130-source-follower-isolated-latch-candidate.json`.
The next physical revision must change the transfer/hold topology itself and
retain the explicit timeout classification.

The declared isolated PMOS transfer/hold cell was independently rerun under
the 50 ps transient step and 2.50 ns decision-time contract. It again reached
the numerical-convergence timeout before measurement. The follow-up receipt
is
`analog-digital-chip-design-eda/evidence/aimc-simulator-adapters/sky130-isolated-bottom-plate-cell-followup-20260912.json`.
This confirms that the current precharge/isolated-transfer topology is not a
qualified handoff; the next repair must change its topology before any
16-code campaign is attempted.

The paired-row balanced latch layout redesign passed Magic DRC, connectivity,
body-tie, capacitance-export preflight, and same-candidate sub-block LVS. Its
extracted transient nevertheless failed both polarity-edge margin cases: the
sign was correct but the output differential was only about `76 uV` versus the
`0.5 V` margin requirement, and both output nodes overshot the `1.8 V` legal
rail to about `1.867 V`. The symmetric-capacitance diagnostic reproduced the
same weak differential and overshoot, so extracted capacitance asymmetry is
not the primary cause. The candidate remains diagnostic-only and is not a
qualified latch or converter. Its physical preflight is under
`analog-digital-chip-design-eda/evidence/aimc-simulator-adapters/balanced-latch-layout/20260912T191434473920Z`,
LVS is under
`analog-digital-chip-design-eda/evidence/aimc-simulator-adapters/isolated-latch-v2-lvs/20260912T191454044864Z`,
and the extracted transient receipts are under
`analog-digital-chip-design-eda/evidence/aimc-simulator-adapters/isolated-latch-v2-transient/`.
The next redesign must address latch drive/regeneration and legal output
clamping before any array integration.

The next named schematic candidate, a two-phase preamp-then-latch topology,
is the first local physical branch to clear its bounded electrical screen. Both
target-edge cases converged and resolved with the contracted polarity; the
output differential was `+/-1.3710865 V`, and sampled-node kickback was
`19.7 uV`, below the `219.7265625 uV` half-LSB hard line. The receipt is
`analog-digital-chip-design-eda/evidence/aimc-simulator-adapters/sky130-two-phase-preamp-latch-candidate.json`.
This remains a schematic candidate only: it has no extracted layout, LVS,
noise, offset, PVT, mismatch, SAR, or converter qualification. The next
physical action is to implement this phase-separated handoff as a layout
candidate and repeat DRC, connectivity, LVS, and extracted transient checks.

The existing extracted two-stage handoff diagnostic was also rerun before
starting that layout work. It measured both target-edge cases, but only one
of two cases passed the latch polarity contract: the positive `+0.1529706 mV`
edge resolved with the wrong output sign. The reported sampled-node movement
was zero for both cases, so this is a polarity/offset handoff failure rather
than evidence that the phase separation is physically qualified. Receipt:
`analog-digital-chip-design-eda/evidence/aimc-simulator-adapters/sky130-two-stage-preamp-latch-handoff.json`.

To localize that failure, the handoff runner now has an explicit
frontend-netlist and pin-interface selector. Replaying against the extracted
strong-sense frontend and the previously polarity-confirmed capacitive
isolation frontend still produced only one passing polarity out of two. In
the capacitive-isolation replay, both target edges reached approximately
`+5.4 mV` at the preamp sense difference and the latch settled to the same
raw output sign. A frontend swap is therefore not a sufficient fix; the next
design change must preserve signed differential information through the
preamp/latch boundary, with explicit regeneration-state reset or handoff
drive verified on both edges.

The next physical branch is now grounded in an existing active-isolation
sub-block. Its wrapper check reports zero Magic DRC errors, successful
extraction, and a unique two-device LVS match against the independent
Sky130 reference. Receipt:
`analog-digital-chip-design-eda/evidence/aimc-simulator-adapters/active-isolation-pair-wrapper-physical-check.json`.
The existing transistor active-isolation-plus-preamp schematic evidence also
passes both signed target edges after zero-input correction and clears the
`0.5 mV` preamp output-margin target, but remains schematic-only. The next
integration step is to connect this physically checked isolation pair to the
phase-separated preamp/latch and rerun extracted transient and polarity
checks; neither the wrapper nor the schematic receipt authorizes analog
execution by itself.

An extracted integration rerun using the recorded `extracted_560k_pre4_4ua`
setting and the required preamp-input polarity swap did not reproduce the
older schematic receipt: both target-edge cases timed out before measurement.
The fresh receipt is
`analog-digital-chip-design-eda/evidence/aimc-simulator-adapters/sky130-transistor-active-isolation-preamp-current-extracted-swapped2.json`.
This makes extracted convergence a prerequisite for the next latch
integration; the prior passing preamp result remains historical evidence and
is not promoted as current physical proof.

The extracted integration was then rerun with an explicit `1e12 ohm` global
ngspice shunt to regularize the intentionally floating parasitic regions.
Both target edges measured, both zero-input-corrected signs passed, and the
worst corrected preamp output difference was `0.7566 mV`, above the `0.5 mV`
diagnostic margin. Receipt:
`analog-digital-chip-design-eda/evidence/aimc-simulator-adapters/sky130-transistor-active-isolation-preamp-rshunt1e12.json`.
This is convergence evidence for the extracted isolation-plus-preamp chain,
not physical qualification: the shunt must be sensitivity-checked and then
removed or replaced by explicit physical leakage paths before latch/SAR
signoff.

The shunt sensitivity check is stable across three decades: `1e11 ohm`,
`1e12 ohm`, and `1e13 ohm` each measured both target edges, passed both
corrected polarities, and cleared the `0.5 mV` margin. The worst corrected
margins were respectively `0.7547 mV`, `0.7566 mV`, and `0.7569 mV`. Receipts:
`analog-digital-chip-design-eda/evidence/aimc-simulator-adapters/sky130-transistor-active-isolation-preamp-rshunt1e11.json`,
`analog-digital-chip-design-eda/evidence/aimc-simulator-adapters/sky130-transistor-active-isolation-preamp-rshunt1e12.json`,
and
`analog-digital-chip-design-eda/evidence/aimc-simulator-adapters/sky130-transistor-active-isolation-preamp-rshunt1e13.json`.
This establishes numerical sensitivity, not a physical leakage model; the
next implementation must replace the global shunt with explicit legal device
or resistor paths and repeat the same envelope.

That replacement has now been exercised in SPICE. Four explicit high-value
resistors from the extracted frontend's floating parasitic regions to a
declared `0.9 V` common-mode node were used with global `rshunt` disabled.
Both target edges passed after correction, with a worst margin of `0.8077 mV`
at both `1e12 ohm` and `1e13 ohm`. Receipts:
`analog-digital-chip-design-eda/evidence/aimc-simulator-adapters/sky130-transistor-active-isolation-preamp-explicit-leak1e12.json`
and
`analog-digital-chip-design-eda/evidence/aimc-simulator-adapters/sky130-transistor-active-isolation-preamp-explicit-leak1e13.json`.
These are explicit circuit leakage paths, not yet drawn layout devices; the
next physical step is to implement and extract the same paths, then rerun
the polarity and margin envelope.

The floating-region labels were then promoted to four explicit ports in a
derived frontend layout cell. Magic reported zero DRC errors and extracted a
13-port frontend containing those regions. That extracted frontend was
attached to the extracted transistor isolation pair and rerun with explicit
`1e5 ohm` leakage paths and no global solver shunt. Both signed target edges
passed correction and margin; the worst corrected output was `0.5349 mV`.
Receipts:
`analog-digital-chip-design-eda/evidence/aimc-simulator-adapters/sky130-leaky-ultra-sense-frontend-physical.json`
and
`analog-digital-chip-design-eda/evidence/aimc-simulator-adapters/sky130-transistor-active-isolation-preamp-physical-leak1e5-fixed.json`.
This is the first extracted physical-interface branch that clears the signed
preamp screen. The four leakage resistors are still external SPICE elements,
so the branch is not yet layout-qualified; their legal geometry and extracted
resistance remain the next physical gate.

The missing-code adapter now classifies every requested code: the 10 absent
codes are explicitly `unsupported`, the six measured codes remain
`measured_diagnostic_only`, and all 16 route to digital fallback. This policy
is recorded at
`analog-in-memory-ai-inference/software-architecture/experiments/gpt2-hybrid-v1/runs/20260912-local-transfer-table-fallback-policy-v1/transfer_table_fallback_policy.json`.
No partial circuit evidence can silently enter the hybrid workload path.

The compiler/runtime replay now exercises all 16 converter codes. It emits
explicit `unsupported` events for the 10 absent codes, routes every code to
`RUN_DIGITAL_FALLBACK`, executes zero analog instructions, and records exact
fallback output preservation. The trace is at
`analog-in-memory-ai-inference/software-architecture/experiments/gpt2-hybrid-v1/runs/20260912-local-transfer-table-runtime-trace-v1/transfer_table_runtime_trace.json`.

That all-code policy is now joined to the transformer’s 162-vector runtime
schedule. Every scheduled vector inherits the complete converter-code contract,
all 10 unsupported codes remain explicit, all module routes are digital
fallback, and zero analog instructions execute. The joined trace is at
`analog-in-memory-ai-inference/software-architecture/experiments/gpt2-hybrid-v1/runs/20260912-local-transformer-transfer-table-runtime-v1/transformer_transfer_table_runtime_trace.json`.

The fallback output audit joins that 162-vector schedule with the retained
native-model replay. Exact logits and generated sequences are proven for four
held-out contexts; per-vector tensor parity is deliberately marked open because
those tensors were not retained. This prevents the handoff from overstating
the evidence while preserving the authoritative digital reference. The audit
is at
`analog-in-memory-ai-inference/software-architecture/experiments/gpt2-hybrid-v1/runs/20260912-local-transformer-fallback-output-audit-v1/transformer_fallback_output_audit.json`.
Because all three module families have at least one out-of-envelope held-out
context, it records a 162-vector digital fallback trace and blocks analog
promotion. The next experiment is consequently falsifiable: change only the
calibration/range policy, rerun coverage and the held-out replay, and retain
fallback if the envelope or quality gate still fails.

The remaining tensor-retention gap is now closed locally. A fresh replay of the
same native GPT-2 prefill plus cached-decode schedule captured every one of the
162 vectors for all three target modules and independently recomputed each
projection with GPT-2's digital `torch.addmm` contract. All rows pass the
explicit float32 parity gate (`atol=3e-5`, `rtol=1e-5`); raw row fingerprints
remain in the artifact as diagnostics, with kernel-order differences kept
separate from functional mismatches. This proves complete local digital
fallback coverage, not analog execution, hardware timing, energy, or silicon
behavior. The package is at
`analog-in-memory-ai-inference/software-architecture/experiments/gpt2-hybrid-v1/runs/20260912-local-transformer-per-vector-fallback-fingerprint-v7/per_vector_fallback_fingerprint.json`.

These local results are consolidated into the hash-bound digital qualification
package at
`evidence/local-digital-qualification-v1/local_digital_qualification_package.json`.
Its decision is explicitly **digital reference and deterministic fallback only**:
all 162 scheduled vectors route through fallback, while modeled cost remains
counterfactual and analog authorization remains closed. The package checker is
`scripts/check_local_digital_qualification_package.py`.

The corresponding counterfactual advantage report sweeps analog-array and
converter cost coefficients against the same digital reference. At the
retained nominal assumptions it models a 98.2% cost reduction and 97.7% cycle
reduction, with a converter break-even of approximately 190.6 pJ at the
nominal array coefficient. These numbers are sensitivity outputs, not energy
or latency measurements; the enforced route remains digital fallback. The
report is at
`evidence/counterfactual-hybrid-advantage-v2/counterfactual_hybrid_advantage_report.json`.
The reproducible local rebuild/check entrypoint is
`python3 scripts/run_local_derived_qualification.py`; it writes to a fresh
temporary directory and never overwrites the retained evidence packages.
It also emits a portable `local-qualification-evidence.zip` containing the
hash-bound reports, goal, handoff, manifest, and source receipts; the archive
is checked by `scripts/check_local_qualification_archive.py`.

That experiment has now been run with a 12-text coverage-guided calibration
fixture, disjoint from every evaluation split. The stateful profile retained
`1.0` agreement on the original and prior-stress sets, but the third holdout
reached only `0.987654`; the `0.99` screen therefore remains closed. The
replay is retained at
`analog-in-memory-ai-inference/software-architecture/experiments/gpt2-hybrid-v1/runs/20260911-local-stateful-calibration-v3-v1/stateful_transfer_report.json`.
The resulting coverage-aware governor records the negative promotion decision
and keeps all 162 vectors on digital fallback at
`analog-in-memory-ai-inference/software-architecture/experiments/gpt2-hybrid-v1/qualification/local-coverage-aware-profile-governor-v4/coverage_aware_profile_governor.json`.

Affine versus quadratic per-channel transfer correction was tested on both
splits. Affine passed only the stress split; quadratic passed only the
original split. No single transfer model generalized across both, so adding a
nonlinear correction alone is insufficient and the governor remains fully
digital.

Magnitude-context affine transfer was then tested using a calibration-median
partition. It passed the original split (`1.0` agreement) but failed stress
(`0.986301`); global affine showed the opposite split bias. Context partitioning
alone therefore does not produce a generalizable profile.

The causal-style boundary intervention receipt is recorded at
`analog-in-memory-ai-inference/software-architecture/experiments/gpt2-hybrid-v1/runs/20260911-local-boundary-interventions-v1/boundary_intervention_report.json`.
It injects calibrated ADC12 perturbations at amplitudes 0.25x, 0.5x, 1x,
and 2x, and measures downstream outputs and final logits. `c_proj` is the
dominant propagation-sensitive boundary; the measurements are local CPU
interventions, not causal silicon evidence.

The machine-readable joined gate state is generated at
`ai-hardware-analysis/evidence/end-to-end-qualification-manifest.json` by
`ai-hardware-analysis/scripts/build_end_to_end_qualification_manifest.py`.
Regenerate and print the complete gate summary from the product root with:

```bash
python3 scripts/report_end_to_end_status.py
```

Validate the handoff and its fail-closed invariants with:

```bash
python3 scripts/validate_end_to_end_handoff.py
```

For the reproducible local-only path, run the orchestrator from the product
root:

```bash
python3 scripts/run_local_end_to_end_qualification.py
```

It rebuilds the profile-to-workload package and decision from the retained
local GPT-2/tensor/calibration receipts, regenerates the joined manifest, and
runs both validators. It does not run Colab, require a GPU, or authorize
analog execution.

To validate the complete local cross-project package—including the public
digital reference release, clean archive replay, browser/API adversarial gate,
and this model-to-workload qualification—run from the product root:

```bash
python3 scripts/run_local_unified_release_acceptance.py
python3 scripts/check_local_unified_release_acceptance.py
```

The resulting `.artifacts/local-unified-release-acceptance.json` is the
top-level local handoff receipt. It must remain bounded to reference and local
CPU evidence; it cannot authorize analog execution or promote GPU, physical,
measured-energy, or silicon claims.

The current frozen-model source receipt is the immutable
`20260912-local-profile-replay-tensors-v4` run. The prior v3 receipt is
retained as history but is not current evidence because its source hash for
`tiled_projection_model.py` predates the transfer-model extensions.

Its current decision is `digital_reference_and_fallback_only`; a receipt hash
mismatch, open physical qualification, or open workload gate cannot be hidden
by a green software validator.
The DeepSeek readiness summary consumes this joined circuit gate when reporting
`physical_converter_qualified`, so its summary cannot promote a stale local
physical-evidence status.

## Immediate work order

### 1. Preserve the evidence boundary

Use separate diagnostic output stems, retain timeout decks/logs, and rerun the
existing model, bridge, integration, and physical validators. Never let a
converged subset become an acceptance receipt.

### 2. Repair and qualify the physical cell

Replace the direct bottom-plate pass/hold arrangement with an independently
isolated transfer and hold cell. For every code and required corner, measure
rail disconnect/arrival, gate-edge charge injection, top-plate kick, selected
and unselected bottom-plate voltages, convergence/failure class, exact waveform,
and source/model hashes. Do not bind a workload profile until a complete legal
16-code receipt is stable at the declared decision time; then reconnect the
comparator/controller and run PVT and mismatch campaigns.

### 3. Restore external evidence

Run `DeepSeek-From-Scratch/integration/DeepSeek_Model_GPU_Chip_Bridge.ipynb` in
GPU Colab using the documented ZIP snapshot. Clear stale receipts, run all four
CUDA benchmarks, create a fresh receipt, download all artifacts, restore them
locally, and rerun integration proof.

### 4. Close the workload decision

After circuit qualification, bind the profile version and hash to the existing
transformer package. Run digital, hybrid, and compiler/runtime modes on held-
out inputs with ADC/DAC overhead, calibration, memory movement, energy scope,
latency, and digital fallback. Publish one conclusion:

```text
analog advantage | no advantage | unresolved
```

Unsupported regions remain open and cannot authorize analog execution.

### 5. Local-only continuation

Use the activation-coverage receipt to choose one falsifiable profile change:
expand calibration/range where a held-out module exceeds the retained
distribution, then rerun the same three-context qualification matrix and the
third holdout. Promote nothing unless every context passes; if the expanded
profile still fails, preserve the negative boundary and stop tuning that
profile family. This closes the remaining software question without Colab,
hardware, or new external measurements.

That local continuation has now been executed. Coverage-guided and second-order
stateful replays did not generalize across all held-out contexts, and targeted
`c_proj` ADC, transfer-correction, settling, and state-machine variants did not
open the promotion gate. The complete 162-vector fallback fingerprint and the
counterfactual cost/quality sensitivity package are now retained. The local
software conclusion is therefore **digital reference and deterministic fallback
only**; further local profile tuning should not be treated as progress unless it
changes the declared held-out quality result without weakening the evidence
boundary.

The latest physical increment is a legal extracted Sky130 resistor wrapper around
the derived ultra-sense frontend. Its four drawn `uhrpoly` branches extract as
`ultra_sample_p_sense_p_region`, `ultra_sample_n_sense_n_region`,
`symmetric_reset_region`, and `symmetric_latch_clock_region` to `float_cm`, with
zero Magic DRC errors. When this wrapper is attached to the extracted active
isolation pair and the preamp, the `extracted_560k_pre3p9_4ua` setting passes both
signed transient cases with no timeout and a minimum corrected differential of
`0.0005003 V` against the `0.0005 V` local target. Receipts are
`analog-digital-chip-design-eda/evidence/aimc-simulator-adapters/sky130-leaky-frontend-resistor-wrapper-physical.json`
and
`analog-digital-chip-design-eda/evidence/aimc-simulator-adapters/sky130-transistor-active-isolation-preamp-physical-resistor-wrapper-pre3p9.json`.
This advances the physical branch but does not prove extracted resistor value or
corner leakage, full frontend LVS, noise/PVT/mismatch, latch decision, SAR
conversion, energy, or converter acceptance; the four resistor branches are
still not full converter qualification evidence.

The next staged physical-DAC gate was also exercised with a bounded two-code
smoke (`AIMC_PHYSICAL_SAR_INPUT_CODES=0,7`, `AIMC_COUPLED_TIMEOUT_S=20`). Both
physical switched-capacitor DAC/comparator trials timed out before producing a
measurement (`0/2` comparisons measured), so the SAR sequence is explicitly
`physical_dac_sar_timeout_smoke`, not a passing converter result. The immediate
physical work is therefore convergence/phase diagnosis in the DAC/comparator
fixture, followed by a measured representative code set and only then a full
16-code campaign. No DAC/SAR evidence may be inferred from the wrapper/preamp
pass.

That convergence diagnosis is now resolved at the fixture-schedule level. With
the proven long-acquisition schedule enabled, the same two-code smoke produced
8/8 measured physical comparator trials and 2/2 correct SAR conversions; the
runner now defaults to that schedule while retaining an explicit short-schedule
override for diagnostics. The subsequent complete 16-code campaign measured all
64 comparator trials with zero timeouts, but only 11/16 conversions were correct;
codes 10 through 14 failed. The failure is consistent with the measured DAC
transfer departing from the ideal linear threshold contract (and exceeding the
nominal supply range at the high end), not with missing measurements. The
physical converter therefore remains unqualified; the next repair is DAC
range/transfer calibration or topology correction, followed by a repeat of the
full 16-code campaign and then PVT/mismatch/noise repetition.

The measured 0.9 V-source transfer is preserved in
`analog-digital-chip-design-eda/evidence/aimc-simulator-adapters/sky130-physical-dac-transfer-table.json`.
It is complete and monotonic across codes 0–15, with code 8 the first code above
the 1.8 V supply and code 15 reaching `2.408658 V`. This table is now the
calibration/repair contract for the next DAC revision; it must not be treated as
an analog authorization receipt.

Two bounded DAC repair screens were rejected without weakening that boundary.
Changing the selected charge rail to `1.0 V` made the transfer nonmonotonic;
using `1.4 V` left a code-7-to-8 inversion and a `2.274761 V` maximum, while a
combined `1.2 V` rail and `1.2x` MSB scale still produced code inversions and a
`2.097055 V` maximum. All of these trials measured successfully, so the result
is a topology/charge-redistribution problem rather than a convergence gap.
The next repair must change the bottom-plate switching or array partitioning
itself; rail-only and naive MSB-ratio tuning are now negative controls.

The top-dummy array screen produced a useful but bounded result. A `16 pF`
top-plate dummy at the nominal 1.8 V switching rail gave a complete monotonic
in-range transfer (`0.900002–1.753144 V`) across all 16 codes, preserved in
`sky130-physical-dac-transfer-table-topdummy16.json`. However, the code-7 to
code-8 increment compressed to approximately `6.5 mV`, and the corresponding
full 16-code SAR run with a bounded `0.8 V` input span timed out before any
conversion measured. This is transfer characterization, not converter
qualification. The next design must preserve both in-range swing and binary
MSB separation—likely through a physically partitioned/segmented array or a
different bottom-plate switch sequence—before another SAR campaign.

Binding SAR thresholds to measured transfer midpoints was also tested against
the `16 pF` table. The calibrated run attempted the full 16-code sequence but
only 5 of 21 comparisons measured; the remaining MSB trials timed out and all
16 conversions failed. Thus calibration arithmetic is not sufficient to repair
the candidate. The next physical implementation must restore MSB observability
and convergence structurally, with calibration applied only after that transfer
is stable.

The segmented-array repair now provides a stronger transfer candidate. A fresh
nominal sweep using four thermometric coarse units plus two fine binary units,
with the `16 pF` top dummy, measured all 16 codes with zero timeouts and
correct comparator polarity for every code. The extracted transfer is monotonic
and in range (`0.900011–1.670243 V`), with approximately `51.35 mV` code steps
and `1.589 mV` maximum endpoint-linearity error. The source receipt is
`sky130-coupled-dac-comparator-bit-source09-segmented-topdummy16-final.json` and
the derived table is
`sky130-physical-dac-transfer-table-segmented-topdummy16.json`. This closes
nominal segmented transfer characterization only; the calibrated full SAR
campaign is still required to prove conversion accuracy, convergence, state
retention, and the remaining physical gates.

## Current closure checkpoint

The strongest local state is now packaged and reproducibly validated. The
digital/model-to-chip reference path passes its local acceptance and the
end-to-end handoff validator. The segmented DAC transfer is a complete nominal
16-code characterization, but the calibrated multi-cycle SAR campaign was
stopped after prolonged execution without emitting a terminal receipt. It is
therefore an operationally unqualified attempt, not qualification evidence.
The release manifest therefore remains
`blocked_pending_declared_gates`, with `gpu_ready=false` and
`analog_authorized=false`.

The remaining work is deliberately closed into these gates:

1. Obtain a terminal calibrated SAR receipt with all declared input codes
   measured and correctly converted; classify timeout or convergence failure if
   the campaign cannot complete.
2. Repeat the accepted converter and frontend at declared PVT, mismatch, noise,
   timing, energy, and multicycle conditions.
3. Restore fresh external GPU/board evidence and reconcile its hashes with the
   release manifest.
4. Join measured converter behavior to the held-out workload and publish the
   bounded conclusion `analog advantage`, `no advantage`, or `unresolved`.
5. Preserve digital reference plus deterministic fallback as the authoritative
   route for unsupported or failed regions.
6. Rebuild and validate the final hash-bound evidence bundle, then change
   `analog_authorized` only if every physical and external gate passes.

Until gates 1–3 have terminal evidence, gates 4 and 6 cannot be promoted. The
current honest release conclusion is **digital reference and deterministic
fallback only**.

## Definition of done

The handoff is complete only when a clean checkout reproduces the frozen
workload and produces linked, hash-verifiable model, GPU, digital fallback,
circuit, hybrid-profile, compiler/runtime, and final-decision artifacts. The
package must contain complete legal 16-code converter evidence, PVT and
mismatch/noise receipts, a held-out circuit-derived error/timing/calibration
profile, matched digital/hybrid results, runtime-trace agreement, complete
accuracy/latency/energy/transfer/calibration/fallback accounting, and an honest
ship/no-ship conclusion.

Until then, native digital execution is authoritative and
`analog_authorized` remains `false`.
