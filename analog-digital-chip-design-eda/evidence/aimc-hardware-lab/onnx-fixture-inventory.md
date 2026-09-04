# ONNX Fixture Inventory

This file is generated from the actual ONNX sample files in the restored backend.

It answers a narrow question: what model slices do we already have, and which one is the strongest local candidate before a real uploaded model slice exists?

## Current Selection

- selected fixture: `deep-transformer-mlp-stack.onnx`
- fixed-weight MatMul rows: `12`
- reason: largest existing fixed-weight MatMul family and current residual-aware placement source

## Inventory

| model | nodes | initializers | parameters | MatMul | fixed-weight MatMul | status |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| attention-block.onnx | 9 | 5 | 257 | 6 | 4 | usable_larger_fixture |
| deep-transformer-mlp-stack.onnx | 36 | 24 | 22080 | 12 | 12 | selected_current_best_fixture |
| projection-stack.onnx | 11 | 8 | 724 | 4 | 4 | usable_larger_fixture |
| tiny-mlp.onnx | 5 | 4 | 23 | 2 | 2 | small_fixture |
| transformer-mlp-block.onnx | 12 | 8 | 1888 | 4 | 4 | usable_larger_fixture |

## First-Principles Reading

The useful analog object is not an ONNX file by itself. The useful object is a fixed matrix multiply whose weights are known and reused.

A larger slice is stronger when it has more fixed-weight MatMul rows, real initializer tensors, and digital support operators around those rows. That tests whether analog placement still makes sense when MatMul is only part of a graph, not the whole graph.

The current best local fixture is still a fixture. It is larger and model-shaped, but it is not a pretrained foundation-model slice and not a user-uploaded deployment model.

## Refused Claim

This inventory does not prove full model accuracy, measured latency, measured energy, calibrated silicon, analog macro signoff, or production readiness.
