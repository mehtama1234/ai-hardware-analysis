"""Focused ASPLOS walkthrough of tracing overhead, coverage, and accuracy."""

PDF = 'https://cs.sjtu.edu.cn/~lichao/publications/EXIST_Enabling_ASPLOS-2025-Wang.pdf'
DOI = 'https://doi.org/10.1145/3676641.3716283'

EXIST = {
    'id': 'exist-2025',
    'route': 'asplos-2025',
    'title': 'EXIST: observe the cause without hiding it under measurement cost',
    'identity': 'Xinkai Wang, Xiaofeng Hou, Chao Li, and colleagues · EXIST: Enabling Extremely Efficient Intra-Service Tracing Observability in Datacenters · ASPLOS 2025',
    'scope': 'A focused walkthrough of the paper’s observability problem, trace-control and buffer mechanisms, and reported efficiency and accuracy. Sections 3.1–3.4 and 5 of the author-hosted conference paper were inspected. Measurements are author-reported and were not reproduced; the latency and tracing examples below are original teaching models unless attributed.',
    'lessons': [('s1', 'Measure the full request'), ('s3', 'Shared resources and contention'), ('queues-and-batching', 'Queues and waiting'), ('s10', 'End-to-end evidence')],
    'blocks': [
        {
            'title': 'An average can show a slowdown without showing its cause',
            'paragraphs': [
                'Suppose a service’s response time doubles for some requests. A utilization average may say the machines are busy, but not which operation held up a particular request. A distributed trace can connect one service call to another; an intra-service trace records the execution inside a service, showing where that request spent time and which events came first. That chronology can reveal a blocking operation or a wait hidden by service-level averages.',
                'The measurement can also change the system being measured. Traditional tracing methods can add work at each scheduling event, copy large records, or wait for shared locks. The paper reports that existing intra-service tracing commonly adds 5–10% time overhead on traced applications, with worst cases around 18%. In a shared datacenter, the effect can spread: tracing consumes processor time or memory bandwidth, slows a neighboring service, and delays later calls in a request chain.',
                'Use a deliberately simple chain: service A takes 20 ms without tracing and then calls service B, which takes 5 ms. If tracing adds 2 ms to A, that one delay is paid before B can finish, so the sequential response rises from 25 to 27 ms, an 8% increase. A different request may not take the same path, and shared queues can amplify or hide the change. This arithmetic illustrates propagation only; it is not an EXIST measurement.',
            ],
        },
        {
            'title': 'EXIST treats tracing as a pipeline with three limited resources',
            'paragraphs': [
                'EXIST uses processor support that records which way a program moved through its decision points, then rebuilds that path later. Its design addresses three different costs. First, its controller avoids changing tracing settings every time the operating system pauses one thread and runs another. The paper reduces those costly control actions from roughly one per scheduling event to roughly one per processor core during a tracing period. Second, a memory allocator chooses which cores to trace and how much buffer space each receives, because a finite buffer can fill before the interval ends. Third, a cluster-level controller chooses observation periods and repeats them across workers, trading more chances to see the event against more measurement work.',
                'These mechanisms solve different bottlenecks. Less controller work does not create unlimited trace storage. More buffer space does not guarantee that the chosen interval captures the anomaly. Longer or repeated observation may improve coverage but consumes more resources. A trace is therefore a constrained measurement plan: decide what to record, where to store it, how long to observe, and which gaps remain.',
                'The pipeline also defines what the tool can observe. Intel Processor Trace records the program path and timing, not a complete record of every value the program handled. The authors identify richer value-tracking support and more flexible hardware interfaces as future work. Knowing that a program took one branch rather than another can help reconstruct order, but it does not by itself say which input value caused that choice.',
            ],
            'sources': [(PDF + '#page=5', 'Author-hosted full paper, sections 3.1–3.4: tracing pipeline and three modules'), (PDF + '#page=13', 'Author-hosted full paper, section 6.2: platform and future-work limits'), (DOI, 'Official ASPLOS 2025 proceedings record')],
        },
        {
            'title': 'More trace data is not automatically evidence for the incident',
            'paragraphs': [
                'EXIST measures accuracy against a reference trace, but the paper uses different comparison procedures for standard benchmarks and live cloud applications. For compute benchmarks, it compares reconstructed execution paths with exhaustive native hardware-tracing (NHT) reference traces. It reports 90.2% average accuracy across its single-threaded benchmarks, while the multi-threaded 657.xz result is 62.2%. The paper attributes the gap mainly to trace data lost after its memory-space threshold is reached.',
                'For live applications, identical executions cannot be repeated on demand, so the authors use a relative comparison based on differences in function occurrence counts. Under that separate measure, they report 83.7%, 82.6%, and 86.2% average accuracy for 0.1-, 0.5-, and 1-second tracing periods. These figures are not directly comparable to the benchmark path-matching numbers. Nor does a high average guarantee that the specific rare event behind a production incident was recorded.',
                'The practical lesson is to name what “accurate” means. Does it mean matching each instruction path, preserving function counts, or capturing the event needed to explain one incident? State the reference, time window, lost-data policy, and denominator. If a buffer fills during a rare event needed for diagnosis, a good average may still miss the evidence the operator needs.',
            ],
            'sources': [(PDF + '#page=11', 'Conference paper, section 5.3: accuracy definitions and results')],
        },
        {
            'title': 'Compare measurement cost at the service boundary',
            'paragraphs': [
                'For its SPEC CPU benchmarks, the paper reports EXIST tracing slowdown from 0.4% to 1.5%. In its online workloads, it reports 1.1% average tracing overhead; for real-world applications it also reports a 1.1% average CPU-use increase and a 2.2% increase in cycles per instruction over the untraced comparison at low workload stress. These measure different things. A longer elapsed time, extra processor use, and more processor cycles per instruction cannot be swapped for one another.',
                'The authors also measure a Search1 request’s 99th-percentile response time. EXIST adds 1–3% end-to-end delay in the stated experiment, compared with more than 10% for several comparison methods that add single-digit overhead inside a traced service. This shows why a local tracing cost and a whole-request cost can differ: shared resources and dependent service calls can carry the tracer’s extra work downstream.',
                'The results are specific to the paper’s Intel hardware-tracing implementation, workloads, comparison methods, sampling periods, and shared-cluster setup. The authors note that worst-case EXIST overhead can be higher, that ARM and RISC-V support remains future work, and that traces may be incomplete when buffers fill. Before deploying a tracing tool, measure both its local resource use and the end-to-end response-time distribution, then check that the captured record actually contains the interval and events needed for the incident under investigation.',
            ],
            'sources': [(PDF + '#page=10', 'Conference paper, section 5.2 and Tables 2–3: overhead'), (PDF + '#page=10', 'Conference paper, Figure 16: tail-latency impact'), (DOI, 'Official ASPLOS proceedings record')],
        },
    ],
    'exercise': {
        'question': 'An operator observes a 10% rise in 99th-percentile response time while tracing is enabled. A component-level test reports only 1% extra CPU use. What can be concluded? Name two additional measurements and one trace-quality check needed before deciding whether the tracer caused the service regression.',
        'answer': 'The figures alone do not prove causation or contradict each other: CPU use and tail response time are different quantities, and dependent calls or shared queues can magnify local delay. Compare end-to-end latency under the same arrivals and workload with tracing on and off; measure traced-service time and co-located resource contention; and check whether the trace captured the interval and events of interest without buffer loss. Repeat across representative load levels. These are proposed diagnostic checks, not results claimed for EXIST.',
    },
}
