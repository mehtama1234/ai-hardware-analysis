# Converter Post-Layout Candidate Readiness Run

- status: `candidate_not_ready_for_strict_submission`
- payload: `evidence/aimc-simulator-adapters/candidate-post-layout/payload.json`
- workspace: `evidence/aimc-simulator-adapters/candidate-post-layout`
- audit status: `candidate_workspace_still_scaffold`
- checklist status: `fill_checklist_ready`
- progress status: `candidate_waiting_for_real_values`
- preflight status: `not_ready_for_strict_submission`
- placeholder count: `29`
- missing or unresolved file count: `3`
- open checklist items: `32`
- preflight issue count: `22`
- ready for strict submission: `False`

This is the one-command readiness path for the candidate post-layout package. It refreshes the workspace audit, fill checklist, progress report, and preflight result. It stops before submission.

## First Principle

A real converter package should move through four questions in order. Does the workspace still contain placeholders? Does the checklist have open fields or files? Does the short progress state say the packet is ready? Does preflight agree that strict submission may start?

Only when all four answers are clean should the submission command run.

## Commands

- audit: `python3 scripts/audit_converter_post_layout_candidate_workspace.py`
- checklist: `python3 scripts/generate_converter_post_layout_candidate_fill_checklist.py`
- progress: `python3 scripts/generate_converter_post_layout_candidate_progress_report.py`
- preflight: `python3 scripts/preflight_converter_post_layout_payload.py evidence/aimc-simulator-adapters/candidate-post-layout/payload.json`
- submit_if_ready: `python3 scripts/submit_converter_post_layout_payload.py evidence/aimc-simulator-adapters/candidate-post-layout/payload.json`

## Refused Claim

does not submit evidence, does not write accepted post-layout artifacts, and does not prove converter physics
