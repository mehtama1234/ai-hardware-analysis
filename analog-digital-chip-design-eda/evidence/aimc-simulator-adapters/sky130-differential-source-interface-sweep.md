# Sky130 Differential Source Interface Sweep

- status: `rejected_endpoint_headroom_and_sar_accuracy`
- internal common mode: `0.9 V`
- converter topology: `break-before-make differential DAC with 4x top-plate dummy capacitance`

| input scale | input offset | calibration | comparisons | correct conversions | result |
| ---: | ---: | ---: | ---: | ---: | --- |
| 0.8 | 0.18 V | 16/16 | 20/20 | 2/5 | SAR accuracy rejected |
| 0.9 | 0.09 V | 16/16 | 12/14 | 1/5 | low-end convergence rejected |
| 1.0 | 0.03 V | n/a | 3/3 endpoint probes | n/a | code 8 plate range rejected |
| 0.667 | 0.30 V | n/a | 1/1 clamp probe | n/a | ideal clamp loads transfer and is rejected |

## Conclusion

Changing the source mapping does not close the physical converter. The stable
`0.8x` interface completes calibration and all attempted comparisons but
returns only `2/5` representative conversions. Increasing the scale worsens
low-end convergence. Endpoint-fitted unity scaling measures the low-end trials
but drives a plate below ground at code 8. The next cell revision must provide
headroom control during source acquisition and redistribution; threshold-map
adjustments alone are insufficient. An ideal diode-clamp diagnostic held the
low plate to approximately ground, but caused a large differential transfer
shift and still failed the strict numeric legal-range check; it is not promoted
to the physical cell.
