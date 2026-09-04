# Sky130 Transistor-Switched Capacitor DAC

This page is the next physical boundary after the ideal-switch capacitor DAC. It uses Sky130 NMOS/PMOS devices for the sample path and bottom-plate redistribution switches, then measures the same binary code thresholds and settling error.

## Reproduce

```bash
python3 scripts/run_sky130_transistor_switched_capacitor_dac.py
```

The machine-readable result is `evidence/aimc-simulator-adapters/sky130-transistor-switched-capacitor-dac.json`.

The first switch-sizing and timing diagnostic improves the worst measured error to about `143 mV` with wider devices and a `70 ns` redistribution read point. After fixing a repeating-pulse control bug, all sixteen codes complete and their measured order is monotonic. Codes `8` through `11`, `14`, and `15` exceed the `56.25 mV` half-LSB target; the worst error is about `206.9 mV`, so the DAC is not accepted for the SAR loop.

## Boundary

This is transistor-switched DAC evidence. It does not prove capacitor mismatch statistics, reference loading across a full SAR, comparator coupling, extracted layout, board behavior, or silicon.
