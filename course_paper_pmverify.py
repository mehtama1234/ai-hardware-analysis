"""Focused ASPLOS walkthrough of crash outcomes and checker verdicts."""

PDF = 'https://feihe.github.io/materials/asplos25.pdf'

PMVERIFY = {
    'id': 'pmverify-2025',
    'route': 'asplos-2025',
    'title': 'PMVerify: ask which states a crash can leave behind',
    'identity': 'Zhilei Han and Fei He · Robustness Verification for Checking Crash Consistency of Non-volatile Memory · ASPLOS 2025',
    'scope': 'A focused walkthrough of the paper’s robustness property, crash-state search, and PMDK evaluation. The author-hosted paper and its stated model were inspected; the tool and benchmarks were not rerun. The two-store trace is adapted from the paper’s introductory example. The all-or-nothing recovery requirement is an added teaching example.',
    'lessons': [('durable-update', 'Durable updates'), ('s8', 'Correctness claims'), ('s7', 'Failures and recovery'), ('s2', 'Ordering')],
    'blocks': [
        {
            'title': 'A completed instruction may not mean a durable update',
            'paragraphs': [
                'Persistent memory keeps its contents after power loss. A processor may first place a store in a cache and write it to persistent media later. So “the program executed the store” and “the new value will still be there after a crash” are different statements. Hardware provides flush and fence operations to constrain when writes become persistent, but the programmer must use them with a valid ordering.',
                'The paper’s introductory example writes a=1 and then b=1, with both values initially zero. If a crash occurs after b=1 has reached persistent memory but before a=1 does, recovery can see a=0,b=1. Program order said a was written first; persistence order allowed b to survive first. The visible order of operations and the durable order of writes are not automatically identical.',
                'Now add a separate application requirement: recovery must return either (0,0) before the update or (1,1) after it. Enforcing write order can rule out (0,1), but still allows a crash to leave (1,0), after the first write survives and before the second does. That intermediate pair also fails this all-or-nothing requirement. A recovery protocol must finish or undo the partial update, or select a complete saved version. This explains why matching ordinary execution states is only one part of correctness: ordinary execution itself passes through (1,0).',
            ],
            'sources': [(PDF + '#page=1', 'Conference paper, introduction and Figure 1')],
        },
        {
            'title': 'Robustness compares crash states with ordinary program states',
            'paragraphs': [
                'PMVerify checks a property the paper calls robustness. In plain language, it asks whether a state left in persistent memory by a crash could also occur during an ordinary, non-crashing execution under the specified memory rules. If a crash exposes a state that ordinary execution cannot reach, the program violates this property. For the two-store example, ordinary execution preserves the write order; the crash-only state (0,1) therefore reveals a problem.',
                'This is a specific correctness question, not a complete proof that an application is correct. A program might reach a state during ordinary execution that still violates its own data-structure rules. Robustness would not by itself reject that state. After checking crash robustness, developers still need to establish that ordinary reachable states obey the application rules that must always hold, and that recovery uses those states correctly.',
                'The paper describes robustness as a bridge: first check whether crashes introduce states outside ordinary behavior; then check whether the ordinary behavior itself is correct under the memory model. This separation can avoid requiring a programmer to write a special crash invariant for the checker, but the property may be stronger than some applications actually require.',
            ],
            'sources': [(PDF + '#page=2', 'Conference paper, robustness definition and motivation')],
        },
        {
            'title': 'How the checker searches—and where it can stop',
            'paragraphs': [
                'A crash can cut an execution at many points, and only some earlier writes may have reached persistent media. PMVerify represents program actions and their ordering constraints, explores possible partial executions, and asks which persistent states can result. It then asks whether each candidate state is also reachable without a crash under the paper’s specified x86 memory rules—the rules that constrain which order of reads and writes a normal execution can expose. The implementation encodes that question for an SMT solver, a program that searches for values and event orders satisfying a set of logical constraints.',
                'A reported counterexample is a concrete ordering and crash state allowed by the model that violates robustness. A “robust” verdict requires exhaustive exploration of the cases the tool modeled. But a timeout, unsupported primitive, or loop bound that excludes relevant behavior is not an exhaustive proof. The sound conclusion depends on the code analyzed, the x86 and persistence model, supported operations, loop treatment, and whether exploration actually completed.',
                'The physical device is not being crashed and measured by this proof. The checker reasons about an abstract execution model. If the real platform, compiler, or persistent-memory behavior differs from the model, that gap needs its own validation. Likewise, a proof about the selected program does not cover a different version or an unmodeled library operation.',
            ],
            'sources': [(PDF + '#page=1', 'Conference paper, abstract and algorithm summary'), (PDF + '#page=7', 'Conference paper, implementation and analysis limits')],
        },
        {
            'title': 'Unknown is a result, not a safety verdict',
            'paragraphs': [
                'On 26 PMDK example programs, the paper reports one robust case, 12 robustness violations, and 13 cases the tool could not settle. It also reports six violations found beyond the dynamic tool PSan on that set, and proves six of 12 separately hand-crafted robust programs. These are counts for the named examples and tool settings, not estimates of how often arbitrary persistent-memory software fails.',
                'The 13 unknown cases are neither safe nor confirmed violations. For this benchmark, the paper says that most used PMDK operations its frontend did not model, while one supported program timed out. Reporting only the 12 violations would hide half the benchmark’s verdicts. Reporting 12/26 as a real-world failure probability would confuse a selected example set with a random sample of deployed applications.',
                'A useful report separates three outcomes: a counterexample found within the model, an exhaustive proof over the modeled cases, and an inconclusive run. Then state the model, source program, supported operations, loop bounds, and solver status. This lets a developer decide whether to repair code, increase analysis capacity, add support, or reconcile the model with the target system.',
            ],
            'sources': [(PDF + '#page=2', 'Conference paper, benchmark verdict summary'), (PDF + '#page=9', 'Conference paper, experimental results and limitations')],
        },
    ],
    'exercise': {
        'question': 'A checker reports a counterexample where a crash leaves (a,b)=(0,1), although ordinary execution can reach only (0,0), (1,0), and (1,1). A second program gets “unknown” because one library operation is unsupported. What does each outcome establish? If recovery must return either (0,0) or (1,1), why is a proof of robustness alone insufficient?',
        'answer': 'The first result establishes that the stated model permits a crash outcome outside ordinary reachable states, so the program is not robust under that model. The model must match the target device and compiler for this conclusion to apply there. “Unknown” means the checker did not settle the case. Even a robust program could leave (1,0), because that state occurs in ordinary execution. Recovery must still turn that partial update into one of the two complete versions required by the application.',
    },
}
