# Verification Workbench usability study

This study validates whether verification engineers can complete the workbench
journey without relying on platform knowledge. It is evidence gathering, not a
claim about usability until results are recorded and independently reviewed.

## Participants and setup

Recruit at least three engineers who have recent SystemVerilog simulation or
formal-debug experience, including one verification lead. Use a fixed seeded
counter project and the same release build for every session. Do not expose
the participant to the expected diagnosis or repair before the task.

## Observed tasks

1. Connect to a project, identify missing collateral, and upload the required
   RTL and checker.
2. Start a procedural simulation and explain whether the result is failed,
   blocked, or unexecuted.
3. Select the correct run and locate the first meaningful divergence using
   source, signal, event, and waveform evidence.
4. Review an exact repair proposal, identify its requirement and digest, and
   approve or reject it.
5. Compare baseline and retest, inspect coverage and claim boundaries, and
   record a sign-off decision.

Record task completion, elapsed time, wrong-run selections, unrecoverable
errors, help requests, and a short confidence rating. Capture the release
version, browser, viewport, project key scope, and evidence-bundle digest;
never record credentials or private design content in the study report.

## Release interpretation

The study is complete only when every participant's raw task results and
reviewer notes are retained, the aggregate metrics are calculated, and an
independent lead reviewer signs the result. A failed task is valid evidence and
must remain visible. Do not replace it with a sample success or average away a
blocked or abandoned task.

Use `pilot-usability-study-template.json` and validate it with:

```bash
python3 scripts/validate_usability_study.py deployment/pilot-usability-study-template.json
```

Finalized results require at least three participants, all five task records
per participant, measured completion/time fields, a lead reviewer, and a
SHA-256 digest over the retained evidence bundle.
