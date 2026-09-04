# Sky130 Long-Acquisition Coupled Probe

- status: `long_acquisition_coupled_probe_characterized`
- codes: `7, 15`
- source switch sizing: `32 um NMOS / 64 um PMOS`
- source acquisition ends: `4.0 ns`
- bottom-plate transition: `5.0 ns`
- comparator sampling: `9.1-9.6 ns`
- preamp enabled: `9.7 ns`
- latch: `11.7 ns`

This probe carries the larger source switch and longer acquisition phase from the isolated `8 pF` loading test into the coupled physical DAC/comparator transient. It is a timing and interface probe, not a complete converter result.

| code | DAC top after V | DAC-reference diff V | preamp diff V | output diff V | correct polarity |
| ---: | ---: | ---: | ---: | ---: | --- |
| 7 | 1.899735 | 0.399735 | 0.487778 | -1.390706 | True |
| 15 | 2.396624 | 0.896624 | 0.752294 | -1.395830 | True |

## Refused Claim

does not prove all DAC codes, full SAR accuracy, calibration, mismatch/noise yield, PVT behavior, extracted layout, board behavior, or silicon
