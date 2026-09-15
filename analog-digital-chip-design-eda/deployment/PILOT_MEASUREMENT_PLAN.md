# Verification pilot measurement plan

Use this scorecard for a customer pilot. Record a baseline period before
enabling the workbench, then compare the same testbench scope and failure mix
after adoption. Every result must link to a run ID, request ID, artifact hash,
and reviewer decision.

| Metric | Definition | Evidence | Acceptance target |
|---|---|---|---|
| Triage latency | Time from terminal failure event to first root-cause hypothesis | Durable event timestamps and reviewer receipt | 30% lower median than baseline |
| Root-cause usefulness | Reviewer marks hypothesis actionable without reopening the full regression | Signoff notes and adjudicated finding | ≥80% actionable across sampled failures |
| Reproduction time | Time from selected failure to a bounded rerun with linked artifacts | Baseline/retest job timestamps | 25% lower median |
| Regression signal quality | Fraction of sampled failures with complete run identity, logs, waveform/proof status, and hashes | Evidence endpoint and bundle manifest | 100% complete or explicitly blocked |
| Manual effort | Human actions required to prepare, inspect, and hand off a sampled run | Browser trace and request IDs | 30% fewer actions than baseline |
| Closure integrity | Approved retests whose comparison scope is comparable and whose receipt verifies | Comparison report and signoff receipt | 100%; incomparable scope blocks signoff |

## Sampling and controls

Select at least 20 failures across simulation, lint, formal, and regression
categories, including at least three blocked or timeout cases. Keep the RTL,
testbench, tool versions, timeout policy, and sampling window fixed between
baseline and workbench periods. Record exclusions with a reason; do not replace
missing coverage with a simulation-pass proxy.

## Review protocol

Two verification engineers independently label triage usefulness and effort.
Resolve disagreements with a verification lead, retaining the original labels.
The lead signs the final scorecard only when each numerator and denominator is
traceable to immutable evidence bundles. Report confidence intervals for
sampled metrics and state when the sample is too small for a general claim.

The scorecard measures workflow value. It does not claim exhaustive functional
coverage, formal completeness, silicon correctness, or replacement of a
customer's qualified EDA signoff process.

Validate a completed JSON scorecard before attaching it to a handoff:

```bash
python3 scripts/validate_pilot_scorecard.py deployment/pilot-scorecard-template.json --finalized
```

An empty result means the structural contract passed; it does not replace the
lead review or evidence-bundle verification.

For a collected before/after sample, use the deterministic collector:

```bash
python3 scripts/collect_pilot_scorecard.py baseline-observations.json \
  workbench-observations.json --customer CUSTOMER --project PROJECT \
  --output .artifacts/customer-scorecard.json
python3 scripts/validate_pilot_scorecard.py .artifacts/customer-scorecard.json
```

The collector requires the same failure IDs in both periods, at least 20
observations, all four required categories, and at least three blocked or
timeout cases. It computes the six metrics but leaves independent labeling and
lead approval review-only. Continuous metrics include a deterministic bootstrap
95% interval; fraction metrics include a Wilson 95% interval so the lead can
judge uncertainty instead of treating a small sample as a precise claim.
Finalization validation also rejects scorecards that omit or invert any metric's
confidence interval.
