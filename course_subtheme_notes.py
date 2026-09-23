"""Explicit subtheme teaching notes for the first audited conference routes.

These notes connect a compact subtheme definition to the worked reasoning already
shown in its theme. They do not turn a limited paper sample into conference-wide
evidence.
"""

VLSID = 'https://arxiv.org/html/2409.00495v1'
ISSCC = 'https://arxiv.org/pdf/2512.17555v1'
FCCM = 'https://arxiv.org/html/2503.24132v1'
ICCAD = 'https://www.cse.cuhk.edu.hk/~byu/papers/C287-ICCAD2025-RSizing.pdf'


def note(example, failure, evidence, source):
    return {'example': example, 'failure': failure, 'evidence': evidence,
            'source': source}


SUBTHEME_NOTES = {
    ('vlsid-2025', 1, 1): note(
        'Use the duration decoder in the worked example: convert a physical timing error into the corresponding value error before judging it.',
        'A small duration error can cross a decision threshold when the true value is close to that threshold.',
        'The pulse-bit-error review distinguishes control fields with different simulated consequences. Both linear duration rules are original teaching models.', 'analysis/vlsid-2025-full-evaluation-adjudication-001-003.md'),
    ('vlsid-2025', 1, 2): note(
        'Follow the value error into the final yes/no decision, as with 1.9 being decoded as 2.1 in the worked example.',
        'A bound on a local number does not preserve a task result when the downstream rule has a nearby boundary.',
        'The pulse-bit study evaluates simulated output changes, not physical fault occurrence rates. The 1.9-to-2.1 threshold example is original.', 'analysis/vlsid-2025-full-evaluation-adjudication-001-003.md'),
    ('vlsid-2025', 2, 1): note(
        'Trace one value through loading, storage, arithmetic, update, and output conversion; the recurring-cost example counts every stage.',
        'Removing one transfer does not remove conversion, update, or output work, so the claimed saving can disappear.',
        'The inspected TimeFloats preprint describes timing and alignment hardware; this course keeps the complete value path as an original teaching model.', VLSID),
    ('vlsid-2025', 2, 2): note(
        'Compare the one-time parameter load with the number of later uses in the energy break-even calculation.',
        'If parameters change every vector, the one-time cost becomes recurring and the apparent near-data advantage reverses.',
        'The paper’s modeled energy accounting is reported with an unresolved component-sum discrepancy; no full training result is claimed.', VLSID),
    ('vlsid-2025', 3, 1): note(
        'Use the A-versus-B timeline: include queue, preparation, execution, and acceptance rather than comparing execution alone.',
        'A target device can have shorter execution but lose after translation, routing, or acceptance work is included.',
        'QuaLITi evaluates target-specific translated circuits in noisy simulation. The A/B timeline is original.', 'analysis/vlsid-2025-full-evaluation-adjudication-001-003.md'),
    ('vlsid-2025', 3, 2): note(
        'Compare arrival-to-accepted-result time and the uncertainty interval, not just the time until a device starts.',
        'A quicker start or lower central estimate does not guarantee an earlier acceptable answer when intervals overlap.',
        'QuaLITi measures real-device queue behavior separately and estimates full inference waits. The 20-second prediction and 50-second trace are original.', 'analysis/vlsid-2025-full-evaluation-adjudication-001-003.md'),
    ('vlsid-2025', 4, 1): note(
        'For each term in the additive error example, write down the process and operating condition that justifies its bound.',
        'If the final computation is nonlinear or a component bound does not hold jointly, adding the bounds is not a valid certificate.',
        'TimeFloats uses synthesis and circuit/process models. Its unresolved energy accounting is separate from the original additive-error example.', 'analysis/vlsid-2025-full-evaluation-adjudication-001-003.md'),
    ('vlsid-2025', 4, 2): note(
        'Separate a simulated timing or error value from a value observed on a fabricated device when reading the evidence.',
        'Measuring one stage cannot silently convert modeled neighboring stages into measurements.',
        'QuaLITi combines simulated accuracy and separate measured queue observations; full inference waits are estimates. The table retains this split.', 'analysis/vlsid-2025-full-evaluation-adjudication-001-003.md'),

    ('isscc-2025', 1, 1): note(
        'Compare transfer and calculation time separately for each phase in the 27-ms teaching job.',
        'Halving arithmetic does not halve the job when unchanged transfers still take time.',
        'The ConvFormer digest is inspected for the hybrid attention, layer fusion, and pruning mechanisms; its chip measurements remain author-reported.', ISSCC),
    ('isscc-2025', 1, 2): note(
        'Check data readiness before overlapping stages, then test the final answer when attention or retained contributions change.',
        'A shorter ideal schedule is unavailable if the calculation needs unfinished inputs; changed arithmetic also needs a quality check.',
        'The ConvFormer digest combines attention, reuse, and trained pruning. The timing schedules are original, not its measured results.', ISSCC),
    ('isscc-2025', 2, 1): note(
        'Track which phase still consumes each intermediate and keep it until its last legal consumer.',
        'Releasing or overwriting a value before a dependent tile is ready produces a plausible-looking but wrong result.',
        'The paper’s layer-fusion and buffer discussion motivates the schedule; the exact buffer numbers in the course are invented.', ISSCC),
    ('isscc-2025', 2, 2): note(
        'Distinguish storing an intermediate for less time from removing its contribution to the calculation.',
        'Replacing an unavailable neighbor with zero changes 15 to 9 in the teaching example; calling the schedule fused does not make that exact.',
        'The digest uses a trained pruning mask as well as data reuse. The three-value sum is original and is not a measured quality result.', ISSCC),
    ('isscc-2025', 3, 1): note(
        'Record the voltage and clock frequency for the reported peak, then distinguish it from achieved efficiency over a complete workload.',
        'A supported operating range does not place the best reported efficiency at every point in that range.',
        'The ConvFormer digest locates its peak at 0.65 V and 200 MHz. The device/host joule example is original.', ISSCC),
    ('isscc-2025', 3, 2): note(
        'Compare equivalent dense work and actually executed work only after stating which operation count the efficiency uses.',
        'An operations-per-joule ratio can change when the numerator counts skipped work, even with identical physical energy.',
        'The digest’s comparison assumptions are preserved in the walkthrough; no competing chip measurement was reproduced.', ISSCC),
    ('isscc-2025', 4, 1): note(
        'List each tested duration/activity pair and compare that list with the combinations required by the proposed use.',
        'Passing short/high and long/low does not test long/high; the missing combination is neither a demonstrated success nor failure.',
        'The digest names specific model and dataset tests. The two-duration/two-activity grid and three-chip example are invented.', ISSCC),
    ('isscc-2025', 4, 2): note(
        'Read the claimed chip result together with process, voltage, frequency, model, dataset, and comparison baseline.',
        'A fabricated chip result does not establish behavior at another operating point, workload, software stack, or quality target.',
        'The three-page digest is the inspected primary source and its prior-design peak-efficiency assumption is stated in the walkthrough.', ISSCC),

    ('fccm-2025', 1, 1): note(
        'Map each address to its bank and count the busiest bank, then add result-return capacity to the timing model.',
        'Four banks do not provide four reads per cycle when all requests land on one bank or when the return path is narrower.',
        'The Banked Memories manuscript sections III–VI are inspected for the controller and arbitration mechanism; the return-path extension is a teaching model.', FCCM),
    ('fccm-2025', 1, 2): note(
        'Count requests separately for each bank: addresses 0,4,8,12 need four read-start cycles, while 0,4,1,5 need two.',
        'Dividing four reads by four banks gives one cycle, but cannot reveal that all four reads need the same bank. Delivery time must be counted separately.',
        'The manuscript is evidence for its own soft-SIMT memory organization, not for every configurable-memory design.', FCCM),
    ('fccm-2025', 2, 1): note(
        'Recompute bank numbers after changing row stride: five-word rows spread column-zero accesses across the four banks.',
        'Six-word rows in the same toy layout map column-zero accesses to only two banks, so more padding is not automatically better.',
        'The manuscript compares organizations for selected workloads; the padding arithmetic is original and isolates layout effects.', FCCM),
    ('fccm-2025', 2, 2): note(
        'Charge conversion setup and the useful lifetime of the converted layout in the repeated-read break-even example.',
        'If the array changes before the prepared copy is reused, rebuilding can cost more than the access saving.',
        'The source discusses workload organizations and footprint; the course does not claim its toy setup cost was measured.', FCCM),
    ('fccm-2025', 3, 1): note(
        'Convert cycles into seconds using the achieved clock rate before ranking two designs.',
        'Fewer cycles can take longer when the design runs at a lower rate, as the 8-cycle/200-MHz versus 6-cycle/100-MHz example shows.',
        'The manuscript’s reported implementation boundary remains separate from the original timing example.', FCCM),
    ('fccm-2025', 3, 2): note(
        'Identify whether a number came from a simulator, implementation tool, or running board, then keep that label attached to it.',
        'A simulated clock assumption is not evidence that routed hardware reaches the same rate.',
        'The paper’s sections IV–VI and the unresolved 51-versus-52 benchmark count are recorded as source limits.', FCCM),

    ('iccad-2025', 1, 1): note(
        'Put every candidate through the hard delay limit before minimizing area; the A/B/C example makes the ordering explicit.',
        'A weighted penalty can prefer an invalid design because a preference score is not the same as a hard constraint.',
        'The RSizing paper formulates multi-objective analog sizing with yield requirements; the candidate coordinates are original.', ICCAD),
    ('iccad-2025', 1, 2): note(
        'Keep the acceptable set first, then compare tradeoffs such as area and delay only within that set.',
        'One passing design may be smaller while another is faster. Choosing between them requires a stated preference, not just their measurements.',
        'RSizing’s Pareto and yield framing is inspected in section II; this note does not summarize all ICCAD 2025 optimization work.', ICCAD),
    ('iccad-2025', 2, 1): note(
        'Compare predicted delay with the later check near the 10-ns boundary, not only with average absolute error.',
        'A small average error can still select an invalid fastest candidate or reject a valid one.',
        'RSizing uses surrogate models and later Monte Carlo refinement; the three-candidate delays are original.', ICCAD),
    ('iccad-2025', 2, 2): note(
        'Use a certified worst-case error to form a safe screening threshold, and treat an observed mean as descriptive rather than certifying.',
        'An uncertainty bound established for one layout class or operating condition may not cover another.',
        'The paper’s HGP model and refinement limitations are inspected in section III; no claim is made that its surrogate is a universal bound.', ICCAD),
    ('iccad-2025', 3, 1): note(
        'Test the generated counter at the wrap boundary using an independent modulo-256 reference.',
        'A test generator that copies the implementation’s saturation rule can accept the same mistake indefinitely.',
        'The counter is an original teaching model; RSizing is the inspected paper for this route, not a code-generation paper.', ICCAD),
    ('iccad-2025', 3, 2): note(
        'Check functional behavior, timing, and physical feasibility as separate obligations for the generated artifact.',
        'Passing a functional test does not establish timing, and meeting timing does not repair a wrong boundary behavior.',
        'The route’s evidence boundary distinguishes discovery abstracts from the inspected RSizing full paper; this example is intentionally original.', ICCAD),
    ('iccad-2025', 4, 1): note(
        'Add candidate-generation, evaluation, failed attempts, parallel capacity, and final validation to the search budget.',
        'Fewer iterations can still cost more time, and a faster search is not better if it returns a lower-quality or invalid design.',
        'RSizing reports simulation settings and benchmark runtimes in section IV; the serial and four-worker totals are original.', ICCAD),
    ('iccad-2025', 4, 2): note(
        'Record the circuit, simulator, process model, settings, and random-sampling conditions before comparing a rerun.',
        'A successful rerun under one model does not establish generalization to unseen designs, process conditions, or physical silicon.',
        'The author-hosted RSizing paper is the primary source for this route’s focused evidence; the broader ICCAD corpus remains unaudited.', ICCAD),
}

GSIM = 'https://arxiv.org/html/2508.02236v1'
CORRECTBENCH = 'https://arxiv.org/html/2411.08510v1'

SUBTHEME_NOTES.update({
    ('dac-2025', 1, 1): note(
        'In the GSIM-style toy count, retain only activity and graph dependencies that the estimator actually needs, then compare the work saved with the checks added.',
        'Dropping a dependency can make the simulator faster by making its answer wrong.',
        'The GSIM paper is inspected for graph extraction, activity checks, and generated simulation; the 100-operation count is original.', GSIM),
    ('dac-2025', 1, 2): note(
        'Compare the chain and paired-adder descriptions: both count three additions, but their longest dependency paths differ.',
        'An operation count can preserve the arithmetic while hiding the information needed to predict delay.',
        'The NetTAG review describes circuit connections, gate behavior, and physical attributes used for prediction. The adder example is original.', 'analysis/dac-2025-full-evaluation-adjudication-009-016.md'),
    ('dac-2025', 2, 1): note(
        'Count the saving from retaining one input and the extra delay caused by displacing another user’s data.',
        'The first user’s 1 ms saving does not outweigh the second user’s added 6 ms under the stated combined-time objective.',
        'CaMDN studies competing models and reusable cache contents in simulation. The two-user timings are original.', 'analysis/dac-2025-full-evaluation-adjudication-001-008.md'),
    ('dac-2025', 2, 2): note(
        'Check when every required part finishes and how the results are combined, not just the fastest module’s calculation time.',
        'Moving more work to a lower-energy module can violate the required completion time if another module must wait for it.',
        'HH-PIM models placement across different memory-compute modules under a time limit. Its energy results are not fabricated-chip measurements.', 'analysis/dac-2025-full-evaluation-adjudication-017-024.md'),
    ('dac-2025', 3, 1): note(
        'Mark the permitted stopping points and both switching intervals on the urgent-job timeline.',
        'A priority label cannot interrupt work at a point the implementation does not support. Recent timing observations also do not bound every future run.',
        'DARIS uses stage boundaries and recent execution-time estimates. The 12 ms job and 0.5 ms switches are original teaching assumptions.', 'analysis/dac-2025-full-evaluation-adjudication-001-008.md'),
    ('dac-2025', 3, 2): note(
        'Subtract required remaining calculation from the time left before the deadline; charge switching to the remainder before inserting work.',
        'A job that appears to fit can miss the existing request’s deadline once switching is counted.',
        'Tropical checks both answer-start and continuing-answer requirements. The 10 ms deadline example is original.', 'analysis/dac-2025-full-evaluation-adjudication-017-024.md'),
    ('dac-2025', 4, 1): note(
        'Compare the repeated doubling and halving examples, then calculate the joint effect of changing both inputs to a product.',
        'Adding single-step error limits can miss amplification; adding separate change effects can miss their interaction.',
        'CLADO estimates cross-layer interactions. The 0.31 accumulated error and 0.21 product error are original examples.', 'analysis/dac-2025-full-evaluation-adjudication-009-016.md'),
    ('dac-2025', 4, 2): note(
        'Check generated-output quality separately from simulated execution speed, and name the tested model and input conditions.',
        'Passing a sample-based quality test does not establish an error limit for every future input.',
        'The SQ-DM review separates simulated accelerator results from quality evidence. The error-bound examples are original.', 'analysis/dac-2025-full-evaluation-adjudication-009-016.md'),
    ('dac-2025', 5, 1): note(
        'Separate the time and power used to move inputs from the time and power used to calculate.',
        'Changing calculation speed leaves the stated input-transfer time unchanged; using only calculation energy omits the rest of the job.',
        'The EdgeMM review describes phase-specific processing and transfer allocation. The 18 J and 16 J stage totals are original.', 'analysis/dac-2025-full-evaluation-adjudication-001-008.md'),
    ('dac-2025', 5, 2): note(
        'Compare energy to completion and energy over a fixed window separately, while keeping the deadline visible.',
        'Lower power can still cost more energy if the job takes longer; idle behavior can change the fixed-window ranking again.',
        'HH-PIM models energy-aware placement under a completion limit. The 8-second window and idle-power values are original.', 'analysis/dac-2025-full-evaluation-adjudication-017-024.md'),
    ('dac-2025', 6, 1): note(
        'State whether the observer gets returned values only, or also timing and physical power measurements.',
        'Identical reply text does not hide the private bit in the timing example. Physical measurement results require the stated measurement access.',
        'DeepPUFSCA combines challenges and power traces for a tested FPGA circuit. The 1 ms and 3 ms responses are original.', 'analysis/dac-2025-full-evaluation-adjudication-009-016.md'),
    ('dac-2025', 6, 2): note(
        'List the substitute data and intermediate values visible outside the protected part of a computation.',
        'Keeping the original private does not establish that a transformed copy reveals nothing about it.',
        'GNNVault splits prediction between public and protected parts. The three-copy deletion example is original, not a GNNVault deletion claim.', 'analysis/dac-2025-full-evaluation-adjudication-009-016.md'),
    ('dac-2025', 7, 1): note(
        'Add candidate-generation, cheap estimation, high-fidelity checking, and failed attempts to the search budget.',
        'A cheaper estimator can increase total time if it causes too many wrong candidates to reach expensive checking.',
        'LMM-IR motivates reducing repeated physical-analysis cost. The 14-second search and 13-second budget are original, not measured tool runtimes.', 'analysis/dac-2025-full-evaluation-adjudication-017-024.md'),
    ('dac-2025', 7, 2): note(
        'Compare equal prediction errors far from and near the mandatory limit, then check which one wrongly accepts a failing design.',
        'An average error is not a maximum-error bound and does not justify a guaranteed safety margin.',
        'LMM-IR evaluates numerical error and high-drop-region detection on its benchmark. The 0.2 ns errors are original teaching values.', 'analysis/dac-2025-full-evaluation-adjudication-017-024.md'),
    ('dac-2025', 8, 1): note(
        'Check the intended logical operation against simulated voltage behavior and timing under the stated operating conditions.',
        'A correct truth table does not establish that a proposed circuit produces those values reliably or on time.',
        'WISEDRAM uses HSPICE and a specified technology model. The 1.8 ns clock and changed wire delays are original.', 'analysis/dac-2025-full-evaluation-adjudication-025-032.md'),
    ('dac-2025', 8, 2): note(
        'Label measured input data, classification accuracy, implementation resources, and processing delay separately.',
        'Measured input signals do not make every downstream timing or whole-system quantity a hardware measurement.',
        'KLiNQ combines measured qubit data with FPGA implementation evidence. The course does not claim an independently reproduced full readout system.', 'analysis/dac-2025-full-evaluation-adjudication-017-024.md'),

    ('date-2025', 1, 1): note(
        'Use the execution example to count what can run independently and what must wait for a shared value.',
        'A regular or smaller description can still preserve a dependency that prevents the expected speedup.',
        'The SAT-sampling review connects logical rewriting to GPU operations. The old/new-y schedule is original, not a paper benchmark.', 'analysis/date-2025-full-evaluation-adjudication-001-008.md'),
    ('date-2025', 1, 2): note(
        'Enumerate the allowed x/f pairs, then compare the two constraints with the explicit f = not x operation.',
        'An existence-preserving transformation alone does not certify the validity or variety of every returned sample.',
        'The SAT paper describes an equisatisfiable transformation and valid, distinct solutions. The two-variable explanation illustrates its inverter relation.', 'analysis/date-2025-full-evaluation-adjudication-001-008.md'),
    ('date-2025', 2, 1): note(
        'Compare choosing among buildable candidates with repairing the highest-scoring ideal candidate after selection.',
        'Repairing an unbuildable feature can change performance enough to reverse the original ranking.',
        'BOSON-1 includes fabrication restrictions during search. The 30/50/60 nm example is invented, not a process specification.', 'analysis/date-2025-full-evaluation-adjudication-001-008.md'),
    ('date-2025', 2, 2): note(
        'List the allowed timing intervals and any separately justified relation between logic and wire delays.',
        'A midpoint or a set of favorable samples does not exclude the failing combination allowed by the model.',
        'BOSON-1 evaluates sampled process variations. The 2.1 ns worst case and 1.9 ns joint bound are original teaching values.', 'analysis/date-2025-full-evaluation-adjudication-001-008.md'),
    ('date-2025', 3, 1): note(
        'Compare continuous service with reserved slots, including the changed assumption that transfers can be split into blocks.',
        'Borrowing unused slots can reintroduce dependence on another user’s activity even when it improves completion time.',
        'MC3 measures effects of shared memory contention. The seven-versus-four-millisecond reservation example is original.', 'analysis/date-2025-full-evaluation-adjudication-001-008.md'),
    ('date-2025', 3, 2): note(
        'Identify who deliberately sends a signal and who observes it before describing the security result.',
        'A demonstrated cooperative channel does not by itself establish extraction of an unwilling victim’s secrets or corruption of stored data.',
        'MC3 evaluates covert communication on three Orin platforms. The exact timing inference and fixed-slot comparison are original.', 'analysis/date-2025-full-evaluation-adjudication-001-008.md'),
    ('date-2025', 4, 1): note(
        'Compare ordered output sequences, not sorted values, when the requirement is to preserve queue order.',
        'Sorting can hide reordered outputs; using sets can additionally hide a lost duplicate.',
        'CorrectBench evaluates generated testbench reports against a reference. The 7,2,7 queue trace is original.', CORRECTBENCH),
    ('date-2025', 4, 2): note(
        'After a repair, test cases beyond the triggering example and inspect the benchmark’s exact acceptance rule.',
        'Passing an eight-of-ten agreement threshold permits disagreements; bounded repair can stop without producing a correct checker.',
        'CorrectBench separates functional repair from mutant-based Eval2 evaluation. The all-ten-reference-rejections scenario is original.', CORRECTBENCH),
    ('date-2025', 5, 1): note(
        'Compare coarse and fine error-control units, including metadata and the decisions made at each unit.',
        'Finer control can cost more metadata or coordination than the numerical error it removes.',
        'Cocktail selects precision per context chunk and retains higher-precision exceptions. The three-byte payload plus one-byte tag is original.', 'analysis/date-2025-full-evaluation-adjudication-009-015.md'),
    ('date-2025', 5, 2): note(
        'Specify the fallback’s time, memory, and output-quality obligations before treating it as a safety net.',
        'A fallback that misses the deadline or changes the accepted answer is not equivalent to the primary path.',
        'Cocktail quality tests are model/workload evidence, not the linear example’s worst-case bound. The 3 ms plus 4 ms fallback is original and not attributed to Cocktail.', 'analysis/date-2025-full-evaluation-adjudication-009-015.md'),
    ('date-2025', 6, 1): note(
        'Draw the boundary between independently optimized blocks and the coupling that returns when they share timing, power, or data.',
        'Two locally best choices can be incompatible when combined.',
        'The CGRA paper separates time then placement under a neighbor-register-access assumption. The equal-area split is an original counterexample to arbitrary decomposition.', 'analysis/date-2025-full-evaluation-adjudication-009-015.md'),
    ('date-2025', 6, 2): note(
        'Compare the time to find a design separately from its execution time, and retain cases where the search times out.',
        'A fast average over completed comparisons does not describe success on every benchmark or equal improvement in application speed.',
        'The CGRA paper uses a 4,000-second timeout and excludes cases with either tool timing out from its average compilation-time comparison.', 'analysis/date-2025-full-evaluation-adjudication-009-015.md'),
    ('date-2025', 7, 1): note(
        'Compare a check for changed stored bits with a check that the generated circuit implements the intended behavior.',
        'Unchanged maliciously generated bits can pass an integrity check; detecting corruption is not the same as checking the original design.',
        'RTL-Breaker evaluates poisoned generation under selected triggers and tasks. The parity counterexample is original.', 'analysis/date-2025-full-evaluation-adjudication-001-008.md'),
    ('date-2025', 7, 2): note(
        'Identify the protected reference used at a function return and place validation before the action it guards.',
        'Checking an allowed control-flow target does not certify every numerical output or exclude every allowed-but-unwanted target.',
        'EILID checks return state and selected call targets under its stated threat model. The publish-at-4/check-at-5 timeline is original.', 'analysis/date-2025-full-evaluation-adjudication-001-008.md'),
    ('date-2025', 8, 1): note(
        'Write the exact acceptance rule before comparing pass rates, and record any change to inputs, settings, or hardware.',
        'Agreement on selected tests is not the same requirement as detecting every fault; partial delivery is not completion of a mandatory batch.',
        'CorrectBench supplies a concrete reference-agreement rule. The ten-answer deadline example is original.', CORRECTBENCH),
    ('date-2025', 8, 2): note(
        'Count preparation, successful execution, checks, failures, and recovery through completion of the required batch.',
        'Dropping unfinished searches or failed outputs changes the population described by an average.',
        'The CGRA review records timeout exclusions and compilation-time scope. The batch fallback totals are original, not a combined DATE system.', 'analysis/date-2025-full-evaluation-adjudication-009-015.md'),

    ('isca-2025', 1, 1): note(
        'Use the LUT walkthrough to write down what the compressed or encoded representation makes directly available to the next operation.',
        'A representation that hides a needed pattern forces decoding or a fallback before the operation can run.',
        'The LUT-Tensor-Core preprint is inspected for table-based multiplication and its modeled accelerator boundary; the byte counts are original.', 'https://arxiv.org/html/2408.06003v3'),
    ('isca-2025', 1, 2): note(
        'Add table lookup, setup, conversion, and unsupported-case costs to the direct arithmetic cost in the break-even example.',
        'Fewer stored bytes lose if decoding and table access cost more than the arithmetic they replace.',
        'The source reports a modeled TSMC-28-nm design and simulator comparisons, not measured silicon or every consumer workload.', 'https://arxiv.org/html/2408.06003v3'),
    ('isca-2025', 2, 1): note(
        'Mark the operands and intermediate values that stop crossing the original memory boundary when the operation moves nearer to data.',
        'Later consumers can still require a transfer, so removing one movement path does not mean all movement disappeared.',
        'NMP-PaK’s publication abstract describes near-memory processing combined with software changes. The transfer arithmetic is original.', 'https://arxiv.org/abs/2505.08071'),
    ('isca-2025', 2, 2): note(
        'List local storage, programming setup, peripheral work, and numerical effects beside the shorter physical path.',
        'A nearer operation can lose when its local table, setup, or conversion work exceeds the avoided transfer.',
        'The local NMP-PaK review identifies scratchpad and processing-element constraints and a simulated evaluation. These limits do not establish performance for every near-memory device.', 'analysis/isca-2025-full-evaluation-adjudication-006-010.md'),
    ('isca-2025', 3, 1): note(
        'Draw when X and Y load and calculate. Mark the transfer connection and calculation unit used by each step.',
        'Calculations that do not need each other’s results can still have to wait for the same hardware.',
        'The RSN abstract describes exposing calculation and transfer times to software. The 14 ms and 11 ms schedules are original teaching examples.', 'https://research.google/pubs/reconfigurable-stream-network-architecture/'),
    ('isca-2025', 3, 2): note(
        'Keep X’s 6 MB in storage until its calculation finishes. Check whether another 6 MB is available for Y.',
        'Starting Y’s load too soon can overwrite X. Starting Y’s calculation at its predicted arrival time can read incomplete data.',
        'Storage amounts and the late-arrival exercise are original, not a claimed RSN buffer size or prediction rule. The linked review records the paper’s evaluation conditions.', 'analysis/isca-2025-full-evaluation-adjudication-001-005.md'),
    ('isca-2025', 4, 1): note(
        'Trace which inputs are ready at the same time and which shared link or port limits their arrival.',
        'Adding unrelated link bandwidth does not help when one narrow connection carries every required input.',
        'The transfer arithmetic is original. DeepSeek’s section 5.1 provides the network comparison, not these invented connection rates.', 'https://arxiv.org/html/2505.09343v2#S5.SS1'),
    ('isca-2025', 4, 2): note(
        'Draw both paths through the invented collector network. Mark any switch they share and check how the receiver orders incoming data.',
        'Two paths through one switch both stop if that switch fails. A shorter path can also let later data overtake earlier data.',
        'The local DeepSeek evaluation review distinguishes deployed hardware from proposed interface features and unresolved failure risks. The shared-switch example is original.', 'analysis/isca-2025-full-evaluation-adjudication-011-017.md'),
    ('isca-2025', 5, 1): note(
        'Charge the mapping and setup work before applying the specialized path to the input shape it accepts.',
        'A fast kernel can lose on a small or one-off workload when preparation is not amortized.',
        'The LUT paper is inspected for table construction and accelerator modeling; the preparation totals are original.', 'https://arxiv.org/html/2408.06003v3'),
    ('isca-2025', 5, 2): note(
        'In the invented 12 ms program, separate the accelerated comparison from the 4 ms that still runs elsewhere and the transfers between devices.',
        'Reducing comparison from 8 ms to 2 ms loses overall if transfers add 7 ms: complete execution takes 13 ms.',
        'The HPVM-HDC evaluation review records unsupported accelerator applications and a slower generated GPU case. The 12 ms program is an original teaching example.', 'analysis/isca-2025-full-evaluation-adjudication-001-005.md'),
    ('isca-2025', 6, 1): note(
        'Check whether a reordered access still refers to the same location and whether another observer can see the changed order.',
        'Matching final values does not excuse an illegal intermediate ordering or an externally visible side effect.',
        'DX100’s compiler discussion requires nonconflicting memory accesses and independent loop repetitions. The p/q example is original.', 'https://doi.org/10.1145/3695053.3731015'),
    ('isca-2025', 6, 2): note(
        'Subtract the largest allowed error from the winning score and add it to the losing score. Check whether the winner still leads.',
        'Small changes can reverse close scores. A tested accuracy score does not establish an error limit for every input.',
        'The local HyFlexPIM review records simulated noise and model-dependent protection rates. The score-gap guarantee is original and assumes a known absolute error limit.', 'analysis/isca-2025-full-evaluation-adjudication-011-017.md'),
    ('isca-2025', 7, 1): note(
        'List modeled timing, process, memory, and workload assumptions beside the accelerator estimate.',
        'A detailed simulator output can still be wrong if its model omits a supporting bottleneck.',
        'The LUT paper uses synthesis and accelerator simulation rather than fabricated-chip measurement; this boundary is explicit.', 'https://arxiv.org/html/2408.06003v3'),
    ('isca-2025', 7, 2): note(
        'Name the actual device, workload, input distribution, and measured boundary before using an observed result as evidence.',
        'Measuring one control path or kernel does not establish measurement of the complete proposed system.',
        'The RSN evaluation review records measured execution, estimated power, and externally reported comparison times. These are different evidence types within one paper.', 'analysis/isca-2025-full-evaluation-adjudication-001-005.md'),
    ('isca-2025', 8, 1): note(
        'Hold shape, length, reuse, access pattern, and numerical requirement fixed while changing the mechanism.',
        'A gain that depends on one favorable shape is unknown for a different shape, even if the paper title sounds general.',
        'The Oaken evaluation review records per-model profiling. The two workload timing breakdowns are original, not Oaken measurements.', 'analysis/isca-2025-full-evaluation-adjudication-001-005.md'),
    ('isca-2025', 8, 2): note(
        'Trace software planning, storage, transfers, and recovery around the accelerator before combining independent speedups.',
        'Two separately measured kernel gains cannot be multiplied when they use different implementations or bottlenecks.',
        'The NMP-PaK review distinguishes a software-only comparison from the complete proposal. The four-way calculation/conversion comparison is original.', 'analysis/isca-2025-full-evaluation-adjudication-006-010.md'),

    ('hpca-2025', 1, 1): note(
        'In the invented storage-mode timeline, mark the six milliseconds during which an ordinary access cannot proceed.',
        'A local mode change can erase the gain if it serializes the next required operation.',
        'MVE supplies the in-cache computing connection. The mode timeline and ordinary-access delay are original, not measured MVE timings.', 'https://ieeexplore.ieee.org/document/10946805/'),
    ('hpca-2025', 1, 2): note(
        'Trace every temporary and address used by the local operation, including values that spill outside its intended storage.',
        'Repeated spills recreate the movement the optimization was meant to remove.',
        'The local MVE review records cache and execution assumptions. The 10 MB requirement, 8 MB capacity, and specified spill traffic are original teaching numbers.', 'analysis/hpca-2025-full-evaluation-adjudication.md'),
    ('hpca-2025', 2, 1): note(
        'For a compact code, count the table read or reconstruction step before the arithmetic begins.',
        'A smaller value representation can lose if its lookup path dominates the saved traffic.',
        'VQ-LLM’s abstract describes placing codebook entries across GPU storage and combining lookup with calculation. The byte counts are original.', 'https://arxiv.org/abs/2503.02236'),
    ('hpca-2025', 2, 2): note(
        'In the four-worker example, compare leaving all four remaining operations on one worker with paying to redistribute them.',
        'Fewer contributions can leave uneven work that makes one unit wait while others finish.',
        'EXION’s abstract describes packing remaining work and reusing selected results. The worker assignments and preparation times are original.', 'https://arxiv.org/abs/2501.05680'),
    ('hpca-2025', 3, 1): note(
        'Draw the separate row additions and the final combination that needs the previous row’s sum.',
        'Repeating a pattern does not make a value independent of the previous iteration.',
        'LEGO’s architecture study supplies context for parallel execution; the dependency trace is original.', 'https://arxiv.org/html/2509.12053v1'),
    ('hpca-2025', 3, 2): note(
        'Count address generation, fetching, and result collection on the timeline beside arithmetic.',
        'A serial fetch or collection stage can cap throughput even when arithmetic units are idle only briefly.',
        'The LEGO evaluation review records a memory-limited GPT-2 case and excluded CPU communication. The cycle-by-cycle supply/store schedule is original.', 'analysis/hpca-2025-full-evaluation-adjudication.md'),
    ('hpca-2025', 4, 1): note(
        'Compare added instances with their energy, state-loading, and coordination costs in the resource table.',
        'More parallel units can reduce queueing while increasing the work needed to feed and synchronize them.',
        'DynamoLLM’s publication abstract describes changing instance count, model division, and frequency together. The capacity and power numbers are original.', 'https://ieeexplore.ieee.org/document/10946802'),
    ('hpca-2025', 4, 2): note(
        'Keep arrivals at 15 per second but lower each of three devices’ completion rates from six to four. Calculate how quickly the queue grows.',
        'An unchanged arrival count can hide longer requests. A controller using the old completion rate would overestimate available capacity.',
        'The local DynamoLLM review limits results to the tested H100 setup and request traces. The changed-request example is original.', 'analysis/hpca-2025-full-evaluation-adjudication.md'),
    ('hpca-2025', 5, 1): note(
        'Charge generation, tuning, profiling, or retraining where the workload actually pays for it, then test reuse break-even.',
        'A one-time preparation cost is not free for a single request, even if repeated use eventually repays it.',
        'The VQ-LLM evaluation review records preparation tied to the model and hardware. The 100 ms setup and batch calculations are original.', 'analysis/hpca-2025-full-evaluation-adjudication.md'),
    ('hpca-2025', 5, 2): note(
        'Compare discovering an unsupported request after conversion with selecting the general routine before conversion. Count any inspection needed to choose safely.',
        'A fast supported case does not establish application-level speed if common cases use a slow fallback.',
        'The local review distinguishes EXION’s unavailable optimizations for some models from VQ-LLM’s untested multi-GPU setting. Neither establishes the invented fallback timings.', 'analysis/hpca-2025-full-evaluation-adjudication.md'),
    ('hpca-2025', 6, 1): note(
        'Check transitions, power, and timing at mode changes rather than only measuring the steady-state mode.',
        'A schedule that fits an ideal steady state can violate a physical limit during switching or boundary activity.',
        'The MVE review records cache writeback at mode changes. The power-transition schedule is original and is not an MVE measurement.', 'analysis/hpca-2025-full-evaluation-adjudication.md'),
    ('hpca-2025', 6, 2): note(
        'Separate measured values from technology-model assumptions and scaling claims in the evidence ledger.',
        'A model of noise or area is not a measurement of the fabricated system.',
        'The IRIS review separates GPU energy measurements from modeled and technology-scaled components. No experiment was independently reproduced here.', 'analysis/hpca-2025-full-evaluation-adjudication.md'),
    ('hpca-2025', 7, 1): note(
        'Separate first-output delay from later output gaps and from complete request time in the serving timeline.',
        'An average rate can look good while first output or tail gaps violate the service promise.',
        'The DynamoLLM review distinguishes first-output and later-output delays. The four-piece timelines are original.', 'analysis/hpca-2025-full-evaluation-adjudication.md'),
    ('hpca-2025', 7, 2): note(
        'State the task-specific quality measure before accepting a faster approximate result.',
        'A result that violates a required constraint cannot be redeemed by lower latency or higher occupancy.',
        'The Choco-Q review distinguishes constraint satisfaction from solution quality and timing. The coloring illustration is original.', 'analysis/hpca-2025-full-evaluation-adjudication.md'),
    ('hpca-2025', 8, 1): note(
        'Vary access pattern, sparsity, and reuse in the worked comparison until the extra organization cost exceeds the saving.',
        'The mechanism stops helping when its setup or movement cost dominates the skipped work.',
        'The VQ-LLM and MVE reviews record profiling and transition limits. The worker timings and break-even changes are original.', 'analysis/hpca-2025-full-evaluation-adjudication.md'),
    ('hpca-2025', 8, 2): note(
        'Recheck conversion support, timing, capacity, and calibration when moving the design to another device.',
        'A fitted model for one device does not automatically predict a different memory, clock, or power environment.',
        'The DynamoLLM review limits its hardware evidence to a homogeneous H100 setup. The faster-worker comparison is original.', 'analysis/hpca-2025-full-evaluation-adjudication.md'),

    ('micro-2025', 1, 1): note(
        'Compare the recent-use rule with the invented permanent reservation. Track what remains in each slot when the program changes its accesses.',
        'Keeping unused code indefinitely can leave too little space for the code that now runs. Replacement prediction does not establish shared-data validity.',
        'TRRIP supplies code-use labels through page attributes. The permanent-reservation failure is original and is not TRRIP’s replacement policy.', 'https://arxiv.org/html/2509.14041v1'),
    ('micro-2025', 1, 2): note(
        'Keep the single fetch-tracking record occupied until A finishes at time 10. Only then start B’s fetch.',
        'Ignoring the occupied record predicts B’s completion at 12 instead of 20, despite using the same ten-unit fetch duration.',
        'The fetch-record example is original. The local TRRIP review records simulation and proxy workloads, not a fabricated cache or this exact capacity.', 'analysis/micro-2025-full-evaluation-adjudication-006-010.md'),
    ('micro-2025', 2, 1): note(
        'Place a consumer beside its input and then count the values that still cross the partition boundary.',
        'Moving one operation near data does not help if its partial results must immediately return across the same boundary.',
        'Pimba’s abstract describes near-memory update units shared across banks. The subtotal and transfer arithmetic is original.', 'https://arxiv.org/abs/2507.10178'),
    ('micro-2025', 2, 2): note(
        'Track R1 and R2 by identity even if R2 arrives first. The required subtraction is R2 − R1, not an operation chosen by arrival order.',
        'Without result identifiers or a guaranteed order, the next operation can produce −4 instead of 4.',
        'The labeled-subtotal example is original, not a Pimba protocol. The local review records Pimba’s modeled execution and remaining state-update dependencies.', 'analysis/micro-2025-full-evaluation-adjudication-006-010.md'),
    ('micro-2025', 3, 1): note(
        'Change the invented group’s largest value from 7 to 28, then decode the smaller values using the new scale of four.',
        'Making the largest value fit can coarsen the available steps for smaller values; fitting in range does not preserve every value.',
        'MX+ supplies the outlier-representation connection. The unsigned codes, scales, and rounding convention are original.', 'https://snu.elsevierpure.com/en/publications/mx-pushing-the-limits-of-microscaling-formats-for-efficient-large/'),
    ('micro-2025', 3, 2): note(
        'Decode codes 3 and 5 separately, then compare their sum with decoding raw code 8. Account for the offset once per original value.',
        'Treating a sum of two codes as one encoded value subtracts the offset the wrong number of times.',
        'The arithmetic is original. The MX+ evaluation review separates model quality, GPU software timing, and modeled arithmetic hardware.', 'analysis/micro-2025-full-evaluation-adjudication-006-010.md'),
    ('micro-2025', 4, 1): note(
        'Compare grouped and dispersed activity while charging grouping metadata, setup, and synchronization.',
        'A more balanced grouping can lose when per-group control work exceeds the saved idle time.',
        'The Task-LP review separates hardware task placement from precomputed server groupings. The split-job timings are original.', 'analysis/micro-2025-full-evaluation-adjudication-011-015.md'),
    ('micro-2025', 4, 2): note(
        'Draw the event timeline instead of using only an average rate; include full-buffer and refill events.',
        'An average can hide the moment a buffer fills and legally blocks the producer.',
        'The OmniSim review describes conditional queues, dependencies, and deadlock tests against detailed simulation. The two-slot burst is original.', 'analysis/micro-2025-full-evaluation-adjudication-011-015.md'),
    ('micro-2025', 5, 1): note(
        'Compare the generated instructions with an independent reference behavior, including boundary and state cases.',
        'Successful code generation or parsing does not prove that the emitted instruction sequence preserves behavior.',
        'The RISSP evaluation review requires retargeting and verification for unsupported instructions. The four-entry implementation is original.', 'analysis/micro-2025-full-evaluation-adjudication-011-015.md'),
    ('micro-2025', 5, 2): note(
        'List which cache, memory, and timing details the model retains before trusting its scheduling prediction.',
        'A model can rank policies incorrectly if it omits the resource that actually becomes full.',
        'The OmniSim review bounds the supported queue/execution model; the RISSP review bounds instruction compatibility. Neither proves this invented fast path correct.', 'analysis/micro-2025-full-evaluation-adjudication-011-015.md'),
    ('micro-2025', 6, 1): note(
        'State the attacker’s allowed observations and the exact forbidden effect before interpreting the attack trace.',
        'A failed attack in one setup does not prove protection against a different observer, input, or placement.',
        'The local ρHammer review records real-platform attack results with privilege and memory-configuration limits. The ten-trial example is original.', 'analysis/micro-2025-full-evaluation-adjudication-001-005.md'),
    ('micro-2025', 6, 2): note(
        'Check both frame rate and position error in the toy tracking example. The 40-frame-per-second case fails its separate error limit.',
        'A favorable average image score or high frame rate can hide an unacceptable position estimate.',
        'The RTGS review separates rendering quality, camera-estimation error, and modeled hardware timing. The 5 cm threshold and toy results are original.', 'analysis/micro-2025-full-evaluation-adjudication-006-010.md'),
    ('micro-2025', 7, 1): note(
        'Place memory size, link rate, clock, and transition costs beside the workload’s actual request volume.',
        'A design that fits the average case can fail when the workload reaches the limiting capacity.',
        'The ReGate review records workload-dependent power-control costs. The frequency, capacity, and idle-energy calculations are original.', 'analysis/micro-2025-full-evaluation-adjudication-016-020.md'),
    ('micro-2025', 7, 2): note(
        'Label every technology parameter as measured, synthesized, modeled, or projected before changing it.',
        'A new process or device can change leakage, routing, conversion, and clock tradeoffs in different directions.',
        'The ReGate review separates circuit estimates and calibrated simulation from measured processor observations. Its complete-workload savings remain modeled.', 'analysis/micro-2025-full-evaluation-adjudication-016-020.md'),
    ('micro-2025', 8, 1): note(
        'Hold input trace, accepted result, resource budget, and comparison settings fixed while changing one mechanism.',
        'A gain cannot be assigned to the proposed policy if the workload or resource allocation changed with it.',
        'The commercial compute-in-SRAM review records separate layout/transfer optimizations and their combination. The four-combination timing tables are original.', 'analysis/micro-2025-full-evaluation-adjudication-016-020.md'),
    ('micro-2025', 8, 2): note(
        'Separate a measured kernel or simulator component from the projected full design that surrounds it.',
        'One measured component does not make estimated caches, links, or software integration measured.',
        'The commercial compute-in-SRAM review identifies directly measured device components combined with simulated external-memory timing in the retrieval study.', 'analysis/micro-2025-full-evaluation-adjudication-016-020.md'),

    ('sc-2025', 1, 1): note(
        'In the concentration example, check the amount of substance and the volume represented by each input before averaging.',
        'A program can correctly calculate an unweighted average while answering the wrong scientific question.',
        'The InferA review distinguishes executable analysis from scientific satisfaction. The weighted-concentration calculation is original.', 'analysis/sc-2025-full-evaluation-adjudication-091-095.md'),
    ('sc-2025', 1, 2): note(
        'Trace preparation, execution, validation, and output movement in the total workflow time.',
        'A faster kernel does not shorten the accepted workflow if staging or validation dominates.',
        'The SimAI-Bench review separates transfer performance from complete coupled-workflow timing and limits scientific validation. The solver timeline is original.', 'analysis/sc-2025-full-evaluation-adjudication-096-100.md'),
    ('sc-2025', 2, 1): note(
        'Follow one collective exchange through the physical links and count the busiest route, not aggregate bandwidth alone.',
        'A high total network rate can still bottleneck a particular all-to-one or neighbor exchange.',
        'The cMPI review records shared-memory communication costs and limits group-wide operation coverage. The shared-link example is original.', 'analysis/sc-2025-full-evaluation-adjudication-106-110.md'),
    ('sc-2025', 2, 2): note(
        'Compare nearby placement with the available capacity and interference from other work in the locality example.',
        'The closest memory may not hold the task, forcing spills that erase the locality benefit.',
        'The D-CHAG review records memory reduction alongside participant-dependent aggregation work. The two 6-GB partitions are original teaching inputs.', 'analysis/sc-2025-full-evaluation-adjudication-096-100.md'),
    ('sc-2025', 3, 1): note(
        'Add encoding, decoding, metadata, and layout conversion to the compressed-file size comparison.',
        'A smaller file can take longer to supply the next computation when decoding or reordering dominates.',
        'cuSZ-Hi is inspected for prediction, quantization, and encoding stages; the transfer arithmetic is original.', 'https://arxiv.org/html/2507.11165v1'),
    ('sc-2025', 3, 2): note(
        'Subtract the two reconstructed values and compare the result with the exact difference. Check the sign as well as the absolute error.',
        'Errors within the per-value limit can reverse the sign of a small difference between similar numbers.',
        'The subtraction and sum bounds are original. The cuSZ-Hi review limits quality evidence to tested datasets and measures, not every downstream scientific quantity.', 'analysis/sc-2025-full-evaluation-adjudication-111-115.md'),
    ('sc-2025', 4, 1): note(
        'Draw the first transfer, each calculation, and the final completion. Do not report only the interval between completed chunks.',
        'A short scientific run may finish before the pipeline reaches its steady rate.',
        'The AGILE review separates synchronous and asynchronous execution. The 22 ms and 30 ms chunk timelines are original.', 'analysis/sc-2025-full-evaluation-adjudication-111-115.md'),
    ('sc-2025', 4, 2): note(
        'Mark shared memory and network resources on both supposedly overlapping activities and size the buffer over time.',
        'A spare buffer cannot make the single transfer engine run faster. Reusing an occupied buffer can overwrite an input still being calculated.',
        'The AGILE review records cache and request-pressure dependence. The one-, two-, and three-buffer schedules are original teaching models.', 'analysis/sc-2025-full-evaluation-adjudication-111-115.md'),
    ('sc-2025', 5, 1): note(
        'State what the answer must satisfy and how much rounding error is allowed before moving the program to another device.',
        'Two devices can accept the same program yet round intermediate results differently.',
        'The FFTMatvec review describes choosing numerical precision subject to an error limit. The three-digit decimal example is original.', 'analysis/sc-2025-full-evaluation-adjudication-101-105.md'),
    ('sc-2025', 5, 2): note(
        'Count sending inputs, calculating, and returning results. State whether later calculations can reuse inputs already on the device.',
        'A faster calculation can still produce a slower job when moving its inputs and results costs more than the time saved.',
        'The FFTMatvec review separates translation, tuning, precision choices, and communication costs. The 8 ms and 9 ms jobs are original examples.', 'analysis/sc-2025-full-evaluation-adjudication-101-105.md'),
    ('sc-2025', 6, 1): note(
        'Label whether a scaling experiment keeps total work fixed or grows it with resource count before interpreting the curve.',
        'Strong and weak scaling answer different questions and cannot be compared as one speedup.',
        'QuaTrEx reports growing-work experiments and excludes input/output from its performance measurement. The worker-cost formula is original.', 'analysis/sc-2025-full-evaluation-adjudication-101-105.md'),
    ('sc-2025', 6, 2): note(
        'Separate the fixed delay of an exchange from the time spent moving its bytes. Then ask which part a proposed change actually reduces.',
        'Halving the bytes does not halve an exchange whose fixed delay is unchanged.',
        'FFTMatvec reports communication-delay limits at larger device counts. The 3 ms to 2.5 ms example is original.', 'analysis/sc-2025-full-evaluation-adjudication-101-105.md'),
    ('sc-2025', 7, 1): note(
        'When two compiled programs give different answers, check the permitted numerical behavior and whether the source program has a defined result.',
        'A disagreement can be allowed or caused by an invalid test program; detecting it does not identify a compiler bug by itself.',
        'LLM4FP explicitly discusses allowed differences and false positives. The retry probabilities are original teaching assumptions.', 'analysis/sc-2025-full-evaluation-adjudication-106-110.md'),
    ('sc-2025', 7, 2): note(
        'Check both the time saved by writing less information and whether the saved pieces support acceptable continued training.',
        'A smaller saved state is not useful if required information is missing or incompatible. Successful resumption alone does not establish identical numerical updates.',
        'LLMTailor reports storage, saving time, and resumed-model checks for selected training cases. The 119-second failure trace is original.', 'analysis/sc-2025-full-evaluation-adjudication-086-090.md'),
    ('sc-2025', 8, 1): note(
        'In the original timing example, recording events makes both programs take 12 seconds: one has 10 seconds of work plus 2 of recording, the other 8 plus 4. Equal recorded times conceal different unrecorded times.',
        'Subtracting the same recording cost from both runs gives the wrong correction for at least one. Separately, a blocked hardware test supplies no answer; an incorrect sharing indication supplies a misleading one.',
        'MT4G section V reports the blocked MI300X test and incorrect P6000 sharing indication as distinct cases. The 12-second recording example is invented, not an MT4G measurement.', 'https://arxiv.org/html/2511.05958v1#S5'),
    ('sc-2025', 8, 2): note(
        'In the original example, a constant 10-second prediction matches the average of equal numbers of 2- and 18-second jobs. Yet every prediction misses by 8 seconds. State whether a repeat check confirms the average, individual times, or another quantity.',
        'Repeating the average comparison cannot establish accurate individual predictions. Also separate jobs used to choose model settings from jobs used only to test those settings; agreement on the first set does not answer the second question.',
        'CGSim section 4.2 describes historical-job calibration but does not specify a separate held-out job set there. The timing example and proposed separate-data check are teaching guidance, not reported CGSim results.', 'https://arxiv.org/html/2510.00822v1#S4.SS2'),
})

FLASH = 'https://proceedings.mlsys.org/paper_files/paper/2025/file/dbf02b21d77409a2db30e56866a8ab3a-Paper-Conference.pdf'
BLITZ = 'https://www.usenix.org/system/files/osdi25-zhang-dingyan.pdf'
CXL = 'https://johnwickerson.github.io/papers/cxl_cache_ASPLOS25.pdf'
AUTOPRAC = 'https://arxiv.org/abs/2606.23905'
SMACK = 'https://arxiv.org/abs/2502.05429'
PMVERIFY = 'https://feihe.github.io/materials/asplos25.pdf'
FAST = 'https://www.usenix.org/system/files/nsdi26-wu-bingyang.pdf'
WALLET = 'https://www.usenix.org/system/files/nsdi26-sabanic.pdf'
PRVTEL = 'https://www.usenix.org/system/files/nsdi26-zhou-yajie.pdf'
PRIVATE_SET_INTERSECTION = 'https://www.usenix.org/system/files/nsdi26-arpaci.pdf'
SLOWPOKE = 'https://www.usenix.org/system/files/nsdi26-xie.pdf'
CC_EVAL = 'https://www.usenix.org/system/files/nsdi26-liu-tianfeng.pdf'
COACH = 'https://www.microsoft.com/en-us/research/publication/coach-exploiting-temporal-patterns-for-all-resource-oversubscription-in-cloud-platforms/'
BLOCKDEPEND = 'https://dl.acm.org/doi/10.1145/3676641.3716264'
VOYAGER = 'https://doi.org/10.1145/3676642.3736121'
MVQ = 'https://arxiv.org/abs/2412.10261'
PAST_FUTURE = 'https://doi.org/10.1145/3676641.3716011'
INSTRUCTION_TLB = 'https://gvavou5.github.io/Documents/Vavouliotis_ASPLOS25.pdf'
CENT = 'https://arxiv.org/abs/2502.07578'
PUSHTAP = 'https://arxiv.org/abs/2508.02309'
CONCERTO = 'https://doi.org/10.1145/3669940.3707223'
PLAID = 'https://arxiv.org/abs/2412.08137'
MICRO_BLOSSOM = 'https://arxiv.org/abs/2502.14787'
CXL_COHERENCE = 'https://arxiv.org/abs/2410.15908'
FSMOE = 'https://arxiv.org/abs/2501.10714'
COSERVE = 'https://arxiv.org/abs/2503.02354'
RANGE_BLOCKS = 'https://doi.org/10.1145/3669940.3707225'
DVFS = 'https://doi.org/10.1145/3669940.3707231'
COACH_PDF = 'https://www.microsoft.com/en-us/research/wp-content/uploads/2024/12/Coach-Resource-Oversubscription.pdf'


def add_route_notes(route_id, source, rows):
    for row in rows:
        theme_number, subtheme_number, example, failure, evidence = row[:5]
        row_source = row[5] if len(row) > 5 else source
        SUBTHEME_NOTES[(route_id, theme_number, subtheme_number)] = note(example, failure, evidence, row_source)


add_route_notes('mlsys-2025', FLASH, [
    (1, 1, 'Compare the two orders of a matrix operation and count the intermediate each order must materialize.', 'An algebraic saving disappears when a nonlinear step, conversion, or unsupported operator sits between the reordered products.', 'FlashInfer is inspected for attention execution and scheduling; the small matrix is an original calculation.'),
    (1, 2, 'Use the precision example to count storage, conversion, and the error introduced before the next operator.', 'A smaller representation loses if conversion dominates or if its error crosses the task’s acceptance boundary.', 'The FlashInfer paper is a serving-engine source; the precision tradeoff is a course-wide teaching model.'),
    (1, 3, 'For the indexed sum, compare dense visits with retained entries plus index handling.', 'Skipping a nonzero contribution changes the answer, and irregular survivors can cost more to locate than dense values.', 'The paper’s attention engine is not treated as evidence for a general sparsity gain; the count is original.'),
    (2, 1, 'Mark a reusable prefix and the conditions that make its intermediate state valid for a later request.', 'Matching text alone is insufficient when model parameters, positions, or masks differ.', 'FlashInfer’s serving scope motivates the reuse question; the validity-key example is original.'),
    (2, 2, 'Separate parameters, gradients, saved activations, and update history in the training-memory peak calculation.', 'Recomputing activations does not remove optimizer state or parameters that still coexist at the peak.', 'The route connects serving and training memory as different state categories; no training result is attributed to FlashInfer.'),
    (2, 3, 'Calculate whether a value is already at the consumer or must cross a slower boundary before the arithmetic starts.', 'A faster operation cannot use its rate while waiting for a remote operand or a conversion buffer.', 'FlashInfer supplies an inspected execution-engine source; the storage schedule is original.'),
    (3, 1, 'Assign each partition an owner and trace where its produced intermediate is consumed next.', 'A balanced arithmetic split can create an exchange bottleneck when one partition owns data needed by all others.', 'The paper’s uneven-work scheduling supports this dependency framing; the partition totals are original.'),
    (3, 2, 'Draw calculation and transfer intervals and subtract overlap only where the data is ready and resources are independent.', 'An asynchronous API call does not establish legal overlap when the next operation depends on the transfer.', 'FlashInfer is inspected for split/combine execution; the timeline is an original teaching model.'),
    (3, 3, 'Increase input length and recount saved context, transfer volume, and buffer capacity rather than scaling one term alone.', 'Longer inputs can change the limiting resource and make a previously useful partition spill or wait.', 'The paper evaluates stated serving lengths and devices; behavior outside those conditions is unknown.'),
    (4, 1, 'Order the 8-ms and two 2-ms requests by the stated service promise, then compute each completion time.', 'Short-first improves the mean but can miss a long request’s deadline.', 'FlashInfer reports serving delay metrics under its stated load adjustment; the queue is original.'),
    (4, 2, 'Include state-loading and preparation time when moving a request to another worker.', 'A second worker that is not ready can turn migration into extra latency and still miss the deadline.', 'The source is inspected for serving-engine scheduling; no allocation experiment beyond the toy model is claimed.'),
    (4, 3, 'Cap the shared input path before adding nominal worker capacity in the throughput example.', 'Two fast workers cannot sustain more requests than their shared input or memory path supplies.', 'FlashInfer’s A100/H100 serving boundary remains separate from this shared-resource model.'),
    (5, 1, 'Compare the training batch timeline before and after filtering, and inspect which rare examples remain.', 'A faster data path that drops cases required in deployment changes the learning problem.', 'The route’s data-supply example is original; FlashInfer is an inference-serving paper, not a data-selection result.'),
    (5, 2, 'Track which sites contribute updates and how their different data distributions affect the resulting batch mix.', 'Local storage does not prove privacy or that the combined update represents every site fairly.', 'The course connects this to its distributed-learning lesson; no federated result is attributed to FlashInfer.'),
    (5, 3, 'Pipeline parsing, filtering, arrangement, and transfer beside the training device’s compute interval.', 'Halving preparation time does not preserve the workload if labels or difficult records are silently removed.', 'The timing is an original pipeline model; the FlashInfer source remains bounded to serving.'),
    (6, 1, 'Compare a device’s initial rate with its sustained rate over the complete 1,000-request run.', 'Extending a short peak rate across a long run understates completion time and energy.', 'MEADOW’s recorded evaluation is on a sub-10-W FPGA; it does not establish this stipulated rate change or a thermal law. The rate and power schedule is an original model.', 'https://openreview.net/forum?id=fR7Plt5D7p'),
    (6, 2, 'Add transfer and preparation costs when assigning work between CPU, GPU, or another processing unit.', 'The unit with faster arithmetic can lose after input movement and unsupported-operation fallback.', 'FlexInfer is the CPU–GPU/PCIe offload lead. The course’s two-device rates, powers, and preparation costs are stipulated teaching values, not its measurements.', 'https://openreview.net/forum?id=sFNRNTduKO'),
    (6, 3, 'Count the memory path, conversion, and fallback around the nominal execution kernel.', 'A kernel speedup can be irrelevant when hardware-aware movement dominates the request.', 'MAS-Attention is the edge-accelerator dataflow lead; MEADOW is the FPGA memory/dataflow lead. Neither is evidence for the toy ranking or a universal device claim.', 'https://openreview.net/forum?id=fLSlGn641R'),
    (7, 1, 'Compare predicted and actual completion times at the admission threshold, not only their average error.', 'A low mean error can still accept a deadline miss and reject a request that would pass.', 'AIOpsLab is a cloud-agent evaluation lead; the four-request admission example and its prediction values are original teaching material.', 'https://openreview.net/forum?id=3EXBLwGxtq'),
    (7, 2, 'Use a genuine worst-case bound to decide a safe prediction threshold, and label a mean as descriptive.', 'An observed sample maximum is not a universal future bound.', 'The uncertainty paper is a lead in multimodal robotics, not evidence for this toy upper-error guarantee. Its catalog record is abstract-only; local text availability is not an independent reproduction.', 'https://openreview.net/forum?id=HPHrIBlJYw'),
    (7, 3, 'Follow a model file through loading, parsing, and execution and identify the component enforcing allowed behavior.', 'A timing predictor cannot make an untrusted loader safe.', 'The supply-chain paper analyzes attacks through Python package behavior; the invented model-file field is not its finding, but illustrates why the real interpreter and trust boundary must be traced.', 'https://openreview.net/forum?id=EH5PZW6aCr'),
    (8, 1, 'Expose the causal structure of a triangular or masked operation and count which contributions a specialized plan can skip.', 'Reusing the plan for a full-attention request produces the wrong answer.', 'FlexAttention exposes score and mask rules to generate attention kernels. The prefix-sum plan and its costs are original teaching material; the local catalog marks this record abstract-only.', 'https://openreview.net/forum?id=2QMYV4bA0R'),
    (8, 2, 'Choose the serving plan from length, reuse, deadline, and acceptable output conditions, then charge plan creation.', 'A plan optimized for short requests can waste memory or miss deadlines for long requests.', 'XGrammar specializes constrained text generation using grammar state; the route’s length/reuse/deadline plan is a separate teaching model, not an XGrammar result.', 'https://openreview.net/forum?id=rjQfX0YgDl'),
    (8, 3, 'Remove a helper only after checking every supported call and its fallback path.', 'A helper unused in one trace may be required by another shape, model, or recovery path.', 'The Hidden Bloat study removes code unused by its tested workloads; that does not prove a capability is unnecessary for every supported input or recovery path.', 'https://openreview.net/forum?id=nddxAiToZn'),
])

add_route_notes('osdi-2025', BLITZ, [
    (1, 1, 'Trace a request from source program through compiler, runtime, and hardware and keep its required result fixed.', 'A faster lower layer is not a valid improvement if translation changes the program’s observable behavior.', 'QiMeng-Xpiler is the route’s cross-platform translation lead; the array-aliasing interface example is original and is not a QiMeng-Xpiler result.', 'https://www.usenix.org/conference/osdi25/presentation/dong'),
    (1, 2, 'List the model or program features the specialized path accepts before charging its preparation cost.', 'A specialization that rejects common operators pushes them to a slow fallback.', 'Mirage explores tensor-program transformations across GPU levels and uses probabilistic equivalence verification. This ownership/specialization example is original; probabilistic checking is not presented as absolute proof for every possible input.', 'https://www.usenix.org/conference/osdi25/presentation/wu-mengdi'),
    (1, 3, 'Compare a predicted runtime with measured completion after including loading and queue state.', 'An average prediction can hide a tail caused by a full buffer or delayed layer.', 'KPerfIR reports compiler-integrated Triton profiling with 8.2% overhead and 2% relative error in its stated evaluation. The unequal instrumentation costs are original; Neutrino is a separate profiling lead, not evidence for those toy values.', 'https://www.usenix.org/conference/osdi25/presentation/guan'),
    (2, 1, 'Map a virtual address to its physical placement and count the transfer when a page is not local.', 'A larger address space does not remove the latency or bandwidth cost of reaching the backing store.', 'FineMem studies the tradeoff between fine-grained allocation overhead and wasted space. The toy region sizes are original. The route also names Tigon, whose CXL setup is emulated; do not treat it as a physical CXL hardware measurement.', 'https://www.usenix.org/conference/osdi25/presentation/wang-xiaoyang'),
    (2, 2, 'Compare row and column layouts by the access pattern the next operation actually issues.', 'Removing a conflict for one access pattern can create a conflict for another or consume extra space.', 'Okapi separates placement for I/O performance from grouping for erasure-coded reliability; Stripeless is another storage-layout lead. Neither is evidence for the toy row/column dimensions or costs.', 'https://www.usenix.org/conference/osdi25/presentation/athlur'),
    (2, 3, 'Give a cached value a lifetime and invalidate it when the state or owner it depends on changes.', 'A cache hit with stale state is not a valid reuse.', 'Tiered Memory Management Beyond Hotness ranks placement by estimated performance impact, not access count alone. Its AOL/MLP context is distinct from this original local-hit/remote-miss model.', 'https://www.usenix.org/conference/osdi25/presentation/liu'),
    (3, 1, 'Draw message production, transfer, receipt, and acknowledgement for the distributed update.', 'A sender that finishes locally cannot claim global completion before the required recipients or durable state agree.', 'Picsou studies quorum acknowledgements for cross-cluster replicated-state-machine messages. The counter retry example is original and does not claim that message receipt alone makes an application update durable or exactly-once.', 'https://www.usenix.org/conference/osdi25/presentation/frank'),
    (3, 2, 'Place the long GPU layer and short layers on a timeline and include startup, partial loading, and drain.', 'Overlap fails when the next layer is not ready or the loader and executor share a saturated path.', 'BlitzScale sections on cooperative loading motivate the timeline; values are original.'),
    (3, 3, 'State whether replicas provide availability, ordering, or both, then identify the acknowledgement rule.', 'A replica that is reachable but stale cannot satisfy a read-after-write promise.', 'Skybridge is a distributed-cache example with an explicit bounded-staleness target; this route’s counter and read-your-write promise are original, not its measured protocol.', 'https://www.usenix.org/conference/osdi25/presentation/lyerly'),
    (4, 1, 'Compare queue orderings using both completion time and the service promise the caller receives.', 'A lower mean can hide a deadline miss or a very slow tail.', 'Kamino studies latency- and cache-aware placement of VM allocation requests; XSched studies preemption policies across XPUs. Neither paper supplies this queue or its deadlines, which are original teaching values.', 'https://www.usenix.org/conference/osdi25/presentation/domingo'),
    (4, 2, 'Charge moving state and preparing a newly allocated GPU before counting its execution capacity.', 'A nominally free GPU does not help if its layers arrive after the request’s deadline.', 'BlitzScale studies model-parameter loading and live autoscaling; the twelve-millisecond preparation cost and deadline comparison here are original, not paper measurements.'),
    (4, 3, 'Measure memory, execution, and loading contention for co-running jobs rather than inferring interference from occupancy.', 'An idle arithmetic unit can coexist with a saturated memory path.', 'The OSDI straggler study uses cluster traces and what-if analysis to investigate causes beyond hardware failure; WLB-LLM addresses workload imbalance in training. Neither establishes the toy contention cause here.', 'https://www.usenix.org/conference/osdi25/presentation/lin-jinkun'),
    (5, 1, 'Track payload, publication metadata, and the durable confirmation that orders them; test every crash point between writes.', 'If the index can survive while its payload does not, recovery can select an unreachable version.', 'F2FSJ journals metadata after data flushing in its F2FS design; the payload/index object and four-plus-two-millisecond costs are an original teaching model, not F2FSJ measurements.', 'https://www.usenix.org/conference/osdi25/presentation/cui'),
    (5, 2, 'Name the safety promise and the failure conditions separately; trace which replica or participant can still establish the result.', 'Requiring every participant may stop progress during one outage; replying too early may expose a result that can disappear.', 'Basilisk automatically derives invariants used to prove safety properties for modeled distributed protocols. It is a verification tool, not a repair mechanism or a general proof of liveness; the three-replica example is original.', 'https://www.usenix.org/conference/osdi25/presentation/zhang-tony'),
    (5, 3, 'Record the inputs and execution events that determine the result, and state which external state lies outside the recording boundary.', 'A replay can be repeatable yet fail to reproduce the cause when a remote reply or relevant event was not recorded.', 'KRR narrows recording and replay to kernel execution. The broader checklist here is original and does not imply that KRR captures remote service responses or every application-level cause.', 'https://www.usenix.org/conference/osdi25/presentation/zhang-tianren'),
    (6, 1, 'Trace sensitive data to every reader and output, including access patterns that reveal information even when contents stay hidden.', 'A final-output check misses exposure through logs, timing, queries, or shared state.', 'Paralegal checks marked data flows against stated privacy policies in Rust programs. The report-name race is original and is not one of its reported bugs; Weave and Compass address access-pattern leakage in their respective analytics/search settings.', 'https://www.usenix.org/conference/osdi25/presentation/adam'),
    (6, 2, 'List the memory, calls, and other abilities an extension needs, then enforce only those permissions at the boundary where it runs.', 'Checking only the first API call leaves later helper actions or uncounted resource use outside the restriction.', 'The Extension Interface Model treats needed features as resources and bpftime enforces its specification for userspace extensions. The mutable-name race and buffer budget are original teaching examples, not results from that system.', 'https://www.usenix.org/conference/osdi25/presentation/zheng-yusheng'),
    (6, 3, 'Separate whether an artifact is available, works as documented, reproduces named results, and matches the build deployed in service.', 'A public repository or successful reproduction does not by itself identify the binary a live service executes or prove that binary enforces a policy.', 'OSDI 2025 artifact review defines separate Available, Functional, and Results Reproduced badges. Those criteria concern the submitted artifact and paper claims; build-to-deployment identity and policy enforcement need separate evidence.', 'https://www.usenix.org/conference/osdi25/call-for-artifacts'),
    (7, 1, 'Repeat measurements under the relevant conditions and separate system variation from uncertainty in the measurement itself.', 'One average can hide both a rare slow run and uncertainty caused by how events were measured.', 'Tintin characterizes uncertainty in hardware-counter profiling, including errors from multiplexing limited counter resources; it does not supply this course’s request-delay distribution.', 'https://www.usenix.org/conference/osdi25/presentation/li'),
    (7, 2, 'Draw one request from arrival through startup, queueing, first output, and full completion.', 'A fast component or first response can coexist with a slow complete request.', 'Fork in the Road finds that isolated cold-start optimizations can miss end-to-end workflow interactions and concurrent execution. The two-, twenty-, and four-millisecond traces are original teaching values.', 'https://www.usenix.org/conference/osdi25/presentation/chai-xiaohu'),
    (7, 3, 'Write down each timer’s start, stop, and denominator before comparing measurements.', 'Two accurate timers can disagree because one omits queueing, startup, or later output.', 'Fork in the Road studies multiple cold-start stages and workflow interactions in a production serverless system; the handler-versus-user timing example is original and not its measurement.', 'https://www.usenix.org/conference/osdi25/presentation/chai-xiaohu'),
    (8, 1, 'Trace which software choices depend on a hardware feature and whether the interface lets the whole path use it.', 'A faster device or kernel adds no user benefit if another layer cannot feed, schedule, or control it.', 'PipeThreader connects software-controlled scheduling to specialized GPU units such as Tensor Cores and Tensor Memory Accelerators. Its DNN results do not supply the course’s multi-stage service timings.', 'https://www.usenix.org/conference/osdi25/presentation/cheng'),
    (8, 2, 'Count starting, loading, readiness checks, updates, and recovery before declaring a worker ready.', 'An already-running process may hold stale or incomplete state, while a cold-start benchmark may omit work done before timing begins.', 'MettEagle measures container startup and application performance on its L4Re/Linux setups. Its results are specific to those implementations and workloads; the course’s update, version-readiness, and worker-maintenance checklist extends beyond that evaluation.', 'https://www.usenix.org/conference/osdi25/presentation/miemietz'),
    (8, 3, 'Follow one request to a checked, usable result and record its delay separately from shared energy and other resource costs.', 'A shorter execution step or a smaller mean does not prove the whole service improved on every promised measure.', 'BlitzScale reports serving latency under stated service objectives and GPU serving time as distinct measures. Neither yields the course’s 15-ms component sum or evenly assigned idle energy; those are original teaching values.', 'https://www.usenix.org/conference/osdi25/presentation/zhang-dingyan'),
])

add_route_notes('asplos-2025', CXL, [
    (1, 1, 'In the 12 MB example, keep both callers’ observed free space and their later 8 MB requests visible; then compare that with Coach’s separation of guaranteed and shared resources.', 'A snapshot or forecast can be useful for planning but cannot prove that capacity is still available when the request arrives.', 'Coach studies predictions, resource sharing, and contention monitoring across cloud VMs. The two-caller pool is an original teaching example; it is not a Coach experiment.', COACH),
    (1, 2, 'Label each statement in the pool example as a guarantee, a current observation, or a prediction; only an atomic reservation makes the capacity promise enforceable.', 'Treating a prediction as a reservation can overbook the resource and violate the promise made to the caller.', 'Coach describes CoachVMs with guaranteed and oversubscribed portions and monitors for contention. Its specific cloud design does not validate this invented 12 MB interface.', COACH),
    (1, 3, 'For the dependent iterations, retain which earlier value each iteration reads before deciding what may run in parallel; BlockDepend is a reading lead for the value of tracking dependencies between computation blocks.', 'A count of iterations or operations hides the read-after-write relation and can permit an invalid schedule.', 'BlockDepend’s local paper record is abstract-only, so this is a conceptual connection, not a verified account of its implementation. The loop and dependency are teaching examples.', BLOCKDEPEND),
    (2, 1, 'Compare the two orders of plain matrix multiplication, then put softmax back into the expression and check whether the same reassociation still applies.', 'A rewrite that saves an intermediate can change the answer when a nonlinear operation breaks the algebraic identity.', 'Voyager is an abstract-only reading lead for input-adaptive algebraic transformations in graph neural networks. It does not establish the course’s matrix example or the legality of any particular rewrite.', VOYAGER),
    (2, 2, 'For a compressed model, compare both its storage/work reduction and its task accuracy against the stated baseline; do not call a different model representation lossless.', 'A model may use fewer bits and compute while missing the required accuracy, so resource savings alone do not show that it solves the same task.', 'MVQ is the inspected example for combining pruning and quantization with accuracy evaluation. It does not provide a general early-stopping rule or guarantee for other models and tasks.', MVQ),
    (2, 3, 'For each adaptive choice, record what was observed, what action followed, and how the system detects a bad prediction. Past-Future uses output-length history to estimate future memory before admitting requests.', 'A choice based on old requests can misjudge a changed output-length distribution; Past-Future relies on short-term stability and needs a warm-up period.', 'The inspected Past-Future record identifies adjacent-window stability and startup warm-up as limits. Its LLM-serving admission results do not establish that every adaptive policy handles a sudden change safely.', PAST_FUTURE),
    (3, 1, 'Track who benefits when a shared memory level favors one kind of access. In the TLB/cache paper, favoring instruction-address translations reduces code stalls but increases data-address misses and page-table reads; a second-level cache policy addresses that added pressure.', 'Improving one stream can worsen another: fewer instruction translation stalls do not mean fewer total misses or less work for every request.', 'The author version reports 18.9% and 11.4% geometric-mean improvements on its tested single-core and SMT server workloads. Those results are specific to its workload sets; the course’s four-by-four transfer counts are invented.', INSTRUCTION_TLB),
    (3, 2, 'Compare the same table layout for row-wise CPU transactions and column-wise in-memory analytical scans, as PUSHtap does for its two kinds of work.', 'A layout that helps one consumer can slow the other; even a layout that aligns both dimensions must account for device parallelism, updates, and extra stored state.', 'The inspected PUSHtap paper studies a unified format for a PIM-based HTAP system. It motivates the competing-consumer question but does not supply the course’s four-by-four array counts.', PUSHTAP),
    (3, 3, 'Separate transfer volume from transfer wait. Concerto’s abstract describes splitting critical synchronous collectives into pieces that can overlap computation; ask which wait is hidden and whether any bytes were actually removed.', 'Overlap cannot hide work across a true data dependency or when both tasks need the same busy resource, and hiding transfer time does not reduce the bytes moved.', 'Concerto is abstract-only in the local paper record. Its abstract supports the overlap mechanism, not detailed schedules or a numerical result for the course’s invented timeline.', CONCERTO),
    (4, 1, 'Trace each operation and each value to its actual execution place; Plaid’s local three-operation groups and global links make the boundary visible.', 'A pattern that does not fit a local group still uses wider communication; specialization moves cost rather than making it disappear.', 'Plaid is the source for motif-based grouping and hierarchical mapping, not evidence that three-operation motifs suit every workload.', PLAID),
    (4, 2, 'Separate the promise made to software from the invariant proved about the shared protocol.', 'A safety proof can rule out conflicting writers in the model without proving progress, larger-device behavior, or every implementation.', 'The CXL.cache paper proves single-writer/multiple-reader safety for a two-device formal model; do not extend that result to arbitrary hardware or liveness.', CXL_COHERENCE),
    (4, 3, 'Follow the data and each operation through CENT’s memory-side arithmetic, nearby processing, host work, and returned result.', 'Near-memory arithmetic can lose when remaining operations or communication dominate; moving only the central multiply is not the whole application.', 'CENT’s reported comparison is workload-specific: it is weaker on compute-heavy prefill and evaluates Llama 2 up to 32K context; the filtering arithmetic here is invented.', CENT),
    (5, 1, 'Assign the long and short tasks to minimize the time until the required final output; CoServe also groups requests by their known expert needs to avoid repeated model loading.', 'Equal task counts can leave one worker busy while another waits; an assignment that looks balanced can still lose if it moves data or triggers expensive expert swaps.', 'CoServe is evaluated on circuit-board inspection with known expert routes; it does not establish the same gains for dynamic routing or other workloads.', COSERVE),
    (5, 2, 'For each shared object, name the operations that may conflict and block only those; RANGE-BLOCKS uses key ranges as symbolic mutual-exclusion boundaries for dynamic data structures.', 'A lock prevents conflicting access but does not by itself make all participants reach a phase; a barrier or a coherence rule solves a different coordination problem.', 'The local RANGE-BLOCKS record contains only an external abstract. It supports the key-range-lock idea, not implementation, baseline, or detailed evaluation claims.', RANGE_BLOCKS),
    (5, 3, 'Draw compute and communication intervals, then overlap only work that is ready and does not contend for the same resource; FSMoE provides an inspected communication/computation scheduling example.', 'Communication cannot be hidden behind dependent work or a busy shared link; smaller pieces add handling and pipeline drain.', 'FSMoE is reviewed for MoE training on clusters up to 48 GPUs; the course’s two-stage timeline and task durations are invented, not measurements from the paper.', FSMOE),
    (6, 1, 'For the DVFS paper’s GPT-3 iteration, multiply average SoC power by iteration time; compare the resulting energy estimate with the reported power reduction.', 'Lower watts do not guarantee a proportionally lower energy total when the run takes longer, and energy at one chip boundary is not whole-facility energy.', 'The author PDF reports 250.04 W and 11.29 s at baseline, then 236.14 W and 11.47 s at its 2% performance-loss target. The 2,823 J versus 2,709 J estimate is the course’s multiplication of rounded values, not a directly reported table column.', DVFS),
    (6, 2, 'Separate a guaranteed memory allocation from a shared/oversubscribed portion, then compare saved physical memory with the measured slowdown and contention controls.', 'A capacity increase is not free throughput: cold-page displacement, faults, and contention can make the added space slow or unsafe for the workload.', 'Coach evaluates temporal, multi-resource VM oversubscription on Azure traces and its system; its memory trade-offs do not establish the invented serial-worker timing example.', COACH_PDF),
    (6, 3, 'Define accepted completion before calculating goodput: Past-Future counts serving throughput under an SLA while trading request queuing against memory-related eviction.', 'A request admitted or completed late is not automatically an accepted result; estimates based on recent output lengths may misjudge abrupt distribution changes and need warm-up.', 'Past-Future reports goodput gains for its LightLLM implementation and workloads, not the course’s 85-of-100 threshold or every notion of result quality.', PAST_FUTURE),
    (7, 1, 'Write down the property, model, assumptions, and search bounds before interpreting a proof or counterexample. Compare AutoPRAC’s model and settings with MOAT’s original claimed design.', 'A counterexample in a bounded model is evidence against that modeled claim under those assumptions; it is not by itself a demonstrated hardware attack. No counterexample within a bound is not a universal proof.', 'AutoPRAC (June 2026 preprint) reports a bounded-model counterexample to MOAT’s counter-reset policy under a simplified PRAC model/configuration; it does not model RTL or silicon and omits some full MOAT optimizations. Treat this as a model discrepancy to reconcile, not as proof that deployed DIMMs are exploitable.', AUTOPRAC),
    (7, 2, 'For SMaCk, name the attacker precisely: an unprivileged process on a sibling SMT thread of the same physical core, observing instruction-cache timing on tested x86 systems.', 'A performance-counter classifier can detect the studied pattern but does not prevent every leak or prove absence of other observation paths; the paper discusses evasions.', 'SMaCk supports this narrow x86 threat-model example. Do not generalize its detector results into a universal isolation guarantee.', SMACK),
    (7, 3, 'Trace which persistent states may survive each crash point, then separate proved-safe cases, found violations, and unknown cases.', 'A file being present does not establish a consistent application state; an unknown result is not a safe result.', 'PMVerify evaluates 26 PMDK examples: one was verified robust, 12 had violations, and 13 remained unknown. Its model, bounded-loop analysis, and supported operations limit the claim; it is not a deployment-wide recovery guarantee.', PMVERIFY),
    (8, 1, 'For a Past-Future-style request, follow arrival, admission, predicted KV-cache occupancy, decode, and SLA-qualified output. Count a result only after the stated TTFT/MTPOT conditions are met.', 'Admission can be timely and still harm the service if output-length history becomes stale: abrupt request-mix changes and startup warm-up weaken the short-window prediction.', 'Past-Future reports up to 2–3× higher goodput for its LightLLM implementation under its tested heavy-load workloads and SLA. It relies on short-window output-length stability and startup warm-up; the course’s queue/activation values are separate teaching numbers, not that experiment.', PAST_FUTURE),
    (8, 2, 'For a PUSHtap-style HTAP comparison, hold the transaction stream, analytical queries, data, and result requirements constant while checking both OLTP and OLAP throughput under concurrent access.', 'A layout that serves CPU row access and PIM column access well under one mix may not win when queries, updates, placement, or devices change.', 'PUSHtap reports 3.4× OLAP and 4.4× OLTP throughput over its multi-instance PIM-based baseline on its stated CH-benchmark setup. This is not a cross-paper ranking or a claim for every HTAP workload.', PUSHTAP),
    (8, 3, 'In Coach, separate predicted demand from guaranteed allocation; then follow the contention monitor through detection, resource reassignment or VM migration, and the period users may experience slowdown.', 'A prediction can become stale, and mitigation begins only after contention is noticed and the response takes effect; complementary demand peaks are not guaranteed for every placement.', 'Coach reports up to about 26% more VMs hosted per server in its Azure-trace-informed evaluation and system. That capacity result does not mean each workload sees no delay or that the course’s queue response time was measured by Coach.', COACH_PDF),
])

add_route_notes('nsdi-2026', FAST, [
    (1, 1, 'Compare a queue with two long jobs against one with four short jobs, then account for work that finishes or arrives while the measurement travels. The controller needs the work remaining and the observation time.', 'A detailed old reply can still send work to the wrong worker when new jobs arrive before assignment.', 'UNUM’s official abstract supports using measurement history to construct learned network state. The worker-queue calculation is original and does not describe its evaluated controller.', 'https://www.usenix.org/conference/nsdi26/presentation/chen-jiayi'),
    (1, 2, 'Charge six milliseconds for the teaching probe and one millisecond saved per later decision. Six decisions repay the cost; seven are needed for a net saving under the stated assumptions.', 'The transfer may end, or conditions may change, before later decisions recover the cost of gathering evidence.', 'PolicyCache’s official abstract describes exploration and learning within a single flow. The probe duration and savings are teaching quantities, not reported measurements.', 'https://www.usenix.org/conference/nsdi26/presentation/tian'),
    (1, 3, 'For video delivery, distinguish bytes arriving from whether playback has enough data to continue. For a worker assignment, distinguish request count from work remaining. Choose observations that address the user’s required result.', 'A high transfer rate measured after a playback interruption cannot undo the interruption the viewer already experienced.', 'UNUM’s official abstract identifies adaptive video bitrate selection and congestion control as evaluated tasks. The playback example explains why the task matters; it makes no numerical claim about UNUM.', 'https://www.usenix.org/conference/nsdi26/presentation/chen-jiayi'),
    (2, 1, 'Split work only at a point where the current output and state form a legal restart boundary.', 'Interrupting in the middle of a dependency can force recomputation or change the answer.', 'The FastServe walkthrough’s preemption threshold motivates the example; the stopping points are original.'),
    (2, 2, 'Draw the dependencies between request segments and mark which cached values must arrive before each segment can continue. Count the transfer before assigning a start time.', 'Moving a later segment without its required earlier state can force repeated calculation or prevent correct continuation.', 'Libra’s official abstract describes cooperating segments and chunked attention-cache transfers across workers. The dependency-accounting exercise is original.', 'https://www.usenix.org/conference/nsdi26/presentation/ruan-libra'),
    (2, 3, 'For each worker’s batch, identify which requests have a first-output, between-output, or completion-time target. Include waiting and movement between segments when checking each target.', 'A batch that finishes quickly can still contain a request that waited too long before joining it.', 'Libra’s official abstract describes local batches formed with service targets in mind. The three possible timing targets are teaching questions, not an assertion that its evaluation covers all three.', 'https://www.usenix.org/conference/nsdi26/presentation/ruan-libra'),
    (3, 1, 'Separate the parameters needed for model execution from the history needed to update them. List which bytes must move when a different machine takes on more expert work.', 'Moving all associated state with every assignment change can consume the time and network capacity the reassignment was meant to save.', 'SYMI’s official abstract describes fixed optimizer-state partitions and changing expert-parameter placement. The six-GB copy timeline is an original teaching model.', 'https://www.usenix.org/conference/nsdi26/presentation/skiadopoulos'),
    (3, 2, 'For each part of the state, identify where it is stored, which machine uses it, and which machine may update it. Include the path and transfer time between those roles.', 'A finished copy does not by itself grant exclusive permission to accept the next write. Placement and update authority need separate rules.', 'SYMI provides the state-placement example. Its abstract does not define the generic copy-and-handoff protocol in this lesson; that protocol is a teaching question.', 'https://www.usenix.org/conference/nsdi26/presentation/skiadopoulos'),
    (3, 3, 'Count one ten-GB base plus three one-GB differences: thirteen GB rather than forty for four separate ten-GB models, before bookkeeping.', 'A missing or wrong base prevents exact reconstruction. Lower storage consumption alone does not establish faster loading or a smaller execution footprint.', 'ZipLLM’s official abstract describes lossless differences and array-level deduplication. The sizes and loading questions are original teaching examples.', 'https://www.usenix.org/conference/nsdi26/presentation/wang-zirui'),
    (4, 1, 'Draw the startup dependencies before adding their durations. In the teaching example, independent 60 ms and 40 ms stages finish together after 60 ms; a dependency forces them to take 100 ms.', 'Even independent stages may compete for the same network or processor, making the assumed overlap unattainable.', 'HydraServe’s official abstract describes overlapping startup stages and placing workers to reduce network competition. The stage durations and deadline are original teaching quantities.', 'https://www.usenix.org/conference/nsdi26/presentation/lou'),
    (4, 2, 'At each preemption, count remaining work and the lifetime of the state that must survive until resumption.', 'Saving state for a request that will finish soon can cost more than waiting; evicting it can make resumption slower.', 'The paper’s output-aging and proactive management provide source context; the lifetime calculation is original.'),
    (4, 3, 'For a shared wireless channel, record each transmitter’s waiting intervals and delivered packets. Ask whether shorter waits for one leave another without a useful turn.', 'An aggregate delivery rate can improve while one participant experiences longer interruptions. Decide which participants and deadlines the evaluation must cover.', 'BLADE’s official abstract describes adjusting contention windows and reports fairness in its evaluated conditions. The per-participant reading questions are teaching guidance, not an additional measured result.', 'https://www.usenix.org/conference/nsdi26/presentation/guo-fengqian'),
    (5, 1, 'Separate operations completed by the network card from features handled by the host proxy. Use the teaching timings to count both the short path and the longer handoff path.', 'A faster ordinary path can coexist with an eight-millisecond exceptional path that misses the seven-millisecond deadline.', 'HybridMesh’s official abstract describes its SmartNIC and CPU-side proxy. The one-, two-, and five-millisecond costs are original teaching quantities.', 'https://www.usenix.org/conference/nsdi26/presentation/you'),
    (5, 2, 'At the handoff, state which data is being passed and which effects have already happened. The counter example requires the receiver to distinguish work still needed from work already completed.', 'Matching the request format does not prevent the host from repeating an increment the device already performed.', 'HybridMesh provides a concrete hardware/software division. Its abstract does not establish the counter protocol; that example teaches a separate interface requirement.', 'https://www.usenix.org/conference/nsdi26/presentation/you'),
    (5, 3, 'Compare the number of feature records produced each second with the number the next stage can process. In the teaching case, 200 arriving and 150 processed leave 50 more waiting each second.', 'Five hundred extra buffer slots absorb ten seconds of the imbalance but cannot sustain it indefinitely. Reducing records also requires checking classification quality.', 'FENIX’s official abstract describes rate control between switch feature extraction and FPGA inference. The rates and queue arithmetic are original and do not specify its implemented selection rule.', 'https://www.usenix.org/conference/nsdi26/presentation/gao'),
    (6, 1, 'List what must reach a replacement worker: a usable saved state, later updates if required, and the authority to continue. Count the machines and network traffic used to keep that state ready.', 'A recent copy cannot help if it fails with the original or cannot reach the replacement in time.', 'Checkmate’s official abstract describes maintaining a CPU model copy using gradients already exchanged during training. The joint-failure and transfer-deadline questions are teaching extensions.', 'https://www.usenix.org/conference/nsdi26/presentation/bhardwaj'),
    (6, 2, 'Mark which earlier results survive a failed command and which later commands depend on them. Restart from retained usable results, while separately checking whether an external recipient has already acted.', 'Repeating an earlier calculation can be harmless while repeating its notification changes the outcome. A restart point must account for both.', 'Fractal’s official abstract describes tracking dependencies and progress to limit repeated regions. The file, filter, sort, and notification example is original; command support must be checked in the paper.', 'https://www.usenix.org/conference/nsdi26/presentation/huang'),
    (6, 3, 'Use the reserve example: two failed services need 8 GB and 80 requests per second. A spare with 8 GB but only 60 requests per second stores both states while accumulating unfinished work.', 'The queue grows by 20 requests each second even with instantaneous transfer. Enough storage does not supply the missing processing rate.', 'This shared-spare calculation is original. Checkmate’s separate CPU cluster provides a concrete example of resources maintained for recovery; its abstract does not establish the shared-spare sizing rule used here.', 'https://www.usenix.org/conference/nsdi26/presentation/bhardwaj'),
    (7, 1, 'Use the ten-millisecond example to identify the missing event: execution start. Before replacing a trace with a summary, list which distinctions that summary must preserve.', 'Recording more detail later cannot recover an earlier event that was never retained. Recording everything can also change the measured execution cost.', 'μView’s official abstract supports compact streaming measurement processing and identifying informative data. The missing-event example and one-millisecond recording cost are original.', 'https://www.usenix.org/conference/nsdi26/presentation/cornacchia'),
    (7, 2, 'Before comparing a changed controller with the original, match the relevant network state and traffic. Identify the time resolution needed to reproduce the event being investigated.', 'A replay can agree with broad traffic totals while missing the order or timing that caused a short queue to form.', 'MirrorNet’s official abstract describes historical state reconstruction and alignment with a production network. The queue example is a question to test, not a reported failure of MirrorNet.', 'https://www.usenix.org/conference/nsdi26/presentation/miao'),
    (7, 3, 'Separate the number of naturally observed incidents from the number and kinds of errors deliberately introduced in simulation. Record both detections and false alerts with their observation periods.', 'Detecting one observed incident does not establish detection of every error type. No false alerts over a finite interval does not establish a zero future probability.', 'CrossCheck’s official abstract reports one detected invalid-input incident during four weeks of production checking and separate simulation results. These provide different evidence about coverage.', 'https://www.usenix.org/conference/nsdi26/presentation/krentsel'),
    (8, 1, 'Limit the information exposed to a scheduler or helper to the fields needed for its decision.', 'Extra prompt, tenant, or model information can leak data without improving the decision.', 'PrvTel connects compact telemetry retention with differential privacy; the minimum-disclosure question here is broader, and its example is original.', PRVTEL),
    (8, 2, 'Check both authorization and environment: model version, device, filesystem, and request identity.', 'A correctly authorized request can still use an unsafe helper or unexpected environment.', 'Wallet is a primary example of defining a trust boundary for sensitive serverless data; the authorization checklist here is original, not a claim about Wallet.', WALLET),
    (8, 3, 'Validate output shape, content, and provenance before returning a collaborative result to the caller.', 'A fast response with the wrong model version or incomplete tokens is not an accepted result.', 'The over-threshold private-set-intersection paper defines what a collaborative result reveals; output validation is an original extension, not a reported mechanism.', PRIVATE_SET_INTERSECTION),
    (9, 1, 'Compare the two sensor traces with average two. Only one exceeds five, so their common average cannot support the alarm decision. Choose the representation from the question the receiver must answer.', 'Discarding the difference between two inputs with different required answers makes exact decision-making impossible from that message alone.', 'KDC’s official abstract describes task-oriented representations. The four-sample alarm is an original information-loss example, not a measured KDC workload.', 'https://www.usenix.org/conference/nsdi26/presentation/chen-xingyu'),
    (9, 2, 'Count reconstruction time and check the downstream decision after reducing transmitted data. Include unusual inputs where the receiver’s prior knowledge may suggest the wrong reconstruction.', 'A plausible image or likely sensor trace does not establish that the missing input has been recovered exactly.', 'KDC’s official abstract describes receiver-side knowledge and updated context. The proposed unusual-input tests are reading guidance, not reported failures.', 'https://www.usenix.org/conference/nsdi26/presentation/chen-xingyu'),
    (9, 3, 'Separate finding a similar query from deciding that its old answer applies. In the teaching command example, preserve the requested software version before accepting reuse.', 'A relevant-looking answer can describe an older version and change the user’s result. Include the cost and accuracy of the reuse check.', 'Cortex’s official abstract describes candidate retrieval followed by a small language-model judge. The version example is original and does not assert a Cortex bug.', 'https://www.usenix.org/conference/nsdi26/presentation/ruan-cortex'),
    (10, 1, 'Set an explicit error or delay limit before allowing a predictive model to change scheduling or admission.', 'A model with good average error can make unsafe decisions near a hard boundary.', 'CCEval uses repeated trials and confidence intervals to reason about uncertain performance estimates; the per-job admission bound in this lesson is original.', CC_EVAL),
    (10, 2, 'Change one arrival, length, or state condition at a time in a what-if comparison and recompute the whole path.', 'A scenario that changes several conditions cannot show which factor caused the result.', 'Slowpoke directly studies modeled what-if changes to end-to-end throughput; the lesson’s counterfactual arithmetic is original.', SLOWPOKE),
    (10, 3, 'Search configurations only after defining the feasible region, evaluation budget, and independent validation check.', 'A search can choose a noisy lucky configuration or discard a valid one through an unsafe early screen.', 'CCEval’s evaluation of trial variability motivates the evidence boundary; the configuration-search protocol here is original.', CC_EVAL),
])


def get_subtheme_note(route_id, theme_number, subtheme_number):
    return SUBTHEME_NOTES.get((route_id, theme_number, subtheme_number))
