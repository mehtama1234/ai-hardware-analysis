# Sky130 Preamp Capacitive-Latch Sweep

The two-stage transistor preamp was connected to the latch through capacitive isolation, using the earlier schematic idea that had passed with a much smaller ideal signal. Coupling values of `0.01 fF`, `0.05 fF`, `0.1 fF`, and `0.2 fF` were tested.

All cases completed, but every coupling value resolved only one of the two target polarities. The measured latch-gate differential after regeneration remained about `0.234–0.241 V` in magnitude, while the input polarity-dependent transition was only tens to hundreds of microvolts before regeneration.

The detailed artifacts are `sky130-two-stage-preamp-cap-latch-001.json`, `sky130-two-stage-preamp-cap-latch-005.json`, `sky130-two-stage-preamp-cap-latch-01.json`, and `sky130-two-stage-preamp-capacitive-latch.json` under `evidence/aimc-simulator-adapters/`.

## Decision

Capacitive isolation alone is not sufficient for this extracted preamp/latch interface. It removes a DC path but does not provide enough differential drive to control regeneration. The next circuit must create a stronger, balanced differential signal before the latch—likely a dedicated fully differential output stage with controlled common-mode and a defined offset-cancellation mechanism.

## Boundary

This is a connected transistor transient diagnostic. It does not prove statistical offset, noise, mismatch, extracted preamp layout, DRC/LVS, SAR bit cycling, or accepted converter evidence.
