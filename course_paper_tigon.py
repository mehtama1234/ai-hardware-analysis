"""Focused OSDI walkthrough of Tigon's CXL-aware distributed database."""

PDF = 'https://www.usenix.org/system/files/osdi25-huang-yibo.pdf'

TIGON = {
    'id': 'tigon-2025',
    'route': 'osdi-2025',
    'title': 'Tigon: put only the cross-host active data on shared memory',
    'identity': 'Yibo Huang, Haowei Chen, Newton Ni, and colleagues · Tigon: A Distributed Database for a CXL Pod · OSDI 2025',
    'scope': 'A focused walkthrough of Tigon’s cross-host active tuple idea, CXL placement, coherence and transaction boundaries, and the emulated-pod evaluation. The final OSDI paper was inspected. Results are author-reported and have not been reproduced here. The small transaction schedules are original teaching models.',
    'lessons': [('s3', 'Memory and movement'), ('s4', 'Shared connections'), ('s7', 'Coordination and durability'), ('s8', 'Correctness evidence'), ('s10', 'Whole-system results')],
    'blocks': [
        {
            'title': 'The database is large, but the contested part can be small',
            'paragraphs': [
                'A distributed transactional database must keep concurrent operations from producing an invalid result. In a shared-nothing design, each host owns a partition. A transaction that touches several partitions sends messages and may use two-phase commit, so coordination grows with cross-host access. Putting all data in a shared, slower memory would avoid some messages but would make ordinary local reads pay the remote cost.',
                'Tigon starts from a narrower observation: a large database does not mean that every tuple is being accessed by different hosts at the same moment. It calls the currently shared set the cross-host active tuples, or CAT. The system keeps the database partitions in local DRAM and moves a tuple into shared CXL memory when another host needs it. The shared region holds the contested working set, not the whole database.',
                'The paper gives a scale example: a TPC-C transaction, from a standard database transaction benchmark, touches about 39 tuples, around 7 KB, so 1,000 simultaneously active transactions would expose at most about 39,000 tuples or 7 MB, under its assumptions. That calculation is an upper estimate for the active set, not proof that every workload has a small CAT. A workload with broad scans, long transactions, or many concurrently shared records could change the placement decision.',
            ],
            'sources': [(PDF + '#page=2', 'OSDI paper, section 1: CAT motivation and active-tuple example')],
        },
        {
            'title': 'Use each memory tier for the work it can afford',
            'paragraphs': [
                'CXL memory can be shared by several hosts and accessed with ordinary load and store instructions, but it is not equivalent to local DRAM. The paper cites measured CXL latency of 214–394 ns versus 111–117 ns for local DRAM, and read-only bandwidth of 18–52 GB/s versus 218–246 GB/s in the cited hardware study. Exact values depend on the device and access pattern. A design that moves every tuple to CXL would replace message costs with a slower memory path.',
                'Tigon keeps owner-host data in local DRAM when it is private. When another host needs it, the owner moves it into the shared region and records metadata that lets both hosts find and protect it. Tigon also keeps a shortcut pointer at the owner so repeated access can avoid searching the shared index. The pointer is an optimization with a correctness obligation: movement and pointer updates must not make a concurrent operation follow stale location information.',
                'Original break-even model: a local access costs 1 unit, a CXL access costs 4, and a network round trip costs 12. Moving one tuple to CXL costs 3 units and then serves five remote reads at 4 each, for 23 total. Leaving it local and using five network reads costs 60. If only one remote read occurs, movement plus one CXL read costs 7 and the network costs 12; moving still wins in this toy model. If the move costs 15 instead, one read loses and five reads cost 35 versus 60. Reuse count and movement cost decide, not the label “shared memory.”',
            ],
            'sources': [(PDF + '#page=3', 'OSDI paper, section 2: CXL latency, bandwidth, and coherence limits'), (PDF + '#page=4', 'OSDI paper, section 3.1: partitioning, CAT movement, and local access')],
        },
        {
            'title': 'Limited hardware coherence changes the protocol design',
            'paragraphs': [
                'CXL can provide hardware cache coherence across hosts, but the hardware-coherent region is limited in practical devices. Tigon therefore places the small synchronization structures in the hardware-coherent area and uses a software coherence protocol for other shared metadata. The system is not claiming that all CXL memory has the same visibility or cost. The location of a lock, index, tuple, or message determines which mechanism protects it.',
                'Tigon uses atomic operations, latches, and locks on the shared active data so hosts can coordinate without the same message exchange and two-phase commit used by a partitioned design. It also changes concurrency-control and logging protocols to retain transaction semantics. Removing a network round trip does not remove the need to define who owns a tuple, when a write is visible, what a reader may observe, and how a crash is recovered.',
                'Use a toy transaction that reads a remote balance and writes a local order. If the balance moves to shared memory but the log remains local, a crash can leave the shared balance changed without a durable record of the order. A fast atomic update has not established durability. Tigon assumes fail-stop failures and uses local SSD logging; those assumptions bound what its recovery claim means. Do not turn “atomic CXL operation” into a general database correctness guarantee.',
            ],
            'sources': [(PDF + '#page=3', 'OSDI paper, sections 2 and 2.1: hardware-coherent region and failure model'), (PDF + '#page=4', 'OSDI paper, section 3: concurrency-control and data-movement design')],
        },
        {
            'title': 'Compare complete transactions, not only the transport',
            'paragraphs': [
                'Tigon’s evaluation emulates an eight-machine CXL pod using eight virtual machines on one system with a 128 GB CXL 1.1 device. The CXL device has 1.6× the measured latency of local DRAM and 13% of its bandwidth under the stated 3:1 read/write test. The physical host’s cache coherence implements inter-VM coherence faster than future real inter-host coherence is expected to be, so the authors analyze higher coherence latency separately. This is an emulated-pod result, not a measurement from an eight-host physical CXL pod with the proposed coherence hardware.',
                'The baselines are not left untouched. The authors compare Sundial and DS2PL, improve them to support all five TPC-C transactions and durability, and give them CXL memory as a transport in separate comparisons. Tigon uses a 16 MB non-hardware-coherent CXL message area while those baselines receive 512 MB because they pass larger messages. These details matter: a headline comparison without the baseline modifications and transport boundary would not say what caused the difference.',
                'The paper reports up to 2.5× higher throughput than two optimized shared-nothing databases using CXL as a transport and up to 18.5× over an RDMA-based distributed database on TPC-C and a YCSB variant, a key-value-store workload. RDMA, or remote direct memory access, lets one machine access another machine’s memory with little intervention from the remote CPU. Tigon prioritizes throughput using group commit and reports 30 seconds of warm-up followed by 30 seconds of measurement. The results belong to those workloads, transaction mixes, emulator, memory budget, logging settings, and baselines. They do not establish lower latency for every transaction or scalability beyond the CXL pod’s small host count.',
            ],
            'sources': [(PDF + '#page=10', 'OSDI paper, section 4.1: emulated pod, hardware limits, and baseline construction'), (PDF + '#page=2', 'OSDI paper, abstract and introduction: reported throughput comparisons')],
        },
    ],
    'exercise': {
        'question': 'In the teaching model, local access costs 1, CXL access costs 4, a network round trip costs 12, and moving a tuple costs 3. What is the total cost of five remote reads if the tuple is moved once to CXL? How does that compare with leaving it remote and using the network each time? Name one correctness or durability fact the arithmetic does not establish.',
        'answer': 'Moving once costs 3 and five CXL reads cost 20, for 23 units. Five network round trips cost 60, so the toy model favors moving. It does not establish that the tuple’s location metadata stays correct under concurrent movement, that the write is visible under the required transaction rule, or that the update survives a crash. Those need protocol and recovery evidence; the numbers are an original teaching model.',
    },
}
