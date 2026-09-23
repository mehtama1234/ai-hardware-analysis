"""Focused ASPLOS walkthrough of thermal- and power-aware LLM scheduling."""

PDF = 'https://arxiv.org/abs/2501.02600'

TAPAS = {
    'id': 'tapas-2025',
    'route': 'asplos-2025',
    'title': 'TAPAS: schedule for heat and power, not only speed',
    'identity': 'Jovan Stojkovic and colleagues · TAPAS: Thermal- and Power-Aware Scheduling for LLM Inference in Cloud Platforms · ASPLOS 2025',
    'scope': 'A focused walkthrough of phase-specific thermal and power behavior, placement, request routing, reconfiguration, multi-tenant control, and the reported cluster evaluation. The local public primary text was inspected. Results are author-reported real-cluster and trace-driven simulation results and have not been independently reproduced here. The heat, capacity, and service examples are original teaching models.',
    'lessons': [('s1', 'Whole-request timing'), ('queues-and-batching', 'Scheduling'), ('s9', 'Power and energy'), ('s10', 'Whole-system cost')],
    'blocks': [
        {
            'title': 'A fast request can still be a bad datacenter decision',
            'paragraphs': [
                'A GPU inference service consumes electricity and produces heat while it serves requests. The datacenter must keep both within limits. A placement that is safe on average can still create a hot row or exceed a shared power limit when several servers peak together. The service also changes phases: prefill processes a prompt, while decode produces tokens one at a time. Their performance, power, and temperature patterns are not identical.',
                'TAPAS treats speed, temperature, power, and answer quality as linked but separate outcomes. It can place GPU VMs using historical load and thermal data, route requests toward instances with useful slack, and reconfigure provider-controlled SaaS instances during a spike or failure. Opaque IaaS VMs cannot be changed in the same way, so visibility is part of the control problem.',
                'Original capacity model: three rows each have a 100-unit safe power envelope. Existing loads are 70, 50, and 40. A new 20-unit VM fits in rows 2 and 3 but would push row 1 to 90; a second 20-unit VM fits row 1 after the first placement but not if both are sent there. Total spare capacity is 140, but the useful placement depends on the row-level constraint. Adding totals alone hides the hotspot.',
            ],
            'sources': [(PDF, 'TAPAS paper, abstract and introduction: phase-specific profiles, shared limits, and placement/routing/reconfiguration')],
        },
        {
            'title': 'The control loop must operate at the workload’s timescale',
            'paragraphs': [
                'If a controller reacts only to slow averages, it may miss the short phases that create a spike. If it reacts too aggressively to every sample, it may keep changing model size, precision, parallelism, or frequency and spend more time reconfiguring than serving. The controller needs a measured signal, an actuation delay, a safety threshold, and a service objective such as tail latency or accepted answer quality.',
                'TAPAS combines historical temperature and power patterns with current load. Its configuration choices have different directions of effect: reducing model size or precision can lower temperature and power but may lower quality; reducing parallelism can lower power but can hurt performance; lowering frequency can reduce power and speed. The choice is therefore a constrained decision, not a single “best” knob.',
                'Original control model: a row reaches 90 units, its safe limit is 100, and a reconfiguration takes 3 time units. A request burst adds 5 units per time unit for 4 units of time, so the row would reach 110 before the action completes. A controller must predict the next state and act before the threshold, or route work elsewhere. Waiting for the measured violation is already too late.',
            ],
            'sources': [(PDF, 'TAPAS paper, sections 2 and 3: thermal/power characterization, temporal and spatial variation, and inference control knobs')],
        },
        {
            'title': 'Placement, routing, and configuration solve different parts of the problem',
            'paragraphs': [
                'Placement decides where a VM starts. Routing decides which existing instance receives a request. Configuration changes the work an adjustable SaaS instance performs. These actions operate at different timescales and have different costs. A good placement cannot repair a sudden load spike by itself; a routing policy cannot help if every eligible instance shares the same hot row; a configuration change may protect the hardware while reducing model quality or throughput.',
                'Emergency handling makes the tradeoff explicit. When cooling or power capacity fails, TAPAS can reduce load or use smaller models for provider-controlled workloads while preserving the safety boundary. That may protect the cluster but it is not free: the accepted answer, latency target, or customer policy may change. The system must record which promise was relaxed and for how long.',
                'Original service model: two instances each serve 100 requests per second at quality 1.0. Routing can move 30 requests per second from a hot instance to a cool one, but the cool instance has only 20 spare requests per second, so 10 remain. A lower-quality configuration raises the hot instance’s capacity to 120 but quality falls to 0.95. The scheduler must compare the safety limit, queue, capacity, and quality requirement instead of calling every change an improvement.',
            ],
            'sources': [(PDF, 'TAPAS paper, sections 4–6: placement, request routing, reconfiguration, and emergency response')],
        },
        {
            'title': 'Read thermal, power, capacity, and quality results at their boundaries',
            'paragraphs': [
                'The paper reports a production-trace evaluation in a large GPU cluster. In its main ablation, TAPAS maintains the P99 inference latency target while reducing maximum temperature by 17% and peak row power by 23%, enabling up to 40% additional capacity under the stated oversubscription policy. In a larger trace-driven simulation, it reports 97% fewer thermal-throttling events and 99% fewer power-throttling events; a scaled real-cluster experiment reports 20% lower peak utilization in its stated setup.',
                'These are not interchangeable claims. Lower temperature is not the same as lower energy; more capacity is not the same as more accepted requests at a fixed quality; fewer throttling events depend on the chosen threshold and trace. The evaluation combines a real cluster experiment with a discrete-time simulation driven by production traces and Llama2 profiles, so the evidence boundaries must remain visible.',
                'The paper also acknowledges emergency choices that may trade SaaS quality for safety and limits the provider’s control over opaque IaaS workloads. This walkthrough has not reproduced the traces, simulator, cluster experiment, or control policy. Its heat, capacity, and service calculations are original teaching models.',
            ],
            'sources': [(PDF, 'TAPAS paper, abstract and evaluation sections: reported temperature, power, capacity, throttling, latency, and evidence boundaries')],
        },
    ],
    'exercise': {
        'question': 'A row has a 100-unit power limit and currently draws 82 units. A new request would add 8 units, but a second request would add another 7. Can both be placed there? If the scheduler can route 5 units of work to another row, what still needs to be checked before accepting both requests?',
        'answer': 'Both requests would bring the row to 97 units, so they fit the stated 100-unit limit; without routing, the spare capacity is 18 and the combined addition is 15. Routing 5 units elsewhere lowers the row to 92 after both requests, but the scheduler must still check the other row’s capacity, thermal state, request latency, queueing, answer quality, actuation delay, and shared power limits. These are original teaching calculations, not TAPAS measurements.',
    },
}
