# ENABLING AI Infrastructure: Tomahawk Ultra - Ultra Low Latency, High Bandwidth Ethernet Switch for HPC & AI/ML applications

**Venue:** HOTCHIPS  
**Confidence:** low (abstract-only)

## Problem
AI/ML data centers require ultra-low-latency, high-bandwidth switching to support collective operations and distributed training; Tomahawk Ultra targets sub-microsecond latency Ethernet switching.

## Motivation
Distributed AI training scaling depends critically on collective operation latency; sub-microsecond switch latency directly improves AllReduce and AllGather performance, enabling efficient training on thousands of GPUs.

## Method
Tomahawk Ultra implements high-radix Ethernet switching with optimized packet pipeline, cut-through forwarding, and minimal queue depth for ultra-low latency, combined with advanced congestion control and in-switch QoS to prioritize AI collective traffic.

## Key Novelty
Ultra-low-latency Ethernet switch architecture optimized for AI collective operations and distributed training.

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
