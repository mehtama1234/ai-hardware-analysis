#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from audit_converter_post_layout_candidate_workspace import build_audit
from preflight_converter_post_layout_payload import build_report as build_preflight


ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "evidence" / "aimc-simulator-adapters" / "candidate-post-layout" / "payload.json"
WORKSPACE = PAYLOAD.parent
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-blocker-ledger.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-blocker-ledger.md"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"missing required artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def evidence_action(category: str, message: str) -> str:
    if category == "missing_file":
        if "extracted_netlist" in message:
            return "Place the extracted post-layout converter netlist in the candidate netlist folder and point extraction.extracted_netlist at it."
        if "model_files" in message:
            return "Place the process, parasitic, or measurement model file in the candidate models folder and list it in simulation.model_files."
        if "rerun_artifact" in message:
            return "Run the source break-even calculation with the extracted values and place the resulting JSON in the candidate rerun folder."
        return "Supply the referenced file and keep the payload path inspectable."
    if category == "numeric_boundary":
        return "Replace the placeholder with a numeric value from the same post-layout simulation or measured run."
    if category == "noise_boundary":
        return "Use the measured or simulated readout noise from the same converter path and keep output_noise_rms at or below 0.004."
    if category == "sharing_boundary":
        return "Keep the sharing rule matched to 64 rows, 4 columns, 4 converter instances, and 16 outputs per conversion cost."
    if category == "missing_field":
        return "Add the missing payload field from the schema before preflight or submission."
    return "Fix the claim boundary so the payload says only what the evidence can support."


def build_ledger() -> dict[str, Any]:
    audit = build_audit(WORKSPACE)
    preflight = build_preflight(PAYLOAD)
    handoff = load_json(ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-handoff-manifest.json")

    blockers: list[dict[str, Any]] = []
    for item in audit.get("placeholders", []):
        if not isinstance(item, dict):
            continue
        blockers.append({
            "source": "workspace_audit",
            "category": "placeholder",
            "field": item.get("field"),
            "current_value": item.get("value"),
            "why_it_blocks": "A placeholder is a promise to fill evidence later, not evidence.",
            "evidence_action": "Replace this field with a real value from the extracted simulation or measured silicon run.",
        })
    for item in audit.get("missing_or_unresolved_files", []):
        if not isinstance(item, dict):
            continue
        blockers.append({
            "source": "workspace_audit",
            "category": "missing_file",
            "field": item.get("kind"),
            "current_value": item.get("path"),
            "why_it_blocks": "The payload cannot be inspected if the named evidence file is absent.",
            "evidence_action": evidence_action("missing_file", str(item.get("kind"))),
        })
    for issue in preflight.get("issues", []):
        if not isinstance(issue, dict):
            continue
        category = str(issue.get("category"))
        message = str(issue.get("message"))
        blockers.append({
            "source": "strict_preflight",
            "category": category,
            "field": message.split(" must ", 1)[0].replace("missing ", ""),
            "current_value": message,
            "why_it_blocks": "Strict preflight rejects payloads whose numbers, files, or boundaries cannot support a replacement decision.",
            "evidence_action": evidence_action(category, message),
        })

    unique: dict[tuple[str, str, str], dict[str, Any]] = {}
    for blocker in blockers:
        key = (str(blocker["source"]), str(blocker["category"]), str(blocker["current_value"]))
        unique.setdefault(key, blocker)
    blocker_list = list(unique.values())
    by_category: dict[str, int] = {}
    for blocker in blocker_list:
        category = str(blocker["category"])
        by_category[category] = by_category.get(category, 0) + 1

    return {
        "result_type": "converter_post_layout_blocker_ledger",
        "status": "blocked_on_real_post_layout_evidence" if blocker_list else "ready_for_strict_submission",
        "payload": rel(PAYLOAD),
        "workspace": rel(WORKSPACE),
        "source_handoff_manifest": rel(ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-handoff-manifest.json"),
        "source_candidate_payload": rel(PAYLOAD),
        "preflight_status": preflight.get("status"),
        "template_only": audit.get("template_only"),
        "blocker_count": len(blocker_list),
        "blockers_by_category": by_category,
        "blockers": blocker_list,
        "fixed_target_boundary": handoff.get("fixed_target_boundary"),
        "next_command": "python3 scripts/run_converter_post_layout_candidate_readiness.py",
        "claim_boundary": {
            "allowed": "shows every current blocker that prevents strict post-layout converter submission",
            "not_allowed": "does not supply extracted files, measured values, accepted post-layout evidence, or analog replacement proof",
        },
    }


def write_markdown(ledger: dict[str, Any]) -> None:
    lines = [
        "# Converter Post-Layout Blocker Ledger",
        "",
        f"- status: `{ledger['status']}`",
        f"- payload: `{ledger['payload']}`",
        f"- preflight status: `{ledger['preflight_status']}`",
        f"- template only: `{ledger['template_only']}`",
        f"- blocker count: `{ledger['blocker_count']}`",
        "",
        "This ledger is the current reason the converter cannot be accepted as post-layout evidence. It reads the candidate workspace and strict preflight result, then turns each failure into a concrete evidence action.",
        "",
        "## First Principle",
        "",
        "A converter claim is not made true by a payload shape. It becomes testable only when a value is tied to a physical object. The physical objects are the extracted netlist, the model files, and the break-even rerun artifact. The values are energy, time, noise, area, supply, temperature, and the replace-or-fallback decision.",
        "",
        "Until those objects and values are real, the right answer is not a weaker claim. The right answer is a clear list of blockers.",
        "",
        "## Blockers By Category",
        "",
    ]
    for category, count in sorted(ledger["blockers_by_category"].items()):
        lines.append(f"- `{category}`: `{count}`")
    lines.extend(["", "## Current Blockers", ""])
    for blocker in ledger["blockers"]:
        lines.extend([
            f"### {blocker['field']}",
            "",
            f"- source: `{blocker['source']}`",
            f"- category: `{blocker['category']}`",
            f"- current value: `{blocker['current_value']}`",
            f"- why it blocks: {blocker['why_it_blocks']}",
            f"- evidence action: {blocker['evidence_action']}",
            "",
        ])
    lines.extend([
        "## Fixed Target Boundary",
        "",
        *[f"- {key}: `{value}`" for key, value in (ledger.get("fixed_target_boundary") or {}).items()],
        "",
        "## Next Command",
        "",
        f"`{ledger['next_command']}`",
        "",
        "## Refused Claim",
        "",
        ledger["claim_boundary"]["not_allowed"],
        "",
    ])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ledger = build_ledger()
    OUT_JSON.write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(ledger)
    print("converter_post_layout_blocker_ledger")
    print(f"status,{ledger['status']}")
    print(f"blocker_count,{ledger['blocker_count']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")


if __name__ == "__main__":
    main()
