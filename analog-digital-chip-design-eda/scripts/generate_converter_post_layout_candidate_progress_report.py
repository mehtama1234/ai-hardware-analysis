#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
AUDIT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-workspace-audit.json"
CHECKLIST_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-fill-checklist.json"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-progress-report.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-progress-report.md"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"missing required artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    audit = load_json(AUDIT_JSON)
    checklist = load_json(CHECKLIST_JSON)
    open_items = checklist.get("items") if isinstance(checklist.get("items"), list) else []
    groups = checklist.get("groups") if isinstance(checklist.get("groups"), list) else []
    placeholder_count = int(audit.get("placeholder_count") or 0)
    missing_file_count = int(audit.get("missing_or_unresolved_file_count") or 0)
    template_only = audit.get("template_only") is True
    ready_for_preflight = (
        audit.get("status") == "candidate_workspace_ready_for_preflight"
        and not template_only
        and placeholder_count == 0
        and missing_file_count == 0
        and not open_items
    )
    status = "candidate_ready_for_preflight" if ready_for_preflight else "candidate_waiting_for_real_values"
    report = {
        "result_type": "converter_post_layout_candidate_progress_report",
        "status": status,
        "workspace": audit.get("workspace"),
        "payload": audit.get("payload"),
        "source_audit": str(AUDIT_JSON.relative_to(ROOT)),
        "source_checklist": str(CHECKLIST_JSON.relative_to(ROOT)),
        "template_only": template_only,
        "placeholder_count": placeholder_count,
        "missing_or_unresolved_file_count": missing_file_count,
        "open_checklist_items": len(open_items),
        "open_groups": groups,
        "ready_for_preflight": ready_for_preflight,
        "next_commands": [
            "python3 scripts/audit_converter_post_layout_candidate_workspace.py",
            "python3 scripts/generate_converter_post_layout_candidate_fill_checklist.py",
            f"python3 scripts/preflight_converter_post_layout_payload.py {audit.get('payload')}",
        ],
        "claim_boundary": {
            "allowed": "summarizes whether the candidate package is still an editable scaffold or ready for preflight",
            "not_allowed": "does not supply real post-layout values, does not validate circuit physics, and does not submit accepted converter evidence",
        },
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Converter Post-Layout Candidate Progress Report",
        "",
        f"- status: `{report['status']}`",
        f"- workspace: `{report['workspace']}`",
        f"- payload: `{report['payload']}`",
        f"- template only: `{report['template_only']}`",
        f"- placeholder count: `{report['placeholder_count']}`",
        f"- missing or unresolved file count: `{report['missing_or_unresolved_file_count']}`",
        f"- open checklist items: `{report['open_checklist_items']}`",
        f"- ready for preflight: `{report['ready_for_preflight']}`",
        "",
        "This report is the short answer for the candidate package. It reads the workspace audit and the fill checklist, then says whether the packet is still a scaffold or ready for preflight.",
        "",
        "## First Principle",
        "",
        "A post-layout converter claim needs two things at once: numbers and objects. The numbers are energy, latency, noise, area, voltage, temperature, and the replace-or-fallback decision. The objects are the netlist, model files, and rerun artifact that let someone inspect where those numbers came from.",
        "",
        "If either side is missing, the packet is not almost evidence. It is still an editable packet. This report keeps that boundary visible.",
        "",
        "## Open Groups",
        "",
    ]
    if groups:
        lines.extend(f"- `{group}`" for group in groups)
    else:
        lines.append("- none")
    lines.extend([
        "",
        "## Next Commands",
        "",
        *[f"- `{command}`" for command in report["next_commands"]],
        "",
        "## Refused Claim",
        "",
        report["claim_boundary"]["not_allowed"],
        "",
    ])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print("converter_post_layout_candidate_progress_report")
    print(f"status,{report['status']}")
    print(f"open_checklist_items,{report['open_checklist_items']}")
    print(f"ready_for_preflight,{report['ready_for_preflight']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")


if __name__ == "__main__":
    main()
