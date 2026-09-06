# Sky130 Continuous SAR Low-Side Clamp Width Sweep

The canonical continuous SAR candidate had legal DAC top-plate samples but
small bottom-plate excursions below ground. This sweep widened the physical
low-side NMOS devices, without adding a precharge device or changing the
decision waveforms.

| Low-side NMOS width | Scope | Result | Bottom-plate gate | Conversion result |
|---:|---|---|---|---|
| 8 µm | five conversions | baseline | fail | `0→0, 2→1, 4→4, 6→6, 7→7` |
| 64 µm | one conversion | measured | pass | `2→0` |
| 64 µm | five conversions | measured | fail | `0→0, 2→2, 4→4, 6→6, 7→8` |
| 128 µm | five conversions | invalid deck | not measured | Sky130 model rejects width |

The 64 µm device is a meaningful improvement in the repeated sequence: three
previously problematic representative conversions (`2`, `4`, and `6`) decode
correctly, and the first one-conversion diagnostic keeps every sampled bottom
plate inside 0–1.8 V. In the required five-conversion history, however, later
states still reach about `−198 µV` and `2.008 V`; the highest case changes from
`7→7` to `7→8`. The wider clamp changes the charge-transfer trajectory instead
of merely removing undershoot.

The 128 µm setting is not evidence of a failed transient: the Sky130 model
rejects that width during netlist elaboration, so it must not be used as a
candidate sizing point.

This sweep is therefore a sizing boundary, not acceptance. The next repair
must isolate the bottom-plate clamp from the retained charge-transfer path or
change the switch/control topology. It must then pass all five conversions,
the 0–1.8 V node-range gate, and the existing PVT/layout evidence gates.

Evidence:

- `evidence/aimc-simulator-adapters/sky130-continuous-nmos64-single.json`
- `evidence/aimc-simulator-adapters/sky130-continuous-nmos64-full.json`
- `evidence/aimc-simulator-adapters/sky130-continuous-nmos128-full.json`
