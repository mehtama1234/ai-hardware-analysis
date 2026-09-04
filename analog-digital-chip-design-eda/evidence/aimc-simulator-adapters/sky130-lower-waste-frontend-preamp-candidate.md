# Sky130 Lower-Waste Frontend Preamp Candidate

- status: `lower_waste_frontend_preamp_candidate_failed_scaled_rc_margin`
- scaled nonuseful sense cap count: `8`
- nonuseful sense cap scale: `0.483013`
- source average sense capacitance fF: `3.292970`
- candidate average sense capacitance fF: `2.004136`
- target average sense capacitance fF: `2.004136`
- measured case count: `2`
- sign pass count: `2`
- output margin pass count: `0`
- minimum abs preamp output diff V: `5.040000000e-05`
- output margin target V: `5.000000000e-04`
- accepted post-layout written: `False`

## First Principle

This experiment asks one narrow question: if the useful sample-to-sense capacitors stay the same and only the wasted sense-node capacitance is reduced to the budget target, does the same preamp finally receive enough voltage?

Charge is fixed by the sample event. Voltage is charge divided by capacitance. Reducing capacitance that does not carry signal should raise the sense voltage without changing the intended coupling path.

## Result

| input diff mV | sense diff V | preamp output diff V | transfer ratio | sign preserved | margin pass |
|---:|---:|---:|---:|---|---|
| `-0.152971` | `-5.900000000e-06` | `-5.040000000e-05` | `0.038562` | `True` | `False` |
| `0.152971` | `5.700000000e-06` | `5.150000000e-05` | `0.037255` | `True` | `False` |

## Next Gate

The scaled-RC candidate still misses margin. The next required work is to combine lower wasted capacitance with stronger useful coupling or move to an isolation stage.

## Refused Claim

does not prove a drawn layout, DRC/LVS, latch decision, SAR conversion, post-layout converter energy, or accepted converter evidence
