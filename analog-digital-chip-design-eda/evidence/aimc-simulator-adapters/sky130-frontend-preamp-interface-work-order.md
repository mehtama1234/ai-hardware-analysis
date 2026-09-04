# Sky130 Frontend Preamp Interface Work Order

- status: `frontend_preamp_interface_work_order_ready_not_design_proof`
- candidate count: `3`
- current attached transfer ratio: `0.041830`
- required transfer ratio: `0.399174`
- required transfer improvement x: `9.543`
- average useful sample-to-sense capacitance fF: `0.800000`
- average sense total capacitance fF: `3.292970`
- target total cap if useful fixed fF: `2.004136`
- target useful coupling if total fixed fF: `1.314469`
- accepted post-layout written: `False`

## First Principle

The preamp cannot repair a voltage that was lost before the gate. The interface must first deliver enough voltage to the preamp input. After that, gain, latch timing, and SAR logic become meaningful tests.

A useful next circuit change must therefore name which physical quantity it changes: less wasted capacitance, more useful coupling, or lower input capacitance between frontend and preamp.

## Candidate Work

| candidate | physical move | numeric target | acceptance test |
|---|---|---|---|
| `lower_waste_sense_node` | keep about the same useful sample-to-sense coupling but remove non-signal capacitance from sense_p and sense_n | average sense-node capacitance <= 2.004 fF with useful coupling near 0.800 fF | attached-preamp run measures both signs, preserves sign, and reaches at least 0.5 mV output difference |
| `stronger_useful_coupling` | increase intentional sample_p-to-sense_p and sample_n-to-sense_n coupling without growing every other sense-node capacitance at the same rate | useful sample-to-sense coupling >= 1.314 fF while average sense-node capacitance stays near 3.293 fF | frontend-only transfer reaches the required ratio, then attached-preamp output reaches margin |
| `low_input_capacitance_isolation` | insert an isolation device or prebuffer whose input capacitance is materially smaller than the direct preamp gate load | attached sense voltage should be within 2x of the standalone measured-source voltage before gain is judged | measured attached sense loss is reduced from about 10.47x to 2x or better, then preamp margin is retested |

## Next Artifact

- script: `run_sky130_frontend_preamp_interface_candidate.py`
- page: `docs/research/sky130-frontend-preamp-interface-candidate.md`

## Refused Claim

does not edit layout, run a new redesigned circuit, prove latch resolution, prove SAR conversion, or write accepted converter evidence
