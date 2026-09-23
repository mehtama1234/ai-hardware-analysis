"""Focused DAC walkthrough of SLO-aware prefill/decode multiplexing."""

PAPER = 'https://arxiv.org/pdf/2606.16264'
DOI = 'https://doi.org/10.1109/DAC63849.2025.11132617'

TROPICAL = {
    'id': 'tropical-2025',
    'route': 'dac-2025',
    'title': 'Tropical: spend spare decode time without breaking either latency promise',
    'identity': 'Jinming Ma and colleagues · Tropical: Enhancing SLO Attainment in Disaggregated LLM Serving via SLO-Aware Multiplexing · DAC 2025',
    'scope': 'A focused walkthrough of prefill/decode interference, queuing, slack, SLO-aware multiplexing, and the reported serving evaluation. The locally extracted manuscript was inspected through the definitions, workload characterization, scheduler design, and evaluation. Results are author-reported and have not been independently reproduced here. The queue schedules and latency arithmetic below are original teaching models, not measurements or a reimplementation.',
    'lessons': [('queues-and-batching', 'Deadlines and demand'), ('dependencies-and-pipelines', 'Phases'), ('s4', 'Routes'), ('s10', 'Complete request cost')],
    'blocks': [
        {
            'title': 'One request has two different latency promises',
            'paragraphs': [
                'Large-language-model serving has a front half and a repeating back half. Prefill reads the prompt and prepares the state needed to begin answering. Decode uses that state to produce one more output token at a time. A user cares about both the time until the first token and the gaps between later tokens. A system that improves one while damaging the other has not solved the whole request.',
                'Time-to-first-token, or TTFT, runs from request arrival to the first output. Time-per-output-token, or TPOT, measures the average delay between generated tokens. Tropical treats a request as meeting its service-level objective only when both conditions hold. Passing one condition does not compensate for failing the other. This is why one average latency number can hide the user-visible failure.',
                'Original teaching timeline: a request arrives at time 0, prefill takes 4 ms, and its first token arrives at 4 ms. Four later tokens take 2 ms each, so the average TPOT is 2 ms. If a scheduling change makes prefill take 3 ms but the token gaps become 5 ms, TTFT improves by 1 ms while TPOT worsens from 2 to 5. If the two limits are TTFT ≤ 4 and TPOT ≤ 3, the changed schedule fails even though its first token is earlier.',
            ],
            'sources': [(PAPER, 'Manuscript sections I–II: prefill/decode phases, TTFT, TPOT, SLO attainment, and slack')],
        },
        {
            'title': 'Separate workers trade interference for a queue',
            'paragraphs': [
                'If prefill and decode share a worker, a long prompt can interrupt token generation. That lowers TPOT. If they use separate workers, decode is protected from prefill, but all prompts must wait for the capacity assigned to prefill. That raises TTFT when prompt arrivals are uneven. The two arrangements move the cost; neither removes it.',
                'Original queue model: two workers serve a stream of prompts and token generation. In a shared-worker design, a prompt takes 6 ms and blocks an ongoing decode step for 4 of those milliseconds; the prompt starts quickly but the token gap grows. In a separated design, the decode worker never sees that prompt, but the prefill worker has one 6-ms slot and three prompts arrive together. Their starts are 0, 6, and 12 ms, so the third prompt waits 12 ms before its own 6-ms work. A protected token stream and a long prompt queue are both real costs.',
                'Static worker ratios create another problem. Short prompts need little prefill capacity, while long prompts need much more. A ratio that fits one arrival mix can leave one worker overloaded while another sits idle when the mix changes. Switching roles can help, but moving state or recomputing it can itself violate token timing. The scheduling problem is therefore about current phase, queue, state, and deadline—not merely assigning a fixed number of GPUs to each label.',
            ],
            'sources': [(PAPER, 'Manuscript sections II-A and III-B–III-D: non-disaggregated interference, disaggregated queuing, workload variation, and static allocation limits')],
        },
        {
            'title': 'Use slack as a bounded permission to share a worker',
            'paragraphs': [
                'A decode step may finish sooner than its TPOT limit requires. The unused time is slack. Tropical uses it as a budget for a short prefill on a worker that is normally serving decode; this is its SLO-aware multiplexing rule, and it acts only when the predicted prefill work fits inside the available budget. The idea is not “run more work whenever the device is idle.” It is “borrow only the time that can be spent without crossing the stated deadline.”',
                'Original slack calculation: a decode step normally takes 3 ms, while its TPOT limit allows 5 ms. The available slack is 2 ms. A prefill predicted to take 1.5 ms can be inserted if switching and other stated costs are zero. A 2.5-ms prefill cannot: it would make the step 5.5 ms. If entering and leaving the prefill costs 0.25 ms each, even the 1.5-ms prefill needs 2 ms total and exactly consumes the budget. Any prediction error then creates risk.',
                'Tropical’s scheduler records worker state, queues, predicted prefill time, predicted local queue time, decode timing, and memory use. It can send a prompt to a normal prefill worker when the predicted wait plus execution fits the TTFT slack. It can send a prompt to a multiplexing worker only when the added work fits the decode slack and the worker is below relevant resource thresholds. Chunking a long prompt limits the size of one interference event, but it does not make that interference disappear.',
            ],
            'sources': [(PAPER, 'Manuscript section IV: SLO-aware multiplexing, slack checks, worker state, queue prediction, memory thresholds, and chunked prefill')],
        },
        {
            'title': 'Measure joint success, not a favorable phase in isolation',
            'paragraphs': [
                'The natural end-to-end result is the fraction of requests that meet both limits. If 90 of 100 requests meet TTFT but only 80 meet TPOT, at most 80 can meet both; the two percentages cannot be added. A scheduler may improve TTFT by using decode workers for prompts and still reduce the number of requests whose token gaps stay within their limit. The joint count is the service result.',
                'The paper reports its evaluation on the Mooncake long-context trace using InternLM-20B and eight A100 80GB GPUs. It compares Tropical with non-disaggregated serving, chunked prefill, and disaggregated serving. The paper reports up to 2.09× more requests within a 90% SLO-attainment target and a 9× P90 TTFT improvement against its disaggregated comparison, with a 15% reduction in P90 TPOT. Against non-disaggregated serving, it reports 2.8× better P90 TPOT at the same P90 TTFT. These values belong to the stated trace, model, hardware, baselines, and SLO setup.',
                'A fair follow-up would vary prompt length, output length, arrival burstiness, slack threshold, prediction error, and worker ratio while retaining the same joint SLO definition. It should report TTFT, TPOT, queue time, interference time, joint attainment, and resource use together. This course does not run that experiment; the paper’s numbers remain author-reported and should not be read as a universal serving guarantee.',
            ],
            'sources': [(PAPER, 'Manuscript sections V and conclusion: testbed, workload, baselines, SLO-attainment results, queueing/interference analysis, and evidence boundary'), (DOI, 'Official DAC 2025 publication record: paper identity and venue')],
        },
    ],
    'exercise': {
        'question': 'A decode step takes 3 ms and has a 5-ms TPOT limit. Inserting a prefill takes 1.5 ms, and entering and leaving it each costs 0.25 ms. Does the insertion fit within the decode slack? Separately, if 92 requests meet TTFT and 84 meet TPOT, what is the largest possible number that meet both?',
        'answer': 'The decode slack is 5 − 3 = 2 ms. The insertion costs 1.5 + 0.25 + 0.25 = 2 ms, so it exactly fits the teaching model; any unmodeled delay or prediction error would remove the margin. At most 84 requests can meet both because the joint set cannot be larger than the smaller individual set. These are original calculations, not Tropical measurements.',
    },
}
