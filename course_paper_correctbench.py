"""DATE walkthrough with a bounded source summary and original checking examples."""
PAPER = 'https://arxiv.org/html/2411.08510v1'

CORRECTBENCH = {
    'id': 'correctbench-2025',
    'route': 'date-2025',
    'title': 'CorrectBench: who checks the generated checker?',
    'identity': 'Ruidi Qiu and colleagues · CorrectBench: Automatic Testbench Generation with Functional Self-Correction using LLMs for HDL Design · DATE 2025',
    'scope': 'Focused reading of author manuscript arXiv:2411.08510v1, sections III and IV-A–B. The publisher identifies the DATE 2025 publication. Examples below are original teaching models, not a reproduction or implementation of CorrectBench. Reported measurements have not been independently rerun.',
    'lessons': [('s8', 'Required behavior and tests'), ('s6', 'Generated programs'), ('durable-update', 'State and ordering')],
    'blocks': [
        {
            'title': 'A test contains two different jobs',
            'paragraphs': [
                'To test a circuit, first supply inputs in a particular order. One scenario is one concrete input sequence together with the output observation the checker expects. Then decide whether the resulting outputs satisfy the requirement. A testbench is the surrounding program that performs these jobs. Producing valid input code does not establish that its expected answers are right. Nor does a circuit passing that test establish that the test would reject an incorrect circuit.',
                'Consider an original requirement: a counter must become zero when reset. A test supplies reset and expects one instead. A correct circuit returning zero fails; a faulty circuit returning one passes. The simulation executed normally, but the judgment was reversed. Before treating a failure as evidence against the circuit, inspect what the checker expected and why.',
            ],
        },
        {
            'title': 'What CorrectBench changes',
            'paragraphs': [
                'CorrectBench builds on AutoBench and generates 20 candidate circuit descriptions from the specification. Reports from candidates with syntax errors are discarded. If more than half have those errors, it generates replacements until at least half are free of syntax errors. For usable candidates, it records agreement with the generated checker on each test scenario. If at least 70% of the candidates disagree on one scenario, the paper marks that scenario wrong. There is one counter-rule: if more than 25% of the candidates agree with the checker on every scenario, the paper accepts the checker. The resulting report identifies scenarios for correction or triggers a new generation attempt.',
                'The candidates are not assumed correct; the paper explicitly calls them imperfect generated designs. The method uses their pattern of agreement as evidence because it has no known-correct circuit at this stage. That evidence shows where candidates agree or disagree; it is not direct proof that the checker implements the natural-language requirement. A group of generated designs can share the same misunderstanding.',
            ],
            'sources': [(PAPER + '#S3', 'Author manuscript, section III — generation, scenario validation, and correction'), ('https://ieeexplore.ieee.org/document/10992873/', 'Publisher record — DATE 2025 paper identity')],
        },
        {
            'title': 'Read agreement without turning it into truth',
            'paragraphs': [
                'First apply the paper’s thresholds to an invented group where all 20 candidates are usable. Fourteen disagreeing on one scenario reaches 70%. But if the other six agree on every scenario, their 30% share triggers the acceptance override. Five candidates agreeing everywhere would be exactly 25%, which does not trigger the “more than 25%” rule. Count both per-scenario disagreement and whole-design agreement; either count alone can miss how this decision is made.',
                'Use an original five-design, three-scenario example. The numbers of designs disagreeing with the checker are 0, 4, and 2. Adopt a toy rule: flag a scenario if at least four of five designs disagree. Only scenario two is flagged. This rule is deliberately simpler than the paper’s rules; it lets us inspect what disagreement alone establishes.',
                'There are at least two explanations for the flagged scenario: the checker may be wrong, or four designs may be wrong in the same way. Agreement has the same limitation. In the reset example, suppose all five generated circuits return one and the checker expects one. They agree completely while jointly violating the requirement that reset produce zero. Creating more copies of the same misunderstanding does not add an independent reference.',
                'A disagreement report is therefore useful diagnostic information, not a replacement for the requirement. It tells a repair process where to look. After a proposed repair, rerun the affected scenarios and check cases that distinguish the suspected misunderstanding. For reset behavior, these might include resetting from different prior counter values; other timing and priority cases still need their own specified expectations.',
            ],
        },
        {
            'title': 'Stopping the repair loop and accepting the result are separate events',
            'paragraphs': [
                'Algorithm 1 also uses its “Pass” action when correction and restart limits are exhausted. That control-flow label alone does not establish successful validation.',
                'For an original cost example, generation takes 3 seconds, a check takes 2, and one repair takes 4. Generating, checking, repairing, and checking again costs 11 seconds. If the second check still finds a violation and the budget is exhausted, the outcome is an unresolved test at a cost of 11 seconds. Returning an artifact does not change that outcome into a validated test.',
                'The result interface should distinguish validated under the stated checks, unresolved after the budget, and unable to execute. This is a teaching recommendation about reporting results, not a claim that we inspected the project’s user interface. Preserve the failure information when comparing generation cost or counting usable outputs.',
            ],
            'sources': [(PAPER + '#S3.SS1', 'Author manuscript, section III-A and Algorithm 1 — stopping conditions')],
        },
        {
            'title': 'Attach the reported pass rate to its test',
            'paragraphs': [
                'The main experiment uses 156 HDLBits-derived tasks and five runs with gpt-4o-2024-08-06. Eval2 requires earlier syntax and reference-circuit checks plus agreement with a reference testbench on 80% of ten circuit mutants. Table I reports 70.13% Eval2 passes for CorrectBench, 52.18% for AutoBench, and 33.33% for direct generation. These are task pass rates under that evaluation, not proof of all behaviors.',
                'A mutant is a deliberately changed implementation. Matching a trusted checker’s judgments on selected mutants can test whether a generated checker distinguishes those cases appropriately. It does not automatically cover every input sequence or every possible design error. In particular, a threshold allowing some disagreement should not be retold as perfect agreement on the evaluation set.',
            ],
            'sources': [(PAPER + '#S4.SS1', 'Author manuscript, section IV-A and Table II — dataset and evaluation definitions'), (PAPER + '#S4.SS2', 'Author manuscript, section IV-B and Table I — main comparison')],
        },
        {
            'title': 'Count accepted mistakes, not just overall accuracy',
            'paragraphs': [
                'Use a separate invented population of 100 testbenches whose true quality is known: 80 correct and 20 incorrect. A validator accepts 76 of the correct ones and rejects 12 of the incorrect ones. Its total correct decisions are 76 + 12 = 88, or 88%. But it also accepts 8 incorrect testbenches. Of the 84 it accepts, 8/84, about 9.5%, are incorrect.',
                'A second denominator is the original 20 incorrect testbenches: 8/20, or 40%, slipped through. The 88% overall accuracy, 9.5% incorrect share among accepted tests, and 40% missed-error share answer different questions. None may be substituted for another. These teaching numbers are unrelated to the paper’s measurements.',
                'For a user who will trust an accepted checker, the remaining mistakes among accepted outputs matter directly. For a repair system, rejecting correct tests also matters because it spends time changing something that already met the requirement. Report both kinds of mistake and the costs of responding to them.',
            ],
        },
    ],
    'exercise': {
        'question': 'In another original evaluation, 100 testbenches are correct and 100 are incorrect. The validator accepts 95 correct ones and rejects 60 incorrect ones. What are its overall accuracy and the incorrect share among accepted outputs? Does a larger evaluation set by itself explain the change from the earlier example?',
        'answer': 'There are 95 + 60 = 155 correct decisions out of 200, giving 77.5% accuracy. The validator accepts 95 correct and 40 incorrect tests, so 40/135, about 29.6%, of accepted outputs are incorrect. Its acceptance rate for correct tests remains 95%, and its rejection rate for incorrect tests remains 60%, exactly as in the earlier example. The mixture changed from 80% correct tests to 50%, altering the combined metrics. The changed mixture, not merely the larger count, explains this arithmetic.',
    },
}
