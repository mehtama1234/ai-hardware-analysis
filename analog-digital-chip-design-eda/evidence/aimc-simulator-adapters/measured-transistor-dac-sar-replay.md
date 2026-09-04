# Measured Transistor DAC SAR Replay

- status: `measured_dac_transfer_replay_characterized_not_closed_loop_spice_proof`
- measured thresholds: `16` of `16`
- correct quantization regions: `10` of `16`
- wrong quantization regions: `6`

## What This Means

This replay takes the measured 16-code top-plate transfer and puts it inside the digital SAR decision rule. It is deliberately separate from a transistor transient: the measured transfer is real, but the comparator is represented by an exact voltage comparison. That makes the source of any wrong code visible instead of hiding it behind a new idealized circuit.

The input tests use the center of each ideal quantization region. A correct converter should return the region's expected code. A wrong result means the measured DAC threshold has moved far enough that the current transfer curve changes the digital answer even before comparator noise and mismatch are added.

## Results

| expected code | input V | replayed code | correct |
| ---: | ---: | ---: | --- |
| 0 | 0.956250 | 0 | True |
| 1 | 1.068750 | 1 | True |
| 2 | 1.181250 | 2 | True |
| 3 | 1.293750 | 3 | True |
| 4 | 1.406250 | 4 | True |
| 5 | 1.518750 | 5 | True |
| 6 | 1.631250 | 6 | True |
| 7 | 1.743750 | 7 | True |
| 8 | 1.856250 | 7 | False |
| 9 | 1.968750 | 8 | False |
| 10 | 2.081250 | 9 | False |
| 11 | 2.193750 | 10 | False |
| 12 | 2.306250 | 12 | True |
| 13 | 2.418750 | 15 | False |
| 14 | 2.531250 | 15 | False |
| 15 | 2.587500 | 15 | True |

## Refused Claim

does not prove a same-deck comparator-DAC transient, comparator noise, mismatch yield, PVT SAR accuracy, extracted layout, board behavior, or silicon
