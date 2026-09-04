# Sky130 Frontend Preamp Capacitance Budget

- status: `frontend_preamp_interface_capacitance_budget_requires_less_waste_or_more_useful_coupling`
- average useful sample-to-sense capacitance fF: `0.800000`
- average sense total capacitance fF: `3.292970`
- current useful-over-total capacitance ratio: `0.242942`
- measured attached transfer ratio: `0.041830`
- required transfer ratio: `0.399174`
- required transfer improvement x: `9.543`
- required total cap if useful coupling fixed fF: `2.004136`
- required useful coupling if total cap fixed fF: `1.314469`
- total cap reduction needed x if useful fixed: `1.643`
- useful coupling increase needed x if total fixed: `1.643`
- accepted post-layout written: `False`

## First Principle

The frontend stores a small voltage as charge. The preamp input reads that charge through a node that also has capacitance to supply, ground, substrate, clocked regions, and internal metal. The voltage at the preamp input is the useful sample coupling divided by everything that must be moved.

That is why gain alone did not fix the attached preamp. The preamp can amplify the voltage it receives, but the extracted node is giving it only a small fraction of the sampled difference.

## Physical Budget

The extracted frontend has about `0.800 fF` of useful sample-to-sense coupling and about `3.293 fF` total sense-node capacitance. To reach the required transfer without changing preamp gain, either total sense capacitance must fall toward `2.004 fF`, or useful coupling must rise toward `1.314 fF` without dragging equal wasted capacitance with it.

## Design Choices

- reduce non-signal capacitance on sense_p and sense_n while keeping sample coupling
- increase intentional sample-to-sense coupling without increasing wasted capacitance at the same rate
- insert an isolation device whose input capacitance is much smaller than the direct preamp gate load
- measure the redesigned attached-preamp output before any latch or SAR claim

## Refused Claim

does not edit layout, prove a new circuit, prove latch resolution, prove SAR conversion, or write accepted converter evidence
