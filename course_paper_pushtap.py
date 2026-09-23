"""Focused ASPLOS walkthrough of one layout serving two access patterns."""

PAPER = 'https://doi.org/10.1145/3676642.3736120'
ARXIV = 'https://arxiv.org/abs/2508.02309'

PUSHTAP = {
    'id': 'pushtap-2025',
    'route': 'asplos-2025',
    'title': 'PUSHtap: make one data layout serve transactions and analysis',
    'identity': 'PUSHtap: PIM-based In-Memory HTAP with Unified Data Storage Format · ASPLOS 2025',
    'scope': 'A focused walkthrough of access direction, one-copy layout, updates, snapshots, controller scheduling, and the reported evaluation. The paper record and primary full-text link were inspected. Results are author-reported and have not been independently reproduced here. The transfer and freshness calculations are original teaching models.',
    'lessons': [('s3', 'Memory'), ('s6', 'Compilation'), ('s7', 'Parallel hardware'), ('s10', 'Whole-system cost')],
    'blocks': [
        {
            'title': 'A layout is a decision about who reads which neighbors',
            'paragraphs': [
                'A transaction usually needs a complete record: read an account row, change a balance, and write the row back. An analytical query often needs one field from many records: scan every price or timestamp. This combination is called hybrid transactional/analytical processing (HTAP): the same data store must serve both updates and analysis. A row-oriented layout makes the first job efficient and a column-oriented layout makes the second job efficient. Keeping both layouts gives each reader what it wants, but it duplicates data and creates a freshness problem when a transaction changes one copy before the other.',
                'PUSHtap asks whether the two readers can use different directions through one physical arrangement. Its processing-in-memory (PIM) design puts calculation near the stored data. The CPU accesses across memory devices in an interleaved direction, so a row can be assembled from pieces across devices. A processing unit inside one device accesses locally in the other direction, so a column can be scanned in parallel within devices. The central idea is not that rows and columns are both contiguous in the ordinary sense; it is that the hardware provides two access directions through the same stored values.',
                'Original four-record model: a CPU row read costs one transfer when the four fields of a record travel together. A PIM column scan costs four local transfers when the four records of a field are separated across one device. After remapping the same physical values, suppose the CPU row costs two transfers and PIM scans cost one. A layout choice should be judged by the actual mixture of readers, not by calling either row or column access universally better.',
            ],
            'sources': [(PAPER, 'PUSHtap paper record and primary publication: unified format, CPU interleaved access, and PIM localized access'), (ARXIV, 'Primary full-text version: access directions and unified HTAP layout')],
        },
        {
            'title': 'Packing and rotation keep the shared layout from wasting capacity',
            'paragraphs': [
                'Columns do not all have the same width. If every column is padded to the widest one, the layout wastes space; if alignment is ignored, the PIM units may need awkward partial accesses. PUSHtap groups columns with similar widths using a packing rule and exposes a threshold that trades padding against alignment. That is a concrete storage decision with a measurable cost, not a claim that alignment is free.',
                'Even a compact layout can create a hotspot. If a frequently scanned column always lands on one PIM device, that device determines the scan time while other devices wait. PUSHtap rotates the column-to-device assignment across blocks of rows. The values remain in one logical table, but the physical owner changes from block to block so repeated scans share the work more evenly.',
                'Original balance model: four devices receive column work of 10, 10, 10, and 40 units. The group finishes in 40 units because the busiest device is the limit. A rotation that makes the four blocks distribute 25, 25, 10, and 10 per round has a 25-unit limit. If rotation itself adds 3 units of setup, the new total is 28, still below 40. If the query touches only one small block, the setup may not pay back; the workload determines whether balancing is worthwhile.',
            ],
            'sources': [(ARXIV, 'Primary full-text version: compact aligned format, width grouping, threshold, and block-circulant placement')],
        },
        {
            'title': 'One copy still needs a rule for updates and reader visibility',
            'paragraphs': [
                'A single physical table does not remove the problem of a reader observing an update halfway through. PUSHtap uses multi-version concurrency control (MVCC): it keeps versions of changed rows and gives each reader a defined view. The system separates a main data region from a delta region for recent changes. An analytical reader uses a snapshot describing which row version is visible; updates can proceed without rewriting the entire main region immediately. The snapshot is encoded as compact visibility bits and distributed to the devices so local processing can skip versions that do not belong to the query’s view.',
                'This is a consistency mechanism, not merely a storage trick. The system must define when a snapshot is taken, which update versions it includes, what happens if a row has both an old main copy and a newer delta, and when cleanup can merge them. Defragmentation moves data back into a cleaner arrangement, but that maintenance work has to be scheduled and charged. Freshness, isolation, storage overhead, and cleanup time are separate results.',
                'Original visibility model: rows 1–4 have main values 10, 20, 30, and 40. An update creates a delta value 35 for row 3. A snapshot bit pattern 1101 means rows 1, 2, and 4 use the main region while row 3 uses its committed delta; a reader that ignores the snapshot can return 30 or 35 unpredictably. The bitmap is only useful if the reader applies the stated version rule. In this model, a four-bit snapshot costs 4 bits; that arithmetic does not establish PUSHtap’s measured storage overhead.',
            ],
            'sources': [(ARXIV, 'Primary full-text version: MVCC, main/delta regions, bitmap snapshots, and PIM-assisted defragmentation')],
        },
        {
            'title': 'Concurrency needs a controller that knows which side is waiting',
            'paragraphs': [
                'CPU transactions and PIM analysis share the memory devices. Letting either side issue unrestricted requests can make the other side wait behind long transfers. PUSHtap adds memory-controller support for fine-grained scheduling and polling, and uses a two-phase analytical path: load the needed data, then perform the PIM computation. The controller’s job is to coordinate the two access directions while keeping the CPU from being blocked for the whole analytical query.',
                'The useful end-to-end question is not just whether PIM bandwidth rises. Ask how long a transaction waits, how much data the analysis loads, whether the snapshot is current, how much storage the format consumes, and how much controller and cleanup work is added. A design that wins the analytical kernel but delays every transaction may fail the HTAP goal. Conversely, preserving transaction response while reducing analysis throughput may be the right choice for a different service promise.',
                'The paper reports 3.4× OLAP (online analytical processing) throughput and 4.4× OLTP (online transaction processing) throughput over its multi-instance PIM-based baseline on the CH-benchmark combination of TPC-C and TPC-H. It also reports 97.4% PIM effective bandwidth at threshold 0.6, 2.3% snapshot storage overhead, and 0.8% zero-padding overhead. These values belong to the paper’s hardware model, benchmark, baseline, and settings; they are not measurements from this course. The stated limitation is concrete: layout choices that classify columns assume a relatively stable analytical workload, so changing query patterns can require retuning.',
            ],
            'sources': [(PAPER, 'PUSHtap paper record: reported OLAP/OLTP comparison and benchmark identity'), (ARXIV, 'Primary full-text version: controller support, evaluation, overheads, and workload boundary')],
        },
    ],
    'exercise': {
        'question': 'An invented workload has six row reads and two column scans. Layout A costs 1 transfer per row read and 4 per column scan. Layout B costs 2 per row read, 1 per column scan, and 8 transfers once to convert or prepare the layout. Which layout is cheaper under these assumptions? What must be checked before applying that choice to PUSHtap?',
        'answer': 'Layout A costs 6×1 + 2×4 = 14 transfers. Layout B costs 8 + 6×2 + 2×1 = 22, so A wins for this workload. The choice could change with more column scans, cache retention, update traffic, snapshot work, controller contention, or a different conversion cost. These are original teaching calculations, not PUSHtap measurements; the paper’s reported gains remain bounded to its evaluated PIM design, benchmark, and baselines.',
    },
}
