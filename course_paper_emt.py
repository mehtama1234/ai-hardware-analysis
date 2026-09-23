"""Focused OSDI walkthrough of operating-system support for new translation hardware."""

PDF = 'https://www.usenix.org/system/files/osdi25-chai-siyuan.pdf'

EMT = {
    'id': 'emt-2025',
    'route': 'osdi-2025',
    'title': 'EMT: change how memory is translated without rebuilding the whole OS',
    'identity': 'Siyuan Chai and colleagues · EMT: An OS Framework for New Memory Translation Architectures · OSDI 2025',
    'scope': 'A focused walkthrough of the boundary between Linux memory management and hardware address translation, plus the paper’s correctness, interface-overhead, and emulated-hardware evidence. Reported results have not been reproduced here. The address and cost examples are original teaching models, not paper measurements.',
    'lessons': [('s4', 'Memory and data movement'), ('s7', 'Execution plans'), ('s8', 'Correctness evidence'), ('s10', 'Whole-system cost')],
    'blocks': [
        {
            'title': 'A program’s address is not the memory chip’s address',
            'paragraphs': [
                'A program works with virtual addresses: names for locations in its own address space. Hardware translates those into physical addresses that identify memory locations. The operating system creates and manages the mappings; the memory-management unit (MMU) uses them while the program runs. This division lets programs use a convenient, protected view without needing to know where the bytes physically sit.',
                'A translation design changes how that lookup is represented and performed. Linux must still create, inspect, update, and remove mappings. If Linux assumes every design is a fixed multi-level tree, a new design such as a hash-based table can force changes throughout code that was written around that tree. The hardware idea then carries an operating-system rewrite cost that a hardware-only speed test would not count.',
                'Original teaching model: imagine a building directory that maps a room label to a physical room. One directory is a tree of shelves; another is a hash index. The building staff still need to add, find, move, and remove room assignments. An interface that names those operations without assuming either directory shape can let each directory use its own fast method, provided it preserves the behavior callers require.',
            ],
            'sources': [(PDF + '#page=2', 'Conference paper, sections 1–2: translation designs and the Linux support gap')],
        },
        {
            'title': 'Put a small, precise boundary between Linux and the MMU design',
            'paragraphs': [
                'EMT adds an interface inside Linux. The general memory-management code asks for translation operations through architecture-neutral objects; a hardware-specific MMU driver implements those operations for a particular translation design. The paper groups its interface around translation objects, the database of mappings for an address space, and the service that manages MMU state. With this boundary, adding a scheme should mainly require a driver rather than rewriting the general memory-management code.',
                'A boundary can fail in two opposite ways. If it exposes only a minimal “map this address” operation, it may hide details needed for fast hardware-specific behavior. If every caller depends on the details of one translation structure, the supposed shared interface preserves the old assumption and does not make new designs easier to add. EMT therefore allows selected operations to be customized by the MMU driver while keeping the general meaning of translation visible to Linux.',
                'This is a reusable design question: what facts must callers know to preserve behavior, and what details can the implementation choose? Hiding a detail is safe only if the interface still states the operations and guarantees callers rely on. Performance-critical paths may need a deliberate extension point, not a guess that a generic path is always fast enough.',
            ],
            'sources': [(PDF + '#page=6', 'Conference paper, sections 4–5: EMT interface and customization')],
        },
        {
            'title': 'Check the operating-system framework separately from new hardware',
            'paragraphs': [
                'The paper asks two different questions. First: does adding EMT’s interface to Linux preserve ordinary operating-system behavior and add little cost on existing hardware? Second: can Linux use two experimental translation designs, named ECPT and FPT in the paper, and what operating-system work or performance effects appear? One headline cannot answer both questions, because one uses available hardware and the other depends partly on an experimental hardware model.',
                'For correctness, EMT-Linux with Radix, ECPT, and FPT drivers passed all 1,208 Linux Test Project checks applicable to the tested kernel configuration; the full suite has 1,405 tests.',
                'On the same dual-socket Xeon Gold 6346 machine, EMT-Linux averaged 99.9% of the result from Linux without EMT across 41 small kernel tests. Its larger application tests added under 0.1% overhead. For Redis, Memcached, and PostgreSQL, measured throughput, average response time, and 99th-percentile response time differed by at most 0.1%, 0.1%, and 0.2%. The last measure is a delay threshold near the 99% position in the sorted measurements. Requests beyond that threshold can take longer, so it does not bound the worst delay. These results support a low-overhead claim for the tested Linux setup and workloads, not every kernel path or future MMU.',
                'For the experimental translation systems, the researchers used QEMU to imitate an MMU and connected it to a hardware simulator; QEMU itself does not model the exact timing of every processor cycle. In that evaluated setup, ECPT reduced total cycles by 2.3% averaged across workloads and by 6.6% during the compute-serving phase. The full FPT configuration reduced running-phase total cycles by 6.4%, but that configuration supported only 4 KB base pages, not huge pages. Those are results from the paper’s simulation conditions, not measurements on fabricated ECPT or FPT hardware.',
            ],
            'sources': [(PDF + '#page=11', 'Conference paper, sections 8.1–8.3: correctness, machine, and EMT interface overhead'), (PDF + '#page=14', 'Conference paper, sections 8.4–8.5: OS costs and simulated ECPT/FPT results')],
        },
        {
            'title': 'Use the simulator to choose what hardware must later test',
            'paragraphs': [
                'The framework contributes more than a convenient coding interface: it lets the authors run a working operating system with new translation drivers, observe the operating system’s own work, and test how hardware choices alter that work. For example, an OS page-fault handler can spend time scanning mappings; a faster hardware lookup does not automatically remove that software cost. In the paper, customizing an EMT iterator cuts measured kernel work for one GraphBIG breadth-first-search case, showing that the OS and translation design need to be examined together.',
                'But simulation does not settle what real hardware will do. Results depend on the simulated cache and translation configuration, workload, OS code, and the accuracy of the simulator. The paper itself notes limitations in the emulation and simulation path. A stronger next test would preserve the same workloads and OS version while comparing simulator predictions with hardware measurements as prototypes become available. Until then, the measured Linux-interface overhead and the projected new-MMU behavior must remain separate evidence claims.',
            ],
            'sources': [(PDF + '#page=10', 'Conference paper, section 8.4: iterator optimization and OS work'), (PDF + '#page=15', 'Conference paper, sections 8.5 and 9: simulation limits and development lessons')],
        },
    ],
    'exercise': {
        'question': 'A proposed translation design cuts address-lookup time by 20%, but its OS driver adds 12 ms of work to a request that originally took 100 ms, of which 40 ms was address lookup. In this teaching model, what is the new total and speedup? Which separate evidence would you want before claiming the design is ready for use?',
        'answer': 'The lookup falls from 40 ms to 32 ms, saving 8 ms. Adding the 12-ms driver cost gives 104 ms total, so the proposal is slower: 100/104, or about 0.96×. This invented model shows why faster hardware lookup alone does not establish a faster system. Separately check that the OS preserves required memory behavior, quantify interface and driver work on the target machine, and measure the complete workload on representative hardware. EMT’s reported emulated-MMU results do not substitute for measurements on the proposed hardware.',
    },
}
