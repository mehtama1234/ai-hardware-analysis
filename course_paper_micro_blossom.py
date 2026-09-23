"""Focused ASPLOS walkthrough of heterogeneous exact decoding."""

PDF = 'https://arxiv.org/abs/2502.14787'

MICRO_BLOSSOM = {
    'id': 'micro-blossom-2025',
    'route': 'asplos-2025',
    'title': 'Micro Blossom: put each part of an exact decoder where it fits',
    'identity': 'Yue Wu, Namitha Liyanage, and Lin Zhong · Micro Blossom: Accelerated Minimum-Weight Perfect Matching Decoding for Quantum Error Correction · ASPLOS 2025',
    'scope': 'A focused walkthrough of exact matching, heterogeneous CPU/FPGA partitioning, local graph parallelism, software–hardware interaction, and stream decoding. The local full primary text was inspected. Results are author-reported FPGA measurements and have not been independently reproduced here. The latency and partition calculations are original teaching models.',
    'lessons': [('s1', 'Critical paths'), ('s6', 'Execution plans'), ('s7', 'Parallel hardware'), ('s10', 'Whole-system cost')],
    'blocks': [
        {
            'title': 'The decoder must be fast without changing the answer',
            'paragraphs': [
                'Quantum error correction produces a stream of measurement results. A decoder examines the resulting graph and chooses corrections; if the answer arrives too late, the quantum system must wait. An approximate decoder may be faster but can make more logical errors. Micro Blossom keeps minimum-weight perfect matching (MWPM)—pairing detected errors while minimizing total correction cost—exact and targets the latency of the feedforward path.',
                'This creates a constrained optimization problem. The system cannot freely replace the algorithm with a cheaper approximation, and it cannot measure only the accelerator’s internal work while ignoring the CPU, transfers, or the time needed to accept a new measurement round. The useful boundary is: measurements arrive, the exact correction decision is produced, and the next operation can rely on it.',
                'Original critical-path model: a decoder spends 0.4 microseconds reading a round, 0.8 computing, and 0.3 returning the decision, for 1.5 microseconds. Moving only the 0.8 computation to an accelerator does not make the path 0.8; if transfers add 0.25 each way, the new path is 0.4 + 0.25 + 0.8 + 0.25 + 0.3 = 2.0. Acceleration helps only when the whole path gets shorter or when the work overlaps safely.',
            ],
            'sources': [(PDF, 'Micro Blossom paper, abstract and introduction: exact MWPM, feedforward latency, and error-quality tradeoff')],
        },
        {
            'title': 'Partition by what each machine can handle well',
            'paragraphs': [
                'Micro Blossom divides the blossom decoder instead of sending the entire algorithm to one device. The CPU keeps the primal phase and complex data structures, where flexible control is useful. The programmable accelerator handles the dual phase, where many vertices and edges can perform local updates in parallel. This is a division by dependency and regularity, not simply a division by instruction count.',
                'The accelerator uses processing units associated with vertices and edges in the decoding graph. Each unit keeps local state and communicates with nearby units. That arrangement exposes graph parallelism while limiting global coordination. The CPU still matters: it prepares work, handles cases the local hardware cannot decide, and receives the state needed to continue the exact algorithm.',
                'Original partition model: a task has 100 units of irregular control work and 900 units of independent edge updates. The CPU can do control at 50 units per time and the accelerator can do 300 edge-update units per time, but a transfer costs 2 units each way. A CPU-only path takes 100/50 + 900/50 = 20 time units. A split path takes 100/50 + 2 + 900/300 + 2 = 9, so it wins. If updates are not independent and require five extra synchronization rounds, the split path may lose; the dependency graph decides.',
            ],
            'sources': [(PDF, 'Micro Blossom paper, sections 3 and 4: heterogeneous architecture and vertex/edge-level parallelism')],
        },
        {
            'title': 'Local conflict handling protects the real critical path',
            'paragraphs': [
                'A fine-grained accelerator can still lose if every small conflict returns to the CPU. Micro Blossom therefore handles common isolated conflicts inside the parallel units, using only local neighbors where the decision is sufficient. More complicated conflicts remain visible to the CPU so the exact algorithm is preserved. The design spends hardware resources to reduce the number of software–hardware round trips.',
                'The distinction changes the claim: “more parallel units” is not the same as “more useful progress.” If every unit waits for a global controller, the controller remains the bottleneck. Local state and local communication remove some waits, but they are valid only for conflicts whose surrounding information is enough to prove the local result. A fast incorrect shortcut would not be an exact decoder.',
                'Original interaction model: 100 graph events each take 1 unit in hardware. With a CPU trip costing 3 units for every event, the total is 400 units. If 80 events are isolated and can be settled locally, only 20 trips remain: 100 + 20×3 = 160 units, before local-control overhead. If local detection adds 1 unit to every event, the total becomes 260; it still wins here, but the margin is smaller. Count both avoided trips and new work.',
            ],
            'sources': [(PDF, 'Micro Blossom paper, section 5: isolated-conflict resolution and reduced CPU interaction')],
        },
        {
            'title': 'Streaming changes the timing question',
            'paragraphs': [
                'A batch decoder can wait for all measurement rounds before solving. A stream decoder processes new rounds as they arrive. Micro Blossom uses round-wise fusion so arriving layers can be incorporated without restarting the complete problem, while preserving the same final matching result as the corresponding batch procedure under the paper’s construction. This targets the time at which a correction becomes usable, not only total work over a long batch.',
                'The paper reports a prototype on a Xilinx Versal VMK180 FPGA at 62 MHz. At code distance 13 and physical error rate 0.1%, it reports 0.8 microseconds average decoding latency, described as 8× shorter than the best prior MWPM result and 17× better than its cited Parity Blossom CPU baseline. These are paper-reported measurements under the stated code, noise model, clock, implementation, and baselines; this course has not reproduced them.',
                'The prototype’s limitation is part of the result: no ASIC measurement is presented, and a larger code distance or different graph may need more programmable resources. The right follow-up keeps exactness, physical error rate, code distance, stream arrival pattern, and correction-ready boundary fixed while changing the hardware partition. A lower accelerator-only time is not enough if CPU handling or transfer time moves the critical path.',
            ],
            'sources': [(PDF, 'Micro Blossom paper, sections 6–8: stream decoding, prototype, and measured evaluation')],
        },
    ],
    'exercise': {
        'question': 'A CPU-only decoder spends 6 units on flexible control and 18 units on parallel graph updates. A split design keeps the 6 units on the CPU, runs graph updates in 6 units, and adds 2 units to send work plus 2 units to return the result. Which path is shorter? What additional condition must be checked before calling the split design an exact end-to-end improvement?',
        'answer': 'The CPU-only path takes 24 units. The split path takes 6 + 6 + 2 + 2 = 16 units, so it is shorter by 8 units in this original teaching model. Before calling it an exact end-to-end improvement, verify that the partition preserves the same matching result, that dependencies permit the overlap, and that setup, conflict handling, queueing, and the correction-ready boundary are included. These are original teaching calculations, not Micro Blossom measurements.',
    },
}
