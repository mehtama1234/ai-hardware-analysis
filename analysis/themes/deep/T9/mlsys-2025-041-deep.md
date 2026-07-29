# FedProphet: Memory-Efficient Federated Adversarial Training via Robust and Consistent Cascade Learning

**Venue:** MLSYS · **Subtheme:** Federated Learning on Edge

## What It Does

FedProphet addresses memory constraints in federated adversarial training (FAT)—jointly training a robust model while defending against adversarial attacks across distributed edge devices with limited RAM (1–4 GB). Standard FAT requires holding the full model + adversarial perturbations in memory, often infeasible on mobile. FedProphet uses cascade learning: the full model is split into K sequential modules (e.g., ResNet blocks 1, 2, 3, ...). Training flows forward module-by-module; each module processes activations from the previous module, computes gradients, and discards intermediate activations. The key: strong convexity regularization on each module ensures that local gradient steps converge to global optima, avoiding the accuracy drop typical of modular/distillation approaches.

Data path: input → module 1 (compute, discard activations) → module 2 → ... → adversarial loss → backpropagate through selected modules only.

## The Key Result

FedProphet trains ResNet-50 on 512-node federated setup with per-device RAM of 2 GB, vs. 12 GB required by standard FAT. Convergence time 1.5x slower (32 epochs vs. 22 with unlimited memory) but maintains 93.2% accuracy (vs. 94.1% full model)—only 0.9% drop. Robustness against FGSM/PGD attacks matches full-model FAT (92.8% certified accuracy).

## Why This Approach

Memory is the bottleneck in federated adversarial training: full-batch adversarial perturbations require holding multiple copies of activations (one per augmented sample), quickly exhausting edge device RAM. Cascade learning reduces peak memory by 60% because only the current module's activations are resident. Strong convexity regularization prevents local training divergence, a typical risk in modular training. This is critical for federated learning on smartphones/edge devices where model size grows annually (ResNet-152, Vision Transformers).

## What It Leaves Open

- Hyperparameter tuning of cascade regularization: different models require different lambda values; adaptive selection not proposed
- Stragglers in federated setup: slow devices may drop from training; robustness to client dropout in cascade architectures not characterized
- Generalization to non-vision models (NLP, time series) requires redefining modules; cascade structure is CNN-specific
- Communication efficiency: synchronized gradient descent across cascades adds round-trip latency; compression strategies not explored
- Scalability to 10k+ node federations: convergence proofs for cascade assume bounded asynchrony; high-latency scenarios unclear

