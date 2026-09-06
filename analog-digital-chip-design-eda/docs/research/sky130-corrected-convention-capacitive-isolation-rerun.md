# Sky130 Corrected-Convention Capacitive Isolation Rerun

On 2026-09-05, the canonical corrected-convention capacitive-isolation command
was rerun with the current local toolchain. All four cases reached the
Ngspice timeout before producing measurements. The run therefore did not
replace the tracked canonical evidence.

Command:

```text
python3 scripts/run_sky130_corrected_convention_capacitive_isolation_confirm.py
```

The tracked canonical artifact remains the earlier bounded schematic result:
four measured cases, four polarity passes, and worst sampled kickback below the
12-bit half-LSB line. This rerun is a reproducibility warning, not a new pass
and not a full-converter result.

## Boundary

The rerun does not prove or disprove extracted-layout behavior, noise,
mismatch, SAR cycling, DRC/LVS, or accepted post-layout converter evidence.
