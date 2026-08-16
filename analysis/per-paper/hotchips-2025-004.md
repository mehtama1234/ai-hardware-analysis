# ConnectX-8 SuperNIC

**Venue:** HOTCHIPS  
**Confidence:** low (abstract-only)

## Problem
AI data centers require ultra-high-speed networking for distributed training and inference; ConnectX-8 SuperNIC addresses bottlenecks in Ethernet switching and packet processing at scale.

## Motivation
As AI clusters scale to thousands of GPUs, network bandwidth and latency become critical bottlenecks; programmable SmartNIC offloads allow reducing CPU load and improving collective operation performance.

## Method
ConnectX-8 works by processing packets in customizable ways directly on the network interface card (NIC — the hardware connecting servers to the network). It performs collective operations (like AllReduce and AllGather, which combine and share data across servers) inside the network hardware itself, rather than sending data back to servers' processors. It also manages network congestion by adjusting traffic flow when links get busy, and uses a high-speed switching infrastructure to move data between servers with minimal delay.

## Key Novelty
A network interface card now runs collective operations (AllReduce and AllGather, used to combine and share data across servers in distributed training) directly in its hardware, instead of requiring a server's main processor.

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
