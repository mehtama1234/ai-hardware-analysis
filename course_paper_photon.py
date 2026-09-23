"""Focused MLSys walkthrough of federated large-model pre-training."""

PDF = 'https://proceedings.mlsys.org/paper_files/paper/2025/file/185087ea328b4f03ea8fd0c8aa96f747-Paper-Conference.pdf'

PHOTON = {
    'id': 'photon-2025',
    'route': 'mlsys-2025',
    'title': 'Photon: train large models when the machines cannot talk often',
    'identity': 'Lorenzo Sani, Alexandru-Andrei Iacob, and colleagues · Photon: Federated LLM Pre-Training · MLSys 2025',
    'scope': 'A focused walkthrough of Photon’s local-training and aggregation strategy, the system choices around it, and selected quality and wall-time results. The figures are reported by the paper’s authors and are not independently reproduced here. The small timing model is an original teaching example, not a measurement or reproduction.',
    'lessons': [('s1', 'Work and waiting'), ('s3', 'Communication costs'), ('s4', 'Pipelines and dependencies'), ('s6', 'Execution plans'), ('s8', 'Correctness and quality promises'), ('s10', 'Whole-system cost')],
    'blocks': [
        {
            'title': 'If every step needs a conversation, the network sets the pace',
            'paragraphs': [
                'Large-model training divides examples among machines. In a common method, each machine calculates a small update, then the machines exchange updates so they can continue from a shared model. This frequent agreement works well when the machines have very fast connections. Across regions, the same messages take longer and can leave expensive processors waiting.',
                'Photon lets each participating site make several local updates before it exchanges model changes with the others. In everyday terms, each site does a longer stretch of work before checking back in. This can greatly reduce the number of long-distance exchanges. But the sites are now working from an older shared model while they train locally. Their updates can differ, especially if their data differ. Fewer conversations change the learning process; they do not simply remove a network delay while leaving everything else identical.',
                '“Federated” here means the training data can remain at participating sites while model updates are communicated. That is a data-placement choice, not by itself a proof that the updates reveal nothing about the data. Privacy requires its own threat model and protections; this paper’s performance results should not be read as such a guarantee.',
            ],
            'sources': [(PDF + '#page=2', 'Conference paper, sections 1–2: frequent synchronization, local steps, and the cross-silo setting')],
        },
        {
            'title': 'The system changes the learning rule to make local work useful',
            'paragraphs': [
                'A straightforward local-training method could use the same learning settings as the frequent-agreement method. Photon instead combines small batches at each site with high learning rates and averages updates across sites. A batch is the examples used to form one update; the learning rate controls how large a step the model takes. The authors argue that federated averaging can tolerate settings that would behave differently under ordinary synchronized training, and that the extra variation in local updates can help the model generalize.',
                'This is the conceptual center of the paper: reducing communication requires a learning process that can make progress between exchanges. The model’s quality after training is therefore part of the systems result. A timing comparison at a fixed count of local steps would be incomplete if one method needed more steps or produced a less useful model. Photon evaluates quality measures as well as time and communication, and its reported advantage belongs to the tested algorithm, models, datasets, and training settings—not a general rule that larger steps always improve learning.',
            ],
            'sources': [(PDF + '#page=4', 'Conference paper, section 3: Photon’s federated optimization and small-batch/high-learning-rate choice'), (PDF + '#page=7', 'Conference paper, section 5.2 and Table 2: model quality results')],
        },
        {
            'title': 'Choose how each site works, not just when sites synchronize',
            'paragraphs': [
                'Photon has to work with links both between sites and inside each site. Where several GPUs are connected well, they can use a conventional distributed method locally. Across a weak link, the system can do more local training before sending updates. The authors adapt among three ways to combine updates: send them to a coordinating machine (a parameter server), have all participants combine them as one group (AllReduce), or pass partial results from one participant to the next in a ring (Ring-AllReduce). They also vary the local multi-GPU arrangement. The useful choice depends on the available connections and the training plan.',
                'This is a layered schedule: use fast coordination inside a site where it is available, then use less frequent coordination across the slower boundary. It is not enough to count transmitted bytes. Include local computation, the time to aggregate updates, any slowest link that holds a round open, and how many rounds are needed to reach the required model quality. The system’s data and compute placement is another part of the schedule: local datasets need not be copied to a central data center, but local data and model updates still have to be prepared and moved at their respective boundaries.',
            ],
            'sources': [(PDF + '#page=5', 'Conference paper, section 4: system design and adaptive local parallelism'), (PDF + '#page=8', 'Conference paper, section 5.3: effect of federation size and local work')],
        },
        {
            'title': 'Read the speedup beside model quality and network assumptions',
            'paragraphs': [
                'For its 7-billion-parameter model, the paper reports perplexity of 13.8 for Photon and 16.6 for centralized training on its stated evaluation. Perplexity measures how well a language model predicts the next text item on a dataset; lower is better on that measure, but it is not a complete measure of all model behavior. In a separate 7B comparison designed to reach the same perplexity, the authors report 95.6 hours for Photon and 147.9 hours for centralized training with a 10 Gbps connection and Ring-AllReduce. The paper explains that federated training used almost twice the compute time but greatly reduced communication time in that setting.',
                'The paper’s 3B and 7B experiments use federations of four to sixteen clients, with all selected clients participating each round. The broader study includes C4 and The Pile; the cited quality table is tied to the paper’s C4 evaluation. These experiments support the possibility of useful low-bandwidth training under the tested cross-silo conditions. They do not establish the same result for phones, unreliable cross-device networks, different data distributions, other model families, or faster interconnects where communication is a smaller part of total time.',
                'The comparison also relies on a declared network model, including a fixed bandwidth for the slowest link in the ring-based method. If a real link slows, drops out, or changes its bandwidth over time, the round time and best communication pattern may change. Preserve the model-quality target, hardware, client count, dataset, local work, and link conditions when comparing a new setup.',
            ],
            'sources': [(PDF + '#page=7', 'Conference paper, sections 5.2 and Table 3: 7B perplexity and time-to-quality comparison'), (PDF + '#page=8', 'Conference paper, sections 5.3–5.5: scaling and data-heterogeneity evaluations'), (PDF + '#page=2', 'Conference paper, section 2.1: assumptions for the cross-silo setting')],
        },
        {
            'title': 'A small timing model shows the trade, not the learning result',
            'paragraphs': [
                'Original teaching model: suppose 100 local training steps each take 2 time units, and each synchronization costs 80 units. If sites synchronize after every step, the total is 100 × 2 + 100 × 80 = 8,200 units. If they synchronize after every 20 steps, the same 100 local steps plus five exchanges cost 100 × 2 + 5 × 80 = 600 units. Under these assumptions the long-distance exchange, not arithmetic, dominates elapsed time.',
                'This arithmetic does not show that the two schedules reach the same model quality. The second schedule uses older shared weights between exchanges, and may need different learning settings or a different number of steps. The real comparison must time both methods until they meet the same stated quality test, counting all local work and communication. That is why a communication reduction by itself is not a training-speed result.',
            ],
        },
    ],
    'exercise': {
        'question': 'Using the paper’s reported 7B time-to-quality values, compute the percentage reduction from 147.9 hours to 95.6 hours. Why is that result not a promise of the same improvement on a faster network?',
        'answer': 'The reduction is (147.9 − 95.6) / 147.9 ≈ 0.354, or about 35.4%, which agrees with the paper’s roughly 35% summary. This comparison uses a 10 Gbps Ring-AllReduce setup where communication is a large cost. With a faster network, the centralized method spends less time communicating, so removing many exchanges may save a smaller fraction of the whole run. The percentage is author-reported evidence for the stated 7B comparison, not an independently reproduced result or universal speedup.',
    },
}
