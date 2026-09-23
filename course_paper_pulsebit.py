"""Focused VLSID walkthrough of representation-sensitive control-memory faults."""

PAPER = 'https://arxiv.org/html/2405.05511v1'

PULSE_BIT = {
    'id': 'pulse-bit-2025',
    'route': 'vlsid-2025',
    'title': 'Pulse-bit errors: count what a changed control bit does',
    'identity': 'Investigating Impact of Bit-flip Errors in Control Electronics on Quantum Computation · VLSID 2025',
    'scope': 'A focused walkthrough of bit representation, pulse-control data, sensitivity, Total Variation Distance, and the reported simulator evaluation. The locally extracted manuscript was inspected, especially sections 3.2 and 4.1. Results are author-reported and have not been independently reproduced here. The bit-value and probability calculations are original teaching models.',
    'lessons': [('s2', 'Numerical error'), ('s8', 'Fault models'), ('physical-design', 'Physical conditions'), ('s10', 'Whole-system cost')],
    'blocks': [
        {
            'title': 'One changed bit can mean a small or enormous changed value',
            'paragraphs': [
                'A quantum processor is controlled by ordinary electronics that store pulse descriptions. A pulse has properties such as amplitude, phase, and duration; the stored numbers tell the electronics what signal to produce. A bit flip in that memory changes the encoded number. The effect depends on which bit changed and on how the next operation uses the value.',
                'Floating-point storage separates a number into a sign, an exponent, and a fraction. Changing an exponent bit can multiply or divide the represented magnitude by a large factor, while changing a low-order fraction bit may only make a small numerical adjustment. Therefore “one bit flipped” is not a complete fault description. We need the representation, bit position, original value, and downstream operation.',
                'Original four-bit model: use unsigned binary 0011 for 3. Flipping the last bit gives 0010, or 2, a value error of 1. Flipping the first bit gives 1011, or 11, an error of 8. Both are one-bit faults. A fault counter that reports only “one bit” hides the difference in the value delivered to the control logic.',
            ],
            'sources': [(PAPER, 'Manuscript sections 2–3: FPGA control memory, pulse amplitude/phase data, and floating-point representation')],
        },
        {
            'title': 'Measure the changed answer, not only the changed number',
            'paragraphs': [
                'A changed pulse value matters only through the quantum operation it produces. The paper compares the probability distribution from an unmodified pulse sequence with the distribution after a bit flip. Total Variation Distance, or TVD, measures how far two probability distributions are apart: add the absolute difference for each outcome and divide by two. A larger TVD means the observed output distribution changed more, but it is still a result under the simulator and circuit used.',
                'The position of a bit can therefore be ranked by its effect on the final distribution rather than by its numerical distance alone. A small amplitude change may matter little for one gate and more for another. Conversely, a large change in a control quantity may have limited effect in a circuit that is insensitive to that quantity. Fault sensitivity belongs to the chain from stored representation to required output.',
                'Original distribution model: an ideal gate produces outcomes [0.8, 0.2], while a faulted pulse produces [0.6, 0.4]. TVD is (|0.8−0.6| + |0.2−0.4|)/2 = 0.2. If the faulted distribution is [0.79, 0.21], TVD is 0.01. The same one-bit fault count could correspond to very different output changes; the metric must be computed at the output boundary.',
            ],
            'sources': [(PAPER, 'Manuscript sections 3.2 and 4.1: TVD definition, bit-sensitivity experiments, and simulated gate outputs')],
        },
        {
            'title': 'Large sensitivity is not the same as likely failure',
            'paragraphs': [
                'The study reports that flips in exponent and early mantissa bits of the real amplitude can produce TVD increases approaching 200% in its tested simulations, while other bit positions have much smaller effects. It also reports that fixed-point representation is less sensitive in the tested comparison. These findings identify a representation-level sensitivity pattern; they do not tell us how often a physical memory cell flips or whether a real controller detects and stops an invalid pulse.',
                'The local source review records two evidence limits. Some tested bit positions produced invalid pulses, and neighboring graph values were filled by interpolation rather than by valid simulation results. The study also assumes detection and stopping for those invalid pulses. A plotted line through neighboring points is therefore not a measurement of the invalid point, and a safeguard assumption is not a demonstrated safeguard.',
                'A risk estimate needs two separate quantities: the consequence if a bit flips and the probability that this bit flips under the operating conditions. If a high-impact bit has probability 0.0001 per pulse and a low-impact bit has probability 0.01, the low-impact fault may dominate the expected count even though its consequence is smaller. Multiplying sensitivity and occurrence requires an occurrence model; the simulator study supplies the first kind of evidence, not the second.',
            ],
            'sources': [(PAPER, 'Manuscript sections 3.2 and 4.1: reported sensitivity, invalid-pulse interpolation, and assumed stopping behavior')],
        },
        {
            'title': 'A protection claim must include detection and what happens next',
            'paragraphs': [
                'If the system is expected to detect an invalid pulse before transmission, that detector is part of the control path. It needs a defined input condition, a response time, and a recovery action: stop, replace the value, retry the gate, or report an incomplete computation. Measuring the pulse’s effect without testing this response leaves the safety story unfinished.',
                'The paper’s simulator evidence can support a bounded question: under its representation, gates, backends, and fault injections, which bit positions most disturb the simulated output? It cannot establish a physical fault rate, manufactured-memory behavior, or the reliability of an assumed detector. Fixed-point’s tested sensitivity advantage also has costs such as range and precision choices; changing the representation changes the value semantics that the control path must preserve.',
                'A fair follow-up would inject the same faults into a complete control pipeline, test valid and invalid pulse handling, record whether a pulse was transmitted, and measure the final accepted computation. It should report simulation, FPGA-memory test, and physical quantum-device evidence separately. The output distribution, interruption rate, retry cost, and missed-deadline cost are different results.',
            ],
            'sources': [(PAPER, 'Manuscript evaluation and conclusion: representation comparison and scope of the simulator study')],
        },
    ],
    'exercise': {
        'question': 'An ideal two-outcome distribution is [0.75, 0.25]. A changed pulse produces [0.55, 0.45]. What is the TVD in this teaching model? Does that number tell you how often the memory fault occurs or whether the controller detects it?',
        'answer': 'TVD is (|0.75−0.55| + |0.25−0.45|)/2 = 0.20. It measures the output-distribution change for this fault and setup. It does not give the fault’s occurrence probability, prove behavior on physical hardware, or show that a detector stops the invalid pulse. Those require separate evidence. This is an original teaching calculation, not a pulse-bit paper measurement.',
    },
}
