"""VLSID teaching walkthrough; the inspected preprint has unresolved energy figures."""
PAPER = 'https://arxiv.org/html/2409.00495v1'

TIMEFLOATS = {
    'id': 'timefloats-2025',
    'route': 'vlsid-2025',
    'title': 'TimeFloats: follow a number through time, charge, and stored state',
    'identity': 'Maeesha Binte Hashem and colleagues · TimeFloats · VLSID 2025',
    'scope': 'Focused reading of the August 2024 preprint, sections III–IV; not a verified comparison with the final conference text. Examples are original. No hardware or training experiment was reproduced.',
    'lessons': [('s2', 'Numerical representations'), ('s3', 'Storage and movement'), ('physical-design', 'Physical error and evidence'), ('training-workflow', 'Training requirements')],
    'blocks': [
        {
            'title': 'A floating-point sum needs a common scale',
            'paragraphs': [
                'Floating-point notation writes a number as meaningful digits times a power of two. The digits are called the significand, also known as the mantissa; the power is called the exponent and says how large or small those digits are. In a positive-valued teaching example, 3 = 1.5×2¹ and 2 = 1×2¹. Their product is 1.5×2² = 6. Meanwhile, 0.25×4 = (1×2⁻²)(1×2²) = 1×2⁰ = 1. Adding the two products requires respecting their different scales.',
                'Choose exponent two as the common scale. Then the sum becomes (1.5 + 0.25)×2² = 7. Adding the unadjusted digits as 1.5 + 1 would treat values at different scales as though they meant the same thing. Aligning scales is real work, even if the physical mechanism makes each individual multiplication inexpensive.',
                'TimeFloats combines stored digits and exponents with time-based exponent addition, scale alignment, charge accumulation, and conversion of the result back into digital bits. Its shared analog-to-digital converter (ADC) performs that last conversion. Calling this path conversion-free would omit an explicit circuit stage.',
            ],
            'sources': [(PAPER + '#S3', 'Preprint, section III'), ('https://doi.org/10.1109/VLSID64188.2025.00101', 'Conference publication DOI')],
        },
        {
            'title': 'Alignment can make a small contribution disappear',
            'paragraphs': [
                'Keep the original sum, but invent a deliberately coarse aligned representation: each nonnegative significand must be a multiple of 0.5, and conversion truncates downward. The aligned 1.5 survives exactly; 0.25 becomes zero. The computed answer is now 1.5×4 = 6 instead of 7. The error came from alignment followed by limited precision, not from an incorrect multiplication. This is not TimeFloats’ particular encoding or rounding rule.',
                'A small discarded term is not always harmless. Consider one contribution of six and sixteen contributions of one, all aligned to exponent two under the same toy rule. Each small term becomes 0.25 at that scale and is discarded. The exact sum is twenty-two, while the truncated sum is six. Bounding each dropped contribution separately is insufficient unless their combined effect is also within the application’s tolerance.',
                'Exponent errors and significand errors also have different consequences. With value 1.5×2² = 6, mistakenly increasing the exponent by one produces twelve. Adding 0.0625 to the significand instead produces 6.25. The first change doubles the value; the second changes it by about 4.17%. These examples do not establish how often either physical error occurs. They explain why an error model must identify which represented quantity is disturbed.',
            ],
        },
        {
            'title': 'A timing code needs enough separation to be distinguishable',
            'paragraphs': [
                'Use an invented timing code t = 1 ns + c×0.25 ns, where c is an integer from zero to fifteen. Codes four and five ideally produce 2 ns and 2.25 ns. Suppose total timing error relative to the decoder’s reference is bounded by 0.1 ns. The possible arrival intervals are 1.9–2.1 ns and 2.15–2.35 ns: they do not overlap. A threshold between them can distinguish these two codes under the stated bound.',
                'If the timing error bound grows to 0.15 ns, the intervals become 1.85–2.15 ns and 2.10–2.40 ns. Their overlap means some observed times are consistent with either input. A decoder cannot guarantee the correct choice from timing alone in that overlap. For adjacent spacing d and symmetric error bound j, non-overlapping intervals require d > 2j. This is a deterministic toy bound, not a distribution or a measured circuit tolerance.',
                'Increasing spacing to 0.4 ns separates codes under j = 0.15 ns, but the latest code now arrives at 1 + 15×0.4 = 7 ns instead of 4.75 ns. Greater separation can cost time. Calibration can remove a known systematic shift, but its measurement, storage, and refresh cost remain, and residual timing error still needs a bound. Temperature changes or different cells may invalidate an old calibration.',
            ],
        },
        {
            'title': 'A product engine is only part of a training step',
            'paragraphs': [
                'Training changes stored parameters using information about how the current result should improve. In an invented update, weight w = 1, learning rate 0.1, and gradient 0.03 give a requested weight of 0.997. Suppose storage near one can represent only multiples of 0.01 and rounds to nearest. Storing each update immediately rounds back to one. If the same gradient repeats ten times and every update starts from the rounded stored value, all ten updates disappear.',
                'If a more precise accumulator instead retains the ten increments, their combined change is 0.03 and the final weight is 0.97, which fits that storage grid. This is a different update strategy with extra state and a different schedule. In a real training process, gradients can change after each update, so postponing writes needs a learning argument as well as an arithmetic one. The example assumes a fixed gradient solely to isolate rounding.',
                'For a complete implementation, follow the input through the forward calculation, error calculation, gradient calculation, parameter update, and stored state used by the next step. Account for activation storage, conversion, update precision, programming costs, and any optimizer state. Locating multiplication beside weights does not by itself establish that all these stages fit or that learning reaches the required quality.',
            ],
        },
        {
            'title': 'Keep the evidence and unresolved numbers visible',
            'paragraphs': [
                'The preprint uses two kinds of design-model evidence, not fabricated-chip measurements. Digital synthesis estimates a logic implementation from a hardware description and timing constraints; HSPICE is a detailed circuit simulator for the analog blocks. Both use predictive 15 nm technology models. Its Table I lists digitization at 21 fJ and crossbar work at 1.23 pJ; section IV-B instead gives 2.421 pJ and 1.32 pJ. The listed table components sum to 5.804 pJ, while the prose components sum to 8.294 pJ. The stated total is 5.8 pJ. These discrepancies remain unresolved here.',
                'Do not silently select whichever component number makes a headline ratio work. First confirm the intended circuit, operation count, units, and included peripherals. A verified energy total would still need to be connected to the number of accepted training steps or outputs before supporting an application-level energy claim.',
                'The paper therefore serves two teaching purposes: following a representation through physical stages, and recognizing where the available evidence stops. A circuit model can explain a mechanism and guide a design. Establishing manufactured-device behavior, a complete training implementation, and task-level quality requires additional evidence. The course has not supplied those experiments.',
            ],
            'sources': [(PAPER + '#S4', 'Preprint, section IV'), ('https://arxiv.org/pdf/2409.00495v1#page=5', 'Preprint PDF, Table I on page 5; energy prose on page 6')],
        },
    ],
    'exercise': {
        'question': 'In the timing model, keep a 1 ns base and codes zero through fifteen. Total timing error is bounded by 0.12 ns, and the last ideal pulse must arrive by 5 ns. What spacings satisfy both requirements? If the bound rises to 0.14 ns, can changing spacing alone satisfy them?',
        'answer': 'Distinguishability needs d > 0.24 ns. The ideal latest-pulse limit needs 1 + 15d ≤ 5, or d ≤ 4/15 ns, about 0.2667 ns. Thus 0.24 < d ≤ 0.2667 works, including 0.25. At error bound 0.14, distinguishability needs d > 0.28, incompatible with d ≤ 0.2667. The design must change another requirement or reduce the error bound. If the deadline applies to actual rather than ideal arrival, include the positive timing error too: the upper bound becomes (4−j)/15. None of these intervals establishes a real TimeFloats timing margin.',
    },
}
