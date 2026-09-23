"""Focused DATE walkthrough of parallel SAT sampling and its evidence boundary."""

PAPER = 'https://arxiv.org/abs/2502.08673'
CODE = 'https://github.com/arashardakani/High-Throughput-SAT-Sampler'

SAT_SAMPLING = {
    'id': 'sat-sampling-2025',
    'route': 'date-2025',
    'title': 'High-Throughput SAT Sampling: make many valid candidates at once',
    'identity': 'Arash Ardakani and colleagues · High-Throughput SAT Sampling · DATE 2025',
    'scope': 'A focused walkthrough of satisfying assignments, probabilistic circuit evaluation, GPU batches, unique-solution throughput, and the paper’s source-backed evaluation. The locally extracted arXiv manuscript was inspected, including its definitions, method, and evaluation. Results are author-reported and have not been independently reproduced here. The sampling and probability calculations are original teaching models.',
    'lessons': [('s2', 'Numerical error'), ('dependencies-and-pipelines', 'Dependencies'), ('s6', 'Compilation'), ('s7', 'Parallel hardware')],
    'blocks': [
        {
            'title': 'A satisfying assignment is an accepted answer, not necessarily a new one',
            'paragraphs': [
                'A Boolean formula is a rule built from variables that are either true or false. A satisfying assignment is one choice of those variables that makes the complete formula true. SAT sampling asks for many such choices, not only one. That creates two separate obligations: every returned choice must be valid, and the collection should contain useful variety. Returning the same valid choice repeatedly has high validity and poor diversity.',
                'The paper rewrites a SAT problem as a multi-level Boolean circuit and replaces hard true/false values with probabilities during optimization. The continuous representation lets many candidate assignments be processed as a batch on GPU arithmetic. After optimization, the candidates are converted back to Boolean assignments and checked against the original formula. The GPU makes candidate generation parallel; it does not remove the need for a validity check.',
                'Original four-variable model: the formula is (A OR B) AND (C OR D). Assignment 1001 means A=true, B=false, C=false, D=true and satisfies the formula. Assignment 0000 fails both clauses. If a batch returns [1001, 1001, 1010, 0110], all four may be valid, but only three are distinct. Count validity and distinctness separately before calling the batch diverse.',
            ],
            'sources': [(PAPER, 'Primary manuscript, sections defining SAT sampling and the probabilistic circuit formulation'), (CODE, 'Authors’ implementation repository')],
        },
        {
            'title': 'Probabilities allow GPU arithmetic, but they change the question being optimized',
            'paragraphs': [
                'A hard Boolean OR returns true when at least one input is true. During optimization, the method uses differentiable probability representations so small changes to a candidate can produce a usable direction for improvement. The continuous value is not itself a final satisfying assignment. It is a search state that must eventually be rounded or sampled and then checked in the original discrete formula.',
                'This separation prevents a common mistake: a high circuit output probability is not proof that the rounded assignment satisfies every clause. A candidate with a predicted output of 0.99 can still round badly if intermediate probabilities are correlated or the approximation does not preserve the exact Boolean behavior. The acceptance test remains the original formula.',
                'Original probability model: suppose two independent inputs have true probabilities 0.8 and 0.3. A simple teaching approximation for OR is 1 − (1−0.8)(1−0.3) = 0.86. If the inputs are not independent, that number need not be correct. Even when 0.86 is a useful search signal, it is not a guarantee that one sampled Boolean assignment passes. Check the assignment directly.',
            ],
            'sources': [(PAPER, 'Primary manuscript, probabilistic operator table and optimization formulation')],
        },
        {
            'title': 'Batching changes throughput, not the definition of a good sample',
            'paragraphs': [
                'The method generates many candidates together and uses GPU operations to update the batch. This can reduce the time per candidate when the batch is large enough to fill the GPU. But a larger batch also creates more duplicates, more memory traffic, and more candidate-checking work. The useful batch size is therefore an end-to-end choice, not simply the largest number that fits.',
                'The paper defines throughput as the number of unique valid solutions generated per second. That denominator matters. Counting all generated candidates would reward duplicates and invalid assignments. A run can have high raw generation rate but low unique-valid throughput if most candidates repeat or fail the formula. The paper compares its method with UNIGEN3, CMSGEN, and DIFFSAMPLER under its stated instance and timeout setup.',
                'Original batch model: a 100-candidate batch takes 10 ms to generate and 2 ms to check, returning 60 unique valid assignments. Its measured teaching throughput is 60/0.012 = 5,000 unique valid assignments per second. A 200-candidate batch takes 14 ms to generate and 6 ms to check, returning 80 unique valid assignments: 4,000 per second. More candidates per batch did not improve the accepted-answer rate enough to offset checking cost.',
            ],
            'sources': [(PAPER, 'Primary manuscript, evaluation definition and tables: unique valid solutions per second, GPU setup, baselines, and timeout')],
        },
        {
            'title': 'Throughput is not a uniformity guarantee',
            'paragraphs': [
                'Different valid assignments may not be selected with equal probability. A sampler can produce many distinct answers while repeatedly favoring easy-to-reach regions of the solution space. If an application needs approximate uniformity, coverage of rare solutions, or a stated probability bound, those are additional tests. A distinct-answer count cannot establish them.',
                'The paper reports unique-solution throughput speedups ranging from 33.6× to 523.6× over the compared samplers on its evaluated SAT instances, using the stated GPU and timeout procedure. These are paper measurements for the tested instances, batch choices, baselines, and implementation. They do not by themselves establish equal selection probability or the same result for every SAT family.',
                'Original selection model: suppose a sampler chooses common answer A with probability 0.99 and rare answer B with 0.01 on each independent draw. The probability of missing B in 100 draws is 0.99^100 ≈ 36.6%. A run can therefore return many valid and distinct common answers while still missing a rare answer. To claim coverage, measure the property directly and state how the reference distribution is known.',
            ],
            'sources': [(PAPER, 'Primary manuscript, evaluation and related-work boundary: unique-valid throughput versus sampling-distribution guarantees')],
        },
    ],
    'exercise': {
        'question': 'A sampler generates 500 candidates in 20 ms, checks them in 5 ms, and returns 150 unique valid assignments. What is its unique-valid throughput? If another sampler returns 180 unique valid assignments in 40 ms, which is faster by this measure? What property is still not established?',
        'answer': 'The first sampler produces 150/0.025 = 6,000 unique valid assignments per second. The second produces 180/0.040 = 4,500 per second, so the first is faster by this measure. Neither result establishes uniform selection, rare-solution coverage, equal probability, or the same validity behavior on another SAT family. These are original teaching calculations, not measurements from the paper.',
    },
}
