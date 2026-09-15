# Verification Workbench adversarial evaluation

This is the evaluation contract for an LLM acting as a skeptical reviewer. It
does not replace deterministic browser and service assertions.

## Judge roles

- First-time pilot engineer: can I connect, select inputs, run a check, and
  understand the next action without URL editing or developer tools?
- Debug engineer: does every selected failure show the matching run, revision,
  logs, waveform availability, and diagnosis evidence?
- Verification lead: can I inspect the exact proposal, retest scope, comparison,
  bundle inventory, limitations, reviewer identity, and report hash before
  signing?

## Required input

Provide the judge the current screenshots, DOM snapshots, browser action trace,
API responses, and artifact/run identities from the relevant test. Do not give
it only the marketing copy or a seeded screenshot.

## Scenarios

1. Select two distinct failures in succession. The second must never display or
   mutate the first failure's evidence.
2. Switch projects while an evidence request is delayed. The old response must
   not populate the new project.
3. Hide the waveform file and run again. The result must say evidence is
   unavailable or blocked; it must not claim a verified waveform.
4. Change the RTL after creating a repair proposal. Approval of the old digest
   must be rejected.
5. Approve a repair and narrow the retest scope. The judge must call out an
   incomparable result instead of declaring closure automatically.
6. Disconnect the service during polling. Existing identity and last known
   state must remain visible with a recoverable error.
7. Submit an expired or missing credential. No sample metrics, failures, or
   report may appear in connected mode.
8. Load a passing run with no functional coverage marker. The UI must show
   coverage as unreported rather than inventing a percentage.

## Finding format

Every finding must include:

```json
{
  "severity": "P0|P1|P2|P3",
  "role": "first-time|debug|lead",
  "action_sequence": ["..."],
  "expected": "...",
  "observed": "...",
  "evidence": ["screenshot or DOM/API artifact"],
  "trust_risk": "...",
  "acceptance_test": "..."
}
```

The judge must not award credit for a favorable prose claim when a browser
assertion, artifact hash, report boundary, or API result contradicts it. Model
findings are hypotheses until reproduced by the deterministic suite. Diagnose
correctness and interface usability are scored separately.

The generated packet includes `packet_sha256`, computed over the canonical
packet with that field removed. Recompute it before review and compare it to
the stored value. When `--findings` is supplied, the packet also records the
finding file's SHA-256 and count under `llm_adjudication`; a finding file is
attached for reproduction only after that digest is checked. An absent
`llm_adjudication` attachment means no independent LLM review is present.

## Current deterministic gate

`scripts/verify_workbench_browser.py` covers selection isolation, missing
evidence, artifact inspection/filtering, section navigation, sample report
guard, mobile navigation, connected-mode no-sample fallback, labels, focus,
and page errors. `scripts/verify_workbench_setup.py` covers credential recovery,
project creation, uploads, bound run submission, reload, and cancellation.
`scripts/verify_workbench_handoff.py` covers selected-run PoV, bundle preview,
and reviewer signoff. The service tests cover exact repair digest, worker
execution, evidence identity, report generation, and comparison.

The current gates prove the listed state-isolation, missing-evidence,
credential-boundary, formal-timeout, delayed-refresh, and signoff-integrity
scenarios in a deterministic browser/service harness. They do not prove that
representative verification engineers can complete the workflows efficiently,
or that an independent LLM reviewer agrees with the deterministic results.
Those remain release requirements and must be recorded separately from the
deterministic packet.
