# Balancing Pipeline Parallelism with Vocabulary Parallelism

**Venue:** MLSYS 2025 · **Subtheme:** Communication Optimization for Distributed LLM Training

## What It Does

In pipeline-parallel LLM training, the model is vertically split across GPUs (early layers on GPU 0, middle on GPU 1, late on GPU 2, etc.) to reduce memory pressure and increase throughput through microbatching. However, embedding and output projection layers — especially with large vocabularies (32K-200K tokens) — contain massive parameter matrices (e.g., embedding: [200K vocab, 12288 hidden dims] = 2.4B parameters, output projection: [12288, 200K] = 2.4B parameters). When both are placed on the first/last pipeline stage, they create severe compute and memory imbalance: the first stage must compute the vocabulary embedding (expensive matrix-multiply), causing pipeline bubbles while other stages wait. Vocabulary Parallelism (VP) partitions the embedding and output layers evenly across all pipeline stages. For example, in a 4-stage pipeline: stage 0 computes embedding[:50K], stage 1 computes embedding[50K:100K], stage 2 computes embedding[100K:150K], stage 3 computes embedding[150K:200K]. This requires new forward and backward pass algorithms. **Algorithm 1** performs forward pass separately on each stage (each produces a partial embedding), then communicates results via all-reduce to gather the complete embedding, followed by standard transformer layers. Backward pass reverses this: each stage computes gradients for its partition, all-reduce sums them, each stage updates its partition. This reduces communication barriers from 3 to 2. **Algorithm 2** further optimizes by fusing online softmax (computing softmax incrementally as partial results arrive) with pre-computed gradient partial sums, reducing barriers to just 1. The result is that embedding computation no longer blocks the pipeline and load is perfectly balanced across stages.

Data flow (Algorithm 2): Token IDs → Stage 0 computes embedding[:50K] (partial emb₀) in parallel with Stages 1-3 computing transformer layers downstream → all-reduce gathers partial embeddings → fused softmax computes final embedding → backward pass reuses partial gradients, reducing communication stalls.

## The Key Result

On LLM pre-training with large vocabularies (32K-200K tokens), Vocabulary Parallelism achieves 5% to 51% throughput improvement versus naive pipeline parallelism (vocabulary on one stage). Algorithm 2 reduces communication barriers from 3 to 1. When combined with the V-Half pipeline schedule (which overlaps forward and backward passes), VP achieves perfect compute and memory balance across all pipeline stages with only small constant overhead in activation memory.

## Why This Approach

Pipeline parallelism is the standard scaling mechanism for LLM training (Megatron-LM, NVIDIA Transformer Engine, etc.), but the vocabulary layers (embedding and output projection) are a structural bottleneck. Concentrating them on one stage creates severe imbalance because vocabulary size is often 10-100× larger than hidden dimension. The alternative approaches don't work: (1) Tensor parallelism on vocabulary layers alone adds fine-grained all-reduce synchronization that is more expensive than piping; (2) sequence parallelism requires chunking sequences, adding communication per token; (3) data parallelism requires duplicating all parameters, negating memory savings. VP's insight is that vocabulary projection is associative and can be partitioned — each partition computes a subset of token embeddings independently, then results are combined via all-reduce. By combining this with online softmax (a streaming algorithm that computes softmax correctly from partial sums), VP eliminates the need for a third synchronization point, keeping the pipeline full. This is especially powerful because vocabulary size is typically constant regardless of model scale, making VP applicable to all LLM scales.

## What It Leaves Open

- Small but measurable activation memory overhead from storing partial embeddings; impact on memory-constrained training (very large models with aggressive gradient checkpointing) not fully explored.
- Communication pattern becomes more complex (all-reduce after embedding); scalability beyond 8-16 pipeline stages and how all-reduce tree algorithms (binomial, etc.) interact with NVLink topology is not analyzed.
- Benefit scales with vocabulary size; for small vocabularies (8K tokens) or shared embedding-output layers, gain is marginal; no guidance on when to apply VP.
- Requires modification to pipeline scheduler logic; implementation complexity and engineering effort to integrate into existing frameworks (Megatron, vLLM) not addressed.
- No evaluation with dynamic vocabularies or sparse token distributions (common in multilingual models); assumes uniform vocabulary access patterns.
