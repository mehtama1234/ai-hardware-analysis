#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
WORKSPACE = EVIDENCE / "candidate-post-layout"
OUT_JSON = EVIDENCE / "first-real-converter-physical-object-audit.json"
OUT_MD = EVIDENCE / "first-real-converter-physical-object-audit.md"

REQUIRED_PARTS = {
    "row_dac": ["row_dac", "dac"],
    "sar_readout": ["sar", "adc", "comparator", "readout"],
    "shared_mux": ["mux", "shared"],
    "references": ["reference", "vref", "ref"],
    "sample_path": ["sample", "hold", "switch", "sampling"],
}


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def read_lower(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore").lower()
    except OSError:
        return ""


def candidate_files() -> list[Path]:
    if not WORKSPACE.exists():
        return []
    return sorted(path for path in WORKSPACE.rglob("*") if path.is_file() and path.name != ".gitkeep")


def inspect_file(path: Path) -> dict[str, Any]:
    text = read_lower(path)
    looks_like_netlist = path.suffix.lower() in {".sp", ".spice", ".cir"} or ".subckt" in text
    matched_parts = []
    if looks_like_netlist:
        for part, terms in REQUIRED_PARTS.items():
            if any(term in text or term in path.name.lower() for term in terms):
                matched_parts.append(part)
    return {
        "path": rel(path),
        "bytes": path.stat().st_size,
        "suffix": path.suffix,
        "matched_parts": matched_parts,
        "looks_like_netlist": looks_like_netlist,
        "looks_like_measurement_json": path.suffix.lower() == ".json" and "result_type" in text,
    }


def build_report() -> dict[str, Any]:
    files = [inspect_file(path) for path in candidate_files()]
    present_parts = sorted({part for item in files for part in item["matched_parts"]})
    missing_parts = [part for part in REQUIRED_PARTS if part not in present_parts]
    netlist_files = [item["path"] for item in files if item["looks_like_netlist"]]
    expected_netlist = "evidence/aimc-simulator-adapters/candidate-post-layout/netlist/aimc_readout_candidate_001_extracted.spice"
    expected_exists = (ROOT / expected_netlist).exists()
    complete = expected_exists and not missing_parts
    status = "b1_physical_object_ready_not_accepted_evidence" if complete else "physical_object_missing"
    return {
        "result_type": "first_real_converter_physical_object_audit",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "candidate_id": "aimc_readout_candidate_001",
        "workspace": rel(WORKSPACE),
        "expected_extracted_netlist": expected_netlist,
        "expected_extracted_netlist_exists": expected_exists,
        "candidate_file_count": len(files),
        "netlist_file_count": len(netlist_files),
        "candidate_files": files,
        "required_parts": sorted(REQUIRED_PARTS),
        "present_parts": present_parts,
        "missing_parts": missing_parts,
        "ready_for_b1": complete,
        "claim_boundary": {
            "allowed": "audits whether the first converter candidate has one inspectable physical object",
            "not_allowed": "does not measure energy, latency, noise, or area, does not fill the candidate payload, and does not write accepted post-layout evidence",
        },
    }


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# First Real Converter Physical Object Audit",
        "",
        f"- status: `{report['status']}`",
        f"- candidate id: `{report['candidate_id']}`",
        f"- workspace: `{report['workspace']}`",
        f"- expected extracted netlist: `{report['expected_extracted_netlist']}`",
        f"- expected extracted netlist exists: `{report['expected_extracted_netlist_exists']}`",
        f"- candidate file count: `{report['candidate_file_count']}`",
        f"- netlist file count: `{report['netlist_file_count']}`",
        f"- ready for B1: `{report['ready_for_b1']}`",
        "",
        "## First Principle",
        "",
        "A converter claim starts with an object. Before energy, latency, noise, or area can mean anything, the project must point to one physical circuit that turns an analog row result into a digital value.",
        "",
        "If the named extracted converter object exists and contains every required part, B1 is ready. The later blockers still need measured energy, latency, noise, area, and a break-even rerun on the same object.",
        "",
        "## Required Parts",
        "",
    ]
    for part in report["required_parts"]:
        state = "present" if part in report["present_parts"] else "missing"
        lines.append(f"- `{part}`: {state}")
    lines.extend(["", "## Candidate Files", ""])
    for item in report["candidate_files"]:
        parts = ", ".join(item["matched_parts"]) if item["matched_parts"] else "none"
        lines.append(f"- `{item['path']}`: {item['bytes']} bytes; matched parts: {parts}")
    lines.extend([
        "",
        "## What Would Close B1",
        "",
        f"Create `{report['expected_extracted_netlist']}` and make it contain or reference row DAC, SAR/readout, shared mux, references, and sample path behavior for the same candidate.",
        "",
        "## Refused Claim",
        "",
        report["claim_boundary"]["not_allowed"],
        "",
    ])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print("first_real_converter_physical_object_audit")
    print(f"status,{report['status']}")
    print(f"candidate_file_count,{report['candidate_file_count']}")
    print(f"netlist_file_count,{report['netlist_file_count']}")
    print(f"ready_for_b1,{report['ready_for_b1']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
