"""Conference teaching routes. Status is explicit; a route is not a paper review."""

from course_route_nsdi import NSDI_ROUTE
from course_route_isca import ISCA_ROUTE
from course_route_hpca import HPCA_ROUTE
from course_route_micro import MICRO_ROUTE
from course_route_sc import SC_ROUTE
from course_route_dac import DAC_ROUTE
from course_route_date import DATE_ROUTE
from course_route_vlsid import VLSID_ROUTE
from course_route_isscc import ISSCC_ROUTE
from course_route_fccm import FCCM_ROUTE
from course_route_iccad import ICCAD_ROUTE

CONFERENCE_SCOPE = [
    ('mlsys-2025', 'MLSys 2025'), ('osdi-2025', 'OSDI 2025'),
    ('asplos-2025', 'ASPLOS 2025'), ('nsdi-2026', 'NSDI 2026'),
    ('isca-2025', 'ISCA 2025'), ('hpca-2025', 'HPCA 2025'),
    ('micro-2025', 'MICRO 2025'), ('sc-2025', 'SC 2025'),
    ('dac-2025', 'DAC 2025'), ('date-2025', 'DATE 2025'),
    ('vlsid-2025', 'VLSID 2025'), ('isscc-2025', 'ISSCC 2025'),
    ('iccad-2025', 'ICCAD 2025'), ('fccm-2025', 'FCCM 2025'),
]

# Short evidence labels for the coverage table. Full limits remain on each route.
ROUTE_EVIDENCE_STATUS = {
    'mlsys-2025': '61 papers with extracted source text; focused walkthroughs are bounded readings, not independent reproduction.',
    'osdi-2025': '53-paper working synthesis; named papers are reading leads and results remain author-reported.',
    'asplos-2025': 'Inspected passages and artifacts are distinguished from abstract-only records; no new measurements are claimed.',
    'nsdi-2026': '150-paper local synthesis; selected official abstracts and focused walkthroughs, not a claim-by-claim proceedings review.',
    'isca-2025': '17 papers with detailed local evaluation reviews among 135 records; the rest help identify papers to read, not assess their experiments.',
    'hpca-2025': 'Seven papers with detailed local evaluation reviews among 121 records; device measurements, simulations, and model estimates remain separate.',
    'micro-2025': '20 papers with detailed local evaluation reviews among 123 records; the rest have only abstracts or titles.',
    'sc-2025': '119 locally extracted texts with evaluation reviews, 312 abstract-only records, and two title-only records; 433 total.',
    'dac-2025': '32 source-backed records among 456 proceedings records; the other 424 support discovery only.',
    'date-2025': '15 source-backed records among 425 proceedings records; the other 410 support discovery only.',
    'vlsid-2025': 'Three papers with detailed local evaluation reviews; the other 95 records have only abstracts or titles.',
    'isscc-2025': 'One extracted ConvFormer source record; the other 257 records support discovery only.',
    'iccad-2025': 'One inspected RSizing paper; the 281-record local audit otherwise has structured abstracts only.',
    'fccm-2025': 'One externally inspected banked-memory manuscript; the 68-record local audit has no validated PDFs.',
}

ROUTES = [NSDI_ROUTE, ISCA_ROUTE, HPCA_ROUTE, MICRO_ROUTE, SC_ROUTE, DAC_ROUTE, DATE_ROUTE, VLSID_ROUTE, ISSCC_ROUTE, FCCM_ROUTE, ICCAD_ROUTE, {
    "id": "mlsys-2025",
    "title": "MLSys 2025: follow a model through the system that runs it",
    "status": "Eight-theme route with explicit subtheme teaching blocks and five focused walkthroughs (FlashInfer, QServe, SOLA, Photon, and MiLo). Broader paper walkthroughs and full-corpus synthesis remain unfinished.",
    "intro": "Begin with one request: input arrives, data is prepared, stored values are read, operations execute, and an answer returns. Training adds repeated updates and additional saved state. MLSys studies choices along this whole path. Its eight working themes below are an interpretation of the local conference analysis, not eight isolated kinds of machine. One change can affect several themes at once.",
    "evidence": "The local subtheme essay reports 61 conference papers with extracted source text, while the source-acquisition catalog records 56 full-text entries and five additional text-bearing records from other acquisition paths. Those counts describe available source material, not independent reproduction. This route summarizes the existing theme and subtheme essays. Five papers—FlashInfer, QServe, SOLA, Photon, and MiLo—also have focused learner walkthroughs with inspected source passages; the other named papers are reading leads, not equivalent full reviews. No measurements have been independently reproduced.",
    "themes": [
        {
            "title": "1. Change the work the device actually performs",
            "body": "A smaller mathematical expression need not become a faster program. The machine still has to read its inputs, arrange them, convert representations, and execute supported instructions. Treat a proposed reduction as a hypothesis about the complete execution path.",
            "worked_example": [
                "Original teaching execution: two consecutive operations each take three milliseconds of calculation and one of launch overhead. Between them, storing and reloading an intermediate result costs four more milliseconds. With sequential costs, total time is twelve milliseconds. A combined operation retaining the intermediate locally takes six milliseconds of calculation and one launch, totaling seven, provided the intermediate fits and the combined implementation preserves the required answer.",
                "Suppose that combined implementation needs so much temporary storage that calculation slows to ten milliseconds, and it must still transfer the intermediate at a four-millisecond cost. It now takes 10 + 1 + 4 = 15 milliseconds. Combining the operations removed one launch but did not establish a saving for the full path. The implementation must support the intended reuse, not merely describe the operations together.",
                "Skipping work has a similar accounting requirement. In a separate toy sum, visiting each of 100 entries costs one unit. A format retaining only 30 nonzero entries costs one unit of arithmetic work plus two units of index handling per retained entry, totaling 90. Retaining 50 costs 150 and loses. Skipping exact zeros preserves this exact-arithmetic sum; dropping nonzero entries would additionally require an error allowance. Lower operation count, lower traffic, and acceptable output are different checks.",
            ],
            "practice": {
                "question": "For the indexed sum, what is the largest integer number of retained entries that strictly beats the dense cost of 100 units? If representation conversion adds twenty units per use, how does that threshold change?",
                "answer": "Without conversion, require 3n < 100, so at most 33 entries. With conversion, require 20 + 3n < 100, so at most 26. These thresholds use the specified sequential costs and exact-zero omission. They do not establish that a particular device performs index handling at that cost or that an approximate omission meets the task's quality target.",
            },
            "subthemes": [
                ("Operator execution", "Arrange and combine operations to reuse data and avoid unnecessary intermediate storage. Ask whether an isolated operation's saving survives the surrounding program."),
                ("Numerical precision", "Use fewer representable values where the task tolerates it. Count conversion time and check output quality, not just the smaller stored model."),
                ("Skipping entries", "Avoid contributions that are zero or deliberately removed. Include the cost of locating the remaining entries and the effect of uneven work."),
            ],
            "reading": "Read the FlashInfer and FlexAttention discussions for execution choices, QServe and MiLo for representation choices, and the sparsity discussions for skipped work. Compare which cost each changes before comparing headline improvements.",
            "lessons": [("s6", "Compiler choices"), ("s2", "Number representations"), ("s5", "Skipping work")],
        },
        {
            "title": "2. Decide what to keep, reconstruct, or move",
            "body": "Memory has both a space limit and a movement cost. Keeping a value saves future work only if it will be reused while still valid. Evicting it makes room but can create reconstruction or transfer work later.",
            "worked_example": [
                "Original teaching training step: at its peak, parameters occupy 4 GB, gradients 4, update history 8, and saved intermediate values 6. These categories coexist, totaling 22 GB on a device with 20 GB available. Reducing saved intermediates to 3 GB by recalculating some values lowers the peak to 19 GB. It does not shrink the other sixteen GB. Assume the revised schedule has no additional peak allocation and preserves the required numerical behavior; those assumptions need checking in an implementation.",
                "Suppose recalculation adds 12 milliseconds to a 50-millisecond step. Another feasible schedule keeps the original saved values but transfers 2 GB out and later retrieves them. At 100 GB per second, four GB of sequential traffic takes 40 milliseconds, making that path 90 milliseconds versus recalculation's 62. At 400 GB per second it takes 10 milliseconds, making the transfer path 60. These stipulated schedules exclude startup and overlap; a storage saving alone does not identify the faster choice.",
                "Reusing processed context poses a related but different question. Suppose two requests have the same text prefix, but use different model parameters or different position assignments. That prefix match alone does not establish that saved intermediate values mean the same thing for both requests. A reuse key must include the conditions on which the saved state depends, or another mechanism must verify them. Finding stored bytes is not enough to establish that they are usable.",
            ],
            "practice": {
                "question": "At what transfer rate does the stipulated out-and-back schedule tie the twelve-millisecond recalculation cost? What if an extra two-GB temporary buffer is simultaneously needed by the nominally nineteen-GB recalculation schedule?",
                "answer": "Four GB divided by 0.012 seconds gives about 333.33 GB per second. Faster transfer favors the transfer path under these sequential assumptions. The extra temporary buffer raises recalculation's peak to 21 GB, exceeding the 20-GB capacity. Its twelve-millisecond overhead is irrelevant until a feasible schedule is supplied; peak space and elapsed time are separate checks.",
            },
            "subthemes": [
                ("Previously processed context", "Retain reusable state from earlier inputs. Ask how often the same context returns and what retrieval or decompression costs."),
                ("Training state", "Separate parameters, intermediate results, gradients, and update history. Recomputing one kind of state does not eliminate the others."),
                ("Placement and storage", "Choose where data lives and in what format. A device cannot benefit from a faster operation while waiting for its input."),
            ],
            "reading": "Compare Marconi's reuse discussion with HyC-LoRA and APOLLO's training-memory discussions. They address different kinds of state; a reduction in one is not evidence of a reduction in another.",
            "lessons": [("s3", "Memory"), ("s2", "Precision")],
        },
        {
            "title": "3. Divide work without losing the saving to exchange",
            "body": "Splitting a job creates boundaries across which results must travel. Choose a division that respects dependencies, reuse, and available connections. Equal device counts do not imply equal execution times.",
            "worked_example": [
                "Original teaching step: one device performs 24 milliseconds of calculation. On two devices, the calculation divides evenly into twelve milliseconds each, but the step also needs an eight-millisecond exchange. If the exchange follows calculation, completion takes 20 milliseconds. It is faster than 24, but not twice as fast. If a legal dependency schedule instead places six milliseconds of that exchange beside independent calculation, with separate resources and no slowdown, completion can fall to fourteen. The six hidden milliseconds require an actual schedule; an asynchronous call alone does not supply it.",
                "Now consider four devices, each with six milliseconds of calculation. Suppose the required exchange rises to twenty milliseconds and begins only after all calculations finish. Completion takes 26 milliseconds, slower than the one-device step. This is a stipulated workload and connection model, not a general scaling law. More devices can shorten the divided stage while enlarging a stage that every device must wait for.",
                "Longer inputs can change both terms. If the two-device calculation doubles to 24 milliseconds per device while exchange grows from eight to twenty, the sequential total becomes 44. The original six-millisecond overlap opportunity cannot simply be scaled or assumed to remain available. Recheck when each transferred value is produced, which device needs it next, and whether storage can hold it until then.",
            ],
            "practice": {
                "question": "For the original two-device case, suppose contention makes calculation take fifteen milliseconds and exchange ten, with only four milliseconds overlapping. Does this still beat the original one-device 24-millisecond step? What would happen without overlap?",
                "answer": "With the stated overlap, elapsed time is 15 + 10 − 4 = 21 milliseconds, still below 24. Without it, time is 25 and loses. This subtraction is valid only because the overlapping durations and slowed stage times are stipulated consistently. It is not permission to subtract an assumed overlap from isolated, interference-free measurements.",
            },
            "subthemes": [
                ("Partitioning", "Assign portions of the model or data to devices. Identify who owns each intermediate result and who needs it next."),
                ("Overlapping transfer and calculation", "Move completed data while independent work executes. Show both independence and resource availability on the timeline."),
                ("Long inputs", "Account for growing saved context and exchanges. Increasing input length can change the limiting resource rather than merely extend runtime proportionally."),
            ],
            "reading": "Use the context-parallelism discussions to trace ownership, and TileLink, PipeFill, and COMET as leads for overlap. A legal overlap opportunity is not proof that a shared link or memory connection can sustain it.",
            "lessons": [("dependencies-and-pipelines", "Dependencies"), ("s4", "Routes"), ("s7", "Coordination")],
        },
        {
            "title": "4. Choose whose work runs next",
            "body": "Arrival patterns and request sizes change while a service runs. A policy can raise total completed work and still make a particular user's experience worse. State the promised delay, fairness, or cost before judging the policy.",
            "worked_example": [
                "Original teaching queue: three requests arrive together. Their service times are eight, two, and two milliseconds on one device, with no switching cost. Serving them in that order completes them at 8, 10, and 12 milliseconds, with a mean response time of 10. Serving the two short requests first completes them at 2, 4, and 12, with a mean of 6. Total work and final completion time are unchanged; the distribution of waiting changes.",
                "Suppose the long request has an absolute deadline of time 9, while each short request has a deadline of time 12. The original order meets all three. Short-first misses the long request's deadline despite its lower mean response time. If the service promise is to meet those deadlines, a lower mean is not a better outcome. Different promises may justify different orders, but the policy must name its objective.",
                "Adding a device also requires checking shared resources. In a separate toy example, each of two devices can calculate ten requests per second, but a shared input connection supplies only twelve requests per second in total. The pair cannot sustain twenty completed requests per second when every request needs that input path. Moving queued work to the second device does not remove the supply limit, and any state-loading traffic uses capacity too unless it has a genuinely separate path.",
            ],
            "practice": {
                "question": "Return to the simultaneous three-request queue. Assume a second ready device can run the long request while the first runs the two short ones, with no shared-resource interference. What are the completion times and mean? What if preparing that second device first takes four milliseconds and the long request waits for it?",
                "answer": "With both devices ready, the long request finishes at 8 and the short ones at 2 and 4, giving a mean of 14/3, about 4.67 milliseconds; all deadlines are met. With four milliseconds of preparation, the long request finishes at 12 while the short ones still finish at 2 and 4. The mean becomes 6, and the long request misses its time-9 deadline. Allocation time is not the same as readiness to execute.",
            },
            "subthemes": [
                ("Request scheduling", "Choose batches and execution order using the current requests. Separate waiting for the first output from waiting for completion."),
                ("Changing allocations", "Move or resize jobs as needs change. Charge the time spent migrating state and preparing the new arrangement."),
                ("Shared-machine interference", "Measure how co-running work competes for memory, execution units, and other resources. Unused capacity on one resource does not establish spare capacity everywhere."),
            ],
            "reading": "Read SOLA and ThunderServe for serving decisions, Rubick and LAVA for allocation changes, and ProtoRAIL for shared-resource questions. Compare request traces and service targets before comparing outcomes.",
            "lessons": [("queues-and-batching", "Queues and batching"), ("s3", "Shared memory limits")],
        },
        {
            "title": "5. Include the work that supplies training data",
            "body": "The training loop can show a high calculation rate while spending much of its elapsed time waiting for examples. Changing the supply path can also change which examples the model sees. Both effects belong in the evaluation.",
            "worked_example": [
                "Original teaching pipeline: preparing one batch takes 12 milliseconds and training on it takes 8. One preparation worker and one training device operate independently, with enough buffering. For three batches, preparation runs 0–12, 12–24, and 24–36; training runs 12–20, 24–32, and 36–44. Completion takes 44 milliseconds. Halving training time to four milliseconds only reduces completion to 40; the device still waits for preparation between batches.",
                "Instead halve preparation time to six milliseconds while keeping training at eight. Prepared batches become available at 6, 12, and 18; training runs 6–14, 14–22, and 22–30. Completion is now 30 milliseconds. This change targets the stage limiting supply, but it is valid only if preparation still produces the required examples and labels. Silently dropping difficult records is a different workload, not merely a faster parser.",
                "Selecting fewer examples changes another obligation. Suppose a dataset has 1,000 examples, including ten from a rare case the deployed system must handle. A filter retains 500 examples but drops all ten rare cases. Reducing the number of training batches does not establish unchanged performance on that case. Likewise, if separate sites retain their data locally but only some participate in an update, the resulting example mix needs inspection. Local storage alone also supplies no argument about what an exchanged update reveals.",
            ],
            "practice": {
                "question": "With the faster six-millisecond preparation stage, let training take four milliseconds instead of eight. When do three batches finish? Does faster completion establish that filtering half the dataset preserves the learned result?",
                "answer": "Training runs 6–10, 12–16, and 18–22, finishing at 22 milliseconds. Preparation again limits the continuing supply rate. This schedule says nothing about the learned result after filtering. Compare the same required quality checks, including relevant rare cases, and count any additional training needed to meet them.",
            },
            "subthemes": [
                ("Selecting examples", "Choose data expected to help learning. Include selection cost and check whether rare cases required by deployment disappear."),
                ("Learning across separate sites", "Coordinate updates when data stays with different participants. Different availability and data distributions matter; local storage alone does not prove privacy."),
                ("Preparing inputs", "Parse, filter, arrange, and transfer examples. Verify that faster preparation preserves the intended contents and labels."),
            ],
            "reading": "Use the Photon walkthrough to follow model updates between sites, then compare the local discussions of subset selection, FedProphet, AdaParse, Youmu, and FLStore. These concern different parts of training: coordinating model updates is not the same as selecting examples, preparing inputs, or storing federated metadata. Follow one example from stored source to training input before deciding which stage limits progress.",
            "lessons": [("dependencies-and-pipelines", "Pipelines"), ("s3", "Storage and movement"), ("s9", "Privacy assumptions")],
        },
        {
            "title": "6. Fit sustained work within a real device",
            "body": "A device has limited storage, supported operations, cooling, and energy. A short peak measurement does not establish that the same behavior can continue for the workload's full duration.",
            "worked_example": [
                "Original teaching workload: a device must complete 1,000 requests and has enough queued work to stay busy. It serves 100 requests per second for the first two seconds, then only 50 per second for the rest of the run. Treat that rate change as stipulated; it is not a thermal model. The first 200 requests finish in two seconds and the remaining 800 need sixteen more. Total time is eighteen seconds, not the ten predicted by extending the initial rate to the whole run.",
                "Suppose device power is 60 watts in the initial phase and 40 afterward. Device energy is 60 × 2 + 40 × 16 = 760 joules. A second device sustains 60 requests per second at 45 watts, finishing in 50/3 seconds and using 750 joules. It has a lower initial rate but finishes this workload sooner and uses slightly less device energy. These figures exclude the rest of the system and assume equivalent accepted outputs.",
                "Now add two seconds and 100 joules of exclusive preparation for the second device, with no overlap and no such additional cost for the first. Its total becomes 56/3 seconds, about 18.67, and 850 joules. The ranking reverses again. A deployment comparison must include preparation, data movement, and unsupported work at the boundary where they actually occur; peak rate alone answers none of those questions.",
            ],
            "practice": {
                "question": "For only 100 requests, ignore the second device's extra preparation and use the same initially stated rates and powers. Which finishes sooner, and which uses less device energy?",
                "answer": "The first device remains in its initial phase, finishing in one second and using 60 joules. The second takes 100/60 = 5/3 seconds and uses 45 × 5/3 = 75 joules. The first wins both comparisons for this shorter workload. That does not contradict the 1,000-request result: the longer run crosses the first device's rate-change boundary.",
            },
            "subthemes": [
                ("Local execution", "Run within the device's memory and power limits. Account for the task rate and required answer quality."),
                ("Different processing units", "Assign work across CPUs, GPUs, and other units. Moving inputs to the nominally faster unit may cost more than its execution saving."),
                ("Hardware-aware movement", "Arrange computation around the data paths and operation types the target actually supports. Include unsupported-operation fallbacks."),
            ],
            "reading": "Use MEADOW, FlexInfer, and MAS-Attention as leads in the local essays. Keep each claim attached to its tested device and workload. Use the physical-limits lesson to check energy boundaries and sustained operation.",
            "lessons": [("s3", "Movement costs"), ("s6", "Execution plans"), ("physical-design", "Physical limits")],
        },
        {
            "title": "7. Check whether the result can be trusted",
            "body": "A systems claim needs a workload, a comparison, and a measurement boundary. It also needs an account of cases where predictions fail or an adversary acts. One average cannot stand in for all these obligations.",
            "worked_example": [
                "Original teaching admission rule: accept a request on a device if its predicted completion time is at most ten milliseconds. Predictions for four requests are 8, 9, 9, and 12 milliseconds. Actual times, if run there under the specified conditions, are 9, 11, 8, and 10. The rule accepts the first three, including one that misses the deadline, and rejects the fourth even though it would meet it. The mean absolute prediction error is only (1 + 2 + 1 + 2)/4 = 1.5 milliseconds, but that average does not describe the decisions at the deadline.",
                "Suppose a justified bound for this operating range says actual time never exceeds the prediction by more than two milliseconds. Accepting only predictions at most eight would then certify the deadline within that range. Observing a maximum underprediction of two in these four examples does not establish such a bound for future inputs. A safety margin must come from evidence appropriate to the promise, not from treating a small sample maximum as a universal limit.",
                "Prediction quality also does not establish software trust. In a separate hypothetical service, a model file includes a field naming code to execute when loaded. If the loader obeys that field without enforcing the deployment's allowed-code rule, a timing predictor cannot make the load safe. Follow the file through the component that interprets it and the restriction that component enforces. This describes an invented interface, not a claim about any particular model format or library.",
            ],
            "practice": {
                "question": "For the four requests, how many accepted requests miss the deadline and how many rejected requests would meet it? If a genuine two-millisecond upper-error bound applies, is prediction 8.5 sufficient for a ten-millisecond guarantee?",
                "answer": "One of three accepted requests misses, and the one rejected request would meet the deadline. These are observed counts, not future error probabilities. Prediction 8.5 plus the bound gives 10.5, so it cannot certify ten. That does not prove the request will be late; it says the available bound is insufficient for the guarantee.",
            },
            "subthemes": [
                ("Evaluation", "Include preparation and added overhead where the claim is end to end. Keep paper-reported measurements distinct from independent reproduction."),
                ("Uncertain predictions", "Ask how prediction errors affect resource decisions. A confidence estimate needs checking against observed errors under relevant conditions."),
                ("Software and artifact trust", "Follow dependencies, model files, parsers, and updates. Identify where an untrusted component can influence execution."),
            ],
            "reading": "Read the local AIOpsLab, uncertainty, and supply-chain discussions as different questions about trust. They do not jointly establish a general guarantee that a system is reliable or secure.",
            "lessons": [("s8", "Correctness evidence"), ("s9", "Threat models"), ("queues-and-batching", "Distributions and averages")],
        },
        {
            "title": "8. Expose model structure to the execution system",
            "body": "The interface between a model and its runtime determines which choices remain visible. Hiding structure can prevent specialization; specializing too narrowly can reject required future inputs.",
            "worked_example": [
                "Original teaching operation: for a sequence of four values, output position i must sum only values at positions zero through i. With inputs [1, 2, 4, 8], the required outputs are [1, 3, 7, 15]. A full four-by-four description contains sixteen possible input-to-output contributions, but only 1 + 2 + 3 + 4 = 10 are permitted by this rule. An execution system can avoid the six forbidden contributions if the interface exposes the rule in a form it understands.",
                "The interface must expose the actual rule, not a familiar label guessed from the application. If another call requires each output to sum all four inputs, every output must be 15. Reusing the restricted plan would produce [1, 3, 7, 15] and be wrong for the first three positions. Selecting a specialized plan requires a reliable description or check of the permitted relationships.",
                "Count execution costs too. Suppose each evaluated contribution costs one unit. A general implementation visits all sixteen positions, including checking which are permitted, at a total cost of sixteen units. A specialized plan evaluates ten contributions but needs eight units to prepare, costing eighteen for one use. If the same prepared plan serves two compatible uses, total cost is 28 instead of 32. If the rule changes between uses, preparation may recur. Removing a general fallback because the first workload did not exercise it would need a separate justification about all supported calls.",
            ],
            "practice": {
                "question": "For five positions under the same prefix-only rule, how many contributions are permitted and how many possible positions does the full square description contain? With the same eight-unit preparation cost and one-unit contribution costs, does specialization win on one use?",
                "answer": "The permitted count is 1 + 2 + 3 + 4 + 5 = 15, versus 25 positions in the full square. Specialization costs 8 + 15 = 23 units and wins against 25 under this stipulated model. This says nothing about floating-point reordering, an actual attention kernel, or a different allowed-position rule; those would require their own correctness and cost checks.",
            },
            "subthemes": [
                ("Programming and compilation", "Express the operation patterns a compiler needs to choose an implementation. Check both the generated execution and preserved behavior."),
                ("Model choices for service needs", "Change model behavior to make cost or scheduling more predictable. Say which quality requirement remains satisfied."),
                ("Removing unused software", "Eliminate capabilities a deployment does not need. Verify required inputs and failure handling before calling a component unnecessary."),
            ],
            "reading": "Compare the FlexAttention and XGrammar discussions with the hidden-bloat analysis. Exposing structure and deleting unused capabilities are different ways of changing the executable path, with different correctness obligations.",
            "lessons": [("s6", "Compilation"), ("s8", "Behavioral promises")],
        },
    ],
    "exercise": "Choose a paper from the local essays. Write five sentences: what work or state it changes; why that could help; what extra work it adds; which workload and machine were evaluated; and one condition under which the gain could disappear. If a needed fact is absent, record it as unknown. Do not fill it with a result from another paper.",
    "sources": [
        ("analysis/mlsys-2025-first-principles-theme-syntheses.md", "Existing eight-theme synthesis"),
        ("analysis/mlsys-2025-first-principles-subthemes.md", "Existing 24-subtheme essays and evidence boundary"),
        ("https://proceedings.mlsys.org/paper_files/paper/2025/file/185087ea328b4f03ea8fd0c8aa96f747-Paper-Conference.pdf", "Photon: local training, adaptive parallelism, and measured quality/wall-time tradeoffs"),
        ("https://proceedings.mlsys.org/paper_files/paper/2025/file/9032e5c9ec394ce768a2fa9bdc56af6c-Paper-Conference.pdf", "MiLo: quantize-then-compensate, adaptive rank choices, and measured INT3 kernel results"),
    ],
}]

ROUTES.append({
    "id": "osdi-2025",
    "title": "OSDI 2025: preserve the service's promise as execution changes",
    "status": "Focused Mirage, Tigon, BlitzScale, Picsou, Fork in the Road, and EMT walkthroughs have local primary-source reviews. The other OSDI records have machine-selected passages or bounded catalog evidence that still needs manual confirmation; this route is not a paper-by-paper review.",
    "intro": "Follow an operation that changes state: a request arrives, code runs, memory and devices are shared, an update becomes durable, and a reply is delivered. What may the caller assume at each point? OSDI's eight working themes connect performance choices to that question. Compared with the MLSys route, pay particular attention to ownership, permitted observations, and what remains true after a crash or retry.",
    "evidence": "The local synthesis covers a 53-paper OSDI 2025 corpus and explicitly calls these themes a working interpretation, not an official classification. This route restates that analysis for learners. The six named walkthroughs include local primary-source evidence maps; their measurements remain author-reported and were not independently reproduced. Other named papers are reading leads whose selected passages still require manual confirmation. Some subthemes, especially artifact trust, express cross-paper questions rather than a verified common mechanism.",
    "themes": [
        {
            "title": "1. Translate a program without changing its promise",
            "body": "The program describes required behavior, while an implementation must choose instructions, layouts, and resource use. Translation and specialization can save repeated work, but their preparation cost and restrictions remain part of the decision. Measurements and performance models help compare the choices only when they include the setup and execution path that matter to the caller.",
            "worked_example": [
                "Original teaching interface: a function receives [2, 5] and promises to return a new array with one added to each element, leaving the input unchanged. A caller keeps another reference to the input. A proposed fast implementation edits the input in place and returns it. The returned numbers [3, 6] look right, but the caller's saved reference now also sees [3, 6]. The promised original [2, 5] has disappeared. Checking only the returned numbers misses the broken interface.",
                "An implementation may use the in-place path when the contract permits it and ownership information establishes that no required observer needs the original. Otherwise it must preserve the input or choose another path. The ownership fact is part of the justification for the optimization. A frequently true assumption about callers cannot replace that fact for a call where it fails.",
                "Measurement can hide the remaining tradeoff. Suppose a valid allocating version takes eight time units and a valid exclusive-ownership version takes five, including its ownership check. Instrumentation that adds one unit to the first but four to the second makes both observed totals nine. The recorded totals describe execution with that instrumentation. Inferring equal uninstrumented cost would require understanding its unequal effect.",
            ],
            "practice": {
                "question": "What should a test observe to distinguish the invalid in-place replacement from the promised operation? Is accepting an exclusive-ownership path equivalent to dropping the original requirement?",
                "answer": "Retain a second reference to the input, call the function, then check both the returned array and the values visible through that reference. A test of object identity can also check the stated new-array requirement. An exclusive-ownership path is acceptable only if the interface permits that behavior or the transformation preserves every observation the interface requires. Lack of another reader alone does not erase an explicit identity promise.",
            },
            "subthemes": [
                ("Compiler and runtime translation", "Keep required behavior intact while changing the executable form. Count search, rejected candidates, compilation, and fallback as well as execution."),
                ("Specialized execution", "Use known operation patterns to avoid general-purpose work. Identify which inputs fit the specialized path and what happens outside it."),
                ("Observing and modeling performance", "Measure enough to choose an implementation without obscuring the effect being studied. Separate measurement overhead, noise, and bias; overhead alone does not determine resolution."),
            ],
            "reading": "Start with Mirage and QiMeng-Xpiler for translation choices, then KPerfIR and Neutrino for the evidence used to understand execution. A fast generated operation does not establish that preparation pays off for a one-time request.",
            "lessons": [("s6", "Execution plans"), ("s8", "Required behavior")],
        },
        {
            "title": "2. Make stored state reachable at an acceptable cost",
            "body": "State can fit somewhere and still be too expensive to use. Its location determines lookup, movement, bookkeeping, and recovery costs. Ask where the next required value lives, not just how much total memory exists.",
            "worked_example": [
                "Original teaching placement: four separate 64-KiB regions each contain one frequently read 4-KiB page. Moving whole regions keeps 256 KiB locally. Moving only the four read pages keeps 16 KiB. Assume either method needs a 64-byte tracking entry per retained unit. Their tracked footprints are 256.25 and 16.25 KiB respectively. A 32-KiB budget can hold the fine placement but cannot hold all four whole regions. One KiB here means 1,024 bytes.",
                "Change the workload so that every page of all four regions is read. The fine placement now needs 64 page entries, occupying four KiB; the coarse placement still needs four entries, occupying 0.25 KiB. Both retain 256 KiB of data. Fine placement saved space in the first workload because most of each region was untouched. It is not inherently cheaper once the read coverage changes.",
                "Placement also creates a lookup path. Suppose reading a local value costs one microsecond, the fine placement adds two microseconds to locate it, and a remote read otherwise costs ten. A successful local read then costs three and saves seven. A local miss that still pays the lookup before the remote read costs twelve. With half hits and half misses, mean cost is 7.5 microseconds. Include that miss path and any later loading or eviction when choosing what to keep.",
                "Access count alone can also mislead. In one controlled test from Tiered Memory Management Beyond Hotness, a stream of independent reads touched its pages 13.6 times as often as a stream that followed a chain of dependent addresses. Yet putting the more frequently touched pages in fast memory and the chain's pages in slower memory left combined performance at 52.4% of the all-fast setup. The many independent reads could overlap while the processor worked; each step in the chain had to wait for the previous address. So count the waiting an access exposes, not just how often it occurs. These numbers describe that paper's benchmark, not every workload or tiered-memory system.",
            ],
            "practice": {
                "question": "Under the three-microsecond hit and twelve-microsecond miss model, what hit fraction makes the mean strictly smaller than always reading remotely in ten microseconds?",
                "answer": "With hit fraction h, mean time is 3h + 12(1 − h) = 12 − 9h. It beats ten when h exceeds 2/9, about 22.2%. This mean says nothing about a deadline on the twelve-microsecond miss path, and the calculation excludes loading and eviction costs not specified in the model.",
            },
            "subthemes": [
                ("Address translation and placement", "Find the physical data associated with an address and choose where it should reside. Fine-grained placement can save space while increasing metadata work."),
                ("Layout and redundancy", "Organize data for access and reconstruction after failure. A layout with fast reads may require expensive repair traffic."),
                ("Caching and lifetime", "Keep values whose expected reuse justifies their space. Include loading and eviction, and ask how quickly the prediction becomes obsolete."),
            ],
            "reading": "Compare Tigon, FineMem, and Tiered Memory Management with Okapi and Stripeless for where data is placed and what each access costs. Add EMT to ask a separate but connected question: can the OS manage a different address-translation design without rewriting its general memory code? Faster address translation is not the same claim as faster access to stored data. The local subtheme essay identifies Tigon's CXL setup as emulated; EMT's new-MMU results also use emulation and simulation, not fabricated hardware. Keep those boundaries attached to any hardware conclusion.",
            "lessons": [("s3", "Memory costs"), ("s7", "Saved and replicated state")],
        },
        {
            "title": "3. Move results and agree on what happened",
            "body": "A message carries more than bytes: its recipient must know how to interpret it, whether it repeats earlier work, and when it is safe to act. Transfer speed and agreement rules answer different questions.",
            "worked_example": [
                "Original teaching service: a counter starts at zero. A client sends request R to increment it once. The server increments to one and sends success, but the reply is lost. The client retries R. If the server treats every arrival as a new operation, the counter becomes two. Every delivered message was intact; the error arose from confusing a repeated message with a second intended operation.",
                "Remembering completed request identifiers can distinguish the retry, but the remembered identifier and the counter update must survive consistently under the failure model. If a crash preserves the increment but loses R's completion record, the retry can increment again. If only the completion record survives, a retry may report success for an increment that disappeared. A reply promise therefore needs a rule for committing and recovering both pieces of state.",
                "Replication adds a version question. Suppose the primary has counter value one and a replica still has zero. Returning zero to a client that was promised it would observe its acknowledged increment violates that promise. The service can wait for the required copy or direct the read to a suitable copy. A different interface may explicitly allow older reads. Faster transfer helps shorten the wait but does not define which version is allowed.",
                "Picsou studies a related boundary: sending a committed change from one replicated service to another. In its failure model, the sender needs evidence that at least one correct server in the receiving group got each message; one server saying ‘I got it’ is not enough. Its QUACK is a compact group confirmation covering messages up to a numbered point. If the sender sees that same point again, it can treat the next message as possibly missing and resend it. This confirms delivery under Picsou’s rule—not that the receiving service has committed the change, nor that its clients can read it. Those are separate promises, each needing its own evidence.",
            ],
            "practice": {
                "question": "A client times out and does not know whether R executed. Is sending a fresh identifier S an equivalent retry? Which fact must recovery retain to answer R consistently?",
                "answer": "S names a new logical request and may legitimately cause another increment. To retry the same intended operation, the client must retain R under this interface. Recovery needs R's outcome together with the corresponding committed state, or another protocol that establishes an equivalent fact. Timeout alone cannot reveal whether the earlier operation executed.",
            },
            "subthemes": [
                ("Distributed communication", "Account for bytes, ordering, acknowledgements, and retries. Multiple interfaces help only if the surrounding path can use them."),
                ("Pipelining and overlap", "Place transfers beside genuinely independent calculation. Include filling, draining, buffering, and contention for shared resources."),
                ("Replication and consistency", "Define which version a reader may observe and what happens when copies disagree. A stale answer may be permitted by one service and forbidden by another."),
            ],
            "reading": "Use FuseLink for a multi-interface reading lead, ZEN for reducing communicated updates, and Picsou, Mako, and Skybridge for differing coordination promises. Do not translate fewer bytes into unchanged training quality or stronger consistency without evidence.",
            "lessons": [("s4", "Routes"), ("dependencies-and-pipelines", "Overlap"), ("s7", "Coordination")],
        },
        {
            "title": "4. Change allocation only when the change is worth its cost",
            "body": "An allocation decision changes the state the next decision will observe. Moving a job consumes bandwidth and can discard cached data that the job will need again. Keeping it in place may instead prolong interference. The comparison must include both consequences.",
            "worked_example": [
                "Original teaching workload: each remaining unit of a job takes five milliseconds on its current worker and three on a destination worker. Moving its required state pauses the job for twelve milliseconds. With n units left and sequential execution, staying costs 5n and moving costs 12 + 3n. Six units tie at thirty milliseconds; seven favor moving, at 33 versus 35. The destination's faster steady execution helps only after movement is repaid.",
                "Now suppose that migration also delays another user's completion by eight milliseconds because the transfer uses a shared link. For seven remaining units, the migrating job saves two milliseconds while the other user loses eight. Under an objective minimizing the sum of the two completion times, the move is six milliseconds worse. A priority policy might still choose it, but that policy must state whose delay it is willing to increase.",
                "A controller can also undo its own saving by moving the job back after a noisy measurement. Two twelve-millisecond moves consume twenty-four milliseconds before counting any lost cached state. A policy needs evidence about how long the favorable condition will persist and a rule for reassessing it. The first measurement does not guarantee that the target remains the faster location.",
                "Real systems also choose what counts as movable work. XSched makes accelerator tasks preemptible through a shared command-queue interface, while accounting for the fact that different accelerator generations expose different scheduling capabilities. BlitzScale changes the unit of model scale-out: it can send individual layers to new GPUs and start their work before every parameter has finished loading. These are different designs, not one shared mechanism. Their common lesson is narrower: allocation can happen sooner or more precisely only when the system identifies a safe unit to move and makes its readiness visible. Moving a task, declaring a worker ready, and meeting a user-facing deadline are separate events.",
            ],
            "practice": {
                "question": "If the other user's extra delay remains eight milliseconds, how many units must remain for migration to strictly improve the sum of completion times? Assume all other costs stay fixed.",
                "answer": "Require 12 + 3n + 8 < 5n, so n must exceed ten. Eleven units give a combined counted cost of 53 instead of 55. This condition concerns the stated sum; it does not establish fairness or that either user's individual deadline is met.",
            },
            "subthemes": [
                ("Scheduling and resource allocation", "Choose shares and placement using the actual resource demands. Name the fairness rule and charge migration or preemption overhead."),
                ("Serving and capacity changes", "Bring new workers online with the model state they need. A worker counted as allocated may not yet be ready to serve."),
                ("Contention and slow workers", "Determine which shared resource or lagging participant delays completion. An actionable diagnosis names a possible intervention and the work or fairness cost it adds."),
            ],
            "reading": "Compare Kamino, XSched, and DeDe as allocation leads with BlitzScale's startup problem and WLB-LLM's work-balancing problem. They change different costs and need different workload traces to support their claims.",
            "lessons": [("queues-and-batching", "Scheduling"), ("s7", "Slow participants")],
        },
        {
            "title": "5. Decide what survives before failure happens",
            "body": "Recovery depends on information retained during normal operation. The system needs to distinguish completed work from unfinished or repeated work. A fast restart is not sufficient if it exposes a state the caller was never allowed to see.",
            "worked_table": {
                "caption": "Crash states in the teaching protocol, before old-version cleanup. Durable means retained through the stipulated crash. The last row is the state the ordering rule must exclude.",
                "headings": ["Durable payloads", "Durable index", "What recovery can reach"],
                "rows": [
                    ["Old only", "Old", "Old version"],
                    ["Old and new", "Old", "Old version"],
                    ["Old and new", "New", "New version"],
                    ["Old only", "New", "Missing payload; forbidden"],
                ],
            },
            "table_after_paragraph": 2,
            "worked_example": [
                "Original teaching object: its payload and an index pointing to that payload must describe the same version. Version one is already durable. An update writes a new payload, then changes the index. If the new index can survive while the new payload does not, recovery follows a pointer to missing data. The program's issue order alone is insufficient when the storage interface permits the writes to become durable in a different order.",
                "For a simplified protocol, retain the old version, write the new payload, and wait for confirmation that it is durable before publishing a durable index change. Assume the index publication is atomic, storage honors these confirmations, and readers obey the publication rule. Before publication they see the old version; after it they can reach the new one. Reclaiming the old payload must also wait until no reader or recovery path still requires it. Those assumptions are part of the protocol, not properties supplied by ordinary assignment syntax.",
                "The teaching protocol makes safety by ordering two durable steps. WOFS, the model behind the OSDI file system WOLVES, takes a different route for metadata in persistent memory: it packages the metadata for a file operation with a checksum and writes that package once at a defined durability point. The idea is to make each package recoverable as a unit, rather than repair a half-finished chain of in-place metadata edits. That does not make crashes disappear: the system must still define package contents, translate packages into normal file operations, and recover or reclaim them correctly. The shared principle is to make the set of states recovery may observe explicit; the mechanisms are not interchangeable.",
                "Suppose durable payload confirmation takes four milliseconds and index publication two, sequentially. A durable-success reply takes at least six milliseconds under this model. Replying after the first four acknowledges a different state unless the service supplies another mechanism to recover publication. A replay log must capture the inputs and ordering choices required to reconstruct the operation; a timestamp alone may omit a remote response that changed the result.",
                "The same reasoning separates safety from progress in replication. In a simplified crash-only example, three replicas begin at version zero and version one is acknowledged only after two replicas confirm that it is durable. If replica A then fails, replica B still holds the acknowledged version. If the system instead replies after only A confirms and A is lost, the acknowledged update disappears. Requiring all three confirmations can preserve more copies but prevents progress whenever even one replica is unreachable. This example assumes no concurrent writes; real protocols must also define version ordering and behavior during network partitions. A count of acknowledgements by itself is not a complete protocol.",
            ],
            "practice": {
                "question": "A crash occurs after the new payload is durable but before the index changes. Which version can a reader safely find, and what would recovery need to finish the update? For the three-replica example, what is the cost of requiring all three confirmations?",
                "answer": "The durable index still identifies the old version, so retaining that version makes the old result reachable. The unreferenced new payload alone does not prove that publication was intended or acknowledged. Completing the update during recovery requires a recorded intent and a defined recovery rule, including how it relates to the caller's retry. Requiring all three replica confirmations means an unavailable replica can stop a write even when two copies are reachable; requiring only one can lose an acknowledged update if that copy fails. Leaving the old committed version visible is consistent with the simplified publication protocol.",
            },
            "subthemes": [
                ("Interrupted durable updates", "Identify which combinations of writes can survive a crash and how recovery chooses a valid state. Include normal-path recording cost."),
                ("Fault-tolerant protocols", "Preserve a stated property despite specified message or participant failures. Keeping a result safe does not guarantee that progress continues."),
                ("Debugging and replay", "Record the information needed to reproduce a failure. Count recording and storage cost, and identify external state the replay does not capture."),
            ],
            "reading": "Read F2FSJ and WOFS for durable-update organization, Basilisk for protocol properties, and KRR for replay. Semantic Checkers and Training with Confidence are separate leads for detecting bad behavior; detection does not automatically provide repair.",
            "lessons": [("s8", "Correctness and detection"), ("s7", "Recovery")],
        },
        {
            "title": "6. Keep each part within its permissions and limits",
            "body": "A service passes data to plugins and helpers, runs code written elsewhere, and loads updates. Its rules must hold at each place that can read data, change state, or use resources. Checking only the first request leaves later actions unchecked.",
            "worked_example": [
                "Original teaching service: a plugin may read a public report but must never receive a private report. The service checks the public name, then sends that name to a helper that resolves it later. If another participant can change what the name refers to between the check and resolution, the helper may open a private object even though the first check succeeded. The protected object must remain the one that was authorized throughout use.",
                "A possible interface passes a stable reference to the authorized object and enforces its permitted operations at the helper. Whether that works depends on who can create, change, and use the reference. Merely checking the same mutable name twice still leaves a gap if it can change again. This is an invented object-resolution model, not an assessment of a particular plugin platform.",
                "Access control does not settle resource use. A plugin allowed only to read public data might repeatedly allocate one-megabyte buffers. A thousand live buffers use roughly a gigabyte even if every read is authorized. If the service promises bounded memory use, it needs an enforced allocation budget and a defined response when the budget is exhausted. Similarly, authenticating the source of a plugin does not prove its behavior is acceptable.",
                "Evidence about a program answers different questions. Can reviewers obtain the submitted artifact? Is it documented, complete, and usable for the work the paper describes? Can they use it to reproduce the paper's main results? OSDI's artifact review treats availability, functionality, and reproduced results as separate claims. Even reproducing a paper's result does not establish that a live service runs that exact build or that it enforces your access policy; those require separate identity and behavior checks.",
                "Privacy has a similar boundary: encrypting a record hides its contents, but a server may still observe which stored pieces a query touches. Repeatedly looking up the same small group of records can reveal a pattern even when every byte is encrypted. Compass addresses this for semantic search by hiding the search's access pattern as well as protecting the data, query, and result under its stated threat model. Weave tackles a different workload—cloud analytics—and designs for hidden access patterns there. They are examples of a broader rule, not interchangeable protections: name what the observer can see, then check that the proposed mechanism covers that observation without silently excluding the workload you need.",
            ],
            "practice": {
                "question": "A helper enforces a 100-MB buffer budget but never checks which object a plugin reads. Has it enforced both the private-report rule and bounded buffer use? If an artifact is publicly available and a paper result was reproduced from it, does that prove a service runs the same build?",
                "answer": "It has addressed buffer allocation under the stated accounting, but the object-access rule remains unenforced. The two promises govern different effects and require their own checks. One thousand live one-megabyte buffers are roughly a gigabyte, so the budget also needs to cover the memory the service claims to limit. Public availability and reproduction support specific claims about the submitted artifact; they do not identify the binary running in a service. That requires a separate link from the reviewed build to the deployed one.",
            },
            "subthemes": [
                ("What can someone learn?", "Trace who can read sensitive data and what they can infer from outputs, timing, or access patterns."),
                ("Limit what plugins and helpers can do", "State which data, memory, calls, and resources each component may use. Blocking one action does not block every other effect."),
                ("Which exact build was checked?", "Link the source, tested package, and deployed version. A public repository or research result does not identify the code a service is running."),
            ],
            "reading": "Compare Paralegal, Weave, and Compass for different privacy questions; use Omniglot and the Extension Interface Model for boundaries around foreign code and plugins. Then compare OSDI's separate artifact badges: availability, functionality, and reproduced results answer different questions. None alone proves a deployed service is running the reviewed build or enforces your policy.",
            "lessons": [("s9", "Attacker access and observations"), ("s8", "Scope of evidence")],
        },
        {
            "title": "7. Measure the conditions before predicting performance",
            "body": "A runtime number describes one run under a particular setup; it is not a fixed property of the machine. If the workload or starting state changes, the time may change too. Measure the conditions that matter to the decision, then say what your timing does and does not include.",
            "worked_example": [
                "Original teaching traces: nine requests finish in two milliseconds and one takes twenty. Their mean is 3.8 milliseconds, but a five-millisecond deadline is missed once. Another system takes four milliseconds for every request. It has a slightly worse mean and meets all ten deadlines. The preferred system depends on which promise the application makes.",
                "Now separate starting state. Suppose the long request was the only one that had to initialize the service. If a later workload has five warm starts and five cold starts, the original two- and twenty-millisecond costs give a mean of eleven. Reusing 3.8 as a prediction would silently carry over the earlier mix of warm and cold starts. Measure how often each state occurs as well as the time in that state.",
                "A timer around the request handler may begin after queueing and initialization. Its two-millisecond reading can be accurate while the user waited twenty. Name the start and end event for each measurement, and connect them on the same request. Adding unrelated average stage times cannot establish an individual request's maximum delay.",
                "Even a hardware counter can give a misleadingly precise answer. A processor has a limited number of counter slots, while a profiler may want to track more events than fit at once. Time-sharing the slots means different events are observed at different moments; if the program changes phase between those moments, the combined estimates may not describe one consistent run. Tintin treats this as measurement uncertainty: it works to reduce the error, reports remaining uncertainty to the program using the profile, and provides an operating-system interface for different profiling needs. The practical question is not only ‘what number did the profiler report?’ but ‘how uncertain is it, which event may be undercounted, and would that uncertainty change the decision?’",
            ],
            "practice": {
                "question": "With warm requests taking two milliseconds and cold requests twenty, what cold-request fraction keeps the mean at most five? Does that mean guarantee a five-millisecond deadline for each request?",
                "answer": "For cold fraction c, mean delay is 2(1 − c) + 20c = 2 + 18c. It is at most five when c is at most 1/6. Every cold request still takes twenty and misses the individual deadline. The mean requirement and the per-request requirement are distinct.",
            },
            "subthemes": [
                ("How much does it change?", "Repeat the measurement across the machines and workloads that matter; report how far the results move."),
                ("From request to answer", "Count startup, queueing, time to first output, and full completion. Choose the delay that matches the service promise."),
                ("What exactly was timed?", "Name the timer's start and end events and what its count includes. Comparing different intervals does not establish a speedup."),
            ],
            "reading": "Use Tintin for uncertainty in hardware-counter measurements, the straggler study for causes that change across workers and time, and Fork in the Road for cold-start work across a production workflow. Serial Performance Optimization organizes ways to remove, replace, or reorder serial work; it does not supply the timing values in these exercises. A result from one workload or starting state needs new evidence before being used to predict another.",
            "lessons": [("s1", "Timing boundaries"), ("queues-and-batching", "Delay distributions")],
        },
        {
            "title": "8. Count the whole cost of a usable result",
            "body": "Compare what the user receives with the time and resources needed to provide it. A faster step may barely matter if waiting, preparation, or checking still takes most of the time. Keeping a worker ready can save delay while using energy before requests arrive.",
            "worked_example": [
                "Original teaching request: startup takes six milliseconds, queueing four, execution three, and checking and delivery two. If these stages happen one after another, the user receives a usable answer after fifteen milliseconds. Halving execution reduces the total to 13.5 milliseconds—not to half—because the other stages stay the same.",
                "Keeping a worker ready removes startup for requests that reach it, reducing delay to nine milliseconds without changing execution. Suppose the idle worker draws eight watts for ten seconds, then handles twenty requests before shutdown. The idle interval uses eighty joules. Dividing that shared cost evenly assigns four joules to each request; it does not mean each request physically used four extra joules. With only four requests, the assigned idle cost rises to twenty joules each even though the stipulated request delay stays nine milliseconds.",
                "After an update, a worker process may still be running but hold the wrong model or configuration. The service must decide whether new requests wait for reload, may use the old version, or should fail. A benchmark that starts after every worker is prepared does not include this update and readiness work; it answers a narrower question than a cold-start test.",
                "Fork in the Road shows why these stages must be followed as one workflow: its production study identifies delay in the service's control path, contention for resources, and user-code initialization. An optimization to one startup step can leave the caller waiting on either of the others, especially when many functions start together. The paper reports that prior techniques still left cold starts in the hundreds of milliseconds to seconds on the studied Ant Group platform; its own production system reports reducing them to milliseconds. Treat those as results for that deployment, not as a universal startup time. When comparing systems, keep the request boundary, concurrency, readiness definition, and latency percentile aligned; report resource use separately rather than converting it into latency by assumption.",
            ],
            "practice": {
                "question": "If only four requests use the worker during the same ten-second idle interval, what idle energy is allocated per request? Does the nine-millisecond warm-request time necessarily change?",
                "answer": "Eighty joules divided by four is twenty joules per request. The stipulated warm-request latency can remain nine milliseconds: the allocation of idle cost changed while that request path did not. Compare time, energy, readiness, and accepted output under the boundary relevant to the caller's goal.",
            },
            "subthemes": [
                ("Make the parts fit together", "Show which software decision relies on a hardware ability and how the interface lets them work together. A fast component is useless if another part cannot feed or control it."),
                ("Count setup and upkeep", "Include startup, loading, updates, health checks, and restart before calling a worker ready. Say what happens when required state or resources are missing."),
                ("Count from request to usable answer", "Follow arrival through processing and checks. Report delay, energy, and failures separately instead of blending unlike results into one score."),
            ],
            "reading": "Use PipeThreader for software schedules that rely on specialized GPU hardware, MettEagle for container startup and application behavior, and BlitzScale for model loading during live scale-up. Fork in the Road (theme 7) examines production cold starts. Their systems and measurements differ, so do not combine their numbers as if they were one service. The timeline and energy allocation here are original teaching examples.",
            "lessons": [("s1", "Follow a request"), ("s6", "Preparation costs"), ("s8", "Accepted results")],
        },
    ],
    "exercise": "Choose one paper from this route. Trace a request or update from its input through work, movement, sharing, checks, and the result the user can rely on. At each boundary write what must remain true, what state or resource changes, what could fail or be delayed, and which event starts and stops the measurement. Add only durations that really occur one after another; mark overlapping work separately. Include setup and shared idle cost, and state how you allocate that cost. Compare your trace with the paper’s tested boundary. Mark missing evidence instead of joining numbers from unrelated papers. Finally propose one change, name the predicted measurable improvement, and state one observation that would prove your prediction wrong.",
    "sources": [
        ("analysis/osdi-2025-first-principles-theme-syntheses.md", "OSDI eight-theme synthesis and end-to-end derivations"),
        ("analysis/osdi-2025-first-principles-subthemes.md", "OSDI 24-subtheme essays with paper-record links"),
        ("https://www.usenix.org/system/files/osdi25-liu.pdf#page=3", "Tiered Memory Management Beyond Hotness, section 2.1: access frequency and exposed waiting"),
        ("https://www.usenix.org/system/files/osdi25-frank.pdf", "Picsou: cross-cluster delivery guarantee and QUACK acknowledgements"),
        ("https://www.usenix.org/conference/osdi25/presentation/shen-weihang", "XSched: preemptible command queues across diverse accelerators"),
        ("https://www.usenix.org/conference/osdi25/presentation/zhang-dingyan", "BlitzScale: layer-level scale-out before all parameters finish loading"),
        ("https://www.usenix.org/conference/osdi25/presentation/pan", "WOLVES/WOFS: checksum-protected metadata packages and synchronous crash recovery"),
        ("https://www.usenix.org/conference/osdi25/presentation/zhu-jinhao", "Compass: encrypted semantic search and access-pattern protection"),
        ("https://www.usenix.org/conference/osdi25/presentation/soleimani", "Weave: oblivious analytics for cloud-hosted sensitive data"),
        ("https://www.usenix.org/conference/osdi25/presentation/li", "Tintin: hardware-counter multiplexing errors and reported profiling uncertainty"),
        ("https://www.usenix.org/conference/osdi25/presentation/chai-xiaohu", "Fork in the Road: production cold-start workflow, control path, contention, and initialization"),
        ("https://www.usenix.org/conference/osdi25/presentation/chai-siyuan", "EMT: Linux support, interface overhead, and simulated memory-translation architectures"),
        ("https://www.wisdom.weizmann.ac.il/~padon/mirage-osdi2025.pdf", "Mirage: multi-level tensor-program search, equivalence checking, and GPU evaluation"),
        ("https://www.usenix.org/system/files/osdi25-huang-yibo.pdf", "Tigon: cross-host active tuples, CXL placement, transaction protocols, and emulated-pod results"),
    ],
})

ROUTES.append({
    "id": "asplos-2025",
    "title": "ASPLOS 2025: follow a design choice across software and hardware",
    "status": "Theme route, explicit subtheme teaching blocks, and focused CXL permission-proof, PMVerify crash-analysis, EXIST observability, Past-Future request-scheduling, Teola end-to-end orchestration, CIPHERMATCH encrypted-near-data, vAttention virtual-memory, COMET mixed-precision, Micro Blossom heterogeneous-decoding, PipeLLM confidential-pipeline, PartIR compiler-partitioning, TAPAS thermal-power scheduling, PCcheck checkpointing, Cascade dependency-aware training, Mint full-coverage tracing, PowerMove movement-aware compilation, PUSHtap unified-layout, CoServe dependency-aware serving, fine-grained DVFS energy-control, and BTrace complete-tracing walkthroughs included. Other paper walkthroughs and outstanding full-text checks remain unfinished.",
    "intro": "Start with a choice that appears local: combine two operations, compress stored values, or assign work to another device. Then follow what changes elsewhere. Temporary storage may grow, transfers may move, and a different worker may become the one everyone waits for. ASPLOS connects these choices across programming, operating systems, and architecture. The eight themes below organize those connections rather than classify papers into disjoint boxes.",
    "evidence": "The local essays distinguish inspected source passages, abstract-only records, and artifacts. They warn that automatic paper assignments do not establish a mechanism. This route preserves those limits and reports no new performance measurements. A source file's presence does not mean that its entire evaluation has been reviewed; consult the cited subtheme essay for the inspected portion.",
    "themes": [
        {
            "title": "1. Keep the facts needed for the next decision visible",
            "body": "An interface must hide enough detail to remain usable while exposing enough to support good decisions. A scheduler cannot use a fact that has disappeared during translation, but exposing a particular machine layout can make software dependent on it.",
            "subthemes": [
                ("Program and data meaning", "Define what an observer may see, including intermediate observations and acknowledged updates. Matching the final array alone may not preserve a concurrent program's promise."),
                ("Interfaces and abstractions", "Distinguish a guarantee from an estimate. Predicted free space is information for planning, not capacity reserved for the caller."),
                ("Intermediate compiler forms", "Retain loops, blocks, or operations until decisions that need their structure have been made. Eventually commit to concrete storage and instructions."),
            ],
            "reading": "Read the Coach discussion for allocation promises and the Plaid and BlockDepend discussions for retained computation structure. BlockDepend is presented through an abstract record; do not infer unreviewed implementation details from the conceptual explanation.",
            "worked_example": [
                "Consider an invented interface to a 12 MB temporary-storage pool. Two callers each ask how much space is free. Both receive the answer 12 MB, then each plans an 8 MB allocation. Each plan fits the observation, but the combined 16 MB does not fit the pool. A query describes a moment; it does not reserve a future allocation. If both callers were promised successful allocation, the interface has promised more than it can provide.",
                "A reservation operation can instead check and subtract space as one indivisible step. The first 8 MB reservation leaves 4 MB; the second must wait or fail. This makes the promise enforceable, but the program needs a defined response to failure. Silently discarding part of an array would not be an acceptable response. A predicted release time may help decide whether to wait, but it is still not a guarantee that space will be free then.",
                "The compiler needs comparable clarity about shared values. Suppose iteration i reads a[i−1] and writes a[i]. Successive iterations depend on earlier writes. A representation retaining those read and write relationships can explain why unrestricted parallel execution is invalid. Merely knowing that there are eight iterations is insufficient. The relevant information is the fact needed to justify a decision, not every available implementation detail.",
                "A hardware interface also has to make the facts that govern shared state explicit. In their CXL.cache study, Tan, Donaldson, and Wickerson turn the standard's prose into a state-transition model: it records device cache states and messages in flight, then defines which message events may change that state. They use the model to check required message-order scenarios and prove a single-writer/multiple-reader coherence property. That is stronger than saying ‘the caches agree’ because it names a rule and proves it over modeled transitions. But the theorem remains about that model: their proof omits deadlock and progress properties and restricts its modeled system to two devices and one location. The result can guide a reader only if its guarantee and boundary stay attached to it.",
            ],
            "practice": {
                "question": "Three callers each require 5 MB from the 12 MB pool. Reservations are indivisible and successful callers keep their space until completion. How many can be promised immediate space? Does adding an accurate estimate of each caller's duration change that capacity?",
                "answer": "Two reservations fit, consuming 10 MB and leaving 2 MB. The third cannot be promised immediate space. Duration estimates can help order waiting callers or predict a later start; they do not make three simultaneous 5 MB allocations fit. Even a perfect duration estimate only supports a later reservation if the interface also controls who may use the released space. Allocation semantics and planning information are separate obligations.",
            },
            "lessons": [("s6", "Compilation"), ("s8", "Observable behavior")],
        },
        {
            "title": "2. Justify both the changed answer and the changed cost",
            "body": "Two independent arguments are needed: why the transformation is allowed, and why it helps. Exact rewrites, approximate answers, and prediction-driven choices satisfy different obligations.",
            "subthemes": [
                ("Algebraic and structural rewrites", "Remove or reorder work under the program's actual numerical and ordering rules. Combining passes can increase temporary storage enough to erase the saving."),
                ("Approximation and early stopping", "State whether the answer is exact, error-bounded, or statistically justified. A usable compressed model is not necessarily a losslessly represented model."),
                ("Choices from observed behavior", "Count observation, decision, and reconfiguration costs. Include the consequence when the input differs from the history used for prediction."),
            ],
            "reading": "Read Voyager as an abstract-only lead on input-adaptive graph transformations; the full paper was not available in the local source review. MVQ is the inspected pruning-and-quantization example, not lossless compression or a general stopping rule. Past-Future is the inspected LLM memory-prediction example. DarwinGame tests configuration choices under shared cloud interference, a different kind of adaptation. Compare their specific decisions and failure cases rather than treating them as one universal adaptive method.",
            "worked_example": [
                "Use an invented equation, a×x = b, with a = 0.01 and b = 1. The exact answer is x = 100. Suppose an iterative solver stops at x = 99 because the remaining mismatch, |b−a×x|, is only 0.01. That mismatch is called the residual. The error in x is nevertheless one whole unit. For this scalar equation, answer error equals residual divided by |a|. A small residual alone does not specify the accuracy of the answer.",
                "If the application requires absolute answer error at most 0.1, this equation needs residual at most 0.001. For a different equation with a = 1, residual 0.01 already means answer error 0.01. Reusing one stopping threshold across the two equations changes the answer guarantee. These statements follow directly from subtraction of a×x and a×x_exact; they are not measurements from a conference paper.",
                "Now give the solver an invented cost. Eight iterations take 8 ms; stopping after four takes 4 ms. If four iterations do not meet the requested answer tolerance, that is not a faster solution to the same task. If inspecting progress costs 0.5 ms after each of four iterations, the early-stopping path takes 6 ms, not 4. A valid stopping rule and its execution cost need separate accounting.",
                "MVQ makes the same two-part obligation concrete for neural-network compression. It removes weights selected by a structured rule, then groups the remaining weights into a smaller set of shared values; this changes the model, so it is not lossless compression. Its method tries to protect the weights it treats as important, and the paper evaluates resulting model accuracy on specified vision tasks. Separately, it evaluates hardware energy efficiency and array size. A result on one axis cannot stand in for another: a smaller model is not automatically accurate enough, and maintained accuracy does not by itself show lower energy on a different processor. The real acceptance test is the application's accuracy requirement on its own data, followed by an end-to-end measurement of the target hardware path.",
            ],
            "practice": {
                "question": "For 0.02×x = 1, a computed answer has residual 0.004. What is its absolute answer error? Would it satisfy a tolerance of 0.1? What residual threshold would suffice in this exact-arithmetic teaching model?",
                "answer": "The answer error is 0.004/0.02 = 0.2, so it fails. Residual at most 0.02×0.1 = 0.002 would suffice. This conclusion uses a known nonzero scalar coefficient and exact arithmetic. A larger system of equations or a residual computed with rounding needs its own error argument; this scalar calculation does not establish a general solver guarantee.",
            },
            "lessons": [("s2", "Numerical error"), ("s6", "Legal rewrites"), ("queues-and-batching", "Changing demand")],
        },
        {
            "title": "3. Align where data lives with how it is used",
            "body": "Moving a value to faster storage pays only if its later use justifies the copy and occupied space. Evaluate layout and placement against the actual sequence of consumers, including misses and eviction, rather than calling one arrangement better by default.",
            "subthemes": [
                ("Memory hierarchy and locality", "Identify which values will be reused before eviction. Distinguish shared weights from request-specific state whose size grows with concurrency."),
                ("Layout and access pattern", "Put together values consumed together, while accounting for other consumers that prefer a different layout. Include conversion and duplicate copies."),
                ("Avoiding communication", "Separate removing bytes from overlapping their transfer. Keeping state, combining messages, and moving operations introduce different space and waiting costs."),
            ],
            "reading": "Keep four different ideas separate. In the TLB/cache paper, favoring code-address translations in the shared last-level translation cache reduces some code stalls but causes more data-address misses and page-table reads; a second-level cache policy tries to limit that added cost. CENT places arithmetic beside memory for model inference; its full paper reports that it is less effective during compute-heavy prompt processing and that linking more memory devices adds communication. PUSHtap arranges one database store for both row-by-row CPU transactions and column-oriented in-memory scans, while accounting for updates and snapshots. Concerto's abstract describes splitting large communication operations so some can overlap independent computation; the local record has no full text, so detailed implementation and performance claims remain unchecked.",
            "worked_example": [
                "Take an invented four-by-four array stored row by row. Storage transfers aligned blocks of four values, starting at addresses 0, 4, 8, and 12. A cold read of the first column needs addresses 0, 4, 8, and 12: four transfers fetch sixteen values to supply four requested values. Reading the first row needs addresses 0, 1, 2, and 3: one transfer supplies all four. The difference comes from which neighbors travel together.",
                "Transposing the stored array makes an original column contiguous, but original rows now cross four blocks. Suppose copying to that layout costs eight block transfers, reads retain nothing for the next operation, and the original array is unchanged. For six column reads and two row reads, the original layout costs 6×4 + 2×1 = 26 transfers. The converted layout costs 8 + 6×1 + 2×4 = 22. For four column reads and four row reads, the original costs 20 and conversion costs 28. The mixture of consumers changes the choice.",
                "The no-retention assumption controls this calculation. If all sixteen values remain in a sufficiently large cache after one traversal, subsequent reads can use those retained values. Counting four cold transfers for every column would then overstate the cost. Keeping both layouts also uses twice the array storage and requires a rule for updating both copies. Neither the transfer count nor the footprint can be assessed from one favored access alone.",
                "A real processor example makes the same point across two levels of memory. Instruction-aware TLB replacement (iTP) keeps more instruction address translations close to the processor, where a miss would stall instruction delivery. This choice can evict data translations, causing extra page walks. The paired xPTP cache policy tries to keep the resulting page-table data close in the L2 cache, and switches back to ordinary LRU when address-translation pressure is low. The paper reports geometric-mean performance improvements over LRU at both levels on its tested server workloads: 18.9% for 120 single-core workloads and 11.4% under two-thread co-location. The mechanism is cooperative because protecting one access path creates work for another; those results are not a claim that every kind of miss decreases or that the same gains transfer to another workload or processor.",
            ],
            "practice": {
                "question": "Keep eight total reads and the same no-retention assumptions. Let c be the number of column reads, with the remaining reads being rows. What is the smallest c for which paying eight transfers to convert the layout strictly reduces total transfers?",
                "answer": "The original needs 4c + (8−c) = 8 + 3c transfers. Conversion and subsequent reads need 8 + c + 4(8−c) = 40−3c. Conversion wins when 6c > 32, so six column reads are the first whole-number case. With five, the costs are 23 and 25; with six, 26 and 22. The threshold would change if the copy, cache behavior, or required output layout changed.",
            },
            "lessons": [("s3", "Memory"), ("s4", "Transfer paths"), ("dependencies-and-pipelines", "Overlap")],
        },
        {
            "title": "4. Map the whole supported computation to the device",
            "body": "A device that performs the central arithmetic still needs inputs, temporary state, control, and a path for unsupported operations. Judge the complete assignment of work, not the fastest unit's peak rate.",
            "subthemes": [
                ("Accelerator mapping", "Assign operations and communication to physical resources. Check which portion fits well and where the remainder runs."),
                ("Hardware and software promises", "State the access, visibility, and exceptional-condition rules both sides rely on. A proof of a protocol model does not prove every implementation."),
                ("Computing near stored data", "Move operations toward large inputs when supported there. Include residual transfers and functions that still execute elsewhere."),
            ],
            "reading": "Compare three different meanings of ‘put the work on the device.’ Plaid groups common three-operation dataflow patterns inside small units, then uses a wider network for links between groups; complex dependencies still need that wider path. Micro Blossom leaves parts of an exact matching decoder on the CPU and puts highly parallel graph work on an FPGA, so the split is about which steps can run together, not about replacing the CPU wholesale. CENT moves much of LLM arithmetic next to memory, but still assigns other operations and coordination to nearby processors and the host; its paper reports weaker performance on compute-heavy prompt processing and studies Llama 2 only up to 32K context. These are different workloads and cannot be ranked from their headline results. Separately, the CXL.cache formalisation proves a single-writer/multiple-reader safety property in its model and exposes specification defects; its two-device model is not proof of every device implementation, larger device groups, or progress under all conditions.",
            "worked_example": [
                "Imagine filtering 100 MB of records held beside a simple processing unit. The connection to the main processor moves 10 MB per millisecond. The ordinary path transfers all records in 10 ms, then filters them in 2 ms: 12 ms with no overlap. The nearby unit can apply the exact same predicate in 3 ms and return only matching records. If one tenth match, returning 10 MB takes 1 ms, making the path 4 ms. If every record matches, it takes 13 ms and loses to the ordinary path.",
                "For a matching fraction f, the nearby path takes 3 + 10f ms. Under these assumptions it beats 12 ms only when f < 0.9. Computing beside data helps by reducing the material that must cross the connection; the location alone is not a speed guarantee. This model assumes the data is already there and omits costs shared equally by both paths.",
                "Suppose the nearby unit instead supports only a preliminary test. Passing records must still undergo a 2 ms final test on the main processor, assumed fixed for this example. The cost becomes 5 + 10f ms, and the threshold becomes f < 0.7. More importantly, the preliminary test must never discard a true match. It may let extra candidates through, because the final test can reject them. A discarded true match cannot be recovered from the reduced data sent back.",
                "CENT makes ‘match the device to the work’ concrete across two phases of LLM inference. In the paper's evaluated comparison, GPUs have 2.5 times the throughput in compute-heavy prompt processing, while CENT has 2.5 times the throughput in memory-heavy token decoding. CENT connects its memory-side devices through CXL, a hardware connection and set of rules for exchanging data with attached memory devices. The paper reports that assigning more of those devices to a transformer block reduces the work time inside the devices but increases time spent exchanging data across CXL. So the right question is not ‘which chip is faster?’ but ‘which phase sets the end-to-end result, and how much extra movement does the mapping create?’ These are results for the paper's modeled hardware and workloads, not a universal ranking of GPUs and memory-side processing.",
            ],
            "practice": {
                "question": "The preliminary test passes 40 MB, including every true match. Its work takes 3 ms, transfer takes 4 ms, and final checking takes 2 ms. What is the total? Would dropping one true match be acceptable just because the total is below the ordinary path's 12 ms?",
                "answer": "The stages are sequential here, so the total is 9 ms. It is a valid improvement only if the final output satisfies the same filtering requirement. Dropping one true match violates exact filtering, even if the final checker rejects every incorrect candidate it receives. If approximate filtering is allowed, the missed-match allowance must be stated and checked as a different application promise.",
            },
            "lessons": [("s6", "Execution plans"), ("s4", "Connections"), ("s8", "Model boundaries")],
        },
        {
            "title": "5. Coordinate actual work rather than equal task counts",
            "body": "Tasks with equal counts can require different amounts of calculation, memory, and communication. The schedule must respect dependencies while using available resources, including the resources consumed by coordination itself.",
            "subthemes": [
                ("Scheduling unequal work", "Balance the costs that determine completion. Moving a task can save arithmetic time on one worker while adding a larger transfer."),
                ("Synchronization and agreement", "Identify exactly which observations must be ordered. A lock, a barrier, and a cache-coherence protocol provide different kinds of coordination."),
                ("Pipelining and overlap", "Choose partition sizes that permit early work without excessive per-piece handling. Include startup, draining, and buffers."),
            ],
            "reading": "These papers show that a schedule is about when work is ready, where its data is, and which shared resource it needs—not just which worker has the fewest tasks. FSMoE profiles expert computation and communication, then overlaps inter-node transfers, within-node communication, and computation; it also divides gradient communication to fit available gaps. That works only where dependencies and resources permit overlap, and its cluster results do not establish scaling to much larger systems. CoServe uses known expert requirements in its circuit-board inspection workload to group requests and reduce costly model swaps; that advantage depends on routes being known ahead of time and is not evidence for dynamically routed models. RANGE-BLOCKS addresses a different question: its abstract describes symbolic key-range locks for mutual exclusion in data-structure accelerators. The local record is abstract-only, so its implementation and evaluation details remain unchecked. A lock prevents conflicting access; a barrier waits for a group; a pipeline overlaps independent stages. They are not interchangeable.",
            "worked_example": [
                "In an invented job, four independent tasks take 6, 6, 2, and 2 ms on either of two workers. Each worker runs one task at a time. Giving the first worker the two long tasks and the second the two short tasks assigns equal task counts but finishes at 12 ms. Giving each one long and one short task finishes at 8 ms. A final 3 ms merge that needs all four outputs changes those totals to 15 and 11 ms. It cannot start when only the faster worker has finished.",
                "Placement can change this calculation. Suppose the inputs begin beside the badly balanced assignment, and exchanging a long and a short task requires a non-overlapped 5 ms transfer before either worker starts. The balanced version now takes 5 + 8 + 3 = 16 ms, worse than leaving the data in place. Counting only post-transfer computation would hide the reason it loses.",
                "Smaller pieces also introduce repeated handling. For a separate two-stage pipeline, two pieces each require 4 ms to produce and 4 ms to consume; independent stages and a buffer permit finishing at 12 ms instead of 16 ms. Split the same work into four pieces of 2 ms per stage, but add 1 ms of handling per piece at each stage. Each stage now takes 3 ms per piece, so completion is 3 + 4×3 = 15 ms. More overlap is available, but extra handling consumes most of the saving.",
                "FSMoE shows how this reasoning applies when a training layer uses several kinds of communication. The system measures routing, data exchange between machines, coordination within each machine, and expert computation, then schedules these as overlapping streams where dependencies permit. It also cuts a large gradient-reduction into pieces that can fit computation gaps. This is not ‘communication disappears’: overlap lowers elapsed time only if the transfers use resources the computation does not need and if their results are ready before the next dependent step. In the paper's tests, FSMoE reports 1.19×–3.01× speedups over DeepSpeed-MoE for GPT-2 and Mixtral models on clusters up to 48 GPUs. That bounds the evidence; it does not establish the same result on a much larger cluster or a different routing and hardware mix.",
            ],
            "practice": {
                "question": "Keep the pipeline's eight milliseconds of stage work per stage, but divide it into eight pieces. Each piece takes 1 ms of stage work plus 1 ms of handling at each stage. When does the last piece finish? Why is it slower than the two-piece case?",
                "answer": "Each stage takes 2 ms per piece. The first result finishes at 4 ms, and seven more finish at 2 ms intervals, giving 18 ms. Handling now adds 8 ms of work to each stage. Finer division reduces startup and permits earlier partial output, but increases the total work that the stages must perform. These formulas assume independent stage resources, identical piece times, sufficient buffering, and no additional transfers.",
            },
            "lessons": [("s7", "Unequal workers"), ("dependencies-and-pipelines", "Pipelines"), ("queues-and-batching", "Scheduling")],
        },
        {
            "title": "6. Count the resource consumed per acceptable result",
            "body": "Power is a rate; energy accumulates over time. Capacity tells how much work can be held, not how quickly it finishes. An efficiency ratio is meaningful only when it counts resources across the complete run and divides by outputs that meet the same correctness and deadline rule. Keep those boundaries fixed before comparing designs.",
            "subthemes": [
                ("Power, energy, and temperature", "Power is joules per second; energy is the accumulated use across the run. State which components are measured. Sustained temperature can also change the rate seen in a long run."),
                ("Capacity and contention", "Separate how much work fits from how fast the shared workers and links serve it. More admitted work can increase queues or contention without increasing completed work."),
                ("Cost per accepted result", "Count resources spent on the full run, including failed and retried work, then divide by outputs meeting a stated quality and deadline rule."),
            ],
            "reading": "Start by keeping rate and total separate. In the ASPLOS fine-grained-DVFS paper, the GPT-3 row at a 2% performance-loss target reports 250.04 W over an 11.29 s baseline iteration and 236.14 W over an 11.47 s DVFS iteration. Multiplying power by time gives about 2,823 J and 2,709 J, or roughly 4.1% lower implied SoC energy—not the 5.56% reduction in average SoC power. This is a course calculation from rounded table values, assuming each power value averages over its listed iteration; it is not a separate energy measurement reported in that table. Coach then shows why memory capacity and performance must be read together: it separates guaranteed from oversubscribed allocation and monitors contention, trading physical-memory savings against slowdown. Past-Future makes the output rule explicit through goodput: serving throughput that meets the stated service-level agreement, balancing queued requests against memory-driven evictions. CENT reports still other denominators, including tokens per joule and tokens per dollar; its decoding-heavy results differ from its compute-heavy prefill results. These studies use different systems and workloads, so their ratios are examples of what to measure, not a shared ranking.",
            "worked_example": [
                "Compare two invented ten-second service runs with 100 requests each. A draws an average 60 W over the measured boundary, consuming 600 J, and produces 90 correct results before their deadlines. B draws 50 W, consuming 500 J, but produces only 60 correct results on time. Energy per accepted result is about 6.67 J for A and 8.33 J for B. B uses less total energy while using more energy per accepted result. Report both facts and the failed requests, not just the favorable denominator.",
                "If the application requires at least 85 accepted results from those 100 requests, B is not an eligible design in this comparison. Giving B more time changes the task when deadlines are fixed. Retrying can add energy and queueing, and a late correct result still fails a deadline requirement. The acceptance rule must be fixed before comparing efficiency.",
                "Suppose memory holds 20 simultaneous requests, but one serial worker needs 10 ms per request. Admitting 20 at once makes them fit; it does not make them finish together. With no other work, their completion times are 10, 20, …, 200 ms. For a 50 ms deadline from simultaneous arrival, only the first five finish on time. More storage alone does not change that worker's service rate.",
                "CENT illustrates why ‘efficient’ needs a named denominator. The paper reports throughput (tokens per second), energy use for the compared runs, and total cost of ownership as tokens per dollar. In its stated comparison against GPU baselines, it reports 2.3× higher throughput, 2.9× less energy, and 5.2× more tokens per dollar. These are three different questions: TCO includes a hardware-cost model, while energy is about physical use over a run, and throughput is about rate. The results are for the paper's evaluated Llama 2 configurations; they are not interchangeable guarantees for another model, input/output mix, service deadline, or cost assumption. A fair decision checks the same accepted output and service boundary first, then reports time, energy, and money separately.",
            ],
            "practice": {
                "question": "A third design consumes 560 J in the same ten-second experiment and returns 84 accepted results. How does its energy per accepted result compare with A? Does it meet the requirement of at least 85?",
                "answer": "560/84 = 20/3 J, the same as A's 600/90 = 20/3 J. It nevertheless fails the 85-result requirement. A matching ratio does not imply capacity that meets the result requirement or eligibility to be counted. The experiment must also state which components contribute to measured energy and apply that boundary consistently to both designs.",
            },
            "lessons": [("physical-design", "Power and energy"), ("s3", "Capacity"), ("queues-and-batching", "Accepted work")],
        },
        {
            "title": "7. Keep the protection claim as narrow as its evidence",
            "body": "A design can be fast and still violate the required numerical, isolation, or recovery behavior. State the property, the cases it covers, and how the evidence connects to the implemented system.",
            "subthemes": [
                ("Correctness after a change", "Distinguish tested examples, model proofs, and statistical bounds. None should silently become a claim covering the others' domains."),
                ("Isolation and protection", "Name the attacker's access and the effects being prevented. Restricting direct reads does not remove all shared-resource observations."),
                ("Faults and recovery", "Specify what is committed, what may repeat, and what saved state can safely restart. Files existing is not sufficient evidence of a consistent checkpoint."),
            ],
            "reading": "Start with the exact claim each method checks. Formalising CXL Cache Coherence proves a single-writer/multiple-reader property in a model with two devices and one location; it does not prove every CXL configuration or that the protocol always makes progress. For a model-reconciliation check, AutoPRAC (a June 2026 preprint) reports a bounded-model counterexample to MOAT’s counter-reset policy under its simplified PRAC model and settings. That is a reason to reconcile the models and assumptions, not evidence of a demonstrated attack on commercial memory: AutoPRAC does not model RTL or silicon, and it omits some full MOAT optimizations. SMaCk studies an unprivileged attacker on a sibling SMT thread on tested x86 systems; its performance-counter detector is detection, not proof that timing leakage is impossible, and the authors discuss evasion. PMVerify asks which persistent-memory states can follow a crash under its chosen model and supported operations. It analyzed 26 PMDK examples, proved one robust, found violations in 12, and left 13 unknown; unknown is not a pass. Across all four, a proof or test covers its stated property, system model, and assumptions—not every behavior suggested by a broad label such as secure or correct.",
            "worked_example": [
                "Consider a checkpoint for two balances, initially A = 10 and B = 0. A completed transfer of three units changes them to A = 7 and B = 3. The application promises to save a complete state either before or after that transfer. Saving old A = 10 and new B = 3 produces a total of 13. Saving new A = 7 and old B = 0 produces a total of seven. Both individual files can be intact while the pair violates the application promise.",
                "One teaching solution pauses transfers, saves both balances under a new generation number, waits for both to be durable, then durably publishes that generation as the one to recover. Retain the previous generation until publication completes. A crash before publication leaves recovery on the old generation; a crash after publication exposes the complete new one. This reasoning assumes indivisible durable publication and storage surviving the stipulated crash. It says nothing about losing the entire storage device or about a real checkpoint implementation.",
                "PMVerify makes the difference between a verdict and a sample statistic visible. On 26 PMDK benchmark programs, it reports one robust case, 12 robustness violations, and 13 cases it could not settle. ‘Unknown’ is unresolved, not a softer form of ‘safe.’ Nor does 12 out of 26 estimate how often arbitrary real programs fail: these are selected examples, and results depend on the crash model, supported operations, and analysis limits. A proof of robustness is a guarantee for the checked program and model; it does not automatically cover different code or a different storage system.",
                "Protection needs similarly explicit observations. In a separate invented machine, a program cannot read another user's data, but its own probe always takes 1 ms when a shared resource is idle and 4 ms while the other user performs a particular operation. In this noiseless model, a 2 ms threshold reveals whether that operation overlaps the probe. Preventing direct reads has not prevented this observation. This is a constructed example of information through timing, not evidence of an attack on a named machine.",
            ],
            "practice": {
                "question": "A bounded model checker finds a counterexample within its model but does not run on a physical device. What has it shown, and what has it not shown? Then classify PMVerify’s 13 unknown examples: are they safe, unsafe, or unresolved?",
                "answer": "It has shown that the stated design model and assumptions permit a behavior that violates the checked property. It has not shown that a commercial device executes that behavior, nor that every implementation has the same flaw. The model and implementation must be reconciled. PMVerify’s 13 unknown cases are unresolved: neither a proof of safety nor a confirmed violation. In the balance example, A = 6 and B = 4 also preserves the total but is not one of the two allowed snapshots, so even a plausible summary check can miss an invalid state.",
            },
            "lessons": [("s8", "Correctness"), ("s9", "Security"), ("s7", "Recovery")],
        },
        {
            "title": "8. Recheck the complete path when conditions change",
            "body": "A service result has a path: arrival, admission, waiting, execution, and delivery. A change may improve one stage while making another slower. After a workload shifts, response time includes both the delay before the system reacts and the time needed to drain work that accumulated meanwhile.",
            "subthemes": [
                ("Input to delivered result", "Name arrival, admission, and acceptance. Count waiting, execution, and output only once, and include work on the path to a result that meets the service promise."),
                ("Workloads and comparisons", "Hold offered work, output quality, deadline, and resource boundary steady. A different request mix or transaction/query mix can change memory pressure and response time as well as throughput."),
                ("After deployment", "Name the signal, its age, the action it triggers, and the time that action takes. Report the interval before response and the time to clear any backlog, not just the new steady rate."),
            ],
            "reading": "Follow one request from arrival to an accepted answer. Past-Future estimates future KV-cache need from recent output lengths to decide whether another request can be admitted; its goodput measure counts requests meeting the paper’s response-time limits, and the estimate depends on recent output lengths remaining representative and on a warm-up history. PUSHtap asks a different whole-path question: can one memory layout serve row-oriented transactions and column-oriented analysis at once? Its reported gains are for its PIM-based HTAP design and tested benchmark, not a general promise for other query mixes. Coach uses long-term demand patterns to share otherwise idle cloud resources, while a monitor detects contention and can reassign resources or migrate a VM. Its reported capacity gain depends on those temporal patterns and the evaluated platform. These papers do not rank the same system: use each to ask what enters the path, what promise defines success, which observation drives a decision, and how long the decision takes to affect users.",
            "worked_example": [
                "Use a continuous-flow teaching model: requests arrive at a steady 100 per second and the current worker can finish 120 per second. After a workload change, its capacity falls to 80 per second. Monitoring notices after three seconds, and activating another worker takes two more seconds. During those five seconds, unfinished work grows at 100−80 = 20 requests per second, reaching 100 requests. The numbers describe an idealized average flow, not individual integer arrival times.",
                "Once the new worker is ready, total capacity is 140 per second. Only 40 of that capacity is available to reduce the backlog because new requests still arrive at 100 per second. Clearing the 100 waiting requests takes 100/40 = 2.5 additional seconds. The system returns to an empty queue 7.5 seconds after the change, not when the new worker becomes ready at five seconds.",
                "An adaptation report should include the period before recovery and the backlog-repair period. Faster monitoring may shorten the first but can consume resources or react to short-lived changes. If the new capacity were only 100 per second, the backlog would stop growing but would never shrink under these steady-arrival assumptions. Matching the ongoing arrival rate prevents further growth; it does not finish work that is already waiting.",
                "Past-Future applies a related idea to admission rather than worker activation. It uses recent request-output lengths to estimate future KV-cache use, then admits a request only when the estimated peak fits in memory. This guards against two opposite losses: reserve too much and requests wait unnecessarily; reserve too little and live requests may be evicted. The goal is goodput—requests that meet the paper’s response-time limits—not maximum raw admissions. The estimate can become misleading when the output-length mix changes abruptly or while the service is warming up, so a report should name that assumption. The paper reports up to 2–3× higher goodput than compared schedulers under heavy load; this is a result for its evaluated workloads and systems, not a universal multiplier or an independent reproduction.",
            ],
            "practice": {
                "question": "Keep the three-second detection delay and two-second activation delay, but suppose the workload change lasts only two seconds. The original worker then recovers to 120 requests per second, while arrivals remain at 100. When does its queue empty without the extra worker? At time three, the activation has not started; at time five it is ready. What should the controller check before starting or completing a delayed action?",
                "answer": "The queue grows by 20 requests per second for two seconds, reaching 40. After recovery, spare capacity is 120−100 = 20 per second, so it empties two seconds later, at time four. An extra worker ready at time five arrives after this backlog has cleared. A controller should compare the current arrival rate, service rate, queue, and expected time to act—not only the three-second-old observation—and reconsider an action that is still cancelable. If activation is already irreversible, include its cost rather than pretending the decision can be undone. Persistent changes can still justify scaling; this example shows why signal age, change duration, and actuation delay all matter.",
            },
            "lessons": [("s1", "Whole-request timing"), ("queues-and-batching", "Service promises"), ("s3", "Changing reuse")],
        },
    ],
    "exercise": "Use this teaching scenario: CPU execution takes 6 ms. An accelerator takes 2 ms but needs 5 ms to load cold data and 1 ms to return the result; assume no overlap or queueing. The cold accelerator request takes 8 ms and loses to the CPU. With already resident data it takes 3 ms and wins. Before choosing a deployment, identify the expected reuse, eviction behavior, arrival pattern, and required answer quality. Then find a paper discussion that measures these conditions rather than borrowing its kernel result as a whole-service prediction.",
    "sources": [
        ("analysis/asplos-2025-first-principles-theme-syntheses.md", "ASPLOS eight-theme essays"),
        ("analysis/asplos-2025-first-principles-subthemes.md", "ASPLOS 24-subtheme explanations and inspected-source boundaries"),
        ("https://johnwickerson.github.io/papers/cxl_cache_ASPLOS25.pdf", "Formalising CXL Cache Coherence: state-transition model, SWMR proof, and assumptions"),
        ("https://arxiv.org/abs/2412.10261", "MVQ: structured pruning and masked vector quantization with separate task-accuracy and hardware evaluations"),
        ("https://gvavou5.github.io/Documents/Vavouliotis_ASPLOS25.pdf", "Instruction-Aware Cooperative TLB and Cache Replacement: paired translation and page-table locality policies"),
        ("https://arxiv.org/abs/2502.07578", "CENT: phase-specific throughput and CXL communication tradeoffs in LLM inference"),
        ("https://arxiv.org/abs/2501.10714", "FSMoE: measured scheduling and communication-computation overlap for sparse expert training"),
        ("https://arxiv.org/abs/2502.07578", "CENT: separate throughput, energy, and tokens-per-dollar comparisons for LLM inference"),
        ("https://feihe.github.io/materials/asplos25.pdf", "PMVerify: crash-robustness verdicts and unresolved PMDK benchmark cases"),
        ("https://doi.org/10.1145/3676641.3716283", "EXIST: official ASPLOS proceedings record, tracing overhead, trace coverage, and end-to-end observability results"),
        ("https://cs.sjtu.edu.cn/~lichao/publications/EXIST_Enabling_ASPLOS-2025-Wang.pdf", "EXIST: author-hosted full paper for the focused walkthrough"),
        ("https://doi.org/10.1145/3676641.3716011", "Past-Future Scheduler: output-history-based KV-cache admission and SLA goodput evaluation"),
        ("https://doi.org/10.1145/3676641.3716251", "CIPHERMATCH: encrypted string packing, addition-only matching, and in-flash processing"),
        ("https://doi.org/10.1145/3669940.3707256", "vAttention: virtual/physical memory separation for dynamic KV-cache allocation"),
        ("https://arxiv.org/abs/2410.12168", "COMET: mixed-precision activation outliers, W4Ax kernels, and A100 serving results"),
        ("https://arxiv.org/abs/2502.14787", "Micro Blossom: exact matching split across CPU and FPGA for quantum-error decoding"),
        ("https://arxiv.org/abs/2409.13702", "PipeLLM: speculative pipelined encryption for confidential LLM transfers"),
        ("https://arxiv.org/abs/2401.11202", "PartIR: composable compiler-level SPMD partitioning and collective-cost reasoning"),
        ("https://arxiv.org/abs/2501.02600", "TAPAS: phase-aware thermal, power, placement, routing, and configuration control"),
        ("https://anakli.inf.ethz.ch/papers/PCcheck_asplos25.pdf", "PCcheck: concurrent persistent checkpointing, pipeline overlap, and goodput evidence"),
        ("https://doi.org/10.1145/3676641.3716250", "Cascade: dependency-aware temporal graph batching, memory freshness, and accuracy evidence"),
        ("https://doi.org/10.1145/3669940.3707287", "Mint: commonality/variability trace compression, full coverage, and end-to-end overhead"),
        ("https://arxiv.org/abs/2411.12263", "PowerMove: joint gate scheduling, qubit placement, movement, and zoned-architecture fidelity"),
        ("https://doi.org/10.1145/3676642.3736120", "PUSHtap: unified PIM layout, updates, snapshots, controller scheduling, and HTAP evaluation"),
        ("https://arxiv.org/abs/2508.02309", "PUSHtap primary full-text version: access directions, layout, concurrency, and evaluation boundary"),
        ("https://doi.org/10.1145/3676641.3715986", "CoServe: predictable expert dependencies, request grouping, eviction, profiling, and throughput boundary"),
        ("https://arxiv.org/abs/2503.02354", "CoServe primary full-text record: dependency-aware scheduling and limited-memory CoE serving"),
        ("https://doi.org/10.1145/3669940.3707231", "Fine-grained DVFS: operator-level frequency choice, slowdown budgets, and power/time boundaries"),
        ("https://cs.nju.edu.cn/_upload/tpl/01/65/357/template357/lunwen/2025/asplos25-zibo.pdf", "Fine-grained DVFS author-hosted full paper: Ascend evaluation and platform limits"),
        ("https://doi.org/10.1145/3676641.3715994", "BTrace: coordinated mobile trace buffers, event completeness, resizing, and evaluation boundary"),
        ("https://wangjwchn.github.io/papers/ASPLOS2025.pdf", "BTrace author-hosted full paper: buffer mechanism, resizing, smartphone traces, and reported results"),
        ("https://arxiv.org/pdf/2507.10150", "Authors’ full-text version used for the bounded Past-Future mechanism and evaluation walkthrough"),
        ("https://arxiv.org/pdf/2407.00326", "Teola: primitive-level workflow graphs, graph optimization, application-aware scheduling, and end-to-end evaluation"),
    ],
})
