#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RECIPE = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-real-run-recipe.json"
CHECKLIST = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-fill-checklist.json"
BLOCKERS = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-blocker-ledger.json"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-real-run-recipe-coverage.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-real-run-recipe-coverage.md"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"missing required artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    recipe = load_json(RECIPE)
    checklist = load_json(CHECKLIST)
    blockers = load_json(BLOCKERS)
    recipe_fields = {
        str(field)
        for step in recipe.get("recipe_steps", [])
        if isinstance(step, dict)
        for field in step.get("payload_fields", [])
    }
    checklist_fields = {
        str(item.get("field"))
        for item in checklist.get("items", [])
        if isinstance(item, dict) and item.get("field")
    }
    blocker_items = [item for item in blockers.get("blockers", []) if isinstance(item, dict) and item.get("field")]
    blocker_fields = {str(item.get("field")) for item in blocker_items}
    non_field_boundary_blockers = sorted(
        str(item.get("field"))
        for item in blocker_items
        if item.get("category") == "claim_boundary" and str(item.get("field", "")).startswith("template payloads cannot")
    )
    payload_blocker_fields = blocker_fields - set(non_field_boundary_blockers)
    uncovered_checklist_fields = sorted(checklist_fields - recipe_fields)
    covered_blocker_fields = sorted(payload_blocker_fields & recipe_fields)
    uncovered_blocker_fields = sorted(payload_blocker_fields - recipe_fields)
    payload = {
        "result_type": "converter_post_layout_real_run_recipe_coverage",
        "status": "real_run_recipe_covers_current_checklist" if not uncovered_checklist_fields else "real_run_recipe_missing_checklist_fields",
        "source_recipe": str(RECIPE.relative_to(ROOT)),
        "source_checklist": str(CHECKLIST.relative_to(ROOT)),
        "source_blocker_ledger": str(BLOCKERS.relative_to(ROOT)),
        "recipe_field_count": len(recipe_fields),
        "checklist_field_count": len(checklist_fields),
        "blocker_field_count": len(blocker_fields),
        "payload_blocker_field_count": len(payload_blocker_fields),
        "non_field_boundary_blocker_count": len(non_field_boundary_blockers),
        "non_field_boundary_blockers": non_field_boundary_blockers,
        "covered_checklist_field_count": len(checklist_fields & recipe_fields),
        "uncovered_checklist_fields": uncovered_checklist_fields,
        "covered_blocker_field_count": len(covered_blocker_fields),
        "uncovered_blocker_field_count": len(uncovered_blocker_fields),
        "uncovered_blocker_fields": uncovered_blocker_fields,
        "claim_boundary": {
            "allowed": "checks that the generated real-run recipe covers the current candidate fill checklist",
            "not_allowed": "does not supply real post-layout files, measured values, accepted evidence, or analog replacement proof",
        },
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Converter Post-Layout Real Run Recipe Coverage",
        "",
        f"- status: `{payload['status']}`",
        f"- recipe field count: `{payload['recipe_field_count']}`",
        f"- checklist field count: `{payload['checklist_field_count']}`",
        f"- covered checklist field count: `{payload['covered_checklist_field_count']}`",
        f"- blocker field count: `{payload['blocker_field_count']}`",
        f"- payload blocker field count: `{payload['payload_blocker_field_count']}`",
        f"- non-field boundary blocker count: `{payload['non_field_boundary_blocker_count']}`",
        f"- covered blocker field count: `{payload['covered_blocker_field_count']}`",
        f"- uncovered blocker field count: `{payload['uncovered_blocker_field_count']}`",
        "",
        "This audit checks the recipe against the current checklist. The recipe is useful only if every checklist edit appears in at least one ordered step.",
        "",
        "## First Principle",
        "",
        "A run recipe can sound complete while still skipping a needed field. This audit removes that ambiguity. It compares the fields the candidate package still needs with the fields named by the ordered recipe.",
        "",
        "## Uncovered Checklist Fields",
        "",
    ]
    if uncovered_checklist_fields:
        lines.extend(f"- `{field}`" for field in uncovered_checklist_fields)
    else:
        lines.append("- none")
    lines.extend([
        "",
        "## Non-Field Boundary Blockers",
        "",
    ])
    if non_field_boundary_blockers:
        lines.extend(f"- `{field}`" for field in non_field_boundary_blockers)
    else:
        lines.append("- none")
    lines.extend([
        "",
        "## Uncovered Payload Blocker Fields",
        "",
    ])
    if uncovered_blocker_fields:
        lines.extend(f"- `{field}`" for field in uncovered_blocker_fields)
    else:
        lines.append("- none")
    lines.extend([
        "",
        "## Refused Claim",
        "",
        payload["claim_boundary"]["not_allowed"],
        "",
    ])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    if uncovered_checklist_fields:
        raise SystemExit("real-run recipe does not cover all checklist fields")
    print("converter_post_layout_real_run_recipe_coverage")
    print(f"status,{payload['status']}")
    print(f"covered_checklist_field_count,{payload['covered_checklist_field_count']}")
    print(f"uncovered_checklist_fields,{len(uncovered_checklist_fields)}")
    print(f"uncovered_blocker_field_count,{payload['uncovered_blocker_field_count']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")


if __name__ == "__main__":
    main()
