"""Focused MLSys walkthrough of extreme MoE quantization and its kernel cost."""

PDF = 'https://proceedings.mlsys.org/paper_files/paper/2025/file/9032e5c9ec394ce768a2fa9bdc56af6c-Paper-Conference.pdf'

MILO = {
    'id': 'milo-2025',
    'route': 'mlsys-2025',
    'title': 'MiLo: recover useful detail after pushing MoE weights to three bits',
    'identity': 'Beichen Huang, Yueming Yuan, Zelei Shao, Minjia Zhang · MiLo: Efficient Quantized MoE Inference with Mixture of Low-Rank Compensators · MLSys 2025',
    'scope': 'A focused walkthrough of the quantize-then-compensate idea, adaptive rank choices, the mixed-precision kernel, and the paper’s measured evaluation. The results are author-reported and have not been reproduced here. The small matrix examples are original teaching models, not MiLo measurements.',
    'lessons': [('s2', 'Number representations'), ('s3', 'Memory and movement'), ('s6', 'Execution plans'), ('s8', 'Quality evidence'), ('s10', 'Whole-system results')],
    'blocks': [
        {
            'title': 'Fewer bits solve one problem and create another',
            'paragraphs': [
                'A model weight is a number used by the next calculation. Quantization stores that number using fewer bits and later reconstructs an approximation. Three bits can reduce weight traffic and storage compared with sixteen-bit weights, but the allowed values are farther apart. In a mixture-of-experts model, the total collection of weights is large even though each input uses only some expert blocks. That makes storage important while leaving the output sensitive to errors in the blocks that are selected.',
                'The paper’s starting comparison makes the trade concrete. On WikiText-2, direct INT3 quantization raises Mixtral-8×7B perplexity from 3.42 in FP16 to 4.81 with round-to-nearest and 4.61 with GPTQ. Perplexity is a next-token prediction measure; lower is better for this test, but it is not a complete quality guarantee. INT4 is much closer in that table. A smaller weight file is therefore not yet a successful deployment: the accepted output rule must survive the changed numbers.',
                'Use a two-number teaching model. Suppose the original weights are 1.0 and 1.2, while three-bit reconstruction gives 0.9 and 1.3. A calculation that adds them changes from 2.2 to 2.2, hiding the individual errors. A second calculation that subtracts them changes from −0.2 to −0.4. Agreement on one output does not establish agreement on all inputs or layers. The example is invented; it shows why an average-looking result cannot replace a stated quality test.',
            ],
            'sources': [(PDF + '#page=2', 'Conference paper, Table 1 and introduction: INT3 quality and quantization tradeoffs')],
        },
        {
            'title': 'Store a small correction for the detail quantization lost',
            'paragraphs': [
                'MiLo first quantizes a weight matrix, then stores a low-rank correction for the remaining error. If the original matrix is W and the reconstructed quantized matrix is Q⁻¹(Wq), the teaching form is W ≈ Q⁻¹(Wq) + UV. U and V are smaller matrices whose inner dimension is the chosen rank. This does not restore every discarded value exactly; it spends a limited amount of extra storage on the largest useful patterns in the error.',
                'A rank-1 correction for a 4-by-4 matrix uses 4 + 4 values instead of the sixteen entries in a full correction. If each stored value uses the same cost, it uses half as many correction values. Rank 2 uses sixteen values and loses that storage advantage. The choice is therefore a three-way decision: bits saved in the main weights, rank used for the correction, and quality recovered by the combination. A low-rank correction is not free memory and not a general exact backup.',
                'The paper does not use one rank everywhere. Its observations distinguish dense layers from sparse expert layers, weight distributions with different tail behavior, and experts used at different frequencies. MiLo can assign more rank to dense layers, to weights with higher kurtosis—a measure that emphasizes extreme values—or to experts selected more often. DeepSeek-MoE’s uneven expert use makes frequency a useful policy in the paper’s tested setting; that does not make frequency the right signal for a different routing pattern.',
            ],
            'sources': [(PDF + '#page=4', 'Conference paper, sections 3.1.2–3.2: residual correction and optimization'), (PDF + '#page=6', 'Conference paper, section 3.2.5: adaptive rank policies')],
        },
        {
            'title': 'Optimize the two parts together, then stop with a rule',
            'paragraphs': [
                'If the quantized weights are chosen first and the correction is fitted afterward, the two representations can waste space correcting one another. MiLo alternates between updating the quantized weights and fitting the low-rank correction. The goal is to reduce the remaining matrix error without fine-tuning the whole language model. This is a preparation step performed before serving, not an operation that disappears from the system’s total cost.',
                'The paper measures the remaining matrix error with a Frobenius norm, the square-root of the summed squared entry errors. That is an optimization signal, not the same thing as language-model perplexity or task accuracy. The authors use a three-iteration sliding average, stop when its relative improvement falls below 10⁻⁴, and cap the process at twenty iterations in the reported experiments. A stopping rule prevents “more optimization” from being treated as automatically better or free.',
                'Suppose a toy preparation run costs 3 seconds for quantization and 0.4 seconds per alternating iteration. Ten iterations cost 7 seconds before any serving request arrives. If the prepared model serves 1,000 requests, that is 7 milliseconds per request when preparation is charged across the batch. For ten requests it is 700 milliseconds each. The same compressed representation can be worthwhile at one deployment scale and not another; online latency alone hides this choice.',
            ],
            'sources': [(PDF + '#page=5', 'Conference paper, sections 3.2.3–3.2.4: low-rank fitting, error measure, and stopping rule')],
        },
        {
            'title': 'Make the three-bit representation usable by the processor',
            'paragraphs': [
                'A bit count becomes a speed result only when the processor can fetch, unpack, convert, and multiply the representation efficiently. MiLo supplies an INT3-by-FP16 matrix-multiplication kernel for batched inference. It packs three-bit weights without unused padding bits, performs binary-manipulation-based dequantization, and pipelines several stages so weight loading can overlap calculation. These details address the work added by a tiny representation; they are not optional implementation polish.',
                'The comparison also depends on the baseline’s capabilities. In the paper’s end-to-end test, GPTQ’s three-bit backend supports batch size one but not larger batches. MARLIN uses an optimized INT4 path. MiLo uses asymmetric quantization with group size 64 in that comparison; this improves its quality setting but adds computation. Its fused dequantization and matrix multiplication avoid an extra round trip through global GPU memory. Comparing only “three bits versus four bits” would hide these different kernels and settings.',
                'The same principle appears in a toy schedule. Suppose reading packed weights takes 6 units, unpacking takes 2, and calculation takes 5. A serial path takes 13. If a pipeline overlaps unpacking of one tile with calculation of the previous tile after the first tile, four tiles take 6 + 4×max(2, 5) = 26 units rather than 52. The overlap requires separate buffers and enough independent tiles; it is not implied by naming the format INT3.',
            ],
            'sources': [(PDF + '#page=2', 'Conference paper, sections 1–2: W3A16 kernel motivation and hardware constraints'), (PDF + '#page=9', 'Conference paper, section 4.3.1: backend settings and fused end-to-end path')],
        },
        {
            'title': 'Read the reported gain with every boundary attached',
            'paragraphs': [
                'MiLo’s end-to-end Mixtral-8×7B test runs on one NVIDIA A100 with 40 GB of VRAM. PyTorch runs out of memory because the FP16 model needs about 90 GB. MARLIN’s reported latencies are 0.123, 0.141, and 0.145 seconds for batch sizes 1, 16, and 32; MiLo reports 0.102, 0.112, and 0.113 seconds. The paper describes this as 1.2× at batch size one and 1.26× above one, against MARLIN in that setup. Those numbers are not a general speedup for every MoE or GPU.',
                'The paper also reports model-quality and memory results on Mixtral-8×7B and DeepSeek-MoE, including more than 87% recovery of the WikiText-2 perplexity gap at a stated 22% compression ratio and up to 3× speedups over baseline approaches. “Recovery” is a comparison to the loss introduced by quantization, not a claim that all original behavior was restored. The table’s quality, the kernel’s latency, and the model’s memory footprint answer different questions and must not be collapsed into one score.',
                'A fair follow-up would hold the model, prompts, accepted quality rule, batch, GPU, and complete serving path fixed while comparing MiLo with the named backend. It would charge preparation time when the deployment is short-lived, report first-output and full-response delay, and check models or routing patterns not used to choose the ranks. The course has not run that experiment; this walkthrough preserves the paper’s measured boundary rather than extending it.',
            ],
            'sources': [(PDF + '#page=9', 'Conference paper, sections 4.3.1 and Table 7: A100 setup, backend comparison, and latency'), (PDF + '#page=2', 'Conference paper, abstract and contributions: quality recovery and reported speedups')],
        },
    ],
    'exercise': {
        'question': 'A 4-by-4 weight matrix is quantized, and a rank-1 correction stores four values in U and four in V. If the original matrix uses sixteen values and the correction values use the same storage cost, what fraction of the original matrix size is the correction? Why does that not tell you the final model size or serving speed?',
        'answer': 'The correction stores 8 values, or one-half of the original matrix’s sixteen values. The quantized matrix, scales, packing metadata, and any other layers still occupy space. Serving speed also depends on unpacking, dequantization, matrix shape, batch size, memory traffic, and whether the correction kernel is fused. The arithmetic is an original teaching model, not a MiLo measurement.',
    },
}
