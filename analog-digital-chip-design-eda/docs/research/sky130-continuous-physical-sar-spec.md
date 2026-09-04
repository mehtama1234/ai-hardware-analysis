# Sky130 Continuous Physical SAR Specification

This contract defines the next proof rung after the nominal calibrated
four-bit result. The current calibrated runner uses a fresh transient for each
bit decision; that is useful physical comparison evidence but is not a
continuous multicycle SAR.

## Required Evidence

- one continuous transient containing all four retained-bit cycles;
- source acquisition, break-before-make redistribution, comparator sampling,
  and latch timing recorded for every cycle;
- physical DAC threshold measured before comparator kickback at every cycle;
- no ideal numerical threshold injected into the comparator;
- five representative conversions, each with four measured decisions;
- cycle-to-cycle state retained between bits and reset only between conversions;
- the PMOS-only topology and the source-matched calibration map bound to the
  same hardware profile.

The machine-readable contract is
`evidence/aimc-simulator-adapters/sky130-continuous-physical-sar-spec.json`.

## Claim Boundary

This is an acceptance contract for the next physical deck. It is not evidence
that continuous multicycle SAR operation, PVT, mismatch/noise yield, extracted
layout, board behavior, or silicon has been demonstrated.
