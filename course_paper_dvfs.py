"""Focused ASPLOS walkthrough of operator-level frequency selection."""

PAPER = 'https://doi.org/10.1145/3669940.3707231'
PDF = 'https://cs.nju.edu.cn/_upload/tpl/01/65/357/template357/lunwen/2025/asplos25-zibo.pdf'

FINE_DVFS = {
    'id': 'fine-dvfs-2025',
    'route': 'asplos-2025',
    'title': 'Fine-grained DVFS: spend power where an operator can use it',
    'identity': 'Using Analytical Performance/Power Model and Fine-Grained DVFS to Enhance AI Accelerator Energy Efficiency · ASPLOS 2025',
    'scope': 'A focused walkthrough of operator-level frequency choice, performance-loss budgets, analytical prediction, and the reported Ascend-NPU evaluation. The author-hosted primary PDF and publication record were inspected. Results are author-reported and have not been independently reproduced here. The time, power, and energy calculations are original teaching models or explicitly derived estimates.',
    'lessons': [('s1', 'Follow one request'), ('s2', 'Numerical error'), ('physical-design', 'Physical design'), ('s10', 'Whole-system cost')],
    'blocks': [
        {
            'title': 'One workload contains operations with different reasons for waiting',
            'paragraphs': [
                'Dynamic voltage and frequency scaling, or DVFS, changes how quickly a processor runs and how much power it uses. A whole program often contains both compute-heavy operations and memory-heavy operations. Raising frequency can help the compute-heavy part, while a memory-heavy part may spend much of its time waiting for data and gain little from a faster arithmetic unit. A single frequency for the entire program therefore leaves some energy choices unused.',
                'Fine-grained DVFS makes the operator the decision unit. The controller estimates how each operator’s time and power change at candidate frequencies, then selects a schedule under a stated performance-loss target. The target matters: “use less power” is incomplete unless the system says how much slower it may become and whether the limit applies to one operator, one iteration, or a whole service.',
                'Original two-operator model: operator A takes 4 ms at high frequency and 6 ms at low frequency, while operator B takes 8 ms at either frequency because memory is the limit. High frequency for both takes 12 ms. Lowering A alone takes 14 ms and saves power during A; lowering B alone adds no time in this model and may save power. The model predicts where frequency has leverage, but the real choice still requires measured or validated power and timing behavior.',
            ],
            'sources': [(PDF, 'Author-hosted paper: operator-level performance/power model and compute- versus memory-bound behavior'), (PAPER, 'ASPLOS publication record: primary citation')],
        },
        {
            'title': 'A slowdown budget turns the choice into a constrained search',
            'paragraphs': [
                'The system can search candidate frequencies rather than lowering every operator equally. For each candidate schedule it estimates total iteration time and power, rejects schedules that exceed the allowed slowdown, and chooses among the remaining schedules according to its energy objective. This is different from calling the lowest frequency efficient: a frequency that saves power but keeps the accelerator busy much longer can use more energy overall.',
                'The constraint must be checked at the boundary that users care about. If one iteration contains a communication gap or a fixed input-loading stage, slowing arithmetic may affect only part of the iteration. If the service promise is request latency, an average training iteration may be the wrong constraint. Likewise, average power is not the same thing as total energy unless the time interval is included.',
                'Original budget model: a baseline iteration takes 100 ms and uses 200 W on average. A candidate takes 102 ms at 180 W. Its slowdown is 2%, and its approximate energy is 18.36 J versus 20 J for the baseline, a reduction of 1.64 J. A second candidate takes 110 ms at 170 W: it uses 18.7 J, so it saves more power but less energy than the first candidate and violates a 5% slowdown budget.',
            ],
            'sources': [(PDF, 'Author-hosted paper: performance-loss targets, schedule search, and power/performance trade-off')],
        },
        {
            'title': 'A model needs visible inputs and a stated scope',
            'paragraphs': [
                'An analytical model can make a large search practical, but its prediction is not a measurement. It must state which hardware counters, operator shapes, memory behavior, voltage/frequency points, and fixed costs it uses. A model calibrated on one accelerator may select a poor schedule on another. A controller also needs a way to apply the chosen frequency quickly enough; if changing frequency costs more time than the operator, fine-grained control loses its purpose.',
                'The paper’s implementation controls the Ascend NPU’s AICore, its AI calculation cores. The paper notes that other system components, including HBM (high-bandwidth memory) and the AICPU (the processor that handles supporting control work), are not tuned in the same way. Those parts sit inside the larger SoC, the complete system-on-chip. That boundary matters when interpreting power: reducing AICore power does not mean the same percentage reduction in total chip power, and total energy still depends on how the iteration time changes.',
                'The paper reports, at a 2% performance-loss target for GPT-3, a baseline iteration of 11.29 seconds at 250.04 W average SoC power and a DVFS iteration of 11.47 seconds at 236.14 W, with reported performance loss of 1.59%. Multiplying the rounded power and time values gives about 2,823 J and 2,709 J; that 4.1% estimate is derived here, not separately reported by the paper. Across its tested GPT-3, BERT, ResNet50, and ResNet152 workloads, the paper reports average AICore power reduction of 13.44%, average SoC power reduction of 4.95%, and average performance loss of 1.76%.',
            ],
            'sources': [(PDF, 'Author-hosted paper: Ascend platform boundary, GPT-3 end-to-end table, and cross-workload results'), (PAPER, 'ASPLOS publication record: paper identity')],
        },
        {
            'title': 'Read power, time, energy, and platform coverage as different results',
            'paragraphs': [
                'A lower average power number says how much power was drawn during the measured interval. It does not say how much energy the complete job used until the interval length is known. A longer run at lower power may use more energy; a shorter run at higher power may use less. Report the measurement window and whether the value covers only the accelerator core or the complete system.',
                'The paper’s evidence is bounded to the studied Ascend NPU, operator set, workloads, frequency controls, and target-loss settings. It is evidence that this model-and-control approach worked under those conditions, not a universal rule that every AI operator should run slowly or that every accelerator will obtain the same savings. A follow-up should test frequency transition overhead, thermal state, memory traffic, tail latency, and the energy of the controller itself.',
            ],
            'sources': [(PDF, 'Author-hosted paper: evaluation scope, power/time reporting, and platform limitations')],
        },
    ],
    'exercise': {
        'question': 'An invented baseline takes 80 ms at 250 W. A DVFS schedule takes 84 ms at 230 W. Does it satisfy a 5% slowdown limit? What are the approximate baseline and DVFS energies, and why is a reported power reduction alone insufficient?',
        'answer': 'The slowdown is (84−80)/80 = 5%, so it meets the stated limit exactly. Baseline energy is 250×0.080 = 20 J; DVFS energy is 230×0.084 = 19.32 J, a saving of 0.68 J in this teaching model. Power alone omits the changed time interval and may cover only one component. These are original teaching calculations, not measurements from the fine-grained DVFS paper.',
    },
}
