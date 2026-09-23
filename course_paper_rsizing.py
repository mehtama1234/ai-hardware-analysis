"""ICCAD paper walkthrough; original examples are not circuit experiments."""

PAPER = 'https://www.cse.cuhk.edu.hk/~byu/papers/C287-ICCAD2025-RSizing.pdf'
DOI = 'https://doi.org/10.1109/ICCAD66269.2025.11240990'

RSIZING = {
    'id': 'rsizing-2025',
    'route': 'iccad-2025',
    'title': 'RSizing: a good average does not tell you how many parts will work',
    'identity': 'Jindong Tu and colleagues · RSizing: Robust Bayesian Optimization for Analog Circuit Sizing Under Process Variations · ICCAD 2025 · DOI 10.1109/ICCAD66269.2025.11240990',
    'scope': 'Focused reading of the author-hosted paper, sections II–IV, including the limits acknowledged in refinement and the yield results in Table II. This is one paper, not a completed ICCAD survey. All numerical examples below are original teaching models unless explicitly identified as paper results. No circuit experiment was reproduced.',
    'lessons': [('physical-design', 'Physical variation'), ('s8', 'What a check establishes'), ('s6', 'Search and evaluation costs')],
    'blocks': [
        {
            'title': 'Choose a design for the parts that will actually be made',
            'paragraphs': [
                'Suppose a circuit must respond within 10 ns. Choosing its component dimensions fixes a design, but does not make every manufactured copy identical. The relevant question is therefore not just “What delay does this design have?” It is “What fraction of copies meet the limit?” That fraction is called yield. Here we mean passing the stated requirement, not every possible manufacturing test.',
                'Use an invented population with two equally likely manufacturing conditions. Design A takes 7 ns in one and 11 ns in the other: its mean delay is 9 ns, but only half its copies pass. Design B takes 9.5 ns in both conditions: its mean is slower, yet every copy passes. These values describe the entire toy population, not estimates from two simulated samples. Ranking designs by mean delay alone chooses A; requiring at least 99% to pass chooses B.',
                'The distinction also changes what “best” means. Among designs that satisfy the passing-rate requirement, one may use less current while another responds sooner. Neither wins without the application stating how to trade those quantities. Keep that choice separate from the acceptance requirement: lowering current does not excuse a failure unless the requirement itself changes.',
                'RSizing first narrows the search using results at nominal conditions—the chosen reference conditions—then models design-dependent variation from sampled simulations, and finally refines promising regions with more samples. Its surrogate model is a learned mathematical stand-in for expensive circuit simulations: it predicts which design settings are worth checking next, but it does not turn a limited simulation sample into manufactured-chip evidence. Sections III.C–D acknowledge errors from approximating distributions by bell-shaped curves and estimating joint acceptance from separate requirements.',
            ],
            'sources': [(PAPER + '#page=3', 'Paper, section III: search and refinement')],
        },
        {
            'title': 'Separate uncertainty about a design from variation between its copies',
            'paragraphs': [
                'Imagine repeatedly measuring a perfectly repeatable object with a perfect instrument. More measurements would not reveal a new distribution of objects. Now imagine measuring different manufactured copies: even perfect measurements can reveal a real spread. Learning that spread more accurately does not make it disappear. A search method needs to distinguish what it has not learned from what actually varies.',
                'For a separate teaching calculation, let two independent, zero-mean contributions to a delay prediction have standard deviations 3 ns and 1 ns. The first represents uncertainty about the predicted mean; the second represents variation between copies. Standard deviation measures spread, and independent variances add: total spread is √(3² + 1²), about 3.162 ns, not 4 ns. If more observations reduce the first contribution to 0.2 ns, total spread becomes √(0.2² + 1²), about 1.020 ns. The second contribution remains.',
                'This arithmetic assumes independence and that both contributions have been represented adequately. It does not provide a passing probability without a distribution and a threshold. Nor does it turn the observed largest delay into a worst-case limit. An unobserved tail can remain after the mean appears stable.',
                'A cheap early screen can still be valuable. In an original serial cost model, 1,000 candidates receiving 1,000 simulations each require one million simulations. Giving each candidate five early simulations and then giving 20 retained candidates 1,000 additional simulations requires 25,000: one fortieth of the original count, a 97.5% reduction. That is an evaluation-count saving, not a demonstrated equal-quality search result. The screen can discard the best design, and a large final sample cannot recover a candidate that is never reconsidered. Simulation duration, model fitting, and parallel execution would affect elapsed time too.',
            ],
        },
        {
            'title': 'Passing each requirement separately is not passing them together',
            'paragraphs': [
                'Consider an invented population of 1,000 equally likely copies. Ten fail the delay requirement. A different ten fail the current requirement. Each requirement has a 99% passing rate, but only 980 copies pass both: joint yield is 98%. If the same ten copies fail both requirements, joint yield is 99%. Separate passing rates do not reveal which situation applies.',
                'Assuming independence would give 0.99 × 0.99 = 0.9801, or 98.01%, but shared manufacturing causes may make that assumption wrong. Without assuming independence, a safe lower bound comes from counting failures: the fraction failing either requirement is at most the sum of the two failure fractions. To ensure at least 99% pass both from separate bounds alone, it is sufficient to bound each failure fraction by 0.5%. Their sum is then at most 1%. This is sufficient, not necessary; overlap between failures can make a looser allocation work.',
                'This is a general acceptance issue. A response arriving on time and a response containing a correct answer must be properties of the same response. Likewise, a chip meeting timing and a chip staying within its power limit must be the same chip under the relevant conditions. Report the joint event required by the task, not two reassuring percentages with an unstated relationship.',
            ],
        },
        {
            'title': 'Zero observed failures is not a zero failure probability',
            'paragraphs': [
                'Fix one design before testing it, and draw 1,000 independent trials from a correctly specified population. If its true passing probability is 99.9%, the probability that all trials pass is 0.999¹⁰⁰⁰, about 36.8%. Seeing no failures is quite compatible with a nonzero failure rate. It does not establish perfection.',
                'We can invert the same calculation. With n passes in n independent trials, solve pⁿ = 0.05. The resulting value p = 0.05^(1/n) is an exact one-sided 95% lower confidence bound for the passing probability in this all-pass case. At n = 1,000 it is about 99.701%, below 99.9%. “95% confidence” describes the repeated-sampling coverage of the procedure, not a 95% probability assigned to a fixed unknown value after this particular test.',
                'For the all-pass lower bound to reach 99.9%, require 0.05^(1/n) ≥ 0.999. Taking logarithms gives n ≥ log(0.05)/log(0.999), about 2,994.23, so at least 2,995 trials are needed. This is only the all-pass case under the stated assumptions. It is not a general sample-size recipe for tests with failures, correlated samples, or multiple selected winners.',
                'Search and validation should also have separate roles. Selecting a design because it looked unusually good on noisy search samples, then treating those same samples as a fresh test, can overstate the evidence. New independent validation samples for the selected design address that reuse problem, but still test the assumed simulation distribution. They do not establish that the distribution represents every manufacturing condition.',
            ],
        },
        {
            'title': 'Read the reported result at its actual boundary',
            'paragraphs': [
                'The paper evaluates three circuit benchmarks using Spectre, a circuit simulator, and a TSMC 40-nm technology model—not manufactured chips. It checks each selected solution with 1,000 sampled simulations. Table II reports, for the 99.9% target, amplifier mean yield 99.79% and minimum 99.5%. Section III.D says refinement does not remove the separate-metric approximation error; section IV.B acknowledges unmet targets.',
                'Those observations should remain visible beside the method, rather than being replaced with an unconditional promise of a guaranteed passing rate. A requested target, a model prediction, a sample estimate, and the unknown population value are four different quantities. Comparing them is part of understanding the result, not an optional qualification afterward.',
                'The runtime comparison also depends on what a search returns. In Table IV, PVTSizing has a separate runtime for each chosen target, whereas RSizing reports one runtime for producing a set of design alternatives. A reader needing one particular design and a reader exploring several tradeoffs are asking different questions. Keep that output boundary beside the simulated passing rates when comparing search time.',
                'For a follow-up comparison, hold the circuit, allowed dimensions, process distribution, acceptance conditions, and evaluation budget fixed. Record how candidates are screened, which requirements must pass together, whether validation samples were reused, and how much uncertainty remains. Then compare the quality of acceptable designs and the complete cost of finding them. This is a proposed evaluation checklist, not an experiment performed here.',
            ],
            'sources': [(PAPER + '#page=5', 'Paper, section III.D: remaining approximation error'), (PAPER + '#page=6', 'Paper, section IV: simulation and validation setup'), (PAPER + '#page=7', 'Tables II–IV: sampled yield and runtime comparison boundaries'), (DOI, 'Official ICCAD 2025 publication record: paper identity and venue')],
        },
    ],
    'exercise': {
        'question': 'Three requirements each have a true passing probability of at least 99%. With no information about their dependence, what joint passing probability can you guarantee? What equal failure allocation would suffice for a joint 99% target? Separately, does a new all-pass test of 1,000 independent trials establish a 99.9% passing probability at 95% one-sided confidence?',
        'answer': 'The combined failure probability is at most 1% + 1% + 1% = 3%, so joint passing is at least 97%. To ensure joint 99% from separate bounds alone, allocate at most 1%/3 failure probability to each requirement, meaning at least 99⅔% passing for each. Independence is not needed for this bound. The all-pass test gives a lower confidence bound of about 99.701%, so it does not reach 99.9%. Population bounds in the first question and finite-sample estimates in the last question are different kinds of information.',
    },
}
