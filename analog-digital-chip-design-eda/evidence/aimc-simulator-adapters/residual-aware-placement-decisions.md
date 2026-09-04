# Residual-Aware Placement Decisions

This report joins structural placement with calibrated simulator evidence.

The backend placement says which operators are shaped like analog work. The calibrated residual bridge says whether the available simulator evidence is strong enough to request analog service today.

## Source Evidence

- placement: `labs/analog/analog-in-memory-foundation-model-hardware/measurements/backend-hardware-placement.json`
- calibrated bridge: `evidence/aimc-simulator-adapters/calibrated-residual-governor-bridge.json`
- accepted tool: `crosssim`
- accepted source: `deep_transformer_mlp_stack`
- accepted target: `deep-transformer-mlp-stack.onnx 12 fixed-weight MatMuls`
- calibration profile: `crosssim-held-out-affine-deep-transformer-mlp-stack-v0`
- residual q8: `0`
- source matching policy: `fixed_weight_matmul_family_match`
- placement source hint: `deep_transformer_mlp_stack`
- selected source reason: Backend operators are dense fixed-weight MatMul rows, so the calibrated deep transformer-MLP stack is the closest available fixture. The one-block transformer-MLP source remains the next fallback, and attention projection evidence remains a general fixed-weight projection fallback.

## Decisions

| operator | kind | structural placement | structural candidate | residual-aware decision | residual q8 | evidence source | evidence tool |
| --- | --- | --- | ---: | --- | ---: | --- | --- |
| dense1.matmul | MatMul | analog | 1 | analog_allowed | 0 | deep_transformer_mlp_stack | crosssim |
| dense1.bias | Add | digital | 0 | digital_fallback | 0 | not_used | not_used |
| dense1.relu | Relu | digital | 0 | digital_fallback | 0 | not_used | not_used |
| dense2.matmul | MatMul | analog | 1 | analog_allowed | 0 | deep_transformer_mlp_stack | crosssim |
| dense2.bias | Add | digital | 0 | digital_fallback | 0 | not_used | not_used |

## First-Principles Reading

Placement and acceptance are different decisions.

A matrix multiply is a good structural match for an analog array because fixed weights can sit as conductances and input values can arrive as row voltages. That only says the operator has the right shape. It does not say the current analog path is accurate enough.

The residual-aware decision adds the missing second step. It asks whether a calibrated simulator payload passed the strict evidence rule, then asks whether that payload is the right kind of source for the backend operator. In the current local run, the backend rows are dense MatMul rows, so the transformer-MLP source is selected ahead of the attention source even though both CrossSim rows pass. Non-MatMul rows stay digital because calibration evidence for a matrix multiply should not be used to justify bias, activation, softmax, dynamic attention work, or residual adds.

## Refused Claim

This does not prove analog macro layout, silicon calibration, board latency, board power, analog softmax, pretrained model accuracy, signoff, or tapeout readiness.
