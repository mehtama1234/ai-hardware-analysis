# Customer verification pilot framework

This framework translates the open-source workbench into a customer-shaped
technical engagement. It assumes simulation/formal execution first and keeps
physical silicon evidence separate.

## Discovery inputs

Capture one representative block, its revision, specification or register map,
normal testbench entry point, simulator/formal commands, regression metadata,
coverage format, and the team's accepted failure-report format. Record tool
versions, licensing constraints, run-time limits, and which actions require
human approval.

## 30-day foundation

- Map the customer's planning, regression, debug, review, and closure workflow.
- Select one block and seed or replay five representative failure classes.
- Build an adapter contract for the customer's simulator, formal engine, and
  coverage output; unavailable tools remain explicitly blocked.
- Establish baseline diagnosis time, duplicate-failure count, coverage, and
  engineer review effort.

## 60-day closed-loop pilot

- Ingest the collateral into typed IR with source hashes and retrieval links.
- Generate a traceable plan, reviewable SVA/UVM, and executable checks.
- Run regressions, cluster failures, back-trace signals, and attach waveform or
  counterexample evidence.
- Propose bounded repairs or next experiments; require human approval before
  design-intent changes.
- Retest an isolated repaired revision and generate a closure report.

## 90-day proof of value

Compare the assisted workflow with the customer's baseline using the same
design revision and regression seeds. Report:

- time from failure to accepted diagnosis;
- first-divergence localization accuracy;
- duplicate failures collapsed into actionable clusters;
- generated checks that compile and pass review;
- coverage gained per compute hour;
- redundant jobs avoided;
- requirements with complete traceability;
- invalid, vacuous, or unsupported closure claims detected; and
- engineer review time per closure decision.

## Acceptance gates

The pilot is successful only when the evidence bundle can be reproduced from a
clean checkout, every claim names its evidence kind, blocked backends are
visible, original RTL remains unchanged after repair, and customer engineers
accept the diagnosis and closure artifacts. A metric with no improvement is
retained as a result and used to reject or redesign that use case.

The current implementation demonstrates this contract on five open-source
benchmarks. The next customer-specific work is adapter implementation and
validation against the customer's normal toolchain and review process.
