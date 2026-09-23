"""Focused ASPLOS walkthrough of complete mobile tracing under a fixed buffer."""

PAPER = 'https://doi.org/10.1145/3676641.3715994'
PDF = 'https://wangjwchn.github.io/papers/ASPLOS2025.pdf'

BTRACE = {
    'id': 'btrace-2025',
    'route': 'asplos-2025',
    'title': 'BTrace: keep the evidence that a mobile failure leaves behind',
    'identity': 'Enabling Efficient Mobile Tracing with BTrace · ASPLOS 2025',
    'scope': 'A focused walkthrough of distributed versus coordinated trace buffers, buffer utilization, event completeness, resizing, and the reported smartphone evaluation. The locally extracted primary source was inspected in sections 3.1–3.4 and the evaluation. Results are author-reported and have not been independently reproduced here. The buffer and loss calculations are original teaching models.',
    'lessons': [('s1', 'Follow one request'), ('s3', 'Memory'), ('s7', 'Parallel hardware'), ('s10', 'Whole-system cost')],
    'blocks': [
        {
            'title': 'A fast trace that loses the event needed for diagnosis is incomplete evidence',
            'paragraphs': [
                'A trace records events so someone can explain what a system did later. On a phone, many cores can produce events at different rates. A common design gives each core or thread its own circular buffer. That reduces contention because producers write independently, but a busy producer can overwrite its old events while another buffer still has unused space. The final trace then contains gaps at exactly the time a diagnosis needs continuity.',
                'BTrace changes the storage question from “how fast can each producer write locally?” to “how much of the available memory can the complete trace use?” It coordinates a global buffer by partitioning it into blocks, allowing producers to retain the low-contention behavior of separate blocks while allocating blocks where event demand exists. The design aims to preserve a longer continuous fragment without pretending that recording has zero overhead.',
                'Original four-block model: four cores produce 8, 8, 8, and 32 event units, while each private buffer holds 10. Private buffers retain 10+8+8+10 = 36 units because the busiest core overwrites 22 and the quiet cores leave 4 unused. A coordinated pool of 40 units can retain all 40 if its block management is correct. The improvement comes from using spare capacity elsewhere; it is not simply a faster write instruction.',
            ],
            'sources': [(PDF, 'BTrace paper, sections 3.1–3.4: distributed-buffer loss, global capacity, partitioned blocks, and coordination'), (PAPER, 'ASPLOS publication record: primary citation')],
        },
        {
            'title': 'Completeness and recording latency are separate promises',
            'paragraphs': [
                'A buffer design can be judged by at least two different questions: how long each event takes to record, and how much of the desired history survives. A distributed buffer may have low write contention but poor utilization. A single global lock may use memory well but make every producer wait. BTrace’s block coordination tries to reach high utilization without paying the full contention cost of one shared write point.',
                'The amount of trace retained also depends on event rates, buffer size, and the requested history. A “zero loss” result means no event was lost in the stated workload and buffer configuration; it does not mean an unlimited trace or protection against a workload that produces events faster than the available memory can absorb. The experiment must name which events count as required and how overflow is handled.',
                'Original loss model: a trace has 100 required events, but a 20-event buffer receives 30 events before a symptom and 10 after it. If the first 20 are overwritten, only 10 of the 30 pre-symptom events survive, so 20 required events are missing. Doubling the buffer to 40 may prevent loss in this schedule, but it does not prove the same for a later burst of 80 events. Capacity, rate, and retention interval must be stated together.',
            ],
            'sources': [(PDF, 'BTrace paper, evaluation setup and buffer-utilization analysis: retention, loss, and recording-latency boundaries')],
        },
        {
            'title': 'Resizing makes memory management part of the tracing protocol',
            'paragraphs': [
                'A production tracer may need a small buffer during normal operation and a larger one while investigating a suspected failure. Growing and shrinking per-core buffers is difficult when producers and the collector access them concurrently: a writer may still hold a pointer while the memory is being reclaimed, or the system may move data while a reader is copying it. A safe resize therefore needs ownership and visibility rules, not only an allocator call.',
                'BTrace’s coordinated blocks give the system a way to change capacity while keeping block addresses and active writers understandable. The exact safety obligation is that a writer either completes against a valid block or is stopped and redirected before the old block can be reclaimed. The trace consumer must also know the order of events across blocks; retaining bytes without a consistent order can still make diagnosis impossible.',
                'Original resize sequence: block A is active, the collector marks block B as unavailable, waits for its writer to leave, copies or records its retained range, then returns B to the pool. If the writer can continue after the unavailable mark, the collector may miss an event or read reclaimed memory. The mark, acknowledgment, and reuse steps are part of correctness; the copy time is part of performance.',
            ],
            'sources': [(PDF, 'BTrace paper, sections on dynamic buffer resizing and block ownership: concurrent resize and safe reuse')],
        },
        {
            'title': 'Read the reported result at the phone, trace, and buffer boundary',
            'paragraphs': [
                'The paper reports 0.00% loss for BTrace in its evaluated trace-replay workloads, compared with about 60% average loss for ftrace and LTTng and about 90% for VTrace in the stated comparison. It reports 53 ns geometric-mean recording latency for BTrace versus 63 ns for ftrace, and a 10.8 MB geometric-mean latest continuous fragment in a 12 MB buffer. These are different measures: event completeness, per-event latency, and retained history should not be collapsed into one score.',
                'For its production beta configuration, the paper reports that a 450 MB BTrace buffer stores more than 30 seconds of trace data and that the deployment helped identify more than 200 long-duration bugs. The evaluated evidence comes from 20 smartphone traces on 12-core production hardware, with the stated benchmark and production configurations. Privacy, general-availability deployment, available memory, and workload-specific event-rate changes remain boundaries.',
                'A fair follow-up should hold event definitions, trace duration, buffer capacity, producer workload, and collection policy constant. It should report loss, ordering, recording latency, retained duration, memory cost, CPU cost, and the behavior during resize separately. A complete trace is valuable only if its events are interpretable and collecting it does not change the failure being diagnosed.',
            ],
            'sources': [(PDF, 'BTrace paper, evaluation: 20 smartphone traces, loss, latency, retained fragment, production buffer, and bug-finding boundary'), (PAPER, 'ASPLOS publication record: primary citation')],
        },
    ],
    'exercise': {
        'question': 'An invented phone has four private buffers of capacity 10. Four cores produce 8, 8, 8, and 32 event units before collection. How many event units can the private design retain? If a coordinated 40-unit pool retains all events, what principle explains the difference, and what must still be measured?',
        'answer': 'The private design retains 10 + 8 + 8 + 10 = 36 units; the busiest producer overwrites 22 while 4 units remain unused in the other buffers. The coordinated pool can retain 40 by sharing spare capacity. Still measure write contention, event ordering, resize safety, CPU and memory overhead, and loss under changing event rates. These are original teaching calculations, not BTrace measurements.',
    },
}
