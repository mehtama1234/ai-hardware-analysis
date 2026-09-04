# Sky130 Transistor DAC Representative PVT Codes

This page checks low, midscale, and high DAC codes at the nominal, slow/cold/low-supply, and fast/hot/high-supply corners.

It tests whether deterministic DAC calibration is stable enough to investigate further. It is a targeted corner sample, not a full all-code calibration matrix.

## Reproduce

```bash
python3 scripts/run_sky130_transistor_dac_pvt_codes.py
```

The machine-readable result is `evidence/aimc-simulator-adapters/sky130-transistor-dac-pvt-codes.json`.

The measured result is `8/9` completed cases. Only the zero-code endpoint passes the half-LSB check. Code `8` stays near `0.53 LSB` error at the nominal and slow/cold/low-supply corners, while code `15` ranges from about `1.83` to `2.50 LSB`; the fast/hot/high-supply zero-code case also times out. A nominal lookup table therefore cannot yet be treated as a stable converter correction.

## Boundary

This is representative transistor-DAC PVT evidence. It does not prove all-code calibration stability, mismatch/noise yield, SAR accuracy, extracted layout, board behavior, or silicon.
