# Converter Post-Layout Submission Preview

- status: `ready_to_submit_without_writing`
- source payload: `evidence/aimc-simulator-adapters/starter-post-layout-candidate/payload.json`
- output dir: `evidence/aimc-simulator-adapters/accepted-post-layout`
- converter id ready: `True`
- would write accepted evidence: `True`
- strict issue count: `0`

This preview answers one practical question before submission: if the strict submitter ran on this payload, would it write accepted evidence, and which files would it write?

## First Principle

Submission should be boring. The only time it should create accepted evidence is when the payload already names one real converter, one real run, real referenced files, and real numeric values. A preview step lets a reviewer inspect that boundary without creating the accepted directory.

## Would Write Files

- `evidence/aimc-simulator-adapters/accepted-post-layout/aimc-converter-macro-starter-layout-smoke.break-even-rerun.json`
- `evidence/aimc-simulator-adapters/accepted-post-layout/aimc-converter-macro-starter-layout-smoke.submission-report.json`

## Submission Command

`python3 scripts/submit_converter_post_layout_payload.py evidence/aimc-simulator-adapters/starter-post-layout-candidate/payload.json`

## Strict Issues

- none

## Refused Claim

does not submit evidence, does not create accepted-post-layout, does not run break-even, and does not prove post-layout converter replacement
