"""Focused ASPLOS walkthrough of end-to-end orchestration for LLM applications."""

PDF = 'https://arxiv.org/pdf/2407.00326'

TEOLA = {
    'id': 'teola-2025',
    'route': 'asplos-2025',
    'title': 'Teola: schedule the whole LLM application, not only the model call',
    'identity': 'Xin Tan, Yimin Jiang, Yitao Yang, Hong Xu · Teola: Towards End-to-End Optimization of LLM-based Applications · ASPLOS 2025',
    'scope': 'A focused walkthrough of primitive-level workflow graphs, graph optimization, application-aware scheduling, topology-aware batching, and the reported evaluation. The authors’ arXiv full text was inspected. Results are author-reported and have not been reproduced here. The critical-path and batching calculations are original teaching models.',
    'lessons': [('s1', 'Whole-request timing'), ('s6', 'Execution plans'), ('queues-and-batching', 'Scheduling'), ('s10', 'Whole-system cost')],
    'blocks': [
        {
            'title': 'The model call is only one part of an LLM application',
            'paragraphs': [
                'A real LLM application may search a database, create embeddings, call an external tool, rerank documents, prefill a model, decode its answer, and judge or post-process the result. If the framework treats each module as a sealed box, it can optimize a model call while leaving the rest of the request waiting. The user experiences the total path, so the scheduler needs the total path too.',
                'Teola breaks a workflow into primitive operations and represents each query as a dataflow graph. A node says what work must happen; an edge says what result another node needs. The graph exposes independent branches that can overlap, partial results that can enter a later step before an earlier step is fully finished, and the shared engines that create queueing between requests.',
                'Original critical-path example: a sequential request spends 20 ms searching, 40 ms embedding, and 80 ms generating, for 140 ms. If search and embedding have an independent branch that can overlap for 20 ms, and generation starts after both finish, the path becomes max(20, 40) + 80 = 120 ms. The 20 ms saving is real only if the dependency is valid and the shared engine has capacity; overlap is not permission to run dependent work early.',
            ],
            'sources': [(PDF + '#page=1', 'Teola paper, abstract and introduction: non-LLM latency and primitive-level workflow graphs'), (PDF + '#page=3', 'Teola paper, workflow examples and coarse-grained orchestration limit')],
        },
        {
            'title': 'Graph rewrites expose parallelism but can add their own work',
            'paragraphs': [
                'Teola’s graph optimizer applies targeted passes to the primitive graph. It can parallelize independent operations, pipeline partial data, and decompose large operations such as embedding or prefilling when doing so makes the complete request finish sooner. The optimization is a change to the execution plan, not a claim that each individual primitive runs faster.',
                'Decomposition can reduce the critical path while hurting one operation. Partial prefilling may repeatedly move or prepare key–value state and may use the GPU less efficiently than one complete prefill. Teola reports that this slowdown is small in its tested cases, but the decision still requires a whole-path comparison. An optimizer must count the new communication, setup, and synchronization edges it creates.',
                'Original plan comparison: one complete operation costs 100 ms. Splitting it into two 55 ms pieces lets another 70 ms operation run during the first piece, but adds 8 ms of transfer and 5 ms of coordination. If the second piece and the other operation finish in 55 + 70 = 125 ms after the first starts, total time is 125 + 8 + 5 = 138 ms, worse than 100. If the other operation was otherwise on the critical path for 90 ms and overlaps fully, the same split can win. The graph must be recalculated with the actual dependencies.',
            ],
            'sources': [(PDF + '#page=5', 'Teola paper, graph optimizer and optimization passes'), (PDF + '#page=9', 'Teola paper, graph-optimization ablation and partial-prefill execution efficiency')],
        },
        {
            'title': 'A request scheduler must understand graph position, not just engine type',
            'paragraphs': [
                'Teola uses two scheduling levels. An upper level schedules each query’s execution graph. Lower-level engine schedulers batch primitives that use the same engine, while retaining their dependencies and relationships to the original queries. Two embedding operations may be compatible for a batch, but a primitive near the critical path may deserve different treatment from one with ample slack.',
                'Topology-aware batching uses graph depth and request correlations to decide which primitives to combine. A scheduler that only minimizes each invocation’s service time can make the overall application slower by causing later dependent work to wait. Conversely, a scheduler that always favors one request can damage throughput under load. The service objective must say whether it values per-request latency, average latency, goodput, or a combination.',
                'Original queue example: request A has a 10 ms embedding at depth 1 followed by 50 ms generation; request B has a 10 ms embedding at depth 4 followed by 5 ms post-processing. A shared embedding batch saves 4 ms of setup, but delaying A’s embedding by 8 ms delays its long critical path. If the batch starts immediately, total completion can be worse than running A first and batching B later. The graph position changes the value of the same engine operation.',
            ],
            'sources': [(PDF + '#page=6', 'Teola paper, two-tier runtime scheduler and primitive metadata'), (PDF + '#page=12', 'Teola paper, topology-aware batching ablation and latency effect')],
        },
        {
            'title': 'Read the result at the application and systems boundary',
            'paragraphs': [
                'Teola evaluates search-engine generation, document question answering with naive and advanced retrieval, contextual retrieval, and co-located applications. It compares against distributed LlamaIndex variants, module-parallelized baselines, and AutoGen under the paper’s resource allocations, datasets, model sizes, request rates, and engine implementations. The paper reports up to 2.09× lower end-to-end latency in its tested application settings, with separate gains across workflows.',
                'The paper’s ablations attribute the improvement to graph parallelization, pipelining, and topology-aware batching. It also reports graph-optimization overhead of about 1.3–3% with caching, communication overhead of about 3.1–6.2%, and a 3.11–12.12% slowdown for some decomposed prefilling cases before the gained overlap is counted. These numbers belong to the tested prototype and do not prove that any arbitrary workflow can be decomposed safely.',
                'Teola’s stated limitations matter: it assumes structured workflows known ahead of time, while autonomous agents can create new steps during execution; finer orchestration requires changes in engine-side mechanisms and reduces plug-and-play modularity. This walkthrough has not reproduced the Ray prototype or its testbed. Its teaching examples are not Teola measurements.',
            ],
            'sources': [(PDF + '#page=1', 'Teola paper, abstract: reported end-to-end speedup and application scope'), (PDF + '#page=11', 'Teola paper, application results, co-location, and ablations'), (PDF + '#page=13', 'Teola paper, overhead analysis and limitations')],
        },
    ],
    'exercise': {
        'question': 'A sequential application spends 20 ms searching, 40 ms embedding, and 80 ms generating. If search and embedding are independent and can overlap, what is the new critical-path time? What must you verify before claiming the saving?',
        'answer': 'The new critical path is max(20, 40) + 80 = 120 ms, versus 140 ms sequentially, so the teaching saving is 20 ms. Verify that the two operations truly have no dependency, that the shared engines have capacity, and that setup, data movement, queueing, and answer-quality requirements do not erase the saving. These are original teaching calculations, not Teola measurements.',
    },
}
