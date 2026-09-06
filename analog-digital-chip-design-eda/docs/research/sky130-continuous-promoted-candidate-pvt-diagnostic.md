# Sky130 Continuous SAR Promoted Candidate PVT Diagnostic

The promoted nominal candidate uses the switched post-sample DAC/reference
handoff, a `64 um` low-side NMOS, an eight-device PMOS bank, and a measured
`1.5x` scale on the LSB capacitor. Its nominal five-conversion map
passes all codes and bottom-plate legality.

## Corner results

| Process | Supply | Temperature | Code map | Bottom plates |
|---|---:|---:|---|---|
| SS | 1.62 V | 85 C | `0→0, 2→2, 4→5, 6→7, 7→7` at 1.5×; `0→0, 2→2, 4→4, 6→6, 7→7` at 2.0× | pass |
| FF | 1.98 V | −20 C | `0→0, 2→2, 4→4, 6→6, 7→7` at 1.5× | pass |
| SS | 1.80 V | 27 C | `0→0, 2→2, 4→4, 6→6, 7→7` at 1.5× | pass |
| FF | 1.80 V | 27 C | `0→0, 2→2, 4→5, 6→7, 7→7` at 1.5× | pass |

Evidence:

- `evidence/aimc-simulator-adapters/sky130-continuous-promoted-ss162-hot.json`
- `evidence/aimc-simulator-adapters/sky130-continuous-promoted-ff198-cold.json`
- `evidence/aimc-simulator-adapters/sky130-continuous-promoted-ss27.json`
- `evidence/aimc-simulator-adapters/sky130-continuous-promoted-ff27.json`

The trim-selection workflow is implemented in
`scripts/run_sky130_continuous_trim_calibration.py`. A checked SS-hot run
selects `2.0x` from the supplied candidate list and records the result in
`evidence/aimc-simulator-adapters/sky130-continuous-trim-calibration-check-ss-1.62v-85c.json`.

## Decision

The nominal candidate is promoted for nominal schematic-level map evidence.
The four measured corner runs show a calibration path: the SS low-voltage/hot
corner requires a 2.0× LSB trim, while the other tested corners use 1.5×.
This is not yet a universal PVT qualification because the trim procedure must
be implemented in the eventual control/firmware path and then requalified for
mismatch, noise, and extracted layout.
