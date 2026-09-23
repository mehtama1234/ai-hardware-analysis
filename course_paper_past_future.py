"""Focused ASPLOS walkthrough of request admission under future KV-cache demand."""

ACM = 'https://doi.org/10.1145/3676641.3716011'
ARXIV = 'https://arxiv.org/pdf/2507.10150'

PAST_FUTURE = {
    'id': 'past-future-2025',
    'route': 'asplos-2025',
    'title': 'Past-Future: admit requests by checking the memory they may need next',
    'identity': 'Ruihao Gong, Shihao Bai, Siyu Wu, and colleagues · Past-Future Scheduler for LLM Serving under SLA Guarantees · ASPLOS 2025',
    'scope': 'A focused walkthrough of request-length prediction, future memory accounting, and the paper’s goodput evaluation. Detailed mechanism and experiment discussion were checked against the authors’ arXiv full-text version; this course has not reconciled every passage with the ACM camera-ready copy. Results are author-reported, not independently reproduced. The memory timeline is an original teaching model.',
    'lessons': [('s1', 'Requests, waiting, and throughput'), ('s3', 'Memory and movement'), ('s5', 'Scheduling'), ('s10', 'Whole-request cost')],
    'blocks': [
        {
            'title': 'A request consumes memory as it generates text',
            'paragraphs': [
                'A language model does not only need room for its fixed model weights. While it generates a reply one token at a time, it also stores intermediate attention values for the prompt and the text already generated. This growing per-request memory is called the key–value cache, or KV cache. If too many requests are admitted at once, their combined cache can exceed GPU memory and force the system to stop, evict, or restart requests that were already in progress.',
                'Continuous batching lets a service add new requests between generation steps instead of waiting for every current request to finish. That improves use of the GPU, but creates a decision: can the new request fit not only now, but while existing replies continue growing and some requests finish? Current free memory answers only the first question. It does not reveal the batch’s future peak.',
            ],
        },
        {
            'title': 'Too cautious wastes room; too aggressive breaks work already started',
            'paragraphs': [
                'A cautious scheduler can reserve enough memory for every request to reach its maximum allowed reply length. That avoids some memory failures, but holds space that many requests will never use. The waiting line grows, so some requests miss the time limit for receiving their first token. An aggressive scheduler can instead admit requests based mostly on their prompts and current use. It fits more work at first, but if replies grow longer than expected, running requests may be evicted and have to wait or restart, missing limits on token delivery.',
                'The objective is not simply “put the most requests on the GPU.” The paper calls request rate under its service promises goodput. It tracks whether each request receives its first token and subsequent tokens quickly enough, not merely how many tokens the GPU emits in total. A scheduler that creates more raw throughput but causes many requests to miss their limits may complete more work while meeting fewer service promises.',
            ],
        },
        {
            'title': 'Use recent replies to estimate lengths, then walk the future timeline',
            'paragraphs': [
                'Past-Future uses output lengths from recently completed requests to estimate the length pattern of requests now waiting. It does not need to guess every future reply perfectly. For requests already running, it updates each estimate using how much that request has generated so far. The authors found adjacent time windows often had similar output-length patterns in the chat, code, and service traces they examined. Their implementation uses a recent window of about 1,000 requests; when a service first starts, it begins with the preset maximum output length and updates as requests complete.',
                'It then predicts memory use at the future points when requests may finish or grow. The scheduler checks the highest predicted memory demand over that timeline, including the candidate request, against available GPU memory. This matters because an early point can be the peak even if memory later falls as requests end. Admission based only on the final memory value can miss a temporary overflow.',
                'Original teaching model: a GPU has 100 memory units available. With the current batch, predicted memory at three future checkpoints is 84, 96, and 72. A waiting request adds 10, 4, and 4 units at those same checkpoints. The combined path is 94, 100, and 76, so it has no predicted overflow. A different request adding 10, 8, and 4 would produce 94, 104, and 76; it must wait, even though the last checkpoint is below capacity. The model illustrates why the maximum across time—not just current use or eventual use—sets the admission limit in this model. It is not the paper’s workload or its algorithm’s exact arithmetic.',
                'A forecast used for admission is neither a reservation of future GPU memory nor a guarantee of a request’s eventual length. It is a calculation based on the history and progress known when the scheduler decides. A changed request mix or an unusually long reply can make actual demand differ from the timeline, so evictions and missed service limits remain outcomes to measure. The paper’s goal is to reduce that risk and queueing under its traces and service rules, not to make capacity uncertainty disappear.',
            ],
            'sources': [(ARXIV, 'Authors’ full-text arXiv version, sections 3.1–3.3: recent output lengths and future memory estimates'), (ACM, 'ASPLOS 2025 proceedings record and published abstract')],
        },
        {
            'title': 'Measure accepted service and keep the workload attached to the result',
            'paragraphs': [
                'The paper evaluates 7B and 13B models on one A100-80GB GPU and a 70B model on four A100 GPUs connected by NVLink. Its service limits require 99% of requests to receive the first token within 10 seconds and keep their maximum gap between output tokens below 1.5 seconds for 7B/13B; the 70B limits are 15 seconds and 5 seconds. These are the paper’s tested limits, not general definitions of acceptable response time.',
                'In the authors’ published abstract, LightLLM with Past-Future reports up to two to three times the goodput of the compared schedulers under heavy load. The full-text comparison says it tests several request-length distributions and compares against conservative and aggressive scheduler implementations. A footnote says the framework comparison uses versions from December 2023 and that the frameworks have since changed substantially. Treat the headline as a bounded comparison with those versions, model settings, hardware, traces, and SLA rules; it is not a current ranking of all serving systems.',
                'The prediction depends on recent replies resembling near-future replies. The authors use an initial conservative maximum-output setting until the history fills in, but a sudden change in request mix can make the old window misleading. A useful deployment check should watch prediction error and SLA misses after such changes, and should keep first-token delay, token gaps, evictions, and raw throughput visible as separate measurements.',
            ],
            'sources': [(ARXIV, 'Authors’ full-text arXiv version, sections 5.1–5.4: models, SLA limits, evaluation, and baseline-version note'), (ACM, 'ASPLOS 2025 published abstract: reported goodput result and paper scope')],
        },
    ],
    'exercise': {
        'question': 'In the teaching timeline, a candidate request adds 10, 8, and 4 memory units to predicted uses of 84, 96, and 72. What is the peak combined use? Should the request be admitted if capacity is 100? Why is checking only the final point unsafe?',
        'answer': 'The combined values are 94, 104, and 76; the peak is 104, so the request should wait. The final value is only 76, but memory exceeds capacity at the middle checkpoint, before enough existing requests finish. This is arithmetic in the teaching model, not a measurement or reproduction of Past-Future.',
    },
}
