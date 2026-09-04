# Sky130 Differential Matching Requirement

- status: `sky130_differential_matching_requirement_defined_not_converter_proof`
- best measured hold error V: `6.300000000e-05`
- best measured margin x: `3.488`
- reference uncancelled differential error V: `2.086600000e-03`
- 12-bit half LSB V: `2.197265625e-04`
- max allowed differential mismatch mV: `0.2197`
- allowed mismatch percent of reference error: `10.53`
- required common rejection percent: `89.47`
- control mismatch case over limit x: `1.365`
- candidate post-layout written: `False`
- accepted post-layout written: `False`

## First Principle

Differential sampling helps only when the unwanted charge is almost the same on both sides. The shared part disappears from the decision voltage. The unmatched part remains.

The uncancelled differential fixture moves by millivolts. The 12-bit limit is about 0.2197 mV. The new differential dummy case is below that line in one measured mid-input case, which means the next question is no longer only size. It is whether the cancellation survives input range, device mismatch, noise, and layout parasitics.

Said another way, if the physical circuit produces a disturbance about as large as the uncancelled differential fixture, the two sides must leave less than the half-LSB line in the decision voltage. The passing dummy row has margin in nominal simulation, but mismatch can spend that margin quickly.

## Numeric Target

| quantity | value | meaning |
|---|---:|---|
| uncancelled differential movement | `2.0866 mV` | size of the disturbance before dummy cancellation |
| best measured dummy-cancelled movement | `0.0630 mV` | current best nominal decision-voltage movement |
| max allowed remaining mismatch | `0.2197 mV` | largest differential error allowed by the 12-bit line |
| best measured margin | `3.4877` | half-LSB line divided by the best measured movement |
| allowed mismatch fraction | `0.1053` | remaining mismatch divided by uncancelled movement |
| required common rejection | `0.8947` | common movement that must disappear from the decision |

## Design Consequence

The next transistor fixture should not only report node movement. It must report matched movement. If both held nodes move by millivolts but their difference moves by less than 0.2197 mV, differential sampling is doing the job. If their difference moves more than that, the circuit still fails even if it looks symmetric on paper.

## Refused Claim

does not prove Sky130 transistor matching, comparator offset, noise, SAR conversion, extracted layout, DRC/LVS signoff, or accepted replacement economics
