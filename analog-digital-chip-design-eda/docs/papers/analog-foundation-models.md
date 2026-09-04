# Analog Foundation Models

## Bibliographic Identity

- Title: Analog Foundation Models
- Year: 2025
- Venue or source: arXiv
- Link: https://arxiv.org/abs/2505.09663
- Track: digital-design-and-architecture
- Subtheme: model adaptation for analog in-memory hardware

## First-Principles Reading

The object being controlled is language-model behavior after the model is forced through analog hardware constraints. The weights and activations no longer pass through exact digital arithmetic. They pass through noisy, low-precision analog approximations.

The constraint is that a pretrained LLM was not trained to survive this boundary. Input quantization, output quantization, analog noise, and limited precision can change hidden states enough to damage the next-token distribution. The hard object is not one matrix product. It is the residual stream after many approximated layers.

The mathematical form is robust adaptation under perturbation: `h_next = f((W + delta_W)(h + delta_h) + delta_readout)`. The method is to adapt foundation models under analog-like noise and quantization so their internal representations tolerate the hardware path.

The evidence artifact is benchmark behavior under analog constraints and comparison against low-bit digital baselines. The failure boundary is that simulated hardware is not silicon. The method still needs measured device drift, converter behavior, tile scheduling, and calibration evidence before it proves a deployable chip.

## Concept Links

Related concept articles:

- adc-dac-boundaries-set-analog-compute-cost
- dacs-turn-activation-codes-into-row-voltages
- sar-adcs-turn-current-into-a-timed-digital-decision
- hybrid-foundation-model-accelerators-are-partitioning-problems
- where-analog-compute-actually-helps
- transformer-block-error-is-state-drift
- calibration-is-a-schedule-not-a-single-fix
- tile-health-monitoring-spends-calibration-where-error-grows
- analog-serving-policy-decides-when-to-use-the-array
- hybrid-analog-digital-accelerators-need-a-control-plane

Related labs:

- labs/analog/analog-in-memory-foundation-model-hardware

## What The Paper Teaches

The lesson is that analog hardware can be handled partly by changing the model. Calibration corrects the machine; adaptation changes the computation so the model is less fragile to the machine. For foundation models, that distinction matters because the error is carried through many layers before it becomes a visible output.
