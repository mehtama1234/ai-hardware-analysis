"""Focused OSDI walkthrough of end-to-end cold-start latency."""

PDF = 'https://www.usenix.org/system/files/osdi25-chai-xiaohu.pdf'

AFAAS = {
    'id': 'afaas-2025',
    'route': 'osdi-2025',
    'title': 'Fork in the Road: find the work hidden inside a cold start',
    'identity': 'Xiaohu Chai and colleagues · Fork in the Road: Reflections and Optimizations for Cold Start Latency in Production Serverless Systems · OSDI 2025',
    'scope': 'A focused walkthrough of the paper’s cold-start cost breakdown, staged optimizations, and production comparison. The measurements below are reported by the authors and have not been reproduced here. The small cost model is an original teaching example, not a measurement or reimplementation.',
    'lessons': [('s4', 'Routes and message paths'), ('s6', 'Whole-system cost'), ('s10', 'End-to-end completion')],
    'blocks': [
        {
            'title': 'A cold start is a journey, not one operation',
            'paragraphs': [
                'A serverless function can be fast once it is running and still answer slowly on its first request. Before useful code can respond, the platform must notice the request, arrange a worker, set up an isolated environment, and initialize the language runtime and application code. After that, the function still has to do its actual work. A warm start reuses some already prepared state; a cold start pays more of this setup again.',
                'Keep the clocks separate. “Startup latency” may stop when the function is ready, while an end-to-end timer includes more of the path through the response. In this paper, that timer starts when a server node receives a scaling request from the scheduler or auto-scaler and ends when the function sends its response. It does not automatically include time before that scaling request, such as an earlier client-to-scheduler delay. A system can improve startup and barely change the paper’s end-to-end time when the function itself does most of the work. The reverse can also happen: a faster request path may matter greatly for a tiny function. The paper’s central move is to measure the stated full path and ask which part is delaying the caller.',
            ],
            'sources': [(PDF + '#page=4', 'Conference paper, section 2.1: stated end-to-end timing boundary')],
        },
        {
            'title': 'The paper finds three different sources of delay',
            'paragraphs': [
                'The authors separate cold-start delay into control-path work, resource contention, and user-code initialization. Control-path work is the platform’s own sequence of decisions and coordination before execution. Resource contention is extra waiting when concurrent starts compete for shared machine resources. User-code initialization is work such as loading modules and preparing application state. These costs are not fixed shares: a short function and a module-heavy function can have different bottlenecks, and concurrent arrivals can change the breakdown again.',
                'This breakdown changes how to investigate a slow start. Timing only the function body misses all three setup costs. Timing only container creation misses platform coordination and application initialization. A complete measurement marks the request, readiness, first application execution, and response boundaries, then records enough internal events to locate the added delay. Percentiles and concurrency matter: an average from isolated runs cannot describe a busy platform’s tail behavior.',
            ],
            'sources': [(PDF + '#page=3', 'Conference paper, sections 2–3: cold-start gaps and cost breakdown')],
        },
        {
            'title': 'Follow the staged baseline to see what each change buys',
            'paragraphs': [
                'The evaluation builds up from CataOnly, a Catalyzer baseline with other platform-level optimizations excluded. CataOPT1 adds the resource-contention optimization. CataOPT2 adds the control-path optimization to CataOPT1. AFaaS then adds the user-code-initialization optimization. This sequence isolates one named cost at a time while showing its effect on the whole function path. It is not valid to add the separate percentage gains as if they were independent: later changes run in a system already altered by earlier ones.',
                'The mechanisms include reducing control-path work, sharing resources or namespaces to reduce contention, preparing security setup in advance, and using seed states at different levels to reduce repeated initialization. Reuse has a cost: prepared state occupies memory, and a system must decide how much state to retain and for how long. The paper therefore reports memory as well as latency; faster setup is not free capacity.',
                'Teaching model—not paper data: suppose a request takes 12 ms in platform setup, 8 ms in isolation setup, 60 ms in code initialization, and 20 ms in useful execution. Total response time is 100 ms. Cutting isolation setup from 8 ms to 2 ms saves 6 ms, not 75 ms, because the other stages remain. If code initialization instead falls from 60 ms to 10 ms, the new total is 50 ms. These sums assume stages occur one after another; real systems may overlap some work, so actual traces must establish the boundaries.',
            ],
            'sources': [(PDF + '#page=7', 'Conference paper, section 6.1: staged comparisons and test setup'), (PDF + '#page=8', 'Conference paper, sections 3–5: optimization mechanisms and seed levels')],
        },
        {
            'title': 'Read the result with its workload and comparison attached',
            'paragraphs': [
                'The paper first tests representative functions from Function-Bench and SeBS on a 24-core Xeon Platinum 8163 server with 512 GB of memory. Its graphs report both average end-to-end delay and the 99th-percentile delay: a threshold near the point where 99% of the measured requests have finished. The remaining requests can take longer; this threshold does not describe their average or maximum delay. The graphs include sequential and concurrent conditions. For longer-running functions, startup savings form a smaller share of the response; the authors report only 1.05×–1.14× average improvements in one longer-execution group. This limits the headline: removing setup does not remove application work.',
                'The production study compares AFaaS with CataOnly for eight representative Node.js functions at Ant Group. AFaaS latency is measured on the production server over one day; CataOnly is tested on the same hardware with peer-call responses mocked. The paper reports 1.80×–8.14× end-to-end speedup and 5.45–9.41 ms startup latency. The authors explain that the function with more execution work gains less, while reduced module loading helps another gain more. Because the comparison includes mocked peer calls for CataOnly, and concerns one platform and a selected set of functions, these values are not a universal serverless guarantee or a like-for-like replay of every production interaction.',
                'When comparing another platform, match the function and dependency set, cold versus warm definition, arrival concurrency, request and response boundaries, peer-service behavior, hardware, and percentile. Report memory consumed by retained seeds beside latency. Without those conditions, a single “cold-start speed” number can hide a changed workload or a moved cost.',
            ],
            'sources': [(PDF + '#page=7', 'Conference paper, sections 6.1–6.2: benchmark machine, functions, and latency'), (PDF + '#page=11', 'Conference paper, section 6.6 and Figure 18: production comparison and its boundary')],
        },
    ],
    'exercise': {
        'question': 'In the teaching model, a function spends 15 ms in platform setup, 10 ms in isolation setup, 45 ms initializing its code, and 30 ms executing. What is its end-to-end time? If code initialization is reduced to 15 ms, what is the new time and speedup? Why should that speedup not be promised for a function that executes for 300 ms?',
        'answer': 'The original total is 15 + 10 + 45 + 30 = 100 ms. The new total is 15 + 10 + 15 + 30 = 70 ms, so the speedup is 100/70, about 1.43×. If execution instead takes 300 ms, the total changes from 370 ms to 340 ms, about 1.09×. The same setup saving is a smaller share of a longer request. This is arithmetic in the teaching model, not a result measured by AFaaS.',
    },
}
