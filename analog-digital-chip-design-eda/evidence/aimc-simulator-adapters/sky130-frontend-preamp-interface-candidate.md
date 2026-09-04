# Sky130 Frontend Preamp Interface Candidate

- status: `frontend_preamp_interface_candidate_ranked_not_yet_layout_proven`
- candidate count: `3`
- recommended first candidate: `lower_waste_sense_node`
- current attached transfer ratio: `0.041830`
- required transfer ratio: `0.399174`
- required transfer improvement x: `9.543`
- current best output margin V: `5.650000000e-05`
- output margin target V: `5.000000000e-04`
- best measured sense-to-preamp gain V/V: `8.188406`
- accepted post-layout written: `False`

## First Principle

The interface has one job: move enough of the sampled voltage to the preamp input. A candidate is better when it asks the layout to change a smaller physical quantity before the same preamp is tested again.

The current attached run is not short by a vague amount. It needs about 9.54x more voltage transfer, or the preamp output stays around 56.5 uV instead of the 0.5 mV margin target.

## Candidate Ranking

| rank | candidate | measured object | current | target | change needed x | passes now | next measurement |
|---:|---|---|---:|---:|---:|---|---|
| 1 | `lower_waste_sense_node` | `first_order_capacitance_budget` | `3.292970` | `2.004136` | `1.643` | `False` | edit extracted frontend geometry, re-extract sense_p/sense_n total capacitance, then rerun attached-preamp transient |
| 2 | `stronger_useful_coupling` | `first_order_capacitance_budget` | `0.800000` | `1.314469` | `1.643` | `False` | increase intentional sample-to-sense coupling, re-extract useful capacitance, then rerun frontend-only transfer and attached-preamp transient |
| 3 | `low_input_capacitance_isolation` | `loss_budget` | `9.542764` | `2.000000` | `4.771` | `False` | insert a low-input-capacitance isolation stage and prove attached sense loss is 2x or better before judging preamp gain |

## Reading

The smallest first move is not automatically the final design. It is the cheapest honest next test. If useful coupling or wasted capacitance can move by about 1.64x after extraction, the attached-preamp margin should be tested again. If neither physical capacitance move is practical, the isolation path becomes the circuit fork.

## Refused Claim

does not edit layout, re-extract a redesigned frontend, prove preamp margin, prove latch/SAR behavior, or write accepted converter evidence
