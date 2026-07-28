# DynamoLLM: Designing LLM Inference Clusters for Performance and Energy Efficiency

**Venue:** HPCA · **Theme:** KV Cache Scheduling

## What It Does

LLM inference clusters running on GPU-dense infrastructure consume excessive energy and incur high operational carbon emissions because existing systems provision resources for peak load at maximum GPU frequency and tensor parallelism, ignoring the strong heterogeneity in request types (input/output length variation) and diurnal load fluctuations that create large energy-saving opportunities.

LLM inference workloads are rapidly becoming a dominant share of datacenter power consumption, and a single static cluster configuration cannot simultaneously serve the energy needs of short/low-compute and long/high-compute requests, leaving 35-53% energy savings on the table while meeting latency SLOs.

DynamoLLM is a hierarchical three-level energy management framework (Cluster Manager, Pool Manager, Instance Manager) that dynamically reconfigures a GPU cluster across three knobs: number of inference server instances (scale in/out), tensor parallelism (shard up/down), and GPU frequency (scale up/down). The cluster is partitioned into per-request-type instance pools (classified by input/output token length into SS/SM/.../LL buckets); a BERT-based output-length predictor routes requests to the appropriate pool. Configuration selection is formulated as a MILP optimization using offline energy-performance profiles, with a hierarchical approximation heuristic for real-time operation. Reconfiguration overheads are minimized by: pre-warming VMs from snapshots, direct NVLink weight re-sharding via a bipartite graph matching algorithm (minimizing weight transfers), and keeping nvidia-smi loaded in-memory for rapid GPU frequency changes.

## The Key Experiment

- **speedup:** None
- **energy or tops w:** 53% energy saving, 38% carbon reduction vs. static SinglePool baseline
- **area:** None
- **accuracy:** None
- **other:** 61% cost reduction to customer; DynamoLLM vs. single-knob baselines: ScaleInst 4.1%, ScaleShard 7%, ScaleFreq 19%, DynamoLLM 35% energy reduction in cluster experiment

**Compared against:** SinglePool (TP8, max frequency, static); MultiPool (per-type pools, no scaling); ScaleInst (scale instances only); ScaleShard (scale parallelism only); ScaleFreq (scale frequency only)

**Hardware:** GPU · **Workloads:** LLM-inference

## Why This Approach

A hierarchical multi-knob (instance count + tensor parallelism + GPU frequency) dynamic reconfiguration framework for LLM inference clusters that maintains per-request-type resource pools and minimizes reconfiguration overheads via weight-stationary NVLink re-sharding and proactive VM pre-warming.

This paper sits in the **attention efficiency** subtheme. The core constraint: generating one token requires reading all past key-value vectors from memory — O(n) bandwidth per step. This paper's angle: Characterization of LLM inference energy-performance heterogeneity across request lengths, system load, model size, and SLO requirements using Azure production traces.

## What It Leaves Open

- Evaluation assumes all GPUs are NVIDIA H100 (homogeneous hardware)
- heterogeneous GPU cluster scenarios and multi-tenant LLM co-location are not addressed.

**Tags:** llm-inference, energy-management, gpu-cluster, tensor-parallelism, gpu-frequency-scaling, slo
