"""Focused ASPLOS walkthrough of dependency-aware temporal graph training."""

PDF = 'https://doi.org/10.1145/3676641.3716250'

CASCADE = {
    'id': 'cascade-2025',
    'route': 'asplos-2025',
    'title': 'Cascade: batch only the temporal graph work that is safe to combine',
    'identity': 'Yue Dai, Xulong Tang, and Youtao Zhang · Cascade: A Dependency-Aware Efficient Training Framework for Temporal Graph Neural Networks · ASPLOS 2025',
    'scope': 'A focused walkthrough of temporal graph event dependencies, memory freshness, topology-aware batching, stabilized nodes, adaptive update frequency, and the reported evaluation. The local author-hosted primary text was inspected. Results are author-reported and have not been independently reproduced here. The dependency and batch calculations are original teaching models.',
    'lessons': [('dependencies-and-pipelines', 'Dependencies'), ('queues-and-batching', 'Scheduling'), ('s8', 'Accuracy and correctness'), ('s10', 'Whole-system cost')],
    'blocks': [
        {
            'title': 'A larger batch can make a temporal model less correct',
            'paragraphs': [
                'A temporal graph is a stream of events such as an interaction between two nodes. A temporal graph neural network keeps a memory for each node and updates that memory as events arrive. The next prediction depends on the latest relevant memory, so event order is part of the input meaning, not merely an implementation detail.',
                'Large batches expose parallel hardware, but events in one batch may touch the same nodes. If they are processed together, later events can use an older memory than they would in the original sequence. Small batches preserve freshness but leave the GPU with too little independent work. The problem is therefore not “choose the largest batch”; it is “find events whose required state does not conflict.”',
                'Original dependency model: event A changes node 1 and event B changes node 1 later, so B must see A’s update. Event C changes node 8 and event D changes node 9; if neither touches state used by the other, C and D can run together. A batch containing A and B is unsafe unless the update is explicitly serialized; a batch containing C and D can be parallel without inventing a stale memory value.',
            ],
            'sources': [(PDF, 'Cascade paper, abstract and introduction: temporal events, node memories, batching, and freshness/accuracy tradeoff')],
        },
        {
            'title': 'Use graph structure to find safe parallel work',
            'paragraphs': [
                'Cascade’s topology-aware scheduler adds events to a batch while tracking which nodes the current batch already touches. Events from separate parts of the graph are candidates for parallel processing. This is more precise than treating the entire event stream as one serial chain and safer than assuming every event in a large time window is independent.',
                'The scheduler also looks for node memories that have stabilized: their values change little across recent updates. For those nodes, Cascade can relax some temporal restrictions and update them less often using runtime feedback. This is an approximation with an explicit condition. A node is not safe merely because it was quiet once; the threshold and update policy must be checked against the model’s accuracy requirement.',
                'Original batch model: eight events each take 1 unit. A fixed serial policy takes 8 units. If the dependency graph permits two groups of four independent events, four workers finish in 2 units per group, or 4 units total. If one “stable” node becomes active again and its two events were incorrectly combined, the speed result is invalid because the second event used the wrong memory. Parallelism is earned by a dependency argument, not by a queue length.',
            ],
            'sources': [(PDF, 'Cascade paper, sections 3–4: spatial independence, stabilized node memories, adaptive batching, and update frequency')],
        },
        {
            'title': 'Reduce memory updates only when the state change is small enough',
            'paragraphs': [
                'Updating every node memory after every event costs work and can limit batch size. Skipping updates can make training faster, but it changes the state used by later predictions. Cascade adapts update frequency from runtime behavior rather than applying one fixed skip rule to every node. The control decision must connect a measured memory change to an accepted validation-loss or accuracy boundary.',
                'This creates two separate obligations. First, the scheduler must not combine events that truly depend on one another. Second, its “stable” classification must remain valid as the graph changes. A node that is stable in one time window may become highly active later. The system needs a way to re-enter the conservative path when evidence of change appears.',
                'Original error model: an exact memory update costs 3 units and contributes 0.2 error units if delayed for one event; a stable approximation costs 1 unit and contributes at most 0.01. For 10 stable events, the approximate path saves 20 units of work and adds at most 0.1 error units. If one supposedly stable event actually contributes 0.5 error units, the bound is broken and the scheduler must detect or limit that case.',
            ],
            'sources': [(PDF, 'Cascade paper, sections 4 and 5: adaptive memory update frequency, implementation, and evaluation methodology')],
        },
        {
            'title': 'Read speed and model quality on the same workload boundary',
            'paragraphs': [
                'The paper reports 1.3×–5.1× speedups, 2.3× on average, over TGL in its main five-dataset evaluation, and 1.2×–5.0× over TGLite for Cascade-Lite. It reports normalized validation loss averaging 99.4% of the baseline in the stated experiments. The paper also reports billion-event results on GDELT and MAG, including separate Cascade_EX comparisons.',
                'These numbers depend on the temporal graph models, datasets, A100 setup, batch choices, dependency thresholds, and baselines. Speedup without the validation-loss result would not establish that the same training problem was solved. Conversely, a near-baseline loss does not tell us whether the system’s memory or GPU utilization improved unless those metrics and their boundaries are named.',
                'This walkthrough has not reproduced Cascade or tested its similarity threshold on another graph. A fair follow-up would hold the event order, model, stopping rule, and accepted validation loss fixed while varying only batch policy and memory-update policy. It should report useful training time, update work, batch sizes, memory freshness, and accuracy together.',
            ],
            'sources': [(PDF, 'Cascade paper, evaluation sections: A100 setup, baselines, speedups, validation loss, and billion-event boundary')],
        },
    ],
    'exercise': {
        'question': 'Eight events each take 1 unit. A serial trainer handles them in 8 units. A dependency-aware scheduler can run four independent events at once, then the remaining four at once. What is the ideal compute time? What must be true before claiming the result preserves the temporal model?',
        'answer': 'The ideal compute time is 2 batches × 1 unit = 2 units, a 4× compute-only reduction. Before claiming a valid training improvement, verify that events within each batch do not require one another’s updated memories, that any stabilized-node rule remains within the accepted accuracy boundary, and that scheduling and update overhead are included. These are original teaching calculations, not Cascade measurements.',
    },
}
