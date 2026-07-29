# Distributed Submodular Subset Selection at Billion Scale

**Venue:** MLSYS 2025 · **Subtheme:** Data Selection and Pruning via Distributed Optimization

## What It Does

This work enables submodular subset selection (a combinatorial optimization task) to scale beyond centralized memory by distributing data across workers without requiring a central bottleneck. Submodular functions reward selecting diverse items: adding a new item gives decreasing marginal benefit as more items are already selected. For dataset pruning, this selects a high-quality training subset by greedily maximizing a diversity metric.

The key mechanism is a distributed bounding algorithm: each worker computes local upper and lower bounds on marginal gains using "grow" steps (expanding bounds from already-selected items) and "shrink" steps (contracting bounds based on minimum/maximum utility values). These bounds are provably tight without requiring point-to-point communication between all data pairs. A multi-round partition-based greedy scheme aggregates global selections: in each round, workers perform local greedy selection within their partition, then the system uses adaptive repartitioning to adjust work distribution. The method is implemented on Apache Beam for large-scale distributed execution.

## The Key Result

On 13 billion data points, the system achieves 98% of the quality achieved by centralized greedy maximization within 32 communication rounds. This scales to billion-point datasets on commodity clusters without a single machine holding all data simultaneously.

## Why This Approach

Centralized greedy submodular maximization requires materializing O(N) candidate points in a single machine's memory, making it infeasible at billion scale. Naive distributed approaches either lose quality (independent per-partition selection with no global coordination) or require dense pairwise communication (computing marginal gains for all global pairs). The bounding algorithm exploits the structure of submodular functions: marginal gains can be bounded from above (no point will improve more than the global upper bound) and below (each point improves at least the global lower bound), so workers compute these bounds locally without global synchronization. Adaptive repartitioning further reduces rounds by observing which partitions have high-quality selections and concentrating future rounds in those regions.

## What It Leaves Open

- Quality degrades with fewer communication rounds; no formal analysis of the quality-round tradeoff curve provided beyond the 98%/32-round datapoint.
- Bounding tightness depends critically on data distribution and partition quality; pathological distributions (highly non-uniform marginal gains) could require many more rounds to converge.
- Apache Beam infrastructure required for deployment; method not evaluated on simple parameter servers or gossip-based systems, limiting accessibility.
- Adaptive repartitioning adds coordination overhead; overhead cost not isolated or characterized separately from selection cost.
- Evaluation focused on CIFAR-100 and ImageNet; generalization to other dataset selection tasks (e.g., active learning, noisy label filtering) unexamined.
