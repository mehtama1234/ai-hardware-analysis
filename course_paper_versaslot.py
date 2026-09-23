"""Focused DAC walkthrough of heterogeneous FPGA sharing."""

PAPER = 'https://arxiv.org/pdf/2503.05930'
DOI = 'https://doi.org/10.1109/DAC63849.2025.11132514'

VERSASLOT = {
    'id': 'versaslot-2025',
    'route': 'dac-2025',
    'title': 'VersaSlot: choose FPGA slots around reconfiguration cost',
    'identity': 'Jianfeng Gu and colleagues · VersaSlot: Efficient Fine-grained FPGA Sharing with Big.Little Slots and Live Migration in FPGA Cluster · DAC 2025',
    'scope': 'A focused walkthrough of partial reconfiguration contention, heterogeneous FPGA slots, task bundling, dual-core scheduling, live migration, and the reported evaluation. The locally extracted manuscript was inspected through the system design, scheduling algorithms, and evaluation. Results are author-reported and have not been independently reproduced here. The slot schedules and response-time arithmetic below are original teaching models, not measurements or a reimplementation.',
    'lessons': [('dependencies-and-pipelines', 'Dependencies'), ('s3', 'Capacity and placement'), ('queues-and-batching', 'Scheduling'), ('s4', 'Routes')],
    'blocks': [
        {
            'title': 'Reprogramming a region is work that can block other work',
            'paragraphs': [
                'An FPGA can be configured to perform a particular task, but changing part of its logic takes time. Dynamic partial reconfiguration loads a new bitstream into one region while other regions continue. The loading interface may still accept only one partial bitstream at a time, so several applications can queue for reconfiguration even when their computation slots are otherwise free.',
                'That queue can break a pipeline. Suppose task A finishes in slot 1 and its next task needs slot 2, but slot 2 is waiting for a bitstream load requested by another application. A’s data is ready, yet A cannot continue. If one CPU handles both reconfiguration commands and task launches, the reconfiguration operation can also delay the scheduler that would have launched work in another slot. Counting only the FPGA arithmetic hides both waits.',
                'Original timing model: two applications each have two dependent stages. Each stage computes for 4 ms. Loading a stage takes 3 ms, and only one load can proceed at a time. A time-based whole-FPGA design loads and runs one application at a time: 3 + 4 + 3 + 4 = 14 ms per application, or 28 ms for both. A spatial design can compute in parallel, but if the two applications repeatedly wait on one serial loader, the possible overlap depends on load order; the loader, not the arithmetic, can become the limit.',
            ],
            'sources': [(PAPER, 'Manuscript sections I–II and figure 2: partial-reconfiguration serialization, task blocking, and pipeline disruption')],
        },
        {
            'title': 'Use large and small regions for different shapes of work',
            'paragraphs': [
                'Uniform slots all have one fixed size, so they force every task to fit the same region. A slot that is too large wastes unused logic; one that is too small cannot host the task. VersaSlot uses two region sizes: a Big slot can hold a bundled group of tasks, while Little slots expose smaller pieces of the FPGA to more applications. The choice trades fewer reconfiguration events against more sharing opportunities.',
                'The Big slot does not make a task free. VersaSlot bundles three related tasks into one larger bitstream and can execute them serially or as a pipeline inside that region. The bundle reduces outside reconfiguration contention, but it occupies a large region and may contain an idle stage when the task shapes do not balance. Little slots allow finer placement, but their separate tasks can contend for the reconfiguration interface.',
                'Original capacity model: a board has one Big slot of capacity 2 and four Little slots of capacity 1. Three applications each need three stages of capacity 1. Assigning all work to Little slots exposes four regions but requires repeated loads. Bundling one application’s three stages into the Big slot uses capacity 2 under this simplified model and removes two inter-stage loads from that application. If the Big bundle waits 10 ms for a batch while Little-slot work could finish in 6 ms, the larger region is not automatically the better choice. The policy must count both load savings and occupancy.',
            ],
            'sources': [(PAPER, 'Manuscript sections III-A–III-B and figures 2–3: Big.Little layout, 3-in-1 bundling, serial/pipeline choices, and slot configurations')],
        },
        {
            'title': 'Separate scheduling decisions from bitstream loading',
            'paragraphs': [
                'VersaSlot puts the scheduler and the partial-reconfiguration server on separate CPU cores; this is the paper’s dual-core scheduling arrangement. The scheduler can decide which ready task should run while the other core performs a bitstream load. This removes one direct blocking path, but it does not remove the FPGA’s serial loading limit. The two activities can overlap only when their data, slot state, and dependencies permit it.',
                'The allocator first gives available Big slots to applications that can bundle tasks, then assigns Little slots, redistributes unused capacity, and can unbind a not-yet-started Little-slot application for a different assignment. Rebinding a running dependent pipeline would be unsafe if its next task can no longer reach the required region. A free slot is therefore not enough; the assignment must preserve the application’s dependency path.',
                'Original scheduling model: a task’s compute takes 5 ms and its bitstream load takes 4 ms. With one CPU, the two stages are serialized at 9 ms before the next task can be considered. With separate scheduler and loader cores, the first task still needs 9 ms, but a ready second task can have its 4-ms load overlap the first task’s 5-ms computation if it targets an independent slot. The pair then completes at 14 ms rather than 18 ms. If the second task depends on the first result, that overlap is illegal and the 18-ms comparison does not apply.',
            ],
            'sources': [(PAPER, 'Manuscript sections III-A and III-C: hypervisor, PR server, allocation/rebinding, and dual-core scheduling')],
        },
        {
            'title': 'Move work between boards only when migration costs fit',
            'paragraphs': [
                'A cluster can contain boards with different slot layouts. VersaSlot’s live migration can switch an application between boards and migrate its task and data state so the cluster can change which layout serves the current demand. This lets the scheduler use an available Little slot when Big slots are overloaded, but migration adds transfer and coordination time. A board change is a scheduling action with a cost, not an instantaneous improvement.',
                'Original break-even model: an application waits 12 ms on board A. Board B would run the remaining work in 7 ms, but moving its state takes 4 ms and restarting the destination takes 2 ms. Migration completes in 13 ms, so it loses by 1 ms. If the remaining work on B takes 3 ms instead, migration takes 9 ms and saves 3 ms. A controller needs the remaining-work estimate, transfer cost, and destination readiness before moving the application.',
                'The paper evaluates VersaSlot on an FPGA cluster built from Xilinx UltraScale+ boards and compares response time and logic-resource utilization with four scheduling approaches. It reports up to 13.66× lower average response time than traditional temporal sharing, up to 2.19× improvement over the named spatio-temporal comparison, and average LUT/FF utilization improvements of 35%/29%. These are results for the paper’s boards, applications, scheduling settings, and baselines; they are not measurements made by this course.',
            ],
            'sources': [(PAPER, 'Manuscript sections III-D and IV–V: cross-board switching, live migration, cluster testbed, baselines, and reported results'), (DOI, 'Official DAC 2025 publication record: paper identity and venue')],
        },
    ],
    'exercise': {
        'question': 'A task needs 5 ms of computation and 4 ms of bitstream loading. A second independent task can load while the first computes. What is the completion time for both tasks if the first load starts at time 0, the first computes after loading, and the second load overlaps that computation? What would the time be if the tasks were dependent?',
        'answer': 'The first task loads from 0–4 ms and computes from 4–9 ms. The independent second load runs from 4–8 ms and its 5-ms computation runs from 8–13 ms, so both finish at 13 ms. If the second task depends on the first result, its load starts after the first task completes at 9 ms and finishes at 18 ms. The 13-ms overlap is valid only for independent tasks. These are original teaching times, not VersaSlot measurements.',
    },
}
