# Converter Post-Layout Submission Path

This report proves the one-command intake path for a future real converter payload.

- status: `submission_path_ready_waiting_for_real_payload`
- submission script: `scripts/submit_converter_post_layout_payload.py`
- placeholder rejected: `True`
- missing-file payload rejected: `True`
- temporary positive payload accepted: `True`
- temporary fixture persisted: `False`

## First-Principles Reading

Submission is the point where a payload becomes part of the evidence trail. That step should not be a manual copy of files. It should run the same strict checks every time: field validation, file existence, break-even rerun, and a written submission report.

The dry run proves three things. The placeholder is rejected. A shape-correct payload with missing files is rejected. A temporary complete fixture is accepted and writes rerun/report files only inside a temporary directory. That means the command path is ready without storing synthetic post-layout evidence.

## Command For A Real Payload

Run `python3 scripts/submit_converter_post_layout_payload.py REAL_PAYLOAD.json`.

## Refused Claim

does not submit, save, or claim real post-layout converter evidence
