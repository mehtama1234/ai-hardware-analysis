# Online schedule audit

Receipt: `/home/mehtama1/git-repo/ai-hardware-analysis/analog-digital-chip-design-eda/evidence/colab-rawcapture-ab-20260910/comparison.json`

Status: `completed`

### fixed

| conversion | final code | retained bits | state rails | trial P rails | retained P rails |
|---:|---:|---|---|---|---|
| 1 | 0 | `0000` | `—` | `—` | `—` |
| 2 | 2 | `0010` | `—` | `—` | `—` |
| 3 | 4 | `0100` | `—` | `—` | `—` |
| 4 | 6 | `0110` | `—` | `—` | `—` |
| 5 | 7 | `0111` | `—` | `—` | `—` |

Claim boundary: one continuous five-conversion physical DAC/comparator transient; fixed-decision diagnostic when enabled; not closed-loop qualification, PVT, mismatch/noise, extracted-layout, board, or silicon acceptance

### two_control

| conversion | final code | retained bits | state rails | trial P rails | retained P rails |
|---:|---:|---|---|---|---|
| 1 | 0 | `0000` | `HIGH,HIGH,HIGH,HIGH` | `LOW,LOW,LOW,LOW` | `LOW,LOW,LOW,LOW` |
| 2 | 0 | `0000` | `HIGH,HIGH,HIGH,HIGH` | `LOW,LOW,LOW,LOW` | `HIGH,HIGH,HIGH,HIGH` |
| 3 | 15 | `1111` | `LOW,LOW,LOW,LOW` | `LOW,LOW,LOW,LOW` | `HIGH,HIGH,HIGH,HIGH` |
| 4 | 0 | `0000` | `HIGH,HIGH,HIGH,HIGH` | `LOW,LOW,LOW,LOW` | `LOW,LOW,LOW,LOW` |
| 5 | 0 | `0000` | `HIGH,HIGH,HIGH,HIGH` | `LOW,LOW,LOW,LOW` | `HIGH,HIGH,HIGH,HIGH` |

Claim boundary: one continuous five-conversion physical DAC/comparator transient; fixed-decision diagnostic when enabled; not closed-loop qualification, PVT, mismatch/noise, extracted-layout, board, or silicon acceptance

### fixed_state

| conversion | final code | retained bits | state rails | trial P rails | retained P rails |
|---:|---:|---|---|---|---|
| 1 | 0 | `0000` | `HIGH,HIGH,HIGH,HIGH` | `HIGH,HIGH,HIGH,HIGH` | `HIGH,HIGH,HIGH,HIGH` |
| 2 | 0 | `0000` | `HIGH,LOW,HIGH,HIGH` | `HIGH,LOW,HIGH,HIGH` | `HIGH,HIGH,HIGH,HIGH` |
| 3 | 0 | `0000` | `LOW,HIGH,HIGH,HIGH` | `LOW,HIGH,HIGH,HIGH` | `HIGH,HIGH,HIGH,HIGH` |
| 4 | 0 | `0000` | `LOW,LOW,HIGH,HIGH` | `LOW,LOW,HIGH,HIGH` | `HIGH,HIGH,HIGH,HIGH` |
| 5 | 0 | `0000` | `LOW,LOW,LOW,HIGH` | `LOW,LOW,LOW,HIGH` | `HIGH,HIGH,HIGH,HIGH` |

Claim boundary: one continuous five-conversion physical DAC/comparator transient; fixed-decision diagnostic when enabled; not closed-loop qualification, PVT, mismatch/noise, extracted-layout, board, or silicon acceptance

## Interpretation

This table classifies saved probe voltages at the conversion boundary. It does not prove timing margin, PVT robustness, mismatch tolerance, energy, or analog authorization.
