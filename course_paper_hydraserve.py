"""Focused NSDI walkthrough of HydraServe's serverless LLM cold-start path."""

PDF = 'https://www.usenix.org/system/files/nsdi26-lou.pdf'

HYDRASERVE = {
    'id': 'hydraserve-2026',
    'route': 'nsdi-2026',
    'title': 'HydraServe: make a cold worker useful before every stage is finished',
    'identity': 'Chiheng Lou, Sheng Qi, Chao Jin, and colleagues · HydraServe: Minimizing Cold Start Latency for Serverless LLM Serving in Public Clouds · NSDI 2026',
    'scope': 'A focused walkthrough of the cold-start path, pipeline worker creation, stage overlap, worker placement, consolidation, and reported evaluation. The final USENIX paper was inspected. Results are author-reported and have not been reproduced here. The schedules and cost calculations are original teaching models.',
    'lessons': [('s1', 'Whole-request timing'), ('dependencies-and-pipelines', 'Overlap and dependencies'), ('s3', 'Movement costs'), ('queues-and-batching', 'Service promises'), ('s10', 'Complete-path evidence')],
    'blocks': [
        {
            'title': 'A cold start is a chain, not one download',
            'paragraphs': [
                'A serverless model worker may be created only when a request arrives. Before it can produce the first token, the platform must create a container, load libraries, initialize the CUDA context, fetch model weights, load them into GPU memory, and run inference. Time-to-first-token (TTFT) measures the wait until that first token. Time per output token (TPOT) describes the later stream. A cold-start optimization must say which of these it changes.',
                'HydraServe’s paper gives a production-style example in which a first token takes more than 40 seconds while later generation takes about 30 milliseconds per token. Its breakdown makes model fetching the largest stage under the stated setup, but container and library work also consume time. Removing only the largest stage cannot reduce the complete path below the remaining stages. The system therefore treats startup as a dependency graph rather than as a single bandwidth number.',
                'Original timing model: container creation takes 4, library loading 3, model fetch 10, model load 5, and first inference 1 second. Sequential cold start is 23 seconds. If library loading and model loading are independent after CUDA initialization, overlap changes the middle portion from 3+5 to max(3,5), reducing total time to 18. If model loading depends on fetch completion, that fetch cannot be overlapped with loading. A claimed overlap must name both the dependency and the resource.',
            ],
            'sources': [(PDF + '#page=3', 'NSDI paper, section 2.2 and figures 1–2: cold-start stages and reordered workflow')],
        },
        {
            'title': 'Use several workers to fetch one model, then pay for consolidation',
            'paragraphs': [
                'A single server may have too little bandwidth to fetch a large model quickly. HydraServe partitions model layers across workers on different servers, so the workers fetch different portions in parallel and pass intermediate results through a pipeline. This can make the first request useful before any one worker holds the entire model. It changes the startup path from one long fetch to several shorter fetches plus pipeline communication.',
                'The temporary arrangement is not the final serving arrangement. A pipeline worker initially owns only part of the model. HydraServe lets it continue loading the missing layers while serving, then consolidates the group into standalone workers. It migrates the key–value cache and can release extra workers or retain them according to later load. Startup capacity and steady-state capacity are therefore different states; counting every startup worker as permanent capacity would overstate resource use.',
                'Toy example: one worker fetches 100 GB over a 20 GB/s path, taking 5 seconds, then needs 1 second to load. Four workers fetch 25 GB each over separate 20 GB/s paths, so fetch takes 1.25 seconds; assume 0.4 seconds of pipeline communication and 1 second of loading. The first result can arrive after 2.65 seconds under these assumptions. If the paths share one 20 GB/s bottleneck, the four workers do not get four times the bandwidth. Placement and contention determine whether parallel fetching is real.',
            ],
            'sources': [(PDF + '#page=2', 'NSDI paper, section 1: pipeline parallelism and consolidation motivation'), (PDF + '#page=4', 'NSDI paper, section 3: three-level HydraServe architecture and request migration')],
        },
        {
            'title': 'Choose placement from the SLO and the shared network',
            'paragraphs': [
                'HydraServe makes a cluster-level decision about how many pipeline workers to create and where to place them. More workers can shorten model fetching, but they use more GPUs and can compete for network bandwidth with other cold starts. The controller estimates TTFT and worst-case TPOT and uses the user’s service-level objective when selecting resources. A placement that looks fast in isolation can miss the SLO when neighboring workers share the same link.',
                'At the worker level, HydraServe prefetches model data, overlaps remote-to-host fetch with container and runtime preparation, loads the GPU while libraries load on the CPU, and pipelines fetching and loading at tensor granularity. These stages do not all become free: the design has to provide separate resources, buffers, and a safe point at which a partially loaded worker may serve. At the inference level, state migration connects temporary pipeline execution to the standalone worker that takes over.',
                'Suppose the SLO is TTFT at most 10 seconds. A one-worker plan has 12 seconds of fetch and 2 seconds of other startup, so it fails. A two-worker plan halves fetch to 6 seconds but adds 1 second of pipeline communication and 1 second of placement overhead, totaling 10. A four-worker plan halves fetch again to 3 seconds but adds 4 seconds of shared-link contention, totaling 9. Both meet the SLO, but the four-worker plan may consume more cost or harm another model. Meeting one request’s limit is not the same as improving system capacity.',
            ],
            'sources': [(PDF + '#page=4', 'NSDI paper, sections 3 and 4: controller, placement, and overlap'), (PDF + '#page=5', 'NSDI paper, Figure 5 and tradeoff analysis: pipeline size, TTFT, TPOT, and cost')],
        },
        {
            'title': 'Read the result at the cold-start and steady-state boundaries',
            'paragraphs': [
                'The paper reports that HydraServe reduces cold-start latency by 1.7×–4.7× and improves SLO attainment by 1.43×–1.74× against its baselines. It also reports an average 2.6× latency reduction in a brownfield evaluation. These are not one universal speedup: the values depend on model, workload, worker placement, pipeline size, SLO, and the comparison system.',
                'The evaluation includes testbed and production settings. It measures startup and later inference separately because a pipeline that helps the first token can add communication or sharing cost to later tokens. Pipeline consolidation and key–value-cache migration are part of the complete path; a benchmark that stops after the first stage would miss their cost. Likewise, resource consumption and the number of temporary workers matter for serverless economics, not just TTFT.',
                'A deployment check should replay its own burst pattern, record TTFT and TPOT per request, count SLO attainment, and charge model prefetch, worker startup, migration, and extra GPU time. The course has not rerun HydraServe. This walkthrough preserves the paper’s tested boundaries and uses invented schedules to teach the dependency and break-even reasoning.',
            ],
            'sources': [(PDF + '#page=2', 'NSDI paper, section 1: reported latency and SLO results'), (PDF + '#page=14', 'NSDI paper, evaluation sections: testbed, production, and brownfield boundaries')],
        },
    ],
    'exercise': {
        'question': 'A one-worker cold start fetches 100 GB at 20 GB/s and then loads for 1 second. A four-worker plan fetches 25 GB per worker over separate links, adds 0.4 seconds of pipeline communication, and has the same 1-second load stage. What are the two startup times under the teaching assumptions? What missing fact could invalidate the four-worker saving?',
        'answer': 'The one-worker fetch takes 5 seconds, so startup is 6 seconds. Four workers fetch in 1.25 seconds, then the assumed communication and loading give 1.25 + 0.4 + 1 = 2.65 seconds. Shared bandwidth, synchronized stage dependencies, GPU contention, or the cost of consolidating the workers could invalidate that result. These are original teaching numbers, not HydraServe measurements.',
    },
}
