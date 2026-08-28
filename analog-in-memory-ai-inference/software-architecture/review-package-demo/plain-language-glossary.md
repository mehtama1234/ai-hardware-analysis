# Plain-Language Glossary

This file explains the terms used in the roadmap without assuming chip, compiler, or robotics background.

Use this rule while reading:

```text
A term explains an idea. Evidence proves whether the idea works for this chip.
```

## Workload

A workload is the real job the customer wants to run.

It is not just a model name. It includes the model, input data, output requirement, accuracy target, response time, power budget, temperature range, update needs, safety needs, and failure tolerance.

Why it matters:

The same analog chip can be a good fit for one workload and a poor fit for another.

Proof needed:

The package needs the actual model, input shape, output type, task metric, success target, and operating conditions.

## Analog In-Memory Compute

Analog in-memory compute means doing some math where the model weights are stored.

In ordinary digital systems, weights are often moved from memory into a processor before math happens. Moving that data can use a lot of energy. Analog in-memory compute tries to reduce that movement by using physical electrical behavior inside memory-like arrays.

Why it matters:

It may save energy for repeated matrix math, but physical signals can be affected by noise, heat, aging, voltage changes, and limited precision.

Proof needed:

The package needs analog accuracy evidence, layout evidence, runtime evidence, board evidence, power evidence, temperature evidence, calibration evidence, and task evidence before strong claims are allowed.

## Matrix Math

Matrix math is a common kind of AI calculation where many numbers are multiplied and added.

Many neural-network layers spend most of their time doing this. Analog arrays are usually most interesting when the same stored weights are reused many times for this kind of work.

Why it matters:

If the workload is not mostly reusable matrix math, analog compute may not help.

Proof needed:

The model intake and analog-fit artifacts must show which layers are matrix-heavy and how often they are reused.

## Hybrid Chip

A hybrid chip uses analog blocks for some work and digital blocks for other work.

Analog blocks should handle repeated matrix-heavy work when they are accurate enough. Digital blocks should handle changing decisions, exact control, scheduling, safety checks, memory movement, and model steps that are hard to trust in analog.

Why it matters:

Modern AI workloads usually should not be described as fully analog.

Proof needed:

The package needs an analog/digital split report, compiler mapping, runtime estimate, board run, task result, and failure/fallback record.

## Compiler

A compiler is a translator.

For this product, the compiler takes a normal AI model and turns it into a plan for the chip. It decides what runs on analog, what stays digital, how big layers are split, where weights are placed, how signal conversion is scheduled, and what the board should load.

Why it matters:

Customers will not manually place weights on arrays, choose converter timing, or write low-level board commands.

Proof needed:

The package needs a compiler artifact that shows layer extraction, analog/digital split, tile placement, bit-slicing, memory movement, unsupported operators, runtime package status, and failure reasons.

## MLIR

MLIR is a compiler framework for representing programs at different levels of detail.

In this roadmap, analog-mlir is useful because it shows ideas for finding supported model layers, converting them into analog-style work, isolating stable weights, and lowering toward simulation.

Why it matters:

analog-mlir can help structure our compiler work, but it is not automatically a finished deployment compiler for our physical chip.

Proof needed:

The package needs a chip-specific compiler target that can produce a board-loadable package for our runtime.

## Tile

A tile is a smaller physical section of the analog array.

Large model layers may not fit on one array. The compiler may need to split a layer across many tiles and then add the partial results back together.

Why it matters:

Splitting a layer can add area, latency, energy, memory movement, and converter work.

Proof needed:

The compiler mapping and layout artifacts must show tile size, tile count, placement, partial-result handling, and unsupported layers.

## Bit-Slicing

Bit-slicing means using several low-precision physical cells or columns to represent one higher-precision model value.

For example, if a model expects an 8-bit value but the cell stores fewer reliable levels, the system may split that value across multiple physical pieces.

Why it matters:

Bit-slicing can improve usable precision, but it can increase area, latency, energy, and result-combining work.

Proof needed:

The compiler and layout artifacts must show slice count, placement, digital accumulation, converter cost, and accuracy effect.

## ADC And DAC

A DAC turns a digital input number into an analog signal the array can use.

An ADC turns the analog result back into a digital number. These blocks are needed when digital software talks to analog compute.

Why it matters:

Converters can use time and power. A fast analog array can still lose if ADCs, DACs, memory movement, or host dispatch dominate the run.

Proof needed:

The runtime and power artifacts must show converter timing, converter energy, sharing rules, bottlenecks, and whether the workload is compute-limited, converter-limited, memory-limited, or host-limited.

## Calibration

Calibration is the correction process for the real chip.

It checks how the physical cells, tiles, voltages, and temperatures behave. Then it gives the runtime correction values and fallback rules.

Why it matters:

An analog result is not trustworthy just because the digital model was accurate. The platform must show which correction profile was used and what happens if correction fails.

Proof needed:

The package needs calibration profile id, board id, chip id, monitor readings, weak-tile list, correction values, drift profile, pass/fail status, recalibration commands, and fallback behavior.

## Drift

Drift means the physical value stored in the chip changes over time.

This can happen because of material behavior, temperature, repeated use, voltage stress, or aging.

Why it matters:

A model can be accurate immediately after programming and less accurate later.

Proof needed:

The package needs drift assumptions for simulation and measured drift evidence for hardware claims. Stronger claims need task accuracy under the same time and temperature conditions.

## Weak Tile

A weak tile is a section of the analog array that is less accurate or less stable than expected.

The runtime may avoid it, use correction values, rerun the operation elsewhere, fall back to digital compute, or block the result.

Why it matters:

The chip should not silently use a bad section of the array and return a confident wrong answer.

Proof needed:

The calibration artifact must list weak tiles, explain how they were detected, and show what fallback behavior was used.

## Runtime Package

A runtime package is the file or bundle that the board can load and execute.

It should include model placement, weights or weight references, analog/digital task plan, runtime commands, calibration metadata, firmware compatibility, and setup information.

Why it matters:

A compiler report is not enough. The board needs a concrete package it can load.

Proof needed:

The board runtime artifact must show package id, firmware version, load status, start status, finish status, latency, jitter, failure reason, and debug trace.

## Board Proof

Board proof means the package actually ran on a physical lab board or prototype setup.

A useful board result includes pass or fail, firmware version, board version, timing, failure reason, and exact setup used.

Why it matters:

Simulator output can guide design, but it cannot replace measured hardware behavior.

Proof needed:

The package needs a validated board runtime trace tied to the same package, workload, board, firmware, and setup.

## Power And Thermal Proof

Power proof shows how much energy was used.

Thermal proof shows how hot the chip or board became. The result must say whether it measured the whole board, the chip, one power rail, or only a small block.

Why it matters:

A chip can look efficient if the measurement ignores the host computer, memory movement, signal conversion, or cooling problem.

Proof needed:

The package needs rail map, energy per run, peak power, temperature trace, sampling rate, equipment, board id, firmware id, package id, and measurement timing.

## Transformer

A transformer is a model family used in many modern AI systems.

Transformers often include repeated matrix-heavy layers, attention, normalization, memory movement, and non-linear steps.

Why it matters:

Some transformer parts may fit analog compute. Other parts should stay digital or require fallback.

Proof needed:

The package needs transformer partitioning, compiler mapping, runtime evidence, task evidence, and clear blocked regions.

## VLA Model

A VLA model uses vision, language, and action information to choose what a machine should do.

These models are important for physical AI because they can connect camera or sensor input, instructions, and movement.

Why it matters:

VLA models can include dynamic attention, action timing, sensor paths, safety/control boundaries, and update needs. A partial analog fit does not prove full VLA readiness.

Proof needed:

The package needs VLA partitioning, task accuracy, runtime proof, sensor-path proof, update proof, and safety/fallback evidence before any full-VLA claim.

## USB, Ethernet, PCIe, JTAG, And UART

These are board communication links.

USB is common for early lab control. Ethernet is useful for networked testing. PCIe is a high-speed connection often used by accelerator cards. JTAG is a low-level debug connection for firmware and chip bring-up. UART is a simple serial text connection for early logs.

Why it matters:

The board must expose a way to load packages, control the chip, collect status, and debug failure.

Proof needed:

The board evidence must state which link was used, what speed or mode was used, what command ran, what failed if anything failed, and where logs were saved.

## Evidence Package

The evidence package is the saved record of the review.

It should include what was tested, what was estimated, what was simulated, what compiled, what ran on hardware, what failed, what is missing, what can be safely claimed, and what must not be claimed yet.

Why it matters:

It prevents a demo conversation from turning into unsupported claims later.

Proof needed:

The package must contain a manifest, schema, step artifacts, source notes, import templates, final answer, and archive validation.
