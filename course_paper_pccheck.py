"""Focused ASPLOS walkthrough of concurrent persistent checkpointing."""

PDF = 'https://anakli.inf.ethz.ch/papers/PCcheck_asplos25.pdf'

PCCHECK = {
    'id': 'pccheck-2025',
    'route': 'asplos-2025',
    'title': 'PCcheck: make recovery protection part of the training pipeline',
    'identity': 'Foteini Strati, Michal Friedman, and Ana Klimovic · PCcheck: Persistent Concurrent Checkpointing for ML · ASPLOS 2025',
    'scope': 'A focused walkthrough of checkpoint interval, failure recovery, concurrent snapshots, pipelined persistence, consistency, and the reported evaluation. The local primary paper text and evidence excerpt were inspected. Results are author-reported and have not been independently reproduced here. The failure and pipeline calculations are original teaching models.',
    'lessons': [('dependencies-and-pipelines', 'Dependencies'), ('s1', 'Whole-request timing'), ('s8', 'Reliability'), ('s10', 'Whole-system cost')],
    'blocks': [
        {
            'title': 'A checkpoint is insurance with a recurring premium',
            'paragraphs': [
                'A long ML training job can lose work when a GPU, machine, network, software component, or spot VM fails. A checkpoint records a state from which training can resume. Checkpointing too rarely means a failure forces more recomputation. Checkpointing too often can pause training or compete with it for GPU-to-CPU bandwidth, memory, and storage.',
                'The useful quantity is goodput: completed useful training work after subtracting work repeated after failures. Raw training throughput with no failures does not answer the recovery question. A checkpoint mechanism must therefore be judged across the normal path and the failure path, with the interval, checkpoint cost, failure pattern, and restart boundary stated.',
                'Original interval model: training makes 100 useful steps per hour and a failure occurs once per hour on average. With checkpoints every 20 steps and 2 steps of checkpoint overhead each time, the job spends 10% of its time checkpointing; a failure loses at most 20 steps, or an average of about 10 under a uniform failure point. With checkpoints every 50 steps, overhead is lower but average lost work is about 25. The better interval depends on the real failure and checkpoint distributions.',
            ],
            'sources': [(PDF, 'PCcheck paper, abstract and introduction: checkpoint frequency, failures, recovery, and goodput')],
        },
        {
            'title': 'Concurrent checkpoints remove a hidden serial dependency',
            'paragraphs': [
                'Older systems may overlap a checkpoint with training, but still allow only one checkpoint to be in flight. If the next snapshot must wait until the previous snapshot has reached durable storage, a short checkpoint interval eventually turns into a queue and stalls the GPU. PCcheck permits multiple checkpoints to progress concurrently, while an orchestrator tracks which pieces belong to which checkpoint.',
                'The design uses copy-on-write snapshots so training can continue while a checkpoint reads a stable view, then pipelines movement from GPU to CPU memory and from CPU memory to SSD or persistent memory. Splitting a checkpoint into chunks lets copying and persistence overlap. Concurrency creates extra memory and storage demand, so the system must retain enough state to guarantee at least one complete valid checkpoint.',
                'Original pipeline model: copying a checkpoint takes 6 units and persisting it takes 8. Three checkpoints sequentially take 42 units. With two stages and enough buffers, the first takes 14 and each later checkpoint takes max(6, 8) = 8, for 30 units. If storage can hold only one in-flight checkpoint, the overlap disappears; if a chunk is overwritten before persistence finishes, speed has violated recoverability.',
            ],
            'sources': [(PDF, 'PCcheck paper, sections 2–3: one-checkpoint bottleneck, concurrent orchestration, copy-on-write, and pipelined persistence')],
        },
        {
            'title': 'The fastest snapshot is useless if its state is inconsistent',
            'paragraphs': [
                'Training changes model parameters and optimizer state while checkpoint data is being copied. A checkpoint must represent a coherent training point, not a mixture of values from unrelated steps. PCcheck coordinates snapshots, chunks, and distributed replicas so the persisted result can be identified as a valid recovery point. Concurrency therefore requires a consistency rule and a commit rule, not only more buffers.',
                'The extra state also has a capacity cost. Multiple checkpoints consume DRAM and persistent storage; PCcheck’s storage requirement grows with the number of concurrent checkpoints while retaining at least one valid complete checkpoint. A system that fits its GPU workload but exhausts CPU memory or storage is not an end-to-end success.',
                'Original consistency example: a model has chunks A, B, and C. Checkpoint 1 has copied A and B when training changes C; checkpoint 2 then copies the new C and A. Neither mixed set is automatically a valid checkpoint. The orchestrator must preserve which version of each chunk belongs together and expose only a fully committed set. If a failure occurs between chunk writes, recovery must choose the last complete set rather than the newest individual chunk.',
            ],
            'sources': [(PDF, 'PCcheck paper, section 3: snapshot coordination, chunk ordering, distributed checkpoints, and storage/memory footprint')],
        },
        {
            'title': 'Keep throughput, recovery, and goodput in separate columns',
            'paragraphs': [
                'The paper reports that PCcheck can checkpoint as frequently as every 10 training iterations with about 3% training-throughput overhead in its stated experiments. It evaluates A100-40GB systems and examines SSD and persistent-memory settings, including a 64-A100 spot-VM trace. The paper reports up to 2.86× higher goodput than the compared checkpointing systems in the stated scenarios.',
                'The 3% number is a steady-state throughput result. It does not by itself establish how many iterations are lost after every failure, the full recovery duration, energy, dollar cost, or application-level exactly-once behavior. Goodput adds a failure trace and recomputation rule, so it answers a different question from checkpoint overhead without failures.',
                'The evidence is bounded to the paper’s models, A100 hardware, checkpoint formats, storage systems, failure trace, and comparison policies. This course has not reproduced PCcheck or validated the production failure distribution. A fair follow-up should report checkpoint cost, storage occupancy, complete-checkpoint validity, recovery time, lost work, and useful progress under the same failure trace.',
            ],
            'sources': [(PDF, 'PCcheck paper, evaluation: A100 results, checkpoint interval, throughput overhead, goodput, and failure-trace boundary')],
        },
    ],
    'exercise': {
        'question': 'A checkpoint copy takes 6 units and persistence takes 8 units. For three checkpoints, what is the sequential time? With two pipeline stages and enough buffers, what is the ideal time? What additional condition must hold before the shorter time counts as a reliable training improvement?',
        'answer': 'Sequential time is 3×(6+8) = 42 units. Ideal pipelined time is 6+8 + 2×max(6,8) = 30 units. The shorter time counts only if each persisted checkpoint is a coherent, complete recovery point, the buffers and storage fit, and failure/restart work is included in the end-to-end comparison. These are original teaching calculations, not PCcheck measurements.',
    },
}
