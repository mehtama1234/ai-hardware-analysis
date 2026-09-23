"""Focused ASPLOS walkthrough of composable compiler-level partitioning."""

PDF = 'https://arxiv.org/abs/2401.11202'

PARTIR = {
    'id': 'partir-2025',
    'route': 'asplos-2025',
    'title': 'PartIR: make distributed layout a separate, checkable program',
    'identity': 'Sami Alabed and colleagues · PartIR: Composing SPMD Partitioning Strategies for Machine Learning · ASPLOS 2025',
    'scope': 'A focused walkthrough of sharding intent, intermediate representations, composable partitioning tactics, communication collectives, and the reported evaluation. The local arXiv primary text was inspected. Results are author-reported and have not been independently reproduced here. The tensor and collective calculations are original teaching models.',
    'lessons': [('s5', 'Representation'), ('s6', 'Compilation'), ('s7', 'Parallel hardware'), ('s10', 'Whole-system cost')],
    'blocks': [
        {
            'title': 'Separate what the model means from where its pieces run',
            'paragraphs': [
                'Large-model training often splits arrays across many devices. One strategy may split different examples across devices; another may split a matrix; another may split optimizer state. These choices change where values live and when devices must communicate, but they should not change what the model computes. When placement instructions are scattered through model code, changing hardware or trying a new strategy becomes difficult and mistakes are hard to isolate.',
                'PartIR puts the model program and the partitioning plan in separate layers. A schedule is a sequence of tactics such as batch partitioning, model partitioning, or optimizer-state partitioning. Each tactic rewrites an intermediate representation, the compiler’s structured description of the program. The next tactic sees the result of the previous one, so the programmer can inspect and reason about each step instead of receiving only a final opaque layout.',
                'Original tensor model: a 16-row matrix is split across 4 devices. A batch-parallel plan gives each device 4 rows of input work; a model-parallel plan instead splits the 8 output columns into 2-column pieces. The two plans have different communication needs even though the mathematical matrix product is unchanged. A compiler must preserve the operation’s meaning while making the data ownership explicit.',
            ],
            'sources': [(PDF, 'PartIR paper, sections 1 and 2: SPMD partitioning, schedules, meshes, and the separation from model code')],
        },
        {
            'title': 'Incremental rewrites make a plan inspectable',
            'paragraphs': [
                'PartIR applies tactics one at a time and propagates their consequences through the program using rewrite rules based on the operation’s meaning. The rules can introduce loops for tiled computation and later make communication operations explicit. Because each step produces a new representation, a user or simulator can inspect the program after batch partitioning, then after model partitioning, then after optimizer partitioning.',
                'This is different from putting annotations in selected tensors and asking a later heuristic pass to guess the rest. An annotation can be useful, but if two strategies disagree on the same dimension, the programmer needs to know where the conflict arose and which rule resolved it. PartIR’s order gives that conflict a visible point in the schedule. The design does not make every program partitionable: unsupported reshapes, uneven dimensions, spatial communication, and values that must remain replicated still need explicit handling.',
                'Original conflict example: tactic A splits a 12-element dimension across 3 devices, giving chunks of 4. Tactic B later wants the same dimension split across 2 devices, giving chunks of 6. Those ownership choices cannot both be true without a new redistribution. A staged compiler can stop at the conflict, insert a communication step, or require replication; a hidden heuristic may silently add movement or produce an invalid layout.',
            ],
            'sources': [(PDF, 'PartIR paper, sections 4–6: tactic schedules, PartIR Core/HLO representations, propagation, and collective lowering')],
        },
        {
            'title': 'Communication is part of the compiled result',
            'paragraphs': [
                'Once arrays are split, the compiler must say how devices exchange the pieces. PartIR exposes collectives such as AllGather, AllReduce, ReduceScatter, and AllToAll in its intermediate representation. That makes communication countable before the final device code is run. A partitioning plan is therefore not complete when it names the owner of each tensor; it must also specify the movement required by the next operation.',
                'The paper’s examples use a logical device mesh. The mesh names are independent of the exact number of devices, while the lowering step maps them to a concrete system. PartIR can compare the expected collectives after each schedule and can mix manual and automatic tactics. Automatic tactics can reduce effort but can also produce slower schedules, so a convenient plan is not automatically a good plan.',
                'Original collective model: four devices each hold one quarter of a tensor. If the next operation needs the complete tensor on every device, one AllGather is required; if each device computes a partial sum and one result is needed, an AllReduce is the relevant operation. Four local computations do not mean communication is free. If compute takes 3 units and the collective takes 5, the stage costs 8; a plan that cuts compute to 2 but raises movement to 9 is slower at 11.',
            ],
            'sources': [(PDF, 'PartIR paper, sections 2, 6, and 7.3: mesh collectives, schedule examples, and analytically expected counts')],
        },
        {
            'title': 'Read predictability, performance, and compiler cost separately',
            'paragraphs': [
                'The paper reports PartIR performance close to GSPMD in its tested configurations: 58.5% versus 58.3% MFU on a 16×2 TPU 5B setup, 52.3% versus 52.2% on a 32×4 TPU 32B setup, and 42.2% versus 42.9% on an 8×2 GPU 5B setup. It also reports closely comparable HBM use and says the partitioning pass takes at most 14% of overall XLA compilation time in the tested models.',
                'The communication-count tables are a different kind of evidence from runtime. They test whether the composed schedule produces the collectives the designer expects. The runtime comparison tests the resulting program on named meshes and models. A schedule can have the expected count and still be slow because message sizes, topology, overlap, or kernels differ.',
                'The evidence is bounded to the paper’s JAX models, A100 and TPU configurations, selected schedules, and supported operations. The authors identify limited reshape and uneven-dimension support, spatial-partitioning limits, and cases where automatic tactics incur penalties. This walkthrough has not run PartIR or reproduced the training results. Its tensor and timing examples are original teaching models.',
            ],
            'sources': [(PDF, 'PartIR paper, sections 7 and 8: MFU/HBM results, collective-count validation, compilation cost, and limitations')],
        },
    ],
    'exercise': {
        'question': 'A four-device plan reduces local computation from 10 units to 4 units but adds an AllGather costing 5 units and a later AllReduce costing 3 units. What is the new total? If a different plan takes 7 units locally and needs only one 3-unit collective, which is faster? What must still be checked about the partitioning result?',
        'answer': 'The first plan takes 4 + 5 + 3 = 12 units. The second takes 7 + 3 = 10 units, so it is faster in this original teaching model despite doing more local computation. Still check that both plans preserve the model’s meaning, that tensor ownership and collective ordering are valid, that memory fits, and that the measured communication matches the assumed cost. These are original teaching calculations, not PartIR measurements.',
    },
}
