"""Bounded MICRO paper reading and separately labeled cache teaching scenarios."""
PAPER = 'https://arxiv.org/html/2509.14041v1'

TRRIP = {
    'id': 'trrip-2025',
    'route': 'micro-2025',
    'title': 'TRRIP: carry knowledge of code reuse to the cache',
    'identity': 'Henry Kao and colleagues · A TRRIP Down Memory Lane · MICRO 2025',
    'scope': 'Focused reading of the author manuscript, sections 2.4, 3, and 4.1–4.4. Results are author-reported, not reproduced. Teaching policies below are not TRRIP implementations.',
    'lessons': [('s3', 'Reuse and capacity'), ('s6', 'Compiler information'), ('s8', 'Evidence boundaries'), ('s1', 'Whole-request timing')],
    'blocks': [
        {
            'title': 'Instructions must arrive before the processor can use them',
            'paragraphs': [
                'A program needs stored instructions as well as stored input values. A cache keeps a limited number of recently fetched blocks close to the processor. Finding a requested block there is a hit; needing to fetch it from farther away is a miss. When all slots are occupied, bringing in a block requires choosing which resident block to remove. The removed block may soon be needed again.',
                'Frequency and recency answer different questions. A block can be used often across a complete run yet have many other blocks accessed between its uses. A policy observing only a short recent history may not retain it long enough. Conversely, a block popular earlier can become useless after the program enters a different phase.',
                'TRRIP uses execution profiles to classify code by frequency: “hot” is not physical temperature. The compiler groups code; the loader and operating system attach page-level hints carried with memory requests. Its cache policy uses those hints to favor hot instructions. It changes how soon a newly loaded or reused block should be considered for removal, while retaining RRIP’s aging-based eviction rule; it does not permanently lock hot blocks in place.',
            ],
            'sources': [(PAPER + '#S3', 'Author manuscript, section 3'), ('https://doi.org/10.1145/3725843.3756110', 'Conference publication')],
        },
        {
            'title': 'Follow six accesses through two slots',
            'paragraphs': [
                'Use an original teaching cache with two slots. Initially it holds blocks H and A, with H least recently used. Every access is sequential. A hit costs one time unit; a miss costs ten including the fetch. All named blocks compete for these same slots. Compare two deliberately simple policies: remove the least recently used block, or reserve one slot for H throughout this short example and use the other for everything else. The second policy isolates the value and danger of a reuse hint; it is not TRRIP’s algorithm.',
                'Read B, C, H, A, C, H. Under the recency policy, B removes H, C removes A, H removes B, A removes C, C removes H, and H removes A. Every access misses, costing sixty units. The stored pair after each access is B/A, B/C, H/C, H/A, C/A, and C/H; pair order here describes membership, not recency.',
                'With H reserved, B and C successively replace the other slot. H then hits. A and C replace the other slot again, and the last H hits. Four misses and two hits cost forty-two units. The policy did not make memory faster or increase the cache size. It changed which earlier work survived until reuse.',
                'This starting state is part of the experiment. Loading H and A initially would have a cost if the measurement began with an empty cache. Comparing a warmed alternative against an empty baseline would mix two different changes. Likewise, placing blocks in different cache groups could remove the competition assumed here.',
            ],
        },
        {
            'title': 'Use a changed trace to challenge the hint',
            'paragraphs': [
                'Restart from the same H/A state, but now read B, C, B, C. The recency policy misses for B and C, then hits for both, costing twenty-two units. Reserving H causes all four reads to miss, costing forty. H occupies half the available space without supplying a single hit. An honest explanation must include this failure case, not only a trace chosen to reward its policy.',
                'A profile is evidence about the executions used to collect it. To use it elsewhere, ask whether program version, input mix, and execution phase still support its prediction. A stale performance hint should affect which block is fetched again, not permit returning the wrong instruction bytes. Correctness still requires valid address mappings and valid cached contents.',
                'Granularity also matters. In another invented layout, a 4 KiB page contains sixty-four 64-byte instruction blocks, only one of which is frequently used. One shared label cannot distinguish that block from its sixty-three neighbors. Grouping frequently used code together can make a page-level description more informative, but code movement, padding, and the resulting access pattern need their own accounting. This is a question to investigate, not a measured overhead attributed to TRRIP.',
            ],
        },
        {
            'title': 'Separate fewer misses from faster completion',
            'paragraphs': [
                'Our first trace removes two of six misses, a one-third reduction. Its cache-access time falls from sixty to forty-two units, a thirty-percent reduction, because the two replacement hits still cost time. If the rest of the task takes one hundred unchanged units with no overlap, complete time falls from 160 to 142: an 11.25% reduction. The time ratio is about 1.13, not the cache-only ratio of about 1.43.',
                'Real execution can overlap some memory waiting with other work. In that case, adding every miss penalty to the total would overcount delays. The needed quantity is the waiting that actually postpones the accepted result. If a unified cache stores both instructions and data, also count whether retaining more instruction blocks displaces useful data. Improving one miss counter alone does not answer that question.',
                'The paper evaluates TRRIP in Sniper using ten proxy workloads, profile-guided compilation, and 400 million simulated instructions after fast-forwarding. It reports a 3.9% geometric-mean speedup over SRRIP. A geometric mean combines per-workload time ratios by multiplying them and taking the matching root; it does not say that every workload became 3.9% faster, or that any one workload had that result. Wrong-path execution and prefetching are omitted. These are simulation results, not measurements of a manufactured TRRIP processor.',
            ],
            'sources': [(PAPER + '#S4', 'Author manuscript, section 4')],
        },
        {
            'title': 'Connect the mechanism to the rest of the course',
            'paragraphs': [
                'The compiler-to-cache handoff has the same teaching structure as the ASPLOS reservation example: identify what information crosses an interface and what it promises. A frequency hint predicts usefulness; a reservation promises capacity. Treating the first as the second would hide the possibility that too many supposedly useful blocks compete for the same space.',
                'Compare this with the ISCA representation examples. Packing values changes how many bytes a consumer must fetch; choosing cache residents changes which fetches are repeated. Both can reduce traffic, but through different mechanisms. A combined design needs a common workload and measurement boundary before their savings can be added or multiplied.',
                'A discriminating follow-up experiment would hold the cache size, initial contents, code, and input trace fixed while changing only the policy. Then repeat with a changed execution phase and report instruction misses, data misses, and complete execution time. Finally vary the profile used for hints separately from the evaluated input. These are proposed checks, not experiments performed by this course.',
            ],
        },
    ],
    'exercise': {
        'question': 'Repeat both teaching traces from H/A, but let a hit cost two units and a miss cost eight. What does each policy cost on each trace? For the first trace, add one hundred unchanged non-overlapping units of other work. What fraction of complete time does the hint save?',
        'answer': 'For B,C,H,A,C,H, recency has six misses: 48 units. Reserving H has four misses and two hits: 36. For B,C,B,C, recency costs 2×8 + 2×2 = 20, while reserving H costs 4×8 = 32. With one hundred other units, the first trace takes 148 versus 136. The saving is 12/148, about 8.11%, not the cache-only 25%. These results apply only to the stated teaching policies and traces; they neither reproduce nor predict TRRIP’s reported speedup.',
    },
}
