"""Focused HPCA walkthrough of making vector quantization actually run fast."""

PDF = 'https://arxiv.org/pdf/2503.02236'

VQ_LLM = {
    'id': 'vq-llm-2025',
    'route': 'hpca-2025',
    'title': 'VQ-LLM: make compressed values cheap to fetch and use',
    'identity': 'Zihan Liu and colleagues · VQ-LLM: High-performance Code Generation for Vector Quantization Augmented LLM Inference · HPCA 2025',
    'scope': 'A focused walkthrough of vector-quantization representation, codebook placement, codebook-centered dataflow and fusion, adaptive choices, and reported evaluation. The arXiv version of the HPCA paper was inspected. Results are author-reported and have not been reproduced here. The byte, traffic, and break-even calculations are original teaching models.',
    'lessons': [('s2', 'Representation'), ('s3', 'Memory'), ('s6', 'Compilation'), ('s10', 'Whole-system cost')],
    'blocks': [
        {
            'title': 'Compression changes the lookup problem, not only the stored size',
            'paragraphs': [
                'Vector quantization stores a short index for a group of values. A codebook maps that index back to a representative vector. The index is smaller than the original vector, but the next calculation must still fetch the codebook entry, reconstruct the needed values, and arrange them for the next operation. The saved bytes are therefore only one part of the execution path.',
                'This differs from element-wise quantization. An element-wise format gives each value its own small representation. A vector-quantized format shares information across several values and can preserve accuracy at a lower bit width, but it introduces indexed lookup and reconstruction. The right comparison is not compressed size alone; it is accepted model output, movement, lookup, reconstruction, and computation together.',
                'Original example: 1,000 four-value groups use 1,000 one-byte indices and a 256-entry codebook of four two-byte values, or 3,048 bytes total. A direct two-byte representation of all 4,000 values uses 8,000 bytes. The compressed representation is smaller, but a run that reads every index and then fetches every codebook vector still has a second access stream. This arithmetic describes the representation, not VQ-LLM hardware traffic.',
            ],
            'sources': [(PDF + '#page=1', 'HPCA paper, abstract and introduction: vector quantization, codebooks, and latency boundary'), (PDF + '#page=2', 'HPCA paper, background: quantization and VQ pipeline')],
        },
        {
            'title': 'Put hot codebook entries where the hardware can reach them',
            'paragraphs': [
                'VQ-LLM observes that codebook entries are not all used equally. It reorders entries using offline access-frequency information, then places the hottest entries in thread-local registers, a middle group in shared memory, and the rest in global memory. Registers are close to the executing threads; shared memory is on the GPU but shared by a block; global memory is larger but farther away. This is a placement decision, not a free cache.',
                'The placement has a constraint: registers and shared memory are limited. Using too much can reduce how many thread blocks run at once, called occupancy. Shared memory can also suffer bank conflicts when many threads request locations that map to the same bank. VQ-LLM therefore uses available resource slack and chooses boundaries for register and shared-memory placement rather than putting the whole codebook in the fastest space.',
                'Original break-even example: suppose a cold entry costs 100 units to fetch from global memory, a shared entry costs 20, and a register entry costs 5. Moving one entry to shared memory costs 60 units of setup and it is used 2 times. The placed version costs 60 + 2×20 = 100 units, versus 2×100 = 200 units without placement, so it saves 100 units. If setup instead costs 200 units, placement costs 240 and loses 40. The correct test is setup plus repeated access cost over the expected lifetime, while also counting the occupancy cost of occupying the faster storage.',
            ],
            'sources': [(PDF + '#page=1', 'HPCA paper, introduction: hierarchical codebook placement and resource limits'), (PDF + '#page=6', 'HPCA paper, sections V-A and V-B: hotness, reordering, nreg, nshared, and occupancy')],
        },
        {
            'title': 'Make the codebook and the computation share one traffic plan',
            'paragraphs': [
                'A second source of waste is disagreement between the way codebook entries are loaded and the way the following operation needs reconstructed values. Different thread blocks may load the same entries, and a layout that is convenient for reconstruction may require another write and read before matrix multiplication or attention can use it. VQ-LLM’s codebook-centric dataflow changes the division of work to reduce repeated codebook loads and can split a reduction dimension when that balances the added partial results.',
                'Its hierarchical fusion can keep the reconstructed values in registers and use intra-warp exchange to rearrange them, instead of writing them to shared memory only to read them back in another layout. Fusion helps only when the saved traffic and synchronization cost more than the exchange and register use. The generated kernel is specialized from templates, but adaptive heuristics choose parameters for the VQ configuration and target GPU; this is why the result is a code-generation problem rather than one fixed kernel.',
                'Original traffic model: a baseline loads 12 codebook blocks at 8 units each, then writes and rereads 12 reconstructed blocks at 3 units each, for 168 units. A fused plan loads the same 12 blocks once and rearranges them in registers at 1 unit each, for 108 units, but adds 20 units of coordination. The fused total is 128, saving 40. If the input layout changes and coordination rises to 70, the same fusion loses. The paper’s GPU measurements are not this model.',
            ],
            'sources': [(PDF + '#page=5', 'HPCA paper, sections IV and VI: codebook-centric dataflow and hierarchical fusion'), (PDF + '#page=9', 'HPCA paper, implementation example: register-level exchange and fusion')],
        },
        {
            'title': 'Judge the result at the full inference boundary',
            'paragraphs': [
                'The paper evaluates kernels and then measures an end-to-end generation setting, because a faster matrix operation can disappear inside the rest of inference. In the reported end-to-end setup, batch size is 16, sequence length is 1,024, and 256 tokens are generated. The paper reports an average 46.13% latency reduction over its unoptimized versions, about 1.9× speedup, and compares against element-wise quantization at equivalent bit widths. These are results under the paper’s models, GPUs, VQ algorithms, baselines, software, and measurement procedure.',
                'The reported comparison answers two different questions. The paper finds that the optimized VQ kernels can be close to or faster than element-wise quantization in its tested cases, while a GeMM kernel can still be slower than an FP16 baseline because the baseline’s tiling is highly optimized. The end-to-end result is about the complete sequence of operators, not a promise that every individual kernel beats FP16. The paper also reports a roughly 2.2× end-to-end improvement over FP16 in its equivalent 4-bit comparison and about a 2.5 percentage-point accuracy advantage over qServe on arc-challenge; those remain author-reported measurements.',
                'A deployment check should therefore record model quality, memory use, prompt and decode timing, batch and sequence lengths, all operators, quantization preparation, and the comparison baseline. A lower memory footprint can be valuable even when a particular kernel is slower. This walkthrough has not reproduced VQ-LLM’s GPU experiments, and its teaching arithmetic is not a measurement from the paper.',
            ],
            'sources': [(PDF + '#page=10', 'HPCA paper, sections VII-B and VII-D: kernel and element-wise comparisons'), (PDF + '#page=11', 'HPCA paper, sections VII-E and VII-F: end-to-end results, accuracy, memory, and overhead')],
        },
    ],
    'exercise': {
        'question': 'A baseline spends 120 units loading codebook data and 48 units writing and rereading reconstructed values. A fused plan spends 120 units loading, 12 units on register exchange, and 20 units on coordination. What is the saving? If coordination rises to 60 units for another layout, does fusion still help?',
        'answer': 'The baseline costs 120 + 48 = 168 units. The first fused plan costs 120 + 12 + 20 = 152 units, saving 16. With the other layout it costs 120 + 12 + 60 = 192, so it loses by 24. This original teaching model shows why fusion must be evaluated with the actual layout and coordination cost; it is not a VQ-LLM measurement.',
    },
}
