# Self-Data Distillation for Recovering Quality in Pruned Large Language Models

**Venue:** MLSYS 2025 · **Subtheme:** Catastrophic Forgetting Mitigation in Structured Pruning

## What It Does

This work addresses catastrophic forgetting in structured depth pruning of LLMs: removing decoder blocks (e.g., reducing a 32-layer Llama from 32 to 26 layers) degrades accuracy, and naive supervised fine-tuning (SFT) on the original fine-tuning dataset worsens forgetting because the pruned model now produces different outputs than the original.

The method uses angular cosine distance between consecutive transformer block outputs to identify redundant layers: layers with minimal output differences are pruned first. The unpruned model then rewrites the fine-tuning dataset by generating new target responses for each prompt, preserving semantic richness while remaining compatible with the pruned model's reduced capacity. Conditional selection keeps original responses for prompts where the pruned model already performs adequately. The pruned model is fine-tuned on this "self-distilled" dataset.

Post-training recovery uses SLERP (spherical linear interpolation) to blend pruned and unpruned model checkpoints in weight space, smoothing the transition. Additionally, the pruned model can be deployed as a speculative decoding draft model paired with the full model as verifier, recovering inference speed without accuracy loss.

## The Key Result

On Llama3.1-8B with 6 decoder blocks pruned (from 32 to 26), the method achieves 91.24% accuracy retention versus 81.66% for standard SFT on OpenLLM Leaderboard v1. In speculative decoding, the pruned model achieves 1.70 average accepted token length at block size 10.

## Why This Approach

Depth pruning removes entire layers, but the pruned model's internal representations differ from the original, so when SFT on the original dataset is applied, the distribution shift causes severe forgetting. Prior methods (LLM-Pruner, ShortGPT, FLAP) use heuristic pruning or require extensive post-training, lacking recovery mechanisms. Self-data distillation exploits the unpruned model as an oracle: it knows the semantic intent of each prompt and can generate responses that the pruned model should learn to imitate. By using the unpruned model's responses as SFT targets, the pruned model learns to compress knowledge into fewer layers while preserving semantic richness. Conditional selection further improves efficiency by not distilling prompts where the pruned model is already competent.

Angular cosine distance for layer selection is a simple, trainable metric: layers with outputs closest in cosine distance (most aligned) are redundant and best candidates for removal. This is faster to compute than full-model quality evaluation per layer.

## Why This Approach

SLERP model merging blends weight vectors in spherical space, which better preserves directional information than linear interpolation in weight space. This smooths the transition between pruned and unpruned models, extracting additional quality from both checkpoints.

## What It Leaves Open

- Self-data distillation requires running inference on the full unpruned model, incurring substantial generation cost during the SFT dataset preparation phase; this cost is not quantified or amortized across the accuracy gain.
- Angular cosine distance metric captures output alignment but may miss structural information relevant to pruning (e.g., layer roles in different tasks); metric optimality not proven.
- Evaluation primarily on Llama3.1-8B and Mistral-7B (7-8B scale); behavior on larger models (70B+) or smaller models (3B) unknown—pruning tolerance and forgetting patterns may differ at different scales.
- Conditional selection heuristic (when to keep original responses) not detailed; sensitivity to this threshold not characterized.
- Speculative decoding application assumes runtime access to full model; applicability to edge/mobile inference of pruned models unclear.
