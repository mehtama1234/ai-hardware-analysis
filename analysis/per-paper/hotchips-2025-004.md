# ConnectX-8 SuperNIC

**Venue:** HOTCHIPS  
**Confidence:** low (abstract-only)

## Problem
AI data centers require ultra-high-speed networking for distributed training and inference; ConnectX-8 SuperNIC addresses bottlenecks in Ethernet switching and packet processing at scale.

## Motivation
As AI clusters scale to thousands of GPUs, network bandwidth and latency become critical bottlenecks; programmable SmartNIC offloads allow reducing CPU load and improving collective operation performance.

## Method
ConnectX-8 integrates programmable packet processing, in-network computing (INC) for collective operations, advanced congestion control, and high-speed switching fabric to deliver ultra-low-latency, high-throughput networking optimized for AI workloads.

## Key Novelty
SmartNIC with in-network computing capabilities enabling offloaded collective operations (AllReduce, AllGather) directly on the NIC hardware.

## Contributions
- ConnectX-8 SuperNIC architecture with programmable packet processing
- In-network computing acceleration for collective operations
- Advanced congestion control for AI collective workloads
- Demonstrated latency reduction for distributed training

## Hardware Targets
SmartNIC, SoC

## Techniques
interconnect, scheduling, parallelism

## Workloads
LLM-training, LLM-inference

## Metrics
- Latency: ultra-low latency for collective operations
- Energy: reduced CPU overhead vs. traditional NIC

## Baselines
ConnectX-7, Traditional Ethernet switches, CPU-based collectives

## Limitations
Not discussed.

## Tags
smartnic, networking, collective-ops, in-network-compute, ai-datacenter, ethernet
