# Next AIMC Evidence Work Queue

This page is the review page for the next proof work.

It does not add new claims. It names the missing evidence that would make stronger claims possible.

The generated source queue is:

- `evidence/aimc-hardware-lab/next-evidence-work-queue.json`
- `evidence/aimc-hardware-lab/next-evidence-work-queue.md`

## Object

The object is the same package and model slice used by the current AIMC system state.

The queue starts from what is already proven: backend placement, simulator payload generation, guarded import, residual-aware placement, archive refresh, and claim readiness.

The queue then asks what evidence is still missing before the workbench can say more.

## Reading Rule

Each item must name five things:

- the claim it would strengthen
- the object being measured or simulated
- the method used to produce the evidence
- the artifact that would prove the result
- the claim that still remains refused

This matters because analog compute can look better than it is when simulator output, board output, and physical-layout assumptions are mixed together.

## Current Boundary

The current system can support local placement, bounded simulator evidence, and digital-control evidence.

The current system cannot yet support measured latency, measured energy, calibrated silicon, full analog macro layout, package reliability, or production readiness.

The converter boundary adds a nearer gate before those system claims: the transistor DAC is monotonic, but its nominal transfer misses half-LSB at upper codes; all three representative PVT calibration decisions require digital fallback; and the controlled mismatch run passes only `4/12` low/mid/high code checks. The `175-250 mV` early-to-late movement at midscale and full scale also means the SAR comparator time cannot be chosen independently of DAC settling.

## Next Handoff

Do the queue in evidence order.

First strengthen the model object. Then repair or bound the AIHWKIT mapping. Then expose layout risk. Then add measured runtime. Then add synchronized measured power.

For the analog converter specifically, the next evidence order is: sweep all 16 DAC codes over time, add random capacitor and switch mismatch, measure comparator noise and offset on the coupled nodes, then run the same cases through a closed-loop SAR. The analog governor must remain disabled for a corner until that chain passes its code-error and wrong-decision limits.

The first time sweep now shows why the order matters: code 8 passes briefly at 5 ns and code 15 passes through 10 ns, but both fail at later reads. The SAR test therefore needs a declared per-bit wait budget and a timestamped top-plate/comparator measurement; “the DAC settled by 70 ns” is not a sufficient acceptance rule.

The measured-transfer SAR replay is the current causal baseline: with an exact comparator, only `10/16` ideal input regions convert correctly. The same-deck SAR must now replace this replay with physical DAC thresholds at each bit decision, then repeat across PVT, mismatch, and noise. Until that happens, the analog path is a research fixture and the governor must select digital fallback.

The first same-deck DAC/comparator bit test initially failed one polarity because the comparator sampled before redistribution. A source-follower variant then exposed a midrange transfer defect. The current direct-late-sampling variant measures `16/16` correct polarities across all nominal codes. The immediate next gate is now a retained-bit 4-bit SAR sequence, followed by PVT, random mismatch, and noise cases using the same measured decision window.

The retained-bit sequence is now measured: `20/20` physical comparator trials complete, but `0/5` conversions return the expected ideal code. This confirms that comparator sign correctness is not converter accuracy. The next repair is a calibrated physical DAC transfer or a redesigned charge-redistribution network, followed by the same sequence at PVT and mismatch/noise corners.

The first source-matched calibration run now measures all 16 thresholds and improves the sequence to `4/5` correct conversions. It still fails the highest region because the code-15 threshold is about `2.082 V` and the logical-to-physical map collapses several high codes onto repeated physical codes. The next converter task is therefore to repair full-scale charge redistribution and prove a strictly usable calibrated map before enabling analog service.

The sample-capacitance diagnostic shows that interface loading is a coupled timing problem, not a one-parameter fix. The tested `200 fF`, `20 fF`, and `2 fF` values are all polarity-correct but produce non-monotonic full-scale thresholds. The next design iteration must specify the comparator storage, switch sizing, charge-injection cancellation, and decision deadline together.

The first same-deck DAC/comparator bit test is now the immediate blocker: `2/2` trials measured but only `1/2` comparator polarities matched the DAC-reference sign. The next repair must make the sign contract pass for both a below-reference and above-reference trial before adding SAR sequencing.

That order keeps the work from jumping to board-level claims before the simulator and placement boundary is clean.
