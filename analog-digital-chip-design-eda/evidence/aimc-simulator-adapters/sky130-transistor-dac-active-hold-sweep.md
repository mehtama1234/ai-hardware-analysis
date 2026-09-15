# Sky130 Transistor DAC Active-Hold Sweep

- status: `active_hold_sweep_diagnostic_physical_qualification_open`
- receipts: `6` measured of `7`

| source | code | hold ns | width um | length um | top error V | legal | status |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `local-fourbit-code14-79ns-50ps-activehold35w4.json` | 14 | 3.5 | 4.0 | None | 0.015006000000000075 | False | `transistor_switched_capacitor_dac_incomplete_or_half_lsb_or_legal_range_failed` |
| `local-fourbit-code14-79ns-50ps-activehold45w1.json` | 14 | 4.5 | 1.0 | None | 0.015193000000000012 | False | `transistor_switched_capacitor_dac_incomplete_or_half_lsb_or_legal_range_failed` |
| `local-fourbit-code14-79ns-50ps-activehold45w4.json` | 14 | 4.5 | 4.0 | None | 0.0146980000000001 | False | `transistor_switched_capacitor_dac_incomplete_or_half_lsb_or_legal_range_failed` |
| `local-fourbit-code14-79ns-50ps-activehold65w4.json` | 14 | 6.5 | 4.0 | None | 0.014739000000000058 | False | `transistor_switched_capacitor_dac_incomplete_or_half_lsb_or_legal_range_failed` |
| `local-fourbit-code14-79ns-50ps-activehold65w16.json` | 14 | 6.5 | 16.0 | None | 0.013662000000000063 | False | `transistor_switched_capacitor_dac_incomplete_or_half_lsb_or_legal_range_failed` |
| `local-fourbit-code14-79ns-50ps-activehold65w16l1.json` | timeout | 6.5 | 16.0 | 1.0 | None | False | `transistor_switched_capacitor_dac_incomplete_or_half_lsb_or_legal_range_failed` |
| `local-fourbit-code13-79ns-50ps-activehold45w4.json` | 13 | 4.5 | 4.0 | None | 0.003983000000000292 | False | `transistor_switched_capacitor_dac_incomplete_or_half_lsb_or_legal_range_failed` |

The sweep is diagnostic only. A measured code subset cannot become a converter profile, and a top-plate half-LSB result cannot override illegal internal nodes or numerical timeouts.

## Next required change

new bottom-plate switch cell with independent transfer and hold paths, then full 16-code/PVT/mismatch campaign

## Refused claim

does not establish converter qualification, SAR correctness, workload accuracy, energy advantage, silicon yield, or analog authorization
