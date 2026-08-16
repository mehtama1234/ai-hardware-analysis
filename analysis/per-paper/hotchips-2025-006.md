# AMD Pensando Pollara 400 AI NIC Architecture and Application

**Venue:** HOTCHIPS  
**Confidence:** low (abstract-only)

## Problem
Enterprise AI data centers require programmable network interfaces for flexible packet processing, load balancing, and security; Pollara 400 addresses these needs with a programmable SmartNIC targeting 400Gbps throughput.

## Motivation
AI clusters demand flexible networking infrastructure supporting dynamic workloads, QoS, and security policies; traditional fixed-function NICs cannot adapt to emerging AI collective communication patterns.

## Method
Pollara 400 combines a programmable packet processing engine—based on PISA-style architecture, which applies custom rules to network traffic—with multiple compute cores and high-speed memory hierarchies. This allows the network card itself to perform computations and offload AI workloads, rather than requiring the server to handle all processing. An advanced switching fabric (the hardware routing infrastructure) connects these components and enables flexible traffic management.

## Key Novelty
A programmable network interface that reaches 400Gbps throughput and performs AI-specific packet processing and computing directly within the card itself.

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
