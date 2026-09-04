# Model Impact Governor Requests

This report translates the measured transformer-impact experiment into the compact evidence fields that the digital governor can consume. It is the bridge between model behavior and hardware control.

The object is one proposed analog service request. The request is no longer described only by circuit residual. It also carries whether attention selection or token choice became sensitive in the measured transformer experiment.

## Request Table

| policy | candidate | residual q8 | attention flip q8 | token flip q8 | sensitivity q8 | cumulative q8 | governor decision | action | governor reason | next q8 | model decision | interpretation |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | --- | --- |
| all_digital_reference | 0 | 0 | 0 | 0 | 96 | 0 | 0 | 0 | not_analog_candidate | 0 | digital_reference | reference path; no analog service is requested |
| measured_fixed_projection_tile | 1 | 6 | 32 | 45 | 96 | 6 | 1 | 0 | analog_within_budget | 12 | analog_path | measured tile damage remains small enough for this fixed-projection use |
| measured_projection_stressed_tile | 1 | 40 | 45 | 51 | 224 | 14 | 0 | 0 | sensitive_path_needs_digital | 14 | digital_fallback | model-level sensitivity is high enough that a moderate residual should not be spent |
| measured_attention_scores_analog | 1 | 40 | 45 | 32 | 208 | 10 | 0 | 0 | sensitive_path_needs_digital | 10 | digital_fallback | model-level sensitivity is high enough that a moderate residual should not be spent |
| measured_logits_analog | 1 | 40 | 38 | 51 | 224 | 12 | 0 | 0 | sensitive_path_needs_digital | 12 | digital_fallback | model-level sensitivity is high enough that a moderate residual should not be spent |
| backend_dense1.matmul | 1 | 6 | 0 | 0 | 96 | 6 | 1 | 0 | analog_within_budget | 12 | analog_path | backend graph operator dense1.matmul enters the hardware lab as analog with projection-tolerant sensitivity |
| backend_dense1.bias | 0 | 0 | 0 | 0 | 128 | 0 | 0 | 0 | not_analog_candidate | 0 | digital_reference | backend graph operator dense1.bias enters the hardware lab as digital with digital-support sensitivity |
| backend_dense1.relu | 0 | 0 | 0 | 0 | 128 | 0 | 0 | 0 | not_analog_candidate | 0 | digital_reference | backend graph operator dense1.relu enters the hardware lab as digital with digital-support sensitivity |
| backend_dense2.matmul | 1 | 6 | 0 | 0 | 96 | 6 | 1 | 0 | analog_within_budget | 12 | analog_path | backend graph operator dense2.matmul enters the hardware lab as analog with projection-tolerant sensitivity |
| backend_dense2.bias | 0 | 0 | 0 | 0 | 128 | 0 | 0 | 0 | not_analog_candidate | 0 | digital_reference | backend graph operator dense2.bias enters the hardware lab as digital with digital-support sensitivity |

## First-Principles Reading

A circuit residual says how far the tile output moved from the ideal dot product. A model-impact row says what that movement did after attention, residual addition, MLP, logits, and token choice. The governor needs both ideas compressed into hardware-sized fields.

`model_residual_q8` is the state movement. `attention_flip_q8` and `token_flip_q8` record whether the error crossed a selection boundary. `sensitivity_q8` is raised when the operation touches attention scores or logits, because those are ranking decisions rather than ordinary vector values.

The fixed-projection policy remains analog because its state error is modest and the sensitive decisions stay digital. The stressed, attention-score, and logits policies are refused or routed to repair because the same measured tile residual has reached a part of the transformer where small movement changes a choice.

When `backend-hardware-placement-governor-input.csv` exists, backend-derived ONNX placement rows are appended to this same request table. That connects the restored workbench model graph to the hardware-lab governor input instead of leaving the lab with only fixed local transformer policies.

This is the hardware lesson. The digital governor cannot see a transformer. It sees small fields. Those fields must be chosen so they preserve the model-level reason for accepting or refusing analog work.
