"""ISSCC orientation with a one-record evidence boundary."""

ISSCC_ROUTE = {
    "id": "isscc-2025",
    "title": "ISSCC 2025: read a circuit result with its workload and measurement boundary",
    "coverage_status": "Limited reading guide; one source-backed record, broader synthesis unfinished",
    "status": "Limited reading guide with one full ConvFormer accelerator walkthrough. It is not a conference-wide theme synthesis; the other 257 records remain discovery evidence and broader primary-paper coverage is unfinished.",
    "intro": "Start with the physical device and the accepted result it is meant to produce. Ask what is implemented on the chip, what supporting work runs elsewhere, which data stays nearby, and how output quality is checked. The questions below are a teaching guide for reading circuit papers. They are not a claim that four themes have been established across the entire ISSCC 2025 proceedings.",
    "evidence": "The local acquisition audit lists 258 records: one PDF with extracted text, one advertised source that returned a landing page, and 256 without a usable PDF URL. The source-backed review concerns record 038, a ConvFormer accelerator, which also has the full learner walkthrough here. The 257 other records support discovery only. Its chip and workload results are paper-reported, not independently reproduced by this course.",
    "themes": [
        {
            "title": "1. Find what each stage is waiting for",
            "body": "One stage can spend most of its time fetching values while another spends most of its time calculating. Faster arithmetic helps those stages by different amounts. Split the job into stages, count their work, and check which costs the proposed change can actually reduce.",
            "subthemes": [
                ("Phase-specific requirements", "Identify the values, operations, and output of each phase. Count the capacity and transfer demand rather than using an application label as an explanation."),
                ("Whole-path coverage", "State which phases the chip performs and which need supporting software or hardware. A high-rate central unit may leave large preparation or delivery costs outside its boundary."),
            ],
            "reading": "The local ConvFormer review distinguishes a memory-intensive model backbone from a computation-intensive segmentation head. Use that distinction to ask why the design needs more than one kind of execution choice; do not extrapolate it to every model.",
            "worked_example": [
                "In an invented two-phase job, phase one transfers for 12 ms and calculates for 3 ms; phase two transfers for 2 ms and calculates for 10 ms. With no overlap anywhere, completion takes 27 ms. Halving all calculation gives 12 + 1.5 + 2 + 5 = 20.5 ms. Halving all transfer instead gives 6 + 3 + 1 + 10 = 20 ms. Neither change halves the whole job, and the limiting work differs between phases.",
                "Suppose a different implementation can fully overlap transfer with calculation inside each phase while preserving all dependencies and resource rates. Its ideal time is max(12, 3) + max(2, 10) = 22 ms. This is a separate schedule, not a saving to subtract blindly from the previous totals. If phase-one calculation needs data that arrives only at the end of its transfer, the proposed full overlap is unavailable. The timing argument needs a data-readiness account.",
                "The ConvFormer accelerator targets semantic segmentation: assigning a category to each image location. Its feature-building stages keep and move large intermediate arrays; its final classification stages require many arithmetic operations. The digest identifies different obstacles in these stages. The attention intermediate can exceed local storage, attention data and convolution weights cannot all be kept together, and the final stages have too few zeros for simple zero-skipping to save much work. Calling the whole model 'memory-bound' would hide the last problem.",
                "The design accordingly changes more than one thing. It uses a mixture of attention methods to reduce intermediate storage, schedules reusable data to avoid repeated transfers, and changes the final-stage representation so a trained mask can remove work. These are not interchangeable improvements. A mask is a recorded choice of which contributions to retain; changing it can change the answer. The attention change also needs a quality test, not just an arithmetic count. The focused walkthrough explains those changes separately from exact matrix rearrangement.",
                "For this one reviewed chip, ask which stage each measurement covers and what data must already be ready. Then check the complete workload as well as the improved stage. The invented 27-, 22-, and 17-ms schedules isolate timing principles; they are not measured timings from the accelerator and do not establish its reported gains. This lesson is a reading guide from one digest, not a finding about all ISSCC papers.",
            ],
            "practice": {
                "question": "Under the ideal within-phase overlap assumption, halve calculation only. What is the new time, and why does phase one not get shorter?",
                "answer": "The time becomes max(12, 1.5) + max(2, 5) = 17 ms. Phase one still waits for its 12-ms transfer, so its calculation saving is hidden inside that interval. Phase two falls from 10 to 5 ms. If faster calculation increases transfer contention or changes when data becomes ready, these fixed-stage assumptions need to be revisited.",
            },
            "lessons": [("s3", "Memory costs"), ("s10", "Whole-service accounting")],
        },
        {
            "title": "2. Keep a value until its last reader is finished",
            "body": "An intermediate value occupies space from the time it is produced until its last use. Changing the schedule can shorten that overlap and make room for other work. Discarding a value that still contributes to the answer is a different change: it needs an explicit allowance for changed output.",
            "subthemes": [
                ("Intermediate state and reuse", "Compare which arrays exist, their sizes, and how long they remain needed. Include the storage needed to preserve a value for later reuse."),
                ("Selective work and quality", "Distinguish an exact reorder from a changed attention rule or removed contribution. State the task-quality test for any approximation rather than assuming algebra alone justifies it."),
            ],
            "reading": "The ConvFormer review describes three different changes: it combines two ways of relating image regions, keeps selected data from one layer for a later layer to use again, and uses a trained mask to omit selected groups of intermediate values. All can reduce storage or work, but the review does not establish that any one change alone explains the complete measured improvement.",
            "worked_example": [
                "Take an original storage example with 8 MB available for intermediate state. Two simultaneously needed arrays occupy 3 MB each, and temporary working space occupies 1 MB: 7 MB fits. Keeping another 2-MB value for reuse raises the requirement to 9 MB and no longer fits. Saving future reads can therefore create a capacity problem now. Count all values that must remain alive together, not only the largest array.",
                "A possible fix is to reuse one array's storage after its last consumer finishes. That changes the peak only if the lifetimes really stop overlapping. Another consumer that still needs the old array makes early overwrite incorrect. Alternatively, splitting the operation into smaller blocks can lower live storage while adding repeated reads or boundary work. These are exact scheduling and storage questions; deleting values because they seem unimportant is a different proposal that needs a quality allowance.",
                "The ConvFormer digest describes a concrete storage conflict: the stored lookup data used by its attention calculation cannot remain on the chip together with all the learned convolution coefficients. Its scheduler first reuses the stored attention data for the selected ordinary-attention regions, then replaces it with convolution coefficients and reuses those. The saving comes from avoiding repeated loads while retaining the outputs needed later. It does not mean every intermediate disappears, or that a consumer can run before its input is ready.",
                "Consider an original neighboring-data example. An operation adds three values, 4, 5, and 6, with equal weights. The answer is 15. If the last region has not produced its 6 yet, substituting zero gives 9. A combined schedule must wait, retain the boundary value when it arrives, or make an explicitly justified change to the calculation. Calling two stages fused—executed together without writing all intermediates out to memory—does not remove their data dependencies.",
                "The digest's pruning mechanism changes the calculation rather than merely changing storage lifetime. It first creates a larger set of intermediate values, then uses a trained mask—a stored yes/no choice learned during training—to keep selected contributions. That can reduce work only where the implementation actually avoids calculating or using the omitted contributions. The model's output quality must then be checked. The focused walkthrough gives separate examples for exact reuse, changed attention, and pruning; none should be described as the same storage optimization.",
            ],
            "practice": {
                "question": "The additional 2-MB value is needed only after every reader of one 3-MB array has finished. Can the job fit without compressing anything? State what must be true before reusing that space.",
                "answer": "Yes, if no earlier step requires the additional value and the old array has no remaining reader. The first stage needs 7 MB; the later stage needs 3 + 1 + 2 = 6 MB, so the peak remains 7 MB. This is reuse of storage across time, not a claim that 9 MB fits simultaneously into 8. Transfer buffers, alignment, or other allocations omitted from the example would need to be added in a real implementation.",
            },
            "lessons": [("s6", "Rewrites and fusion"), ("s5", "Pruning costs"), ("s2", "Approximation")],
        },
        {
            "title": "3. Count energy per completed task, not just per operation",
            "body": "A chip can perform more operations per joule yet use more energy to finish a task. The task may require more operations, and other components may consume energy while it runs. Define what counts as an operation, then count the energy needed for the same acceptable answer.",
            "subthemes": [
                ("Operating point", "Record voltage, frequency, activity, and measurement conditions. A chip's supported range does not mean every reported peak occurs at every point in that range."),
                ("Comparison boundary", "Check whether memory, host work, conversion, and idle time are included. Distinguish a prior device's reported peak from running both devices on the same workload."),
            ],
            "reading": "The local review reports fabricated-chip evidence and explicitly notes that prior-system comparisons depend on reported peak efficiency. Retain that limitation rather than presenting those comparisons as identical end-to-end experiments.",
            "worked_example": [
                "Assume two invented devices produce the same accepted answer. At their achieved operating points, A performs 20 billion defined operations at 10 billion operations per joule, using 2 J. B performs 12 billion at 8 billion per joule, using 1.5 J. B has a worse operations-per-joule ratio but lower device energy per task because it does less work. This calculation assumes the operation counts and efficiency measurements are comparable; an advertised peak alone would not establish achieved task energy.",
                "Now include a host that draws 3 W throughout each run. A finishes in 0.5 seconds; B takes 1 second. Host energy adds 1.5 J to A and 3 J to B, giving totals of 3.5 and 4.5 J. A now wins on both completion time and included energy. No arithmetic contradiction occurred: the measurement boundary changed. Report the device-only comparison and the larger-system comparison separately.",
                "Operation counts need a consistent definition too. In an original example, an unpruned calculation would require 100 multiplications. A method skips 80 and executes 20, using 1 microjoule. Counting executed multiplications gives 20 million per joule; counting the original dense-equivalent work gives 100 million per joule. The physical energy and output have not changed, but the reported ratio differs fivefold. Neither count is necessarily useless; the label must say which it is, and comparisons must use the same convention.",
                "The ConvFormer digest reports its peak of 52.90 TOPS/W at 0.65 V and 200 MHz. TOPS/W means trillions of defined operations per second per watt, equivalent to trillions of operations per joule. That peak belongs to the stated voltage and clock frequency; the chip's wider operating range does not imply the peak holds throughout it. Nor does a peak establish the efficiency achieved during every stage of a complete image-processing job.",
                "The digest's comparison with earlier accelerators includes a DDR3 memory interface and assumes those earlier devices operate at their reported peak efficiencies and configurations. This is an assumption-based system comparison, not a new measurement of every competing chip on identical inputs. Keep it separate from the fabricated chip's own measurements. The source's system-energy result and the invented host-energy example answer the same accounting question, but their components and numbers are not interchangeable.",
            ],
            "practice": {
                "question": "Keeping these device energies and run times fixed, at what common host power do the total energies tie? Which side favors B?",
                "answer": "Set 2 + 0.5P = 1.5 + P, giving P = 1 watt. Below 1 W, B's 0.5-J device saving outweighs its extra half-second of host use. Above 1 W, A uses less included energy. The comparison assumes constant host power during execution and excludes any different startup, idle, or cooling costs.",
            },
            "lessons": [("physical-design", "Power and energy boundaries"), ("s1", "Metric endpoints")],
        },
        {
            "title": "4. Say which conditions the chip actually passed",
            "body": "A working chip is evidence that a physical implementation exists and ran under tested conditions. It is not evidence for every input, environment, or duration. Record what was tested and what counted as success before extending the result to another use.",
            "subthemes": [
                ("Task and dataset scope", "Keep the tested model family and quality measure visible. A segmentation result does not establish performance or quality for an unrelated learning task."),
                ("Physical and review scope", "Identify which conditions were measured and which statements come from a local review rather than a new inspection of the primary source. Leave unexamined details unresolved."),
            ],
            "reading": "The record 038 review names SegFormer/PVT variants and Cityscapes. The linked ConvFormer walkthrough inspects the digest's mechanism and measurement discussion while keeping its prior-accelerator comparison assumptions explicit.",
            "worked_example": [
                "Imagine a report that tests three chips at 25 °C on one workload, at one supply voltage, for one minute each. Suppose all three produce correct outputs and meet the timing limit. The direct observation is success for those samples, conditions, inputs, and durations. It does not establish every chip's behavior at a higher temperature, after longer operation, or on a workload with a different activity pattern. The missing cases remain unmeasured, not failures and not successes.",
                "Changing one condition at a time can help identify why behavior changes, but a deployment may combine conditions. A temperature sweep at one workload does not cover every temperature–workload combination. Separately, a chip-level timing result does not establish a service deadline if input preparation or queueing is excluded. Follow the chain from measured circuit behavior to the application claim and name each additional assumption.",
                "Consider just two test durations, short and long, and two activity levels, low and high. There are four combinations. Passing short/high and long/low covers two, not all four. The long/high combination could have behavior that neither test exposed. This is a statement about the missing experiment, not evidence that the chip will fail it. A justified model of the interaction might reduce the necessary testing, but the model and its supporting evidence would need to be stated.",
                "The ConvFormer digest names SegFormer-B0, PVTv1-Ti, and PVTv2-B0 with the Cityscapes dataset. Those reported tests support a specific image-segmentation comparison. They do not establish the same speed, energy, or output quality for a different model family. The digest also reports a fabricated chip and a range of voltage and clock settings, while its prior-accelerator energy comparison uses assumptions about the other devices' peak efficiencies. Keep those evidence types distinct, as in theme 3.",
                "A clear handoff to another reader would say: the chip and these workload results are author-reported; this course has inspected the digest but has not reproduced the hardware experiment; the three-chip temperature example is invented; and broad ISSCC coverage is still missing. Being specific about those limits lets the reader use the result without treating a one-paper reading guide as a conference-wide conclusion.",
            ],
            "practice": {
                "question": "A chip passes a short high-activity test and a long low-activity test. Does that establish successful long high-activity operation? What new evidence directly addresses the gap?",
                "answer": "No. Duration and activity may interact through temperature, power delivery, or other physical effects. Test the combined condition under stated voltage, cooling, inputs, and acceptance checks, or supply a justified model whose assumptions cover it. Even a successful combined test establishes the sampled conditions rather than every possible operating environment.",
            },
            "lessons": [("physical-design", "Measured evidence"), ("s8", "Claim boundaries")],
        },
    ],
    "exercise": "In an invented comparison, device A delivers 10 billion defined operations per joule and uses 20 billion operations per accepted task. Device B delivers 8 billion operations per joule but needs only 12 billion operations for the same accepted result. Ignoring supporting costs, A uses 2 J per task and B uses 1.5 J. What must be checked before preferring B? Verify comparable operation definitions, accepted task quality, achievable operating rates, and the omitted memory, host, and idle energy. These numbers are not from the ISSCC paper.",
    "sources": [
        ("analysis/isscc-2025-source-acquisition-audit.md", "ISSCC acquisition audit — one source-backed record out of 258"),
        ("analysis/isscc-2025-source-backed-adjudication-001.md", "Bounded ConvFormer review — reported mechanisms and comparison limits"),
    ],
}
