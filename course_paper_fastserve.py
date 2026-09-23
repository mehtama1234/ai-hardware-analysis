"""NSDI scheduling walkthrough with an original two-job trace."""
PDF = 'https://www.usenix.org/system/files/nsdi26-wu-bingyang.pdf'

FASTSERVE = {
    'id': 'fastserve-2026',
    'route': 'nsdi-2026',
    'title': 'FastServe: a useful stopping point still has a cost',
    'identity': 'Bingyang Wu and colleagues · FastServe: Iteration-Level Preemptive Scheduling for Large Language Model Inference · NSDI 2026',
    'scope': 'Focused on preemption, retained state, and evaluation boundaries. The final USENIX conference PDF, sections 4.1–4.2 and 6.1–6.2, was inspected. Earlier preprint headline numbers are not substituted for this edition. The schedules below are original teaching examples, not executions of FastServe; no experiment has been reproduced.',
    'lessons': [('queues-and-batching', 'Service order'), ('dependencies-and-pipelines', 'Legal stopping points'), ('s3', 'Retained state')],
    'blocks': [
        {
            'title': 'Start with the request that cannot get a turn',
            'paragraphs': [
                'Suppose a worker starts a long job L at time 0. L needs 8 ms of execution. A short job S arrives at time 1 and needs 2 ms. If the worker finishes L before starting S, L completes at 8 and S at 10. Their arrival-to-completion delays are 8 and 9 ms, averaging 8.5. The second job spends most of its time waiting for work that does not contribute to its answer.',
                'Now allow L to pause at time 1, after a complete unit of work. With no switching cost, S runs from 1 to 3. L resumes at 3 and uses its remaining 7 ms, finishing at 10. The delays are now 10 for L and 2 for S, averaging 6. The last completion still occurs at 10: changing the order improved the mean without reducing the total execution work. L itself is worse off. This policy favors the newcomer in this particular trace; it is not an oracle that knows every future job’s length.',
                'This interruption is called preemption. To resume safely, the system must retain enough state to continue at the chosen boundary without corrupting the result or repeating an externally visible effect. A boundary between completed iterations can be easier to manage than interruption halfway through an operation. That does not make the boundary costless, nor does it mean the whole job’s remaining duration is known.',
            ],
        },
        {
            'title': 'The paper’s scheduling and memory choices',
            'paragraphs': [
                'The first pass through a request is called prefill: the model reads the whole input prompt and builds the intermediate key–value cache, the saved keys and values that later output steps reuse instead of recalculating the whole prompt. Later steps are decoding: each step adds one output token and updates that saved cache. Prefill can take much longer than one decoding step, while the number of decoding steps depends on how long the answer becomes. That difference is why a scheduler can know something about the first step without knowing the full job length.',
                'FastServe preempts at output-token iteration boundaries. It keeps several priority queues with different time allowances. From the predicted first-iteration time, it puts a new request in the highest-priority queue whose allowance can cover that first pass, rather than making a long prompt first consume several shorter allowances. An unfinished request moves to a lower-priority queue; a request that has waited long enough is moved back to the highest-priority queue. The paper calls this arrangement skip-join multilevel feedback queues. Input length is known; output length is not.',
                'A token boundary is not an arbitrary stopping point inside the first iteration. That first pass processes the input prompt and can exceed a short queue’s time slice. The paper explains that stopping it partway would drop intermediate activations and require their later recomputation. FastServe therefore uses its predicted prefill time to place a new job directly in a queue whose time slice can accommodate that first iteration. Section 4.2 then manages saved key–value state with proactive transfers between GPU and host memory. Paused jobs still need that state.',
            ],
            'sources': [(PDF + '#page=6', 'Final paper, section 4.1 — scheduling'), (PDF + '#page=7', 'Final paper, section 4.2 — saved-state pressure')],
        },
        {
            'title': 'Put the switching cost back into the timeline',
            'paragraphs': [
                'Return to the two-job example. Let saving L cost h ms before S can run, and restoring L cost another h after S finishes. Assume both transfers block useful execution and no other costs change. S completes at 3 + h, so its delay is 2 + h. L completes at 10 + 2h. The mean is therefore (12 + 3h)/2 = 6 + 1.5h ms. The switch helps the mean only when h is less than 5/3 ms, about 1.67.',
                'For h = 1 ms, S completes at 4 and L at 12. Their delays are 3 and 12, averaging 7.5: better than 8.5 even though finishing both jobs takes longer. For h = 2, the mean becomes 9 and the change loses. A scheduler can improve average response while reducing completed work over a short interval. Always name the metric before calling the schedule better.',
                'A transfer lower bound makes h less mysterious. Moving 8 MB across an otherwise idle connection delivering 8 GB per second takes at least 1 ms, using decimal units. A save and a restore require two such transfers. Setup, competing traffic, allocation, and additional state can make the interruption more expensive. Overlap helps only where another operation is independent and the required connection and storage are available.',
            ],
        },
        {
            'title': 'Pausing work changes the memory population',
            'paragraphs': [
                'Imagine 12 GB available for request state, after all other allocations. Each active or paused request retains 4 GB. Three fit; a fourth does not. Pausing one request frees its execution slot but none of that memory. To admit another, the system must complete or discard permitted state, move state elsewhere, or use a representation that occupies less space. Each choice changes time, space, or the reconstruction obligation.',
                'A policy that starts many jobs and then pauses them can therefore create a larger resident population than one that finishes fewer jobs before admitting more. Moving paused state to host memory restores device capacity, but creates future return traffic. A queued request may need little state if it has never started; a partially executed request may already hold much more. Counting jobs without distinguishing these states can hide the pressure.',
                'Fairness is a separate issue. If new short jobs always take priority, a long job can wait indefinitely under continuing arrivals. Increasing a waiting job’s priority is one possible response, but it consumes service that otherwise went to newcomers. No scheduler can promise every request an arbitrary deadline when sustained offered work exceeds available capacity. Specify admission, overload behavior, and which fairness rule is intended.',
            ],
        },
        {
            'title': 'Read the metric before comparing the headline',
            'paragraphs': [
                'The evaluation uses A100 hardware, OPT models and Llama3-8B, and ShareGPT/Alpaca request lengths with generated Poisson arrivals: a standard random-arrival model with a stated average arrival rate. Its average per-token latency is the mean of each job’s end-to-end delay divided by output length. It also reports P95 latency—the value below which 95% of the measured jobs fall—to show a slow-request tail and a fairness-related effect. It compares the rate of completed work while holding a response-time target, including vLLM v0.6.1 and a FastServe version that keeps first-come, first-served order. Section 6.2 notes that implementation differences also improve that first-come, first-served version over vLLM. The complete-system gain therefore cannot be attributed solely to preemption.',
                'Normalized job delay is not an observed gap between adjacent outputs. In a teaching example, a job waits 900 ms and then emits ten outputs over 100 ms. Its 1,000-ms arrival-to-completion delay divided by ten is 100 ms per output. That value includes the initial wait; it is not a statement that consecutive outputs were 100 ms apart. Likewise, taking the mean of job ratios weights jobs differently from dividing total delay by total output count when lengths differ.',
                'Use an internal comparison version to distinguish a scheduling change from a faster execution engine, but inspect exactly which features were disabled. A comparison that removes several techniques together identifies their combined effect, not each technique’s isolated contribution. Preserve the paper’s versions, arrival model, and rule for counting a request as acceptable when carrying its result into another workload; a modern system with the same name may behave differently.',
            ],
            'sources': [(PDF + '#page=10', 'Final paper, sections 6.1–6.2 — metric, versions, and baseline interpretation')],
        },
        {
            'title': 'Compare three different places to intervene',
            'paragraphs': [
                'FlashInfer’s walkthrough asks how to divide ready attention work; BlitzScale’s asks when another worker becomes useful; this one asks which waiting request should receive a turn. Faster arithmetic, more available workers, and a different service order can all reduce waiting in some conditions, but they change different state and costs. None makes saved-state transfer or fairness disappear.',
                'To assess a combined proposal, reconstruct a single timeline with one arrival trace and one memory budget. Include the cost of pausing, the time until added capacity is usable, and the actual execution time after kernel changes. Do not multiply separate paper speedups: the first change may remove the bottleneck that made the second attractive.',
            ],
            'sources': [('#paper-flashinfer-2025', 'Compare: ready work inside attention'), ('#paper-blitzscale-2025', 'Compare: capacity during startup')],
        },
    ],
    'exercise': {
        'question': 'Repeat the two-job schedule with h = 0.5 ms for each save and restore. Compute both completion times and arrival-to-completion delays. If L has a deadline of time 9 ms and S has a deadline of time 5 ms, does either policy meet both? What does the mean conceal?',
        'answer': 'S completes at 3.5 and has delay 2.5. L completes at 11 and has delay 11, giving mean 6.75 ms. Preemption meets S’s deadline but misses L’s. Without preemption, L finishes at 8 and meets its deadline while S finishes at 10 and misses its own. Neither policy meets both. The lower mean conceals which request lost service; choosing a policy needs the actual deadline or fairness objective, not just the average.',
    },
}
