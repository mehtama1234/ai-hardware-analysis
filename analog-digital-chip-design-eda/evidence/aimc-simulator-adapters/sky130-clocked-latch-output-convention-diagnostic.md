# Sky130 Clocked Latch Output Convention Diagnostic

- status: `clocked_latch_output_convention_inversion_confirmed`
- case count: `6`
- outn-minus-outp contract match count: `0`
- outp-minus-outn contract match count: `6`
- inferred clocked latch output contract: `digital_bit_positive_when_outp_exceeds_outn`
- requires new ngspice run: `False`
- uses existing same-run measurements: `True`
- uses sampled nodes: `False`
- accepted post-layout written: `False`

## First Principle

A latch has two analog rails. A digital bit is created only after we name which rail means the positive decision.

The clocked timing run did not show a weak latch. The rail separation is large in every case. The failure is that the report called `outn - outp` the signed output, while the measured rails match the source polarity contract when the digital output is defined as `outp - outn`.

That fixes the next work item. Before adding sampled-node kickback, the converter contract must name the latch output bit explicitly: positive source difference means `outp` high and `outn` low.

## Convention Check

| case | clock ns | expected sign | outn-outp matches | outp-outn matches |
|---|---:|---:|---:|---:|
| `negative_target_edge_clk_0.2ns` | `0.2` | `-1` | `False` | `True` |
| `negative_target_edge_clk_0.6ns` | `0.6` | `-1` | `False` | `True` |
| `negative_target_edge_clk_1.0ns` | `1.0` | `-1` | `False` | `True` |
| `positive_target_edge_clk_0.2ns` | `0.2` | `1` | `False` | `True` |
| `positive_target_edge_clk_0.6ns` | `0.6` | `1` | `False` | `True` |
| `positive_target_edge_clk_1.0ns` | `1.0` | `1` | `False` | `True` |

## Boundary

does not change the circuit, prove sampled-node kickback, prove coupled preamp/latch loading, prove SAR bit cycling, and does not create accepted post-layout converter evidence
