"""Focused DAC walkthrough of deadline-aware GPU scheduling."""

PAPER = 'https://arxiv.org/pdf/2504.08795'
DOI = 'https://doi.org/10.1109/DAC63849.2025.11132423'

DARIS = {
    'id': 'daris-2025',
    'route': 'dac-2025',
    'title': 'DARIS: schedule shared GPU work against deadlines, not averages',
    'identity': 'Amir Fakhim Babaei and Thidapat Chantem · DARIS: An Oversubscribed Spatio-Temporal Scheduler for Real-Time DNN Inference on GPUs · DAC 2025',
    'scope': 'A focused walkthrough of GPU oversubscription, staged priority, recent execution-time estimates, and the reported evaluation. The locally extracted manuscript was inspected through the task model, design choices, and evaluation discussion. Results are author-reported and have not been independently reproduced here. The schedules and arithmetic examples below are original teaching models, not measurements or a reimplementation.',
    'lessons': [('queues-and-batching', 'Deadlines and demand'), ('dependencies-and-pipelines', 'Dependencies'), ('s4', 'Routes'), ('s10', 'Whole-system cost')],
    'blocks': [
        {
            'title': 'A fast device can still miss an urgent job',
            'paragraphs': [
                'A GPU may have unused capacity at one moment and still fail a deadline. The key question is not only how much total work exists; it is when each piece can run, which pieces compete for the same execution unit, and when a result is needed. A real-time scheduler therefore has at least two obligations: keep the device usefully busy and leave enough room for urgent work to finish on time.',
                'DARIS targets periodic soft real-time inference tasks with two priority levels. It uses GPU contexts to divide space among groups of work and CUDA streams to run multiple tasks within those groups. The paper also studies oversubscription: the total configured share of streaming multiprocessors can exceed the physical count because tasks take turns using the same units. This can expose more runnable work, but it can also create interference. Oversubscription is a choice to evaluate, not a free increase in hardware.',
                'Original teaching schedule: one GPU has two equal execution slots. At time zero, four jobs arrive, each needing 6 time units, with deadlines at time 8. Running two jobs at a time gives completion times 6 and 12, so two jobs miss. Splitting every job into smaller stages does not by itself fix the problem: the total required work is 24 slot-time units, while the deadline window provides only 16. A scheduler cannot schedule away a capacity deficit; it can only decide which work gets the limited service and how failures are reported.',
            ],
            'sources': [(PAPER, 'Manuscript abstract and sections 1–2: GPU underutilization, spatial/temporal sharing, oversubscription, and real-time goals')],
        },
        {
            'title': 'Staging creates a safe-enough place to change priority',
            'paragraphs': [
                'A running GPU task is not usually paused at every instruction. DARIS divides a neural-network task into sequential stages and permits a scheduling decision at stage boundaries. This is a coarse stopping rule: it gives the scheduler a place to change which task runs, while avoiding the cost of synchronizing after every small kernel. The boundary is part of the design tradeoff. Larger stages reduce coordination but make urgent work wait longer; smaller stages respond sooner but add more synchronization and may reduce useful GPU work.',
                'Original teaching model: a low-priority job has four stages of 3 milliseconds each. An urgent job arrives 1 millisecond after the first stage begins and needs 2 milliseconds. Without staging, the urgent job waits until 12 and finishes at 14. With a boundary after the first 3-millisecond stage, the scheduler finishes that stage, spends 0.5 milliseconds switching, runs the urgent job until 5.5, spends 0.5 switching back, and finishes the low-priority job at 15. The urgent job’s response improves from 13 to 4.5 milliseconds, while the low-priority job finishes 3 milliseconds later.',
                'The example shows why “preemption” is not one number. The result depends on the stage boundary, saved state, switch cost, and whether the urgent task can actually use the released resources. A scheduler that reports only average throughput hides the priority behavior it was built to control. A scheduler that claims hard guarantees must establish stronger timing bounds than the soft-priority evidence described here.',
            ],
            'sources': [(PAPER, 'Manuscript section 3.2 and figure 2: staging as coarse-grained preemption and virtual stage deadlines')],
        },
        {
            'title': 'Use recent measurements without pretending they are guarantees',
            'paragraphs': [
                'GPU execution time changes when other tasks share the device. A worst-case bound may be so conservative that it rejects useful work; a recent measurement may be optimistic and cause a missed deadline. DARIS uses Maximum Recent Execution Time, or MRET: for each stage, it records the largest observed execution time in a recent window. It then sums the stage estimates for a task and uses that estimate to decide how much work a context can accept.',
                'The paper assigns each stage a virtual deadline in proportion to its estimated share of the whole task. If a task has a 10-millisecond deadline, with stage estimates 2 and 3 milliseconds, the virtual deadlines are 4 and 6 milliseconds. This is a way to distribute the task’s deadline across its stages; it is not evidence that either stage always finishes within that time. The estimate changes as the recent window changes, so admission decisions can change with workload history.',
                'Original teaching model: a stage was observed to take 2, 3, and 5 milliseconds in the recent window. MRET is 5. If its deadline is 8 milliseconds, the scheduler reserves 5/5 × 8 = 8 virtual milliseconds for that stage. If a second stage has MRET 3, the two-stage task has MRET 8 and receives virtual deadlines of 5 and 3 milliseconds. A later run taking 6 milliseconds makes the first estimate stale. The method can adapt, but adaptation is not a proof against a new slowdown.',
                'This distinction matters when reading the evaluation. The paper reports fewer misses and higher throughput for its tested workloads and configurations, including 15% over batching and 11.5% over the compared scheduler. Its abstract also reports that all tested high-priority tasks met their deadlines, while low-priority tasks had under 2% deadline misses. Those are measured comparisons under the paper’s setup. They do not establish that every high-priority task on another workload meets a hard deadline, nor that the same ranking holds for another GPU, model mix, or history-window choice.',
            ],
            'sources': [(PAPER, 'Manuscript sections 3.1–3.2 and evaluation: MRET, utilization, virtual deadlines, and reported comparisons'), (DOI, 'Official DAC 2025 publication record: paper identity and venue')],
        },
        {
            'title': 'Read the result as a policy choice with a stated boundary',
            'paragraphs': [
                'DARIS combines spatial allocation, temporal staging, oversubscription, priority, and recent timing history. The central systems lesson is that these choices interact. Increasing the number of runnable tasks may improve utilization but increase interference. More frequent stage boundaries may improve urgent response but consume coordination time. A recent-time estimate may accept more work but can become wrong when the workload changes.',
                'To evaluate such a scheduler, separate the questions. Throughput asks how much work finishes. Deadline-miss rate asks how often work finishes too late. Priority response asks whether urgent work improves relative to lower-priority work. Utilization asks whether the GPU’s capacity was busy. These numbers have different denominators and can move in opposite directions. One favorable percentage cannot stand in for all four.',
                'A fair follow-up would hold the model set, arrival pattern, GPU, software stack, and deadline rule constant while changing one mechanism at a time: batching, spatial sharing, oversubscription, staging frequency, or MRET window. It should record completed work, deadline misses by priority, switch and synchronization time, and the estimate error. This course does not run that experiment; the paper’s measurements remain author-reported.',
            ],
            'sources': [(PAPER, 'Manuscript sections 1, 2, and evaluation: stated goals, design tradeoffs, and measurement boundary')],
        },
    ],
    'exercise': {
        'question': 'A task has two stages with recent estimates 2 ms and 3 ms and a total deadline of 10 ms. What virtual deadline does each stage receive under proportional allocation? If the first stage later takes 4 ms, does the original calculation prove the deadline is still safe?',
        'answer': 'The estimates sum to 5 ms. The first stage receives (2/5) × 10 = 4 ms and the second receives (3/5) × 10 = 6 ms. A later 4-ms first stage does not prove failure or safety by itself: it uses its entire virtual share, and the second stage may still finish in time or may be delayed by interference. The calculation is an allocation rule based on recent estimates, not a hard execution-time guarantee. These numbers are an original teaching model, not a DARIS measurement.',
    },
}
