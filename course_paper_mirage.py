"""Focused OSDI walkthrough of multi-level tensor-program optimization."""

PDF = 'https://www.wisdom.weizmann.ac.il/~padon/mirage-osdi2025.pdf'

MIRAGE = {
    'id': 'mirage-2025',
    'route': 'osdi-2025',
    'title': 'Mirage: search across the GPU levels without losing the computation',
    'identity': 'Mengdi Wu, Xinhao Cheng, Shengyu Liu, and colleagues · Mirage: A Multi-Level Superoptimizer for Tensor Programs · OSDI 2025',
    'scope': 'A focused walkthrough of Mirage’s multi-level graph, search pruning, equivalence checks, and reported GPU evaluation. The author-hosted OSDI paper was inspected. Results are author-reported and have not been reproduced here. The small schedules and algebraic examples are original teaching models.',
    'lessons': [('s6', 'Execution plans'), ('s3', 'Memory and movement'), ('s8', 'Correctness evidence'), ('dependencies-and-pipelines', 'Dependencies'), ('s10', 'Whole-system results')],
    'blocks': [
        {
            'title': 'A tensor program has more than one execution level',
            'paragraphs': [
                'A tensor program says which arrays are combined, but a GPU also needs a plan for where that work runs. A kernel runs across the GPU, a thread block runs on one streaming multiprocessor, and individual threads perform smaller pieces using registers. Shared memory sits between the last two levels. Choosing only the mathematical operations leaves unanswered which values travel through device memory, which stay nearby, and how many threads cooperate.',
                'Mirage represents one plan as a hierarchical µGraph: a kernel graph, block graphs, and thread graphs. This lets it search for changes such as fusing operations, keeping an intermediate in shared memory, changing the grid and loop mapping, and assigning work to threads. The levels are connected: a plan that looks efficient in a thread is invalid if its block cannot supply the value or its kernel creates an expensive device-memory transfer.',
                'Use a simple two-stage example. A normalization produces an intermediate array and a matrix operation consumes it. Two separate kernels write the intermediate to device memory and read it back. A fused kernel can keep the value inside the block, but only if the required pieces are produced by the same block or can be exchanged legally. Fusion removes a transfer and a launch; it does not remove the data dependency or guarantee that the intermediate fits in shared memory.',
            ],
            'sources': [(PDF + '#page=3', 'OSDI paper, section 2: GPU hierarchy and µGraph levels')],
        },
        {
            'title': 'Search a large space by rejecting plans that cannot matter',
            'paragraphs': [
                'Searching every possible mapping, fusion, layout, and synchronization choice is too large to try blindly. Mirage builds candidate graphs from the input program and uses abstract expressions to prune a partial plan when its intermediate expression cannot contribute to the desired output. For X·Z + Y·Z, a partial plan that computes X·Y cannot contribute to this output; a plan that computes X+Y may still contribute in another legal rearrangement. The pruning rule must preserve possibilities, not merely favor a familiar shape.',
                'Mirage searches exhaustively at the kernel and block levels, where memory movement matters most, and uses a rule-based strategy at the thread level. The paper explains the reason in physical terms: device and shared-memory access costs far more than a register access. This is not a claim that thread-level choices never matter. It is a search-budget decision about where exhaustive exploration buys the most likely gain.',
                'Original search arithmetic: suppose a naive search has 100 kernel choices, 20 block choices, and 8 thread choices, or 16,000 combinations. If a safe abstract-expression test rejects 60% of kernel prefixes before the lower levels are expanded, 6,400 combinations remain. The test itself has a cost, and a wrong rejection can hide the best plan. The numbers illustrate the accounting; they are not Mirage measurements.',
            ],
            'sources': [(PDF + '#page=6', 'OSDI paper, sections 4 and 4.3: graph generation and abstract-expression pruning')],
        },
        {
            'title': 'Check equivalence before trusting a faster plan',
            'paragraphs': [
                'A faster kernel that computes a different result is not an optimization of the same program. Mirage’s probabilistic verifier evaluates the original and candidate programs on random inputs in two finite fields. Finite-field arithmetic avoids floating-point rounding during this check, and the paper gives a probability bound on accepting a non-equivalent candidate when the test conditions are met. This is evidence about functional equivalence under the verifier’s model, not a performance measurement.',
                'The boundary matters. The probabilistic verifier is for LAX programs and does not support some operators such as ReLU. Mirage also has a solver-based verifier for broader programs, but it needs user-provided mathematical properties such as linearity or associativity. The authors state that the search procedure does not introduce false negatives, could theoretically allow false positives, and had not observed any in practice; they planned a final stronger verification for the best graph. A reader should preserve those qualifications rather than saying “the compiler proves every output.”',
                'Consider an invented integer operation that returns (x+y)−y. Replacing it with x is legal under ordinary exact arithmetic, but a check must state the arithmetic domain. With fixed-width overflow, intermediate evaluation can wrap and the two forms may differ. A verifier that proves equivalence in one domain does not automatically prove equivalence in another. The data type and operator rules belong in the claim.',
            ],
            'sources': [(PDF + '#page=8', 'OSDI paper, section 5: probabilistic equivalence verification'), (PDF + '#page=10', 'OSDI paper, section 7: verifier limits and implementation boundary')],
        },
        {
            'title': 'The best graph still needs layout, memory, and generated code',
            'paragraphs': [
                'After Mirage finds a verified µGraph, it applies layout, operator-scheduling, and memory-planning optimizations. Layout chooses how tensor dimensions map to GPU threads and blocks. Scheduling decides when operations run and where synchronization is needed. Memory planning assigns storage offsets to intermediate tensors. These are separate choices: a graph can have the right operations but an unfortunate layout, or a good layout that needs too much temporary storage.',
                'The system is implemented in C++, CUDA, and Python and emits CUDA source for custom kernels, which the CUDA compiler then turns into a binary. It can integrate generated kernels into a PyTorch program with a small code change, but generation and just-in-time compilation are part of the deployment story. A one-time compilation cost may be acceptable for a long-running service and unacceptable for a short job or rapidly changing shape.',
                'Original break-even model: a hand-written path takes 12 ms per request. Mirage’s generated path takes 7 ms but requires 500 ms of search and compilation. It breaks even after 500/(12−7) = 100 requests, assuming the same shape, no invalidation, and no extra memory cost. If the shape changes after 40 requests, the preparation has not paid back. “Faster kernel” and “faster application” require different boundaries.',
            ],
            'sources': [(PDF + '#page=10', 'OSDI paper, section 7: implementation, code generation, JIT compilation, and memory planning')],
        },
        {
            'title': 'Read the speedups with the benchmark and hardware attached',
            'paragraphs': [
                'The paper evaluates six DNN-oriented programs, including GQA (grouped-query attention), QKNorm, RMSNorm, LoRA (low-rank adaptation), GatedMLP, and nTrans, with stated context lengths for the larger attention cases. It compares generated kernels with existing systems on NVIDIA A100 and H100 GPUs. The paper reports up to 3.3× improvement over existing tensor-program optimizers, and its running examples include 1.5× on A100 and 1.9× on H100 for the fused RMSNorm-and-matrix-operation graph. Those are measured results for the listed programs, shapes, batch sizes, baselines, and GPUs.',
                'The result is not uniformly positive. The paper’s figure reports different ratios at batch sizes 1, 8, and 16; for example, its GQA and GatedMLP results vary with batch size, and nTrans is below one for the shown comparisons. The paper explains that light computation can lose when graph-defined kernels move data through shared memory unnecessarily. A system that fuses everything can therefore be slower when the saved launch or device-memory work is smaller than the added movement.',
                'A follow-up experiment should hold the program, shape, output check, GPU, and baseline fixed while varying batch size and whether intermediates fit in shared memory. Report search time, compilation time, steady-state latency, and memory use separately. The course has not rerun Mirage or generated its kernels; this walkthrough teaches how to read the paper’s optimization and evidence chain without turning the largest multiplier into a universal prediction.',
            ],
            'sources': [(PDF + '#page=10', 'OSDI paper, section 8.1: benchmark and hardware setup'), (PDF + '#page=11', 'OSDI paper, evaluation figures: batch-size and GPU-specific performance')],
        },
    ],
    'exercise': {
        'question': 'A generated kernel saves 5 ms per request but takes 500 ms to search and compile. After how many identical requests does it break even against a 12-ms baseline? What evidence would you need before applying that result to a changing input shape?',
        'answer': 'The saving is 12−7 = 5 ms per request, so 500/5 = 100 requests are needed to break even under the stated assumptions. A changing shape may invalidate the generated plan and require new search or compilation. Check shape coverage, output equivalence, preparation time, memory use, and complete request latency; the calculation is an original teaching model, not a Mirage measurement.',
    },
}
