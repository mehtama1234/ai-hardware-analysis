# Sky130 Capacitor-Scale Common-Mode All-Code Diagnostic

This is the all-code follow-up to the focused zero-common-mode diagnostic.

- topology: `PMOS-only bottom-plate connection to VDD`
- full-array capacitor scale: `8.0x`
- sampled input common-mode: `0.000 V`
- measured codes: `16/16`
- status: `all_code_candidate_rejected`

## Measurements

| code | DAC top before comparator (V) | correct polarity |
| ---: | ---: | --- |
| 0 | -0.000118 | True |
| 1 | 0.150868 | True |
| 2 | 0.216255 | True |
| 3 | 0.399560 | True |
| 4 | 0.276003 | True |
| 5 | 0.525551 | True |
| 6 | 0.827374 | True |
| 7 | 1.183938 | True |
| 8 | 0.328446 | True |
| 9 | 0.606279 | True |
| 10 | 0.890847 | True |
| 11 | 1.236163 | True |
| 12 | 1.075629 | True |
| 13 | 1.346174 | True |
| 14 | 1.597136 | True |
| 15 | 1.799298 | True |

Adjacent spacings (mV): 150.986, 65.387, 183.305, -123.557, 249.549, 301.823, 356.564, -855.492, 277.834, 284.568, 345.316, -160.534, 270.545, 250.962, 202.162

## Result

The scaled-array, zero-common-mode candidate is rejected by the all-code threshold test because the transfer is non-monotonic and leaves the legal supply range. The focused high-code result was not sufficient. SAR sequence, PVT, mismatch, noise, settling, energy, extraction, and model-level converter closure remain open.

## Claim Boundary

does not prove SAR accuracy, PVT/mismatch/noise yield, extracted layout, energy, board behavior, silicon, or model replacement readiness
