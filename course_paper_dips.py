"""Focused NSDI walkthrough of cross-cluster training with uneven links and failures."""

PDF = 'https://www.usenix.org/system/files/nsdi26-li-shengwei.pdf'
USENIX_RECORD = 'https://www.usenix.org/conference/nsdi26/presentation/li-shengwei'

DIPS = {
    'id': 'di-ps-2026',
    'route': 'nsdi-2026',
    'title': 'Di-PS: train across clusters without treating every update as equally fresh',
    'identity': 'Shengwei Li, Qiaoling Chen, Zhiquan Lai, and colleagues · Di-PS: System-Algorithm Co-Design for Asynchronous and Heterogeneous Cross-cluster LLM Training at Scale · NSDI 2026',
    'scope': 'A focused walkthrough of the paper’s two-stage training setting, centralized parameter-server design, pseudo-gradient correction, fault handling, and bounded evaluation claims. The final USENIX proceedings PDF and its presentation record were inspected. The paper’s experiments and production deployment were not rerun or independently audited here. The schedules and arithmetic below are original teaching models, not Di-PS measurements or a reproduction of its algorithm.',
    'lessons': [('s1', 'Work, waiting, and complete time'), ('queues-and-batching', 'Queues and stragglers'), ('s7', 'Communication and recovery'), ('training-workflow', 'Training to an accepted model')],
    'blocks': [
        {
            'title': 'Why combine smaller clusters at all?',
            'paragraphs': [
                'A large training job can run inside one tightly connected cluster, but assembling one enormous cluster may be expensive or physically impractical. Several existing clusters can offer more total compute, yet the network between sites is slower and more variable than the links inside each site. The design problem is therefore not simply “add more devices.” It is how to let each cluster do useful local work without making every step wait for the slowest distant connection.',
                'Di-PS builds on a two-stage pattern. Each cluster performs several local training steps using its nearby devices; periodically, the clusters exchange model updates through a global step. The inner steps preserve the fast local work, while the less frequent outer step reconciles what the clusters learned. This reduces how often large model state crosses the wide-area links, but it does not make that transfer free.',
                'Consider an original teaching schedule with two clusters. Cluster A finishes its local work in 3 time units; cluster B takes 7. If every outer step waits for both, A finishes at time 3 and sits idle for 4 units. Allowing A to continue sooner can use that capacity, but its next update may be based on an older shared model than B’s. Removing a wait changes the freshness of the information being combined. This schedule illustrates the design tension; it is not a measured Di-PS result.',
            ],
            'sources': [(PDF, 'Final NSDI 2026 paper, sections 1–2: motivation, two-stage training, and heterogeneity')],
        },
        {
            'title': 'Coordinate communication and judge the updates',
            'paragraphs': [
                'Di-PS uses a centralized parameter server for the outer training step: a group of server processes that keeps the shared model and its update state, and coordinates changes arriving from the clusters. Its follower servers each manage several model layers, while one leader server coordinates the clusters and those followers. The design also separates two activities: deciding which operation should happen next, and moving the large blocks of model values. This lets the system schedule communication alongside computation when their dependencies allow. Coordination is not free, and the server itself needs enough capacity and a recovery plan.',
                'Asynchronous updates create a second problem beyond network speed. Two clusters can return changes derived from different versions of the model. A fast but stale update is not automatically as useful as a fresh one, and accepting every update can destabilize learning. Di-PS adds a pseudo-gradient correction strategy. A pseudo-gradient here is a change inferred from the difference between a cluster’s model and the shared model, rather than a fresh derivative calculated at the shared state.',
                'For each cluster, the parameter server adds up the sizes of that pseudo-gradient across its server pieces. It compares that size with a moving history of earlier sizes. An update whose score crosses the paper’s threshold is excluded. The remaining updates are averaged in proportion to the amount of training data their clusters consumed, and the combined change is clipped before it updates the shared model. This is a paper-specific safeguard, not a universal test for whether any gradient is correct; its threshold and moving-average settings are choices that need evidence for the target training job.',
                'In the two-cluster teaching schedule, the coordinator must know more than “A finished” or “B finished.” It needs enough version and update history to judge what each returned change represents. If A’s repeatedly changing updates are all admitted while B’s much older update is treated identically, the system may gain activity but lose useful progress. Filtering can protect quality, but discarded work is still a cost. The paper’s results therefore need both a time measure and a model-quality or convergence measure.',
            ],
            'sources': [(PDF, 'Final NSDI 2026 paper, sections 3–4: parameter-server design and stable asynchronous training'), ('https://www.usenix.org/system/files/nsdi26_slides-li-shengwei.pdf', 'Authors’ NSDI presentation, slide 15: pseudo-gradient correction steps')],
        },
        {
            'title': 'Treat cluster failure as part of the training protocol',
            'paragraphs': [
                'A cluster may slow down, fail, leave, or rejoin while others keep training. If every participant must restart together, one local failure can throw away work completed elsewhere. Di-PS supports dynamic cluster participation and a self-recovering parameter server. Its production discussion also emphasizes proactive failure reports: a heartbeat or explicit error can identify a failed component sooner than waiting to infer it from a loss spike or falling throughput.',
                'This recovery path has a data-consistency obligation. When the set of clusters changes, the examples assigned to the remaining workers must still form the intended training mix. The authors describe dividing the dataset into many more chunks than clusters so that assignment can change while keeping each cluster’s portion balanced and representative. That design addresses one stated deployment need; it does not establish that arbitrary changing datasets remain statistically equivalent.',
                'The controlled experiments report 1.27–4.67× faster training than synchronous two-stage approaches and 1.00–1.60× faster training than the asynchronous approaches used as baselines. The paper does not leave “convergence” as an unexplained label: its four-cluster LLaMA3.2-1B emulation varies performance disparity through 200%, plots training loss, and reports BBH, MMLU, and DROP scores. Under those settings, the authors report Di-PS scores comparable to synchronous DiLoCo and contrast them with training failures of asynchronous DiLoCo. This is evidence for those models, data, heterogeneity settings, inner-step interval, and quality measures—not a promise that asynchronous training preserves every model’s quality. The two speed ranges use different baselines, so the 4.67× upper bound is not a general asynchronous speedup.',
                'The authors also report a 33-day production training of a 100-billion-parameter model across nine heterogeneous clusters, reaching up to 10,122 NPUs. Its figure shows training loss over days and lists scores on BBH, MMLU, CMMLU, DROP, MBPP, GSM8K, and HellaSwag, but it does not compare that run with a counterfactual synchronous production run. Read the overhead denominator carefully: the abstract says less than 6% overhead compared with single-cluster training, while the production step breakdown says parameter push/pull and update account for about 6% of training time. These are related but not interchangeable measurements. The results are author-reported, not reproduced here.',
            ],
            'sources': [(PDF, 'Final NSDI 2026 paper, sections 5–6: evaluations, production experience, and lessons'), (USENIX_RECORD, 'Official USENIX proceedings record and published abstract')],
        },
    ],
    'exercise': {
        'question': 'In the invented two-cluster schedule, A finishes local work in 3 time units and B in 7. If each outer step waits for both, how long does the round take, and how long does A wait after finishing? If A starts another local step before B returns, name two facts the coordinator should track before combining their eventual updates.',
        'answer': 'The synchronous round takes 7 time units, and A waits 7 − 3 = 4. If A starts again early, the coordinator should track which shared-model version each update came from and how much training data or local work it represents. It may also use update history to judge whether a returned change looks unusual. These are conceptual requirements illustrated by the schedule, not a numerical claim about Di-PS or a reproduction of its correction rule.',
    },
}
