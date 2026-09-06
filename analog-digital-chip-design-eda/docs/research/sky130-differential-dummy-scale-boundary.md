# Sky130 Differential Dummy-Scale Boundary

The complementary differential break-before-make DAC was calibrated at three
dummy-cancellation scales. The purpose was to separate nominal threshold
spacing from the later SAR mapping problem.

| Differential dummy scale | Minimum adjacent spacing | Calibration result | SAR result |
|---:|---:|---|---|
| 4× | about 20.1 mV | `16/16` measured | `2/5` in the full-scale rerun |
| 2× | about 45.7 mV | `16/16` measured | not replayed |
| 1× | about 58.3 mV | `16/16` measured | `1/5` with endpoint-fitted affine mapping |

The 1× setting is the first to clear the 4-bit 56.25 mV spacing target, but
that does not make it a converter pass. Its full mapped SAR run still fails
four representative conversions, and the affine mapping aliases endpoint
codes. This is an important separation: adequate nominal spacing is necessary
but not sufficient when the physical transfer is nonlinear and the source
common-mode changes the decision trajectory.

The candidate remains rejected until the map is injective, all five
conversions are correct, both differential plates stay legal, and the same
topology passes continuous-state, PVT, mismatch/noise, and layout gates.

The current authoritative calibration artifact is
`evidence/aimc-simulator-adapters/sky130-thermometer-calibrated-physical-sar.json`.
The full 1× replay result is retained in the run history and is not promoted
as acceptance evidence.
