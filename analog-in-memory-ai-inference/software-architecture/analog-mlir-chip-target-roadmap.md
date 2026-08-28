# analog-mlir Chip Target Roadmap

## Purpose

This document explains how `analog-mlir` fits our platform and what we would need to change before it can support a real startup analog chip.

The simple answer:

```text
analog-mlir can help us check whether a model can be split and mapped toward analog compute.
But it does not automatically target our real chip.
If we use it as our compiler base, we need a chip-specific target, runtime path, tiling rules, calibration metadata, and transformer partitioning.
```

## What analog-mlir Is Today

The local `analog-mlir` tree describes itself as an experimental MLIR-based compiler that lowers supported tensor and `linalg` kernels into an analog compute-in-memory execution model, then lowers that model to the Golem simulator runtime.

Its current flow is:

```text
input model IR
  |
  v
analog-extract-layers
  |
  v
analog-convert-layers
  |
  v
analog-isolate-weights
  |
  v
analog-assemble-task-graph
  |
  v
analog-lower-to-golem
  |
  v
LLVM/bufferization lowering
  |
  v
analog-emit-runtime-graph
  |
  v
Golem/SST-oriented runtime graph
```

Supported layer families in the current README include:

- linear
- Conv1D
- Conv2D
- grouped Conv2D
- Conv3D
- RNN cell

This is useful, but it is not enough for our physical chip.

## The Main Product Truth

We should not say:

```text
analog-mlir already compiles customer models to our chip.
```

We should say:

```text
analog-mlir is a useful compiler starting point and mapping checker.
To target our chip, we need to add or extend the backend path.
```

## Keep Golem, Add Our Chip Target

We should not think of this as simply bypassing Golem.

Golem/SST is still useful for pre-silicon system simulation.

The better architecture is:

```text
analog IR
  |
  +-- Golem/SST target
  |     used for simulation before silicon
  |
  +-- Our chip target
        used for physical board/runtime execution
```

That means we keep the simulator path and add a real hardware path.

## What Must Change For Our Chip

### 1. Add A Chip-Specific Backend Target

Current issue:

```text
analog-lower-to-golem lowers analog execution into Golem-oriented MLIR.
```

Our real chip will need a different output.

It may need:

- firmware calls
- command buffers
- register writes
- DMA setup
- memory transfer commands
- analog tile programming commands
- digital coprocessor commands
- calibration commands
- runtime status checks
- failure handling

What to build:

```text
analog-lower-to-our-chip
analog-emit-our-chip-runtime
```

These do not need to replace the Golem passes at first. They should live beside them.

User-facing result:

```text
Compiler target:
simulation only, chip target missing, or chip target available.
```

Why the user cares:

```text
The user can see whether the compiler path is a real product path or only a simulator path.
```

### 2. Add Real Hardware Tiling Rules

Current issue:

Analog arrays have physical size limits.

A model may contain a large matrix, but the chip may only have smaller analog tiles.

Example:

```text
model weight matrix: 8192 x 8192
physical array tile: 512 x 512
```

The compiler must split the model matrix into physical tile-sized chunks.

What to build:

- tile-size rules
- row and column limits
- tile placement
- partial-sum collection
- memory placement
- data movement cost
- fallback when a shape cannot fit

User-facing result:

```text
This layer fits in 8 tiles.
This layer needs 128 tiles.
This layer exceeds tile limits.
This layer needs digital fallback or rewrite.
```

Why the user cares:

```text
The user can see whether "analog fit" survives real chip size limits.
```

### 3. Add Bit-Slicing And Precision Rules

Current issue:

One logical model weight may need more precision than one physical analog memory cell can store.

Example:

```text
model wants 8-bit weight
analog cell stores 2 bits
compiler may need 4 cells or slices
```

What to build:

- logical weight precision
- physical cell precision
- bit-slicing plan
- signed weight representation
- slice placement
- ADC range per slice
- digital recombination
- energy and latency cost of recombination

User-facing result:

```text
This layer needs 4 slices per weight.
That increases area, conversion work, and digital accumulation.
```

Why the user cares:

```text
The user can see whether a good analog layer still becomes expensive after precision is counted.
```

### 4. Add Analog/Digital Partitioning For Transformers And VLA Models

Current issue:

Transformers contain both analog-friendly and analog-hostile parts.

Analog-friendly:

- static projection weights
- feed-forward weights
- some linear layers
- some convolution-style frontends

Usually digital:

- dynamic attention scores
- Softmax
- LayerNorm
- dynamic activation-to-activation matrix multiplies
- control flow
- safety logic
- action timing

What to build:

- transformer graph scanner
- static projection detector
- dynamic attention detector
- Softmax boundary detector
- LayerNorm boundary detector
- action-head detector
- analog candidate report
- digital required report
- rewrite suggestion report

This could be a new frontend analysis pass, a new MLIR pass, or a backend pre-pass before `analog-mlir`.

User-facing result:

```text
The projection layers may map to analog.
The attention score calculation stays digital.
Softmax stays digital.
LayerNorm stays digital.
The action head needs separate control-boundary review.
```

Why the user cares:

```text
The user avoids claiming the whole VLA model runs on analog just because some matrix layers fit.
```

### 5. Add Scheduling For ADC, DAC, Tile, And Memory Bottlenecks

Current issue:

Real chips are limited by more than compute.

They are also limited by:

- ADC sharing
- DAC bandwidth
- tile reuse
- column groups
- row drivers
- memory movement
- host dispatch
- digital accumulation

The supplied GLP idea may be relevant if our chip has ADC column-group bottlenecks. But we should not hard-code GLP as a universal requirement until the chip architecture confirms it.

Better requirement:

```text
Add hardware scheduling passes for ADC sharing, tile parallelism, column grouping, and dataflow scheduling.
```

Possible specific optimization:

```text
Group-Level Parallelism if our ADC and column-group design needs it.
```

User-facing result:

```text
This model is compute-limited.
This model is ADC-limited.
This model is memory-limited.
This model is host-dispatch-limited.
```

Why the user cares:

```text
The user can see whether analog compute is actually the bottleneck or whether something else erases the advantage.
```

### 6. Add Calibration Metadata

Current issue:

Analog arrays are imperfect. Different tiles may behave differently.

The compiler should not assume every tile is identical.

What to build:

- tile calibration table support
- weak-tile avoidance
- per-tile correction metadata
- drift profile reference
- temperature profile reference
- voltage profile reference
- recalibration requirement
- fallback behavior when calibration fails

Compiler role:

```text
Emit calibration-aware placement metadata.
```

Runtime role:

```text
Run calibration commands, apply correction values, and report failures.
```

User-facing result:

```text
This mapping assumes calibration profile X.
These tiles are avoided.
These correction values are required.
This claim is blocked until calibration evidence is imported.
```

Why the user cares:

```text
The user can see whether the model is robust on real analog hardware, not only ideal analog hardware.
```

### 7. Add Weight Programming And Update Metadata

Current issue:

Analog IMC works best when weights stay stable. Physical AI may need updates.

The compiler needs to know:

- which weights are static
- which weights are writable
- which adapter layers are writable
- whether the full model must be rewritten
- how long writing takes
- how much energy writing costs
- whether updates hurt endurance
- whether rollback exists

What to build:

- static weight isolation
- writable-scope metadata
- adapter/head update support
- write command planning
- rollback metadata
- post-write validation hook

User-facing result:

```text
This workload is fixed-weight ready.
This workload may support adapter updates.
This workload is blocked for frequent local adaptation.
```

Why the user cares:

```text
The user can see whether the chip supports the update pattern the product needs.
```

### 8. Add Runtime And Board Integration

Current issue:

Compiler output must eventually run somewhere.

For a real chip, that means integration with:

- board runtime
- firmware
- host driver
- register interface
- command queues
- memory transfer
- status polling
- error reporting
- debug traces

What to build:

- runtime command format
- host-side loader
- board execution API
- trace output
- failure output
- version metadata

User-facing result:

```text
Compiler produced a board-loadable package.
Board runtime accepted it.
Board runtime rejected it with this reason.
```

Why the user cares:

```text
The user can see whether the model moved beyond mapping into actual execution.
```

## What We Should Build First

We should not start by deeply hacking every `analog-mlir` pass.

The safer order is:

### Phase 1: Use analog-mlir As A Mapping Reference

Build:

- adapter probe
- dependency/build status
- simple compiler mapping import
- normalized `compiler_mapping.json`
- frontend status for simulation-only vs chip-target missing

Goal:

```text
Show whether analog-mlir can identify analog-shaped regions and where the current compiler path stops.
```

### Phase 2: Add Our Product-Level Compiler Contract

Build a normalized compiler artifact that can be produced by `analog-mlir`, another compiler, or our own mapper.

Fields:

- analog candidates
- digital required regions
- unsupported regions
- tile plan
- bit-slice plan
- memory plan
- weight isolation plan
- calibration assumptions
- runtime target
- blocked reasons
- next action

Goal:

```text
Make the frontend independent of raw analog-mlir output.
```

### Phase 3: Add Transformer Partitioning

Build:

- transformer scanner
- VLA scanner
- attention boundary report
- static projection report
- digital nonlinear report
- rewrite suggestions

Goal:

```text
Stop false claims that the full transformer or VLA model maps to analog.
```

### Phase 4: Add Chip-Specific Lowering

Build:

- chip target dialect or backend
- chip command format
- runtime package format
- calibration metadata
- tile placement rules
- bit-slicing rules
- board loader integration

Goal:

```text
Move from compiler mapping to real chip execution.
```

### Phase 5: Keep Golem/SST For System Simulation

Build:

- Golem/SST adapter
- runtime trace normalization
- dispatch overhead report
- memory movement report
- synchronization report

Goal:

```text
Use simulation to test system bottlenecks before hardware is ready.
```

## How This Appears In Our Platform

The frontend should not show compiler internals first.

It should show:

```text
Compiler Mapping

User benefit:
Know whether the normal model can be prepared for the analog chip path.

Status:
simulation target only, chip target missing, chip target available, or blocked.

Tool support:
analog-mlir, TVM/MLIR/IREE later, our compiler placement adapter.

Result:
analog candidates, digital required regions, unsupported parts, tile limits, bit-slicing cost, calibration assumptions, and runtime target.

Next action:
connect analog-mlir, add chip target, import compiler report, or rewrite blocked operators.
```

## Claim Boundaries

Compiler mapping can support:

```text
This model has regions that may map to analog execution.
```

Compiler mapping cannot support by itself:

```text
The chip is low power.
The board meets latency.
The model keeps task accuracy.
The chip is production ready.
The system supports adaptive Physical AI.
```

Those claims need board runtime, power, task accuracy, calibration, reliability, and update evidence.

## Final Recommendation

Use `analog-mlir` in stages.

Do not treat it as a finished production compiler.

Use it first to learn and report:

- what model parts are analog-shaped
- what weights are static
- what execution graph can be built
- what remains digital
- where the Golem simulation path stops

Then extend it or wrap it with:

- chip-specific lowering
- tile and bit-slice placement
- transformer partitioning
- calibration metadata
- runtime command generation
- board integration

The platform should expose this plainly:

```text
analog-mlir helps us check compiler fit.
Our chip still needs its own target path before this becomes real deployment.
```
