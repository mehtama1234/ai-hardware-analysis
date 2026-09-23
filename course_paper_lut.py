"""ISCA lookup-table walkthrough: source summary plus original exact examples."""
PDF = 'https://arxiv.org/pdf/2408.06003v3'

LUT = {
    'id': 'lut-tensor-core-2025',
    'route': 'isca-2025',
    'title': 'LUT Tensor Core: when is a saved answer cheaper than doing the arithmetic?',
    'identity': 'Zhiwen Mo and colleagues · LUT Tensor Core: A Software-Hardware Co-Design for LUT-Based Low-Bit LLM Inference · ISCA 2025',
    'scope': 'Uses author manuscript arXiv:2408.06003v3, with conference identity checked against the official ISCA program. The design overview and evaluation methodology were inspected. The small tables and cost examples below are original explanations, not the proposed processor or reproduced measurements. Detailed implementation and accuracy review remain outside this focused walkthrough.',
    'lessons': [('s2', 'Number representations'), ('s3', 'Storage and access'), ('s6', 'Preparation and compilation'), ('physical-design', 'Evidence stages')],
    'blocks': [
        {
            'title': 'Build a table you can check by hand',
            'paragraphs': [
                'A dot product multiplies corresponding entries and adds the results. Start with values 3 and 5, and let each of two weights be either 0 or 1. There are only four weight pairs. Their answers are (0,0) → 0, (0,1) → 5, (1,0) → 3, and (1,1) → 8. Once this table exists, a weight pair selects an answer instead of repeating the multiply-and-add calculation. A lookup table is a set of stored answers indexed by the choice that produced them.',
                'The table depends on the input values, not just on the set of allowed weights. If the values change to 4 and 5, the answers become 0, 5, 4, and 9. The old table is now wrong for two pairs. Reuse is possible across several weight pairs applied to the same values; it does not imply that one table works for every future input. Identify precisely what remains unchanged while amortizing its construction cost.',
            ],
        },
        {
            'title': 'What the paper changes',
            'paragraphs': [
                'LUT Tensor Core moves table preparation out of each lookup unit into a separate earlier computation, then combines that preparation with the preceding operation so the table need not be written out and read back unnecessarily. It changes the interpretation of weight codes, together with their scale and offset, so opposite signed patterns have opposite table answers; one stored answer plus a sign rule can then replace two. It also stores table entries in a smaller format when its stated error handling allows that.',
                'For weights with several bits, its bit-serial design treats the weight as separate one-bit positions, looks up each position’s contribution, and shifts before combining them. This avoids building one much larger table, but it still requires multiple lookups and combination work. The paper’s elongated tile shape lets one activation-dependent table serve more weight columns. New instructions and compiler support tell the hardware which table operation and shapes to use. The proposal is a joint execution design, not simply storing low-bit weights and assuming ordinary hardware will execute them efficiently.',
            ],
            'sources': [(PDF + '#page=2', 'Author manuscript — design overview'), ('https://www.iscaconf.org/isca2025/program/', 'Official ISCA 2025 program — paper identity')],
        },
        {
            'title': 'More weight bits need not require one enormous table',
            'paragraphs': [
                'For an original two-bit unsigned example, write each weight as b₀ + 2b₁, where each b is 0 or 1. With input values 3 and 5 and weights 1 and 2, the low-bit pair is (1,0), selecting 3 from our table. The high-bit pair is (0,1), selecting 5. Combine them as 3 + 2 × 5 = 13, matching 3 × 1 + 5 × 2. One binary table can serve both bit positions, but two selections and a weighted combination remain.',
                'This derivation is exact for the stated unsigned integers. Signed numbers need the correct sign rule; scaled quantized values may also need offsets and scaling. Those are not optional bookkeeping. Changing representation without carrying its interpretation through the calculation can make every lookup individually correct while the final result is wrong.',
                'A different exact example explains symmetry. If two weights are each −1 or +1, the answers for inputs 3 and 5 are −8, 2, −2, and 8. Opposite weight pairs produce opposite answers, so storing one answer from each pair plus a rule for the sign can replace four stored answers with two. The sign handling still needs execution support. For binary weights b, the relation b = (s + 1)/2 also shows why reinterpreting 0/1 as −1/+1 requires a correction: the binary dot product is half the signed dot product plus half the sum of the inputs.',
            ],
        },
        {
            'title': 'Count construction, storage, and use together',
            'paragraphs': [
                'With g binary weights in one group, there are 2 to the power g possible weight patterns. A straightforward full table has that many answers. If each answer occupies two bytes, a group of four needs 16 × 2 = 32 bytes and a group of eight needs 256 × 2 = 512 bytes. Doubling group length multiplies this table size by sixteen, not two. Symmetry or another representation can change the count, but must be included explicitly.',
                'Now use invented timing units: a direct calculation costs 4 per output, constructing the table costs 12 once, and each subsequent lookup path costs 1 including the work counted in this simplified comparison. For n outputs sharing the inputs, the costs are 4n and 12 + n. Four outputs tie at 16; five favor the table at 17 versus 20. If inputs change every output, construction recurs and the table path costs 13 each. “Replace arithmetic with lookup” has not removed preparation.',
                'Real table access also has a service capacity. Several lanes looking up different entries can contend for storage ports, just as in the banked-memory walkthrough. Keeping a larger table close may consume space needed by other values. A faster lookup in isolation therefore needs a surrounding schedule, storage budget, and account of which transfers disappear or remain.',
            ],
            'sources': [('#paper-banked-memories-2025', 'Compare: table accesses still need memory service')],
        },
        {
            'title': 'An exact rearrangement and an approximation need different checks',
            'paragraphs': [
                'The small integer derivations above preserve the result exactly. Storing rounded table entries is a separate change. In an invented sum of eight selected entries, if each stored entry has a justified absolute error of at most 0.01 and accumulation is exact, the final absolute error is at most 0.08. Errors can align in sign. That bound does not guarantee an unchanged decision when the true result lies within 0.08 of a threshold.',
                'Additional rounding during accumulation, weights applied to table outputs, clipping, or a nonlinear consumer require a new error account. Do not treat an algebraically valid replacement as proof that every limited-precision implementation meets the application’s quality target. Compare accepted outputs as well as operation counts.',
            ],
        },
        {
            'title': 'Keep each evaluation attached to its evidence stage',
            'paragraphs': [
                'Section 4.1 uses three kinds of model evidence. It synthesizes hardware descriptions written in Verilog against a TSMC 28 nm library and a 1-GHz target to estimate circuit area, timing, and power. It uses Accel-Sim, a GPU simulator configured like an A100, for individual GPU-program-routine (kernel) comparisons. It uses a separate tile-based simulator for model-level evaluation because simulating every low-level event is too slow. These methods establish different modeled results; they are not measurements of a manufactured LUT-equipped A100.',
                'A synthesis target is a constraint supplied to a tool, not automatically a demonstrated operating rate. A simulator can compare architectural alternatives under its assumptions, but its predictions need an accuracy argument and a stated workload. When comparing this paper with an ISSCC chip measurement, preserve that distinction rather than merging their numbers into one hardware ranking.',
            ],
            'sources': [(PDF + '#page=7', 'Author manuscript, section 4.1 — synthesis and simulation methodology'), ('#route-isscc-2025', 'Compare: task energy and chip measurement scope')],
        },
    ],
    'exercise': {
        'question': 'For input values 2 and 7, build the four-entry binary table. Use it to calculate the dot product with two-bit weights 3 and 2. If building this table costs 15 time units, each lookup path costs 2, and the direct alternative costs 5 per output, how many same-input outputs are needed for a strict timing win?',
        'answer': 'The table is (0,0) → 0, (0,1) → 7, (1,0) → 2, (1,1) → 9. Weight low bits (1,0) select 2; high bits (1,1) select 9. Their combination is 2 + 2 × 9 = 20, equal to 2 × 3 + 7 × 2. For the independent timing model, require 15 + 2n < 5n, so n > 5: five tie and six first win. This assumes the stated lookup-path cost includes all work needed per output and that the inputs stay unchanged.',
    },
}
