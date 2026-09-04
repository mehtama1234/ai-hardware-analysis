# Sky130 Two-Phase SAR Bit Cycle

This page connects the measured two-phase comparator boundary to a 12-comparison SAR algorithm. The machine-readable source is `evidence/aimc-simulator-adapters/sky130-two-phase-sar-bit-cycle.json`.

## Result

- Every case executes `12` sequential decisions, from the most significant bit to the least significant bit.
- The sweep tests `14` critical code points on both sides of the selected code values.
- `1,512` combinations were tested with both disturbance directions.
- `368` passed and `1,144` produced a wrong-code proxy failure.
- The test combines offset, three-sigma noise, and measured kickback as a worst-case signed disturbance.

## First-Principles Reading

A SAR ADC is not proven by showing that its state machine has twelve steps. The analog value must remain on the correct side of every threshold while those steps occur. Near a code boundary, even a small error changes the final code. The failed cases show why the converter must carry a threshold-specific error budget into the model and runtime governor.

The high failure count is expected for the deliberately aggressive `200 uV` offset, `100 uV RMS` noise, and `5x` kickback combinations near a boundary. It is evidence that the earlier bounded margin proxy cannot be promoted to a general 12-bit accuracy claim.

## Next Gate

Run the same critical-transition sweep with a transistor-level comparator, capacitor-DAC/reference path, measured offset and noise, and the actual conversion clock. The resulting wrong-code rate must be reported per transition and carried into analog acceptance and digital fallback.

## Refused Claim

This result does not prove a transistor-level SAR, capacitor mismatch, reference settling, comparator noise, extracted SAR layout, or accepted converter evidence.
