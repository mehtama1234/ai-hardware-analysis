# Sky130 Capacitive Isolation Post-Layout Handoff

- status: `confirmed_schematic_candidate_waiting_for_extracted_layout`
- source confirmation: `evidence/aimc-simulator-adapters/sky130-capacitive-isolation-both-polarity-confirm.json`
- all schematic cases pass: `True`
- confirmed coupling caps fF: `0.1, 0.2`
- worst schematic kickback V: `0.0002021999999999302`
- hard kickback limit V: `0.0002197265625`
- physical cell gate ready: `False`
- post-layout ready to replace break-even: `False`
- accepted ready now: `False`
- candidate post-layout written: `False`
- accepted post-layout written: `False`

## First Principle

The both-polarity run proves a schematic behavior: a tiny isolation capacitor lets the latch read either sign while keeping sampled-node kickback under the half-LSB line. That is useful, but it is still not a physical converter.

Layout changes the object being measured. Wires add capacitance and resistance. Device placement changes matching. Clock routing changes charge injection. The isolation capacitor itself must become a drawn or extracted object, not only a value in a generated deck.

So the next gate is not another wording pass. It is a handoff from a confirmed schematic candidate to named extracted objects.

## Required Layout Objects

- capacitive-isolation comparator schematic or extracted subcell naming the coupling capacitor value
- extracted comparator-plus-sample-node netlist including latch input gates, isolation capacitors, sample capacitors, and clock devices
- Sky130 model and corner file path used by the rerun
- post-layout both-polarity kickback rerun using the same target input edge
- post-layout offset/noise stress record or explicit statement that the result is still kickback-only
- DRC/LVS report for the comparator sample front end if it is claimed as a physical candidate
- same-run break-even rerun showing whether the converter still beats fallback after extracted capacitance and timing are included

## Refused Claim

does not create extracted layout, does not prove comparator offset or noise, does not write candidate post-layout evidence, and does not write accepted converter evidence
