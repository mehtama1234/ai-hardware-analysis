# BROCA: A Low-power and Low-latency Conversational Agent RISC-V System-on-Chip for Voice-interactive Mobile Devices

**Venue:** HOTCHIPS  
**Confidence:** low (abstract-only)

## Problem
Mobile voice assistants require on-device AI inference with sub-100ms latency and minimal power consumption; BROCA targets running conversational agent models (speech recognition + NLU + TTS) entirely on mobile SoC.

## Motivation
Cloud-based voice assistants suffer from network latency and privacy concerns; edge inference on mobile devices requires low-power, real-time capable SoCs balancing compute for ML and traditional mobile workloads.

## Method
BROCA implements a RISC-V SoC with specialized accelerators for speech processing (DSP-like vector units), low-latency AI inference (likely quantized transformer acceleration), and integrated audio I/O, optimized for the speech-to-speech latency critical to voice interaction.

## Key Novelty
Low-power RISC-V SoC with integrated voice AI acceleration enabling real-time conversational agent inference on mobile devices.

## Contributions
- RISC-V-based SoC for voice-interactive mobile AI
- Specialized DSP/vector acceleration for speech processing
- Low-latency AI inference accelerator for transformer models
- Integrated audio I/O with sub-100ms end-to-end latency

## Hardware Targets
SoC, RISC-V

## Techniques
circuit-design, parallelism, power

## Workloads
speech, transformer, LLM-inference

## Metrics
- Latency: sub-100ms speech-to-speech latency
- Energy: low-power operation for mobile battery life

## Baselines
Mobile CPU inference, cloud-based voice assistants, traditional mobile SoCs

## Limitations
Not discussed.

## Tags
voice-assistant, risc-v, soc, low-latency, mobile, speech-ai
