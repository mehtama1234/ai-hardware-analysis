#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "evidence" / "aimc-simulator-adapters" / "candidate-post-layout"
ACCEPTED = ROOT / "evidence" / "aimc-simulator-adapters" / "accepted-post-layout"
BUILDER = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-real-candidate-builder.json"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-evidence-leakage-audit.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-evidence-leakage-audit.md"


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def candidate_files() -> list[Path]:
    if not CANDIDATE.exists():
        return []
    return sorted(path for path in CANDIDATE.rglob("*") if path.is_file())


def main() -> None:
    files = candidate_files()
    non_scaffold_files = [
        path
        for path in files
        if path.name != ".gitkeep" and path.relative_to(CANDIDATE).as_posix() not in {"payload.json", "README.md"}
    ]
    temp_markers = ["/tmp/aimc-real-candidate-builder", "temporary self-test payload removed", "temporary self-test workspace removed"]
    candidate_temp_hits: list[dict[str, str]] = []
    for path in files:
        text = read_text(path)
        for marker in temp_markers:
            if marker in text:
                candidate_temp_hits.append({"file": rel(path), "marker": marker})

    builder = load_json(BUILDER)
    builder_temp_paths_are_labeled = (
        builder.get("self_test") is True
        and builder.get("temporary_fixture_persisted") is False
        and builder.get("candidate_payload") == "temporary self-test payload removed"
        and builder.get("workspace") == "temporary self-test workspace removed"
    )
    preview_ready_before_removal = (
        builder.get("preview_status_before_removal") == "ready_to_submit_without_writing"
        and builder.get("preview_would_write_accepted_evidence_before_removal") is True
        and builder.get("preview_strict_issue_count_before_removal") == 0
    )
    issues: list[str] = []
    if ACCEPTED.exists():
        issues.append("accepted-post-layout directory exists before real submission")
    if non_scaffold_files:
        issues.append("candidate workspace contains non-scaffold files")
    if candidate_temp_hits:
        issues.append("candidate workspace contains temporary self-test markers")
    if not builder_temp_paths_are_labeled:
        issues.append("builder self-test temporary paths are not labeled as removed")
    if not preview_ready_before_removal:
        issues.append("builder self-test did not prove preview-ready temporary package")

    report = {
        "result_type": "converter_post_layout_evidence_leakage_audit",
        "status": "no_evidence_leakage_detected" if not issues else "evidence_leakage_risk_detected",
        "accepted_post_layout_exists": ACCEPTED.exists(),
        "candidate_file_count": len(files),
        "candidate_non_scaffold_file_count": len(non_scaffold_files),
        "candidate_non_scaffold_files": [rel(path) for path in non_scaffold_files],
        "candidate_temp_marker_hit_count": len(candidate_temp_hits),
        "candidate_temp_marker_hits": candidate_temp_hits,
        "builder_temp_paths_are_labeled": builder_temp_paths_are_labeled,
        "builder_preview_ready_before_removal": preview_ready_before_removal,
        "issue_count": len(issues),
        "issues": issues,
        "claim_boundary": {
            "allowed": "checks that temporary builder fixtures and accepted-evidence previews did not leak into canonical evidence locations",
            "not_allowed": "does not prove real post-layout evidence exists and does not submit accepted evidence",
        },
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Converter Post-Layout Evidence Leakage Audit",
        "",
        f"- status: `{report['status']}`",
        f"- accepted post-layout exists: `{report['accepted_post_layout_exists']}`",
        f"- candidate file count: `{report['candidate_file_count']}`",
        f"- candidate non-scaffold file count: `{report['candidate_non_scaffold_file_count']}`",
        f"- candidate temp marker hit count: `{report['candidate_temp_marker_hit_count']}`",
        f"- builder temp paths are labeled: `{report['builder_temp_paths_are_labeled']}`",
        f"- builder preview ready before removal: `{report['builder_preview_ready_before_removal']}`",
        f"- issue count: `{report['issue_count']}`",
        "",
        "This audit protects the line between a test fixture and evidence. A temporary builder package may prove that the mechanics work. It must not leave files in the canonical candidate workspace, and it must not create accepted evidence.",
        "",
        "## First Principle",
        "",
        "A proof helper is allowed to make temporary objects. It is not allowed to make those objects look like real converter evidence. The evidence folder should show only two states: a scaffold waiting for real files, or accepted evidence written by the strict submitter after a real package passes.",
        "",
        "## Issues",
        "",
    ]
    if issues:
        lines.extend(f"- {issue}" for issue in issues)
    else:
        lines.append("- none")
    lines.extend([
        "",
        "## Refused Claim",
        "",
        report["claim_boundary"]["not_allowed"],
        "",
    ])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    if issues:
        raise SystemExit("converter post-layout evidence leakage risk detected")
    print("converter_post_layout_evidence_leakage_audit")
    print(f"status,{report['status']}")
    print(f"accepted_post_layout_exists,{report['accepted_post_layout_exists']}")
    print(f"candidate_non_scaffold_file_count,{report['candidate_non_scaffold_file_count']}")
    print(f"candidate_temp_marker_hit_count,{report['candidate_temp_marker_hit_count']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")


if __name__ == "__main__":
    main()
