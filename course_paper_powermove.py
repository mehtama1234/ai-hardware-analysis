"""Focused ASPLOS walkthrough of movement-aware quantum compilation."""

PDF = 'https://arxiv.org/abs/2411.12263'

POWERMOVE = {
    'id': 'powermove-2025',
    'route': 'asplos-2025',
    'title': 'PowerMove: plan gates and qubit movement as one program',
    'identity': 'Jixuan Ruan and colleagues · PowerMove: Optimizing Compilation for Neutral Atom Quantum Computers with Zoned Architecture · ASPLOS 2025',
    'scope': 'A focused walkthrough of neutral-atom gate scheduling, qubit placement, movement, storage/computation zones, fidelity, and the reported compiler evaluation. The local primary text was inspected. Results are author-reported and have not been independently reproduced here. The movement and fidelity calculations are original teaching models.',
    'lessons': [('s5', 'Representation'), ('s6', 'Compilation'), ('s7', 'Movement and locality'), ('s10', 'Whole-system cost')],
    'blocks': [
        {
            'title': 'When data can move, placement becomes part of the program',
            'paragraphs': [
                'Neutral-atom quantum computers can move qubits and use different zones for storage and computation. A two-qubit gate is possible only when the qubits are placed close enough and the hardware rules allow the operation. The compiler therefore chooses more than an order for gates: it chooses where qubits sit, when they move, and when they cross between zones.',
                'A compiler that schedules gates first and inserts movement afterward can make a locally sensible gate order globally expensive. It may move the same qubit repeatedly, pull quiet qubits into a noisy computation zone, or send all qubits back to an initial layout after every block. PowerMove treats movement and zone choice as part of the scheduling decision from the beginning.',
                'Original movement model: three gates need pairs (A,B), (B,C), and (A,C). A fixed layout can execute the first pair cheaply but requires moving C twice for the next two gates, costing 4 movement units. A reordered layout may execute (A,B) and (A,C) together after one placement change costing 2 units, then finish (B,C) with 1 more, for 3 units. The cheaper order is valid only if the gates commute and the placement satisfies the hardware constraints.',
            ],
            'sources': [(PDF, 'PowerMove paper, abstract and introduction: four coupled compilation decisions and zoned neutral-atom hardware')],
        },
        {
            'title': 'Schedule stages, then choose movement that serves the next stage',
            'paragraphs': [
                'PowerMove groups compatible two-qubit gates into stages whose gates act on disjoint qubits and can run in parallel. It then orders stages to reduce interchange between the computation and storage zones. Non-interacting qubits can remain in storage longer, where they avoid unnecessary exposure to the computation laser and preserve coherence, while qubits needed for the next interaction move in deliberately. The movement hardware uses acousto-optic deflectors (AODs), optical devices that steer the laser or trap locations; the number of AOD arrays limits how many movements can proceed together.',
                'Movement itself is constrained. Multiple atom movements can conflict, movement time depends on the longest move in a group, and different AOD arrays can provide additional parallelism. PowerMove’s collective-move scheduler groups compatible movements and balances their distances. The compiler is optimizing a sequence of states and transitions, not just the distance between two static layouts.',
                'Original stage model: stage 1 needs gates (A,B) and (C,D), while stage 2 needs (A,C). Stage 1 can run both gates together. If all four qubits return to a fixed starting layout before stage 2, the transition costs 8 units. If the compiler leaves A and C positioned for the next interaction and moves only B and D as needed, the transition costs 3 units. The saving is real only if the remaining positions do not create unwanted interactions or violate spacing rules.',
            ],
            'sources': [(PDF, 'PowerMove paper, sections 4–6: stage scheduler, continuous router, storage-zone use, and collective-move scheduler')],
        },
        {
            'title': 'Fidelity is a time-and-exposure calculation, not just gate accuracy',
            'paragraphs': [
                'The final quantum result depends on several failure sources: one- and two-qubit gate fidelity, excitation errors from being in the computation zone, movement errors, and decoherence while a qubit idles or transfers. Moving a qubit can reduce one risk while adding another. Keeping a qubit in storage can protect it from excitation but may require a later transfer before its gate.',
                'This is why PowerMove’s compiler objective includes both execution time and fidelity. A shorter schedule that leaves many non-interacting qubits under the computation laser may lose more fidelity. A movement plan that minimizes distance but serializes all collective moves may increase exposure time. The compiler must use the hardware error model rather than calling every movement a cost in the same units.',
                'Original fidelity model: assume three independent operations have fidelities 0.99, 0.98, and 0.995. The combined fidelity is 0.99×0.98×0.995 ≈ 0.965. If a movement removes one 0.98 operation but adds a movement fidelity of 0.999, the product becomes 0.99×0.995×0.999 ≈ 0.984. This is a teaching calculation, not PowerMove’s full fidelity model; real errors may not be independent.',
            ],
            'sources': [(PDF, 'PowerMove paper, section 2: gate, movement, excitation, idle, and fidelity model')],
        },
        {
            'title': 'Keep compilation time, circuit time, and fidelity separate',
            'paragraphs': [
                'The paper reports execution-time improvement factors of 1.71×–3.46× over Enola across its evaluated circuits and compilation-time reductions from 1.89× to 213.55× in its reported table. It also reports fidelity improvements of several orders of magnitude under the stated neutral-atom hardware model. These are different outputs: a faster compiler does not necessarily produce a faster circuit, and a shorter circuit does not automatically have higher fidelity.',
                'The evaluation covers QAOA, QFT, BV, VQE, and QSIM circuits, with non-storage and storage-zone cases under the paper’s device and movement assumptions. Results depend on the gate set, zone spacing, movement constraints, number of AOD arrays, fidelity model, and baselines. This walkthrough has not run PowerMove or reproduced its compiler evaluation.',
                'A fair follow-up should report the same circuit, legal movement schedule, circuit execution time, compilation time, fidelity model, and whether storage-zone protection is counted. It should also state whether an improvement is an absolute value or a ratio and which baseline supplies its denominator.',
            ],
            'sources': [(PDF, 'PowerMove paper, evaluation: circuit workloads, Enola comparison, execution/compilation time, fidelity, and hardware boundary')],
        },
    ],
    'exercise': {
        'question': 'A compiler choice removes one operation with fidelity 0.98 but adds a movement with fidelity 0.999. The remaining operations have fidelities 0.99 and 0.995. What are the approximate combined fidelities before and after? What other result must be checked before choosing the movement plan?',
        'answer': 'Before, the product is 0.99×0.98×0.995 ≈ 0.965. After, it is 0.99×0.995×0.999 ≈ 0.984, so the teaching model improves fidelity. The compiler must also check movement legality, execution time, idle exposure, zone capacity, and compilation cost. These are original teaching calculations, not PowerMove measurements.',
    },
}
