#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
WORKBENCH = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware" / "layout-workbench"
CANDIDATE = ROOT / "evidence" / "aimc-simulator-adapters" / "candidate-post-layout"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "analog-converter-layout-tool-readiness.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "analog-converter-layout-tool-readiness.md"

REQUIRED_TOOLS = ["magic", "xschem", "ngspice", "klayout"]
STARTER_FILES = [
    "README.md",
    "converter-layout-plan.json",
    "magic-extract-skeleton.tcl",
    "xschem-netlist-skeleton.sh",
    "post-layout-measurement-record.template.json",
]
REAL_LAYOUT_PATTERNS = ["*.sch", "*.mag", "*.gds", "*.lef", "*.dspf", "*.spef"]


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def tool_status() -> list[dict[str, Any]]:
    return [{"tool": tool, "path": shutil.which(tool), "available": shutil.which(tool) is not None} for tool in REQUIRED_TOOLS]


def starter_file_status() -> list[dict[str, Any]]:
    status = []
    for name in STARTER_FILES:
        path = WORKBENCH / name
        status.append({"path": rel(path), "exists": path.is_file(), "bytes": path.stat().st_size if path.is_file() else 0})
    return status


def real_layout_files() -> list[str]:
    files = []
    if not WORKBENCH.exists():
        return files
    for pattern in REAL_LAYOUT_PATTERNS:
        files.extend(rel(path) for path in WORKBENCH.rglob(pattern) if path.is_file() and path.stat().st_size > 0)
    return sorted(files)


def candidate_counts() -> dict[str, int]:
    return {
        "netlist_files": sum(1 for path in (CANDIDATE / "netlist").glob("*") if path.is_file() and path.stat().st_size > 0),
        "model_files": sum(1 for path in (CANDIDATE / "models").glob("*") if path.is_file() and path.stat().st_size > 0),
        "rerun_files": sum(1 for path in (CANDIDATE / "rerun").glob("*") if path.is_file() and path.stat().st_size > 0),
    }


def build_report() -> dict[str, Any]:
    tools = tool_status()
    starter_files = starter_file_status()
    layout_files = real_layout_files()
    counts = candidate_counts()
    tools_ready = all(item["available"] for item in tools)
    starter_ready = all(item["exists"] and item["bytes"] > 0 for item in starter_files)
    candidate_empty = all(value == 0 for value in counts.values())
    candidate_payload = CANDIDATE / "payload.json"
    candidate_is_rehearsal = False
    if candidate_payload.is_file():
        try:
            payload = json.loads(candidate_payload.read_text(encoding="utf-8"))
            candidate_is_rehearsal = payload.get("template_only") is True and "replace-with" in json.dumps(payload)
        except (OSError, json.JSONDecodeError):
            candidate_is_rehearsal = False
    if tools_ready and starter_ready and candidate_empty and layout_files:
        status = "first_starter_layout_present_candidate_evidence_still_empty"
    elif tools_ready and starter_ready and candidate_empty:
        status = "tools_ready_waiting_for_real_converter_layout"
    elif tools_ready and starter_ready and candidate_is_rehearsal:
        status = "starter_layout_present_candidate_rehearsal_artifacts_not_accepted"
    else:
        status = "layout_tool_readiness_needs_review"
    return {
        "result_type": "analog_converter_layout_tool_readiness",
        "status": status,
        "required_tools": tools,
        "all_required_tools_available": tools_ready,
        "workbench": rel(WORKBENCH),
        "starter_files": starter_files,
        "starter_files_ready": starter_ready,
        "real_layout_file_count": len(layout_files),
        "real_layout_files": layout_files,
        "candidate_post_layout_counts": counts,
        "candidate_post_layout_still_empty": candidate_empty,
        "candidate_post_layout_rehearsal_only": candidate_is_rehearsal,
        "blocking_files_not_yet_present": [
            "aimc_converter_macro.mag or aimc_converter_macro.gds",
            "aimc_converter_macro_extracted.sp, .dspf, or .spef",
            "post-layout model/setup file for the same run",
            "same-run converter break-even rerun JSON",
        ],
        "claim_boundary": {
            "allowed": "proves the local analog layout workbench has the expected starter files and required tools on PATH",
            "not_allowed": "does not draw converter layout, does not extract parasitics, does not run DRC/LVS, and does not create accepted post-layout evidence",
        },
    }


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# Analog Converter Layout Tool Readiness",
        "",
        f"- status: `{report['status']}`",
        f"- all required tools available: `{report['all_required_tools_available']}`",
        f"- workbench: `{report['workbench']}`",
        f"- starter files ready: `{report['starter_files_ready']}`",
        f"- real layout file count: `{report['real_layout_file_count']}`",
        f"- candidate post-layout still empty: `{report['candidate_post_layout_still_empty']}`",
        f"- candidate post-layout rehearsal only: `{report['candidate_post_layout_rehearsal_only']}`",
        "",
        "## First Principle",
        "",
        "A ready toolchain is not the same as a ready circuit. The tools can open, draw, extract, view, and simulate. The circuit only exists after a concrete layout or imported physical macro exists. This audit separates those two facts.",
        "",
        "The useful claim here is narrow: the local machine can start the analog layout work, and the repo now has the starter workbench. The still-missing claim is the physical converter itself.",
        "",
        "## Tools",
        "",
    ]
    lines.extend(f"- {item['tool']}: `{item['path']}`" for item in report["required_tools"])
    lines.extend(["", "## Starter Files", ""])
    lines.extend(f"- `{item['path']}` exists `{item['exists']}` bytes `{item['bytes']}`" for item in report["starter_files"])
    lines.extend(["", "## Real Layout Files Found", ""])
    if report["real_layout_files"]:
        lines.extend(f"- `{path}`" for path in report["real_layout_files"])
    else:
        lines.append("- none")
    lines.extend(["", "## Candidate Evidence Folder", ""])
    lines.extend(f"- {key}: `{value}`" for key, value in report["candidate_post_layout_counts"].items())
    lines.extend(["", "## Blocking Files Not Yet Present", ""])
    lines.extend(f"- {item}" for item in report["blocking_files_not_yet_present"])
    lines.extend(["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print("analog_converter_layout_tool_readiness")
    print(f"status,{report['status']}")
    print(f"all_required_tools_available,{report['all_required_tools_available']}")
    print(f"starter_files_ready,{report['starter_files_ready']}")
    print(f"real_layout_file_count,{report['real_layout_file_count']}")
    print(f"candidate_post_layout_still_empty,{report['candidate_post_layout_still_empty']}")
    print(f"candidate_post_layout_rehearsal_only,{report['candidate_post_layout_rehearsal_only']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
