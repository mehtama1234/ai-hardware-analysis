#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from preview_converter_post_layout_submission import DEFAULT_PAYLOAD, DEFAULT_OUT_DIR, build_report


ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-real-artifact-discovery.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-real-artifact-discovery.md"

SEARCH_ROOTS = ["evidence", "labs", "sources", "scripts", "docs"]
EXCLUDED_PARTS = {"site", "__pycache__", ".pytest_cache"}
SCAFFOLD_FILES = {
    "evidence/aimc-simulator-adapters/candidate-post-layout/payload.json",
    "evidence/aimc-simulator-adapters/candidate-post-layout/README.md",
    "evidence/aimc-simulator-adapters/candidate-post-layout/netlist/.gitkeep",
    "evidence/aimc-simulator-adapters/candidate-post-layout/models/.gitkeep",
    "evidence/aimc-simulator-adapters/candidate-post-layout/rerun/.gitkeep",
}


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def candidate_kind(path: Path) -> str | None:
    name = path.name.lower()
    suffix = path.suffix.lower()
    if suffix in {".spef", ".dspf", ".spice", ".gds", ".def", ".lef"}:
        return "layout_or_extraction_file"
    if "extracted" in name and suffix in {".sp", ".spi", ".cir", ".net"}:
        return "layout_or_extraction_file"
    if ".pex" in name:
        return "layout_or_extraction_file"
    if suffix == ".lib" or ("model" in name and suffix in {".sp", ".spi", ".cir", ".net", ".json"}):
        return "model_file"
    if ("rerun" in name or "break-even" in name or "break_even" in name) and suffix == ".json":
        return "rerun_artifact"
    return None


def generated_or_placeholder(path: Path) -> bool:
    text_markers = ["synthetic", "self-test", "temporary", "replace-with", "replace_with", "placeholder"]
    lowered_path = rel(path).lower()
    if any(marker in lowered_path for marker in text_markers):
        return True
    try:
        sample = path.read_text(encoding="utf-8", errors="ignore")[:4096].lower()
    except OSError:
        return False
    return any(marker in sample for marker in text_markers)


def scan_files() -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = {
        "layout_or_extraction_files": [],
        "model_files": [],
        "rerun_artifacts": [],
    }
    for root_name in SEARCH_ROOTS:
        root = ROOT / root_name
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or any(part in EXCLUDED_PARTS for part in path.parts):
                continue
            kind = candidate_kind(path)
            if kind is None:
                continue
            entry = {
                "path": rel(path),
                "bytes": path.stat().st_size,
                "generated_or_placeholder": generated_or_placeholder(path),
            }
            if kind == "layout_or_extraction_file":
                grouped["layout_or_extraction_files"].append(entry)
            elif kind == "model_file":
                grouped["model_files"].append(entry)
            elif kind == "rerun_artifact":
                grouped["rerun_artifacts"].append(entry)
    return grouped


def candidate_workspace_state() -> dict[str, Any]:
    workspace = ROOT / "evidence" / "aimc-simulator-adapters" / "candidate-post-layout"
    files = []
    if workspace.exists():
        for path in workspace.rglob("*"):
            if path.is_file():
                path_rel = rel(path)
                if path_rel not in SCAFFOLD_FILES:
                    files.append(path_rel)
    return {
        "workspace": rel(workspace),
        "exists": workspace.exists(),
        "non_scaffold_files": sorted(files),
        "non_scaffold_file_count": len(files),
    }


def build_discovery() -> dict[str, Any]:
    grouped = scan_files()
    preview = build_report(DEFAULT_PAYLOAD, DEFAULT_OUT_DIR)
    candidate_state = candidate_workspace_state()
    accepted_dir = DEFAULT_OUT_DIR
    real_like_counts = {
        key: sum(1 for item in items if not item["generated_or_placeholder"])
        for key, items in grouped.items()
    }
    package_ready = preview.get("would_write_accepted_evidence") is True
    status = "complete_real_artifact_package_found" if package_ready else "no_complete_real_artifact_package_found"
    return {
        "result_type": "converter_post_layout_real_artifact_discovery",
        "status": status,
        "searched_roots": SEARCH_ROOTS,
        "accepted_post_layout_exists": accepted_dir.exists(),
        "accepted_post_layout_dir": rel(accepted_dir),
        "candidate_workspace": candidate_state,
        "current_candidate_submission_status": preview.get("status"),
        "current_candidate_would_write_accepted_evidence": package_ready,
        "current_candidate_strict_issue_count": preview.get("strict_issue_count"),
        "artifact_counts": {key: len(value) for key, value in grouped.items()},
        "real_like_artifact_counts": real_like_counts,
        "artifacts": grouped,
        "claim_boundary": {
            "allowed": "records repo-local files that look like layout, extraction, model, or rerun artifacts and checks whether the current candidate payload can be accepted",
            "not_allowed": "does not prove that no real artifacts exist outside the searched roots, does not verify the physics of any discovered file, and does not turn scaffold or generated proof fixtures into accepted post-layout evidence",
        },
    }


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# Converter Post-Layout Real Artifact Discovery",
        "",
        f"- status: `{report['status']}`",
        f"- accepted post-layout exists: `{report['accepted_post_layout_exists']}`",
        f"- candidate non-scaffold file count: `{report['candidate_workspace']['non_scaffold_file_count']}`",
        f"- current candidate submission status: `{report['current_candidate_submission_status']}`",
        f"- current candidate would write accepted evidence: `{report['current_candidate_would_write_accepted_evidence']}`",
        f"- current candidate strict issue count: `{report['current_candidate_strict_issue_count']}`",
        "",
        "## First Principle",
        "",
        "A real post-layout claim needs a chain of named objects. The extracted circuit tells us what the layout became. The model file tells us which device and corner equations were used. The rerun artifact tells us whether those measured numbers changed the converter decision. If one part is missing, the claim stays blocked.",
        "",
        "## Repo-Local Artifact Counts",
        "",
    ]
    for key, count in report["artifact_counts"].items():
        lines.append(f"- {key}: `{count}` real-like `{report['real_like_artifact_counts'][key]}`")
    lines.extend([
        "",
        "## Candidate Workspace",
        "",
        f"- workspace: `{report['candidate_workspace']['workspace']}`",
        f"- exists: `{report['candidate_workspace']['exists']}`",
    ])
    if report["candidate_workspace"]["non_scaffold_files"]:
        lines.extend(f"- `{path}`" for path in report["candidate_workspace"]["non_scaffold_files"])
    else:
        lines.append("- no non-scaffold files found")
    lines.extend([
        "",
        "## Refused Claim",
        "",
        report["claim_boundary"]["not_allowed"],
        "",
    ])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_discovery()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print("converter_post_layout_real_artifact_discovery")
    print(f"status,{report['status']}")
    print(f"current_candidate_would_write_accepted_evidence,{report['current_candidate_would_write_accepted_evidence']}")
    print(f"current_candidate_strict_issue_count,{report['current_candidate_strict_issue_count']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
