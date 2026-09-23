"""Focused HPCA walkthrough of safe sparse work in diffusion inference."""

PDF = 'https://arxiv.org/pdf/2501.05680'

EXION = {
    'id': 'exion-2025',
    'route': 'hpca-2025',
    'title': 'EXION: skip diffusion work only when the answer can survive it',
    'identity': 'Jaehoon Heo and colleagues · EXION: Exploiting Inter- and Intra-Iteration Output Sparsity for Diffusion Models · HPCA 2025',
    'scope': 'A focused walkthrough of diffusion iteration structure, FFN-Reuse, eager prediction, ConMerge compaction, and the reported accelerator evaluation. The arXiv version of the HPCA paper was inspected. Results are author-reported and have not been reproduced here. The sparsity, cycle, and break-even calculations are original teaching models.',
    'lessons': [('s1', 'Whole-request timing'), ('s2', 'Approximation'), ('s3', 'Memory'), ('s6', 'Execution plans'), ('s8', 'Accepted behavior'), ('s10', 'Whole-system cost')],
    'blocks': [
        {
            'title': 'A diffusion request repeats a changing calculation',
            'paragraphs': [
                'A diffusion model starts from noise and repeatedly predicts how to remove some of it. Each denoising iteration runs a network on the current state, then passes the changed state to the next iteration. Repeating the network creates two different chances to save work: a value may remain useful across iterations, or some values may be unimportant within the current iteration.',
                'EXION calls the first inter-iteration output sparsity and the second intra-iteration output sparsity. This is not the same as weights being zero or inputs being zero. The system is deciding that a particular output can be reused or that a particular contribution can be omitted. That decision is an approximation, so the final generated result—not merely the number of skipped operations—must be checked.',
                'Original timeline: a request has 50 denoising iterations, each with 100 units of work. If every fifth iteration is dense and the four following iterations reuse safe intermediate values, and a sparse iteration costs 35 units, total work is 10×100 + 40×35 = 2,400 units instead of 5,000. If checking and refreshing the reuse mask costs 15 units per iteration, the total becomes 3,150. The saving is real only if the mask cost and quality check are included.',
            ],
            'sources': [(PDF + '#page=2', 'HPCA paper, diffusion-process background and transformer-block workload'), (PDF + '#page=5', 'HPCA paper, sections II-B and III-A: inter- and intra-iteration sparsity')],
        },
        {
            'title': 'Reuse needs a test for when an old value is still safe',
            'paragraphs': [
                'FFN-Reuse first runs a dense iteration. It examines the output after the nonlinear part of a feed-forward layer and makes a bitmask using a threshold. Values judged important are recomputed on later iterations; values below the threshold can be reused for a selected number of sparse iterations. The paper reports 70–97% inter-iteration sparsity in its benchmarks and 52.47–85.41% skipped FFN operations, but those ranges belong to its tested models and thresholds.',
                'Eager prediction is used inside one iteration for attention. It predicts attention scores, keeps only important entries, and can skip a row or related projections when one value clearly dominates. EXION modifies this method because approximation error can accumulate over the many repeated denoising steps. A threshold that looks safe for one transformer block, model, or number of iterations is not automatically safe for another.',
                'Original decision model: 100 values are candidates for reuse. A conservative test marks 70 safe values and costs 20 units; recomputing all values costs 100 units. Reusing the 70 costs 30 units plus the test, or 50, saving 50. If 10 of the marked values later change enough to affect the output and each repair costs 8 units, the total is 130 and reuse loses. The acceptance rule and repair path must be measured, not hidden inside a sparsity percentage.',
            ],
            'sources': [(PDF + '#page=5', 'HPCA paper, section III-A: FFN-Reuse, dense/sparse iterations, thresholds, and reported sparsity'), (PDF + '#page=4', 'HPCA paper, section II-B: eager prediction, top-k attention selection, and accumulated-error concern')],
        },
        {
            'title': 'Sparse output is useless until the hardware can consume its shape',
            'paragraphs': [
                'The skipped values produced by EXION are not necessarily arranged in large regular blocks. A general GPU may still fetch weights and perform work for zero positions because its dense matrix engine does not know how to use this fine-grained output sparsity. Removing arithmetic from the algorithm therefore does not by itself remove memory traffic or empty hardware slots.',
                'ConMerge has two stages. Condensing removes a matrix column when all of its output values are sparse. Merging then groups remaining rows into compact blocks and records the row positions so the hardware can operate on a denser representation. EXION includes dedicated structures to generate and consume these control signals. The data movement needed to discover and represent the sparse shape belongs in the cost model.',
                'Original compaction model: a 10×10 output has 100 positions, but 70 are zero. If only fully empty columns can be removed and two columns are fully empty, dense hardware still processes 80 positions. A merging step packs the remaining nonzeros into four 10-position tiles, with 10 units of control work and 5 units of index movement. If each processed position costs one unit, the compact plan costs 30 + 15 = 45 versus 100, but if the control and index work rise to 80, it costs 110 and loses. Sparsity alone does not determine speed.',
            ],
            'sources': [(PDF + '#page=6', 'HPCA paper, section III-B: output sparsity versus GPU support'), (PDF + '#page=7', 'HPCA paper, ConMerge condensing and merging design')],
        },
        {
            'title': 'Read the accelerator result with the simulator and quality boundary attached',
            'paragraphs': [
                'EXION is a software–hardware design. The paper evaluates accuracy across seven diffusion workloads, then uses a cycle-level simulator with DRAM modeling. It compares EXION configurations against an NVIDIA Jetson Orin Nano edge GPU and an NVIDIA RTX 6000 Ada server GPU with roughly matched throughput and memory-bandwidth targets. Power for the proposed design comes from RTL synthesis and memory models; GPU power comes from measurement tools. These evidence types should not be merged into the phrase “measured chip result.”',
                'The abstract reports performance gains of 3.2–379.3× and energy-efficiency gains of 45.1–3067.6× over the server GPU, with different ranges for the edge GPU. The paper also reports 70–97% inter-iteration sparsity and 20–95% intra-iteration sparsity in its tests. Those large ranges depend on model family, batch size, hardware configuration, and the chosen baseline. Some models contain residual blocks for which the paper does not apply all of its sparsity optimizations.',
                'The paper reports little accuracy change in its tested workloads, while noting exceptions in some metrics for MDM and EDGE under eager prediction. A deployment study should therefore report the generated-output metric, the number of denoising iterations, thresholds, quality failures, simulator assumptions, and the cost of the compaction machinery. This course has not reproduced EXION’s simulator or accelerator estimates, and none of the teaching numbers above are EXION measurements.',
            ],
            'sources': [(PDF + '#page=1', 'HPCA paper, abstract: reported performance, energy, and accuracy claims'), (PDF + '#page=13', 'HPCA paper, evaluation setup: workloads, simulator, GPUs, RTL synthesis, and power sources'), (PDF + '#page=17', 'HPCA paper, latency, energy-efficiency, comparison, and power/area results')],
        },
    ],
    'exercise': {
        'question': 'A dense plan costs 5,000 units for a request. A reuse plan has 10 dense iterations at 100 units each, 40 sparse iterations at 35 units each, and 50 mask checks at 15 units each. What is its total? Does the reuse plan win before checking whether the generated output remains acceptable?',
        'answer': 'The reuse plan costs 10×100 + 40×35 + 50×15 = 3,150 units, saving 1,850 against 5,000. It wins in this teaching model before quality checking. That is not enough for acceptance: compare the generated result with the required quality rule, count any repairs or rejected outputs, and retain the actual hardware and memory costs. These are original teaching numbers, not EXION measurements.',
    },
}
