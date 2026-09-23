"""Focused DAC walkthrough of cache-aware multi-tenant NPU execution."""

PAPER = 'https://arxiv.org/pdf/2505.06625'
DOI = 'https://doi.org/10.1109/DAC63849.2025.11132424'

CAMDN = {
    'id': 'camdn-2025',
    'route': 'dac-2025',
    'title': 'CaMDN: keep useful shared-cache data from being evicted',
    'identity': 'Tianhao Cai and colleagues · CaMDN: Enhancing Cache Efficiency for Multi-tenant DNNs on Integrated NPUs · DAC 2025',
    'scope': 'A focused walkthrough of cache contention, NPU-controlled cache regions, cache-aware mapping, dynamic allocation, and the reported evaluation. The locally extracted manuscript was inspected through sections II–V and the architecture and scheduling algorithms. Results are author-reported and have not been independently reproduced here. The cache counts and timing examples below are original teaching models, not measurements or a reimplementation.',
    'lessons': [('s3', 'Reuse and placement'), ('s4', 'Routes'), ('queues-and-batching', 'Deadlines and demand'), ('s10', 'Whole-system cost')],
    'blocks': [
        {
            'title': 'Cache space is useful only when the next use fits in time',
            'paragraphs': [
                'A cache is a small, nearby store for data that may be used again. Keeping a copy helps only if the copy survives until its next use and is cheaper to read than fetching the data again. When several models share the cache, cache contention lets one model replace another model’s useful copy. The problem is not simply that the cache is full; it is that the stored contents no longer match the future work.',
                'CaMDN starts from two properties of multi-tenant deep-neural-network (DNN) workloads. Some data will not be reused, so placing it in the shared cache displaces data that matters. Other data is reused only after many intervening accesses, so ordinary replacement may evict it before the next use. The paper reports that, in its motivation experiment, increasing co-located models lowered hit rate and increased memory access and latency. Those observations describe its tested workloads and simulator setup, not every model mix.',
                'Original teaching model: a cache holds four blocks. Model A will read A1 twice, with only one other block read between uses; Model B will read B1 once. If the cache keeps all four blocks, A1 hits on its second use. If B streams four one-use blocks through the same cache, it can evict A1 before A returns to it. B performed useful reads, but its one-use data consumed space that A needed later. Bypassing those one-use blocks can reduce total memory traffic even though it sends more of B’s data directly to the processing unit.',
            ],
            'sources': [(PAPER, 'Manuscript sections II-C and II-D: cache hit-rate motivation, reuse counts/distances, and the need to bypass non-reusable data')],
        },
        {
            'title': 'Make ownership explicit when several models share the cache',
            'paragraphs': [
                'A normal cache decides what to keep without asking the NPU program. CaMDN adds a separate NPU-controlled part of the shared cache. It reserves some cache ways for NPU work, gives each model an exclusive region within that NPU part, and uses a page table to translate each model’s virtual cache address to a physical cache location. The purpose is not to make the cache larger. It is to stop unrelated NPU tasks from unexpectedly replacing one another’s controlled data.',
                'The architecture also gives the NPU explicit operations for moving data: ordinary reads and writes, bypassing data that should not occupy the cache, and multicast reads when several NPUs need the same line. This changes the responsibility boundary. The hardware provides controlled storage and translation; the mapping and runtime policy must decide which data deserves that storage. A protected region filled with data that will never be reused is still a poor use of space.',
                'Original capacity example: a 16-page NPU cache is split into 4 pages for model A, 8 for model B, and 4 kept available for a third model. A cannot evict B inside B’s region, but A also cannot borrow B’s unused pages under a fixed partition. Isolation removes one kind of interference and creates a possible underuse cost. Dynamic allocation is needed if the useful shares change while the models run.',
                'The manuscript reports a 32 KB page size for a 16 MB shared cache and a small page-table storage cost in its modeled design. That is an implementation result under the stated configuration. It does not establish that the same page size, cache split, or area overhead is best for another NPU or workload.',
            ],
            'sources': [(PAPER, 'Manuscript section III-B: way partitioning, NPU-exclusive controller, bypass/multicast access, and virtual cache pages')],
        },
        {
            'title': 'Prepare several legal mappings before runtime pressure arrives',
            'paragraphs': [
                'A neural-network layer can often be arranged in more than one legal loop and tile pattern. A mapping chooses how much data is kept nearby, how much is fetched again, and how much local storage is occupied. CaMDN prepares multiple mapping candidates for different cache limits rather than producing one mapping that assumes the cache will always be fully available.',
                'For each layer, its mapper first reduces the choices with rules about cache-line use, private storage, compute use, and loop order. It then solves smaller optimization problems whose objective is reduced DRAM traffic within a specified cache limit. It also creates a layer-block option that keeps intermediate data across several layers when enough cache is available. The block is bounded so one model does not hold the cache indefinitely.',
                'Original teaching model: a layer has three valid mappings. A uses 2 pages and 12 memory transfers, B uses 4 pages and 8 transfers, and C uses 7 pages and 5 transfers. If the current allocation is 3 pages, choose A; if it is 5, choose B; if it is 8, choose C. Choosing C when only 3 pages are available is not an optimization—it is an invalid plan. Choosing A when 8 pages are available is valid, but it causes 7 more transfers than C in this model. The candidate table makes this tradeoff available to the runtime without solving the whole mapping problem for every layer invocation.',
                'The paper’s evaluation uses an indoor cycle-accurate simulator and a synthesized hardware design. Its reported speedup, memory-access reduction, quality-of-service results, and area overhead therefore have different evidence types. A mapping candidate’s modeled memory traffic is not a measurement from a fabricated CaMDN chip, and a simulated deadline rate is not a universal service guarantee.',
            ],
            'sources': [(PAPER, 'Manuscript section III-C and section IV-A: cache-aware mapping candidates, layer-block mapping, and simulator/synthesis boundary')],
        },
        {
            'title': 'Reallocate on predicted need, then fall back safely',
            'paragraphs': [
                'At runtime, the available cache changes as other models move through their layers. CaMDN’s dynamic cache allocation predicts near-future page use, selects the largest candidate that fits the predicted availability, requests those pages, and waits only up to a threshold. If the pages do not become available, it falls back to a candidate needing fewer pages. The system therefore combines an optimistic plan with a bounded escape route; it does not assume its prediction is always correct.',
                'Original timing model: a layer can use mapping A with 2 pages in 4 ms, B with 4 pages in 3 ms, or C with 6 pages in 2 ms. The runtime predicts 5 pages will be available and selects B. Another model keeps its pages longer than predicted, so only 2 pages arrive before the 0.5-ms wait limit. Falling back to A gives a 4-ms layer after the wait, for 4.5 ms total. Waiting forever for C would not be a cache optimization; it would turn a space decision into an unbounded scheduling delay.',
                'This policy creates several quantities that must be kept separate: memory traffic, layer time, cache occupancy, deadline satisfaction, and fairness among models. A reduction in memory access can improve latency, but it does not prove equal progress for every tenant. The paper reports average speedup, scaling results, service-level agreement satisfaction, throughput, fairness, and modeled hardware overhead separately. Read each number against its own baseline and experiment.',
                'A fair follow-up would vary cache capacity, model count, reuse distance, prediction error, and timeout policy while holding the model mappings and hardware configuration fixed. It should report both successful fallback decisions and the cost of waiting. This course does not run that experiment; all paper measurements remain author-reported.',
            ],
            'sources': [(PAPER, 'Manuscript section III-D and sections IV-B–V: dynamic allocation, candidate fallback, QoS metrics, scaling, and reported limits'), (DOI, 'Official DAC 2025 publication record: paper identity and venue')],
        },
    ],
    'exercise': {
        'question': 'A layer has three candidates: A uses 2 cache pages and takes 4 ms, B uses 4 pages and takes 3 ms, and C uses 6 pages and takes 2 ms. The runtime predicts 5 pages, waits 0.5 ms, then discovers only 2 pages are available. Which candidate should it use under a fallback-to-fit policy, and what is the total layer time?',
        'answer': 'It first selects B because B fits the predicted 5 pages. After the wait, only A fits, so it falls back to A. Total time is 0.5 + 4 = 4.5 ms. C is faster in isolation but is not a legal choice under the observed capacity. These values are an original teaching model, not a CaMDN measurement; the point is to count prediction, waiting, legality, and execution together.',
    },
}
