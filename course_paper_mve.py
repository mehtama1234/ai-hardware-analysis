"""Focused HPCA walkthrough of expressing multidimensional work to an in-cache engine."""

PDF = 'https://arxiv.org/pdf/2501.09902'

MVE = {
    'id': 'mve-2025',
    'route': 'hpca-2025',
    'title': 'MVE: describe the data shape the machine must actually load',
    'identity': 'Alireza Khadem, Daichi Fujiki, Hilbert Chen, Yufeng Gu, Nishil Talati, Scott Mahlke, Reetuparna Das · Multi-Dimensional Vector ISA Extension for Mobile In-Cache Computing · HPCA 2025',
    'scope': 'A focused walkthrough of in-cache vector execution, multidimensional logical registers, strided and random access, dimension-level masking, cache-mode transitions, and reported evaluation. The arXiv version and the authors’ artifact were inspected. Results are author-reported and have not been reproduced here. The lane-utilization, transition, and break-even calculations are original teaching models.',
    'lessons': [('s1', 'Whole-request timing'), ('s3', 'Memory'), ('s4', 'Movement boundaries'), ('s6', 'Compilation'), ('s10', 'Whole-system cost')],
    'blocks': [
        {
            'title': 'A wide vector unit is useless when the program cannot fill it',
            'paragraphs': [
                'In-cache computing turns part of a cache into a very wide calculation engine. MVE’s target has thousands of bit-line lanes, but many mobile kernels do not have thousands of independent values along one straight row. They use nested loops: rows, columns, channels, blocks, or repeated copies. A one-dimensional vector instruction sees only one of those dimensions and leaves the rest of the hardware idle.',
                'MVE treats a physical long vector as a multidimensional logical register. A program describes dimension lengths and strides; the controller maps that shape onto the cache’s physical lanes. A stride of one can walk adjacent values, a stride of zero can replicate a value across a dimension, and other dimensions can use configured strides. The programmer sees a vector operation over a data shape instead of cache-bank and bit-line coordinates.',
                'Original utilization example: hardware has 8 lanes, but a one-dimensional row has only 2 independent values. One row uses 2/8, or 25%, of the lanes. If four independent rows can be named as a 2×4 logical shape, all 8 lanes can work. This assumes the rows are independent and the load pattern can express them; it is not a claim about a particular MVE kernel’s measured utilization.',
            ],
            'sources': [(PDF + '#page=1', 'MVE paper, abstract and introduction: mobile in-cache computing and multidimensional parallelism'), (PDF + '#page=5', 'MVE paper, physical-register abstraction and logical dimensions')],
        },
        {
            'title': 'The instruction should describe regular and irregular movement together',
            'paragraphs': [
                'Many kernels do more than read a contiguous row. A matrix transpose reads columns and writes rows. An image upsample operation may load different row bases, then replicate each value horizontally and vertically. MVE provides multidimensional strided loads and random-base loads so one instruction can express these patterns. It also provides dimension-level masks for turning off an outer group of lanes without building a full mask vector in scalar code.',
                'This is an abstraction boundary. Older in-cache extensions may expose cache geometry directly, forcing software to know banks, sets, ways, word lines, and bit lines. MVE hides those details behind long-vector registers, but the compiler still has to configure dimensions, allocate registers, schedule instructions, and avoid spills. A shorter program text does not prove lower execution time if configuration or register pressure becomes the new bottleneck.',
                'Original instruction-count example: a two-dimensional transpose has 4 column groups. A shape-aware instruction handles one group per loop, requiring 4 loads and 4 stores. A one-dimensional fallback handles each of 8 rows separately and needs 8 loads and 8 stores, plus 4 mask/setup operations: 20 actions instead of 8. If each MVE action costs 3 units and setup costs 12, MVE costs 24; if its cache transition costs 30 for a one-off job, the total becomes 54 and the fallback wins at 40. Reuse can change the choice.',
            ],
            'sources': [(PDF + '#page=6', 'MVE paper, multidimensional strided and random access instructions'), (PDF + '#page=8', 'MVE paper, dimension-level masked execution'), (PDF + '#page=10', 'MVE paper, programming model, register allocation, and scheduling')],
        },
        {
            'title': 'Switching the cache into compute mode has a correctness cost',
            'paragraphs': [
                'The same cache must remain available for ordinary CPU work. MVE preserves part of the cache’s storage role and uses compute-capable ways only when a long-vector kernel needs them. Before switching from normal cache use to in-cache calculation, dirty cache lines—cache copies newer than backing memory—must be written back or otherwise preserved. Otherwise the calculation mode could overwrite the newest ordinary program data.',
                'Switching back to normal cache use is cheaper in the paper’s design because it changes a control register, but that asymmetry does not make transitions free. A workload with short alternating kernels can spend more time entering and leaving modes than calculating. The compiler or runtime needs a policy for grouping compatible work, and that grouping can affect response time for unrelated tasks.',
                'Original break-even example: entering compute mode costs 6 ms and leaving costs 1 ms. The in-cache path saves 4 ms per compatible job compared with the ordinary path. One job loses by 3 ms; after two jobs, the 8 ms of savings has paid back the 7 ms transition cost and leaves 1 ms saved; three jobs save 5 ms. If a dirty-line flush adds 2 ms when switching in, the first positive saving moves to three jobs. These are teaching numbers, not MVE transition measurements.',
            ],
            'sources': [(PDF + '#page=14', 'MVE paper, cache coherence and normal-cache/compute-cache switching'), ('https://github.com/arkhadem/MVE', 'MVE artifact README: Snapdragon 855 target, phone measurement and trace-driven simulation workflows')],
        },
        {
            'title': 'Separate real measurements from modeled cache and silicon results',
            'paragraphs': [
                'MVE evaluates 44 data-parallel kernels from 12 mobile libraries using a Snapdragon 855-like configuration, Arm Neon and Adreno baselines, trace-driven cycle simulation, Ramulator memory modeling, CACTI, and RTL (register-transfer-level) synthesis with scaled area and energy estimates. The artifact also documents a Samsung Galaxy S10e measurement path for the Arm and Adreno baselines and the tools needed to run the simulations. These are different evidence paths, not one physical MVE chip.',
                'The paper reports an average 2.9× performance improvement and 8.8× energy reduction over the packed-SIMD Neon model, with 3.6% area overhead in its modeled design. It also reports a 9.3× performance and 5.2× energy comparison against the Adreno GPU under its stated transfer and launch-overhead setup. The result depends on the selected mobile kernels, cache configuration, bit-serial in-SRAM assumptions, compiler, and baseline treatment.',
                'The course should therefore ask which quantity was measured, simulated, synthesized, or scaled; whether switching and data transfer are included; and whether the kernel has enough multidimensional work to fill the engine. A result for one 1D reduction may not predict a result for a 3D image kernel. This walkthrough has not run the artifact or reproduced MVE’s evaluation.',
            ],
            'sources': [(PDF + '#page=1', 'MVE paper, abstract: reported average performance, energy, and area claims'), (PDF + '#page=16', 'MVE paper, benchmark setup, simulator, power, area, and comparison methodology'), ('https://github.com/arkhadem/MVE', 'MVE artifact README: physical target, benchmark and simulation boundaries')],
        },
    ],
    'exercise': {
        'question': 'A compatible job saves 4 ms per job with MVE, but entering compute mode costs 6 ms and leaving costs 1 ms. How many jobs are needed to break even? If a dirty-line flush adds 2 ms to entry, how many jobs are needed to obtain a positive saving?',
        'answer': 'Without the flush, the transition costs 7 ms, so two jobs save 8 ms and break even with 7 ms; three jobs save 12 − 7 = 5 ms. With the additional 2 ms flush, the transition costs 9 ms; three jobs save 12 − 9 = 3 ms. These original teaching numbers show why cache transitions belong in the whole-job cost, not only in steady-state vector throughput. They are not MVE measurements.',
    },
}
