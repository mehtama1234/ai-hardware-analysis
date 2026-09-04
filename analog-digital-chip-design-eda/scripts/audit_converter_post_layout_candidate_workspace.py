#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WORKSPACE = ROOT / "evidence" / "aimc-simulator-adapters" / "candidate-post-layout"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-workspace-audit.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-workspace-audit.md"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def walk_values(value: Any, prefix: str = "") -> list[tuple[str, Any]]:
    if isinstance(value, dict):
        out: list[tuple[str, Any]] = []
        for key, child in value.items():
            child_prefix = f"{prefix}.{key}" if prefix else key
            out.extend(walk_values(child, child_prefix))
        return out
    if isinstance(value, list):
        out = []
        for index, child in enumerate(value):
            out.extend(walk_values(child, f"{prefix}[{index}]"))
        return out
    return [(prefix, value)]


def is_placeholder(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    lower = value.lower()
    return "replace-with" in lower or "replace_with" in lower


def resolve(workspace: Path, maybe_path: Any) -> Path | None:
    if not isinstance(maybe_path, str) or not maybe_path.strip():
        return None
    path = Path(maybe_path)
    return path if path.is_absolute() else workspace / path


def build_audit(workspace: Path) -> dict[str, Any]:
    payload_path = workspace / "payload.json"
    readme_path = workspace / "README.md"
    payload = load_json(payload_path) if payload_path.exists() else {}
    placeholders = [
        {"field": field, "value": value}
        for field, value in walk_values(payload)
        if is_placeholder(value)
    ]
    netlist = resolve(workspace, (payload.get("extraction") or {}).get("extracted_netlist") if isinstance(payload.get("extraction"), dict) else None)
    models = (payload.get("simulation") or {}).get("model_files") if isinstance(payload.get("simulation"), dict) else []
    model_paths = [resolve(workspace, item) for item in models] if isinstance(models, list) else []
    rerun = resolve(workspace, (payload.get("break_even_rerun") or {}).get("rerun_artifact") if isinstance(payload.get("break_even_rerun"), dict) else None)
    required_paths = [
        {"kind": "payload", "path": payload_path, "exists": payload_path.is_file()},
        {"kind": "readme", "path": readme_path, "exists": readme_path.is_file()},
        {"kind": "netlist", "path": netlist, "exists": bool(netlist and netlist.is_file())},
        *[
            {"kind": f"model_file_{index}", "path": path, "exists": bool(path and path.is_file())}
            for index, path in enumerate(model_paths)
        ],
        {"kind": "rerun_artifact", "path": rerun, "exists": bool(rerun and rerun.is_file())},
    ]
    unresolved = [item for item in required_paths if not item["exists"]]
    template_only = payload.get("template_only") is True
    ready = bool(payload_path.exists()) and not template_only and not placeholders and not unresolved
    return {
        "result_type": "converter_post_layout_candidate_workspace_audit",
        "status": "candidate_workspace_ready_for_preflight" if ready else "candidate_workspace_still_scaffold",
        "workspace": str(workspace.relative_to(ROOT)) if workspace.is_relative_to(ROOT) else str(workspace),
        "payload": str(payload_path.relative_to(ROOT)) if payload_path.is_relative_to(ROOT) else str(payload_path),
        "template_only": template_only,
        "placeholder_count": len(placeholders),
        "placeholders": placeholders,
        "missing_or_unresolved_file_count": len(unresolved),
        "missing_or_unresolved_files": [
            {
                "kind": item["kind"],
                "path": str(item["path"].relative_to(ROOT)) if isinstance(item["path"], Path) and item["path"].is_relative_to(ROOT) else str(item["path"]),
            }
            for item in unresolved
        ],
        "next_command": f"python3 scripts/preflight_converter_post_layout_payload.py {payload_path.relative_to(ROOT) if payload_path.is_relative_to(ROOT) else payload_path}",
        "claim_boundary": {
            "allowed": "reports whether the candidate workspace still contains placeholders or missing referenced files",
            "not_allowed": "does not validate physics, does not submit evidence, and does not replace converter break-even assumptions",
        },
    }


def write_markdown(audit: dict[str, Any], output: Path) -> None:
    lines = [
        "# Converter Post-Layout Candidate Workspace Audit",
        "",
        f"- status: `{audit['status']}`",
        f"- workspace: `{audit['workspace']}`",
        f"- payload: `{audit['payload']}`",
        f"- template only: `{audit['template_only']}`",
        f"- placeholder count: `{audit['placeholder_count']}`",
        f"- missing or unresolved file count: `{audit['missing_or_unresolved_file_count']}`",
        "",
        "This audit tells whether the staging folder is still a scaffold or is ready for preflight.",
        "",
        "## First Principle",
        "",
        "A candidate workspace becomes useful only when every name points to a real object. A placeholder field means the payload is still an intention. A missing file means the payload cannot be inspected. A `template_only` flag means the packet is deliberately barred from submission.",
        "",
        "The audit does not judge whether the converter is good. It only asks whether the packet has stopped being a scaffold.",
        "",
        "## Placeholder Fields",
        "",
    ]
    if audit["placeholders"]:
        for item in audit["placeholders"][:20]:
            lines.append(f"- `{item['field']}`: `{item['value']}`")
        if len(audit["placeholders"]) > 20:
            lines.append(f"- plus `{len(audit['placeholders']) - 20}` more")
    else:
        lines.append("- none")
    lines.extend(["", "## Missing Or Unresolved Files", ""])
    if audit["missing_or_unresolved_files"]:
        for item in audit["missing_or_unresolved_files"]:
            lines.append(f"- `{item['kind']}`: `{item['path']}`")
    else:
        lines.append("- none")
    lines.extend([
        "",
        "## Next Command",
        "",
        f"`{audit['next_command']}`",
        "",
        "## Refused Claim",
        "",
        audit["claim_boundary"]["not_allowed"],
        "",
    ])
    output.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit the converter post-layout candidate workspace.")
    parser.add_argument("--workspace", type=Path, default=DEFAULT_WORKSPACE)
    parser.add_argument("--json-output", type=Path, default=OUT_JSON)
    parser.add_argument("--markdown-output", type=Path, default=OUT_MD)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    workspace = args.workspace.resolve()
    audit = build_audit(workspace)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    write_markdown(audit, args.markdown_output)
    print("converter_post_layout_candidate_workspace_audit")
    print(f"status,{audit['status']}")
    print(f"placeholders,{audit['placeholder_count']}")
    print(f"missing_or_unresolved_files,{audit['missing_or_unresolved_file_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
