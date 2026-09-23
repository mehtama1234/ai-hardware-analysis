"""ICCAD foundations with one separately bounded primary-paper walkthrough."""

ICCAD_ROUTE = {
    "id": "iccad-2025",
    "title": "ICCAD 2025: finding a design is not the same as checking it",
    "coverage_status": "Foundational guide and one focused paper walkthrough; conference source review unfinished",
    "status": "The route examples are original teaching models. One full RSizing walkthrough adds a separately inspected primary paper; the route is not a full-conference synthesis.",
    "intro": "Suppose a circuit must produce its answer within ten nanoseconds and fit in a limited amount of chip space. A tool can propose many designs, but which ones actually meet both requirements? This guide follows four questions: what counts as acceptable, when an estimate needs a closer check, whether the circuit does the requested job, and how much time the search itself takes. The examples are invented. One inspected paper, RSizing, has a separate walkthrough; the remaining conference records are leads for further reading, not evidence of methods reviewed here.",
    "evidence": "The historical local source audit reports 281 structured-abstract records and no usable PDF URL in the enriched corpus. That describes the audit boundary, not current worldwide availability. The course subsequently inspected the author-hosted RSizing paper, sections II–IV, for the one full learner walkthrough. Its numerical circuit results are author-reported simulations, not independently reproduced measurements. Other conference topics remain foundational reading questions pending primary-paper review.",
    "themes": [
        {
            "title": "1. Decide what must pass before deciding what is best",
            "body": "A circuit that answers too late may be unusable, however little chip space it occupies. Start by separating requirements from preferences. For example, require an answer within ten nanoseconds, then choose the smallest design that meets that limit. This gives two steps: check whether each design passes, then compare the passing designs. Combining those steps into a single score can change which design wins.",
            "subthemes": [
                ("Requirements and preferences", "A requirement that must be met is called a constraint. The quantity you try to improve is called an objective. Here, delay must stay within the limit; area should be as small as possible. A score that rewards smaller area enough to excuse a missed timing limit is solving a different problem."),
                ("Choosing between passing designs", "Two designs may both pass, with one smaller and the other faster. If the stated objective is minimum area, choose the smaller one. If extra speed matters too, say how much extra area you are willing to spend for it. The measurements alone cannot supply that preference."),
            ],
            "reading": "The audit identifies circuit sizing and design-space optimization as discovery topics. For a selected paper, obtain the full objective, constraint definitions, and treatment of failed candidates before interpreting an improved score.",
            "worked_example": [
                "Use three invented candidates with (area, delay) pairs A = (8, 12), B = (10, 9), and C = (12, 8), where area is in arbitrary units and delay in ns. The task is to minimize area while staying at or below 10 ns. A fails the constraint; B beats C among the acceptable candidates. If delay and area are both preferences without a hard limit, none is simply best: each smaller candidate is slower. The application must supply the tradeoff.",
                "Now replace the hard rule with a score: area + 0.5 × max(0, delay − 10), and choose the lowest score. A scores 9, B scores 10, and C scores 12. The score chooses A even though A violates the original requirement. A penalty is not the same thing as enforcing a limit. Its coefficient converts the timing penalty into score units and expresses a preference; it does not prove that all violations will lose.",
            ],
            "practice": {
                "question": "What penalty coefficient makes A strictly worse than B in this three-candidate example? Would that coefficient guarantee feasibility for every possible candidate?",
                "answer": "A scores 8 + 2λ and B scores 10. A is strictly worse when λ > 1; at λ = 1 they tie. That comparison establishes nothing about unseen candidates: a different area saving or a very small timing violation can change the necessary coefficient. If the delay limit is mandatory, retain an explicit acceptance check rather than relying on this finite example to certify the penalty.",
            },
            "lessons": [("physical-design", "Physical limits"), ("s8", "Specified acceptance")],
        },
        {
            "title": "2. Check what an early estimate leaves out",
            "body": "A detailed circuit check may take too long to run on every proposed design. A faster estimate can help choose what to inspect next. But an estimate of 9.9 nanoseconds is not enough to establish that a design meets a ten-nanosecond limit unless we also know how wrong that estimate could be. Near the limit, a small error can reverse the decision.",
            "subthemes": [
                ("What the estimate omits", "An early estimate may not yet know where components will sit or how long their connecting wires will be. Ask which details it assumes and which the later check includes. Adding those details can change both whether a design passes and which design is fastest."),
                ("Small errors, wrong choices", "Check whether the estimate accepts a failing design or rejects a passing one. An average error combines all the cases; it does not tell you which individual decisions were wrong. In the separate RSizing walkthrough, also distinguish meeting each requirement separately from meeting them all in the same trial."),
            ],
            "reading": "Routing, 3D integration, photonics, and optimization appear in the audit's topic list. These topics do not share one model of physical cost; inspect the selected paper's particular estimate and validation method.",
            "worked_example": [
                "Consider predicted delays A = 9.7 ns, B = 9.9 ns, C = 10.2 ns, with a 10-ns limit. A more detailed check gives A = 10.1, B = 9.8, C = 9.95 ns. For this example, use that later check to decide whether each design passes. The prediction errors, ignoring their signs, are 0.4, 0.1, and 0.25 ns: an average of 0.25 ns. But the decisions matter too. Choosing A because it is predicted fastest selects a failing design. Rejecting C because its prediction exceeds ten discards a passing design. B is the fastest passing design according to the later check. Report these wrong decisions as well as the average numerical error.",
                "Suppose, in a separate teaching case, a justified worst-case prediction error is at most 0.4 ns for every candidate in scope. To certify delay at or below 10 from that bound alone, require predicted delay + 0.4 ≤ 10, or prediction ≤ 9.6. A prediction of 9.7 cannot be certified by this bound; it is not necessarily invalid. A measured average error of 0.4 would not justify the same guarantee, and a bound established for one class of layouts need not cover another.",
            ],
            "practice": {
                "question": "A candidate is predicted at 9.5 ns. Compare what follows from a certified worst-case error of 0.4 ns and from an observed mean absolute error of 0.4 ns. What should happen to candidates that an early screen cannot certify?",
                "answer": "The worst-case bound places delay at most at 9.9 ns, so the stated timing condition follows if the bound applies. A mean error does not bound this candidate's error and cannot certify it. Uncertain candidates can receive a more detailed check or remain unresolved; treating uncertainty as invalidity may discard a good design. The additional check has a cost that belongs in the search budget.",
            },
            "lessons": [("physical-design", "Estimates and later checks"), ("s6", "Search cost")],
        },
        {
            "title": "3. Check the requested behavior, not just whether the code runs",
            "body": "A tool can produce circuit code that the next tool accepts but that computes the wrong answer. Write down the expected behavior before checking the generated code. Include what should happen at boundaries, such as a counter reaching its largest value. Otherwise a test may merely confirm the same mistaken rule that produced the code.",
            "subthemes": [
                ("Where the expected answer comes from", "A test needs both an input and an expected result. Derive that result from the requirement, not by copying what the generated code does. Also state which inputs were checked; ten ordinary cases can miss a mistake at a boundary."),
                ("From correct code to a usable circuit", "Code describes behavior, but the circuit still needs components and connections that fit on the device and operate fast enough. Check behavior and physical limits separately. Passing one check does not supply the result of the other."),
            ],
            "reading": "RTL and code generation are discovery topics, not evidence of successful generation or correctness. A future walkthrough must distinguish parsing, simulation, equivalence checking, physical feasibility, and measured operation.",
            "worked_example": [
                "An invented counter stores a whole number from 0 to 255 using eight bits. The requirement says to add one each tick and return to zero after 255; this return is called wraparound. The generated code instead stays at 255. Both versions are accepted by the code-reading tool, and both give the same answers for the first ten ticks starting at zero. Start at 255, however, and one tick distinguishes them: the required answer is zero, while the generated version gives 255.",
                "Even a functionally correct counter can fail a separate timing requirement. If its required clock interval is 1 ns but an implementation check finds a 1.2-ns path requirement under the stated conditions, the functional result does not establish physical feasibility. Conversely, meeting timing does not fix saturation where wraparound was required. Keep the reference behavior and the implementation constraints as separate checks.",
            ],
            "practice": {
                "question": "A test generator copies the implementation's rule that the counter stops at 255. Why might thousands of generated tests still miss the specification error? What independent reference should the check use?",
                "answer": "The tests can encode the same mistaken behavior as their expected answer. More tests then confirm agreement between two copies of the mistake. Derive the expected answer from the requirement: add one, then take the remainder after division by 256. Checking all 256 possible current values covers every input to this one-step calculation. The counter itself stores state, but here its current value is the complete input needed to calculate the next value. These checks do not cover reset behavior or clock timing, neither of which this example specifies.",
            },
            "lessons": [("s8", "Testing and proof"), ("s6", "Translation"), ("physical-design", "Implementation evidence")],
        },
        {
            "title": "4. Count the time spent searching, including failed attempts",
            "body": "Trying fewer designs need not save time if each attempt is more expensive. Start the timer at a stated point and include proposing designs, evaluating them, and checking the final choice. Count failed attempts too: their results may be discarded, but their time was still spent. Compare searches that must meet the same requirements, so a quick search cannot win merely by returning an unacceptable design.",
            "subthemes": [
                ("Time per attempt and number of attempts", "Record both. Also state whether attempts run one after another or at the same time on separate workers. Equal numbers of attempts need not mean equal elapsed time or equal total machine use."),
                ("What another person needs to repeat the search", "Keep the input design, tool versions, settings, and the starting value used to generate any random choices. Record the conditions used to check the result. Repeating one search successfully does not show that the method will work as well on a different circuit."),
            ],
            "reading": "RSizing, section IV.B and table IV, gives a concrete comparison boundary. For the amplifier, PVTSizing takes 1.53 hours for target T1 and reports 95.1% passing in simulation. RSizing reports 2.41 hours for one search producing several design choices; its T1 result is 99.5%. PVTSizing's T2 and T3 searches have their own runtimes, while RSizing's runtime covers the set. These entries do not establish that one method is simply faster at the same job: both the requested output and the observed passing rate differ. Decide whether the task needs one chosen target or several alternatives, then compare the cost of obtaining outputs that meet the same acceptance conditions. These are author-reported simulation results, not manufactured-chip yields or an independently repeated timing test.",
            "worked_example": [
                "In an invented serial search, method A tests 100 candidates at 2 seconds each and spends 20 seconds validating the winner: 220 seconds total. Method B tests 20 candidates at 12 seconds each, then performs the same validation: 260 seconds. B checks fewer candidates but takes longer. This comparison assumes both find an equally acceptable final design; otherwise time alone is not a sufficient ranking.",
                "Four independent evaluation workers change the scheduling question. If every candidate is ready initially, evaluations have the stated equal durations within each method, and workers share no bottleneck, A takes 25 waves × 2 + 20 = 70 seconds and B takes 5 × 12 + 20 = 80. If each new candidate depends on the previous result, those waves are not available. Parallel hardware does not remove that dependency. Failed candidates, generation overhead, and rechecks would also need to be included if present.",
            ],
            "practice": {
                "question": "Method B can reuse an earlier preparation step and now takes 8 seconds per candidate. What are its serial and four-worker totals? What must remain fixed before comparing it with A?",
                "answer": "Serial time is 20 × 8 + 20 = 180 seconds; the independent four-worker schedule takes 5 × 8 + 20 = 60 seconds. Both beat A's corresponding totals of 220 and 70. Compare the same acceptance constraints, quality of the final design, and resource boundary. If reusable preparation was performed earlier solely for this job, charge it rather than hiding it outside the timer.",
            },
            "lessons": [("s1", "Complete timing"), ("physical-design", "Resource boundaries"), ("s8", "Evidence scope")],
        },
    ],
    "exercise": "Three invented designs have (area, delay) pairs A = (8 units, 12 ns), B = (10 units, 9 ns), and C = (12 units, 8 ns). With a hard 10-ns limit and minimum area as the objective, B is preferred: A is invalid and C uses more area. Tighten the limit to 8.5 ns and C becomes the only acceptable candidate. Explain why declaring A best by area alone silently changes the design problem, and why an early prediction of 8.4 ns for C still needs an uncertainty or implementation check before claiming the tighter limit is met.",
    "sources": [
        ("https://www.cse.cuhk.edu.hk/~byu/papers/C287-ICCAD2025-RSizing.pdf", "Tu and colleagues, RSizing — author-hosted ICCAD 2025 paper; sections II–IV support the focused walkthrough"),
        ("analysis/iccad-2025-source-acquisition-audit.md", "ICCAD local audit — 281 abstracts, no locally acquired full texts"),
    ],
}
