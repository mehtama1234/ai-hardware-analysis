# LEGO: Spatial Accelerator Generation and Optimization for Tensor Applications

**Venue:** HPCA · **Subtheme:** Dataflow Compilation

## What It Does

LEGO uses a relation-centric, affine-transformation-based hardware representation that maps temporal/spatial iteration indices to computation indices via linear matrices, fully decoupling computation logic, data paths, and memory from one another. The LEGO frontend solves integer linear equations to find FU interconnections exploiting data reuse, runs a Minimum Spanning Tree (Chu-Liu/Edmonds algorithm) to prune redundant connections, and applies a BFS-based heuristic to plan direct interconnections across multiple fused dataflows with conflict-free banked memory. The backend translates the FU-level Architecture Description Graph (ADG) into a primitive-level Detailed Architecture Graph (DAG) and applies linear-programming-based delay matching and pin rewiring passes to minimize pipeline register count and eliminate unused logic, yielding synthesizable RTL.

A unified affine-transformation-based representation that decouples control flow from dataflow, enabling automatic generation of synthesizable RTL for any combination of spatial dataflows without hand-written templates, while reducing control logic overhead by 2x-6.5x versus prior polyhedral/STT approaches.

## The Key Result

- **Speedup:** 3.2x over Gemmini
- **Energy Or Tops W:** 2.4x energy efficiency over Gemmini
- **Area:** 35% area savings from backend optimization over naive RTL generation
- **Other:** 6.5x flip-flop savings and 5.0x LUT savings vs AutoSA; 2.0x area, 2.6x power savings vs TensorLib

## Why This Approach

Relation-centric affine representation separating control flow from dataflow, eliminating division/modulo in prior representations and enabling shared control-signal propagation. Frontend interconnection analysis using integer linear equations, MST-based minimal connection selection, and BFS-based heuristic for multi-dataflow fusion with conflict-free memory banking. Backend primitive-level graph (DAG) with linear-programming-based delay matching and pin-rewiring optimization reducing register count and unused-logic overhead by 28-35%. 3.2x speedup and 2.4x energy efficiency improvement over Gemmini; generates one unified architecture for diverse foundation model kernels

This work addresses the fundamental problem: Existing spatial accelerator design frameworks either rely on a small set of hand-written RTL/HLS templates (limiting design space coverage) or cannot automatically generate synthesizable RTL, forcing...

## What It Leaves Open

- LEGO currently supports a set of predefined NoC structures; custom NoC topologies require additional integration; evaluation targets ASIC synthesis with Verilog but full tapeout results are not presented.
