# Qualification slice checkpoint — 2026-09-11

## Purpose

This checkpoint fixes the provenance boundary before the next converter
redesign. It covers the model-to-hybrid software slice and the physical
qualification preflight; it does not promote analog execution.

## Verified software slice

The selected workload is `deep-transformer-mlp-stack.onnx`, represented by
three transformer-style MLP blocks and twelve fixed-weight MatMuls.

```text
python3 scripts/run_hybrid_transformer_vertical_slice.py
python3 scripts/compile_hybrid_transformer_execution_package.py
python3 scripts/validate_hybrid_transformer_vertical_slice.py
```

The current package verifies:

- 16 placed operators: 12 analog candidates and 4 digital-support operators;
- 12 replay candidates and 76 operator-level schedule events;
- plan, replay, schedule, and runtime-trace agreement;
- passing calibrated simulator output comparison (`6.71635e-8` relative L2);
- explicit SRAM, calibration, converter-boundary, and digital-fallback records.

The simulator result is valid only for the named fixture and its stated
CrossSim assumptions. It is not pretrained-model accuracy, measured hardware,
or a converter qualification result.

## Verified physical preflight

```text
python3 colab/validate_top_plate_campaign_settings.py
python3 colab/validate_sequential_control_deck.py
python3 scripts/validate_aimc_physical_evidence.py
```

The top-plate settings are `ready`; the sequential deck passes all 15
structural checks; and the physical evidence audit reports `21/21` implemented
checks. These are configuration and evidence-integrity checks only. The
continuous converter remains `qualification_open` because exact full-range
conversion, robustness, and post-layout evidence are not closed.

## Open gates

1. Rerun the DeepSeek Colab notebook and restore the four canonical CUDA JSON
   artifacts; the retained receipt currently conflicts with CPU-overwritten
   local copies.
2. Acquire or upload the pinned Sky130 model bundle, then run the top-plate
   acquisition experiment with its complete waveform receipt.
3. Repair the charge-transfer/source-common-mode topology; judge it on all
   requested codes, legal internal voltages, monotonic spacing, and exact
   sequential decisions.
4. Run declared PVT and mismatch campaigns, classifying numerical failures,
   functional failures, and legal-range failures separately.
5. Export the passing or bounded circuit-derived error/timing profile into the
   existing transformer workload package and produce the final accuracy,
   latency, energy-scope, and fallback decision.

## New nominal cell evidence

The banked one-bit cell reaches the high rail at the 2.5 ns measurement point,
but the shared two-cell fixture becomes numerically stiff with that bank. The
unbanked cell was therefore run sequentially at the explicitly extended 7.9 ns
acquisition point. All four two-bit ownership codes converged, with selected
rails at `1.799493 V` and unselected rails below `0.14 µV`; the matrix is retained
in `evidence/aimc-simulator-adapters/local-two-cell-unbanked-79ns-four-code-matrix.json`.
This closes only nominal two-cell rail ownership. It does not close the
four-bit transfer, comparator coupling, PVT, mismatch, or workload gates.

The first current four-bit timing probes exposed and then corrected a contract
bug: the transistor deck omitted the declared 1 pF dummy capacitor while its
expected transfer assumed a 16 pF total. With that physical dummy restored,
codes 1, 8, and 15 all fall within the `56.25 mV` half-LSB budget at 7.9 ns;
the worst measured error is `51.921 mV` at code 15. The bounded probe receipt
is `evidence/aimc-simulator-adapters/local-fourbit-79ns-timing-probes.json`.
This is not a complete 16-code or robustness qualification.

The corrected transistor array has since been exercised for all 16 codes at
the same 7.9 ns measurement point. Every code is measured, monotonic, and
within the half-LSB top-plate budget; the worst error is `51.921 mV`. The
campaign uses 20 ps steps for the less stiff codes and 50 ps for the high
region, so the consolidated receipt remains diagnostic rather than acceptance
evidence: `evidence/aimc-simulator-adapters/local-fourbit-79ns-dummy1p-16code-diagnostic-matrix.json`.

A complete single-50-ps rerun also measured all 16 codes and passed the
top-plate half-LSB and monotonicity checks, but failed the physical bottom-plate
legal-range gate: observed values span `-0.217 mV` to `1.800280 V`. Its receipt
is `evidence/aimc-simulator-adapters/local-fourbit-79ns-50ps-dummy1p-full.json`.
The runner now requires both top-plate accuracy and bottom-plate legality before
reporting a boundary pass.

An eight-device PFET-bank screen on the worst high code did not repair the
legality gate: code 14 still reached `-0.226 mV` on an unselected plate. The
bank improves one-bit rail arrival but is not sufficient charge-injection or
edge containment; the next repair must use a sequenced bounded handoff rather
than simply increasing device count.

The four-bit diagnostic handoff confirms that direction: code 14 improves from
`-0.226 mV` to `-5.75 µV` with a 3 ns, 2 Ω rail handoff, but remains outside the
strict rail bound; a 0.1 Ω variant shifts the residual to `+1.55 µV`. These are
ideal-switch control diagnostics, not a physical qualification pass. The next
implementation must realize the same timing with explicit transistor isolation
and characterize its charge injection.

The first explicit transistor break-before-make handoff (NMOS off at 3.0 ns,
250 ps dead time, then PMOS on) materially improves the physical result. Code 14
settles to `2.459432 V` versus `2.475 V` expected (`15.568 mV` error, within the
`56.25 mV` half-LSB budget), but its unselected bottom plate reaches `-0.196 mV`,
so the strict legal-range gate still fails. Code 15 independently passes the
same local boundary at `2.548428 V` versus `2.5875 V` expected (`39.072 mV`) with
all bottom plates legal. These are worst-code diagnostics, not a 16-code,
PVT/mismatch, extracted-layout, or converter acceptance receipt; retained as
`local-fourbit-code14-79ns-50ps-transistor-handoff-v2.json` and
`local-fourbit-code15-79ns-50ps-transistor-handoff-v2.json`.

A 500 ps dead-time follow-up did not converge within the 180 s per-code bound
and produced zero measured codes. It is retained only as a classified numerical
convergence result under
`local-fourbit-code14-79ns-50ps-transistor-handoff-dead500ps.json`. The next
circuit experiment should target the code-14 unselected-plate excursion with an
explicit charge-injection/keeper or switch-topology change, while preserving
the 250 ps handoff as the reproducible baseline.

The subsequent single-resolution 50-ps full campaign with that physical
handoff measured `15/16` codes: code 15 hit the declared 180 s numerical
convergence timeout. The measured high-code region also exceeded the strict
bottom-plate range on both sides: code 14 reached `-0.196 mV`, while codes
10--13 reached up to `1.84216 V`. Top-plate order was monotonic and the
measured top-plate errors remained below half-LSB, but incomplete coverage and
illegal internal nodes make the aggregate receipt a qualification failure:
`local-fourbit-79ns-50ps-transistor-handoff-v2-full.json`. This demonstrates
that the isolated code-14 improvement does not survive the complete campaign;
the next repair must address code-dependent charge injection/common-mode
containment, not only handoff timing.

A PMOS sizing screen reinforces that conclusion. On code 13, a two-device PMOS
bank reduces the top-plate error to `4.095 mV` but produces a `-0.140 mV`
unselected-plate excursion; a four-device bank gives `4.699 mV` error and a
`-0.143 mV` excursion. Increased high-side drive removes the positive rail
overshoot but worsens the opposite-side injection, so device width alone is not
the repair. The isolated receipts are
`local-fourbit-code13-79ns-50ps-transistor-handoff-pmosbank2.json` and
`local-fourbit-code13-79ns-50ps-transistor-handoff-pmosbank4.json`.

The complementary low-side sizing screen is bounded but does not close the
problem either. On code 14, doubling the NMOS bank reduces the unselected
bottom-plate excursion from `-0.196 mV` to `-0.075 mV`; four devices reduce it
further to `-0.029 mV`, with essentially unchanged `15.439 mV` top-plate error.
Both remain outside the strict legal range. The trend supports a real active
low-rail containment requirement, but not a bank-size acceptance shortcut.
Receipts: `local-fourbit-code14-79ns-50ps-transistor-handoff-nmosbank2.json` and
`local-fourbit-code14-79ns-50ps-transistor-handoff-nmosbank4.json`.

An active low-side re-clamp was then tested: unselected NMOS gates release
during the handoff and reassert at `4.5 ns`, after redistribution has begun.
The code-14 run converged, but transfer error worsened to `18.959 mV`, the
unselected plate still reached `-0.137 mV`, and a selected plate reached
`1.800230 V`. This rejects reasserting the same pass device as a sufficient
keeper; the next cell revision needs separate isolation and hold devices whose
charge injection is characterized independently.
Receipt: `local-fourbit-code14-79ns-50ps-transistor-reclamp45.json`.

A physical gate-slew screen gives the same answer. A 50-ps slew inside the
250-ps non-overlap interval changes code-14 error only from `15.568 mV` to
`15.309 mV` and leaves the `-0.192 mV` excursion; a 100-ps slew fails to
converge within 180 s. Gate-edge shaping alone is therefore not sufficient, and
the parameter is retained in the runner only as a bounded diagnostic control.
Receipts: `local-fourbit-code14-79ns-50ps-transistor-handoff-rise50ps.json` and
`local-fourbit-code14-79ns-50ps-transistor-handoff-rise100ps.json`.

An always-connected `100 kOhm` keeper to each code-selected target rail was
also screened on code 14. It produced zero measured codes within the 180 s
bound, so the passive keeper is classified as a convergence failure rather
than a repair. The runner exposes it only as an opt-in diagnostic via
`AIMC_TRANSISTOR_DAC_BOTTOM_KEEPER_OHM`; the receipt is
`local-fourbit-code14-79ns-50ps-transistor-handoff-keeper100k.json`.

The first separate-rail transmission-gate topology was also screened on code
14. It disconnects the capacitor plate at 3.0 ns, charges an intermediate rail
node, and reconnects at 4.5 ns. Although it converged, it settled with
`22.584 mV` top-plate error, selected plates up to `1.810412 V`, and an
unselected plate at `0.765 mV`. The isolation pair's own charge sharing
dominates this first implementation, so it is rejected as-is. The next
topology should isolate the rail-control edge without inserting a full
transmission gate in the stored-charge path. Receipt:
`local-fourbit-code14-79ns-50ps-isolatedhandoff45.json`.

A separate phase-enabled target-rail hold device is a better direction but is
not yet sufficient. With a 1 um hold transistor enabled at `4.5 ns`, code 14
settles with `15.193 mV` error and `-0.179 mV` undershoot; a 4 um hold improves
these to `14.698 mV` and `-0.144 mV`, respectively. Both remain outside the
strict legal range. This is the first candidate that improves transfer and
contains the excursion without inserting a transmission gate in the storage
path, so the next experiment should characterize its enable timing and device
ratio across all 16 codes before adding PVT or workload claims. Receipts:
`local-fourbit-code14-79ns-50ps-activehold45w1.json` and
`local-fourbit-code14-79ns-50ps-activehold45w4.json`.

The 4 um active hold was cross-checked on code 13. It reduced the top-plate
error to `3.983 mV`, but a selected plate still overshot to `1.800465 V` and an
unselected plate undershot to `-0.0368 mV`. Thus the hold device improves the
trajectory but does not establish a legal operating envelope across the
opposite transition polarities. Receipt:
`local-fourbit-code13-79ns-50ps-activehold45w4.json`.

Active-hold phase/size sweeps show the residual is not closed by a stronger
late clamp: code 14 at `3.5 ns`, `4.5 ns`, and `6.5 ns` with a 4 um hold gives
undershoots of `-0.147`, `-0.144`, and `-0.133 mV`; a 16 um hold at `6.5 ns`
improves this to `-0.072 mV`, still illegal. Transfer error remains between
`13.662` and `15.006 mV`. The sweep establishes a bounded improvement trend,
but not a passing operating point; future effort should change the bottom-plate
switch topology or the legal-node contract based on a physical uncertainty
budget, never silently relax the existing gate. Receipts include
`local-fourbit-code14-79ns-50ps-activehold35w4.json`,
`local-fourbit-code14-79ns-50ps-activehold65w4.json`, and
`local-fourbit-code14-79ns-50ps-activehold65w16.json`.

A long-channel variant (16 um hold width, `L=1 um`, enabled at `6.5 ns`) did
not converge within the 180 s bound and produced zero measured codes. The
active-hold device length is therefore retained as an explicit diagnostic
parameter, but this first charge-injection reduction hypothesis cannot be
promoted. Receipt:
`local-fourbit-code14-79ns-50ps-activehold65w16l1.json`.

The complete 4 um active-hold, 250-ps break-before-make, 16-code campaign has
now terminated under the declared 180 s per-code timeout. Only 5/16 codes
measured (codes 6, 9, 10, 11, and 15); the remaining codes are classified as
`numerical_convergence_timeout`. The measured subset has a maximum settling
error of `37.644 mV`, and its bottom-plate values still include code-dependent
rail excursions. The aggregate result is therefore
`transistor_switched_capacitor_dac_incomplete_or_half_lsb_or_legal_range_failed`.
This is complete negative diagnostic evidence, not a converter qualification
receipt: `local-fourbit-79ns-50ps-activehold45w4-full.json`.

The prescribed isolated-cell follow-up was also run independently at a 0.9 V
top-plate common mode with a 20 ps break-before-make interval. It produced no
measurement before the 60 s diagnostic bound and is retained as an explicit
`numerical_convergence_timeout`, not as missing evidence:
`local-onebit-baseline-09v-vdd-20260911.json`.
Repeating the same case with an explicit 50 ps transient step also produced
zero measurements before the 60 s bound, so the timeout is not explained by
the original 5 ps output resolution. The step-controlled receipt is
`local-onebit-step50ps-09v-vdd-20260911.json`.

An 8-device high-side bank at 1.5 V common mode, also using the explicit 50 ps
step, timed out as well. The previously retained bank-8 success is therefore
not reproducible under the current cell generator and cannot serve as a repair
or acceptance point:
`local-onebit-bank8-step50ps-15v-vdd-20260911.json`.
Finally, adding a finite 50 ps high-side gate rise and explicit `uic`
initialization still produced zero measurements at 0.9 V. The timeout survives
the tested timestep, gate-edge, device-bank, and startup-initialization
controls; this closes the parameter-screen branch and points to a netlist-level
cell/control redesign:
`local-onebit-rising50ps-uic-09v-vdd-20260911.json`.

The next cell-control revision bounded both switch edges: a 50 ps low-side
release, a 50 ps high-side rise, and a preserved 20 ps non-overlap interval.
This is the first current one-bit run to converge and produce a measurement,
but it transfers too slowly for the decision boundary: at 2.5 ns the bottom
plate is `0.472123 V` instead of `1.8 V` (error `-1.327877 V`), reaching only
`0.8239104 V` at 3.5 ns. The result establishes that bounded edges repair the
immediate solver timeout but expose an inadequate high-side charge-transfer
path; it is not an accepted cell:
`local-onebit-boundededges-09v-vdd-20260911.json`.
Adding a complementary NMOS high-side assist to the same bounded-edge cell
also timed out before measurement, so a parallel pull-up is not a reproducible
repair. Receipt:
`local-onebit-boundededges-nmosassist-09v-vdd-20260911.json`.
Increasing the same bounded-edge PMOS to `64 um` also timed out at 0.9 V,
despite the nominal 16 um cell producing a converged but badly under-settled
measurement. The high-side limitation is therefore not closed by width alone:
`local-onebit-boundededges-w64-09v-vdd-20260911.json`.

An explicit isolated transfer/hold cell was then implemented with a separately
precharged intermediate rail, a low-side release, and a transmission-gate
connection into the stored plate. It also hit the 60 s numerical-convergence
bound before measurement. The topology is retained as a classified failure,
not silently substituted for a passing direct cell:
`sky130-isolated-bottom-plate-cell.json`.
Simplifying the transfer stage to a single isolated PMOS, while retaining the
separate precharge rail, also timed out before measurement. This rules out the
transmission-gate pair as the sole numerical cause and leaves the intermediate
rail/precharge sequence itself as an unresolved topology risk:
`sky130-isolated-pmos-bottom-plate-cell.json`.
Adding a 100 ohm series element to damp the intermediate precharge supply did
not restore convergence; the damped isolated PMOS variant also timed out before
measurement. Receipt:
`sky130-isolated-pmos-r100-bottom-plate-cell.json`.
With the diagnostic bound extended to 180 s, the same damped isolated PMOS
cell eventually produced a measured transient. The intermediate rail was
`1.800 V` before transfer but fell to `1.269928 V` at 2.5 ns; the stored plate
reached only `0.2602481 V` against a `1.8 V` target (error `-1.5397519 V`).
This distinguishes slow convergence from a passing transfer and rejects the
cell at the decision boundary:
`sky130-isolated-pmos-r100-180s-bottom-plate-cell.json`.
Extending the same transient to `8.5 ns` and measuring at `7.9 ns` showed the
transfer is strongly time-dependent: the rail was `1.702962 V` and the stored
plate was `1.670877 V`, still `129.123 mV` below the `1.8 V` target. The result
is a measured long-acquisition diagnostic, not a passing decision-boundary
cell:
`sky130-isolated-pmos-r100-long-acquisition.json`.
Adding a `10 pF` intermediate-rail reservoir and beginning precharge at
`0.20 ns` made the tradeoff explicit: the rail reached only `0.6887266 V` at
1.75 ns and `0.9856228 V` at 2.5 ns; the stored plate reached only `0.01036779
V`. The reservoir cannot be charged within the available phase and is rejected
as a repair:
`sky130-isolated-pmos-r100-rail10p-earlyprecharge.json`.

The local pinned Sky130 model library is present, so a bounded one-conversion
probe was attempted under a separate output stem. Ngspice timed out before
producing measurements; this is recorded as a convergence/fixture diagnostic,
not as missing-environment evidence. The runner now fails fast with an
explicit `sky130_pdk_model_library_missing` result when the model library is
actually absent.

## Claim status

`analog_authorized` remains `false`. Native digital execution is authoritative;
the hybrid package is a simulator-backed review slice with physical fallback.
