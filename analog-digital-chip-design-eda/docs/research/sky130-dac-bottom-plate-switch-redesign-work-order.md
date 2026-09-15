# Sky130 DAC Bottom-Plate Switch Redesign Work Order

## Purpose

Repair the physical bottom-plate switch cell used by the transistor capacitor DAC so that every code can be simulated reliably at the comparator decision time. This is the next circuit gate before recalibration or a closed-loop SAR claim.

## What The Evidence Says

The present DAC result is not a clean transfer-function failure only. The latest bounded standalone run measured `4/16` codes before timeout, so reproducibility is itself failing. The earlier completed measurements showed monotonic code ordering but large high-code error. The attached comparator also changes the observed threshold through charge sharing and timing.

The local sample-switch experiment gives a useful reference: a conventional Sky130 NMOS/PMOS transmission gate can acquire low, middle, and high input voltages in its small fixture. The separate idealized bootstrap experiment now converges and acquires in all three cases, but its held voltage misses the half-LSB target by `8.5–10.5 mV`; it therefore remains a characterized, hold-failing candidate rather than the repair. The bottom-plate redesign should therefore begin with the simpler transmission-gate control and add complexity only when a measured failure requires it.

The first isolated bottom-plate attempt used one fixed top-plate source, one `8 pF` capacitor, and separate Sky130 low-side/high-side devices. The low-side pulse is `0.18 ns` wide, followed by only `0.02 ns` of actual rail-to-rail dead gap (`1.20 - (1.00 + 0.18) ns`). Its original `30 s` timeout was too short for the installed Sky130 transient model. With process-group cleanup and a `180 s` bound, all `4/4` cases now converge. The ground transition reaches `4.46e-7 V` error, but the high-side transition reaches only `0.24853 V` at `2.5 ns` and `0.30568 V` at `3.5 ns` instead of `1.8 V`. The immediate repair target is therefore high-side charge-transfer speed/topology, not convergence alone.

## Current Physical DAC-to-Comparator Handoff

The coupled comparator fixture already instantiates the same matched differential dummy pair used by the passing sample-and-hold candidate: `dummy_wn=1.0` and `dummy_wp=2.0` against `wn=2.0` and `wp=4.0`, or a nominal `0.50x` scale on both differential sides. The long-acquisition coupled run places the physical DAC top plate on the positive comparator input, retains the physical reference on the negative input, allows the dummy cancellation network to sample both storage nodes, and then enables the transistor preamp and latch.

That nominal handoff currently measures all `16/16` DAC codes and preserves comparator polarity for `16/16` codes. This closes the connection between the passing differential front-end candidate and the physical DAC/comparator transient. It does not close the converter: the DAC bottom-plate transfer is still not fully legal/settled at the required decision boundary, the controller does not yet run a retained-bit SAR sequence in the same transient, and PVT, mismatch/noise, extraction, and energy gates remain open.

The coupled runner now exposes `AIMC_COUPLED_DIFFERENTIAL_DUMMY=1` and `AIMC_COUPLED_DIFFERENTIAL_DUMMY_SCALE=<scale>` to sweep the existing dummy parameters without duplicating devices. This is an experiment hook, not an acceptance switch; the canonical evidence remains the reproducible default run.

## First-Principles Failure Questions

For each bottom plate, answer these questions separately:

1. Is the plate held at the intended pre-redistribution voltage before the edge?
2. Is the old rail disconnected before the new rail is connected?
3. Does the selected switch reach the rail within the allowed settling time?
4. Does the unselected switch remain isolated from the opposite rail?
5. Does the control edge inject enough charge to move the top plate by more than half an allowed code step?
6. Does the node remain numerically well-posed when the switch is off?

The current deck combines these questions in a 16-code transient, which makes a timeout difficult to diagnose. The redesign must first prove one isolated one-bit bottom-plate cell, then prove two complementary cells, then reconnect the binary array.

## Required Cell Experiments

### A. One-bit charge-transfer fixture

Use one physical capacitor, one bottom-plate switch cell, and the installed Sky130 models. Measure the bottom plate and top plate before the edge, during break-before-make, and after the new rail is selected.

Required cases:

- plate held at ground, then moved to `VDD`
- plate held at `VDD`, then moved to ground
- low, middle, and high top-plate common modes
- nominal, slow/cold/low-supply, and fast/hot/high-supply corners

Required measurements:

- old-rail disconnect time
- new-rail arrival time
- top-plate kick from the control edge
- final rail error
- convergence status and runtime

### B. Complementary control check

The control generator must expose two non-overlap intervals: `break_before_make_ns` and `make_after_break_ns`. The generated deck must show the exact gate waveform used by each device. A control waveform that turns both rail paths on together is rejected even if its final voltage looks reasonable.

### C. Four-bit reconstruction

After the one-bit cell passes, reconnect the `8:4:2:1` capacitors and measure all 16 codes at the same fixed decision time. The acceptance record must include every code, every bottom-plate final voltage, the top-plate voltage, the expected voltage, and the error in LSB.

## Acceptance Gates

The cell is accepted only when:

- all requested codes converge without timeout;
- the selected bottom plate reaches its intended rail without simultaneous rail contention;
- the four-bit transfer is monotonic;
- the top-plate error at the comparator decision time is within the declared budget, or the budget is explicitly changed and propagated to the SAR task metric;
- both comparator polarities remain correct in the same-deck coupled run;
- the exact deck and control schedule are stored with the evidence;
- the result is repeated at the required PVT corners before analog service is enabled.

Passing only the final comparator sign is insufficient. A comparator can resolve the wrong physical threshold consistently, which is exactly why the earlier retained-bit sequence produced `0/5` correct conversions despite `20/20` sign-correct trials.

## Implementation Order

1. Factor the bottom-plate switch into a generated one-bit cell.
2. Add explicit break-before-make control and waveform measurements.
3. Run the one-bit low/mid/high common-mode fixture.
4. Run the one-bit PVT fixture and record convergence.
5. Rebuild the four-bit array from four identical cells.
6. Run all 16 codes at the comparator decision time.
7. Reconnect the physical comparator and repeat both polarities.
8. Re-run calibration and retained-bit SAR decisions.
9. Only then add random mismatch/noise trials and model-level task evaluation.

## Refused Claim

This work order does not claim that the current DAC is repaired, calibrated, SAR-correct, layout-extracted, board-measured, or silicon-proven. It defines the evidence needed to make those claims defensible.

## Evidence checkpoint — 2026-09-10

The fixed-decision schedule was repaired so plates that have not reached their
decision edge are held at the low rail rather than left floating. A Colab T4
ideal-switch reference then measured legal bottom-plate rails for all five FF
conversions, but its observed code map remained `[0, 13, 11, 9, 8]` instead of
the required `[0, 2, 4, 6, 7]`. This separates schedule legality from transfer
calibration.

The same schedule was measured with complementary Sky130 NMOS/PMOS devices,
top-plate reset, PFET gate overdrive, and a 10 kΩ bottom keeper. Those variants
all retained the wrong FF map and illegal later-conversion plates; FS did not
produce a child receipt. The next implementation must therefore be a new
one-bit transistor cell with explicit device isolation and charge-injection
measurements, followed by two-cell and four-bit reconstruction. No closed-loop
or GPT-2 workload claim is allowed until that cell contract passes.

The bootstrapped-high diagnostic subsequently reached legal FF rails on all
five conversions, but decoded `[15, 13, 15, 15, 14]`. It improves rail
reachability while disturbing the threshold transfer, and its boosted gate is
not reliability-qualified. It remains a topology clue, not an accepted cell.

With the latch-input polarity swap and an explicit initial reset, the
complementary transistor path reached steady-state codes `[2, 4, 6, 7]` for
the last four references. The first conversion decoded `12`, and later
bottom-plate samples remained illegal. The next cell revision must therefore
provide a defined startup state and contain transistor charge injection while
preserving the corrected comparator polarity.

The ideal-switch follow-up with a startup reference profile measured the exact
FF logical map `[0, 2, 4, 6, 7]`. One later DAC legality check still failed and
the FS child receipt was unavailable, so this isolates a useful reference
profile but does not qualify the transistor cell or converter.

The complementary Sky130 transistor run with that same profile then measured
the exact FF code map `[0, 2, 4, 6, 7]`, while only conversion 1 passed the
bottom-plate legality check. Conversions 2–5 remained physically illegal and
FS again produced no child receipt. The next cell revision must preserve this
logical transfer while isolating transistor charge injection and holding every
bottom plate inside the rails.

The raw FF samples identify the immediate defect: later PMOS-selected plates
reach about `1.80023 V`, above the `1.8 V` rail, while unselected plates return
near ground. A strong-clamp screen is prepared, but it remains diagnostic until
it demonstrates bounded, reliability-qualified rails in complete FS/FF runs.

The `1e6`-area diode clamp screen instead caused an ngspice timestep collapse at
the sample-reset branch near `119.118 ns`. This rejects brute-force diode
clamping as the repair. The next cell must use timed isolation and a bounded
rail handoff so the reset network is not forced to absorb the switching event.

A 100 Ω PMOS source-resistor screen also collapsed ngspice at the handoff
branch near `301.206 ns`. Adding a passive series element to the existing
behavioral handoff therefore creates another stiff branch; the redesign must
remove that behavioral handoff from the measured cell and use an explicit
finite-edge isolation device instead.

The isolated sample-to-preamp copy run preserved the exact FF map and made all
cycle DAC threshold checks legal, but later bottom-plate samples remained
illegal. This localizes the remaining defect to the PMOS/NMOS plate switch and
its rail handoff, rather than the comparator input loading.

A global 2 ns gate-edge screen collapsed at the precharge branch near
`173.206 ns`. Edge slowing must therefore be applied only to an isolated
per-cycle switch control, with precharge and rail handoff explicitly
non-overlapping.

The generator now exposes `AIMC_CONTINUOUS_GATE_DEAD_TIME_NS` independently
from `AIMC_CONTINUOUS_PWL_RISE_NS`; the prepared 2 ns gate-only screen keeps
the precharge edge at 0.2 ns. This is the next physical charge-injection test.

Colab measured the gate-only 2 ns screen with the exact FF map intact. The
later PMOS peak improved from about `1.800233 V` to `1.800215 V`, but
conversions 2–5 still failed the rail check. Gate-edge control is therefore a
useful trim, not the complete repair; it must be combined with explicit rail
isolation and a bounded hold device.

At 4 ns, the same screen made conversion 2 rail-legal and reduced the later
peak to about `1.800047 V`, while conversions 3–5 remained just outside the
rail contract. The next edge point is 8 ns; if the trend saturates, the design
must add a dedicated bounded clamp or handoff device rather than keep widening
the gate edge.

The 8 ns point broke the transfer and rail behavior, producing FF codes
`[0, 2, 0, 2, 3]` with all five conversions illegal. The usable edge window is
therefore below 8 ns; further gate widening is rejected in favor of an
explicit bounded isolation/hold cell.

The first physical transmission-gate isolation cell, with a 0.5 pF plate hold,
was measured on Colab and rejected: FF produced `[0, 2, 4, 6, 3]`, and all
bottom-plate checks were illegal. The isolation device and hold load are too
intrusive at that size; the next iteration must reduce hold capacitance and
switch width while preserving the isolated preamp copy.

The reduced 2 µm/0.05 pF cell still produced FF `[0, 2, 0, 2, 3]` with all
rails illegal. The series transmission-gate architecture is therefore
rejected at both tested load sizes. The next revision returns to the direct
plate topology and limits isolation to the control/state path.

The direct PMOS 100 Ω screen, with the behavioral handoff disabled, still
collapsed ngspice at the sample-reset branch near `173.206 ns`. Passive source
resistance is therefore rejected as a multi-cycle repair; the next cell must
use explicitly sequenced control states with no added stiff branch.

A direct PMOS-bank-1 run preserved the FF code map but worsened the plate peak
to about `1.99504 V`. PMOS bank reduction is therefore rejected as a sizing
fix; the next revision must control the PMOS turn-off state explicitly rather
than rely on parallel-device count.

A direct PMOS gate-low bias of `0.3 V` preserved the FF map but increased later
plate peaks to about `1.810108 V`. Reducing PMOS overdrive is therefore
rejected; the next cell must sequence PMOS turn-on and turn-off states around
the acquisition window instead of relying on static gate bias.

A one-sided 0.5 ns PMOS turn-on delay preserved the FF map but worsened later
plate peaks to about `1.855405 V`. One-sided skew is rejected; the next control
cell must sequence complementary NMOS/PMOS states together with explicit
break-before-make timing.

The symmetric 0.5 ns NMOS-advance/PMOS-delay screen preserved the FF map but
increased later plate peaks to about `1.808833 V`. Simple gate skew is therefore
rejected; controls must be generated as explicit mutually exclusive phases in
a state machine, with a measured hold interval between rail ownership changes.

The local `check_direct_gate_phase_contract.py` now enforces strictly
increasing finite PWL controls and rejects simultaneous PMOS-on/NMOS-on rail
requests before any Colab run. The small 0.1 ns complementary phase-gap
settings are the next measured control-state screen.

Colab measured the 0.1 ns phase-gap screen with the exact FF map intact. One
later high rail reached `1.799785 V`, but subsequent peaks reached `1.800776 V`
and small negative excursions remained. Control sequencing helps, but a
bounded physical hold/clamp is still required for rail qualification.

The direct topology was then given a bounded `0.05 pF` hold capacitor to VDD
while retaining the 4 ns break-before-make interval. Colab preserved the FF
code map `[0, 2, 4, 6, 7]`, but bottom-plate legality remained
`[true, false, false, false, false]` and the later plate peak increased to
about `1.800894 V`. A passive hold capacitor alone is therefore insufficient;
the next revision must use an explicitly state-controlled transistor hold or
clamp whose enable and release are sequenced with the measured phase gap.

The first explicit sequential state-control campaign passed structural
preflight and completed both FS and FF on Colab, but every conversion decoded
as code `15`. The held decision nodes therefore are not aligned with the
comparator capture events (or are not driving the complementary gate switches
with the required polarity). This is a hard rejection of the current state
capture timing, not evidence against physical state control itself. The next
experiment must probe `seq_state*`, `seq_inv*`, and both DAC gate nodes at each
capture boundary, then adjust capture delay/width and gate-driver polarity
before another full-corner campaign.

An opt-in 0.9 V state quantizer was added before the complementary gate
switches and the campaign was repeated on FS and FF. Structural preflight
passed, but all ten conversions still decoded as `15`; the measured gate
handoff remained at the inactive rail. The defect is therefore downstream of
the analog state voltage threshold, in capture scheduling or switch-drive
connectivity. The next diagnostic must expose the complete `seq_clk`,
`seq_state`, `seq_logic`, `seq_logic_inv`, `gp_dac`, and `gn_dac` waveforms at
each boundary and verify switch control polarity before changing device sizing.

The corrected timing-probe campaign measured valid 1.8 V capture clocks,
stable held states, valid quantized logic, and the expected complementary gate
polarity on both FS and FF. Every comparator decision was still zero, yielding
code `15` for all five conversions. Sequential state control is therefore no
longer the active defect; the next experiment must isolate comparator/preamp
sense polarity and decision-source timing with the known-good fixed-decision
DAC waveform, then reconnect the state controller after the decision map is
restored.

The latch-input-swap screen confirmed the comparator polarity direction: FS
now produced decision bits `[1, 1, 1, 1]` and code `0` on every conversion,
while FF collapsed at the sample-reset branch. The polarity is therefore
corrected but the DAC waveform is not progressing through the intended trial
levels under sequential control. The next step is a fixed-decision versus
sequential A/B run at FS with identical references and reset timing, followed
by removal or re-timing of the sample-reset branch before another FF attempt.
The FS fixed-versus-sequential A/B run used identical references, latch
polarity, and corner. The fixed arm restored the exact `[0, 2, 4, 6, 7]` map;
the sequential arm failed at the `bcont_sample_reset` branch before producing
a receipt. This isolates reset injection as the immediate sequential blocker.
The next run disables the sample-reset branch in the sequential arm while
leaving the fixed arm unchanged, then compares the per-cycle DAC and state
probes.

The reset-off FS A/B run preserved the fixed arm's exact code map, while the
sequential arm advanced to a timestep collapse at the `bcont_handoff` branch.
This shows the sample-reset branch was only the first failure; the behavioral
handoff is the next stiff branch preventing sequential operation. The next
iteration disables both reset and behavioral handoff in the sequential arm and
then measures whether the explicit state-controlled DAC can run through all
five decisions.

With both sample reset and behavioral handoff disabled, the isolated FS
sequential arm completed without a timestep failure but produced
`[0, 0, 0, 0, 0]`; the fixed arm still produced `[0, 2, 4, 6, 7]`. The
remaining defect is therefore decision-dependent DAC progression or latch
handoff semantics. The next diagnostic will compare each bit's held state and
gate waveform against the fixed-decision waveform at the four trial times,
then correct the state-to-bit mapping before restoring any handoff circuitry.
The static `check_sequential_bit_mapping.py` contract now passes: each
`seq_stateN` captures `decN` and drives only matching DAC bit `N-1`, including
the split-MSB case. Wiring is therefore not cross-connected. The next physical
diagnostic must hold a validated decision sequence at those state nodes and
compare plate charge against the fixed-decision waveform, isolating latch
handoff semantics from DAC gate connectivity.

The first phase-safe Colab invocation did not actually enable the new phase
driver because the A/B harness omitted its environment flag. Its fixed-state
result is therefore retained only as a pre-phase-safe baseline. The harness
now passes `AIMC_CONTINUOUS_STATE_PHASE_SAFE=1` explicitly to both sequential
arms; the next receipt will be the authoritative physical test of the
PMOS-high/NMOS-low dead-state implementation.

The fixed-state FS diagnostic used the validated decision sequence but still
returned `[0, 0, 0, 0, 0]` and negative first-cycle DAC values. The state-to-bit
wiring contract passed; the failure is the gate driver's dead-state semantics.
A single state value cannot simultaneously provide the required PMOS-high /
NMOS-low break-before-make baseline. The next redesign adds an explicit
phase-safe gate driver that holds those dead rails until each bit's 5/21/37/53
ns trial edge, then applies the captured state only during its active window.
The authoritative phase-safe FS A/B run completed all conversions without a
timestep failure. The fixed arm retained `[0, 2, 4, 6, 7]`; the sequential arm
improved to `[7, 0, 0, 0, 0]`. The explicit dead-state driver is therefore
effective, but held-state voltages drift from roughly `0.20 V` to `0.82 V`
across conversions and the fixed `0.9 V` quantizer misses the comparator
decisions. The next experiment calibrates the state decoder threshold (or adds
a restoring latch) against these measured levels before changing the DAC.

The `0.3 V` threshold sweep changed the first sequential code from `7` to `6`
but left later conversions at `0`. Threshold sensitivity is real, yet no fixed
threshold can compensate for the measured cross-conversion state drift. The
next redesign therefore adds a restoring latch after each decision capture,
with explicit reset and break-before-make timing, instead of further open-loop
threshold sweeps.
The cross-coupled restoring-latch FS campaign completed without numerical
failure but returned `[0, 0, 0, 0, 0]` for both sequential arms, while the
fixed arm remained exact. A free-running latch stabilizes the wrong state
because it has no explicit set/reset phase around comparator capture. This
architecture is rejected; the next design uses pulse-controlled set/reset
devices with a defined capture, restore, and hold sequence.
The pulse-controlled set/reset restore campaign also completed without a
timestep failure but returned `[0, 0, 0, 0, 0]` for the sequential arm; the
fixed arm remained `[0, 2, 4, 6, 7]`. Restore pulses alone do not recover the
decision sequence. The active design question is now the comparator-to-state
interface and SAR timing contract, rather than rail stability.
The sequential timing contract has been corrected: comparator decision N now
drives the next DAC trial bit (dec1→bit1, dec2→bit2, dec3→bit3, dec4→bit0 of
the following conversion), matching the fixed waveform's 5/21/37/53 ns
trial edges. The static mapping and deck preflight pass. All earlier
sequential transient receipts used the old one-phase-late mapping and are not
evidence against this corrected schedule; the next Colab run must remeasure it.

The corrected one-phase-ahead mapping was remeasured on a pinned Sky130 Colab
T4 run. The fixed arm again produced the exact `[0, 2, 4, 6, 7]` map, while
both fixed-state and live sequential arms produced `[0, 0, 0, 0, 0]` with a
completed transient. Therefore the timing correction is necessary but
insufficient; the next work item is to instrument and repair the decision
capture-to-gate handoff before any PVT, noise, mismatch, or workload claims.

The follow-up direct-gate and same-bit mapping diagnostics clarify the repair:
the captured state is present, but one control per decision cannot both retain
the previous bit and present the next trial bit at the shared SAR edge. The
next implementation must emit an explicit two-control sequencer: a retained
gate update for bit N and a trial-enable update for bit N+1, with separate
phase windows and probes for each. The fixed arm remains the reference receipt
for every subsequent comparison.

The first two-control behavioral prototype was added, but its ideal hard-step
gate equations produced a singular node in the remote transient. The prototype
is therefore rejected as a numerical implementation; the follow-up must use
finite-rise sources plus explicit gate holds before a new T4 receipt.

The finite-rise retry still aborted at the highest-bit behavioral gate source,
even though all other A/B arms completed. The next repair is to smooth the
decision-dependent term itself (not only the time edges), or replace the
behavioral source with a sampled transistor switch, before requesting another
full-campaign receipt.

The sampled transistor-switch replacement now completes the full T4 transient.
Its two-control arm still returns `[0, 0, 0, 0, 0]`; gate probes sit near the
0.9 V switch threshold during handoff, showing contention between the trial
override and retained-state paths. The next repair is break-before-make timing
and non-overlapping gate ownership at each SAR edge.

The break-before-make T4 receipt completes without threshold contention, but
the two-control arm remains `[0, 0, 0, 0, 0]`. The next diagnostic must sample
both PMOS and NMOS gate rails at each trial edge; retained rails are clean,
while trial-enable connectivity and polarity are not yet proven.

The edge-probe deck now records trial and retained PMOS/NMOS rails separately.
The measured receipt showed the held state charging slowly (approximately
0.37–0.82 V across conversions), so the calibration arm was widened to a 3 ns
capture delay and 2 ns capture window. Its T4 rerun is pending Colab capacity;
the structural preflight passes for the new controls and probes.

The next unmeasured calibration selects `raw_decN` as the state-sampler input,
with a 3 ns delay and 2 ns aperture, to remove the observed slow-latch rail
settling. The Colab assignment service is currently returning
`TooManyAssignmentsError`; no result is recorded until this calibration runs.

The ownership-gated T4 receipt proves the trial override path: both trial gate
rails measure approximately 0 V while retained rails measure approximately
1.8 V. The two-control arm partially progresses to `[0, 0, 8, 0, 0]`, so the
remaining repair is the retained-bit polarity/weight schedule rather than
trial connectivity.

The raw-decision capture calibration has now run on T4. State probes reach
approximately 0 V or 1.8 V rails, and the two-control arm changes to
`[0, 0, 15, 0, 0]`. This proves the state-sampler repair; the remaining issue
is conversion-to-conversion DAC state sequencing, especially the retention
boundary after conversion 2.

The sequential-only reference calibration also completed on T4 with no code
progression: `[0, 0, 0, 0, 0]` despite references `[1.1, 1.4, 1.1, 1.4, 1.75]`.
This rules out a simple reference-window mismatch as the primary blocker. The
next repair must establish the initial and conversion-boundary trial charge
state before comparator decisions are captured.

An explicit sample-reset boundary test completed on T4 but returned
`[0, 0, 0, 0, 0]`. Resetting the plate path does not restore progression and
disrupts the retained-state sequence, so the next implementation must keep
state retention separate from any plate acquisition reset.
