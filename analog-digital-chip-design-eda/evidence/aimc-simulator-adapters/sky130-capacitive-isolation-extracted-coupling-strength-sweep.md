# Sky130 Capacitive Isolation Extracted Coupling-Strength Sweep

- status: `no_added_coupling_strength_preserves_both_signs`
- tested added capacitor fF: `0.0, 0.09999999999999999, 0.19999999999999998, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0, 200.0`
- first passing added capacitor fF: `None`
- row count: `24`

## First Principle

The extracted frontend has fixed capacitance from latch gates to clock, supply, ground, and substrate. A tiny intended sample-to-gate signal can lose if those fixed paths move the latch inputs more than the sampled difference does.

This sweep keeps the extracted RC cell in the path and adds a controlled symmetric sample-to-gate capacitor. It asks how much stronger the intended differential coupling must be before both signs reach the latch-gate nodes correctly.

It uses the measured normal-mapping extracted-RC sign error as the baseline, then applies the added capacitor through the extracted latch-gate capacitance totals. The added capacitors are a design diagnostic, not a physical layout edit.

## Results

| added cap fF | input diff mV | baseline gate diff V | added coupling delta V | gate diff after V | expected sign | measured sign | sign preserved |
|---:|---:|---:|---:|---:|---:|---:|---|
| `0.000` | `-0.152971` | `1.103900000e-02` | `-0.000000000e+00` | `1.103900000e-02` | `-1` | `1` | `False` |
| `0.000` | `0.152971` | `1.109300000e-02` | `0.000000000e+00` | `1.109300000e-02` | `1` | `1` | `True` |
| `0.100` | `-0.152971` | `1.103900000e-02` | `-7.921656425e-06` | `1.103107834e-02` | `-1` | `1` | `False` |
| `0.100` | `0.152971` | `1.109300000e-02` | `7.921656425e-06` | `1.110092166e-02` | `1` | `1` | `True` |
| `0.200` | `-0.152971` | `1.103900000e-02` | `-1.506325409e-05` | `1.102393675e-02` | `-1` | `1` | `False` |
| `0.200` | `0.152971` | `1.109300000e-02` | `1.506325409e-05` | `1.110806325e-02` | `1` | `1` | `True` |
| `0.500` | `-0.152971` | `1.103900000e-02` | `-3.281161423e-05` | `1.100618839e-02` | `-1` | `1` | `False` |
| `0.500` | `0.152971` | `1.109300000e-02` | `3.281161423e-05` | `1.112581161e-02` | `1` | `1` | `True` |
| `1.000` | `-0.152971` | `1.103900000e-02` | `-5.403328528e-05` | `1.098496671e-02` | `-1` | `1` | `False` |
| `1.000` | `0.152971` | `1.109300000e-02` | `5.403328528e-05` | `1.114703329e-02` | `1` | `1` | `True` |
| `2.000` | `-0.152971` | `1.103900000e-02` | `-7.985843409e-05` | `1.095914157e-02` | `-1` | `1` | `False` |
| `2.000` | `0.152971` | `1.109300000e-02` | `7.985843409e-05` | `1.117285843e-02` | `1` | `1` | `True` |
| `5.000` | `-0.152971` | `1.103900000e-02` | `-1.119672016e-04` | `1.092703280e-02` | `-1` | `1` | `False` |
| `5.000` | `0.152971` | `1.109300000e-02` | `1.119672016e-04` | `1.120496720e-02` | `1` | `1` | `True` |
| `10.000` | `-0.152971` | `1.103900000e-02` | `-1.292959242e-04` | `1.090970408e-02` | `-1` | `1` | `False` |
| `10.000` | `0.152971` | `1.109300000e-02` | `1.292959242e-04` | `1.122229592e-02` | `1` | `1` | `True` |
| `20.000` | `-0.152971` | `1.103900000e-02` | `-1.401404163e-04` | `1.089885958e-02` | `-1` | `1` | `False` |
| `20.000` | `0.152971` | `1.109300000e-02` | `1.401404163e-04` | `1.123314042e-02` | `1` | `1` | `True` |
| `50.000` | `-0.152971` | `1.103900000e-02` | `-1.475665652e-04` | `1.089143343e-02` | `-1` | `1` | `False` |
| `50.000` | `0.152971` | `1.109300000e-02` | `1.475665652e-04` | `1.124056657e-02` | `1` | `1` | `True` |
| `100.000` | `-0.152971` | `1.103900000e-02` | `-1.502199899e-04` | `1.088878001e-02` | `-1` | `1` | `False` |
| `100.000` | `0.152971` | `1.109300000e-02` | `1.502199899e-04` | `1.124321999e-02` | `1` | `1` | `True` |
| `200.000` | `-0.152971` | `1.103900000e-02` | `-1.515828107e-04` | `1.088741719e-02` | `-1` | `1` | `False` |
| `200.000` | `0.152971` | `1.109300000e-02` | `1.515828107e-04` | `1.124458281e-02` | `1` | `1` | `True` |

## Refused Claim

does not modify the physical layout, does not prove latch resolution, does not prove noise, does not run DRC/LVS, and does not write accepted evidence
