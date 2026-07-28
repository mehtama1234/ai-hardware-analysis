# Marconi: Prefix Caching for the Era of Hybrid LLMs

**Venue:** MLSYS 2025 · **Theme:** Prefix Cache Reuse

## What It Does

Hybrid LLMs combining Attention and SSM (State Space Model / Mamba) recurrent layers cannot use standard prefix caching because SSM layers use in-place state updates that preclude rolling back to partial sequence states; only exact-match cache hits are possible, causing an explosion in cache entries with low reuse, wasting memory and compute.

Pure-attention LLMs benefit from prefix caching (e.g., vLLM radix cache) because any prefix of a cached sequence can be reused. Hybrid LLMs break this because SSM state at token i depends on all tokens 1..i via recurrent updates; you cannot restore a mid-sequence SSM state without recomputing from the start. The correct caching unit changes: only checkpointed SSM states at token boundaries matter. Naive policies that treat all prefixes equally fill cache with entries that are unlikely to reuse.

Marconi maintains a unified radix tree storing both KV-cache blocks (for attention layers) and SSM state checkpoints (for recurrent layers) per sequence. Two key policies: (1) Admission: speculative insertion before prefill execution identifies branch points in the radix tree where SSM state checkpointing is needed; admits only entries in two reuse classes - (a) purely-input shared prefixes (system prompts, shared context) and (b) input+output prefixes (multi-turn conversation history). Entries not in these classes are rejected at admission time. (2) FLOP-aware eviction: utility score S(n) = recency(n) + alpha * flop_efficiency(n), where flop_efficiency(n) = FLOPs_saved_by_hit / bytes_of_cache_entry; alpha is tuned via grid search on a bootstrap period. Only leaf nodes and single-child intermediate nodes are eligible for eviction (evicting a branching node would invalidate its subtree). This prevents eviction cascades while prioritizing high-FLOP-return entries.

## The Key Experiment

- **token hit rate:** up to 34.4x higher token hit rates vs state-of-the-art prefix caching (vLLM+)
- **ttft reduction pct:** 71.1% lower P95 Time-To-First-Token vs vLLM+
- **ttft reduction abs:** 617 ms lower P95 TTFT vs vLLM+

**Compared against:** vLLM+ radix cache (attention-only prefix caching applied naively to hybrid models); LRU eviction without FLOP-awareness; No prefix caching

**Hardware:** NVIDIA GPU (A100, H100) · **Workloads:** llm-inference; long-context-inference; conversational-inference; hybrid-llm

## Why This Approach

First prefix caching system for hybrid Attention+SSM LLMs; FLOP-aware eviction metric (FLOPs saved per cache byte) that jointly considers compute savings and memory cost of cached states; speculative admission before prefill that identifies SSM checkpointing points without executing the model.

This paper sits in the **attention efficiency** subtheme. The core constraint: generating one token requires reading all past key-value vectors from memory — O(n) bandwidth per step. This paper's angle: First prefix caching system supporting hybrid Attention+SSM LLMs (Mamba, Jamba, etc.).

## What It Leaves Open

- SSM state checkpoints are large (proportional to state dimension times number of recurrent layers), consuming substantial cache memory
- Exact-match-only constraint means partial prefix overlaps yield zero reuse, unlike attention-only models
- Bootstrap period for alpha tuning requires representative workload samples before optimal eviction policy is active
- Speculative admission overhead not fully quantified for highly dynamic request patterns

**Tags:** prefix-caching, hybrid-LLM, SSM, Mamba, FLOP-aware-eviction, radix-tree, KV-cache
