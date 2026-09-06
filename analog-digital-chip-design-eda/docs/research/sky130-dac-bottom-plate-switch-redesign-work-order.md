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
