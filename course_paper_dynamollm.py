"""Focused HPCA walkthrough of energy-aware LLM inference management."""

PDF = 'https://iacoma.cs.uiuc.edu/iacoma-papers/hpca25_2.pdf'

DYNAMOLLM = {
    'id': 'dynamollm-2025',
    'route': 'hpca-2025',
    'title': 'DynamoLLM: change the cluster configuration without breaking its latency promise',
    'identity': 'Jovan Stojkovic, Chaojie Zhang, Íñigo Goiri, Josep Torrellas, Esha Choukse · DynamoLLM: Designing LLM Inference Clusters for Performance and Energy Efficiency · HPCA 2025',
    'scope': 'A focused walkthrough of DynamoLLM’s workload distinctions, energy-performance profiles, configuration knobs, hierarchical controllers, and reported evaluation. The HPCA paper was inspected. Results are author-reported and have not been reproduced here. The energy and timing calculations are original teaching models.',
    'lessons': [('s1', 'Whole-request timing'), ('queues-and-batching', 'Service promises'), ('s3', 'Resource limits'), ('s6', 'Execution plans'), ('s10', 'Whole-system cost')],
    'blocks': [
        {
            'title': 'The best configuration depends on the request, not just the model',
            'paragraphs': [
                'LLM inference has two useful phases. Prefill processes the input prompt in parallel and is often compute-heavy. Decode produces output tokens one at a time and is often limited by moving model state and the key–value cache. A request with many input tokens can benefit from a higher GPU frequency, while a request with few input tokens and many output tokens may save energy at a lower frequency without violating its service promise.',
                'The same model can therefore need more than one operating point. DynamoLLM considers the number of instances, how the model is split across GPUs, and GPU frequency. It maintains pools with different configurations for different request types, then changes pool sizes as the request mix changes. This is more precise than lowering every GPU equally: one global setting can help one request class and harm another.',
                'Original example: a high-input request takes 8 seconds at 1,800 MHz and 10 seconds at 1,200 MHz, while a decode-heavy request takes 12 and 12.5 seconds respectively. If both have a 10-second SLO, only the first needs the higher setting; the second can use the lower one. If the mix changes, a configuration that was energy-efficient can become wrong. A mean request time does not reveal this per-class constraint.',
            ],
            'sources': [(PDF + '#page=1', 'HPCA paper, introduction: request heterogeneity, phases, and configuration knobs'), (PDF + '#page=2', 'HPCA paper, background: prefill, decode, TTFT, and TBT')],
        },
        {
            'title': 'Measure energy only after fixing the promise it must satisfy',
            'paragraphs': [
                'Energy is not a replacement for latency. DynamoLLM measures watt-hours while meeting specified TTFT and time-between-token (TBT) SLOs. A lower-power configuration that misses the required delay is not a more efficient solution to the same task. Carbon and customer cost are also separate quantities: carbon depends on the electricity accounting boundary, and cost depends on the provider’s pricing and resource duration.',
                'The system first builds an energy-performance profile by running different request lengths, model-parallel settings, and GPU frequencies. It uses measured points and interpolation for intermediate loads, adding points where power changes sharply. The paper reports average prediction accuracy above 98% for its profiles. That is evidence about the evaluated profiling method and workloads, not a guarantee that a new model or request distribution will have the same prediction error.',
                'Teaching calculation: configuration A uses 400 W for 2 hours and meets the SLO, consuming 0.8 kWh. Configuration B uses 250 W for 4 hours and also meets it, consuming 1.0 kWh. B has lower power but higher energy per completed service run. If B serves twice as many accepted requests in the same interval, its energy per accepted request can still be lower. Always state whether the comparison is power, total energy, energy per accepted result, carbon, or money.',
            ],
            'sources': [(PDF + '#page=1', 'HPCA paper, abstract: energy, carbon, cost, and SLO claims'), (PDF + '#page=5', 'HPCA paper, section IV-A: profile generation and prediction boundary')],
        },
        {
            'title': 'Reconfiguration is work that the controller must pay for',
            'paragraphs': [
                'Changing the number of instances can require creating a VM, initializing distributed communication, downloading weights, preparing the inference engine, and placing weights and the key–value cache on GPUs. Changing model parallelism requires re-sharding weights and coordinating the new arrangement. Changing GPU frequency can also affect performance during the transition. These costs can be minutes or can interrupt service, so a controller cannot treat a new configuration as instantly available.',
                'DynamoLLM organizes control hierarchically. A cluster controller decides pool sizes and broad resources, pool controllers decide model parallelism and request assignment, and instance controllers adjust frequency. Each level works within constraints from the level above. The hierarchy limits a central controller’s work and lets a local change happen without recomputing every decision, but it does not remove the need to verify that the lower-level choice still meets the upper-level SLO.',
                'Original break-even example: a new frequency saves 20 W during a 30-minute interval, or 10 Wh. Applying it costs 4 Wh of transition energy and adds 2 minutes in which the service runs at half throughput. If the service normally consumes 100 Wh per hour and the lost throughput causes 3 Wh of extra work, the net saving is only 3 Wh. If the workload changes again after 10 minutes, the transition may not pay back. A controller needs a persistence forecast, not just a favorable current measurement.',
            ],
            'sources': [(PDF + '#page=4', 'HPCA paper, section III: scaling, sharding, frequency, and transition overheads'), (PDF + '#page=5', 'HPCA paper, section IV: hierarchical controller design')],
        },
        {
            'title': 'Read the cluster result with its traces and accounting boundary',
            'paragraphs': [
                'The paper evaluates DynamoLLM on a large GPU cluster using production-level Microsoft Azure traces. It reports, on average, 52% lower energy, 38% lower operational carbon emissions, and 61% lower customer cost while meeting latency SLOs. Those are service-level results under the paper’s traces, models, cluster, pricing and carbon accounting, profiling, and controller assumptions. The numbers should not be transferred to a different electricity mix, billing model, GPU generation, or request distribution without new evidence.',
                'The result is also not “lower frequency is always better.” The paper’s motivation distinguishes compute-heavy prompt processing from memory-heavy token generation and distinguishes request lengths and service requirements. Energy savings come from choosing among configurations while preserving the stated performance promise. Report which requests meet TTFT and TBT limits, not only average power or total cluster energy.',
                'A deployment follow-up should replay its own request mix, measure power and accepted outputs, include every reconfiguration interval, and report energy per accepted request alongside SLO attainment and cost. The course has not reproduced the cluster evaluation. This walkthrough keeps the paper’s measured result separate from the invented calculations and from a general claim about energy-efficient LLM serving.',
            ],
            'sources': [(PDF + '#page=1', 'HPCA paper, abstract and introduction: reported service-level results'), (PDF + '#page=5', 'HPCA paper, framework architecture and profile inputs')],
        },
    ],
    'exercise': {
        'question': 'Configuration A uses 400 W for 2 hours and configuration B uses 250 W for 4 hours. Both meet the same SLO. Which uses less total energy? What additional denominator would you need before calling one more energy-efficient per accepted result?',
        'answer': 'A uses 400 × 2 = 800 Wh, while B uses 250 × 4 = 1,000 Wh, so A uses less total energy in this example. To compare energy per accepted result, measure how many requests each configuration completes while meeting the same quality and latency rules. Power alone is not the denominator; the calculation is an original teaching model, not a DynamoLLM measurement.',
    },
}
