"""Focused MLSys walkthrough of latency promises and request scheduling."""

PDF = 'https://proceedings.mlsys.org/paper_files/paper/2025/file/bc82dbfbfa43232be85b8d9838f49c3e-Paper-Conference.pdf'

SOLA = {
    'id': 'sola-2025',
    'route': 'mlsys-2025',
    'title': 'SOLA: schedule for the requests that can still meet their promises',
    'identity': 'Ke Hong, Xiuhong Li, Lufang Chen, and colleagues · SOLA: Optimizing SLO Attainment for Large Language Model Serving with State-Aware Scheduling · MLSys 2025',
    'scope': 'A focused walkthrough of the latency promises, iteration-level scheduling choice, state observation, and end-to-end evaluation in the conference paper. The reported experiments are author-run; this course does not reproduce them. All hand-calculated request examples are invented teaching models, not SOLA simulations.',
    'lessons': [('queues-and-batching', 'Queues and batching'), ('dependencies-and-pipelines', 'Service phases'), ('s10', 'Complete serving path'), ('s1', 'Latency measures')],
    'blocks': [
        {
            'title': 'One request has two different waiting experiences',
            'paragraphs': [
                'When a language-model request arrives, the system first processes its prompt and produces the first output token. This is the prefill phase. It then generates more tokens in repeated decode steps. Time-to-first-token (TTFT) measures the wait from arrival to that first token. Time-per-output-token (TPOT) measures the time per later token. A service can feel unresponsive because the first token is late, or feel slow because the next tokens arrive too far apart. Passing one measure does not imply passing the other.',
                'A service-level objective (SLO) is a service promise expressed as a limit. For example, a provider might require TTFT no greater than 500 ms and TPOT no greater than 200 ms. A request meets this pair only if both limits are met. “Fast on average” can hide requests that miss a promise, so count the share of requests meeting the complete pair as well as the system’s request rate.',
                'SOLA calls the share of requests meeting the configured latency limits SLO attainment. In this paper, goodput has a specific meaning: the largest incoming request rate at which a chosen share—such as 90% or 99%—still meets both limits. It is not simply output tokens per second or the total number of requests accepted. This connects the user-facing promise to system capacity: the goal is to accept as much offered work as possible while keeping the selected fraction within bounds.',
            ],
            'sources': [(PDF + '#page=1', 'Conference paper, introduction and Figure 1'), (PDF + '#page=8', 'Conference paper, evaluation metric definition')],
        },
        {
            'title': 'A fixed priority can spend the wrong request’s budget',
            'paragraphs': [
                'Prefill and decode use the same limited GPU resources. If a scheduler favors new prompts, those requests may get their first token sooner, while tokens for existing requests wait longer. Favor decode and the existing responses may stream smoothly, while new arrivals wait to begin. Neither fixed choice can know, by itself, which requests have spare time and which are close to missing their limit.',
                'Use an invented example with a 5-second TTFT limit and a 1-second TPOT limit. Request A currently has TTFT 1.0 seconds and TPOT 1.2 seconds; request B has TTFT 2.0 seconds and TPOT 0.8 seconds. A misses only its token-spacing limit, while B passes both and has three seconds of TTFT slack. Suppose one scheduling change improves A’s TPOT to 0.9 seconds and adds 0.5 seconds to B’s TTFT. A now meets both limits, and B’s TTFT becomes 2.5 seconds, still within its limit. Under this toy assumption, the number of passing requests rises from one to two. This illustrates reassigning spare budget; it does not model SOLA’s optimizer or predict a real GPU schedule.',
                'The trade has limits. If the same change raised B’s TTFT to 5.1 seconds, A would be rescued while B would fail, leaving the count unchanged. If no request has slack, redistributing work may not rescue anyone. This is why the scheduler needs both request-level state and the system’s current state, rather than a universal “prefill first” or “decode first” rule.',
            ],
        },
        {
            'title': 'What SOLA observes and changes',
            'paragraphs': [
                'SOLA makes a scheduling decision at each serving iteration. Its state monitor updates individual request progress and system-wide information, including current queue and memory conditions. Its strategy generator chooses request order and workload size, then uses separate latency cost models for prefill and decode to estimate the effect. After an iteration completes, observed timings feed back into those models. The loop is: observe, estimate, choose, run, and update.',
                'The decision is more specific than “serve the oldest request” or “always finish decoding first.” For the next iteration, SOLA can decide which requests participate, whether prefill and decode work should be mixed, and how much input work to include. It also predicts peak memory before admitting a request, to avoid a later memory shortage that would force other requests to be swapped out or recomputed. These decisions connect current latency promises to request order, batch size, and memory use.',
                'The model is still an estimate. SOLA’s cost models are initialized from profiling and adjusted from observed latency; its memory and remaining-output calculations also rely on prediction. If those estimates are poor for a new model, prompt mix, or arrival pattern, the scheduler can choose badly. Feedback can correct estimates over time, but does not make them exact or remove the need to test a changed workload.',
            ],
            'sources': [(PDF + '#page=5', 'Conference paper, Figure 4 state-aware scheduling loop'), (PDF + '#page=7', 'Conference paper, implementation and cost-model sections')],
        },
        {
            'title': 'Keep the reported result attached to its test',
            'paragraphs': [
                'The paper evaluates SOLA on eight pairwise-connected NVIDIA A100 80 GB GPUs, using several open models and request sets that include ShareGPT and LongBench. It generates arrivals at random times with a stated average rate; this common test pattern is called a Poisson arrival model. Its comparisons include two vLLM scheduling variants and shortest-job-first, a policy that gives the request expected to need the least work priority. The paper reports that, averaged over its tested settings, SOLA accepts 1.08–1.27 times the request rate while keeping at least 90% of requests within their latency SLOs; for a 99% target, the increase is 1.04–1.11 times. The added scheduling overhead is reported as 0.40–0.45%.',
                'A figure gives a more concrete but narrower example: Llama 3 70B with ShareGPT on four A100 GPUs, a 4.6-request-per-second arrival rate, and limits of 500 ms for TTFT and 200 ms for TPOT. In that setting the paper’s figure shows attainment rising from 65% with vLLM’s default strategy to 98% with SOLA. These percentages are not universal, and the goodput ratios are not a guarantee for a different model, hardware, prompt-length mix, arrival process, SLO, or scheduling backend.',
            'A deployment check should replay its own arrival trace and record both first-token and per-token delays per request. Report the fraction meeting both limits and the maximum request rate that sustains the required fraction. Also compare queue length, memory pressure, and prediction errors, so a change in attainment has an interpretable cause. These are proposed checks, not new experiments performed by this course.',
            ],
            'sources': [(PDF + '#page=8', 'Conference paper, evaluation setup and summary'), (PDF + '#page=9', 'Conference paper, end-to-end results and scheduling-overhead table')],
        },
    ],
    'exercise': {
        'question': 'A service promises TTFT ≤ 4 seconds and TPOT ≤ 0.8 seconds. Three requests have measured pairs (TTFT, TPOT): A=(2.0, 1.0), B=(3.5, 0.7), C=(4.2, 0.6). How many meet both promises? A scheduling change moves A to (2.4, 0.75), B to (3.8, 0.7), and leaves C unchanged. How many now meet both? Why is that count not enough to prove the change improves capacity?',
        'answer': 'Initially only B meets both limits: A fails TPOT and C fails TTFT. After the change A and B meet both, so attainment rises from one of three requests to two of three in this toy sample. But the example does not report how many requests arrive per second, whether the sample represents future traffic, what resources were used, or how the change affects other requests and later iterations. To claim greater capacity, measure goodput under a stated arrival pattern and hardware while holding the SLO and request population comparable.',
    },
}
