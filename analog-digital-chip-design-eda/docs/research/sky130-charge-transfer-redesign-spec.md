# Sky130 Charge-Transfer Redesign Specification

The selected PMOS-only, low-source candidate now meets the nominal all-code
calibration and five-representative-conversion gates under the corrected
pre-sample measurement and rank-preserving map. The candidate is not accepted
yet: this fixed specification still governs robustness, continuous-SAR, and
post-layout validation.

## Required Phase Order

1. Initialize the top plate with an explicit device path, not an `.ic` value.
2. Acquire the source voltage.
3. Open the source path and enforce break-before-make isolation.
4. Redistribute selected bottom-plate charge.
5. Sample the comparator only after redistribution has settled.
6. Enable the preamp and latch after the DAC threshold measurement.

## Acceptance Gates

- all 16 codes converge without timeout;
- every top and bottom plate remains within `0..1.8 V`;
- adjacent code spacing is at least `56.25 mV` for the 4-bit profile;
- settling error is at most `28.125 mV` at the threshold measurement point;
- selected and unselected controls never connect both rails simultaneously;
- the same topology completes five representative SAR conversions;
- PVT and 100-trial mismatch runs are performed before any analog placement is
  enabled.

The machine-readable contract is
`evidence/aimc-simulator-adapters/sky130-charge-transfer-redesign-spec.json`.
The accepted nominal candidate is the PMOS-only topology with source common
mode `0.004 V` and calibration reference `0.604 V`. Earlier PMOS-only,
lower-common-mode, top-dummy, and top-reset probes remain rejected diagnostics;
they are not silently combined with the current candidate. A converged
comparator sign alone is not enough if the threshold map is out of range or the
endpoint does not converge.

## Claim Boundary

This page is a design and acceptance contract. It records nominal candidate
evidence, but it is not evidence of PVT/mismatch/noise yield, continuous SAR,
extracted layout, or accepted production hardware.
