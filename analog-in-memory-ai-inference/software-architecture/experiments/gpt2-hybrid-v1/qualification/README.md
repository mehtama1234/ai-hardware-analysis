# GPT-2 converter qualification matrix

## Local profile-to-workload qualification

The external GPU and physical-converter gates are not required to exercise the
local product boundary. The reproducible local package joins the frozen GPT-2
evaluation, guarded SAR profile, workload accounting, and compiler fallback
trace. It runs an explicit error-sensitivity screen and a parameterized
counterfactual cost model while keeping analog authorization disabled:

```bash
cd ../../..
python3 scripts/run_local_profile_to_workload_qualification.py \
  --evaluation experiments/gpt2-hybrid-v1/runs/20260911-local-profile-replay-tensors-v3/evaluation.json \
  --tensor-artifact experiments/gpt2-hybrid-v1/runs/20260911-local-profile-replay-tensors-v3/projection_tensors.npz \
  --calibration-report experiments/gpt2-hybrid-v1/runs/20260911-local-affine-calibrated-adc12/calibration_report.json \
  --calibrated-tensor-artifact experiments/gpt2-hybrid-v1/runs/20260911-local-affine-calibrated-adc12/projection_tensors.npz \
  --calibration-generalization experiments/gpt2-hybrid-v1/qualification/calibration-generalization-comparison.json \
  --output experiments/gpt2-hybrid-v1/qualification/local-profile-to-workload-qualification
```

Validate the generated package with:

```bash
cd ../../..
python3 scripts/check_local_profile_to_workload_qualification.py \
  experiments/gpt2-hybrid-v1/qualification/local-profile-to-workload-qualification
```

The package is local numerical evidence, not measured analog execution, GPU
performance, silicon yield, or energy advantage. Its expected decision is
`digital_reference_and_deterministic_fallback_only` until the physical and
matched-cost gates are closed.

The package also emits `execution_trace.jsonl` for all 162 workload vectors
and `failure_injection_replay.json`, which expands five guarded failure modes
across the four held-out contexts. These are policy replays over the exact
digital control; they are not physical fault-injection measurements.

For a fresh local model run, use the fingerprinted evaluation and tensor file:

```bash
cd ../../..
python3 scripts/run_local_profile_to_workload_qualification.py \
  --evaluation experiments/gpt2-hybrid-v1/runs/20260911-local-profile-replay-tensors-v3/evaluation.json \
  --tensor-artifact experiments/gpt2-hybrid-v1/runs/20260911-local-profile-replay-tensors-v3/projection_tensors.npz \
  --output experiments/gpt2-hybrid-v1/qualification/local-profile-to-workload-qualification
```

That package contributes 162 ideal-versus-ADC12 projection tensors, hashes,
and per-vector max-error/RMSE/relative-L2 measurements. These are genuine
local model outputs, but remain software replay evidence rather than circuit
measurements.

The package also emits `workload_runtime_trace.json`: one scheduled event per
vector with operation counts, governor reasons, and enforced route. Its trace
must agree with the per-vector execution trace and threshold governor;
currently it records 162 digital-fallback events and zero analog events.

Build the bounded final decision after generating the package:

```bash
cd ../../..
python3 scripts/build_local_qualification_decision.py \
  experiments/gpt2-hybrid-v1/qualification/local-profile-to-workload-qualification
```

The decision audit reports each gate independently and keeps the conclusion
`unresolved` whenever quality, timing, cost, converter, or authorization gates
remain open.

The local calibration runner fits a per-output-channel residual only on the
three disjoint calibration texts and evaluates the corrected projection on
the four held-out texts:

```bash
cd ../../..
python3 scripts/run_gpt2_calibrated_projection_replay.py \
  --snapshot-path /path/to/cached/gpt2/snapshot \
  --output experiments/gpt2-hybrid-v1/runs/20260911-local-calibrated-adc12
```

The current affine-calibration receipt reduces held-out NLL increase from
`0.004654` to `0.002800` while retaining 4/4 exact generations. It is a
software calibration result, not circuit calibration or analog authorization.

The corrected calibration receipt also retains `(162, 3072)` uncalibrated and
calibrated held-out projection arrays. The calibrated tensor envelope reaches
`79/162` vectors under 2% relative-L2 (up from `74/162`); none are under 1%.

The reusable policy is `../../../scripts/threshold_governor.py`; its gate
behavior is checked with:

```bash
cd ../../..
python3 scripts/check_threshold_governor.py
```

Analog routing requires every gate to pass. The current package deliberately
exercises the all-fallback branch because authorization, timing evidence, and
converter profile support are not closed.

`threshold_sweep` in the report records the quality-only envelope at 0.5%,
1%, 1.5%, 2%, 2.5%, and 3% relative-L2 limits. It must not be read as a
hardware yield estimate: actual analog eligibility remains zero until the
non-quality gates close.

The report also contains a parameterized workload cost model. It separates
operation-count cost from measured energy, includes calibration overhead
amortized over 1, 10, 100, 1,000, and 10,000 workload reuses, and reports an
illustrative timing model without calling it measured latency. By default,
the one-time calibration overhead is set to one equivalent hybrid workload
cost; pass `--calibration-overhead-pj` to analyze another assumption. Every
currently open profile receipt is separately stress-tested through the
fail-closed route, so open-case stress coverage cannot accidentally authorize
analog execution.

The same report includes a 12-point analog-MAC/converter-cost sensitivity
matrix and equal-cost break-even coefficients. These answer “what would have
to be true for the counterfactual hybrid path to win?” under explicit assumed
coefficients. They do not turn modeled pJ or cycles into measured energy,
latency, or a hardware advantage, and they never alter the guarded runtime
route.

`workload_cost_trace.jsonl` is the per-vector companion to those aggregates:
its 162 rows are joined to the execution trace and governor by `vector_id`.
Each row records digital-reference cost, counterfactual hybrid cost, modeled
cycles, calibration amortization context, and the enforced route. This makes
cost/fallback accounting auditable at workload granularity rather than only
as a final total.

`claim_ledger.json` is the claim-by-claim review surface. It labels each result
as locally proven, bounded, modeled-only, blocked, or not authorized, so a
green software check cannot be mistaken for physical qualification.

This qualification matrix is one evidence source in the product-level
[model-to-chip handoff](../../../../../END_TO_END_QUALIFICATION_HANDOFF.md),
which joins it to the frozen model contract, GPU baseline, circuit receipts,
runtime trace, and final bounded decision.

## Multi-module extension

The next local slice is recorded under
`runs/20260911-local-multimodule-v2/`. It replays the same frozen GPT-2 text
split through `mlp.c_fc`, `mlp.c_proj`, and `attn.c_attn` simultaneously, with
per-module shapes, activation bounds, traces, tensors, and disjoint affine
calibration. The ideal control passes. Calibration improves each module's
calibration residual, but the joint calibrated ADC12 replay reaches only
`0.952381` teacher-forced argmax agreement and `3/4` exact generations,
below the provisional `0.99` screen. The earlier uncalibrated result was
`0.936508` and `4/4`; both are retained in the receipt. This is a bounded
negative result, not evidence that the single-module profile generalizes.

Validate that receipt and build/check its decision package with:

```bash
cd ../../..
python3 scripts/check_gpt2_multimodule_replay.py \
  experiments/gpt2-hybrid-v1/runs/20260911-local-multimodule-v2
python3 scripts/build_multimodule_decision.py \
  experiments/gpt2-hybrid-v1/runs/20260911-local-multimodule-v2/multimodule_evaluation.json \
  --output experiments/gpt2-hybrid-v1/qualification/local-multimodule-qualification-v2
python3 scripts/build_multimodule_runtime_accounting.py \
  experiments/gpt2-hybrid-v1/runs/20260911-local-multimodule-v2/multimodule_evaluation.json \
  experiments/gpt2-hybrid-v1/qualification/local-multimodule-qualification-v2
python3 scripts/check_multimodule_decision.py \
  experiments/gpt2-hybrid-v1/qualification/local-multimodule-qualification-v2
```

The local extension now also emits `multimodule_runtime_trace.json` and
`multimodule_cost_trace.jsonl`: all 162 vectors agree on digital fallback and
the three-module digital/counterfactual-hybrid operation-count ledger is
complete. The decision package therefore passes 6/8 local gates. The quality
gate remains closed, the modeled coefficients are not measured energy or
latency, and the multi-module route remains digital fallback only.

The follow-up sensitivity receipt at
`runs/20260911-local-multimodule-sensitivity-v2/sensitivity_report.json`
tests ADC8 through ADC16, isolated and partial module routes, and activation
bound stress. Only isolated `c_fc` and `c_attn` pass the provisional screen;
the complete three-module route still fails at ADC16, while isolated `c_proj`
is the weakest module. The next software investigation is therefore module
interaction and error accumulation.

This is the first execution receipt for the hardware qualification goal. It
uses the same extracted converter candidate identity as the physical repair
evidence and exercises four input differentials:

```text
-100 mV, -0.1529705854 mV, +0.1529705854 mV, +100 mV
```

The current extracted transient run measured all four cases. Three cases pass
the polarity check and zero cases pass the declared 0.9 V logic-margin gate.
The result is useful characterization evidence; it is not converter signoff.

Run the matrix again from the EDA repository with:

```bash
python3 scripts/run_active_converter_macro_extracted_transient.py \
  --candidate-dir evidence/aimc-simulator-adapters/recovery-20260909/contact-rebuild-v3 \
  --input-diffs-mv -100 -0.1529705854 0.1529705854 100 \
  --timeout-seconds 120
```

The runner's output JSON is copied by the physical-gate importer into this
experiment's handoff directory. The next matrix revision must add reset and
repeated-history sequences, supply/common-mode sweeps, PVT or an explicit
model-availability record, noise/mismatch, settling, and full converter code
transfer before the analog path can be authorized.

The first seven-profile repeated-history screen is now recorded in
`matrix.json`: all seven profiles completed and passed the local hold/reset
diagnostic, but none produced a legal waveform under the screen contract. This
is useful characterization evidence and keeps repeated-history and PVT marked
`screened_not_qualified`.

The latch-only rerun separated the receiver from the issue. Hold and reset
checks pass on every cycle, while the observable output briefly undershoots to
`-0.07156 V`; that rail excursion is the current failure mechanism. The
legality check now covers only `out_p` and `out_n` (and receiver outputs when a
receiver is present), while all internal extrema remain in the result for
diagnosis. The repair status is now `repair_screen_passed_combined_screen_passed`.

Every result keeps separate fields for polarity, logic margin, timeout,
energy scope, and claim boundary. A passing polarity row never promotes the
whole converter or the GPT-2 workload to an analog hardware claim.

A reset-timing repair screen then applied `0.5 ns` reset advance and a `1000
ps` clock fall to the latch-only path. All seven process/temperature profiles
completed with legal observable waveforms and passing four-cycle rows. The
screen is recorded as `screen_passed_not_qualified`: it still requires the
combined converter, receiver loading, noise/mismatch, settling and full code
transfer gates.

The repaired timing condition also passes the combined extracted latch/receiver
path for four alternating cycles. The receiver’s extrema are `-2.52 mV` and
`1.80180 V`, inside the explicit `5 mV` waveform tolerance, and all polarity,
hold, reset and receiver checks pass. This is recorded as
`combined_screen_passed_not_qualified`; it does not close the full converter
or analog inference gates.

The matrix now also links the converter-side screens. The 10-bit row-DAC
settling fixture passes three low/mid/high codes within half an LSB (worst
error `176.7 uV` after `4 ns`), and the simple 12-bit SAR readout fixture
passes three readout levels across twelve comparisons. Differential sampling
passes the two common-only cases but intentionally fails the injected-mismatch
case at `300 uV`, which is above the 12-bit half-LSB target. These are useful
block-level SPICE and topology results; they remain open for the extracted
transistor converter, mismatch/noise, PVT, and continuous multi-cycle transfer
proof needed for an analog claim.
Shared-converter loading also passes four simple mux-load cases, including up
to 32 active loads, and the supply-energy fixture reports positive DAC, mux,
and ADC energy for three cases (worst total `4.273 pJ`). Those numbers are
early budgeting evidence only: they exclude input/clock drivers, biasing,
memory movement, accumulation, and the extracted macro path.

The first bounded physical DAC/comparator SAR smoke run was attempted with one
input code and a `5 s` per-transient limit. The first transistor-level
comparison timed out before producing a measurement. The matrix records this
as a runtime/convergence gate, so the simple-load passes are not promoted to a
physical converter claim. The next engineering action is to make that
transient converge or reduce the deck to a validated one-bit extracted slice
before repeating the full SAR sequence.

There is already a stronger nominal one-bit artifact: the physical Sky130
DAC/comparator sweep measured all 16 four-bit trial codes with correct
polarity. The matrix links it as a one-bit transfer pass. It gives us a
validated starting point for the SAR integration, while the failed smoke run
shows that the retained-bit sequence still needs a convergence-friendly deck.

The repository also contains a continuous physical SAR candidate that completes
five decision-dependent conversions in one transient, with all five nominal
results correct. A seeded 1% capacitor-variation stress set measured 97 of 100
trials; 95 passed the complete map and all 97 measured trials passed the legal
bottom-plate checks. This advances the converter gate substantially, but it is
still a candidate result: foundry Monte Carlo, comparator noise/offset, PVT,
and extracted-layout acceptance remain open.

Representative calibrated PVT evidence now covers 25 measured cases across
five process/supply/temperature corners with 25/25 correct polarity and no
timeouts. A separate 20-case comparator-disturbance stress envelope passes 17
cases, with the boundary between passing and failing uncertainty near
`0.153–0.158 mV`. These results tighten the operating envelope but do not
replace transistor-level noise/offset yield evidence.

The current bounded latch-free transistor offset smoke artifact attempts one
`+0.1 mV` differential and times out before measurement. The runner now
supports separate output stems, input subsets, timeout, relative tolerance,
and gmin controls so convergence experiments do not overwrite prior evidence.
Earlier measured offset rows remain useful historical characterization, but the
current canonical artifact is treated as unavailable until rerun end to end.

Five convergence configurations (Gear/Trap, higher gmin, relaxed tolerance,
UIC, and a coarser timestep) were tested on isolated cases. All still timed
out for the positive or zero sign, so this is now recorded as a numerical deck
diagnostic rather than repeatedly presented as missing measurement data.

The offset/noise proxy was rerun against the current source fixture and found
zero successful source rows because that fixture is timing out. The script now
records this explicitly instead of crashing or inventing a margin. A named
converter noise candidate still reports `851.121 uV` RMS within its behavioral
budget, but it is not extracted device-noise evidence.

A minimal DC-biased preamp sanity deck was also tested with the latch removed,
fixed sample controls, and explicit node leakage. All three signed inputs still
timed out, confirming the convergence issue is present before regeneration and
is structural to this model/deck combination.

To isolate the environment, a one-NMOS Sky130 operating-point probe was run
with no capacitors, clocks, or transient analysis. It also timed out at `30 s`.
This is now recorded as a model/runtime availability gate; until it completes,
new transient results cannot be interpreted as circuit behavior.

The latest host preflight captured a 1-minute load ratio of `15.69`. Even though
the narrow simulator-process counter was zero, other long-running workloads
are saturating the machine, so the minimal model probe is not a clean PDK
verdict yet; the next probe must run on an available host window.

An explicitly biased reference differential pair was then tested without any
floating storage nodes or latch devices. Its single zero-differential case
also timed out after `60 s`, so the issue is broader than the candidate latch
topology. This points to the local Sky130 transient/model execution path as
the next infrastructure issue to isolate before further circuit claims.

The ngspice executable itself passes a resistor-only operating-point control in
under two seconds while the host is contended. This isolates the delay to the
Sky130 model/PDK path (or its interaction with host load), rather than the
ngspice binary or process launch.

The Colab CLI currently exposes two authenticated T4 sessions. The hardware
probe should be moved to one of those sessions only after installing or
uploading the pinned Sky130 model bundle and ngspice deck; a GPU session by
itself does not provide the PDK. The existing GPU handoff runbook remains the
reference for session setup.

The corrected model-load probe now includes the Sky130 library plus a simple
resistor operating point, so it exercises the library includes without any
Sky130 device. It still times out at `30 s`; the prior no-analysis return code
was replaced by this valid timeout result.

The dedicated Colab session `sky130-runtime-probe` then installed ngspice,
verified the bundle hash, unpacked the `libs.ref` dependencies, and passed a
nominal `sky130_fd_pr__nfet_01v8` operating point in `11.264 s`. This closes the
PDK runtime gate remotely; the local timeout remains an environment result and
is not used to reject the Colab circuit path.

The first coupled physical circuit run in Colab measured two representative
DAC/comparator trial codes with `2/2` correct polarity and no timeouts. A
fresh T4 session then ran the complete four-bit code sweep sequentially:
`16/16` codes measured, `16/16` correct polarity, and zero timeouts. This
reopens the physical converter path on a clean runtime and closes the complete
one-bit code-sweep gate. It is still not a full retained-bit SAR, PVT,
mismatch/noise, extracted-layout, or GPT-2 tile acceptance result.

The subsequent fresh T4 Colab run completed five representative retained-bit
SAR conversions: `20/20` physical comparator decisions measured, `5/5`
conversions correct, and zero timeouts. Each decision is a fresh physical
transient reset, so continuous clock-to-clock state retention and the PVT,
mismatch/noise, extracted-layout, and GPT-2 tile gates remain open.

The first remote continuous-deck diagnostic converged but returned code `0`
for the code-`2` reference. The five-conversion continuous run exposed a
ngspice timestep collapse at a behavioral gate branch. The gate driver now
supports a smooth transition through `AIMC_CONTINUOUS_GATE_SLOPE` for
convergence work; it has not yet produced an accepted continuous SAR result.
The deck now also supports explicit finite-rise/fall PWL timing through
`AIMC_CONTINUOUS_PWL_RISE_NS`, the preferred next control topology because it
reaches full rail values without ideal behavioral time steps.

The first complete remote continuous-SAR pass uses 50 ps PWL control edges and
100 ps decision-clock edges. It measures and decodes the representative map
`0, 2, 4, 6, 7` exactly (`5/5` conversions, zero timeouts) in one continuous
Sky130 transient. This closes nominal continuous-SAR behavior; robustness and
model-to-tile integration remain open.

The first continuous robustness corner also passes: at SS, −20 °C, and 1.62 V,
the widened 200 ps PWL and clock controls produce `5/5` correct conversions
with zero timeouts. The remaining TT/FF/SF/FS corners and mismatch/noise
campaign are still open.

The remaining corner sweep measured all three additional continuous runs. SF
passes `5/5` with the nominal map; FF at 85 °C/1.98 V decodes
`2,6,7,7,8`, and FS decodes `0,4,5,6,7`. Those are measured corner maps, not
timeouts, and show that FF/FS need corner-specific calibration before a full
PVT claim.

A fresh five-trial fixed-seed mismatch campaign using the current `1.8x` LSB
calibration completed all five transients and kept every bottom plate legal,
but every trial failed the retained-code map in the same pattern
`[1,4,6,7,8]`. This confirms the population harness and exposes a repeatable
functional sensitivity of the current candidate; it is still a seeded
capacitor stress model, not foundry mismatch yield.

The FS bit-1 trajectory comparison bounds the next calibration target:
changing bit-1 from `0.75x` to `0.5x` first changes decisions in conversions 3
and 4, with up to `151.7 mV` DAC and `324.9 mV` preamp trajectory shifts. The
next FS experiment should tune the later bit paths or isolate their charge
transfer rather than adjust the code-2 reference.

`sar-calibration-ranking.json` now ranks 438 checked-in continuous-SAR receipts
(296 complete map passes) by their exact control settings. These are historical
schematic results; the ranking is a selection aid, not a PVT or mismatch yield
claim.

The corrected authenticated T4 handoff is archived under
`runs/gpt2-sar-t4-20260910-r7/`. It ran the pinned revision on `device: cuda`
with synchronized timing. The ADC12 profile reached 100% teacher-forced argmax
agreement and 4/4 exact generations (`0.0047839` NLL increase); the evaluator
and CUDA-required receipt checkers both pass. The 8-bit ADC profile remains a
quality failure, and this is still numerical profile evidence rather than an
analog hardware claim.

The final T4 replay is archived under `runs/gpt2-sar-t4-20260910-r8/`. Its
receipt, evaluator, and CUDA-required checks pass, and the held-out workload
gate passes with three calibration contexts and four disjoint GPT‑2 contexts.
The result remains a numerical profile qualification; physical analog cost and
yield are still open.

`cpu-cuda-comparison.json` compares the synchronized CPU control with T4 r7 on
the same fixture. The ADC12 profile has median reference time `1,791.4 ms` on
CPU versus `408.4 ms` on T4 (about `4.39×`), while deterministic quality fields
match. The noisy profile is stochastic and is intentionally excluded from
bitwise parity checks. These are device-execution numbers, not analog speedup
or energy evidence.

`projection-cost-model.json` now turns the workload counts into an explicit
energy accounting interface. It currently reports six missing matched
coefficients (DAC, ADC, array, digital accumulation, boundary movement, and
same-target digital baseline), so energy claims remain disabled. Supplying a
coefficient file will compute a scoped projection total and break-even result.

`energy-measurement-contract.json` defines the six matched coefficients needed
to populate that model. It records the required corner, voltage, timing,
precision, movement, and measurement controls and labels the current simple
load and T4 timing artifacts as ineligible proxies.

`physical-qualification-gate.json` is the single guarded decision for the next
phase. It joins the GPT-2 workload trace to nominal/PVT/mismatch converter
receipts and the simple-load energy artifact. It currently keeps native digital
GPU execution authoritative because FS/FF acceptance, independent mismatch
yield, and matched converter/array/controller energy are still open. Measured
but rejected circuits remain rejected by this gate.

The gate checker is fail-closed:

```bash
python3 scripts/check_physical_qualification_gate.py \
  experiments/gpt2-hybrid-v1/qualification/physical-qualification-gate.json
```

It verifies the artifact digest, recomputes open checks, and refuses analog
authorization while any physical requirement remains unresolved.
After downloading a Colab campaign bundle, rebuild the gate with
`--campaign-summary /path/to/campaign-summary.json`; FS and FF results embedded
in that summary then replace the older corner receipts for this decision.

The first fresh campaign (`colab-sky130-corner-campaign-20260910`) completed
the remote preflight and attempted both corners. FF reached a measured
ngspice transient but aborted on a timestep collapse at
`bcont_sample_reset#branch`; FS produced no child receipt. These are preserved
under the EDA evidence directory and the gate consumes the FF failure while
leaving FS unresolved. The next circuit change should address this convergence
path before another map or energy claim is attempted.

A controlled diagnostic then disabled the optional sample reset and added
`1 kOhm` series resistance to every continuous gate. Both FS and FF completed
all five physical conversions, proving the stiff behavioral gate source was a
convergence contributor. They still produced the same rejected code map
`[3,6,7,7,8]` rather than `[0,2,4,6,7]`. This screen is preserved as
`colab-sky130-corner-diagnostic-gateseries1000-20260910-*`; it motivates a
charge-transfer redesign, not an analog qualification claim.

A second controlled screen at `100 Ohm` gate series resistance also completed
the FF five-conversion transient but returned the identical rejected map
`[3,6,7,7,8]`; FS again produced no child receipt. Gate-source resistance is
therefore not the functional correction. The next screen should vary the
reference profile or isolate individual bit charge transfer while keeping the
same acceptance map.

The first handoff probe measured the legacy `sp/sn` nodes while switched
handoff was enabled, so its `0.2 uV` movement could not diagnose the active
path. A fresh FF probe now measures `handoff_p/handoff_n` directly. The active
handoff moved by `0.1902 V` across the 42–56 ns window while the preamp moved by
`1.3604 V`; the trajectory is therefore live but not a frozen sample. The
corresponding conversion map remained rejected (`[3,6,7,7,8]`), so this is a
timing/charge-transfer diagnosis and not analog qualification evidence.

A local replay with the historical calibrated operating point (`PMOS bank=8`,
`NMOS width=64 um`, `LSB scale=1.8`, `sample_reset=1`, 50 ps PWL edges) restores
the complete nominal map `[0,2,4,6,7]`. Its direct active-handoff probe spans
`−0.4694 V` to `−0.1881 V`. This is a reproducible nominal candidate and a
useful starting point for the next FS/FF calibration screen; it is not yet a
robustness or workload authorization.

That fresh calibrated FS/FF Colab screen is recorded as
`colab-sky130-calibrated-pvt-20260910-summary.json`. FF still decodes
`[3,6,7,7,8]`, while FS emitted no child receipt. The calibrated point
therefore reproduces nominal behavior but does not transfer across process
corners. The next circuit experiment is a corner-aware charge-transfer and
reference calibration sweep, followed by fixed-seed mismatch only after both
corners produce the exact map.

Using the two complete local FS/FF receipts, the profile builder now emits
`local-fs-ff-cal055-profile-20260910.json`. It contains two supported schematic
cases and no extrapolated error model, but remains explicitly uncalibrated
until the same cases complete on the pinned Colab runtime.

The same profile now drives a claim-safe GPT-2 workload trace with 162 vectors,
2,985,984 DAC conversions, 2,985,984 ADC conversions, and 46,656 array
evaluations. Its execution policy correctly routes all vectors to digital
fallback while analog authorization is false; this is the workload baseline
for the eventual hardware comparison.

The local sweep has now found a shared profile: changing only the second
reference to `0.55 V` gives the exact map at both FS and FF. These receipts are
`local-fs-ref055-20260910.json` and `local-ff-ref055-20260910.json`. The same
profile still encounters a remote ngspice timestep collapse in Colab, so the
next implementation task is to make the reset and gate waveform numerically
stable on the pinned remote runtime before treating the local corner result as
portable.

The runner now has an optional closed-loop decision-filter mode
(`AIMC_CONTINUOUS_DECISION_FILTER=1`): each comparator output drives a small RC
state node, and the gate controls read that state instead of an instantaneous
decision voltage. This preserves feedback semantics while targeting the
NGATE transition singularity. It is a diagnostic candidate until a complete
remote FS/FF receipt confirms its code map.

The control-source repair is now implemented: reset uses an explicit PWL
voltage source, and the switched-handoff and DAC gate enables use VALUE
controlled E sources. A smooth time-edge mode (`AIMC_CONTINUOUS_TIME_SLOPE=10`)
also preserves the local FF map, but the pinned Colab runtime still collapses
at the NGATE branch. The remote numerical issue remains an explicit open gate,
not a functional pass.

The E-source/PWL controls are opt-in through
`AIMC_CONTINUOUS_CONTROL_SOURCE=e`; the default runner retains the verified
B-source/ideal-reset contract so existing nominal receipts remain reproducible.

The next control redesign is available as
`AIMC_CONTINUOUS_SEQUENTIAL_CONTROL=1`. It samples each held comparator
decision through a voltage-controlled switch, stores it on a hold capacitor,
and drives the corresponding DAC gates through complementary voltage-controlled
switches. This removes
the long decision-dependent NGATE expression from the diagnostic deck. The
first one-conversion local attempt timed out before a measured result
(`sky130-sequential-control-diagnostic.json`), so the redesign remains open
until the same deck produces a complete nominal and FS/FF Colab receipt.

The first complete remote FS/FF campaign produced measured five-conversion
receipts, but both corners decoded `[15, 15, 15, 15, 15]`. Direct probes then
showed the held state falling from about `0.30 V` to below `0.15 V` during one
conversion. That rejects the state-hold implementation and motivates the
stronger keeper plus fixed-decision open-loop check before another closed-loop
attempt.

The fixed-decision open-loop replay then isolated the DAC waveform: FF
completed five conversions but decoded `[0, 13, 11, 9, 8]` and violated
bottom-plate rail legality; the FS child failed before publishing a receipt.
This rejects the current PWL waveform as a physical baseline. The next repair
must make both open-loop corners complete and legal before closed-loop feedback
is attempted again.

Campaign receipts are evaluated mechanically with
`python3 scripts/check_sequential_campaign_receipt.py <campaign-summary.json>
<receipt-evaluation.json>`. The evaluator requires complete FS and FF reports,
the exact five-code map, and legal bottom plates before returning `accepted`.

After canonicalizing duplicate PWL timestamps, the v4 replay cleared the
ngspice waveform syntax error but reproduced the same FF code map and rail
violations. The failure is therefore in analog bottom-plate drive/reset timing,
not PWL parsing.

The reproducible campaign settings are checked in at
`analog-digital-chip-design-eda/colab/sky130-sequential-control-campaign-settings.json`.
On Colab, copy that file to `/content/sky130-campaign-settings.json` before
running `run_corner_campaign.py`; the wrapper will apply the sequential flag to
both FS and FF cases and persist each receipt as it completes.

The historical `1.8x` LSB calibration was replayed with sample reset enabled
and a `1 ns` PWL edge. Both corners measured but worsened to FS
`[3,7,9,13,14]` and FF `[3,8,10,13,14]`. This rejects slow-edge timing as the
correction and keeps the current candidate out of analog execution.

The static campaign preflight is recorded in
`corner-campaign-preflight.json`. It confirms the FS/FF corner selectors and
finite PWL controls are wired correctly before a remote ngspice run; it carries
no circuit correctness or energy claim.

`qualification-dashboard.html` is the visual review surface for this matrix.
Check it against the machine-readable gate with:

```bash
python3 scripts/check_qualification_dashboard.py \
  qualification-dashboard.html \
  experiments/gpt2-hybrid-v1/qualification/physical-qualification-gate.json
```

`t4-dispatch-decision.json` is the current end-to-end decision package. It
joins the T4 ADC12 quality result, the `408.39 ms` median T4 reference time,
and the fail-closed converter routes. Zero vectors are authorized for analog
execution; native digital GPU execution remains authoritative until physical
converter and energy measurements close.

The FF-derived remap was then frozen and tested against three holdouts in
`sar-code-remap-holdout-ff.json`. It passed `0/3`: FS contains a collision,
mismatch produces codes outside the FF domain, and split-MSB changes the code
scale. Calibration therefore does not generalize across this envelope; the
next circuit experiment must use per-corner/per-converter calibration or repair
the conversion path before workload promotion.

The complementary per-converter test fits a remap on mismatch trial 000 and
validates it on trials 001–004. It passes `4/4` because all five trials share
the same observed code pattern (`[1,4,6,7,8]`). This is enough to model a
bounded digital label correction for that campaign; it does not repair the
underlying analog settling error or establish yield, so analog placement stays
blocked.

`converter-dispatch-policy.json` turns the evidence into runtime behavior. It
routes nominal/SS/SF/FF and unknown cases to digital fallback, rejects FS on its
code collision, and exposes the mismatch remap only as a bounded digital
correction candidate. Unknown codes and collisions fail closed.

`converter-dispatch-simulation.json` applies those routes to all 162 workload
vectors. FF, FS, and unknown scenarios require fallback; the bounded mismatch
scenario exposes all 162 vectors to digital code correction, with zero vectors
authorized for analog execution. This is the software control behavior the
Colab workload replay will exercise.

The Colab receipt also runs `check_converter_dispatch_simulation.py`, which
verifies scenario coverage, vector conservation, zero analog-authorized
vectors, and fail-closed FF/FS/unknown routing before any model execution.

The first full pinned-model run is archived under
`runs/20260910-profile-driven-colab/`. Its `dac10_weight8_adc12` numerical
variant reaches 100% teacher-forced argmax agreement and 4/4 exact generations
with an NLL increase of `0.0046545` nats/token; the conservative 8-bit and noisy
12-bit variants fail the provisional screen. The evaluator checker passes, but
the run is CPU numerical emulation and does not measure analog hardware cost.

After adding explicit device selection, the verified rerun is archived under
`runs/20260910-profile-driven-device-aware/`; its source-hash checker passes.
Use `--device cuda` in Colab to produce the matched T4 version from the same
runner and fixture.

The complete fresh-runtime instructions are in
`software-architecture/colab/README.md`.

The same package now includes `real-model-workload-hardware-contract.json`,
which joins the existing Tesla T4 serving characterization to the GPT‑2
workload boundary. It records 630.24 MB maximum observed peak memory and keeps
the decision focused on decode-first digital runtime optimization before any
analog placement. The T4 evidence is contextual rather than a matched
analog-versus-GPU benchmark.

`profile-driven-workload-trace.json` converts the saved GPT-2 projection run
into a phase-level schedule: 162 vectors, 2,985,984 DAC conversions, 2,985,984
ADC conversions, array evaluations, digital accumulation, and boundary bytes.
It remains explicitly `digital_fallback_only`; the artifact is the input to the
next Colab holdout run, not analog timing or energy evidence.

`profile-driven-transformer-contract.json` now binds the qualification state to
the frozen GPT-2 `transformer.h.0.mlp.c_fc` projection. One vector requires
2,359,296 MACs, 18,432 DAC conversions, 18,432 ADC conversions, 288 array
evaluations, and 15,360 digital partial-sum additions under the current 128×128
tile schedule. Native digital fallback remains authoritative. The next Colab
run fits remaps on calibration references, validates them on new mismatch
references, and evaluates the unchanged GPT-2 contexts with conversion,
fallback, movement, latency, and energy fields recorded.

For a Colab replay, clone the repository into `/content/ai-hardware-analysis`
and run the bundled entry point:

```bash
python3 analog-in-memory-ai-inference/software-architecture/colab/run_profile_driven_gpt2_colab.py \
  --repo-root /content/ai-hardware-analysis \
  --output /content/gpt2-sar-qualification-receipt
```

Add `--execute-model` only when the pinned model snapshot and required local
evidence are present. The default run validates the contract and emits the
operation trace without silently inventing analog timing or energy.

On a networked Colab runtime, add `--fetch-model --execute-model` to download
the exact fixture revision first and then run the evaluator. The receipt records
the model snapshot and any execution failure instead of substituting another
revision.

The evaluator now synchronizes CUDA before and after each measured call, so the
same runner can produce valid device timing on a Colab T4. The synchronized CPU
control is archived under `runs/20260910-profile-driven-synchronized/` and its
source-hash checker passes.

The full orchestration control is archived under
`runs/20260910-profile-driven-integrated/`. It executes the model, contract
checks, dispatch simulation, and remap attachment in one receipt; all software
checks pass on CPU. The same command with `--device cuda` is the required T4
run.

When present, the entry point also attaches the per-converter mismatch result
(`4/4` holdouts) to the receipt. That result is scoped to the fixed mismatch
campaign; it does not override the global PVT and physical qualification gates.

The contract is checked with:

```bash
python3 scripts/check_profile_driven_transformer_contract.py \
  experiments/gpt2-hybrid-v1/qualification/profile-driven-transformer-contract.json
```

The split-MSB isolation replay also completed in Colab but worsened the exact
failing seed to `[0,10,12,12,14]` despite legal bottom plates. That topology is
rejected for the current candidate; per-bit isolation needs a controlled
charge-transfer design rather than simply splitting the largest plate.

The circuit profile is now imported through `circuit-profile-import.json`. The
handoff preserves four supported cases and three open cases, while explicitly
setting `placement_allowed=false`; model experiments cannot silently turn
schematic evidence into an analog hardware claim.

The ranking now groups receipts by inferred process corner. The best available
FS setting is `bit1=0.75x`, `LSB=1.8x`, but it still achieves only `4/5`
representative codes (`[0,4,4,6,7]`); it is a bounded calibration candidate,
not a passing FS envelope.

`sar-code-remap-contract.json` makes the software handoff rule executable:
remapping is allowed only when a converter's observed codes are monotonic,
one-to-one, and cover the held-out target set. The FF reference case satisfies
that contract; FS has a code collision and the seeded mismatch case produces
out-of-set codes (`[1,4,6,7,8]`), so both remain rejected. This is a guarded
digital calibration interface, not a repair of analog error or a hardware-yield
claim.
# Local profile-family replay

The next local-only qualification increment replays the frozen workload against
five explicit counterfactual profile classes:

```bash
python3 scripts/run_local_profile_family_replay.py \
  --package experiments/gpt2-hybrid-v1/qualification/local-profile-to-workload-qualification
python3 scripts/check_local_profile_family_replay.py \
  experiments/gpt2-hybrid-v1/qualification/local-profile-family-replay
```

The output contains 162 vectors for each profile, deterministic fallback
reasons, and hash-bound family/replay manifests. The profiles are software
scenarios only; this artifact does not promote physical, CUDA, board, silicon,
or energy evidence.
