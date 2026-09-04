# Analog In-Memory Foundation-Model Reading Map

This reading map is for papers and tools that explain whether analog in-memory compute can run useful parts of foundation-model inference. The goal is not to collect optimistic accelerator claims. Each source must be read through the same boundary chain:

```text
digital weight -> programmed conductance or memory state -> row input signal -> analog accumulation -> ADC/readout -> digital correction -> model output
```

The paper is valuable only if it makes at least one part of that chain clearer.

## Source Targets

### Analog AI Chip For Neural Inference

Primary source: IBM/Nature 2023 analog-AI chip paper, "An analog-AI chip for energy-efficient speech recognition and transcription."

Read it for the physical machine. The controlled object is not an abstract model layer; it is many phase-change memory devices arranged across tiles. The important question is how the paper moves from cell conductance to tile communication to chip-level accuracy. The paper is useful because it forces the architecture question: software-equivalent behavior requires not only local analog multiply but also activation movement, peripheral circuits, and inter-tile communication.

First-principles questions:

- What is stored in the memory device?
- How are signed or multi-bit weights represented?
- What does the peripheral circuit measure?
- What has to be digital for the chip to preserve model behavior?
- Where does energy go after the array operation is counted?

### Analog Foundation Models

Primary source: "Analog Foundation Models."

Read it for model adaptation. The controlled object is a pretrained language model under analog hardware noise and quantization constraints. The paper matters because it treats analog deployment as a training and robustness problem, not only a circuit mapping problem. The key question is why off-the-shelf LLMs fail under analog constraints and what training changes make the residual stream tolerate the hardware.

First-principles questions:

- Which errors come from weights, inputs, outputs, or accumulation?
- What does the adaptation method make invariant?
- Does the method correct the hardware, the model, or both?
- Which model sizes and layer types are tested?
- What failure remains compared with digital low-bit inference?

### Efficient Transformer Adaptation For AIMC

Primary source: "Efficient Deployment of Transformer Models in Analog In-Memory Computing Hardware."

Read it for hybrid partitioning. The controlled object is a transformer deployed onto AIMC while lightweight digital adapters compensate for analog constraints. The paper matters because it does not pretend the whole model becomes analog. It puts adaptation capacity in digital cores and lets analog hardware carry dense projection work.

First-principles questions:

- Which tensors go through AIMC?
- Which corrections remain digital?
- Why are low-rank adapters enough or not enough?
- How is tile latency balanced against digital adapter latency?
- What would break during decode versus prefill?

### AIMC Attention With Gain Cells

Primary source: "Analog In-Memory Computing Attention Mechanism for Fast and Energy-Efficient Large Language Models."

Read it for attention rather than static weights. The controlled object is not only a fixed trained matrix; it is token-dependent attention data that changes during generation. This is important because KV-cache behavior is one of the main reasons foundation models are not just repeated static projections.

First-principles questions:

- What memory state is written during generation?
- How does the design compute attention dot products?
- What attention window or approximation is assumed?
- Which analog nonidealities prevent direct mapping of pretrained models?
- What part of attention remains digital?

### Compute-In-Memory For LLM Inference Survey

Primary source: "Memory Is All You Need: An Overview of Compute-in-Memory Architectures for Accelerating Large Language Model Inference."

Read it as the taxonomy page. The controlled object is the whole inference workload: weights, activations, KV cache, operators, and memory traffic. The survey matters because it separates different compute-in-memory approaches instead of treating all memory-side computation as the same thing.

First-principles questions:

- Which transformer operators are memory-bound?
- Which CIM types are analog and which are digital?
- Which claims target prefill, decode, or both?
- What assumptions are made about batch size and sequence length?
- Where do ADCs, DACs, and peripheral circuits enter the cost?

### AIHWKit And Analog Hardware Simulation

Primary source: IBM AIHWKit documentation and code.

Read it for simulation discipline. The controlled object is a software model of analog hardware behavior: device noise, update noise, drift, quantization, and inference-time nonidealities. This is useful because our lab should not jump from ideal SPICE toy arrays to architecture claims. It needs a middle layer where model behavior is tested under measured-like noise.

First-principles questions:

- Which device errors are modeled?
- Which errors are static and which change over time?
- How does training or inference absorb those errors?
- What assumptions are made about ADC/DAC precision?
- Can the simulator reproduce our toy experiments before we scale?

## What We Should Write From These Sources

The next paper notes should not be summaries. Each should answer:

1. What physical or mathematical object is controlled?
2. What boundary makes the object hard to control?
3. What concrete method changes the object?
4. What evidence shows the method worked?
5. What remains digital?
6. What failure boundary remains?

## Theme Articles To Derive

Write these after the first paper-note batch:

- Analog compute is a boundary chain, not a matrix multiply claim.
- Foundation-model inference has two regimes: prefill reuse and decode memory pressure.
- Signed weights require physical representation, not just negative numbers.
- ADC/DAC precision is a model-layer decision.
- Calibration is evidence that the physical machine is still the intended machine.
- KV cache is the part of transformer inference that resists static analog mapping.
- Hybrid accelerators are schedules over unlike error sources.

## Source Links

- https://www.nature.com/articles/s41586-023-06337-5
- https://arxiv.org/abs/2505.09663
- https://arxiv.org/abs/2411.17367
- https://arxiv.org/abs/2409.19315
- https://arxiv.org/abs/2406.08413
- https://aihwkit.readthedocs.io/en/v0.3.0/analog_ai.html
