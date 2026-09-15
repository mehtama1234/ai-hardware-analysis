#!/usr/bin/env python3
"""Build an auditable aggregate for the three-design closed-loop milestone."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--colab-report", type=Path, required=True)
    parser.add_argument("--handoff", action="append", nargs=2, metavar=("DESIGN", "PATH"), required=True)
    parser.add_argument("--formal-suite", action="append", nargs=2, metavar=("DESIGN", "PATH"), default=[])
    parser.add_argument("--stateful-formal-suite", action="append", nargs=2, metavar=("DESIGN", "PATH"), default=[])
    parser.add_argument("--temporal-suite", action="append", nargs=2, metavar=("DESIGN", "PATH"), default=[])
    parser.add_argument("--supersedes-sha256", action="append", default=[], help="Earlier hashes of this versioned aggregate manifest")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    colab = args.colab_report.resolve()
    designs = {}
    formal_suites = {design: Path(path).resolve() for design, path in args.formal_suite}
    stateful_formal_suites = {design: Path(path).resolve() for design, path in args.stateful_formal_suite}
    temporal_suites = {design: Path(path).resolve() for design, path in args.temporal_suite}
    for design, raw_path in args.handoff:
        path = Path(raw_path).resolve()
        report = json.loads(path.read_text(encoding="utf-8"))
        physical = report.get("physical", {})
        formal = report.get("formal", {})
        formal_suite = formal_suites.get(design)
        suite_report = json.loads(formal_suite.read_text(encoding="utf-8")) if formal_suite else None
        temporal_suite = temporal_suites.get(design)
        temporal_report = json.loads(temporal_suite.read_text(encoding="utf-8")) if temporal_suite else None
        stateful_formal_suite = stateful_formal_suites.get(design)
        stateful_formal_report = json.loads(stateful_formal_suite.read_text(encoding="utf-8")) if stateful_formal_suite else None
        formal = suite_report.get("proof", {}) if suite_report else report.get("formal", {})
        designs[design] = {
            "handoff_path": str(path),
            "handoff_sha256": digest(path),
            "status": report.get("status"),
            "physical": {"flow_status": physical.get("flow_status"), "source_match": physical.get("source_match"), "lvs_errors": physical.get("lvs_errors", physical.get("lvs_total_errors_from_report")), "gds_present": physical.get("gds_present"), "extracted_sta_present": physical.get("extracted_sta_present", True)},
            "formal": {"status": suite_report.get("status", "failed") if suite_report else formal.get("status", "not-recorded"), "property_count": formal.get("property_count", 0), "property_runs": formal.get("property_runs", []), "suite_path": str(formal_suite) if formal_suite else formal.get("path"), "suite_sha256": digest(formal_suite) if formal_suite else formal.get("sha256")},
            "temporal": {"status": temporal_report.get("status", "failed"), "property_count": temporal_report.get("proof", {}).get("property_count", 0), "suite_path": str(temporal_suite), "suite_sha256": digest(temporal_suite)} if temporal_suite else {"status": "not-required"},
            "stateful_formal": {"status": stateful_formal_report.get("status", "failed"), "assertion_count": stateful_formal_report.get("proof", {}).get("assertion_count", 0), "suite_path": str(stateful_formal_suite), "suite_sha256": digest(stateful_formal_suite)} if stateful_formal_suite else {"status": "not-required"},
        }
    physical_passed = all(item["physical"]["flow_status"] == "flow completed" and item["physical"]["source_match"] is True and item["physical"]["lvs_errors"] == 0 and item["physical"]["gds_present"] is True for item in designs.values())
    evidence = {
        "schema_version": "three-design-closed-loop-release-manifest-v1",
        "status": "passed" if len(designs) == 4 and all(item["status"] == "passed" for item in designs.values()) and physical_passed else "failed",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "design_count": len(designs),
        "designs": designs,
        "colab_model_evaluation": {"path": str(colab), "sha256": digest(colab)},
        "scope": "Three-design local closed-loop research milestone: Colab model proposal, bounded review-required repair, retest, formal evidence where recorded, and hash-linked OpenLane RTL2GDS physical evidence.",
        "claim_boundary": "Not commercial Innovus/ICC2/PrimeTime signoff, FPGA/emulation, analog qualification, foundry tapeout, manufactured silicon, or autonomous zero-bug operation.",
        "supersedes_sha256": sorted(set(args.supersedes_sha256)),
    }
    output = args.output.resolve(); output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": evidence["status"], "design_count": len(designs), "physical_passed": physical_passed}, sort_keys=True))
    return 0 if evidence["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
