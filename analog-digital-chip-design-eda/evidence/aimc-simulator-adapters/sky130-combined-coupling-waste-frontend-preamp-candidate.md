# Sky130 Combined Coupling/Waste Frontend Preamp Candidate

- status: `combined_coupling_waste_frontend_preamp_candidate_failed_scaled_rc_margin`
- scaled nonuseful sense cap count: `8`
- nonuseful sense cap scale: `0.483013`
- source average sense capacitance fF: `3.292970`
- candidate average sense capacitance fF: `2.004136`
- target average sense capacitance fF: `2.004136`
- measured case count: `2`
- sign pass count: `2`
- output margin pass count: `0`
- minimum abs preamp output diff V: `6.950000000e-05`
- output margin target V: `5.000000000e-04`
- accepted post-layout written: `False`

## First Principle

This experiment asks one narrow question: if useful sample-to-sense coupling rises to its target and wasted sense-node capacitance falls to its target in the same scaled extracted-RC candidate, does the same preamp finally receive enough voltage?

Charge is fixed by the sample event. Voltage is charge divided by capacitance. More useful coupling moves more sampled charge onto the sense node. Less wasted capacitance divides that charge over a smaller load. The useful voltage is the result of both terms together.

## Result

| input diff mV | sense diff V | preamp output diff V | transfer ratio | sign preserved | margin pass |
|---:|---:|---:|---:|---|---|
| `-0.152971` | `-9.000000000e-06` | `-6.950000000e-05` | `0.058824` | `True` | `False` |
| `0.152971` | `9.000000000e-06` | `7.010000000e-05` | `0.058824` | `True` | `False` |

## Next Gate

The combined scaled-RC candidate still misses margin. The next required work is active low-input-capacitance isolation before the preamp.

## Refused Claim

does not prove a drawn layout, DRC/LVS, latch decision, SAR conversion, post-layout converter energy, or accepted converter evidence
