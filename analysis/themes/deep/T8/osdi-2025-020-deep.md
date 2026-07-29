# Training with Confidence: Catching Silent Errors in Deep Learning Training with Automated Proactive Checks

**Venue:** OSDI · **Subtheme:** Silent Error Detection via Automated Invariant Inference in Deep Learning

## What It Does

Silent errors during deep learning training—numerical instabilities (NaN gradients, overflow), silent data corruption (bit flips from cosmic rays or memory errors), incorrect hyperparameter application (wrong learning rate set in code), out-of-distribution bugs (model training on misaligned data)—produce models with degraded accuracy but leave no trace. Detection requires knowing which properties should hold (invariants), but manually specifying invariants is tedious and error-prone. The framework automatically infers invariants from training code by analyzing how variables are initialized, transformed, and constrained.

The system intercepts training loops (via instrumentation or a library wrapper), observes values during warm-up runs with known-correct hyperparameters, and learns patterns: e.g., "gradient norms are always in the range [1e-6, 1e2]", "loss decreases monotonically every 100 steps", "activations are within [-5, 5] after ReLU". It then enforces these learned invariants during production training via runtime checks. When an invariant violation occurs (e.g., NaN gradient, sudden loss spike), the framework flags it, logs context (iteration, layer, batch statistics), and can trigger rollback or detailed inspection. The approach requires minimal manual annotation: developers specify only which metrics to track (loss, gradient norms, activation ranges); the framework infers the valid ranges.

## The Key Result

On real-world deep learning training runs (TensorFlow and PyTorch), the framework detects 18 out of 20 injected or naturally occurring training errors (90% detection rate). Beyond injected errors, the system discovered 6 previously unknown bugs in TensorFlow and PyTorch training libraries (e.g., incorrect gradient accumulation in certain parallelism modes, unintended layer freezing). Detected errors range from hyperparameter application errors (learning rate set to 0) to data pipeline bugs (features transposed incorrectly) to hardware faults (memory corruption causing gradient anomalies). The framework integrates into existing PyTorch and TensorFlow workflows with minimal code changes, making it a practical debugging tool.

## Why This Approach

Silent errors in deep learning are insidious: they corrupt model weights stealthily, producing a model that trains without errors but has degraded generalization. Traditional approaches fail: unit tests cannot catch silent numerical errors (the code runs to completion), assertions require developers to specify what to check, and cross-validation detects the problem late (only after full training). Automated invariant inference solves this by learning normal ranges from good training runs and detecting deviations. The approach is chosen over formal verification (which is too restrictive for floating-point code with inherent noise) and over static analysis (which cannot track dynamic numerical bounds). Learning invariants from examples is practical and catches both systematic errors (bugs in code) and hardware-level errors (cosmic-ray bit flips, DRAM corruption). The framework targets deep learning specifically because training loops are structured (forward pass, compute loss, backward pass, update weights), making it feasible to infer meaningful invariants automatically.

## What It Leaves Open

- **Two errors not detected**: the framework misses 2 out of 20 real-world errors; the paper does not detail why (e.g., errors that do not violate learned invariants due to statistical similarity to good training traces, or errors that manifest only after many iterations).
- **Overhead during training not quantified**: continuous invariant checking adds latency and memory cost; deployments on resource-constrained devices or with tight training time budgets may find the overhead prohibitive.
- **Applicability to all deep learning frameworks uncertain**: evaluation covers PyTorch and TensorFlow; generalization to specialized frameworks (JAX, MXNet, Core ML) and to custom training loops (hand-written CUDA kernels) is unverified.
- **Hyperparameter and architecture generalization**: invariants learned from one model architecture (e.g., ResNet-50) or hyperparameter setting (learning rate 1e-3) may not transfer to other configurations; cold-start detection without warm-up runs is not addressed.
- **No protection against design-level errors**: the framework catches numerical and hardware errors but not design bugs (e.g., wrong loss function chosen, incorrect model formulation); design-level errors leave invariants satisfied but model output wrong.
