# Distributed Training Optimizer

## First Question

Large training splits weights, gradients, optimizer state, and activations across devices. Splitting saves memory but adds communication. This lane asks which split has enough memory headroom and how much communication remains exposed after overlap.

## What The Code Does

- `distributed-training-optimizer/distributed_training_optimizer/analyzer.py models the strategies.`
- `distributed-topology/distributed_topology/planner.py compares device and link layouts when present.`
- `distributed-collectives/distributed_collectives/analyzer.py supplies collective cost estimates.`

## What The Measurement Proves

The measurement proves each strategy records memory per GPU, communication time, pipeline bubble time, optimizer-state savings, and pass or review status.

## What It Does Not Prove

It does not prove a full cluster run completed. The Colab T4 run proves the code path; true collective bandwidth needs a multi-GPU host.

## Read Next

- `site/distributed-training-optimizer.html`
- `site/distributed-topology.html`
- `site/distributed-collectives.html`
