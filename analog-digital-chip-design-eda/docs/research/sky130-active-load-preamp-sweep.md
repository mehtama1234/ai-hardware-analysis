# Sky130 Active-Load Preamp Sweep

The second stage of the extracted-front-end preamp was changed from matched resistive loads to matched PMOS active loads. The PMOS gate bias was swept at `0.3 V`, `0.5 V`, `0.7 V`, and `0.9 V`.

All twelve transient cases completed, and offset-corrected polarity was preserved in both target directions. None reached the required `0.5 mV` output margin:

| PMOS load bias | corrected output magnitude range | corrected margin pass |
|---:|---:|---:|
| `0.3 V` | about `0.010 mV` | `0/2` |
| `0.5 V` | about `0.012 mV` | `0/2` |
| `0.7 V` | about `0.021 mV` | `0/2` |
| `0.9 V` | about `0.060 mV` | `0/2` |

The detailed artifacts are `sky130-active-load-bias03.json`, `sky130-active-load-bias05.json`, `sky130-active-load-bias07.json`, and `sky130-active-load-two-stage-preamp.json` under `evidence/aimc-simulator-adapters/`.

## Decision

The active-load replacement is rejected for this handoff. It preserves sign but loses too much differential gain. The resistor-loaded two-stage preamp remains the stronger candidate, and the next design work should address its output common-mode and calibrated offset before the latch is reattached.

## Boundary

This is a schematic transistor preamp experiment attached to an extracted frontend. It does not prove layout, offset yield, noise, latch behavior, DRC/LVS, SAR conversion, or accepted converter evidence.
