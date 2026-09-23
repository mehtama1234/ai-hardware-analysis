"""Focused ASPLOS walkthrough of predictable expert use under limited memory."""

PAPER = 'https://doi.org/10.1145/3676641.3715986'
ARXIV = 'https://arxiv.org/abs/2503.02354'

COSERVE = {
    'id': 'coserve-2025',
    'route': 'asplos-2025',
    'title': 'CoServe: use known expert needs to avoid needless model swaps',
    'identity': 'Jiashun Suo and colleagues · CoServe: Efficient Collaboration-of-Experts (CoE) Model Inference with Limited Memory · ASPLOS 2025',
    'scope': 'A focused walkthrough of predictable expert dependencies, request grouping, eviction, heterogeneous CPU/GPU allocation, and the reported evaluation. The primary arXiv record and publication record were inspected. Results are author-reported and have not been independently reproduced here. The queue and memory calculations are original teaching models.',
    'lessons': [('s1', 'Follow one request'), ('s3', 'Memory'), ('queues-and-batching', 'Scheduling'), ('s10', 'Whole-system cost')],
    'blocks': [
        {
            'title': 'The expert-selection signal is known before the request runs',
            'paragraphs': [
                'Suppose an edge device runs many small specialist models. One inspection request may need expert A followed by expert C; another may need B followed by C. If the GPU cannot hold all experts, the system loads them from CPU memory or storage. Loading a model is much slower than applying a model that is already resident, so a scheduler that ignores the next expert can spend most of its time moving models rather than using them.',
                'CoServe targets Collaboration-of-Experts, where the route through the specialist models is known before execution. That is different from a Mixture-of-Experts model whose router chooses experts from the current activation while the request is running. Knowing the future route does not make loading free, but it gives the system a fact it can use: requests with compatible next experts can be placed near one another, and an expert that will be needed soon should not be evicted casually.',
                'Original request model: request R1 needs A then C, R2 needs B then C, and R3 needs A then C. With one expert slot, first-come-first-served loads A, B, and A again before the C steps, causing three swaps. If the route is known and requests may be reordered, R1 and R3 can share A, then R2 uses B, then all three can use C if their stages are arranged accordingly. The exact saving depends on the number of slots, stage order, and whether reordering changes the service promise.',
            ],
            'sources': [(ARXIV, 'CoServe abstract: limited-memory expert switching, dependency-aware scheduling, and known expert dependency'), (PAPER, 'ASPLOS publication record: venue and reported throughput result')],
        },
        {
            'title': 'Grouping requests trades fairness for fewer transfers',
            'paragraphs': [
                'A dependency-aware scheduler groups requests that need the same expert within a queue window. Keeping an expert resident across that group can remove repeated loads. But reordering is not free: a request that arrived first may wait behind a compatible request, and the queue window itself adds delay. A good scheduler therefore has two obligations—reduce movement and preserve the latency or ordering promise given to users.',
                'When the device has both CPU and GPU execution lanes, assigning work only by shortest queue can also be misleading. A lane with a short queue may still need to load a large expert, while a busier lane may already have the required expert in memory. The decision should include the next transfer and execution time, not only the number of waiting requests.',
                'Original queue model: request A waits 1 unit for its already-loaded expert and request B waits 6 units for a swap. Serving A first then B costs 1 + 6 = 7 units. If B is followed by two more requests needing that same expert, grouping B with them costs 6 + 1 + 1 = 8 units and lets those three requests share the swap; serving them separately would cost 6 + 6 + 6 = 18 for their transfer portions. The grouping is worthwhile for total work, but the first request in the group still needs an explicit waiting rule.',
            ],
            'sources': [(ARXIV, 'CoServe abstract: dependency-aware request scheduler on heterogeneous CPU and GPU'), (PAPER, 'CoServe publication record: paper identity and source boundary')],
        },
        {
            'title': 'Eviction needs both immediate space and future usefulness',
            'paragraphs': [
                'When a new expert does not fit, the system must choose what to remove. A rule based only on recent use can keep a small expert that is used once per request while leaving a large expert that will never be needed in the next window. CoServe uses dependency information to identify experts that cannot be used soon, first considers how much space an eviction frees, and then uses offline usage probabilities to guide later choices. The order matters because freeing enough space may require removing one large model instead of several small ones.',
                'This is a prediction-driven policy, not a guarantee. The offline probabilities describe the workload used to build them. If the route distribution changes, an expert marked unlikely may become common, and the policy can cause more swaps. The system must also account for the cost of finding and loading the replacement; an eviction that creates space but immediately triggers another transfer may not improve the request path.',
                'Original eviction model: GPU memory has 10 units free, while a requested expert needs 7. Resident expert X uses 8 units and is unlikely in the next window; resident experts Y and Z use 4 units each and are both likely. Evicting X frees enough space in one action. Evicting Y and Z would free 8 units but removes two useful experts and performs two management actions. If X is actually needed by the next three requests, the prediction was wrong and the apparent saving reverses into extra reloads.',
            ],
            'sources': [(ARXIV, 'CoServe abstract and primary record: dependency-aware expert management and offline profiling'), (PAPER, 'ASPLOS publication record: primary citation')],
        },
        {
            'title': 'Tune the memory split with measurements, then read the result at its boundary',
            'paragraphs': [
                'Memory is shared between resident experts, input and output batches, and execution buffers. Giving every available byte to resident experts can reduce swaps but leave too little room to process a batch; giving too much to batches can force constant expert movement. CoServe profiles the target device before serving and uses those measurements to choose a CPU/GPU allocation and executor configuration. This makes the allocation a measured decision for a device, not a universal fixed percentage.',
                'The paper reports 4.5×–12× higher throughput than Samba-CoE on real intelligent-manufacturing workloads and reports up to a 93.87% reduction in expert switching in its evaluated setting. The source record describes more than 300 ResNet101/YOLOv5 experts totaling about 60 GB being served on a 12 GB RTX 3080Ti-class GPU. These numbers are tied to the circuit-board inspection tasks, expert models, devices, baselines, and route distributions in the evaluation. They do not establish the same gain for runtime-routed language models or changing route distributions.',
                'A complete comparison should report request latency as well as throughput, the fraction of requests meeting any deadline, expert-load bytes, CPU/GPU utilization, and the cost of profiling. It should also test a route distribution that differs from the profiling history. A system can process more requests per second while making a particular request wait longer; these are separate service results.',
            ],
            'sources': [(ARXIV, 'CoServe primary record: 4.5×–12× throughput claim, workload description, dependency-aware mechanisms, and evaluation boundary'), (PAPER, 'ASPLOS publication record: related publication')],
        },
    ],
    'exercise': {
        'question': 'An invented device has one free memory slot. Three requests need experts A, B, and A, respectively. Loading any new expert costs 5 units; running a resident expert costs 1. If requests may be reordered and no deadline is violated, what is the transfer and execution cost when A requests are grouped? What additional evidence is needed before claiming that grouping improves the service?',
        'answer': 'Group the two A requests: load A once, then run A twice, for 5 + 1 + 1 = 7 units; load B and run it for another 5 + 1 = 6, for 13 total. In arrival order, A, B, and A cost 5+1 + 5+1 + 5+1 = 18. The teaching model assumes one slot, no overlap, and free reordering. A real claim must check request latency and deadlines, queue-window delay, expert sizes, CPU/GPU overlap, profiling cost, route changes, and the paper’s workload boundary. These are original teaching calculations, not CoServe measurements.',
    },
}
