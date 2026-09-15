#!/usr/bin/env python3
"""Verify the hash-bound local AIMC multi-clock signoff package."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent.parent
DEFAULT_PACKAGE = HERE / "labs/eda/aimc-multi-clock-control-subsystem-openlane-prep"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def main() -> int:
    package = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PACKAGE
    manifest_name = sys.argv[2] if len(sys.argv) > 2 else "openlane-multiclock-sdc-manifest.json"
    manifest_path = package / manifest_name
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if "vsrc" in manifest["run_dir"]:
        assumptions = package / "vsrc_sources.md"
        require(assumptions.is_file(), "modeled PDN-source assumptions are undocumented")
    require((package / "fanout-eco-comparison.md").is_file(),
            "fanout ECO decision record is missing")
    run_dir = Path(manifest["run_dir"])
    require(manifest["release_decision"] == "implementation_and_local_signoff_evidence_only",
            "release decision must remain local-signoff-only")
    require(manifest["claim_boundary"].startswith("This summary is from a CTS-enabled OpenLane run"),
            "commercial/foundry claim boundary is missing")

    summary = package / Path(manifest["summary"]["path"]).name
    require(summary.is_file(), f"missing summary: {summary}")
    require(sha256(summary) == manifest["summary"]["sha256"], "summary hash mismatch")
    for key in ("metrics_sha256", "manufacturability_sha256"):
        source = run_dir / ("reports/metrics.csv" if key == "metrics_sha256" else "reports/manufacturability.rpt")
        require(source.is_file(), f"missing source report: {source}")
        require(sha256(source) == manifest[key], f"{key} mismatch")

    for rel, record in manifest["artifacts"].items():
        artifact = Path(record["path"])
        require(artifact.is_file() and artifact.stat().st_size > 0, f"missing artifact: {rel}")
        require(sha256(artifact) == record["sha256"], f"artifact hash mismatch: {rel}")

    summary_text = summary.read_text(encoding="utf-8")
    for expected in (
        "spef_wns: 0.0",
        "spef_tns: 0.0",
        "tritonRoute_violations: 0",
        "Magic_violations: 0",
        "pin_antenna_violations: 0",
        "net_antenna_violations: 0",
        "lvs_total_errors: 0",
        "Design is LVS clean.",
    ):
        require(expected in summary_text, f"missing clean signoff evidence: {expected}")

    signoff_sdc = next(Path(record["path"]) for rel, record in manifest["artifacts"].items() if rel.startswith("sdc/"))
    sdc_text = signoff_sdc.read_text(encoding="utf-8")
    require(re.search(r"create_clock .*core_clk", sdc_text), "core clock missing from signoff SDC")
    require(re.search(r"create_clock .*maintenance_clk", sdc_text), "maintenance clock missing from signoff SDC")
    require("set_clock_groups" in sdc_text, "clock relationship missing from signoff SDC")

    checks = run_dir / "reports/signoff/34-rcx_sta.checks.rpt"
    require(checks.is_file(), f"missing signoff checks report: {checks}")
    checks_text = checks.read_text(encoding="utf-8")
    require("max fanout" in checks_text.lower(), "fanout check was not reported")
    require("unclocked register" not in checks_text.lower(), "unclocked-register warning remains")
    require("unconstrained endpoint" not in checks_text.lower(), "unconstrained-endpoint warning remains")
    fanout_match = re.search(r"max fanout violation count (\d+)", checks_text, re.IGNORECASE)
    require(fanout_match is not None, "fanout violation count is missing")
    fanout_count = int(fanout_match.group(1))
    irdrop_warnings = run_dir / "logs/signoff/35-irdrop.warnings"
    require(irdrop_warnings.is_file(), f"missing IR-drop warnings report: {irdrop_warnings}")
    irdrop_text = irdrop_warnings.read_text(encoding="utf-8")
    if "vsrc" in run_dir.name:
        require(not irdrop_text.strip(), "aligned IR-drop run still has warnings")
        require((run_dir / "reports/signoff/35-irdrop-VPWR.rpt").is_file(), "missing VPWR IR report")
        require((run_dir / "reports/signoff/35-irdrop-VGND.rpt").is_file(), "missing VGND IR report")
        irdrop_log = run_dir / "logs/signoff/35-irdrop.log"
        drops = re.findall(r"Worstcase IR drop:\s+([0-9.eE+-]+) V",
                           irdrop_log.read_text(encoding="utf-8"))
        require(len(drops) >= 2, "modeled IR-drop values are missing")
    else:
        require("VSRC" in irdrop_text, "IR-drop source-location boundary is not recorded")

    print(json.dumps({"status": "passed", "package": str(package), "run_dir": str(run_dir),
                      "artifacts": len(manifest["artifacts"]),
                      "fanout_check": {"count": fanout_count,
                                       "status": "reported; warning intentionally preserved"},
                      "irdrop": ("explicit modeled sources; local evidence only"
                                 if "vsrc" in run_dir.name
                                 else "not signoff-grade; VSRC locations omitted")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, KeyError, StopIteration, ValueError, json.JSONDecodeError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        raise SystemExit(1)
