# CrossSim Layout-Risk Adapter

This report separates model residual evidence from physical layout risk.

CrossSim can say whether the fixed-weight MatMul output stayed close to the digital reference under the current simulator assumptions. It does not prove that a real macro layout has acceptable wire drop, converter range, bit slicing, column current, extraction, DRC, LVS, or silicon behavior.

## Source Evidence

- residual-aware placement: `evidence/aimc-simulator-adapters/residual-aware-placement-decisions.json`
- tile operating point: `labs/analog/analog-in-memory-foundation-model-hardware/measurements/tile-operating-point.csv`
- accepted source: `deep_transformer_mlp_stack`
- accepted tool: `crosssim`
- source matching policy: `fixed_weight_matmul_family_match`

## Layout-Risk Rows

| operator | array | ADC | DAC | bit slices | row wire ohm | row-drop loss % | column current range uA | risk |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| dense1.matmul | 4x4 | 6 | 4 | 2 | 100.0 | 6.932 | 3.2-41.6 | review |
| dense2.matmul | 4x2 | 6 | 4 | 2 | 100.0 | 6.932 | 1.6-20.8 | review |

## First-Principles Reading

An analog MatMul row is not one object. It is a chain.

A weight becomes conductance. An activation becomes a row voltage. Each cell turns voltage and conductance into current. The column sums current. The ADC turns that current back into a number. The digital side rescales, corrects, accumulates, and decides whether the result can stay in the model path.

The residual score checks the end of that chain. The layout-risk record checks the middle of the chain. A low residual is still incomplete if the assumed row wire, converter range, bit slicing, or column current would be unrealistic in layout.

## Refused Claim

This record does not prove analog macro layout, routed parasitic extraction, DRC, LVS, calibrated silicon, measured latency, measured energy, package reliability, production readiness, or tapeout readiness.
