# LegUp: An Open-Source High-Level Synthesis Tool For FPGA-Based Processor/Accelerator Systems

## Bibliographic Identity

- Title: LegUp: An Open-Source High-Level Synthesis Tool for FPGA-Based Processor/Accelerator Systems
- Year: 2013
- Source: https://dl.acm.org/doi/10.1145/2514740
- Track: digital-design-and-architecture
- Subtheme: high-level synthesis from software to hardware

## First-Principles Reading

The object being controlled is translation from software behavior into hardware structure. C code states operations in program order, but hardware must expose datapaths, control, memory movement, interfaces, and timing.

The constraint is abstraction debt. A high-level program can hide concurrency, memory bandwidth, bit widths, and communication cost. HLS is useful only if the generated hardware makes those costs visible enough to inspect and optimize.

The mathematical form is scheduling and resource allocation over a program dependence graph. Operations must be assigned to cycles, hardware resources, and communication paths while preserving dependencies.

The concrete method is to compile standard C into FPGA accelerators connected to a processor system. LegUp matters here because it makes HLS inspectable as an open tool rather than a black-box productivity claim.

The evidence artifact is generated hardware plus FPGA implementation results: area, performance, resource use, and comparison against other HLS or manual design approaches.

The failure boundary is hardware reality after abstraction. HLS can produce correct-looking hardware that performs poorly because memory, scheduling, timing, or interface costs dominate.

## Concept Links

- `digital-logic-turns-voltage-into-symbols`
- `timing-closure-is-proof-data-arrives-before-decision`
- `verification-is-evidence-implementation-matches-intent`

## What The Paper Teaches

The deeper lesson is that high-level synthesis is not software magically becoming silicon. It is a translation contract: preserve behavior while making time, resources, and communication explicit.

