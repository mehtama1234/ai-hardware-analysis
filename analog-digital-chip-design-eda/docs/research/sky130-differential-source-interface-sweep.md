# Sky130 Differential Source Interface Sweep

This review page tests whether the nominal differential DAC can be connected
to a full-range external input while keeping the Sky130 sampled nodes in a
legal common-mode range.

| input mapping | calibration | conversion comparisons | correct conversions | result |
| --- | --- | --- | --- | --- |
| `0.8x`, offset `0.18 V` | `16/16` | `20/20` | `2/5` | SAR accuracy rejected |
| `0.9x`, offset `0.09 V` | `16/16` | `12/14` | `1/5` | low-end convergence rejected |
| `1.0x`, offset `0.03 V` | endpoint probe | `3/3` | n/a | code 8 plate range rejected |
| `0.667x`, offset `0.30 V` plus ideal rail diode | clamp probe | `1/1` | n/a | transfer loading rejected |

## Decision

Source mapping alone does not close the physical converter. The stable `0.8x`
mapping completes all attempted comparisons but misses three representative
codes. Higher scaling worsens low-end convergence, while endpoint-fitted unity
scaling drives a plate below ground. The next revision must add physical
headroom control during acquisition and redistribution before the SAR gate can
pass.

An ideal rail-diode diagnostic held the low plate near ground, but introduced a
large differential transfer shift and is not considered a physical-cell
solution.

The nominal DAC candidate remains documented at
`sky130-differential-dac-full-scale-candidate.html`; this page is the follow-up
interface qualification.
