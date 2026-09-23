"""Focused ASPLOS walkthrough of full-coverage distributed trace compression."""

PDF = 'https://doi.org/10.1145/3669940.3707287'

MINT = {
    'id': 'mint-2025',
    'route': 'asplos-2025',
    'title': 'Mint: keep the evidence, store the repeated structure once',
    'identity': 'Haiyu Huang and colleagues · Mint: Cost-Efficient Tracing with All Requests Collection via Commonality and Variability Analysis · ASPLOS 2025',
    'scope': 'A focused walkthrough of trace sampling, common structure, variable fields, agent-side reduction, query coverage, and the reported overhead evaluation. The local primary source text was inspected. Results are author-reported and have not been independently reproduced here. The storage and query calculations are original teaching models.',
    'lessons': [('s5', 'Representation'), ('s8', 'Reliability'), ('s9', 'Cost accounting'), ('s10', 'Whole-system cost')],
    'blocks': [
        {
            'title': 'Discarding a request is not the same as compressing it',
            'paragraphs': [
                'A distributed trace records what one request did as it moved through many services. Tracing every request can consume large network and storage budgets, so common systems sample: keep some traces and discard the rest. Sampling reduces cost, but it creates a blind spot. The request that an engineer needs to inspect may be one of the requests that was discarded.',
                'Mint changes the unit of reduction. Instead of treating each trace as an indivisible object, it separates repeated structure from changing fields. The shared structure can be stored once; each request keeps a compact description of its differences. This aims to preserve coverage of all requests while reducing the bytes per request.',
                'Original storage model: 1,000 traces each contain 100 repeated fields and 10 variable fields. Storing every field independently requires 110,000 field units. If one template stores the 100 common fields once and each trace stores its 10 variables plus a 2-unit reference, the total is 100 + 1,000×12 = 12,100 units. The saving depends on the structure actually being common; a bad template can add references without removing repetition.',
            ],
            'sources': [(PDF, 'Mint paper, abstract and introduction: the 1-or-0 sampling problem and commonality-plus-variability design')],
        },
        {
            'title': 'Trace structure is not ordinary text',
            'paragraphs': [
                'A trace is a tree-like set of spans with parent–child relationships, timing, service identity, and request metadata. Two traces can have the same service path but different parameter values, timing, or optional branches. Mint analyzes commonality and variability at more than one level, then attaches per-request metadata to the common pattern. The representation must preserve enough structure to reconstruct or query the trace meaningfully.',
                'The system reduces data near the agent that generates the trace. That saves network traffic before the trace reaches the backend and reduces storage afterward. For sampled traces it retains the variable information needed for fuller analysis; for other traces it preserves the common structure and selected metadata instead of making the request disappear completely. The reduction policy therefore affects what a later query can answer.',
                'Original query model: suppose 100 requests share a service path but only 8 contain a rare error. A sampled system that keeps 10% at random has roughly a 0.9^8 ≈ 43% chance of missing all eight error traces. A full-coverage representation can retain an error flag for every request while storing the repeated path once. This probability is an original teaching calculation, not a Mint measurement or a claim about its sampling baseline.',
            ],
            'sources': [(PDF, 'Mint paper, sections 2–4: trace lifecycle, common/variable structure, agent-side processing, and retention policy')],
        },
        {
            'title': 'Compression must not become the new production bottleneck',
            'paragraphs': [
                'Agent-side parsing, template construction, parameter extraction, serialization, and filtering all consume CPU time. A representation that saves backend storage but delays the application is not automatically useful. The system must also account for network bytes, backend query work, reconstruction time, and the information that a query can still retrieve.',
                'Mint’s design therefore has several boundaries: what is recognized as common, which variable fields are retained, when a template changes, and how the backend joins the pieces. A trace can be small but unusable if its parent–child relationships or timestamps are lost. “All requests collected” means the request has a retained representation; it does not necessarily mean every original byte remains in every query path.',
                'Original end-to-end model: tracing adds 4 ms of agent work, 3 ms of network delay, and 2 ms of backend storage work. A compressed design raises agent work to 5 ms, cuts network delay to 1 ms, and storage to 0.5 ms. The overhead falls from 9 ms to 6.5 ms. If reconstruction adds 8 ms to every diagnostic query, the production request may still improve while the debugging query becomes slower; report both boundaries.',
            ],
            'sources': [(PDF, 'Mint paper, sections 3–5: agent-side reduction, storage/network path, query path, and overhead accounting')],
        },
        {
            'title': 'Keep coverage, storage, network, and latency as separate results',
            'paragraphs': [
                'The paper reports all-request trace collection with average storage overhead of 2.7%, average network overhead of 4.2%, and average end-to-end request-latency increase of 0.21% in its stated experiments. It reports query latency averaging 4.2% above OpenTelemetry with P95 below one second, and CPU increases of 0.86% versus no tracing and 0.39% below OT-Head. These numbers answer different questions and should not be combined into one compression ratio.',
                'The evaluation uses OnlineBoutique, TrainTicket, and Alibaba trace workloads with the stated sampling, anomaly-tagging, request-throughput, and deployment configurations. A storage reduction does not prove the same query completeness on another trace shape; a low request overhead does not prove low diagnostic-query latency. The paper’s result is author-reported and this course has not reproduced it.',
                'A fair follow-up should measure query recall for rare events, reconstructed trace fidelity, agent CPU, network bytes, storage bytes, request latency, query latency, and template-update behavior on the same workload. If a trace cannot answer the operational question that motivated tracing, its byte reduction is not sufficient evidence.',
            ],
            'sources': [(PDF, 'Mint paper, evaluation: OnlineBoutique, TrainTicket, Alibaba traces, overhead, query latency, and coverage boundary')],
        },
    ],
    'exercise': {
        'question': 'One thousand traces share 100 fields and each has 10 variable fields. Storing every field separately costs 110,000 units. A shared template costs 100 units, each trace stores 10 variable fields and a 2-unit reference. What is the new total and saving? What information must be checked before calling the representation equivalent for diagnosis?',
        'answer': 'The shared representation costs 100 + 1,000×(10+2) = 12,100 units, saving 97,900 units, or about 89%. Before calling it equivalent for diagnosis, check parent/child structure, timestamps, service identity, error fields, rare-event query recall, reconstruction behavior, and the complete agent-to-backend overhead. These are original teaching calculations, not Mint measurements.',
    },
}
