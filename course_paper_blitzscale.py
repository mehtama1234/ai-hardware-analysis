"""Focused OSDI walkthrough; toy schedules are not a system reproduction."""

PDF = 'https://www.usenix.org/system/files/osdi25-zhang-dingyan.pdf'

BLITZSCALE = {
    'id': 'blitzscale-2025',
    'route': 'osdi-2025',
    'title': 'BlitzScale: when can a partly loaded machine begin helping?',
    'identity': 'Dingyan Zhang and colleagues · BlitzScale: Fast and Live Large Model Autoscaling with O(1) Host Caching · OSDI 2025',
    'scope': 'A focused discussion of capacity that can actually complete requests during startup. The cooperative-execution explanation in section 4, the introduction to section 5.1, and evaluation sections 6–6.1 were inspected. This is not a walkthrough of the complete scheduling algorithm or a reproduction. All numerical examples below are invented unless explicitly attributed.',
    'lessons': [('dependencies-and-pipelines', 'Pipelines'), ('queues-and-batching', 'Waiting requests'), ('s4', 'Shared connections'), ('s10', 'Complete serving path')],
    'blocks': [
        {
            'title': 'An allocated machine is not yet request-serving capacity',
            'paragraphs': [
                'A service receives more requests than its current workers can finish. Adding a worker is a common response, but the new worker needs the program and model data before it can process an independent request. Allocation time, first processing, and independent full service are three different events. Counting a worker as ready at the first event hides the interval in which the queue is still growing.',
                'Consider an idealized continuous-flow model with 100 arrivals per second and capacity for 80 completions per second. Start with no backlog. While the extra worker is unavailable, unfinished work grows by 20 requests per second. If the worker can process an independent request after eight seconds, the backlog is 160 requests. If it adds capacity for 40 completions per second, total capacity becomes 120: 100 handles continuing arrivals and only 20 clears the backlog. Clearing it takes another eight seconds. This model ignores individual service times; it explains accumulated work, not a measured request-delay percentile.',
                'If the same additional capacity becomes available after three seconds, the backlog is only 60 and takes three seconds to clear. Recovery from the burst takes six seconds from the start rather than sixteen. Startup delay matters twice here: it creates extra waiting work and postpones the spare capacity needed to remove it. These results rely on continuing arrivals at 100 and capacity staying at 120 after startup.',
            ],
        },
        {
            'title': 'The paper’s mechanism',
            'paragraphs': [
                'BlitzScale transfers model parameters through the GPU communication network and plans their distribution to new workers. Its cooperative execution lets a partly loaded worker run available layers while an existing worker runs the rest. Section 5.1 names loading time, planning time, and interference with serving as planning concerns.',
                'The title’s O(1) host caching means one host-held copy per model across the service, rather than one extra host copy for every new serving instance. Here the fixed copy count gives a bound independent of instance count; the notation does not say the copy is small or free. If an instance already holds that model, the paper’s network multicast forwards the parameters through a planned path to several new instances. If none does, a host that holds the model can begin that distribution. O(1) does not mean zero parameter bytes, zero network traffic, or instant startup; it describes how the number of cached copies grows as more instances are added.',
                'Keep the two sizes separate in an original storage example. Three models of 10 gigabytes each need 30 gigabytes for one host-held copy of each. Increasing the serving instances from two to twenty does not change those 30 gigabytes under this storage rule. Increasing the number of distinct models from three to six raises the host copies to 60 gigabytes. The count is constant with respect to serving instances, not with respect to every possible change. This example counts only those cached model bytes, not GPU copies, buffers, other host memory, or traffic; its sizes are not paper measurements.',
            ],
            'sources': [(PDF + '#page=7', 'Conference paper, section 4 cooperative execution and section 5.1 planning objectives')],
        },
        {
            'title': 'Follow a request across a partial worker',
            'paragraphs': [
                'Use a separate teaching model with four sequential layers, each taking 2 ms. A layer transforms the previous layer’s output; the next layer cannot run before that input exists. The original worker holds all four layers and takes 8 ms per request. A new worker has loaded only the first two. Suppose it runs those in 4 ms, sends their result across a separate connection in 1 ms, and the original worker runs the remaining two in 4 ms. One request now takes 9 ms, not 4. Partial availability has not halved its execution delay.',
                'Yet several requests can progress at different stages. With enough ready work and buffers, request A runs on the new worker from 0–4, transfers from 4–5, and finishes on the original worker from 5–9. Request B starts on the new worker at 4, transfers at 8–9, and finishes at 13. Request C finishes at 17. The three completions are at 9, 13, and 17 ms instead of 8, 16, and 24 ms on the original worker alone. The first result is later, but the stream finishes sooner.',
                'This schedule assumes independent workers and a connection that can transfer while both calculate. Loading more model data must not steal the resources assumed available here. It also assumes the original worker can devote its time to the remaining layers instead of simultaneously serving an unchanged share of full requests. You cannot count that same worker’s full standalone capacity again: it is already part of the cooperative path.',
                'Once filled, the pipeline finishes a request every max(4, 1, 4) = 4 ms. If transfer instead takes 6 ms on the one shared connection, that interval becomes 6 ms and the first result takes 14 ms. If transfer takes 9 ms, the continuing interval becomes 9 ms, worse than the original worker’s 8. Moving an intermediate result can erase the benefit of moving its computation. This is a property of the stated toy pipeline, not an empirical threshold for BlitzScale.',
            ],
        },
        {
            'title': 'Readiness also has a correctness condition',
            'paragraphs': [
                'A layer being present in memory is not sufficient evidence that it is ready for a particular request. It must be the intended model version, use the expected representation, and receive the right intermediate values for that request. During a change in assignment, specify which worker owns each step and when buffers may be reused. Otherwise a transfer that is fast in isolation can feed the wrong data into perfectly functioning arithmetic.',
                'These are review questions, not claims that this paper contains such bugs. Ask what happens if loading fails halfway, a request is retried, or an assignment changes while an older request is in flight. Keep the question separate from the performance result until the relevant implementation or protocol evidence is examined. Similarly, storing fewer extra model copies saves space but does not eliminate the need for a valid source or enough bandwidth when demand rises.',
            ],
        },
        {
            'title': 'What was evaluated, and how to compare it',
            'paragraphs': [
                'Sections 6–6.1 evaluate the system on A800 and A100 clusters using scaled versions of the BurstGPT, AzureCode, and AzureConv request traces. The authors preserve each trace’s timing pattern but set its average request rate to half the cluster’s maximum serving capacity. For each model, they choose one trace-and-cluster pairing rather than testing every combination. Section 6.1 uses separate instances for prompt processing and token generation, and scales those two kinds of work independently.',
                'On BurstGPT with a 72-billion-parameter model in cluster A, the authors report mean time to first token 75.5% shorter than ServerlessLLM and 21.1% shorter than its always-host-cached variant. They report the time between later tokens as 7.4% and 5.1% shorter, respectively. The paper also states that its LLM GPU kernels come from FlashInfer. These are paper-reported results and implementation facts, not independent verification.',
                'The paper reports both the average delay in one-second windows and the distribution of delays over the run. The 75.5% figure is for mean time to first token in that selected BurstGPT setup; it is not a 75.5% reduction in every request’s delay or in tail latency. The smaller gains for later-token delay show why the first visible answer and the continuing stream must be measured separately. A shorter first-token delay also does not establish an equal reduction in total GPU time. Preserve the chosen trace, scaled load, hardware, serving layout, and baseline when interpreting the comparison.',
                'The FlashInfer walkthrough asks how ready work is divided inside attention execution. This walkthrough asks when a new worker can contribute during service expansion. Those questions meet because changing computation time also changes how much spare capacity is available to drain a queue. The implementation connection is real, but multiplying separate headline gains would double-count or ignore interacting costs. A joint claim needs a common baseline, workload, software configuration, and measured endpoint.',
            ],
            'sources': [(PDF + '#page=11', 'Conference paper, section 6 setup and implementation'), (PDF + '#page=12', 'Conference paper, section 6.1 comparison and BurstGPT result'), ('#paper-flashinfer-2025', 'Compare with the FlashInfer walkthrough')],
        },
    ],
    'exercise': {
        'question': 'In the continuous-flow example, a partial worker starts helping at time 3 seconds but adds only 10 completions per second until time 8. At time 8 its added capacity becomes 40 per second. Arrivals remain 100 per second. How much backlog exists at time 8, and when does it clear? Why is first useful work not the same as stopping queue growth?',
        'answer': 'The first three seconds add 3 × (100 − 80) = 60 requests. During the next five seconds, capacity is 90, so another 5 × (100 − 90) = 50 accumulate. Backlog at time 8 is 110. Capacity then becomes 120, giving 20 per second for drainage; clearing takes 5.5 more seconds, at time 13.5. Partial help reduced growth but did not reverse it. This assumes no failures, constant arrivals, and the stated effective completion capacities.',
    },
}
