# SparseInfer: Training-free Prediction of Activation Sparsity for Fast LLM Inference

**Venue:** DATE · **Subtheme:** Activation Sparsity Prediction for Inference Optimization

## What It Does

SparseInfer enables real-time sparsity prediction without requiring a separate trained predictor network. The method works by converting ReLU-fied LLMs (replacing SiLU activations with ReLU, which produces zero outputs for negative pre-activations) and then performing lightweight sign-bit comparison to predict which activations will be zero. For each token position, the predictor examines only the sign bits of input activations and weight matrices—if sign(input) and sign(weight) differ, the product contributes zero to the output. This binary logic suffices to identify sparse patterns without ever computing actual values or maintaining predictor state.

An adaptive tuning mechanism adjusts the predictor's conservativeness as a control knob: the system can trade off between predicted sparsity aggressiveness (skipping more computation at risk of accuracy loss) and safety (conservative predictions preserve accuracy). This enables runtime optimization where the predictor adapts based on accuracy monitoring.

## The Key Result

On LLM inference workloads, SparseInfer achieves approximately 21% faster inference compared to state-of-the-art sparsity predictor baselines while maintaining negligible accuracy loss within 1 percentage point.

## Why This Approach

Modern LLMs using SiLU activations exhibit minimal activation sparsity naturally, so replacing SiLU with ReLU is necessary to induce zero patterns. However, prior predictor methods required training a separate neural network to learn sparsity patterns, adding deployment overhead and latency. SparseInfer's sign-bit approach eliminates this training step entirely by exploiting the mathematical property that ReLU outputs are zero whenever the preactivation is negative—a condition directly observable from input and weight signs without any arithmetic. This is fundamentally more efficient than learned prediction because it operates at the bit level with trivial hardware cost, making it deployable immediately on inference hardware without retraining infrastructure.

## What It Leaves Open

- Limited details on how sign-bit prediction handles quantized weights or mixed-precision activations common in deployed LLM inference.
- No characterization of how prediction accuracy degrades as ReLU sparsity patterns vary across different model layers or prompt contexts.
- Adaptive conservativeness tuning mechanism mentioned but not detailed; unclear how the system decides when to increase or decrease conservativeness.
- Evaluation baseline ("state-of-the-art sparsity predictor") not specified; comparison methodology against learned predictors not described.
- Compatibility with structured sparsity accelerators (N:M patterns, tensor cores) not discussed.
