# Sky130 Transistor DAC Calibration Analysis

This page asks whether the measured transistor DAC could eventually use a deterministic code-correction table.

The measured transfer is monotonic, which is necessary. It is not sufficient: all codes must be measured, the correction must repeat across PVT and mismatch, and the corrected thresholds must still leave enough margin for the comparator and SAR timing.

## Reproduce

```bash
python3 scripts/analyze_sky130_transistor_dac_calibration.py
```

The machine-readable result is `evidence/aimc-simulator-adapters/sky130-transistor-dac-calibration-analysis.json`.

## Boundary

This is deterministic calibration analysis from measured code points. It does not prove calibration repeatability, PVT stability, mismatch/noise yield, SAR accuracy, or silicon.
