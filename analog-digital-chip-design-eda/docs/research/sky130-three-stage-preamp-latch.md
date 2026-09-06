# Sky130 Three-Stage Preamp Latch Test

The two-stage extracted-front-end preamp had enough isolated calibrated output margin, but its connected latch test resolved only one target polarity. A third resistor-loaded differential stage was added before the latch and calibrated with a same-run zero-input measurement.

Result:

- target cases measured: `2/2`;
- latch decisions with correct polarity: `1/2`;
- same-run third-stage offset: approximately `-224.6 mV`;
- complete latch handoff: not accepted.

Evidence: [sky130-three-stage-preamp-latch.json](../../evidence/aimc-simulator-adapters/sky130-three-stage-preamp-latch.json).

## Decision

Adding another resistor-loaded gain stage does not repair the handoff. The failure is not simply insufficient preamp gain. The next design must change the latch’s precharge/common-mode architecture or use a genuinely balanced regenerative interface with controlled input-referred offset.

## Boundary

This is a bounded connected transient test. It does not prove statistical offset, noise, mismatch, DRC/LVS, SAR conversion, or accepted converter evidence.
