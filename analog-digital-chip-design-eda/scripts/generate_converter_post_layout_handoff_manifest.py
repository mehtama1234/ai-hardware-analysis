#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-real-payload-package.json"
CHECKLIST = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-fill-checklist.json"
READINESS = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-readiness-run.json"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-handoff-manifest.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-handoff-manifest.md"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"missing required artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    package = load_json(PACKAGE)
    checklist = load_json(CHECKLIST)
    readiness = load_json(READINESS)
    items = checklist.get("items") if isinstance(checklist.get("items"), list) else []
    files = [
        {
            "name": item.get("field"),
            "current_path": item.get("current_value"),
            "what_to_supply": item.get("what_to_supply"),
        }
        for item in items
        if isinstance(item, dict) and item.get("group") == "files"
    ]
    numeric_fields = [
        {
            "field": item.get("field"),
            "current_value": item.get("current_value"),
            "what_to_supply": item.get("what_to_supply"),
        }
        for item in items
        if isinstance(item, dict) and item.get("group") in {"energy", "latency", "noise", "area", "simulation"}
    ]
    identity_fields = [
        {
            "field": item.get("field"),
            "current_value": item.get("current_value"),
            "what_to_supply": item.get("what_to_supply"),
        }
        for item in items
        if isinstance(item, dict) and item.get("group") in {"identity", "extraction", "break_even", "provenance"}
    ]
    fixed_boundary = package.get("fixed_target_boundary") if isinstance(package.get("fixed_target_boundary"), dict) else {}
    commands = readiness.get("commands") if isinstance(readiness.get("commands"), dict) else {}
    manifest = {
        "result_type": "converter_post_layout_handoff_manifest",
        "status": "handoff_manifest_ready",
        "source_package": str(PACKAGE.relative_to(ROOT)),
        "source_checklist": str(CHECKLIST.relative_to(ROOT)),
        "source_readiness_run": str(READINESS.relative_to(ROOT)),
        "current_candidate_status": readiness.get("status"),
        "ready_for_strict_submission": readiness.get("ready_for_strict_submission"),
        "missing_files": files,
        "numeric_values_to_supply": numeric_fields,
        "identity_and_provenance_to_supply": identity_fields,
        "required_file_count": len(files),
        "numeric_value_count": len(numeric_fields),
        "identity_and_provenance_count": len(identity_fields),
        "fixed_target_boundary": fixed_boundary,
        "commands": {
            "fill_workspace": "edit evidence/aimc-simulator-adapters/candidate-post-layout/payload.json and place files under netlist/, models/, and rerun/",
            "readiness": "python3 scripts/run_converter_post_layout_candidate_readiness.py",
            "submit_if_ready": commands.get("submit_if_ready"),
        },
        "claim_boundary": {
            "allowed": "names the concrete files, values, fixed boundary, and commands needed for a real post-layout handoff",
            "not_allowed": "does not provide the real files or values, does not submit evidence, and does not prove analog replacement",
        },
    }
    OUT_JSON.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Converter Post-Layout Handoff Manifest",
        "",
        f"- status: `{manifest['status']}`",
        f"- current candidate status: `{manifest['current_candidate_status']}`",
        f"- ready for strict submission: `{manifest['ready_for_strict_submission']}`",
        f"- required file count: `{manifest['required_file_count']}`",
        f"- numeric value count: `{manifest['numeric_value_count']}`",
        f"- identity and provenance count: `{manifest['identity_and_provenance_count']}`",
        "",
        "This manifest is the handoff sheet for the person or tool that will produce real converter evidence. It names the files to place in the workspace, the numbers to put in the payload, the fixed target boundary, and the commands to run after filling it.",
        "",
        "## First Principle",
        "",
        "A handoff is useful only when the receiver can act without guessing. The converter evidence packet needs inspectable objects and concrete values. The objects are the extracted netlist, model files, and source rerun artifact. The values are energy, latency, noise, area, supply, temperature, and the replacement decision.",
        "",
        "The manifest does not lower the evidence bar. It makes the bar easy to see.",
        "",
        "## Missing Files",
        "",
    ]
    lines.extend(f"- `{item['name']}`: `{item['current_path']}`" for item in files)
    lines.extend(["", "## Numeric Values", ""])
    lines.extend(f"- `{item['field']}`: {item['what_to_supply']}" for item in numeric_fields)
    lines.extend(["", "## Identity And Provenance", ""])
    lines.extend(f"- `{item['field']}`: {item['what_to_supply']}" for item in identity_fields)
    lines.extend([
        "",
        "## Fixed Target Boundary",
        "",
        *[f"- {key}: `{value}`" for key, value in fixed_boundary.items()],
        "",
        "## Commands",
        "",
        *[f"- {name}: `{command}`" for name, command in manifest["commands"].items()],
        "",
        "## Refused Claim",
        "",
        manifest["claim_boundary"]["not_allowed"],
        "",
    ])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print("converter_post_layout_handoff_manifest")
    print(f"status,{manifest['status']}")
    print(f"required_file_count,{manifest['required_file_count']}")
    print(f"numeric_value_count,{manifest['numeric_value_count']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")


if __name__ == "__main__":
    main()
