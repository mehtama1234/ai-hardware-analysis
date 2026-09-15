# Online schedule audit

Receipt: `/home/mehtama1/git-repo/ai-hardware-analysis/analog-digital-chip-design-eda/evidence/colab-rawcapture-ab-20260911/sequential-raw.json`

Status: `continuous_physical_sar_candidate_measured_not_accepted`

### sky130_continuous_physical_sar

| conversion | final code | retained bits | raw decision V | state rails | trial P rails | retained P rails |
|---:|---:|---|---|---|---|---|
| 1 | 15 | `1111` | `0.000,0.000,0.000,0.000` | `MID,MID,MID,MID` | `LOW,LOW,LOW,LOW` | `HIGH,HIGH,HIGH,HIGH` |
| 2 | 0 | `0000` | `1.800,1.800,1.800,1.800` | `MID,MID,MID,MID` | `LOW,LOW,LOW,LOW` | `HIGH,HIGH,HIGH,HIGH` |
| 3 | 6 | `0110` | `1.800,0.000,0.000,1.800` | `HIGH,MID,MID,HIGH` | `LOW,LOW,LOW,LOW` | `HIGH,HIGH,HIGH,HIGH` |
| 4 | 14 | `1110` | `0.000,0.000,0.000,1.800` | `MID,LOW,LOW,HIGH` | `LOW,LOW,LOW,LOW` | `HIGH,HIGH,HIGH,HIGH` |
| 5 | 5 | `0101` | `1.800,0.000,1.800,0.000` | `MID,LOW,MID,MID` | `LOW,LOW,LOW,LOW` | `HIGH,HIGH,HIGH,HIGH` |

Claim boundary: one continuous five-conversion physical DAC/comparator transient; fixed-decision diagnostic when enabled; not closed-loop qualification, PVT, mismatch/noise, extracted-layout, board, or silicon acceptance

## Interpretation

This table classifies saved probe voltages at the conversion boundary. It does not prove timing margin, PVT robustness, mismatch tolerance, energy, or analog authorization.
