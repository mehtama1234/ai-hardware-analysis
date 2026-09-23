"""Focused MICRO walkthrough of memory-side state updates for post-transformer LLMs."""

PDF = 'https://jinuhwang.github.io/papers/2025-micro-pimba.pdf'
DOI = 'https://doi.org/10.1145/3725843.3756121'

PIMBA = {
    'id': 'pimba-2025',
    'route': 'micro-2025',
    'title': 'Pimba: move repeated model-state work closer to where that state lives',
    'identity': 'Wonung Kim, Yubin Lee, Yoonsung Kim, and colleagues · Pimba: A Processing-in-Memory Acceleration for Post-Transformer Large Language Model Serving · MICRO 2025',
    'scope': 'A focused walkthrough of the recurrent state update in several post-transformer language models, the memory bottleneck it creates at serving time, Pimba’s shared processing units and low-precision arithmetic, and the end-to-end evaluation boundary. The final MICRO paper and DOI metadata were inspected. Performance claims are from the paper’s cycle-level simulation; area results use RTL synthesis. No Pimba DRAM device was fabricated or measured by this course, and no experiment was independently reproduced. The two-value state update below is an original teaching model, not the paper’s model or a benchmark.',
    'lessons': [('s3', 'Data movement and memory'), ('s4', 'Shared connections and limits'), ('s2', 'Number representation'), ('s10', 'Whole-system results')],
    'blocks': [
        {
            'title': 'A shorter memory history can still be costly to update',
            'paragraphs': [
                'A standard transformer keeps key and value records for past tokens so later tokens can attend to them. Some newer model families—including state-space models, linear attention, and recurrent models—keep a fixed-size running state instead. This avoids a history that grows with the conversation, but every new token must still update and consult that state.',
                'In a simplified state update, the system first weakens some old state values, adds information from the new token, and then reads the updated state to produce the next output. Each request has its own state. In a large batch, the device repeatedly reads and writes many such states; those transfers can cost more time than the arithmetic performed on the values. A fixed-size state is therefore not the same as a free state.',
                'Original two-number teaching model: begin with state (10, −4), weaken its components by factors (0.9, 0.5), and add new information (1, 3). The new state is (10, 1). If the output uses weights (1, 2), its value is 10 + 2×1 = 12. If we wrongly skip the weakening step, the state becomes (11, −1) and the output is 9. The order matters because each token’s next state depends on the previous one. This small arithmetic model explains the dependency; it is not Mamba-2’s full state matrix or a Pimba measurement.',
            ],
            'sources': [(PDF + '#page=1', 'Final MICRO paper, abstract: scope and central bottleneck claim'), (PDF + '#page=3', 'Final MICRO paper, section 2: Mamba-2 state update and related model families'), (PDF + '#page=4', 'Final MICRO paper, section 3.1: state size and measured/simulated bottleneck analysis')],
        },
        {
            'title': 'Put the arithmetic beside memory, but share the added hardware',
            'paragraphs': [
                'Processing-in-memory (PIM) places small arithmetic units inside or beside memory banks. The point is to do some work before the stored values travel out over the memory connection. This is most promising when a task moves many values but performs relatively little arithmetic on each one.',
                'A state update is not just one matrix multiply. It includes element-by-element multiplication and addition, a new-value update, and a dot product to form the output. Giving every memory bank a complete unit for this sequence can use too much chip area; using a small shared unit for all work can leave memory bandwidth unused.',
                'Pimba’s design shares one state-update unit between two banks. While one bank supplies a read, the other can receive a write, alternating their turns to keep the shared unit busier. The physical limit is important: a row buffer is the small holding area a bank uses for the row it is currently accessing. In this design, one bank’s row buffer cannot supply a new read and accept a write at the same time.',
                'Precision is part of the hardware cost. Repeated updates can lose small values if the number format has too few useful digits. The paper finds that several low-precision floating-point choices damage the tested state-space model results, while integer and MX8 formats preserve quality more closely. In the paper’s MX8 representation, a group of values shares scale information, which makes addition simpler in the proposed hardware. The authors select MX8 with stochastic rounding as a balance between chip area and result quality. Stochastic rounding sometimes rounds a value up and sometimes down according to its distance from the two representable values, helping very small contributions survive repeated updates. This is a design choice measured for the paper’s workloads, not a universally best format.',
                'Pimba does not place the entire language model in memory. In the described serving path, the GPU handles prefill—the initial pass over a user’s prompt that creates starting state—and other work. During later token generation, selected state-update and attention operations run on the memory-side units. The software driver, memory layout, custom commands, GPU kernels, and arithmetic format are all part of the design—not optional details after the hardware idea.',
            ],
            'sources': [(PDF + '#page=5', 'Final MICRO paper, section 3.2: state precision and repeated-update effects'), (PDF + '#page=6', 'Final MICRO paper, section 4: area/accuracy tradeoffs and shared-unit reasoning'), (PDF + '#page=6', 'Final MICRO paper, section 5: GPU/PIM division of work and system stack')],
        },
        {
            'title': 'Check the schedule and evidence, not only the memory-side speed',
            'paragraphs': [
                'The paper reports that, in its comparisons, Pimba reaches up to 4.1× the generation throughput of a GPU system designed for language-model serving and up to 2.1× that of a GPU-plus-PIM comparison system. The full evaluation also reports average gains of 1.9× and 1.4× over those respective systems, and 2.2× lower energy than the GPU comparison. The maximum and average figures answer different summaries; neither is a promise for an arbitrary model, batch, or device.',
                'There is a useful counterexample inside the design. State changes must happen in order: the next update uses the state produced by the previous one. The GPU and memory-side unit therefore alternate in blocks, leaving gaps where one or both may be idle. The authors identify this underutilization and discuss sub-batch interleaving as a possible future integration. Moving an operation next to data can reduce transfer time while making coordination between stages the next bottleneck.',
                'Evidence type limits how far to carry the headline. Pimba’s system results come from the authors’ timing-and-event simulator, built on Ramulator2, with modeled configurations containing 40 HBM2E processing-in-memory modules. They estimate the hardware logic’s area and energy from an RTL description, a detailed hardware design used for analysis before manufacturing. These results support conclusions within that model and setup. They are not measurements from a manufactured Pimba memory device, and the estimated energy and area are not a data center’s complete power use or a production-service measurement. Results for larger modeled systems are projections, not equally sized real deployments.',
                'To compare Pimba with Oaken, ask what each design changes. Oaken compresses the attention cache to reduce the amount of data that must move. Pimba moves selected state calculations closer to memory. They target different operations, use different evaluation setups, and report different baselines; their headline multipliers should not be multiplied or ranked as though they were one experiment.',
            ],
            'sources': [(PDF + '#page=1', 'Final MICRO paper, abstract: headline comparison'), (PDF + '#page=10', 'Final MICRO paper, section 6: simulation, baselines, and evaluation'), (PDF + '#page=13', 'Final MICRO paper, section 8: dependency bubbles and utilization limits'), (DOI, 'Official DOI for the MICRO 2025 proceedings paper')],
        },
    ],
    'exercise': {
        'question': 'Use the invented state update: old state (10, −4), weakening factors (0.9, 0.5), new contribution (1, 3), and output weights (1, 2). Find the new state and output. What output would you get if you accidentally skipped the weakening step? Why does this order matter for an implementation?',
        'answer': 'The weakened old state is (9, −2); after adding (1, 3), the new state is (10, 1). The output is 1×10 + 2×1 = 12. Without weakening, the state would be (11, −1), giving 1×11 + 2×(−1) = 9. The next state depends on the previous one, so operations cannot be freely reordered or overlapped unless the implementation preserves the required values and order. These are teaching numbers, not a paper measurement.',
    },
}
