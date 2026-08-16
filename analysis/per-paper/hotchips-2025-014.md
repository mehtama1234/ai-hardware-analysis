# ENABLING AI Infrastructure: Tomahawk Ultra - Ultra Low Latency, High Bandwidth Ethernet Switch for HPC & AI/ML applications

**Venue:** HOTCHIPS  
**Confidence:** low (abstract-only)

## Problem
AI/ML data centers require ultra-low-latency, high-bandwidth switching to support collective operations and distributed training; Tomahawk Ultra targets sub-microsecond latency Ethernet switching.

## Motivation
Distributed AI training scaling depends critically on collective operation latency; sub-microsecond switch latency directly improves AllReduce and AllGather performance, enabling efficient training on thousands of GPUs.

## Method
Tomahawk Ultra is an Ethernet switch with many ports (high-radix means numerous connection points) designed for extreme speed. It uses cut-through forwarding: instead of waiting to receive an entire data packet before sending it on, it starts forwarding the packet immediately upon arrival—cutting down the delay significantly. The switch keeps the waiting lines (queues) for packets very short to prevent data from sitting idle. It also includes smart traffic controls built into the switch itself that detect when the network is congested and automatically prioritize packets from AI collective training operations, ensuring these time-sensitive workloads experience minimal latency.

## Key Novelty
An Ethernet switch designed to move data with sub-microsecond latency specifically for AI collective operations and distributed training.

## Contributions
- Ultra-low-latency Ethernet switching fabric for AI infrastructure
- Sub-microsecond latency packet forwarding
- Advanced QoS and congestion control for AI workloads
- Demonstrated improvement in distributed training collective operation latency

## Hardware Targets
SoC, ASIC

## Techniques
interconnect, circuit-design, scheduling

## Workloads
LLM-training

## Metrics
- Latency: ultra-low (<1μs) switch latency
- Throughput: high bandwidth Ethernet support

## Baselines
Tomahawk/Tomahawk+, other data center Ethernet switches

## Limitations
Not discussed.

## Tags
ethernet-switch, low-latency, data-center, collective-ops, ai-infrastructure, qos
