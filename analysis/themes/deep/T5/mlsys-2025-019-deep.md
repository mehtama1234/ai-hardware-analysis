# Efficient On-Device Machine Learning with a Biologically-Plausible Forward-Only Algorithm

**Venue:** MLSYS 2025 · **Subtheme:** Memory-Efficient On-Device Training via Forward-Only Algorithms

## What It Does

Bio-FO introduces a forward-only training algorithm that trains each neural network layer independently using only forward passes, eliminating backpropagation's memory overhead and biological implausibility. For each hidden layer l, the method attaches an auxiliary classifier with a fixed random projection matrix Bl that maps layer activations h_l to class predictions. During training, Bio-FO computes cross-entropy loss and gradient for layer l using only its own activations (h_{l-1} and h_l), then updates weights with this local gradient. Crucially, no inter-layer error signals flow backward (solving non-locality), no activation storage is needed (solving frozen activities), and no symmetric backward weight matrices are maintained (solving weight transport). A sparsity mask S_l enables extensions to locally connected and convolutional architectures.

The core mechanism: for layer l with inputs h_{l-1}, compute outputs h_l = σ(W_l h_{l-1}), then apply the fixed random classifier ŷ = B_l h_l, compute local loss L_l = cross_entropy(ŷ, y), and update W_l = W_l - α ∇_{W_l} L_l. Each layer operates independently, so updates proceed as data arrives (update locking resolved).

## The Key Result

On NVIDIA Jetson Nano (128-core Maxwell GPU, 5-10W power envelope), Bio-FO achieves 3x memory reduction versus backpropagation (32 MB vs 96 MB at batch size 1) and up to 19.8x energy reduction on CIFAR-100 compared to Forward-Forward (FF). Accuracy: CIFAR-100 74.57% error (FF achieves 85.76%, PEPITA achieves 76.16%), and mini-ImageNet 67.39% error (versus 91.23% PEPITA, 74.58% CaFo). Convergence is fastest among forward-only methods (slowness parameter 0.156 on MNIST vs 0.541 for FF and 1.494 for DRTP).

## Why This Approach

Backpropagation requires materializing all intermediate activations (activation storage), implementing biological implausibility (weight transport via explicit backwards weights, non-locality via backpropagated error signals, update locking via layer-by-layer dependencies), and consuming 2-3x memory on edge devices with 32-96 MB budgets. Prior forward-only alternatives (FF, PEPITA, DRTP) address some but not all four issues: FF requires explicit symmetric backward weights; PEPITA allows prediction/update locking; DRTP uses predictive coding. Bio-FO is the first to address all four simultaneously by using fixed random projections as auxiliary classifiers, eliminating the need to learn backward weights, propagate errors globally, or store activations.

The key insight is that gradient information (∇L_l / ∂h_l) can be computed locally using only the layer's own activations and a fixed random projection—no learning required. Fixed random matrices are already proven effective in random projection theory (e.g., random features for kernel approximation), so Bio-FO applies them as lightweight auxiliary classifiers for local loss.

## What It Leaves Open

- Accuracy gap versus backpropagation remains significant on large-scale datasets: mini-ImageNet 67.39% error vs 53.49% for BP—a 2.2x error ratio, making deployment on demanding tasks uncertain.
- Fixed random auxiliary classifiers may be suboptimal for complex decision boundaries; no learned adaptation of the projection matrices, limiting expressiveness.
- Not yet evaluated on hardware specifically designed for forward-only algorithms; all results on general-purpose GPUs (Jetson Nano), leaving performance on custom neuromorphic or analog hardware unknown.
- Not extended to transformers, GANs, or graph neural networks; applicability to modern architectures unclear.
- Weight sharing in CNN extension (sparsity mask S_l) is not biologically plausible; this limits the claim of full biological fidelity to CNNs.
