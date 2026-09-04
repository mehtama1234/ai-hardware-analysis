# Sky130 Two-Phase SAR Bit Cycle

- status: `sar_12_comparison_wrong_code_proxy_swept_not_transistor_sar_proof`
- bits: `12`
- comparisons per case: `12`
- critical code points: `14`
- cases: `1512`
- wrong-code proxy passes: `368`
- wrong-code proxy failures: `1144`
- pass fraction: `0.243`
- maximum tested error: `5.995000000e-04` V

## What This Tests

Each case executes exactly twelve sequential decisions, from the most significant bit to the least significant bit. The test concentrates on code transitions where a small analog error can change the result. Offset, three-sigma noise, and kickback are combined as a worst-case signed disturbance.

The current sweep is a deterministic wrong-code proxy. It connects the measured two-phase signal and kickback to the SAR algorithm, but it does not turn assumed offset/noise values into circuit measurements.

## Next Gate

Replace the proxy disturbance with a transistor-level comparator and capacitor-DAC loop, then repeat the same critical-transition trace with reference settling, mismatch, noise, and conversion time recorded.

## Refused Claim

does not prove a transistor-level capacitor DAC, comparator noise, mismatch, reference settling, extracted SAR layout, or accepted converter evidence
