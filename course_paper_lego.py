"""HPCA LEGO walkthrough with source-bounded claims and original teaching models."""
PAPER = 'https://arxiv.org/html/2509.12053'

LEGO = {
    'id': 'lego-2025',
    'route': 'hpca-2025',
    'title': 'LEGO: describe reuse before choosing the wires',
    'identity': 'Yujun Lin, Zhekai Zhang, and Song Han · LEGO: Spatial Accelerator Generation and Optimization for Tensor Applications · HPCA 2025',
    'scope': 'Focused reading of arXiv:2509.12053v1, sections II–VI. The arXiv manuscript identifies the HPCA 2025 submission and the MIT project page identifies the conference publication. The paper’s reported synthesis, simulation, and comparison results are author-reported and have not been independently reproduced here. Examples below are original teaching models.',
    'lessons': [('s6', 'Compiler representations'), ('s3', 'Reuse and movement'), ('dependencies-and-pipelines', 'Dependencies'), ('physical-design', 'Evidence stages')],
    'blocks': [
        {
            'title': 'The design problem is a connection problem',
            'paragraphs': [
                'A spatial accelerator spreads calculation across several units connected by data paths. Those paths deliver inputs, forward values that will be reused, and collect results. Choosing the arithmetic units leaves a further question: how will each value reach the unit that needs it at the required time?',
                'LEGO generates hardware descriptions from relationships among loop iterations, data indices, unit locations, and control timing. It derives connections and memory allocation, then optimizes a lower-level graph before producing synthesizable RTL. Here RTL means a description of registers and the logic that updates them.',
            ],
            'sources': [(PAPER + '#S2', 'Author manuscript, sections II–III — design space and representation'), ('https://hanlab.mit.edu/projects/lego', 'MIT project page — HPCA publication identity and overview')],
        },
        {
            'title': 'A small relation makes reuse visible',
            'paragraphs': [
                'Use a two-by-two matrix multiplication as an original teaching model. The result at row i and column j uses input entries X[i,k] and W[k,j] for k equal to zero and one. At the four output positions, the X entries repeat by row and the W entries repeat by column. A representation that records those index relationships can ask which nearby computation units need the same value, instead of starting from four unrelated output calculations.',
                'For one output, the two products are X[i,0]W[0,j] and X[i,1]W[1,j]. If a neighboring unit computes the next column, it can reuse X[i,0] and X[i,1] while needing W[0,1] and W[1,1]. If another unit computes the next row, it can reuse W[0,j] and W[1,j]. The best path depends on which dimension is placed across units and which is left for time. Reuse is a relationship between work and data, not a property of the tensor name.',
                'To choose a connection, keep four facts available: the required calculation, its assigned unit, the value it reads, and the time that value is valid. Losing one can make an apparently useful sharing opportunity impossible to implement. A value reused at different times may require storage; a value needed by several units at once may require enough delivery capacity.',
            ],
        },
        {
            'title': 'Work through timing and register cost',
            'paragraphs': [
                'Original timing model: each cycle launches a pair of inputs for the same calculation. One path delivers its member after two cycles and another after three. A unit that combines the pair must receive members from the same launch. Delaying the earlier path by one cycle aligns each pair at cycle three after launch. The inserted storage preserves the pairing while both paths continue accepting new inputs every cycle.',
                'With a 16-bit value on the delayed edge, that one cycle needs 16 bits of stored data in this model. Eight separate such edges need 128 bits. Counting arithmetic units would omit this storage. LEGO’s delay-matching formulation accounts for inserted registers and edge widths; our example illustrates the timing requirement that makes this storage necessary.',
                'Add four input values with exact arithmetic and enough range to avoid overflow. The expression ((a + b) + c) + d has three dependent additions. Computing (a + b) and (c + d) together, then adding those results, uses the same three additions across two dependent levels. With separate one-cycle adders and all inputs initially ready, the depths are three and two cycles. Both arrangements need the inputs to reach the right adder at the right time. For rounded arithmetic, changing the grouping also needs a numerical check.',
            ],
        },
        {
            'title': 'Read the evaluation at the stage it measures',
            'paragraphs': [
                'Section VI describes TSMC 28nm synthesis, CACTI memory modeling, and performance simulation checked against RTL simulation. Its Gemmini comparison uses 256 multiply-accumulate units, 256 KB of on-chip buffer, and a 16 GB/s memory link. The reported average speedup is 3.2×; GPT-2 remains limited by memory bandwidth on both systems.',
                'Synthesis estimates an implementation using a technology library. A performance simulator predicts execution under its model, and comparison with circuit-level execution can test that prediction for the exercised cases. A fabricated device would supply a further kind of evidence about operation under physical conditions. Identify which stage supplies each number before comparing it with another paper.',
                'Matched counts of arithmetic units and storage constrain a comparison, but they do not establish equal performance. Wiring, control, supported operations, and the chosen workload still determine how effectively those resources serve the program. These questions connect the paper to the course’s exercises on input supply, sustained performance, and complete execution time.',
            ],
            'sources': [(PAPER + '#S6', 'Author manuscript, section VI — methodology and reported evaluation'), (PAPER + '#S5', 'Author manuscript, section V — backend graph transformations')],
        },
        {
            'title': 'Count fused dataflows as one design with several obligations',
            'paragraphs': [
                'A design supporting two dataflows can serve more workloads, but it may need extra connections, selection logic, and control state. Original model: dataflow A alone needs 100 units of connection area and runs a workload in 10 cycles. Fusing A and B adds 20 units of fixed connection area but lets the scheduler use B, which takes 7 cycles for a second workload. A naïve fused design adds 40 instead of 20 units because it keeps duplicate paths. Optimization matters only relative to a valid fused baseline.',
                'Suppose the fused design uses 120 area units and the naïve design 140. If the chip limit is 125, the optimized fusion fits and the naïve one does not. If an extra selector adds two cycles to every execution, the first workload now takes 12 and the second 9. Whether that trade is worthwhile depends on how often each workload occurs and whether the selector can be bypassed for a fixed dataflow.',
                'For each transformation, follow a specific resource: which live value needs storage, which input needs a route, and which arithmetic unit or connection can become idle? An area reduction helps only if the resulting design still supports the required workload and meets its timing and power limits.',
            ],
        },
    ],
    'exercise': {
        'question': 'A continuous stream launches one pair per cycle. Its two 16-bit members reach a join after two and five cycles respectively. How much storage does a fixed delay line need to align the earlier stream while maintaining that rate? If a generated design reduces a 100-cycle workload to 70 cycles but its clock falls from 1 GHz to 500 MHz, which takes less time?',
        'answer': 'The earlier stream needs three cycles of delay, requiring three 16-bit stages, or 48 bits of stored data, under this fixed-rate model. An isolated value could instead wait in one 16-bit slot; the arrival rate is what requires three simultaneous slots here. At 1 GHz, 100 cycles take 100 nanoseconds. At 500 MHz, 70 cycles take 140 nanoseconds. Compare elapsed time using the implemented clock and the complete schedule.',
    },
}
