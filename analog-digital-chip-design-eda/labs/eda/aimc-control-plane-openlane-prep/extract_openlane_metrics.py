#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import os
import re
from pathlib import Path


DEFAULT_RUN = Path("/home/mehtama1/eda-tools/OpenLane/designs/aimc_control_plane/runs/aimc_control_plane_no_cts")
HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "openlane-no-cts-metrics-summary.md"
MANIFEST_OUTPUT = HERE / "openlane-no-cts-manifest.json"


KEYS = [
    "flow_status",
    "total_runtime",
    "routed_runtime",
    "synth_cell_count",
    "TotalCells",
    "CoreArea_um^2",
    "DIEAREA_mm^2",
    "wire_length",
    "vias",
    "wns",
    "tns",
    "spef_wns",
    "spef_tns",
    "critical_path_ns",
    "suggested_clock_period",
    "suggested_clock_frequency",
    "tritonRoute_violations",
    "Magic_violations",
    "pin_antenna_violations",
    "net_antenna_violations",
    "lvs_total_errors",
]


FINAL_ARTIFACT_KINDS = ["def", "gds", "lef", "lib", "sdc", "sdf", "spef"]


def load_metrics(run_dir: Path) -> dict[str, str]:
    metrics_path = run_dir / "reports" / "metrics.csv"
    with metrics_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 1:
        raise ValueError(f"expected one metrics row in {metrics_path}, found {len(rows)}")
    return rows[0]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    run_dir = Path(os.environ.get("OPENLANE_RUN_DIR", str(DEFAULT_RUN)))
    output = Path(os.environ.get("OPENLANE_METRICS_OUTPUT", str(OUTPUT)))
    manifest_output = Path(os.environ.get("OPENLANE_MANIFEST_OUTPUT", str(MANIFEST_OUTPUT)))
    boundary = (
        "This summary is from the no-CTS run. It is routed-layout evidence, not full CTS-enabled clock-tree signoff."
        if "no_cts" in run_dir.name
        else "This summary is from a CTS-enabled OpenLane run. It is local open-source flow evidence, not foundry or commercial-tool tapeout signoff."
    )
    metrics = load_metrics(run_dir)
    design = Path(metrics.get("design", run_dir.parent.parent.name)).name
    final_artifacts = [f"{kind}/{design}.{kind}" for kind in FINAL_ARTIFACT_KINDS]
    manufacturability = (run_dir / "reports" / "manufacturability.rpt").read_text(encoding="utf-8")
    final_root = run_dir / "results" / "final"

    lines = [
        f"# {design} OpenLane Metrics Summary",
        "",
        "This file is generated from the selected completed OpenLane run artifacts.",
        "",
        "```text",
        f"run_dir: {run_dir}",
    ]
    for key in KEYS:
        lines.append(f"{key}: {metrics.get(key, '<missing>')}")
    lines.extend(["```", "", "## Final Artifact Check", "", "```text"])
    for rel in final_artifacts:
        path = final_root / rel
        status = "present" if path.exists() and path.stat().st_size > 0 else "missing"
        lines.append(f"{rel}: {status}")
    lines.extend(["```", "", "## Manufacturability Extract", "", "```text"])
    for raw in manufacturability.splitlines():
        if "DRC violations" in raw or "LVS clean" in raw or "Pin violations" in raw or "Net violations" in raw:
            lines.append(raw)
    lines.extend([
        "```",
        "",
        "## Boundary",
        "",
        boundary,
        "",
    ])
    irdrop_warnings = run_dir / "logs" / "signoff" / "35-irdrop.warnings"
    if irdrop_warnings.is_file() and not irdrop_warnings.read_text(encoding="utf-8").strip():
        irdrop_log = run_dir / "logs" / "signoff" / "35-irdrop.log"
        if irdrop_log.is_file():
            ir_text = irdrop_log.read_text(encoding="utf-8")
            worst_drops = re.findall(r"Worstcase IR drop:\s+([0-9.eE+-]+) V", ir_text)
            if len(worst_drops) >= 2:
                lines.append(f"Modeled IR-drop worst cases: VPWR {worst_drops[0]} V, VGND {worst_drops[1]} V.")
        lines.extend([
            "The IR-drop run used explicit modeled VPWR/VGND source locations aligned to legal PDN nodes.",
            "These are local package-analysis assumptions, not measured package or board data.",
            "",
        ])
    elif irdrop_warnings.is_file():
        lines.extend([
            "IR-drop source-location warnings are present; these results are not power-integrity signoff evidence.",
            "",
        ])
    output.write_text("\n".join(lines), encoding="utf-8")
    manifest = {
        "schema_version": "aimc-control-plane-openlane-manifest-v0.1",
        "design": design,
        "run_dir": str(run_dir),
        "run_kind": "cts_enabled" if "no_cts" not in run_dir.name else "no_cts",
        "metrics_sha256": digest(run_dir / "reports" / "metrics.csv"),
        "manufacturability_sha256": digest(run_dir / "reports" / "manufacturability.rpt"),
        "summary": {"path": str(output), "sha256": digest(output)},
        "artifacts": {
            rel: {"path": str(final_root / rel), "sha256": digest(final_root / rel)}
            for rel in final_artifacts
            if (final_root / rel).is_file()
        },
        "claim_boundary": boundary,
        "release_decision": "implementation_and_local_signoff_evidence_only",
    }
    manifest_output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {output}")
    print(f"wrote {manifest_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
