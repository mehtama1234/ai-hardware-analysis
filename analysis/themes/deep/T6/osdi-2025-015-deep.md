# KPerfIR: Towards a Open and Compiler-centric Ecosystem for GPU Kernel Performance Tooling on Modern AI Workloads

**Venue:** OSDI · **Subtheme:** Performance Modeling

## What It Does

Integrated profiling infrastructure built directly into the Triton compiler, providing fine-grained kernel performance measurements with instrumentation at compile-time to minimize runtime overhead

First profiling system to integrate directly into Triton compiler pipeline with only 8.2% measurement overhead and 2% error tolerance, enabling closed-loop compiler optimization

## The Key Result

- **Other:** {'profiling_overhead': '8.2%', 'measurement_error': '2%'}

## Why This Approach

Integrated profiling infrastructure in Triton compiler reducing measurement overhead to 8.2%. Measurement error reduced to 2% of true performance metrics. Enables compiler passes to directly use profiling data for performance-driven optimization decisions. Eliminates separate profiling passes, improving developer iteration time

This work addresses the fundamental problem: GPU kernel profiling introduces significant overhead and measurement error, hindering performance analysis and optimization feedback during compiler-driven code generation

## What It Leaves Open

- Limited to Triton compiler ecosystem; measurement overhead still non-zero; applicability to other compiler frameworks unclear.
