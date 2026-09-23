# Recursive AIMC self-improvement implementation status

## Long-horizon objective and current checkpoint

The end-to-end objective is a safety-gated recursive AIMC system that can
propose circuit/compiler mutations, launch bounded simulator experiments,
learn from failures and costs, transfer only reproducible improvements to
held-out workloads, compile a runtime policy with digital fallback, and then
close the loop with synchronized board measurements. The system must improve
search efficiency first, runtime analog quality/cost second, and only claim
physical improvement after measured evidence passes the same gates.

The current checkpoint is `qualified_with_open_gates`: the end-to-end readiness
audit records 13/16 requirements passed and three downstream gates open:
`strict_runtime_analog_improvement`, `physical_board_validation`, and
`runtime_cost_model_consistency`. The independent incumbent–challenger
experiment policy is approved for experiment use after reproducing 240 versus
288 simulator invocations with quality and safety preserved, but the active
runtime policy remains the verified baseline with digital fallback. The latest
45-candidate differential-feedback width refinement followed by a 9-candidate
finger-count refinement is hash-bound in the recursive queue. The best
finger-count candidate (`[32, 1, 2]`) reaches `0.7394457067411795` LSB, a
simulator-only improvement over `0.7730308829277323` LSB; it still fails the
strict `0.5` LSB analog gate. The queue therefore selects synchronized
physical-cost import first, while analog authorization remains false. No board
target is connected, so physical evidence is still absent.

The repository now contains a reproducible hardware-free loop from typed
mutation proposals through extracted Sky130 transistor simulation, PVT and
mismatch stress, held-out confidence, policy IR compilation, transformer
workload propagation, and adaptive workload recovery.

The historical qualification manifest began with 111 stages. The selected mutation is
a 1.05x differential preamp-width change. Its paired simulator search passes
27/27 trials, its held-out population passes 18/18 trials, and its materialized
candidate passes TT/SS/FF. The selected candidate is bound to policy IR by deck
hash, PVT status, mutation confidence, and workload recovery status.

The workload bridge deliberately exposed one TT seed failure under the full
six-operation analog path. A subset search recovered that case with
`q,k,v,o,fc1`; the compiled workload policy therefore has 26 full-analog
actions and one subset-analog action. The action verifier reports zero
inconsistencies. This is a useful recursive-improvement result because the
failure changes the next policy rather than being discarded.

The next substantial project is a budgeted learned policy selector. It should
compare random search, the fixed heuristic, and a contextual selector over the
same simulator-call budget. Context should include workload features, PVT,
mismatch summaries, prior failures, and operation-subset outcomes. Acceptance
requires held-out workloads and seeds, correctness first, then analog coverage
and declared cost; a training-only gain is rejected.

The remaining promotion boundary is explicit: the evidence is simulator and
software evidence. It does not establish foundry mismatch distributions,
silicon yield, board measurements, or production readiness.

## Transistor-backed converter qualification (current)

The loop now includes a transistor-backed 3-bit readout bank and a weighted
transistor-switched DAC using the repaired Sky130/ngspice compatibility bundle.
The DAC is evaluated over TT (1.8 V, 27 C), SS (1.62 V, -40 C), and FF (1.98 V,
85 C), with all eight input codes sampled at each corner. The transfer is
monotonic at all corners and settles within 10 mV between the 1 ns and 2 ns
samples. A per-corner LUT is generated; its maximum normalized calibration
error is 0.429. The resolution sweep estimates the 3-bit operating point at
0.876x digital-only relative cost, so the policy selects analog only when the
PVT, calibration, and held-out risk gates also pass. On the 36 held-out cases,
6 select analog and 30 select digital fallback, with all decisions safe.

The measured DAC remains highly nonlinear before calibration (maximum INL about
5.58 LSB). That is the next circuit-improvement target: search transistor sizes
and resistor ratios, rerun all codes across PVT, and require a materially lower
INL gate before treating the converter as a high-fidelity replacement.

The sizing search has been promoted into the canonical DAC evidence: 800k/100k/20k
resistors with 1u/4u/16u NMOS widths. This reduced maximum simulated INL from
5.58 to 5.35 LSB while preserving monotonicity and settling at all PVT corners.

A second sizing round (12 total measured candidates) improved maximum INL to
5.10 LSB using 1Meg/100k/10k resistors and 1u/8u/64u NMOS widths. This
configuration is now canonical and all downstream calibration and policy
artifacts have been regenerated from it.

Cascode isolation was measured with five cascode widths; 4u was best at 5.02
LSB INL while preserving monotonicity. This confirms that switch sizing and
simple degeneration are insufficient; further work needs a different current
summation topology or explicit linearization.

The current-mode branch search now promotes a stable 1u/6u/80u NMOS geometry
with a 100u PMOS load (3.10 LSB maximum INL), an approximately 8% improvement
over the prior 1u/8u/64u candidate. This candidate remains below the strict
0.5 LSB policy gate, so analog selection stays fail-closed.

Current-mode PMOS-load sensitivity is bounded: 64u, 96u, and 100u loads are
stable and monotonic in the measured region; the promoted 1u/6u/80u, 100u
point is best at 3.10 LSB INL; 112u and 128u are
numerically unstable. The search therefore treats 100u as the current-mode
candidate and does not extrapolate beyond the measured stable region.

## Next recursive cycle checkpoint

The current-mode branch is now connected end to end. The reproducible sizing
population now evaluates 25 candidates, with 22 passing PVT electrical checks
and the selected 1u/5u/100u NMOS, 100u PMOS-load candidate at 1.0V input drive
measured at 2.9382 LSB maximum INL.
The selected PVT artifact is regenerated after the search and is bound into a
current-mode policy bridge and a 36-case held-out workload application. The
bridge correctly rejects analog promotion because the 0.5 LSB INL gate fails;
all 36 workload cases therefore use verified digital fallback.

The earlier recursive cycle manifest recorded 104 stages and passed
142 checks with zero integrity errors. This was a completed recursive evidence
cycle, not completion of the analog replacement objective. The next mutation
must improve analog coverage or declared relative cost while retaining the
same correctness and fallback gates. This is an approximately 13% INL
improvement over the prior 1u/8u/64u, 100u candidate, but it remains above
the 0.5 LSB promotion threshold.

## Contextual recursive-learning checkpoint

The first current-tree contextual policy experiment is implemented in
`run_contextual_bandit_experiment.py`. It consumes the frozen candidate ledger,
fits empirical action values only on the established training corner/seed set
(`tt/0`, `tt/1`, and `ss/2`), and evaluates disjoint held-out cases. Digital
fallback is an explicit always-safe action. The run is recorded in
`contextual-bandit-experiment.json`.

The held-out result is `3/3` safe decisions, with `0/3` analog promotions and
digital fallback for all three cases. The matching oracle also finds no safe
analog promotion in this ledger split. This is useful recursive-learning
evidence because it demonstrates a real train/held-out boundary and preserves
the conservative decision when the evidence does not support analog use. It is
not yet deep reinforcement learning: there is no neural policy, online episode
interaction, or hardware reward. The next learning milestone is to compare
this contextual policy with the fixed heuristic and random/grid baselines over
the expanded workload/PVT population at equal candidate budgets, then add a
proposal action that can generate a new simulator trial rather than only rank
already evaluated candidates.

The equal-budget comparison is now recorded in
`recursive-policy-benchmark.json`. With a strict `12`-candidate budget over
`36` held-out workload/PVT cases, the contextual policy found `6` analog cases,
random found `3`, and grid/failure-memory found `0`; all four methods preserved
`36/36` safe decisions. This result is a policy-ordering signal over a frozen
simulator ledger, not evidence that the contextual policy is globally better:
the reported modeled energy is higher for the analog-promoting policy because
the objective intentionally ranks correctness and analog coverage before the
declared cost proxy. The next experiment must therefore add an explicit
Pareto/coverage-cost comparison and, crucially, an action that launches a new
simulator trial instead of selecting only among precomputed rows.

The proposal/action bridge is now driven directly by the tabular-Q persistent
performance memory in `propose_and_run_new_trials.py`. It selected a safe
high-reward `k`, 12-bit, 1.01-gain action, generated four mutations outside the
frozen search grid (`k` at 9/11 bits and gain `0.995`/`1.005`), and executed
`144` fresh three-repeat simulator trials over `36` held-out cases. The
resulting `new-trial-proposals.json` contains `16` reliable rows and all four
new actions have at least one reliable held-out case. These rows remain
separate from the training ledger and are not silently promoted into policy
evidence. The explicit ingestion step then selects the 11-bit/1.005-gain
proposal from its fresh-trial reliability, preserving an immutable parent
ledger and testing transfer on the independent MLP sweep.

That gate is now exercised by `ingest_retrain_transfer.py`, which emits the
content-hashed `derived-ledger-transfer.json`. It preserves the `216`-candidate
parent ledger, binds the `144` fresh trial rows by artifact digest, and selects
the `k`/11-bit/1.005-gain proposal from its source reliability results. Transfer
to the independent MLP sweep maps 11 bits to the nearest available 10-bit
configuration: `2` target cases use selective analog and `2` use digital
fallback, with `4/4` target decisions safe. This is a successful software
transfer gate with an explicit fallback outcome, not proof that the proposal is
generally superior or that it transfers to hardware.

The derived-policy frontier is now evaluated by
`evaluate_derived_policy_frontier.py`. Over the same `36` held-out source
cases, a coverage-first policy selects analog in `7` cases with modeled energy
`139228.07`, while a cost-aware policy requires the candidate to beat the
`3072` digital baseline and therefore selects digital fallback in all `36`
cases with modeled energy `110592.0`. Both policies preserve `36/36` safe
decisions. This is the required correction to the earlier coverage-only
interpretation: the current analog candidates do not yet demonstrate a modeled
system-cost win once the digital baseline is enforced.

`audit_cost_model_break_even.py` now makes that blocker quantitative. Across
`12` count/precision points, none beats the declared digital baseline. Even if
ADC conversion cost were zero, the analog-MAC coefficient would need to be at
most `0.046875` for break-even; even if analog compute were free, the lowest
ADC-bit break-even coefficient is `10.6667`, below the current declared `20`.
This is an analytic sensitivity result, not a hardware conclusion. It changes
the next recursive action: the system must measure or structurally recalibrate
analog compute, converter energy, SRAM movement, and boundary reuse before
learning cost-based analog promotion.

The physical-cost bridge is now explicit in
`build_physical_cost_calibration_contract.py` and
`physical-cost-calibration-contract.json`. It imports the provisional
`4.273e-12 J` per-conversion extracted/SPICE bound and the three-corner timing
evidence, but keeps promotion blocked until the same run supplies digital
baseline energy, analog-array compute energy, SRAM movement, calibration/probe
energy, and aligned supply/temperature traces. This prevents a provisional
converter number from being mistaken for an end-to-end energy measurement.

The synchronized measurement harness rehearsal is now implemented in
`run_synchronized_cost_rehearsal.py` and recorded in
`synchronized-cost-rehearsal.json`. It runs the same frozen fixture through
digital baseline, hybrid `q` candidate, and guarded fallback paths, emits
command/SRAM/converter/compute/output timeline events, and preserves output
hashes. The fallback reproduces the digital output exactly and the hybrid
fixture passes its declared quality check. Every duration and energy field is
explicitly marked modeled or provisional, and promotion remains blocked until
the physical import supplies current, voltage, temperature, and clock traces.

The import boundary is now executable in
`validate_physical_measurement_import.py`. With no bundle present it rejects
the import and records `no_measured_claim`; it requires synchronized package,
workload, board, runtime-trace, timestamp, latency, energy, power, and thermal
fields plus measured-board provenance. This makes the current absence of lab
data an explicit machine-checked state and prevents simulator or provisional
artifacts from entering the physical evidence layer by accident.

The workload-bound board template is now generated by
`build_board_measurement_bundle_template.py` as
`board-measurement-bundle.template.json`. It is anchored to the transformer
handoff's input, expected-output, and shared-object hashes. Running the strict
validator against the template correctly rejects its placeholders and missing
samples, so the first connected-board run has a precise package identity and
cannot be mistaken for completed measurement evidence.

The physical execution handoff is documented in
`BOARD_MEASUREMENT_RUNBOOK.md`. The configured Android SDK provides `adb`, but
`adb devices -l` currently returns no connected target; no board run was
attempted and no synthetic measurement was promoted. The runbook binds the required package
hashes, shared runtime trace ID, timestamps, power/current samples, thermal
trace, raw logs, and strict import sequence for the first real target.

The local package-preparation path has now been executed successfully. The
materialized package at `/tmp/hexagon-transformer-block-board-package` matches
the handoff for `test_main.so`, `input.bin`, and `expected.bin`; the board gate
now reports only `no connected Android/Hexagon device`. This closes the local
package-integrity gate without changing the physical-measurement claim status.

`record_prepared_board_package.py` now persists that result as
`prepared-board-package.json`: all three handoff hashes match and
`board_execution` remains explicitly `not_run`. This makes package readiness
replayable from the repository instead of relying on an ephemeral `/tmp`
directory, while preserving the absence of any physical measurement claim.

The Hexagon simulator was then rerun after staging host-local compatibility
symlinks for its legacy `libncurses.so.5` request. All three canonical runs
passed with 224 exact floating-point differences, zero tolerance failures, and
maximum absolute error 0.00488281. The rebuilt runtime hash was propagated
through the runtime package and board handoff, and the aggregate audit remains
153 checks passed with zero errors. This is simulator evidence only; board
execution and measured system cost remain blocked.

The physical-import validator now checks measurement sanity in addition to field
presence: finite and non-negative latency, energy, power, memory, and error
values; ordered timestamps; `p95 >= p50`; positive repetition counts; peak power
at least average power; and 64-character hexadecimal handoff/output hashes. A
synthetic acceptance test and invalid-measurement rejection test cover these
paths without writing or promoting measurement evidence. The real template
continues to reject with `no_measured_claim`.

The paired validator also requires digital and guarded-hybrid runs to share the
same target architecture, runtime version, shared-object identity, correctness
thresholds, workload/reference hashes, and host-overhead boundary. This keeps a
latency or energy delta from comparing unlike execution contracts; the paired
contract tests cover both acceptance and mismatch rejection.

The next learning handoff is now explicit in
`ingest_accepted_physical_policy_observation.py`. It revalidates both bundles
and accepts a supplied paired-status artifact only when it says `accepted`; it
then emits a measured-board policy observation containing provenance and latency/
energy deltas. Rejected, template, or simulator-derived inputs produce only
`no_learning_claim`, so physical data cannot silently enter the contextual
selector before the existing held-out and fallback gates are applied.

The checked-in physical and paired template status artifacts were regenerated
after these validator changes: both remain `rejected` with
`no_measured_claim`, now reflecting the current 49-field physical rejection
set and paired cross-run rejection reasons.

The physical handoff now also hashes the Android launcher and Hexagon skeleton
assets selected for the v75 board run. Package preparation records the tool
variant and both hashes; the board launcher verifies them before deployment.
This closes a runtime-environment provenance gap without changing the current
no-device gate or making a physical claim.

An earlier checkpoint compiled into a bounded four-action queue through
`generate_next_recursive_action_queue.py` and
`next-recursive-action-queue.json`. After those regulated-cascode,
mismatch-coverage, and boundary-reuse actions were executed, the current queue
contains only `same_run_physical_cost_import`: capture paired digital and
guarded-hybrid board runs with synchronized power/thermal traces. It still does
not authorize analog execution while the INL, physical-cost, and provenance
gates remain open.

The selected regulated-cascode action was made concrete in
`run_regulated_cascode_current_mode_search.py`. Unlike the earlier fixed-bias
top-cascode probe, this runner defines an explicit behavioral feedback loop per
branch and a bounded 18-point bias/gain/target population over TT/SS/FF. The
runner accepts `AIMC_SKY130_COMPAT_ROOT` and writes
`regulated-cascode-current-mode-search.json` even when prerequisites are
missing. The current checkout is blocked before simulation because the declared
temporary SKY130 compatibility bundle is absent; therefore this action produced
no new circuit measurement and cannot change the digital-fallback decision.

The local PDK was then located under the installed Ciel SKY130 tree and a
temporary NFET/PFET staging bundle was built without modifying the installed
PDK. The 18-case regulated-cascode population executed through the ngspice
runner, but all cases stopped before measurement with the same model-deck
compatibility diagnostic (`Cannot compute substitute`). The final artifact
classifies these as `model_compatibility` failures, with zero voltage samples
and no promotion. This is stronger evidence about the current toolchain
blocker, but it is not evidence for or against regulated-cascode electrical
quality; the digital-fallback gate remains unchanged.

The compatibility transform was then extended to recognize both `_slope` and
`_slope_spectre` nominal-zero terms, and the regulated runner gained the same
undefined-parameter replay used by the existing current-mode flow. The full
18-point search subsequently completed with valid TT/SS/FF measurements for
all candidates. Every candidate was monotonic and settled, but the best
candidate (bias 1.05 V, feedback gain 8, regulated target 0.20 V) reached only
3.548 LSB worst-corner INL. Since the promotion threshold is 0.5 LSB, the
regulated mutation is rejected for analog promotion. The queue now consumes
this completed result and selects fresh mismatch evaluation for the best
candidate rather than repeating the same nominal/PVT search.

The follow-on mismatch population for that candidate evaluated nine bounded
geometry/load perturbations. Seven produced valid TT/SS/FF measurements and
passed the nominal electrical checks with worst measured INL 3.560 LSB; two
(`w4_plus5` and `load_plus5`) were not executable because the installed model
cards have no valid 105um geometry bin. The corner-level diagnosis is retained
in `regulated-cascode-mismatch-failure-diagnosis.json`. The action queue now
selects model-coverage repair before any claim of mismatch robustness, making
the unsupported cases an explicit coverage gap rather than an electrical
failure claim.

The model-coverage audit records declared NFET/PFET width bounds of
0.36--100um and 0.42--100um respectively. A supported-subset summary now
closes the seven in-range mismatch trials as electrically passing (worst INL
3.560 LSB) while retaining the two 105um requests as explicitly unsupported.
The recursive queue consumes that closure and advances to same-run physical
cost import; analog authorization remains false because INL, mismatch coverage,
and physical-cost gates are still not promotion-ready.

The same-run cost handoff now includes
`assemble_physical_measurement_bundle.py`. It joins only caller-supplied
measured runtime and power/thermal exports, preserves their source paths, and
delegates to the strict synchronized import validator. A template assembly was
verified to remain rejected with `no_measured_claim`; no physical values were
created. This closes the host-side assembly gap while leaving the actual board
measurement gate correctly blocked until a connected instrumented target exists.

An audit of that import contract found that runtime/power synchronization alone
was insufficient for the end-to-end claim. The validator now also requires
runtime version and trace data, correctness/reference and device hashes with
finite/error limits, non-negative memory telemetry, and source-handoff hashes.
The assembler requires metadata carrying those correctness, memory, and handoff
fields. Revalidating the template produces 34 rejection errors and
`no_measured_claim`, confirming the stronger fail-closed boundary without
creating physical data.

The durable `END_TO_END_GOAL_REVIEW.md` was reconciled with the current state:
the learning component is identified as a contextual-bandit/policy-search pilot,
not deep RL; the regulated-cascode and boundary-reuse results are included;
and the physical board import is the remaining end-to-end gate. The assembler
was also tested with sparse exports: absent identity fields are filled only
from explicit metadata, while conflicting supplied values remain validator
errors.

While the physical import remains pending, the independent boundary-reuse
experiment was executed on the frozen six-operator transformer fixture. The
baseline full-analog model is 1,011,308.4 relative energy units versus a
786,432 digital baseline. Reuse factor 2 or greater produces a modeled
break-even, with the best swept case at 627,308.4 units. Correctness is only
inherited from the already passing fused/staged simulator reports; no new
runtime schedule or hardware energy claim was promoted. The queue consumes
this completed sensitivity experiment and now contains only the physical
measurement action.

The aggregate qualification audit then exposed and fixed two integration
issues: a null rejected candidate crashed the final audit, and the cycle
orchestrator treated an expected closed-loop-SAR-PVT gate failure as a process
failure. It now supports explicit replay-skip modes for already verified
artifacts and accepts the current 111-stage cycle manifest. The rebuilt cycle
and final audit pass all 153 checks with promotion still blocked, preserving
the four stated simulator/physical qualification blockers.

The final-package audit was extended to include the current regulated-cascode
search, its supported/unsupported mismatch accounting, model coverage audit,
boundary-reuse sensitivity, strict physical-import status, and next-action
queue. The paired-board validator now requires independently accepted digital
and guarded-hybrid bundles with matching workload/source/correctness
boundaries, distinct runtime and power windows, and distinct package
identities. A template pair is rejected with `no_measured_claim`, as required.
The aggregate audit now passes 165 checks with zero errors; this is a stronger
consistency result, not a physical promotion, because the claim-readiness
artifact still explicitly blocks board and measured-energy claims.

The RSI/RL work now has a sequential benchmark in
`run_sequential_rsi_rl_benchmark.py` and
`sequential-rsi-rl-benchmark.json`. Each held-out episode selects experiments
under a fixed budget, observes simulator outcomes, updates failure memory, and
retains digital fallback. Grid, random, contextual, sequential-RSI, and a
second adaptive pass all preserve safety on 36 held-out cases. The early-stop
RSI policy reduces candidate evaluations from 432 to 371 while preserving
36/36 safety. This is an offline model-based/RSI benchmark, not deep RL or
hardware evidence; the next research step is to test transfer on a new
workload without weakening the gates.

That transfer step is now complete for the independent Hexagon MLP numeric
sensitivity sweep. The planner trains on the noise-0.0 context and evaluates
disjoint noise-0.001 and noise-0.005 contexts. Early-stop RSI reaches both
cases with five candidate evaluations versus eight for grid, while preserving
the required fallback for the unsatisfiable high-noise case. The source sweep
has no energy model, so the transfer reports precision-complexity proxy only;
it remains offline numeric evidence, not deep RL, measured energy, hardware, or
production evidence.

The end-to-end orchestration layer is now executable in
`run_end_to_end_rsi_policy_loop.py` and records
`end-to-end-rsi-policy-loop.json`. It consumes the typed candidate ledger,
constructs explicit state/action/observation/reward records, learns action and
failure priors from even-seed corners, runs bounded sequential episodes on
three odd-seed held-out corners, and emits a runtime-package-bound decision
record. The run observes 25 candidate outcomes, preserves 3/3 held-out safety,
selects analog once, and uses digital fallback twice. Promotion is deliberately
rejected until a reproducible held-out improvement is demonstrated; rollback is
digital fallback. The final audit binds this result as check 155.

The learned-policy promotion gate is now executable in
`evaluate_rsi_promotion.py` and records `rsi-promotion-evaluation.json`. It
compares the learned loop against the bound Pareto runtime policy on the same
three held-out corners, requiring safety on every case, no modeled-cost
regression, and at least one strict improvement. The current learned loop is
safe on 3/3 cases and matches the baseline at 13,262.93 modeled units, with
zero strict improvements, so promotion is rejected and the rollback path is
baseline policy followed by digital fallback. Action deduplication reduces
the episode work to 21 unique candidate evaluations on the expanded action
population. The final audit binds the expanded 486-row/8-reliable-candidate
ledger as check 157.

Promotion additionally requires analog-coverage non-regression. This prevents
an apparently cheaper all-digital fallback policy from being mislabeled as an
AIMC improvement merely because it avoids analog execution; the current run
matches the baseline's one analog held-out case and remains unpromoted for lack
of a strict improvement.

The broader generalization run is now recorded in
`population-rsi-benchmark.json`. It trains on 36 workload/seed cases and
evaluates 36 unseen cases from the existing 72-case selector population.
Sequential RSI preserves 36/36 safety, finds 6 analog cases, and reaches the
same 134,873.6 modeled cost as the reliable oracle; random search finds 4 analog
cases and grid search finds none. This is a stronger cross-seed transfer result
but remains frozen simulator evidence, not deep-RL, hardware, or measured-cost
evidence. Failure-aware stopping reduces the sequential search from 432 grid
evaluations to 374 without changing safety, analog coverage, or modeled cost.
The benchmark also includes a contextual tabular-Q policy trained from the
training-seed state/action outcomes; it reaches the same 36/36 safety and six
analog held-out cases. The final audit binds this broader result as check 158.

The end-to-end artifact now persists an action-level performance memory rather
than only a failure count. Each observed action records attempts, safe and
failed outcomes, reward sum, safe rate, and mean reward across the training
ledger and held-out episodes. The final audit verifies that this memory is
present and structurally complete. The converter gate remains unchanged: no
analog action is authorized on a corner that fails the converter evidence.

The runtime handoff is now compiled by `compile_rsi_runtime_handoff.py` into
`rsi-runtime-policy-handoff.json`. It hashes the promotion result, baseline
Pareto policy, and validated runtime package; because learned promotion is not
approved for runtime analog execution, the active policy is explicitly the
baseline runtime policy with digital fallback. The learned experiment selector
was previously treated as approved because it reduces candidate search effort by 40% with
no safety or coverage regression. The handoff remains simulator-replayable and
board-pending, and the final audit verifies this split binding as check 159.
At this checkpoint, the learned experiment selector was treated as approved
because it reduced the candidate evidence lookup count by 40%; a later claim
audit corrected that interpretation as documented below.

`validate_rsi_runtime_handoff.py` now replays that handoff against the baseline
policy and runtime package. It verifies zero errors, six active decisions,
matching baseline/runtime hashes, explicit baseline activation, and digital
fallback. The replay passes and is bound as final audit check 160.

At the earlier 13-contract checkpoint, the requirement-level audit recorded
`end-to-end-readiness-audit.json`. It marks 11 of 13 end-to-end contracts
passed, including recursive proposal-memory transitions, compiler-schedule
handoff provenance, and the separately promoted compiler schedule with staged
rollback. It leaves exactly two honest open gates: strict runtime analog
improvement and physical-board validation. The aggregate audit binds this
distinction rather than treating a green software audit as physical completion.

`verify_rsi_reproducibility.py` now replays the end-to-end loop, 36-case
population benchmark, runtime promotion gate, and compiler-schedule promotion
twice. All four artifacts are byte-identical across replays, providing
deterministic evidence for the promotion decisions; the final audit binds this
replay contract.

The promotion evidence now separates runtime cost from experiment cost. On the
three matched held-out transformer corners, RSI reaches the same safe runtime
decisions and modeled energy as baseline while reducing unique candidate
offline evidence lookups from 35 exhaustive checks to 21, a 40% lookup reduction;
this does not demonstrate fewer simulator invocations.
That is a real offline evidence-filtering result, but not a simulator-call
efficiency improvement; the experiment selector is not approved until matched
executed-call telemetry supports the claim. Runtime-policy promotion also
remains open.

The final manifest now records SHA-256 hashes for the external RSI promotion
gate, runtime handoff, handoff replay, readiness audit, reproducibility record,
fresh proposal episode, and derived memory update. This makes the active
baseline/learned-selector split and proposal evidence cryptographically bound
to the package manifest; the new proposal checks are 164 and 165.

The recursive action queue now consumes the readiness audit and retains two
ordered actions: synchronized physical cost import remains first because no
board is connected, while `strict_runtime_analog_improvement` is explicitly
queued as the next simulator-side promotion action. Analog authorization stays
false until either action's acceptance contract is satisfied.

The end-to-end learner has now been tightened from an action-average heuristic
to an explicit deterministic tabular-Q experiment. It uses contextual states
(`model_section`, temperature, converter-gate result), terminal simulator
rewards, a serialized update count/state-action count, failure memory, and a
zero-exploration held-out evaluation policy. The replay remains reproducible
and the promotion result is unchanged: search efficiency is approved, runtime
analog improvement is not. This is a real bounded model-based RL/RSI loop, not
deep RL. The proposal bridge now consumes that Q memory, emits four fresh
mutations, and the derived ledger records explicit state/action/outcome/reward
transitions plus persistent memory updates and independent transfer results.

The policy loop now applies an explicit Wilson lower-confidence risk gate to
every repeated simulator action. Analog selection requires both the converter
gate and a lower bound of at least `0.25`; otherwise the episode selects the
digital fallback. The current 3/3 held-out safety and one analog decision are
unchanged, but the safety invariant is now present in every trace and verified
by the final manifest audit.

The same confidence gate is now applied to the broader 72-case population
benchmark. All methods retain 36/36 safe held-out decisions; tabular-Q retains
six analog selections, and every trace records its repeated-trial confidence
bound at the same `0.25` threshold. Cross-corner generalization is therefore
subject to the same safety invariant as the end-to-end workload loop.

The compiler schedule action `fused_stack_hoisted_transformer_block` is now
qualified from two independent v75 simulator reports. Both fused and staged
pipelines pass their output-tolerance contracts; the fused stack-hoisted
schedule reduces simulator pcycles by 36.2% relative to the staged boundary
pipeline. It is admitted only to simulator schedule search, with the staged
pipeline as fallback. It is not measured energy, board performance, or analog
runtime evidence. The tabular-Q end-to-end loop now carries this schedule in
its action state and emits the staged schedule on digital fallback. The final
manifest binds this action as audit check 166.

The runtime handoff now carries the schedule qualification digest, selected
`fused_stack_hoisted_transformer_block` schedule, and explicit
`staged_boundary_pipeline` fallback. Handoff replay verifies all three against
the qualification artifact before declaring the simulator-replayable package
board-ready. The active runtime policy remains the baseline policy until the
analog promotion gate passes.

The fused compiler schedule now has a separate promotion artifact,
`compiler-schedule-promotion.json`. It is approved for simulator-runtime use
because both fused and staged outputs pass tolerance and fused execution uses
36.2% fewer simulator pcycles; rollback is the staged boundary pipeline. This
promotion is deliberately scoped away from analog runtime, measured energy,
and board performance. It is bound as final audit check 168.

The wider precision/gain rescue search then evaluated `1,260` repeated
single-operator simulator trials across 6--12 bits and 0.90--1.10 gain trims.
Only `11` trials were reliable, all on the same one PVT corner; the best safe
candidate remained the existing 12-bit q action at `7,118.93` modeled units.
No lower-cost held-out analog action was found, so the strict runtime analog
promotion gate remains correctly closed. This negative result is now bound as
audit check 167 rather than being treated as an informal conclusion.

Following the mutation probe, the regulated-feedback topology search expanded
to 36 bias/gain/target combinations. All 36 passed monotonicity and settling;
the best maximum INL improved to `3.4888` LSB from the prior `3.5479` LSB, but
remains above the `0.5`-LSB promotion threshold. The candidate is therefore
recorded as a reproducible simulator improvement with promotion rejected, and
is bound by the final audit as check 169.

`build_objective_evidence_matrix.py` now emits
`objective-evidence-matrix.json`, mapping all nine requirements in the stated
objective to authoritative artifacts. All nine are evidenced as passed; the
matrix separately records the two downstream gates—physical validation and
strict analog runtime improvement—as open rather than converting missing
evidence into a claim. The matrix is manifest-bound as audit check 170.

The proposal generator now consumes the prior `derived-ledger-transfer.json`
memory layer on the next generation. Its current context contains 12 original
Q-loop entries plus 4 prior proposal updates, and the prior ledger digest is
recorded in `new-trial-proposals.json`. This makes recursive proposal memory
persistent across episodes while preserving the immutable parent ledger and
the same fail-closed selection rule.

## Reuse-aware RSI continuation checkpoint

`run_reuse_aware_rsi_benchmark.py` now treats converter-boundary reuse as an
explicit tabular-Q action dimension. It evaluates reuse factors 1/2/3/6 over
the expanded candidate ledger, trains on even-seed corners, evaluates odd-seed
corners, and applies the Wilson confidence gate plus digital fallback. The run
records 36 training updates and 3/3 safe held-out decisions, but finds zero
strict modeled runtime wins, so runtime promotion remains rejected. It also
records that the structural full-MAC cost model is not comparable with the
normalized candidate-ledger units, preventing a false cost improvement from
entering policy. Reuse remains a hypothesis requiring an executable schedule
and same-run board measurements, not hardware evidence.

The supported-model regulated geometry search then evaluated 12 combinations of
branch widths and PMOS load around the best feedback point. All 12 candidates
were monotonic and settled across TT/SS/FF; the best maximum INL was 3.3768 LSB
with a 50u load. This is worse than the 2.9192-LSB input-drive result and far
above the 0.5-LSB gate, so geometry-only linearization is rejected and the
next circuit mutation must change the summing/feedback architecture.

The per-branch feedback-trim experiment varied three regulated drain targets
over 27 tuples while holding the best prior geometry, bias, and loop gain
fixed. All 27 candidates passed TT/SS/FF monotonicity and settling; the best
maximum INL was 3.3886 LSB at targets (0.10, 0.15, 0.15) V. Branch-specific
target trimming therefore does not cross the 0.5-LSB gate, and the regulated
feedback family remains rejected for analog promotion.

The architecture-level mutation was tested with a segmented unit-current DAC:
seven identical switched/cascode branches replace the binary-weighted branch
set. Six supported-model candidates were evaluated across TT/SS/FF; all passed
monotonicity and settling, but the best maximum INL was 4.3826 LSB. The
segmented topology is therefore rejected for the 0.5-LSB gate, and its exact
parameter-injection compatibility path is retained as failure evidence.

The differential current-steering architecture is now the leading circuit
candidate. Fifteen matched complementary-output candidates passed TT/SS/FF
monotonicity and settling; the best maximum INL reached 1.0189 LSB, materially
below the prior 2.94-LSB single-ended current-mode result but still above the
0.5-LSB gate. A follow-on 14-point differential coarse-MSB plus three unary
fine-residue search stayed electrically valid but reached only 1.1070 LSB.
The differential family remains unpromoted and now needs a calibrated
correction branch or another explicit linearization mechanism.

The differential residue-correction experiment added one-hot decoded
transistor branches for the measured antisymmetric code residual. A uniform
correction width improved max INL to 1.0063 LSB; a 12-point three-amplitude
sweep improved it further to 0.9955 LSB, with all candidates passing
monotonicity and settling across TT/SS/FF. This is reproducible correction
evidence, but it remains above the 0.5-LSB gate and is not promoted; decoder
overhead and physical validation remain open.

Targeted correction-amplitude refinement raised the large-residue branch to
the supported 100u model limit. The best three-amplitude tuple (100u, 2u,
12u) reached 0.9338 LSB max INL across TT/SS/FF, with all five tested
candidates electrically valid. This improves on 0.9955 LSB but still fails the
0.5-LSB gate; a second-finger or alternate correction-device topology is
required before promotion can be considered.

Parallel correction fingers were then tested while keeping each device within
the supported 100u model bound. Two large-residue fingers reduced max INL to
0.9074 LSB and three fingers reduced it to 0.8946 LSB; all six candidates
passed TT/SS/FF monotonicity and settling. The correction architecture is
continuing to improve reproducibly, but remains above the 0.5-LSB gate and is
not authorized for runtime use.

The leading 8-finger correction candidate passed a nine-trial bounded
geometry/load stress population: all nominal and +/-5% branch/load variants
passed TT/SS/FF monotonicity and settling, with worst max INL 0.8849 LSB. A
separate relative-cost accounting artifact counts 20 matched correction
devices plus six decoder outputs and rejects promotion; the coefficients are
declared proxies, not measured energy. This closes the current simulator
robustness check while leaving the 0.5-LSB, workload-transfer, and physical
measurement gates open.

Extending the large-residue correction finger count to 8 reduced max INL to
0.8738 LSB across TT/SS/FF; all seven tested finger configurations passed
monotonicity and settling. Improvement is flattening while decoder/device
overhead grows, so this is the current simulator candidate but remains below
the 0.5-LSB gate and is not runtime-authorized. The next gate is robustness
and declared-cost accounting for the correction network.

`compile_differential_correction_policy.py` now binds the leading correction
candidate into an explicit RSI transition and failure-memory update. Its PVT
and bounded robustness gates pass, while strict INL, measured cost, and
held-out workload-transfer gates remain false. The handoff records a negative
reward and preserves the baseline runtime policy with digital fallback, so the
candidate cannot sit outside the recursive learner or bypass promotion.

The correction candidate was then evaluated against all 72 held-out workload,
PVT, and seed cases. Because strict INL remains false, all 72 selected the
verified digital fallback and all 72 inherited digital correctness. The policy
handoff now records held-out fallback transfer as passed while keeping analog
runtime promotion rejected; this closes the workload-safety gate without
confusing fallback transfer with analog improvement.

An alternate complementary PMOS pull-up correction was screened as a distinct
mutation. Six PMOS variants failed the electrical promotion contract and
produced roughly 1.76--1.80 LSB INL, so the NMOS correction remains the leading
topology. The policy handoff records the selected correction device explicitly
and retains the PMOS branch as rejected mutation evidence.

The RSI reproducibility verifier now includes the differential correction
policy handoff. Five simulator/software artifacts replay byte-identically over
two runs, including the correction candidate's negative reward,
failure-memory update, and fallback selection. The mutation is now part of
the deterministic learning audit rather than an untracked side experiment.

The final-package audit was extended to require those five reproducibility
replays, including the differential correction handoff. The package audit
passes 170/170 again, making the new RSI evidence part of the authoritative
qualification checks rather than only an external report.

The hardware-to-RSI boundary is now executable in
`update_physical_rsi_policy.py`. It accepts only an accepted paired measured-
board observation, verifies finite latency/energy metrics and zero correctness
mismatch, computes an auditable contextual reward, and records a state/action
update proposal. Rejected, template, simulator, or incomplete observations
produce no reward and no update. The current template import was exercised
through this boundary and correctly remained `no_learning_claim`; the new
contract suite passes 5/5. This is the missing software-side handoff for the
future board session, not physical evidence or runtime-policy authorization.

The boundary replay is now included in the authoritative RSI reproducibility
set as `physical_rsi_learning_boundary`: six artifacts replay byte-identically
and the current rejected no-board state remains ineligible for learning. The
final package audit continues to pass 170/170. The next state transition that
cannot be completed in software is still the synchronized digital/hybrid
measurement session on a connected Android/Hexagon v75 target.

The correction search then expanded to a 13-candidate population, adding
12/16-finger NMOS branches and focused correction-amplitude variants around
the leading candidate. The 16-finger `(100u, 2u, 12u)` branch remains best at
0.8661 LSB; the added width variants did not improve it. All nine robustness
trials pass with worst INL 0.8776 LSB, while the relative correction-overhead
proxy rises to 71. Held-out transfer remains 72/72 fallback-correct, but the
strict 0.5-LSB and measured-cost gates remain closed, so the baseline policy
and digital fallback remain active.

A distinct seven-branch differential thermometer/current-steering topology was
then evaluated across 18 unit-width/load combinations and TT/SS/FF. All 18
were electrically valid, but the best result was 1.6368 LSB INL, materially
worse than the 0.8661-LSB decoded-correction branch. The topology is recorded
as rejected mutation evidence in `differential-thermometer-search.json` and
the recursive action queue; it is not promoted or treated as a hardware claim.

A second independent linearization family, matched source-degenerated
differential binary current steering, was evaluated across 12 resistor/load
cases. Only the 100-ohm cases remained electrically valid; the best was 1.4043
LSB INL and the larger degeneration values became non-monotonic. This family
is also rejected in `differential-source-degenerated-search.json`; the
baseline runtime policy and digital fallback remain unchanged.

The accepted-board observation path now feeds an explicit contextual
Q-memory learner in `learn_physical_rsi_policy.py`. It admits only updates
that passed the paired measured-board and correctness gates, records state,
action, reward, and provenance, and still emits a non-authorizing policy
candidate requiring held-out transfer and fallback gates. The current
no-board replay produces zero accepted updates and zero state-action entries;
this learner boundary is now included in the deterministic RSI replay set.

Finally, `evaluate_physical_rsi_promotion.py` now enforces the physical RL
promotion boundary: correctness safety, multiple workload contexts, and a
strict positive held-out reward are required before a measured candidate is
even eligible for the existing runtime gate. The current no-board replay is
rejected with no runtime authorization, and digital fallback remains the only
active policy.

The runtime and structural cost proxies were also audited for unit
consistency. Their digital normalization scales are 256x and 32.14x
respectively, an 87.4% relative mismatch. `runtime-cost-model-consistency.json`
therefore blocks cost-based promotion until a common calibration unit or
same-run measured energy is available; structural break-even sensitivity
cannot be used as runtime proof.

The physical handoff also now has an explicit paired-package contract via
`build_paired_board_package_manifest.py` and
`validate_paired_board_packages.py`. It requires distinct digital and hybrid
runtime hashes while requiring identical input/reference hashes. The current
single prepared package correctly fails this self-comparison check, preventing
an accidental one-package “paired” measurement claim.

The end-to-end readiness matrix now includes this reconciliation as an
explicit fourteenth requirement. It reports 11 passed and three open gates:
physical board validation, strict runtime analog improvement, and cost-model
consistency. The final package audit was updated to require this stricter
matrix and still passes 170/170.

## Executed-search evidence wired into promotion audit (2026-09-22)

The RSI promotion evaluator previously read simulator-call counts only from
the older end-to-end policy-loop artifact. That artifact is an offline replay
and has zero direct simulator calls, so the executed three-round learned vs.
heuristic converter search was not represented in the promotion report even
though it had its own invocation ledgers. The evaluator now consumes the
three-round benchmark, verifies each round report against its recorded
SHA-256, checks distinct seeds and matched candidate budgets, and records the
learned and heuristic invocation totals as direct search-efficiency evidence.

The verified seeds are 41, 73, and 109. Learned and heuristic each used 288
ngspice invocations and each produced zero candidates under the strict 0.5-LSB
promotion gate. Their mean safe INL values were 3.5387 and 3.5722 LSB,
respectively; because later adaptive rounds ingest shared prior outcome
memory, this is descriptive evidence only. Equal simulator-call counts mean
there is no strict search-efficiency improvement, so the learned experiment
selector remains rejected. The runtime handoff was regenerated and validated
with the baseline experiment selector and baseline runtime policy still
active, with digital fallback retained. The end-to-end audit remains open on
experiment-policy promotion, physical board evidence, strict runtime analog
improvement, and cost-model consistency. The focused promotion tests pass
`6/6`; no board, silicon, energy, or runtime improvement claim is made.

The board validator now persists the exact package-gate result it reports;
this corrected a stale `device/claim-readiness.json` shared-object hash. The
live and persisted package hashes now match, and the board-gate test passes.
The staged ABI pipeline was initially checked separately as diagnostic object
evidence; it was not yet a second deployable all-digital package.

The staged ABI boundary was then repaired to normalize its public descriptor to
the frozen `[1, 1, 256]` last-token contract. A fresh v75 simulator build now
passes the strict harness with zero tolerance failures and maximum absolute
error `0.00292969`. `device/prepare_guarded_staged_board_package.sh` packages
that independently linked runtime and hash-binds all stage objects and wrapper
sources in a side-specific handoff. The fused baseline plus this guarded
staged/digital package now pass the paired package manifest and validation
contract with distinct shared-object hashes and identical input/reference
hashes. This closes package construction/integrity only; the staged path is
not analog evidence, and the physical board and measured-improvement gates
remain open.

The physical handoff now also has a fail-closed paired-session coordinator in
`run_paired_board_session.py`. Board validation accepts a package-specific
handoff through `HEXAGON_TRANSFORMER_HANDOFF`, and the coordinator verifies the
paired manifest, both side-specific handoffs, and the selected target before
running either package. It records raw digital and hybrid runtime logs but
does not synthesize power/thermal measurements or admit learning data. Its
no-board integration test passes and the current self-comparison remains
rejected, so this improves execution readiness without changing the open
physical-board or promotion gates.

The recursive queue then consumed a fresh 24-point regulated-cascode
load/geometry mutation population. Twenty candidates passed their declared
TT/SS/FF electrical and settling checks and four were simulator-blocked; the
best maximum INL was `3.9862 LSB`, worse than the prior `3.3768 LSB` point and
far outside the `0.5 LSB` promotion gate. The full per-corner results are in
`regulated-cascode-load-mutation-search.json`, and the queue records the
mutation as non-improving instead of scheduling it again. The runtime policy
therefore remains digital fallback.

That converter action space is now connected to its own failure-aware memory
via `build_converter_mutation_failure_memory.py`. It ingests the expanded,
geometry, and new load-mutation artifacts without conflating them with the
workload-placement Q table. The current memory contains 72 retained mutation
outcomes across 71 unique action signatures; all 72 are rejected by the
declared `0.5 LSB` converter gate, so future proposal generation can avoid
repeating them. This is recursive proposal memory, not analog authorization.

A 12-point cross-product then combined the leading differential current-steering
base geometries with the decoded residue-correction branch. All 12 candidates
passed the simulator and settling checks, but the best maximum INL remained
`0.8660910632673219 LSB`, exactly matching the prior differential point; no
strict improvement was found and the `0.5 LSB` promotion gate remains open.
The replayable population and full per-corner evidence are in
`run_differential_correction_base_mutation_search.py` and
`differential-correction-base-mutation-search.json`. This rejected mutation
family is now included in the converter failure memory and is proposal memory,
not analog authorization.

The paired-board coordinator was re-run against the accepted fused-digital and
guarded-staged package pair. Package and handoff hashes validate, and the
coordinator fails closed solely because no `ANDROID_SERIAL`/connected v75
board is present; the exact result is retained in
`paired-board-session-latest.json`. No runtime, energy, thermal, or learning
observation was synthesized from this preflight.

The offline RSI/RL evidence was also replayed: the tabular end-to-end loop
preserves safety on all three held-out contexts while reducing candidate
evaluation from 35 to 21, and the sequential failure-aware benchmark preserves
36/36 held-out safety. These remain simulator/model-based policy experiments;
the physical policy memory has zero accepted updates until paired measured
board observations arrive.

A 27-point per-branch feedback-target population was evaluated on the leading
regulated-cascode geometry. Every candidate passed the electrical and settling
checks, but the best maximum INL was `3.3886031966122023 LSB`, so independent
LSB/middle/MSB target trims do not close the analog promotion gap. The full
population is retained in `per-branch-feedback-trim-search.json`, added to the
converter failure memory, and included in deterministic replay. The runtime
policy remains digital fallback.

The broader physical handoff gate then advanced independently: the Sky130
hierarchical transformed-landing build at
`analog-digital-chip-design-eda/evidence/aimc-simulator-adapters/hierarchical-driver-receiver-handoff/20260921T184209038132Z`
passes DRC with zero errors, extracts 12 merge records with a connected
differential handoff and no forbidden shorts, and passes unique hierarchical
Netgen LVS. Its extracted TT nominal transient measured a `2.0253047 V`
output differential for a `100 mV` input differential. This is a real physical
composition checkpoint, not board or silicon evidence; the four-cycle,
16-code SAR, PVT-population, board, and runtime gates remain open.

## Search-efficiency claim correction (2026-09-22)

A claim audit found that the end-to-end policy loop's `21` versus `35` count
measures accesses to candidate outcomes already present in the expanded
ledger. The loop launches no simulator trials (`simulator_calls: 0`), so this
is a 40% reduction in offline ledger evidence lookups, not demonstrated
simulator-call savings. The report schema now names that measure accurately
and includes its execution mode. `evaluate_rsi_promotion.py` requires matched,
positive baseline simulator-call telemetry from an executed search before it
can approve experiment-policy efficiency; the current learned selector is
therefore rejected for promotion and the runtime handoff selects the baseline
experiment selector. Readiness and package audits now encode this open gate
instead of treating the offline lookup reduction as simulator efficiency.

The initial three regression tests distinguished offline lookup reduction
from actual matched simulator-call reduction. The matched executable search
milestone has since been run on three adaptive seeds; direct invocation-ledger
verification and the current promotion decision are documented below. The
offline evidence lookup result remains useful as a bounded policy-replay
result, but is not a search-cost promotion claim.

The simulator-side experiment milestone now has an executable harness in
`run_executed_converter_search_benchmark.py`. It compares learned KNN ranking,
a fixed engineering heuristic, and seeded random selection over the same
budget from a repeatable seeded converter-action pool. Each round verifies its
pool is disjoint from both historical training reports and any supplied prior
round. One or more completed `--prior-benchmark` reports can be hash-bound into
the next round's training memory; recursive runs must supply every earlier
round in lineage order to avoid forgetting non-adjacent outcomes. Parent hashes
must resolve to earlier supplied reports; incomplete/out-of-order lineages and
duplicate report paths or content are rejected so outcomes cannot be silently
omitted or overweighted. Replaying a prior action as new validation input is
rejected. The `--seeds` mode runs multiple such rounds as one experiment,
passing the full parent chain each time and writing per-round artifacts,
interruption progress, and a descriptive aggregate of measured calls and safe
INL outcomes.
Each candidate's actual ngspice subprocess
invocations—including undefined-parameter retries—are counted by the
regulated-cascode runner. Each method receives the same maximum invocation
budget, derived from three PVT corners, eight codes, and sixteen compatibility
attempts per code. The result is explicitly exploratory and cannot promote a
runtime policy. Recursive parent reports are rejected if their converter-runner
or ngspice/model provenance differs from the current evaluator. Each round also
records a hash of the benchmark harness so changes in the search logic are
visible across recursive rounds. Selected actions are labeled against frozen
pre-round coordinate bounds, and both single-round and recursive summaries
separate safe outcomes inside versus outside those ranges. Twelve tests cover training/validation disjointness, learned
ranking, failure-memory handling, prior-round ingestion and replay rejection,
matched-budget accounting, exact normal/retry subprocess counts, and partial
round interruption accounting.
The harness hashes its own search logic, the exact converter runner, the
ngspice executable, and 12 PDK corner/model files,
retains per-corner/code measurements in its trial ledger, and flushes a
subprocess-call ledger plus atomic progress state so interrupted runs cannot be
mistaken for completed rounds. The tool/model and seeded-pool preflight was
read-only; the subsequent real-ngspice benchmark is recorded below. Its
equal-budget call counts establish a measured comparison, but show no simulator
call-efficiency reduction by the learned method. The recursive-memory path is
tested with three simulated rounds:
the third round ingests both earlier reports, verifies their hashes, rejects a
missing ancestor, and rejects validation-pool actions seen in either ancestor
report. The multi-seed coordinator is exercised with a fake simulator to check
fresh-seed execution, cumulative training counts, call aggregation, and its
completed progress/final artifacts; it does not count as ngspice evidence.
Before a recursive experiment creates its output directory or spends simulator
calls, the coordinator now validates the complete supplied parent chain against
the current runner/model hashes, checks every seed pool against historical and
parent actions, and checks pairwise pool disjointness. A regression test injects
a later-round pool collision and confirms rejection occurs before any
experiment output is created, avoiding an expensive partial campaign for a
known validation defect.

As a no-simulator preflight for that run, the current KNN ranker was checked
against the 54 historical measured converter candidates using leave-one-action-
out validation (the two identical parameter tuples were held out together).
Across these 54 rows, KNN predicted max INL with `0.0649 LSB` MAE and `0.1097
LSB` RMSE, versus `0.1190 LSB` MAE and `0.1609 LSB` RMSE for the training-set
mean. This is evidence of historical interpolation signal only: every
historical candidate passed monotonicity/settling, so it does not validate the
ranker's safety estimate. More importantly, historical max INL spans
`3.4888–4.2475 LSB`, far above the `0.5 LSB` promotion gate. The executed
benchmark therefore measured whether the ranker selects lower-INL candidates
than matched heuristic and random baselines. It produced a descriptive
learned-method advantage over the heuristic in all three adaptive rounds and
over random in two of three, but all measured INL values remain far above the
gate. Policy promotion remains out of scope unless a future search closes that
physical quality gap and passes independent held-out validation.

A stricter leave-one-campaign-out check exposed asymmetric transfer. Training
on the 18-row original report and testing on the 35 non-overlapping expanded-
campaign actions gave KNN MAE/RMSE `0.0680/0.0857 LSB`, better than a training-
mean baseline (`0.1944/0.2087`). Reversing the split (36 expanded rows to 17
original actions) gave KNN `0.2541/0.3239`, worse than the mean baseline
(`0.2159/0.2868`). This indicates the predictor's apparent pooled
leave-one-action-out signal does not establish robust transfer across search
campaigns; the fresh-seed measured comparison must be treated as exploratory,
and any future learner change should be judged on separate action pools rather
than these reused historical outcomes.

The three-round, equal-budget recursive experiment was executed with seeds
`41`, `73`, and `109`, using two candidate evaluations per method per round. All
three 12-action pools were checked to be disjoint
from the 54 historical measurements and from one another; their SHA-256 hashes
are `64cc9430e6d8a3fc727633a22bfa8a333048754f781bdedb22869c999733caa3`,
`30abc6f725840000ba6e2ae90bdf6e62d64115516e151c8be8571392229d546a`, and
`23028d1fdeec4f5d49c61726583b51fd883866a56a0431dd082294042969e199`.
Respectively, 1, 3, and 5 actions per pool exceed the historical target-voltage
maximum of `0.25 V`; benchmark trial records now explicitly mark which selected
actions cross a training-coordinate bound and aggregate outcomes by that flag.
The current ngspice-plus-model provenance hash is
`86b04c4632506a4559f5ae001eedcdb638d93a84eedfa317280e91c82ba7bb78` across
13 source files. The planned budget requires at least 432 invocations (one per
corner/code) if no compatibility retries occur, with a hard ceiling of 6,912
including all declared retries. Historical search artifacts lack per-candidate
invocation telemetry; the executed experiment's call ledgers now provide the
first direct ngspice invocation counts for this comparison. The completed
results are recorded below.

The recursive experiment aggregate now adds ordered round-level comparisons of
learned search against both baselines. Each round is scored lexicographically:
more safe candidate evaluations first, then lower mean INL among safe trials;
ties and seeds with no safe outcomes are reported explicitly. The aggregate
reports descriptive wins/ties only and deliberately emits no inferential
p-value: later rounds ingest earlier outcomes, so the round comparisons are
dependent rather than independent replicates. Regression coverage verifies
safety-first ranking, ties, and that the report marks inference as invalid for
this adaptive design. This pilot remains exploratory; a significance claim
would require multiple independent adaptive trajectories.

## Archived in-flight timeout snapshots (superseded by final results below)

The following entries preserve observations made while the campaigns were
active; they are not the final result. See the completed retry section below.

While the canonical validation is still running (PID `186510`), 15 per-case
outputs have `timed_out=true`: official-test indices
`264, 266, 268, 270, 271, 277, 278, 280, 284, 286, 290, 294, 296, 297,
304`. All 15 indices have successful rows for the alias action in the completed
alias report, and none overlaps the alias report's 24 timeout indices. This
suggests the observed timeout pattern is action-specific rather than caused
solely by those inputs; it remains provisional until the canonical aggregate
is complete and both action-specific timeout sets are retried.

At `2026-09-22T10:10:45Z`, the canonical run had written 475 case outputs:
460 passed and the same 15 remained open with timeouts. All 15 timeout indices
were present as successes in the alias report, with zero overlap against its
24 timeout indices. The canonical aggregate was still absent and two ngspice
workers were live, so this remains an in-flight diagnostic, not final evidence.

At `2026-09-22T10:15:55Z`, the run had 521 outputs (506 passed, 15 timed out)
and remained live. A sampled timeout log (case 264) ended after the operating-
point branch summary at 267 lines; a neighboring passed log (case 263) continued
through the transient at 428 lines. Both showed similar gmin/source-stepping
warnings, so those warnings alone do not distinguish timeout from success.
This supports retrying timeout cases with a longer limit, but does not prove
they will eventually pass or converge.

## Executed SAR timeout retries and recursive-search handoff (2026-09-22)

The canonical first-pass campaign completed with `1,187` successes and `15`
simulator timeouts among `1,202` sampled rows. Its timeout-only retry recovered
all `15/15` at the longer limit. The alias first-pass campaign completed with
`1,179` successes and `24` timeouts among all `1,203` expected official-test
indices; its timeout-only retry recovered all `24/24`. Both retry aggregates
report `selection_mode=timeout_retry`, preserve the exact source-report path,
and contain only successful retry rows. The alias campaign manifest's stale
`running` marker was reconciled to `completed` only after confirming the final
report, 1,203 unique indices, matching action-mask hash, and no active
simulator workers. These are simulator-backed conversion results, not silicon
measurements or runtime qualification.

The following commands are retained to make those retries reproducible. The
source reports are authoritative for exact timeout selection:

```bash
python3 analog-digital-chip-design-eda/scripts/run_sar_official_test_physical_validation.py \
  --driven-run analog-digital-chip-design-eda/evidence/driven-analog-task/20260907T203543924563Z \
  --optdigits-run analog-in-memory-ai-inference/software-architecture/experiments/optdigits-v1/runs/20260906T195750363771Z \
  --action-mask analog-digital-chip-design-eda/evidence/aimc-simulator-adapters/sar-agent/tile40-24-to-optdigits-policy-bridge-v1/safety-gated-candidate-diagnostic-v1/rl-learned-canonical-middle-prephysical-diagnostic-v1/action_mask.json \
  --corner ss --samples-per-cell 1202 --sample-offset 0 --tile tile40_24 \
  --retry-timeouts-from analog-digital-chip-design-eda/evidence/aimc-simulator-adapters/sar-agent/tile40-24-to-optdigits-policy-bridge-v1/safety-gated-candidate-diagnostic-v1/rl-learned-canonical-middle-prephysical-diagnostic-v1/official-test-middle-canonical-rest-tile40_24-v1/official_test_physical_validation.json \
  --workers 4 --timeout-s 360 \
  --out-root analog-digital-chip-design-eda/evidence/aimc-simulator-adapters/sar-agent/tile40-24-to-optdigits-policy-bridge-v1/safety-gated-candidate-diagnostic-v1/rl-learned-canonical-middle-prephysical-diagnostic-v1/official-test-middle-canonical-timeout-retries-tile40_24-v1
```

The alias timeout-only retry used its own output directory:

```bash
python3 analog-digital-chip-design-eda/scripts/run_sar_official_test_physical_validation.py \
  --driven-run analog-digital-chip-design-eda/evidence/driven-analog-task/20260907T203543924563Z \
  --optdigits-run analog-in-memory-ai-inference/software-architecture/experiments/optdigits-v1/runs/20260906T195750363771Z \
  --action-mask analog-digital-chip-design-eda/evidence/aimc-simulator-adapters/sar-agent/tile40-24-to-optdigits-policy-bridge-v1/safety-gated-candidate-diagnostic-v1/official-test-middle-alias-tile40_24-v1/middle-action-alias-mask.json \
  --corner ss --samples-per-cell 24 --sample-offset 0 --tile tile40_24 \
  --retry-timeouts-from analog-digital-chip-design-eda/evidence/aimc-simulator-adapters/sar-agent/tile40-24-to-optdigits-policy-bridge-v1/safety-gated-candidate-diagnostic-v1/official-test-middle-alias-tile40_24-v1/official_test_physical_validation.json \
  --workers 4 --timeout-s 360 \
  --out-root analog-digital-chip-design-eda/evidence/aimc-simulator-adapters/sar-agent/tile40-24-to-optdigits-policy-bridge-v1/safety-gated-candidate-diagnostic-v1/official-test-middle-alias-tile40_24-retry-timeouts-v1
```

Retry reports now identify `selection_mode=timeout_retry`, record each source
report path, and set `samples_per_cell`/`sample_offset` to null because these
options do not select retry rows. `per_cell_counts` and `sample_count` report
the actual retry population.

After verifying that retry report and confirming that no simulator workers
remained, the three-seed adaptive recursive search was executed with distinct
candidate pools and sequentially accumulated outcome memory:

```bash
python3 recursive-self-improvement-eda-research/run_executed_converter_search_benchmark.py \
  --out-root analog-digital-chip-design-eda/evidence/aimc-simulator-adapters/recursive-converter-search-v1/three-round-seed41-73-109 \
  --candidate-budget 2 --seeds 41 73 109
```

The completed evidence is in
`analog-digital-chip-design-eda/evidence/aimc-simulator-adapters/recursive-converter-search-v1/three-round-seed41-73-109/recursive_search_experiment.json`,
with one hash-bound report and separate trial/invocation ledgers per round.
Seeds `41`, `73`, and `109` each evaluated two candidates per method; each
method has `6/6` safe candidates and `288` observed ngspice invocations across
the three rounds (`864` total). Training memory increased from `54` rows to
`60` and `66`, with round 2 ingesting round 1 and round 3 ingesting both prior
reports by SHA-256. All 12-action pools reproduce from their seeds, are
pairwise disjoint, and each report verifies its pool is disjoint from its
training evidence.

The mean of the three round-level safe mean-INL values is `3.5387 LSB` for the
learned method, `3.5722 LSB` for the heuristic, and `3.5640 LSB` for random.
The paired safety-first/descriptive comparison selects learned over heuristic
in `3/3` rounds and learned over random in `2/3`; these adaptive rounds share
history, so the report correctly provides no inferential p-value. No candidate
passes the strict `0.5 LSB` promotion gate (`0/18` promotion-gate runs), so the
runtime policy remains unchanged and digital fallback remains the qualified
behavior. This is an exploratory recursive search result—not silicon,
board-cost, production, or analog-runtime qualification. The focused tests
passed `16/16` for the recursive benchmark and SAR timeout-retry selection.

## Cascode-isolated differential correction screening (2026-09-22)

To reduce correction-current sensitivity to output voltage, the leading
differential DAC was extended with an NMOS cascode above its one-hot NMOS
correction device. A bounded 15-point sweep covered cascode widths `2u`, `5u`,
and `10u` and local-rail bias fractions `0.55` through `0.95`, evaluated at
TT/SS/FF over all eight codes. All 15 candidates passed monotonicity and 10 mV
settling. The best was `1.004769 LSB` at `10u` and bias fraction `0.95`, with
per-corner INL `0.720002/1.004769/0.620072 LSB` (TT/SS/FF). This is worse than
the direct-correction baseline at `0.866091 LSB`, and remains above the strict
`0.5 LSB` gate. The exact result and a companion SHA-256 provenance record for
the runner, ngspice binary/version, and 12 TT/SS/FF model files are retained in
`differential-cascode-correction-search.json` and
`differential-cascode-correction-provenance.json`. The 15 outcomes are now in
the recursive mutation memory (`143/143` recorded mutations rejected); no
runtime or physical authorization changed. This first cascode result is limited
to an undersized implementation: its 2--10u cascode was placed in series with
the 100u x 16-finger correction branch. It rejects those geometries, not the
cascode family. The matched per-finger follow-up below is the fairer comparison.

## Matched cascode and passive feedback follow-up (2026-09-22)

The correction network was re-evaluated with all six complementary one-hot
branches present and one cascode device per correction finger, matching width
and finger count. Four fixed-bias controls and 12 resistor-feedback variants
were screened at TT/SS/FF. All 16 passed monotonicity and 10 mV settling. The
best was the matched fixed-bias cascode at a 1.0 VDD gate bias: `0.773049 LSB`
max INL, with `0.396285/0.773049/0.579539 LSB` at TT/SS/FF. This beats the
direct-correction `0.866091 LSB` control, but still misses the strict
`0.5 LSB` requirement.

The best passive resistor-feedback candidate reached `0.828162 LSB` at 0.65
VDD bias and 10 MOhm feedback resistance, with `0.739336/0.506860/0.828162`
LSB across TT/SS/FF. It substantially reduced SS error but shifted the worst
error to FF and did not beat the matched fixed-bias candidate. No candidate
meets the promotion gate; the evidence is descriptive transistor-level
simulation with ideal bias references and modeled decode only. Its report is
hash-bound to the ngspice binary and 12 model files in
`differential-feedback-correction-provenance.json`. The full population is
entered in recursive failure memory (`159/159` actions rejected); runtime
policy remains unchanged.

## Group-specific matched-cascode bias search (2026-09-22)

A 20-candidate sweep varied cascode gate bias independently for the three
complementary code-pair groups, including coordinate and pairwise settings.
All 20 candidates passed TT/SS/FF monotonicity and 10 mV settling, but none
beat the uniform matched-cascode control. The best remained `[1.0, 1.0, 1.0]`
at `0.773048 LSB` (TT/SS/FF `0.396285/0.773048/0.579539 LSB`), above the
`0.5 LSB` gate. Evidence and a hash-bound simulator/PDK record are in
`differential-cascode-group-bias-search.json` and
`differential-cascode-group-bias-provenance.json`. The recursive mutation
memory now contains `179/179` rejected actions. Bias-only group trims are
therefore not a useful next action; the next circuit exploration must change
the regulation mechanism itself, such as a transistor-level active-feedback
amplifier controlling correction current. No analog runtime or physical
authorization changed.

## Transistor-level active-feedback correction search (2026-09-22)

A bounded 13-point search then replaced the fixed cascode gate bias with six
transistor-level PMOS differential-pair/NMOS-mirror OTAs driving matched
correction cascodes. Ten candidates completed electrical evaluation across TT,
SS, and FF; all ten were monotonic and settled within 10 mV. The other three
cases, all using a 200u OTA tail device, exceeded the available Sky130 model
geometry and were rejected with `could not find a valid modelname`. They are
model-coverage failures, not evidence of circuit instability or electrical
failure. The best completed point
was 0.803436 LSB max INL (TT/SS/FF 0.516356/0.803436/0.772547 LSB), with a
15% VDD reference and 50% VDD OTA tail-gate bias. This does not beat the
0.773048 LSB matched fixed-cascode control and does not meet the 0.5 LSB gate.

The complete result and hash-bound provenance are in
`differential-active-feedback-search.json` and
`differential-active-feedback-provenance.json`. The record hashes the runner,
candidate model, corner loader, toolchain status, ngspice version, and 12
TT/SS/FF device-model files. Bias reference and tail-gate sources remain ideal;
this is not a complete physical OTA/bias implementation. Recursive converter
failure memory now records 192/192 rejected candidates across ten source
families. Runtime policy, board status, and physical claims are unchanged.

The next circuit search should not repeat the same reference/tail sweep and
must keep unsupported geometries in a separate model-coverage failure class.
Promotion still requires <=0.5 LSB at every required PVT corner, then mismatch,
held-out workload transfer, reproducible cost evidence, and ultimately
synchronized board measurements.

## Active-feedback compensation and mirror-load refinement (2026-09-22)

A follow-up 12-point full TT/SS/FF sweep crossed four OTA compensation
capacitors (`0.01p`--`0.2p`) with three NMOS mirror-load widths (`5u`--`20u`),
holding the best previous bias and input/tail dimensions fixed. All 12 candidates
passed monotonicity and 10 mV settling. The best was `0.803182 LSB`
(TT/SS/FF `0.506863/0.803182/0.728023 LSB`) at `0.01p` and `5u`; the previous
active-feedback best was `0.803436 LSB`. This `0.000254 LSB` gain is small,
does not beat the `0.773048 LSB` fixed-cascode control, and does not meet the
`0.5 LSB` gate. Capacitance did not materially change settled INL; it only
affects transient behavior, while mirror-load sizing caused a small DC shift.

The refinement report is `differential-active-feedback-refinement-search.json`
with its own hash-bound `differential-active-feedback-refinement-provenance.json`.
Its 12 outcomes are retained in failure memory, now `204/204` rejected entries
from 11 source families. Analog/runtime authorization remains closed.

## Shared transistor tail-bias experiment (2026-09-22)

To remove the ideal OTA tail-gate sources, the circuit model now supports a
shared diode-connected PMOS reference device mirrored into the six OTA tail
devices. A 1 MOhm passive divider still generates the 0.15 VDD OTA input
reference; this is a mixed MOS/resistor bias network, not a fully transistorized
reference. Three tail-current settings (5 kOhm, 10 kOhm, 20 kOhm) all passed
TT/SS/FF monotonicity and 10 mV settling. The best reached `0.828991 LSB`
(TT/SS/FF `0.530271/0.799964/0.828991 LSB`) at 5 kOhm, worse than the
`0.803182 LSB` ideal-bias active-feedback best and the `0.773048 LSB`
matched-cascode control. Therefore this bias substitution does not qualify for
promotion.

The candidate-level result and exact simulator/model provenance are recorded in
`differential-active-feedback-shared-bias-search.json` and
`differential-active-feedback-shared-bias-provenance.json`. Failure memory now
contains `207/207` rejected actions from 12 source families. Next, replace the
passive reference divider with a transistor-level reference and evaluate
mismatch before any workload or runtime handoff. No analog authorization,
runtime selection, or physical claim changed.

## Cross-task persistent-memory retrieval ablation (2026-09-22)

The policy-compiler goal's memory/transfer milestone now has an explicit
ablation. It retrieves a transformer proposal from the persistent derived
failure/performance memory (`11` bits, `1.005` gain, `k` placement; 6 safe and
30 failed observations out of 36), maps that precision to the nearest MLP
target resolution (10 bits), and evaluates two held-out noise domains using
the target numeric gate and digital fallback. Across four held-out noise
cases, the failure-aware retrieval has 2 safe analog cases and 2 fallbacks;
the task-local-only and shuffled-memory controls have 0 analog cases. All
gated policies preserve fallback correctness. Removing the target gate would
produce 2 unsafe analog attempts, so retrieved actions remain advisory until
target verification passes.

The failure-aware and mean-return-only source rankings selected the same
action in this small memory corpus, so this run does not show a distinct causal
benefit from the failure-rate feature itself. The target MLP sweep also lacks
explicit PVT-corner, converter-gate, and comparable-cost fields. This is
offline numeric-transfer evidence, not a promoted runtime policy or full
evidence-contract qualification. The replayable report is
`cross-task-memory-retrieval-ablation.json`; focused tests verify the mapping,
split, failure-aware ranking, and fail-closed behavior.

## Adaptive simulator-budget policy promotion (2026-09-22)

Historical checkpoint, superseded by the independent replication recorded
below. The initial cohort did not establish robust promotion.

The learned experiment selector now has a separate, narrowly scoped approval.
On three fresh cold-start seeds (`1103`, `1201`, `1301`), a frozen learned
predictor stopped after its first candidate whenever its best remaining safe
prediction did not imply positive INL gain. Its result matched the fixed
heuristic's best safe INL on every seed, with every executed candidate passing
monotonicity and settling. The learned policy used 48 simulator invocations
per seed versus 96 for the heuristic (144 versus 288 total). The aggregate
verifier rebuilt the comparison from child reports and checked invocation
ledgers, report hashes, disjoint validation pools, and the registered policy;
it reports no errors. This supports experiment-search efficiency only; the
three-seed test does not prove broad distributional robustness or analog
runtime benefit.

The promotion evaluator now approves `experiment_policy_promotion`, and the
recompiled/replayed handoff selects `learned_rsi` only for experiment
selection. `active_policy` remains `baseline_runtime_policy`, and the separate
learned runtime policy remains unapproved. End-to-end readiness is
`qualified_with_open_gates` (12/15 requirements passed), with only
`strict_runtime_analog_improvement`, `physical_board_validation`, and
`runtime_cost_model_consistency` open. The adaptive report is
`fresh-adaptive-budget-20260922-1103-1201-1301/adaptive_budget_rsi_experiment.json`;
promotion, handoff, and readiness outputs were regenerated from that evidence.

### Independent replication and promotion withdrawal (2026-09-22)

The fixed learned selector was evaluated without retuning on independent seeds
`1409`, `1501`, and `1601`. It used 48 simulator invocations per seed versus
96 for the heuristic (144 versus 288 total), and all candidates met safety
checks. However, learned best-safe maxINL was worse than the heuristic on
every seed: 3.55080 vs 3.51121 LSB, 3.54131 vs 3.51127 LSB, and 3.56821 vs
3.54647 LSB. The verifier confirmed the saved execution evidence, but quality
non-regression and the promotion gate failed. The evaluator therefore rejects
experiment-policy promotion; the compiled/replayed handoff uses
`baseline_experiment_selector`. This falsifies the original three-seed
promotion claim as a robust improvement. Call reduction alone is insufficient,
and this evidence does not demonstrate runtime analog or hardware improvement.

### Second incumbent–challenger robustness cohort (2026-09-22)

The unchanged incumbent–challenger policy was preregistered again with
pool-disjoint seeds `2003`, `2107`, and `2209`. The saved report is
hash-verified, and all executed candidates passed safety checks. However, the
learned policy continued on all three seeds, consuming 288 simulator
invocations—the same as the two-candidate heuristic—and its best-safe maxINL
was worse than the heuristic on seeds `2107` (3.62168 versus 3.59805 LSB) and
`2209` (3.55410 versus 3.54875 LSB). Seed `2003` was equal. The preregistered
quality and strict-efficiency gates therefore failed. Promotion was withdrawn
again and the handoff rolled back to `baseline_experiment_selector`. This
result is a robustness boundary for the current policy, not evidence for
tuning against these seeds; it does not affect the separate runtime analog or
hardware gates.

### Predictor calibration follow-up (2026-09-22)

The current distance-weighted INL predictor was calibrated with leave-one-out
residuals over the 54 frozen training rows. Absolute residuals were 0.02365
LSB median, 0.07261 LSB at p75, 0.18880 LSB at p90, 0.26113 LSB at p95, and
0.40374 LSB maximum. The replayable artifact is
`converter-search-predictor-calibration.json`. The search harness now supports
an uncertainty-adjusted stop certificate and an explicit heuristic-challenger
fallback; focused tests cover both paths. This is training-only calibration,
not a new promotion claim. A revised policy must use the calibrated margin,
be preregistered, and pass a fresh independent simulator cohort before any
experiment-selector promotion can be reconsidered.

### Polynomial-ridge calibrated cohort (2026-09-22)

The second revised policy used a deterministic second-order ridge ranker and
the calibrated `0.10980268473515142` LSB p90 uncertainty margin. On fresh,
pool-disjoint seeds `2303`, `2401`, and `2503`, it preserved safety, promotion
gate coverage, and best-safe candidate quality on every seed. Its predicted
gains were negative but smaller than the uncertainty margin, so the certified
stop rule correctly continued on all three seeds. It therefore used 288 calls,
equal to the heuristic's 288, and did not qualify for efficiency promotion.
The saved report is
`fresh-polynomial-ridge-incumbent-20260922-2303-2401-2503/incumbent_challenger_rsi_experiment.json`.
This is positive safety/calibration evidence but not a search-efficiency win;
the handoff remains on the baseline selector.

### Mixed geometry learned-search screen (2026-09-22)

A preregistered mixed population containing eight supported geometry actions and
four model-coverage-risk actions per seed was evaluated on seeds `3203`,
`3301`, and `3403`. The learned policy and controls all selected supported
actions in this cohort; all quality and safety comparisons therefore passed,
but no early-abort trial occurred and all methods used 288 simulator calls.
The corrected aggregate is
`mixed-geometry-screen-20260922-3203-3301-3403/mixed_geometry_screen_experiment.json`.
This is evidence that candidate geometry profiles and fail-closed accounting
are integrated without changing normal quality semantics, not evidence of a
policy-level efficiency win.

A second preregistered mixed cohort on seeds `3601`, `3703`, and `3801` loaded
the persistent memory before execution. Every child contract records the same
canonical memory hash
`5ce716e84e6c01725124e74ddb4104bebd88555125ae53d27d7901cee32ac73d` and two
entries; the aggregate was replayed after correcting the preregistration hash
fields. The learned policy again selected only supported geometry, so quality
and safety passed and no early-abort trial occurred (288 learned versus 288
heuristic calls). This confirms provenance and avoidance behavior, but still
does not demonstrate policy-level savings.

### Persistent model-coverage preflight memory (2026-09-22)

The two verified 200u failures are now materialized in
`model-coverage-failure-memory.json`, keyed by a canonical `nmos_widths`
signature and bound to the source screen hash. The benchmark can consume this
memory before simulator launch: a matching geometry is recorded as blocked,
incomplete, and unsafe with zero simulator invocations. Supported geometry
remains eligible for normal evaluation. Focused tests cover source hashing,
known-failure rejection, and zero-call accounting. This is proposal/search
memory only and does not authorize runtime or hardware behavior.

### Four-candidate recursive-budget cohort (2026-09-22)

To test whether extra local evidence would create a safe stopping point, the
calibrated ridge policy was given up to four candidates and evaluated on fresh,
pool-disjoint seeds `2603`, `2701`, and `2803`. The aggregate was independently
rebuilt from child reports and simulator invocation ledgers and is
`fresh-recursive-budget-20260922-2603-2701-2803/recursive_budget_rsi_experiment.json`.
All learned and heuristic candidates passed safety, and learned best-safe
quality was non-inferior on every seed. However, the learned policy executed
all four candidates on every seed: 576 calls versus 576 for the heuristic.
The recursive policy therefore supplies stronger quality evidence but no
efficiency improvement; it remains exploratory and unpromoted.

### Fail-fast multi-fidelity execution contract (2026-09-22)

The converter simulator boundary now accepts an explicit `early_abort`
evaluation plan. It may reorder the declared TT/SS/FF corners and stop a
candidate immediately after a corner fails execution, monotonicity, or the
10 mV settling check. An aborted candidate is marked incomplete and unsafe;
only a candidate that completes all declared corners can be `passed`. The
benchmark passes this plan only to the learned policy and retains full-fidelity
controls. Focused tests verify invocation accounting and fail-closed status.
This is execution infrastructure only: the current validation pools have not
yet produced a policy-level early-abort efficiency win. A separate declared
model-coverage screen did produce measured fail-fast savings: both 200u probe
actions failed on SS after 16 invocations versus 48 for full evaluation, a
66.7% reduction. The replayable artifact is
`early-abort-failure-screen-20260922.json`; these blocked probes are not
analog-quality or promotion evidence.

### Preregistered incumbent–challenger policy (2026-09-22)

The failed policy was not tuned against its replication seeds. Instead, a new
policy was preregistered in
`fresh-incumbent-challenger-20260922-1709-1801-1901/preregistered-protocol.json`
with fresh, pool-disjoint seeds `1709`, `1801`, and `1901`. It measures the
fixed heuristic's first candidate as an incumbent, then gives the learned
ranker at most one challenger opportunity and applies the same safety-aware
stopping rule. The saved execution report is hash-verified. It used 192
simulator invocations versus 288 for the heuristic; quality was non-inferior
on every seed (equal on seeds 1709 and 1901, better on 1801), all candidates
passed safety, and promotion-gate counts did not regress. The experiment
policy is therefore approved and replayed into the handoff. This remains a
bounded simulator-search result only; it does not promote the analog runtime
policy or establish board, silicon, measured-energy, or production benefit.

## Seed-held-out failure-memory ablation (2026-09-22)

The cross-task memory report now also runs leave-one-seed-out action retrieval
over the 36 fresh source cases, holding all PVT/noise observations for each of
six seeds out together. It checks each stored reliability label against the
converter gate and all three repeated correctness checks, maps source cases
back to the frozen population, and requires a complete per-action observation
set for every case. Across 36 held-out selected-action evaluations, the
failure-rate-first retriever produced 6 reliable cases versus 5 for a
conditional-output-quality-only selector. This is a descriptive one-case
difference on six held-out seeds, not a statistically established or promoted
gain; the original full-memory failure-aware and mean-return-only methods
still choose the same cross-task action. Target MLP transfer remains
advisory and numeric-gated, with no unsafe analog activation in the gated
replay. The source seed-heldout report and frozen-population hash are retained
in `cross-task-memory-retrieval-ablation.json`; the remaining target PVT,
converter-gate, and comparable-cost evidence gaps remain open.

## Frozen-ledger failure-memory audit (2026-09-22)

The self-improving policy compiler's failure-memory ablation now declares its
actual evidence unit. Its even-seed/odd-seed split uses 108 training and 108
held-out ledger rows, matching failures by workload, PVT model/temperature,
corner status, converter gate, placement, precision, and calibration while
excluding seed and injected noise from the coarse key. The retrospective
filter retained 2/2 reliable held-out rows and skipped 106/106 unreliable
rows (no reliable false skips). A seeded cold selection inspected 30 rows and
found no reliable cases. This reads precomputed outcomes and launches zero
simulator trials, so it establishes no simulator-call savings. The selected
failure-aware rows' mean declared energy proxy was 2.43x the cold selection's
mean: a coverage/cost tradeoff, not an unqualified improvement. The report is
`analog-in-memory-ai-inference/software-architecture/qualification/self-improving-policy-compiler-v1/results/memory-ablation.json`.

## Fresh persistent-preflight savings cohort (2026-09-22)

The preregistered three-seed cohort in
`preflight-memory-savings-20260922-3901-4003-4101/preflight_memory_savings_experiment.json`
replayed the hash-bound model-coverage memory during real converter searches.
The learned path removed the known failing geometry before simulator launch;
the heuristic control intentionally probed it and then evaluated the supported
candidate. Across seeds `3901`, `4003`, and `4101`, learned used 144 simulator
invocations versus 288 for heuristic, a 50% reduction, while the best complete
safe quality matched exactly on each seed and all quality/call checks passed.

This is the first fresh, multi-seed call-saving result for persistent search
memory. Its claim boundary is deliberately narrow: the saved work is
model-coverage preflight, blocked probes are expected control outcomes, and no
analog runtime or hardware policy is promoted. The next promotion-grade goal
is to combine this memory with a held-out geometry-diverse candidate pool in
which the learned policy must select among multiple supported analog actions,
then independently verify strict call reduction, non-inferior quality, safety,
and replayable rollback before changing the active policy.

## Code-dependent transfer-shaping mutation (2026-09-22)

The highest-priority converter action was executed as a new mutation family,
not another grouped width sweep. The active-feedback correction network now
accepts six independently decoded correction amplitudes in physical branch
order `1,6,2,5,3,4`. A preregistered 14-setting cohort retained the best
transistor-level OTA/reference setup and measured every candidate over all
eight codes at TT/SS/FF.

The corrected control reproduced the prior result at `0.7828549267517001` LSB;
11 candidates completed electrical checks and 3 were correctly classified as
model-blocked. The best completed candidate was the control itself, with no
strict improvement and no candidate near the `0.5` LSB gate. The hash-bound
report is
`analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/code-dependent-transfer-shaping-search.json`;
the structural replay tests verify protocol hashing, branch order, all-code
corner coverage, and aggregate best-candidate accounting.

This closes the code-dependent amplitude/width-shaping branch. The derived
next action is a distinct residue-injection or segmented-correction topology;
unchanged amplitude and width mutations should not be repeated. Runtime and
analog promotion remain closed, with digital fallback active.

## Active-feedback residue-injection topology (2026-09-22)

The next distinct topology added a separately biased, one-hot direct NMOS
residue-injection branch alongside each active-feedback correction branch. Its
preregistered eight-setting cohort completed all eight candidates over all
codes at TT/SS/FF. The best candidate (`4u` residue width, `0.05` rail-relative
gate) reached `0.7802641666429877` LSB versus the independently replayed
`0.7828549267517001` LSB control; all candidates passed monotonicity and 10 mV
settling. This is a strict simulator improvement, but it remains far above the
`0.5` LSB converter gate and is not runtime or hardware promotion evidence.

The hash-bound report is
`analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/residue-injection-topology-search.json`.
The derived next action is a code-dependent residue width/gate refinement around
the best topology, followed by mismatch and held-out-code evidence.

The code-dependent residue refinement then evaluated nine settings around the
`4u`, `0.05` control, including per-decoded-branch width and gate perturbations.
All nine passed the all-code TT/SS/FF electrical checks, but the best exactly
reproduced `0.7802641666429877` LSB. This closes the local residue
width/gate neighborhood; the action queue now advances to a distinct
segmented-residue or multi-level injection mechanism rather than repeating
these local settings.

## Two-level segmented residue topology (2026-09-22)

The next distinct mechanism was a two-level coarse/fine one-hot residue
injection branch alongside the active-feedback correction. Its eight-setting
preregistered cohort evaluated all eight codes at TT/SS/FF; all eight
candidates passed monotonicity and 10 mV settling. The best setting used an
8u coarse segment at 0.03 rail-relative gate drive and a 0.5u fine segment at
0.02, reaching `0.7778266906732229` LSB versus the prior `0.7802641666429877`
LSB control. This is the strongest new simulator improvement in the current
cycle, but it remains above the strict `0.5 LSB` gate and is not runtime or
hardware promotion evidence.

The hash-bound report is
`analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/segmented-residue-topology-search.json`.
The next action is per-decoded-branch segmented refinement, followed by
mismatch, held-out-code/workload, cost, and rollback gates.

The per-decoded-branch segmented refinement then evaluated nine settings around
that control. Seven completed electrically and two 0.25u proposals were
correctly model-blocked; the best valid setting reproduced `0.7778266906732229`
LSB with no local improvement. This closes the segmented width/gate family.
The next circuit action is a distinct feedback-linearization or
charge-redistribution mechanism, while the best segmented result remains the
simulation control for later mismatch and held-out validation.

## Source-degenerated feedback linearization (2026-09-22)

An explicit source-degeneration resistor was added to each decoded
active-feedback correction branch. Eight bounded resistances were evaluated
over all eight codes at TT/SS/FF; all candidates passed monotonicity and 10 mV
settling. The best result was `0.9246574330018525` LSB at 100 ohm, regressing
the `0.7778266906732229` LSB segmented control. This linearization family is
closed as safe-but-rejected simulator evidence, not a promotion candidate.

The recursive queue now advances to a distinct charge-redistribution
mechanism; runtime policy, mismatch, held-out workload, cost, rollback, and
board gates remain closed.

## Switched charge redistribution (2026-09-22)

The next distinct topology placed a code-selected charge-redistribution
capacitor on every decoded active-feedback branch. Eight capacitances were
evaluated over all eight codes at TT/SS/FF with the 1 ns/2 ns settling check;
all eight passed. Every candidate reproduced `0.7828549267517001` LSB, so the
family did not improve the `0.7778266906732229` LSB segmented control and did
not approach the `0.5 LSB` gate.

Static topology search now advances to the actual end-to-end robustness phase:
fresh mismatch and held-out-code/workload validation of the best segmented
control, followed by cost and rollback evidence. No runtime analog promotion
is authorized.

The topology-matched bounded mismatch cohort then evaluated nine nominal/±5%
LSB, mid-bit, MSB, and load perturbations. All nine passed electrical checks;
worst max INL was `0.7895709051493507` LSB. The held-out workload/PVT replay
covered 72 cases; because the strict 0.5 LSB gate remains closed, all 72
correctly selected digital fallback and all 72 fallback checks passed. This is
end-to-end safety evidence, not analog workload or hardware evidence.

The synchronized physical preflight is prepared for the current workload: the
guarded digital and hybrid-candidate packages have distinct runtime hashes and
identical input/reference hashes, and package validation passed. The paired
board coordinator correctly blocked before execution because no connected v75
target or `ANDROID_SERIAL` was present. This is package-integrity evidence only;
the persistent record is `segmented-board-preflight.json`.
