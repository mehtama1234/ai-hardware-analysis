"""Focused HPCA walkthrough of hard constraints and deployable QAOA circuits."""

PDF = 'https://arxiv.org/pdf/2503.23941'

CHOCOQ = {
    'id': 'choco-q-2025',
    'route': 'hpca-2025',
    'title': 'Choco-Q: keep the answer legal before judging whether it is good',
    'identity': 'Debin Xiang, Qifan Jiang, Liqiang Lu, Siwei Tan, Jianwei Yin · Choco-Q: Commute Hamiltonian-based QAOA for Constrained Binary Optimization · HPCA 2025',
    'scope': 'A focused walkthrough of constrained binary optimization, commute-Hamiltonian constraint encoding, circuit serialization and decomposition, variable elimination, and reported evaluation. The arXiv version of the HPCA paper was inspected. Results are author-reported and have not been reproduced here. The candidate-count, circuit-depth, and measurement calculations are original teaching models.',
    'lessons': [('s2', 'Accepted behavior'), ('s6', 'Compilation'), ('s8', 'Correctness'), ('s10', 'Whole-system cost')],
    'blocks': [
        {
            'title': 'A solution can be legal without being the best one',
            'paragraphs': [
                'Constrained binary optimization chooses zero-or-one decisions, such as whether to open a facility or assign an item, while obeying equations or rules. There are at least three different questions: does the assignment obey every constraint, is it the best assignment, and how long did the method take to find it? Calling all three “accuracy” hides the actual failure.',
                'Choco-Q names these measurements separately. The in-constraints rate asks how often an output obeys the rules. The success rate asks how often it is the optimal answer. The approximation-ratio gap summarizes how close the produced outcomes are to the optimum under the paper’s definition. A method can have 100% legal outputs but a low success rate if it reaches legal but inferior assignments.',
                'Original example: a solver emits 100 assignments. Ninety-eight obey all rules, 20 of those are optimal, and the other 78 are legal but worse. The in-constraints rate is 98%, the success rate is 20%, and neither number alone tells the average objective value of the 78 non-optimal answers. A deployment contract must say which of these outcomes is acceptable.',
            ],
            'sources': [(PDF + '#page=1', 'HPCA paper, abstract and introduction: constrained binary optimization and metric distinction'), (PDF + '#page=10', 'HPCA paper, evaluation metrics: success, in-constraints, approximation-ratio gap, and latency')],
        },
        {
            'title': 'Encode the rule in the motion, not only as a penalty',
            'paragraphs': [
                'QAOA (quantum approximate optimization algorithm) is a quantum procedure that prepares and measures candidate assignments. A penalty-based design adds a cost when a candidate violates a rule. That can discourage violations, but it does not make them impossible: the penalty weight, search behavior, and competing objective still affect which states are measured. Choco-Q instead uses a commute Hamiltonian as the driver Hamiltonian. In everyday terms, the permitted quantum motion is chosen so it preserves the constraint while the state evolves.',
                'The paper’s claim is mathematical: the commute Hamiltonian remains compatible with the constraint operator, so the evolution preserves the constraint expectation for the constructed state. That is a guarantee about the encoding, not a guarantee that the measured legal state is optimal. Hardware noise, the objective search, and the tested problem still affect the final success rate.',
                'Original state-count example: suppose 16 possible assignments exist, but only 4 satisfy the rule. A penalty approach may still measure all 16, then rely on the penalty to prefer the 4 legal ones. A hard-constraint encoding restricts the evolution to the legal subspace in the teaching model. It does not make the four legal assignments equally good or eliminate the need to search among them.',
            ],
            'sources': [(PDF + '#page=2', 'HPCA paper, background: soft penalties, hard constraints, and prior QAOA limits'), (PDF + '#page=5', 'HPCA paper, commute-Hamiltonian encoding and constraint-preservation lemma')],
        },
        {
            'title': 'A mathematically correct circuit still has to fit the machine',
            'paragraphs': [
                'The direct commute Hamiltonian can involve many variables at once, which is hard to map onto a quantum chip with limited connections and executable depth. Choco-Q uses Hamiltonian serialization to replace one large operation with smaller local operations while preserving the constraint property. It then uses an equivalent decomposition into basic phase and controlled-not gates with linear time and circuit-depth growth in the relevant number of variables, rather than an exponential general decomposition.',
                'Variable elimination reduces the constraint matrix before generating the circuit. This can lower qubit count and depth, but it is not free. The eliminated variable must be tried or measured in separate cases, so eliminating k variables can require up to 2^k assignments. This is a useful architectural trade: less depth and fewer qubits in one run, more classical or repeated quantum work across runs.',
                'Original break-even example: a direct circuit takes 900 units once. Eliminating one variable makes each circuit 520 units and requires two cases, for 1,040 units total, so it loses if both cases are mandatory. Eliminating two variables makes each circuit 280 units and requires four cases, for 1,120 units. The smaller circuit may still be necessary because the direct circuit does not fit the hardware; deployability can matter before total work. The correct comparison includes both feasibility and repeated execution.',
            ],
            'sources': [(PDF + '#page=7', 'HPCA paper, serialization and preservation of constraints'), (PDF + '#page=8', 'HPCA paper, equivalent decomposition and linear complexity'), (PDF + '#page=9', 'HPCA paper, variable elimination, depth/qubit reduction, and measurement overhead')],
        },
        {
            'title': 'Read the result as a constrained-QAOA experiment, not a general quantum advantage claim',
            'paragraphs': [
                'Choco-Q evaluates facility location, graph coloring, and k-partition problems with six to 28 variables and up to 16 constraints. It uses IBM Fez, Sherbrooke, and Osaka quantum systems and an A100-accelerated simulation on an AMD EPYC server. The paper reports more than 235× average improvement in finding the optimal solution in its algorithmic comparisons, 100% in-constraints rate for Choco-Q, and 4.69× end-to-end acceleration on real hardware against the named prior design.',
                'These numbers answer different questions. The 100% figure concerns constraint satisfaction. The success-rate improvement concerns finding the optimum on the tested benchmark set. The 4.69× result includes the paper’s stated compilation, execution, and parameter-update timing boundary. It is not a claim that every constrained optimization problem, quantum device, or industrial workload receives that gain.',
                'The paper also reports that circuit depth grows with problem size and constraints, and the evaluation remains at current NISQ (noisy intermediate-scale quantum) scale. Device gate fidelity and connectivity matter: Fez uses a favorable CZ gate, while the other systems implement CZ through multiple ECR gates. This course has not rerun the quantum circuits or reproduced the simulator. The teaching examples are not Choco-Q measurements.',
            ],
            'sources': [(PDF + '#page=1', 'HPCA paper, abstract: reported algorithmic and end-to-end improvements'), (PDF + '#page=10', 'HPCA paper, benchmark, IBM hardware, A100 simulation, and metric setup'), (PDF + '#page=11', 'HPCA paper, success, in-constraints, approximation-gap, depth, and latency results')],
        },
    ],
    'exercise': {
        'question': 'A solver produces 100 outputs: 98 satisfy all constraints and 20 of those are optimal. What are the in-constraints rate and success rate? Separately, if eliminating one variable creates two 520-unit runs from a 900-unit direct run, what is the total repeated cost?',
        'answer': 'The in-constraints rate is 98%, and the success rate is 20%. The eliminated-variable plan costs 2×520 = 1,040 units, compared with 900 for the direct run. It may still be the only deployable plan if the direct circuit exceeds hardware depth or qubit limits. These are original teaching calculations, not Choco-Q measurements.',
    },
}
