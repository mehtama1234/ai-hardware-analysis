# Analog In-Memory Compute For Foundation Models

Analog in-memory compute starts from one useful physical fact: a programmed conductance multiplied by an applied voltage produces a current. If many such cells share a column, their currents add. That gives a matrix-vector multiply in the same place where the weights are stored.

The object being controlled is therefore not an abstract multiply instruction. It is a current produced by a set of programmed conductances and input voltages. The value is useful only if the current can be read, scaled, corrected, and passed to the next model operation with bounded error.

## The First-Principles Chain

The chain is:

```text
weight number -> programmed conductance -> row voltage -> column current -> ADC code -> corrected digital value -> next model state
```

Each arrow can lose information.

Programming loses information when the device lands at the wrong conductance. Voltage conversion loses information when the DAC has too few levels. Current summation loses information when wires, noise, and device variation change the ideal sum. ADC conversion loses information when many possible currents map to the same code. Digital correction loses information when the measured error is not stable enough to fit.

This is why analog in-memory compute is not simply "matrix multiplication in memory." It is a chain of approximations around one physical advantage: the array can produce many weighted sums with little movement of stored weights.

## Why Foundation Models Are A Hard Target

Foundation models spend much of their compute on dense linear maps. That makes them attractive for analog arrays. But a transformer block also contains operations that are poor analog targets:

- normalization, because scale must be controlled carefully
- softmax, because exponentials and probability normalization need stable range
- KV-cache access, because it is an addressing and memory-traffic problem
- token sampling, because the decision must be exact enough to drive control
- routing, masking, and shape changes, because they are data-dependent

So the useful question is not whether a transformer can run on analog hardware. The useful question is which repeated linear maps can move into analog tiles while the digital system keeps control of the model state.

## What The Lab Shows

The current lab has three levels.

First, SPICE shows a four-by-four crossbar where row voltages create column currents. The column current is the weighted sum. This grounds the idea in circuit behavior rather than metaphor.

Second, the Python analog matrix multiply model adds DAC quantization, ADC quantization, conductance noise, and drift. The ADC sweep shows a clear boundary: with too few bits, the output error is dominated by conversion. With more bits, the error falls until other physical errors matter more.

Third, the calibration experiment adds a digital correction loop. The toy model has stable column gain and offset errors. Fitting a per-column gain and bias reduced mean relative error from about `0.15151` to about `0.05307`. That does not prove a product accelerator. It proves a principle: analog error must be measured and corrected, and the digital side is part of the analog compute system.

## The Architecture Argument

A reasonable hybrid tile has:

```text
activation buffer -> DACs -> conductance arrays -> ADCs -> digital accumulator -> correction -> model state
```

The conductance array is the dense projection engine. The digital accumulator combines partial sums across tiles. The correction block applies measured gain, bias, and scale factors. The scheduler decides when a tensor should enter analog and when it should stay digital.

The strongest candidates are MLP projections and Q/K/V projections. They are large, repeated, and weight-heavy. Low-rank adapters are also good candidates because their matrices are smaller and can be isolated from the most fragile parts of the model.

The weaker candidates are softmax, normalization, KV-cache indexing, and sampling. Those are not primarily stored-weight multiplication problems.

## The Scheduling Boundary

A full model matrix does not fit in one tile. A `4096 -> 16384` MLP-up projection mapped onto `128 x 128` tiles requires 32 row-tile groups and 128 column-tile groups. That is 4096 tiles for that projection if the whole matrix is resident. Each output block must collect partial sums across row tiles. The analog array reduces local multiply work, but the digital machine still schedules activation blocks, ADC reads, accumulation, correction, and output movement.

This matters because foundation-model inference has two different regimes. Prefill processes many prompt tokens and can reuse projection weights heavily. Decode processes one new token at a time and often becomes sensitive to KV-cache reads and small-batch inefficiency. Analog arrays are more plausible when reuse is high enough to pay for conversion and scheduling.

## The Wire Boundary

The ideal equation says every cell on a row sees the same input voltage. A real row is a resistor. Current leaves the row through every programmed cell. That means voltage falls along the row, and cells farther from the driver may receive a smaller input than intended.

This matters because larger arrays improve weight reuse but make the electrical path longer. The architecture trades fewer digital boundaries for harder analog control. A tile is therefore not only a matrix block. It is a physical wire network whose voltage error must stay small enough for calibration and model tolerance.

## The Input Boundary

The input activation is digital before it reaches the array. A DAC must turn that code into a row voltage. If the DAC has few levels, nearby activation values collapse together. If it has gain error, the whole row is scaled. If it has offset error, every column receives a biased contribution from that row. If it has not settled, the array computes with an old or incomplete voltage.

This error is different from ADC error. ADC error happens after the currents have been summed. DAC error happens before the sum, so one row error fans out through every programmed conductance on that row. The input boundary therefore creates correlated output damage.

## The Cost Boundary

Analog arrays can make multiplication cheap while ADCs and DACs make the boundary expensive. The lab's relative energy table is intentionally simple, but it teaches the shape of the problem. As ADC and DAC bit counts rise, conversion cost grows quickly. If the model needs high precision at every boundary, analog compute loses much of its reason to exist.

An ADC is not a box that turns current into truth. A SAR ADC makes one timed comparison per bit. More bits mean more comparison steps and a smaller code interval. If comparator noise or settling error is larger than the interval, the extra bits do not create trustworthy information. They create a more detailed code for a value the circuit did not actually know.

The design move is mixed precision:

- use analog only where bounded error is tolerable
- keep high-control operations digital
- calibrate stable analog errors
- accumulate partial sums digitally
- measure model-level output change, not only circuit-level current error

## The Correction Boundary

Calibration corrects stable gain and offset error. Residual correction handles a different case: a few output channels are much worse than the rest. The digital side can add a sparse correction:

```text
y_final = y_analog + y_residual
```

This is useful only when the residual is small compared with the whole output vector. If every output channel needs correction, the system has rebuilt a digital matrix multiply around an analog approximation. If only the largest errors need correction, the hybrid machine has a real control knob: it can spend digital work where analog damage is largest.

## The Failure Boundary

The failure mode is to treat the crossbar as the whole accelerator. It is not. The crossbar is one physical operator. A foundation-model accelerator is a schedule of memory movement, conversion, accumulation, correction, and control.

The honest claim is narrower and stronger: analog in-memory compute may help when weights are reused heavily, the operation is dense, the acceptable error is known, converters are not dominant, and digital correction can keep the model state coherent.

## Reading Direction

The next paper pass should use the analog in-memory reading map, not a general AI-hardware survey. The sources should be chosen because they explain a specific boundary: device conductance, tile communication, transformer adaptation, attention state, CIM taxonomy, or analog hardware simulation. The output should be paper notes that state what remains analog, what remains digital, and what evidence proves the boundary is controlled.

The first derived theme article is `Analog Compute Is A Boundary Chain`. It connects the six first AIMC paper notes through one claim: the useful unit of analysis is the full chain from digital weight to corrected digital output, not the crossbar current sum by itself.

The second derived theme article is `Prefill And Decode Stress Different Hardware`. It separates foundation-model inference into prompt processing and one-token generation so analog acceleration claims can be evaluated by runtime regime rather than by a single dense-matmul benchmark.

The third derived theme article is `Where Analog Compute Actually Helps`. It partitions transformer work by physical object: fixed dense projections are analog candidates, while changing memory, normalization, softmax, sampling, and control remain digital until measured evidence says otherwise.

The operation partition map is `Transformer Operation Partition For Hybrid AIMC`. It is the concrete checklist for that claim. It walks through embedding lookup, Q/K/V projections, attention scores, masking, softmax, value mixing, MLP projections, normalization, residual addition, KV-cache reads and writes, logits, sampling, adapters, calibration, and tile-health policy. For each operation it states the controlled object, the mathematical form, the hardware home, the evidence needed, and the failure boundary.

The fourth derived theme article is `Attention Is Changing Memory, Not Fixed Weights`. It treats attention as generated token memory under comparison and selection, not as a static trained matrix. This is the next boundary for any claim that analog hardware can accelerate more than dense projections.

The fifth derived theme article is `Softmax Turns Score Error Into Selection Error`. It explains why attention score error must be measured after softmax and value mixing. A small analog dot-product error can be harmless when score margins are large and damaging when two memories are in close competition.

The sixth derived theme article is `Transformer Block Error Is State Drift`. It moves the evidence boundary from isolated dot products to the hidden state after attention, MLP, and residual addition. That is the value the next layer actually receives.

The seventh derived theme article is `Stable Bias Accumulates Across Layers`. It separates random noise from persistent hardware error. A one-layer RMS number can look acceptable while repeated offset, gain error, or uncorrected drift pushes the model state across depth.

The eighth derived theme article is `Calibration Is A Schedule, Not A Single Fix`. It treats correction as a runtime policy: the chip must decide how many calibration samples to spend and how many inference tokens can pass before stale drift becomes too large.

The ninth derived theme article is `Tile Health Monitoring Spends Calibration Where Error Grows`. It turns calibration into a selective control problem: the digital side should rank unhealthy rows, columns, converters, or tiles and spend measurement where it reduces model error most.

The tenth derived theme article is `Analog Serving Policy Decides When To Use The Array`. It puts the previous boundaries into a runtime scheduler: prefill, decode, batched decode, calibration state, tile health, and cache pressure can lead to different execution choices on the same chip.

The eleventh derived theme article is `Hybrid Analog Digital Accelerators Need A Control Plane`. It makes the scheduler explicit. A credible analog foundation-model chip must produce a request-level record: resident weights, tile health, calibration age, converter boundary cost, KV-cache pressure, estimated state error, chosen path, and fallback reason.

The twelfth derived theme article is `Digital Control Logic Makes Analog Compute Checkable`. It moves the serving policy into RTL form. The analog path is no longer only an architecture choice; it becomes a clocked decision with encoded path and reason bits that can be simulated, synthesized, and checked.

The thirteenth derived theme article is `Analog Placement Is Not Analog Acceptance`. It separates two decisions that are often collapsed. The scheduler may decide that a fixed projection is allowed to try analog compute, but the measured tile output still needs zero removal, gain correction, bias correction, residual checking, saturation checking, and a final accept-or-fallback decision.

The fourteenth derived theme article is `Analog Compute Needs A Trust Boundary`. It is the central system argument. Analog compute is not accepted because a scheduler chose it, and it is not rejected because it is imperfect. It becomes useful when the digital machine measures the tile output, corrects stable error, rejects unsafe results, and records the reason before the value enters model state.

The fifteenth derived theme article is `Analog Foundation Models Need A Digital Referee`. It explains the runtime control object behind the current RTL and OpenLane work. The analog array proposes a measured value. The digital referee decides whether that value can enter model state, whether the tile should keep serving, whether it needs recalibration, or whether repeated residual failure should remove it from analog service.

The architecture map is `Hybrid AIMC System Architecture`. It is the review page for the whole analog-plus-digital machine: control plane, scheduler, SRAM, KV cache, DACs, conductance tiles, ADCs, digital accumulation, correction, calibration, and fallback.

The interface spec is `Mixed-Signal Trust Boundary Spec`. It names the concrete packet that crosses from analog measurement into digital control: ADC code, zero correction, gain, bias, residual, calibration age, tile enable, corrected value, valid/fallback bits, and reason code. This is the point where a physical current becomes either model state or a digital fallback.

The next physical-flow article is `Physical Flow Turns Control Logic Into Geometry`. It states the next evidence boundary for the controller: RTL and Yosys lowering are not enough. The control decision must eventually survive floorplanning, placement, routing, clocking, and static timing.
