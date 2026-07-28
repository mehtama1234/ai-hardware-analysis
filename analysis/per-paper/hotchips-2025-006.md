# AMD Pensando Pollara 400 AI NIC Architecture and Application

**Venue:** HOTCHIPS  
**Confidence:** low (abstract-only)

## Problem
Enterprise AI data centers require programmable network interfaces for flexible packet processing, load balancing, and security; Pollara 400 addresses these needs with a programmable SmartNIC targeting 400Gbps throughput.

## Motivation
AI clusters demand flexible networking infrastructure supporting dynamic workloads, QoS, and security policies; traditional fixed-function NICs cannot adapt to emerging AI collective communication patterns.

## Method
Pollara 400 integrates a programmable packet processing engine (likely PISA-style) with multiple compute cores, high-speed memory hierarchies, and advanced switching fabric to enable in-NIC compute offloads and flexible traffic management.

## Key Novelty
400Gbps programmable SmartNIC architecture enabling AI-optimized packet processing and in-network computing.

## Contributions
- 400Gbps programmable SmartNIC for enterprise AI infrastructure
- Flexible packet processing engine supporting custom AI workload optimization
- In-NIC compute offload capabilities
- Demonstrated application to AI cluster networking

## Hardware Targets
SmartNIC, SoC

## Techniques
interconnect, scheduling, parallelism

## Workloads
LLM-training, LLM-inference

## Metrics
- Throughput: 400 Gbps
- Latency: reduced latency for AI collective operations

## Baselines
Mellbox NICs, Traditional Ethernet NICs, ConnectX series

## Limitations
Not discussed.

## Tags
smartnic, networking, programmable, ai-nics, 400gbps, enterprise
