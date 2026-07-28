# FLStore: Efficient Federated Learning Storage for non-training workloads

**Venue:** MLSYS 2025 · **Theme:** KV Cache Scheduling

## What It Does

Federated learning non-training workloads (scheduling, personalization, clustering, debugging, incentivization) impose high latency and cost because they access large volumes of metadata (model weights, hyperparameters, aggregated updates) stored in remote cloud object stores or in-memory caches without data locality.

FL non-training workloads exhibit access patterns that differ from training: they require low-latency reads of client update metadata, repeated access to aggregated model checkpoints, and correlation of historical round data. Existing aggregator-server designs serialise these accesses through a central bottleneck, incurring round-trip overheads that dominate total latency.

FLStore is a serverless cache framework that co-locates compute and data on the same cache tier. A Cache Engine (hash-table-based) routes requests to the cache node holding the relevant data based on a locality-aware key hashing. A Request Tracker maintains per-client access history to identify hot data. Four caching policies (P1-P4) are derived from a taxonomy of FL non-training workload types: P1 caches client model updates by round; P2 caches aggregated models; P3 caches derived metadata (gradients, loss) across rounds; P4 implements prefetching for predictable access patterns.

## The Key Experiment

- **latency vs objstore agg:** 71% average latency reduction vs cloud object store aggregator; 99.7% peak
- **cost vs objstore agg:** 92.45% cost reduction; 98.8% peak
- **latency vs cache agg:** 64.6% average latency reduction vs in-memory cloud cache aggregator
- **cost vs cache agg:** 98.83% cost reduction vs in-memory cache aggregator

**Compared against:** ObjStore-Agg (S3-based aggregator); Cache-Agg (Redis/Memcached-based aggregator)

**Hardware:** cloud-cpu; serverless-cache · **Workloads:** federated-learning; model-aggregation; scheduling; personalization

## Why This Approach

Unified data+compute serverless cache tier with a four-policy taxonomy derived from a systematic analysis of FL non-training workload access patterns, enabling locality-aware execution without a central aggregator bottleneck.

This paper sits in the **attention efficiency** subtheme. The core constraint: generating one token requires reading all past key-value vectors from memory — O(n) bandwidth per step. This paper's angle: Taxonomy of FL non-training workloads and their storage access characteristics.

## What It Leaves Open

- Serverless cold-start latency when cache nodes are not warm
- Hash-based routing may cause hotspots for highly skewed client distributions
- Fault tolerance relies on replication which adds storage overhead
- Taxonomy and policies assume relatively stationary access patterns; concept drift requires policy re-tuning

**Tags:** federated-learning, caching, serverless, non-training-workloads, storage, FL
