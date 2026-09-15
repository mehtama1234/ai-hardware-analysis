# Public reference release

This release is the reproducible, open-source reference for the unified
evidence-first verification and inference-qualification platform. It requires
no proprietary EDA tools, customer credentials, or physical hardware.

From a clean checkout, install the pinned deployment requirements and run:

```bash
python3 -m pip install -r deployment/requirements.txt
python3 benchmarks/multi_design_pilot/ci_gate.py
python3 benchmarks/seeded_counter/run_end_to_end.py
python3 scripts/build_unified_release_manifest.py --output .artifacts/unified-hardware-verification-release.json
python3 scripts/verify_unified_release_manifest.py .artifacts/unified-hardware-verification-release.json --root .
python3 scripts/build_commercial_handoff_manifest.py --output .artifacts/commercial-handoff-manifest.json
python3 scripts/verify_commercial_handoff_manifest.py .artifacts/commercial-handoff-manifest.json --root .
python3 -m pytest -q deployment verification_platform
```

The canonical provider-free acceptance command runs the pilot, scorecard and
archive integrity checks, clean-archive replay, and the deterministic
browser/service adversarial gate in one bounded decision package:

```bash
python3 scripts/run_public_reference_acceptance.py
```

It writes `.artifacts/public-reference-acceptance.json`. A green result means
the digital reference release is ready for human sign-off; it never promotes
physical AIMC or measured-hardware claims.

The expected reference result is eleven intentionally failing seeded baselines,
eleven human-approved passing retests, valid artifact/session/release digests,
plus a seeded-counter `reference-agent-proposal.json` with
`status: review_required`, and a unified release decision of
`blocked_pending_qualification`. The latter
is correct: the reference release proves the digital workflow and records AIMC
simulation evidence, while physical-layout and measured-hardware claims remain
unsupported until their qualification gates close.

The release supports two safe agent paths. An agent may submit a typed,
source-revision-bound proposal through `/v1/projects/{project_id}/agent-proposals`
with evidence references. Deterministic adapters and an explicitly authorized
human own execution, repair application, retest, and sign-off.

When no external model is configured, `verification_platform.reference_agent`
provides a deterministic reference agent that turns a typed failure and its
evidence into a `review_required` diagnosis proposal. It is a demonstration of
the agent contract, not an assertion that deterministic text generation has
replaced an LLM.

The same path is available as a CLI. Given `failure.json` containing
`cycle`, `signal`, `expected`, and `actual`:

```bash
python3 scripts/run_reference_agent.py failure.json \
  --source-revision rtl-abc --evidence triage-report.json waveform.vcd \
  --dependency-cone counter_q enable \
  --output .artifacts/reference-agent-proposal.json
```

This package is a reference workflow and benchmark. It does not claim
exhaustive verification, silicon correctness, customer production readiness,
or business ROI.

To turn a captured coverage gap into the next bounded work item:

```bash
python3 scripts/plan_next_test.py \
  benchmarks/seeded_counter/runs/latest/functional-coverage.json \
  --source-revision seeded-counter-baseline-v1 \
  --evidence latest/triage-report.json
```

The output is a `review_required` proposal. An executable identical-scope
retest must produce new evidence before any closure decision is made.

Build the curated source-only archive with:

```bash
python3 scripts/build_public_reference_archive.py \
  --output .artifacts/public-reference-release.tar.gz
python3 scripts/verify_public_reference_archive.py \
  .artifacts/public-reference-release.tar.gz
python3 scripts/replay_public_reference_archive.py \
  .artifacts/public-reference-release.tar.gz
```

The command writes a sidecar JSON manifest and excludes generated run trees,
artifact directories, caches, and secrets.

Replay runs the full multi-design pilot from a temporary extraction, proving
that the archive is self-contained and does not depend on the original
checkout or external AIMC evidence.
