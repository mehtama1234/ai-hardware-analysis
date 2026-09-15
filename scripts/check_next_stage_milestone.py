"""Independently validate a next-stage aggregate report."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


EXPECTED = {
    "openlane-historical-issue-device-agent-repair", "openlane-historical-issue-device-agent-repair-integrity",
    "openlane-historical-podman-mount-agent-repair", "openlane-historical-podman-mount-agent-repair-integrity",
    "openlane-historical-lec-readlib-agent-repair", "openlane-historical-lec-readlib-agent-repair-integrity",
    "openlane-historical-jenkins-pdk-agent-repair", "openlane-historical-jenkins-pdk-agent-repair-integrity",
    "openlane-historical-go-install-agent-repair", "openlane-historical-go-install-agent-repair-integrity",
    "openlane-historical-io-read-def-agent-repair", "openlane-historical-io-read-def-agent-repair-integrity",
    "openlane-historical-remove-nets-agent-repair", "openlane-historical-remove-nets-agent-repair-integrity",
    "openlane-historical-antenna-margin-agent-repair", "openlane-historical-antenna-margin-agent-repair-integrity",
    "openroad-historical-estimate-parasitics-agent-repair", "openroad-historical-estimate-parasitics-agent-repair-integrity",
    "openlane-historical-klayout-design-name-agent-repair", "openlane-historical-klayout-design-name-agent-repair-integrity",
    "openlane-historical-ioplacer-extension-agent-repair", "openlane-historical-ioplacer-extension-agent-repair-integrity",
    "openlane-historical-threads-agent-repair", "openlane-historical-threads-agent-repair-integrity",
    "openlane-historical-jenkins-tag-agent-repair", "openlane-historical-jenkins-tag-agent-repair-integrity",
    "openlane-historical-save-def-agent-repair", "openlane-historical-save-def-agent-repair-integrity",
    "openlane-historical-macro-rotation-agent-repair", "openlane-historical-macro-rotation-agent-repair-integrity",
    "openlane-historical-drc-file-agent-repair", "openlane-historical-drc-file-agent-repair-integrity", "openlane-historical-sdc-override-agent-repair", "openlane-historical-sdc-override-agent-repair-integrity", "openlane-historical-latest-run-agent-repair", "openlane-historical-latest-run-agent-repair-integrity", "openlane-historical-bm64-lint-agent-repair", "openlane-historical-bm64-lint-agent-repair-integrity", "openlane-historical-flow-endpoint-agent-repair", "openlane-historical-flow-endpoint-agent-repair-integrity", "cross-sim-historical-accuracy-agent-repair", "cross-sim-historical-accuracy-agent-repair-integrity", "openroad-historical-cached-copy-agent-repair", "openroad-historical-cached-copy-agent-repair-integrity", "openlane-historical-synth-analyze-agent-repair", "openlane-historical-synth-analyze-agent-repair-integrity", "openlane-historical-synth-explore-agent-repair", "openlane-historical-synth-explore-agent-repair-integrity", "openroad-historical-cts-snapshot-agent-repair", "openroad-historical-cts-snapshot-agent-repair-integrity", "openroad-historical-antenna-limit-agent-repair", "openroad-historical-antenna-limit-agent-repair-integrity", "openlane-historical-config-glob-agent-repair", "openlane-historical-config-glob-agent-repair-integrity", "openroad-historical-stale-target-agent-repair", "openroad-historical-stale-target-agent-repair-integrity", "openlane-historical-halo-width-agent-repair", "openlane-historical-halo-width-agent-repair-integrity",
    "openlane-historical-irdrop-args-agent-repair", "openlane-historical-irdrop-args-agent-repair-integrity",
    "openlane-historical-lec-catch-agent-repair", "openlane-historical-lec-catch-agent-repair-integrity",
    "openlane-historical-placement-order-agent-repair", "openlane-historical-placement-order-agent-repair-integrity",
    "openlane-historical-linter-defines-agent-repair", "openlane-historical-linter-defines-agent-repair-integrity",
    "openlane-historical-resizer-typo-agent-repair", "openlane-historical-resizer-typo-agent-repair-integrity",
    "openlane-historical-lec-liberty-agent-repair", "openlane-historical-lec-liberty-agent-repair-integrity",
    "openlane-historical-sta-blackbox-agent-repair", "openlane-historical-sta-blackbox-agent-repair-integrity",
    "openlane-historical-yosys-check-agent-repair", "openlane-historical-yosys-check-agent-repair-integrity",
    "openlane-historical-report-path-agent-repair", "openlane-historical-report-path-agent-repair-integrity",
    "openlane-historical-macro-units-agent-repair", "openlane-historical-macro-units-agent-repair-integrity",
    "openlane-historical-design-path-agent-repair", "openlane-historical-design-path-agent-repair-integrity",
    "repository-fail-to-pass", "mutation-closure", "heldout-mutation-evaluation",
    "real-openlane-operation-partition-causal-agent-repair", "real-openlane-operation-partition-causal-agent-repair-integrity",
    "real-error-budget-causal-localization", "real-error-budget-causal-localization-integrity",
    "real-openlane-error-budget-causal-agent-repair", "real-openlane-error-budget-causal-agent-repair-integrity",
    "real-peripheral-causal-localization", "real-peripheral-causal-localization-integrity",
    "real-openlane-peripheral-causal-agent-repair", "real-openlane-peripheral-causal-agent-repair-integrity",
    "repository-agent-matrix", "repository-agent-matrix-integrity", "parameterized-mutation-100", "parameterized-mutation-100-integrity", "workstream2-mutation-1000", "workstream2-mutation-1000-integrity", "real-multimodule-rtl-catalog", "real-multimodule-rtl-catalog-integrity", "real-openlane-peripheral-agent-repair", "real-openlane-peripheral-agent-repair-integrity", "real-openlane-multiclock-agent-repair", "real-openlane-multiclock-agent-repair-integrity", "real-openlane-operation-partition-agent-repair", "real-openlane-operation-partition-agent-repair-integrity", "real-openlane-error-budget-agent-repair", "real-openlane-error-budget-agent-repair-integrity", "real-causal-localization", "real-causal-localization-integrity", "real-multiclock-causal-localization", "real-multiclock-causal-localization-integrity", "real-openlane-multiclock-causal-agent-repair", "real-openlane-multiclock-causal-agent-repair-integrity", "coverage-gap-agent", "coverage-closure",
    "agent-repair-closure", "agent-causal-closure-integrity",
    "repaired-induction", "formal-proof-closure", "formal-proof-closure-integrity", "security-red-blue", "security-policy-campaign", "security-policy-campaign-integrity", "openroad-functional",
    "openlane-native-compile", "openroad-native-compile", "openroad-fifo-functional", "openroad-fifo-agent-repair-closure", "openroad-fifo-agent-repair-integrity", "openroad-aes-functional", "openroad-agent-repair-closure", "openroad-aes-agent-repair-closure", "openroad-historical-gallery-agent-repair", "openroad-historical-gallery-agent-repair-integrity", "openlane-timeout-agent-repair-closure", "openlane-historical-gui-agent-repair", "openlane-historical-gui-agent-repair-integrity", "openlane-historical-tcl-env-agent-repair", "openlane-historical-tcl-env-agent-repair-integrity", "openlane-historical-clock-port-agent-repair", "openlane-historical-clock-port-agent-repair-integrity", "openlane-historical-pin-order-agent-repair", "openlane-historical-pin-order-agent-repair-integrity", "cross-sim-historical-parasitics-agent-repair", "cross-sim-historical-parasitics-agent-repair-integrity", "historical-fix-candidate-mining", "historical-fix-candidate-mining-integrity", "historical-replay-split-integrity", "historical-replay-queue", "historical-replay-queue-integrity", "openlane-historical-io-sequence-agent-repair", "openlane-historical-io-sequence-agent-repair-integrity", "openlane-historical-resizer-env-agent-repair", "openlane-historical-resizer-env-agent-repair-integrity", "openlane-historical-def-template-agent-repair", "openlane-historical-def-template-agent-repair-integrity", "openlane-historical-route-obs-agent-repair", "openlane-historical-route-obs-agent-repair-integrity", "agent-handoff", "spec-grounded-assertion-matrix", "spec-grounded-assertion-matrix-integrity",
}


def validate(report: dict) -> list[str]:
    errors = []
    if report.get("schema_version") != "next-stage-milestone-report-v1":
        errors.append("unsupported schema")
    supplied = report.get("components")
    if not isinstance(supplied, list):
        return ["components must be a list"]
    names = [item.get("name") for item in supplied if isinstance(item, dict)]
    if set(names) != EXPECTED or len(names) != len(set(names)):
        errors.append(f"component set mismatch: {sorted(names)}")
    if any(not isinstance(item, dict) or item.get("status") != "passed" or item.get("returncode") != 0 for item in supplied):
        errors.append("one or more components did not pass with returncode 0")
    if report.get("all_passed") is not True:
        errors.append("aggregate all_passed is not true")
    expected_digest = hashlib.sha256(json.dumps({key: value for key, value in report.items() if key != "report_sha256"}, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if report.get("report_sha256") != expected_digest:
        errors.append("report_sha256 mismatch")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    report = json.loads(args.report.read_text(encoding="utf-8"))
    errors = validate(report)
    result = {"schema_version": "next-stage-milestone-check-v1", "status": "passed" if not errors else "blocked", "report": str(args.report), "errors": errors}
    result["check_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    print(json.dumps(result, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
