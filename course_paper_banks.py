"""FCCM memory walkthrough with original, explicitly simplified schedules."""
SOURCE = 'https://arxiv.org/html/2503.24132v1'

BANKS = {
    'id': 'banked-memories-2025',
    'route': 'fccm-2025',
    'title': 'Banked Memories: count who needs the same doorway',
    'identity': 'Martin Langhammer and George A. Constantinides · Banked Memories for Soft SIMT Processors · FCCM 2025',
    'scope': 'Based on the author manuscript arXiv:2503.24132v1, especially section III. Conference identity was checked against the official program. The four-bank examples are original teaching models, not the paper’s processor. No hardware was built or benchmark reproduced. The FCCM route retains the broader source-coverage limits.',
    'lessons': [('s3', 'Memory'), ('s4', 'Shared routes'), ('s6', 'Layout choices'), ('physical-design', 'Physical timing')],
    'blocks': [
        {
            'title': 'Enough stored data does not mean enough simultaneous access',
            'paragraphs': [
                'A field-programmable gate array, or FPGA, provides configurable logic and embedded hardware resources. A soft processor is a processor built using those resources rather than a fixed processor circuit supplied as a finished block. SIMT means single instruction, multiple threads: several execution lanes apply an instruction to their own data. Those lanes still need paths into memory.',
                'Divide a memory into four banks, each with one read opportunity per cycle. In this teaching model, word address a goes to bank a modulo 4—the remainder after division by four. All requests are ready together, each read needs one service opportunity, and there is no broadcast for repeated addresses. Ignore setup, return delay, writes, and other traffic for now. Capacity says how many words fit; this access rule says which words can be read together.',
            ],
        },
        {
            'title': 'A complete schedule beats an average',
            'paragraphs': [
                'Read addresses 0, 4, 8, 1, 5, 2, 6, and 3. The bank counts are 3, 2, 2, and 1. Eight reads divided by four banks suggests a two-cycle lower bound, but bank 0 alone needs three cycles. A legal schedule serves 0, 1, 2, 3 first; 4, 5, 6 second; and 8 third. The two-cycle average is not achievable for these addresses.',
                'For one such group, the largest per-bank count is both a lower bound and achievable under our assumptions: each bank simply handles one of its waiting reads in every cycle until it is empty. This argument relies on independent banks and no extra restrictions on issue or return. If the controller can issue only two requests per cycle, or later requests depend on earlier results, bank counts alone are no longer enough to predict completion.',
            ],
        },
        {
            'title': 'What the paper implements',
            'paragraphs': [
                'Section III describes a 16-lane design. Its controller counts requests per bank and uses the largest count to space operations. At each bank, an arbitration rule chooses which waiting request goes next, and return routing sends each finished value back to the lane that asked for it.',
                'In its standard 16-bank configuration, the paper selects the bank from the address’s lowest four binary digits; it also evaluates shifted index mappings. The four-bank remainder rule in this walkthrough is therefore a teaching model, not a claim that it reproduces every address detail of the processor.',
                'The described read path has five cycles of initial control delay and three cycles of memory delay. These are separate from the conflict service count. The paper compares banked and multi-port organizations; this walkthrough isolates the conflict calculation.',
            ],
            'sources': [(SOURCE + '#S3', 'Author manuscript, section III — issue control, arbitration, and return routing'), ('https://www.fccm.org/fccm-2025-program/', 'Official FCCM 2025 program — paper identity')],
        },
        {
            'title': 'Predict the pattern before changing the hardware',
            'paragraphs': [
                'For four reads, adjacent addresses 0, 1, 2, 3 use all four banks and need one service cycle. A stride of two gives 0, 2, 4, 6: only banks 0 and 2 are used, so two cycles are needed. A stride of four gives 0, 4, 8, 12: every read uses bank 0, so four cycles are needed. Equal numbers of reads can have very different costs.',
                'Adding banks does not necessarily remove the conflict. With eight banks, the stride-four addresses alternate between banks 0 and 4 and still need two cycles. With sixteen banks they occupy four distinct banks and need one. These predictions concern this remainder-based mapping. Changing the mapping can change which patterns conflict, so inspect the actual address-to-bank rule rather than using the bank count as a performance score.',
                'A layout change can help without adding banks. Store a four-by-four array row by row: the first column has addresses 0, 4, 8, 12. Reserve five words per row and that column moves to 0, 5, 10, 15, one read per bank. The reserved footprint increases from 16 to 20 words, or 25%. Every consumer must understand the new row spacing, and the extra space must fit. The logical array has not changed; its physical arrangement has.',
            ],
        },
        {
            'title': 'Charge the layout conversion and the clock change',
            'paragraphs': [
                'Suppose, as another explicit teaching assumption, creating that padded layout costs 12 cycles once and each repeated column-read group drops from four service cycles to one. For n repetitions, the original cost is 4n and the changed cost is 12 + n. Four repetitions tie at 16 cycles; five are the first whole-number case that wins, at 17 versus 20 cycles. A one-use input loses. This comparison excludes common unchanged costs and assumes both versions use the same operating rate.',
                'If a design change alters the achievable clock rate, compare elapsed time instead. Eight cycles at 200 million cycles per second take 40 ns; six at 100 million take 60 ns. The design with fewer cycles is slower. Extra banks, request selection, and return routing require physical resources, so a scheduling gain cannot establish a timing gain without an implementation-level timing account.',
                'The route’s manuscript review distinguishes physical footprint from a convenient single resource count. Keep that distinction when comparing alternatives, and keep tool-derived timing separate from measurements of a running device. The manuscript’s abstract and results section disagree on the benchmark count, as recorded in the route; this walkthrough does not resolve that discrepancy or promote it into a new coverage claim.',
            ],
            'sources': [('#route-fccm-2025', 'FCCM route — evaluation boundaries and unresolved benchmark-count discrepancy')],
        },
        {
            'title': 'Connect the mechanism to the other papers',
            'paragraphs': [
                'The FlashInfer example distributes pieces of work among execution workers. This example distributes access demand among memory banks. Both require looking at the busiest required resource, but they are not interchangeable optimizations. Splitting a calculation into more pieces does not help if every piece still waits for the same memory port. Conversely, removing memory conflicts does not repair an uneven compute assignment.',
                'For a complete program, record addresses, bank mapping, request dependencies, control and return costs, operating rate, and conversion work. Then identify what the proposed change actually affects. That record lets you test a specific explanation instead of treating more parallel lanes as a guarantee of more completed work.',
            ],
            'sources': [('#paper-flashinfer-2025', 'Compare with the FlashInfer work-assignment example')],
        },
    ],
    'exercise': {
        'question': 'Four simultaneous reads use addresses 0, 6, 12, and 18. How many service cycles do they need with four banks? With eight banks? Now suppose changing layout costs 15 cycles and saves three cycles per repeated access group. How many repetitions are needed to be strictly faster, assuming the same clock rate and no other changed costs?',
        'answer': 'With four banks the destinations are 0, 2, 0, 2, requiring two cycles. With eight they are 0, 6, 4, 2, requiring one. The layout change needs 3n > 15: five repetitions tie, and six are the first strict win. Bank service counts omit setup and return latency; the final runtime claim must restore those costs and check whether the layout remains valid for other operations.',
    },
}
