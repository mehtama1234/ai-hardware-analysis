#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from validate_converter_post_layout_same_run import validate_same_run


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PAYLOAD = ROOT / "evidence" / "aimc-simulator-adapters" / "candidate-post-layout" / "payload.json"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-identity-initializer.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-identity-initializer.md"
RUN_ID_SECTIONS = ["simulation", "energy", "latency", "noise", "area", "break_even_rerun"]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def apply_identity(
    payload: dict[str, Any],
    *,
    run_id: str,
    converter_id: str,
    operator: str,
    notebook: str,
    netlist: str,
    model_file: str,
    rerun_artifact: str,
) -> dict[str, Any]:
    updated = json.loads(json.dumps(payload))
    updated["converter_id"] = converter_id
    updated.setdefault("extraction", {})["extracted_netlist"] = netlist
    updated.setdefault("simulation", {})["model_files"] = [model_file]
    updated.setdefault("break_even_rerun", {})["rerun_artifact"] = rerun_artifact
    for section in RUN_ID_SECTIONS:
        updated.setdefault(section, {})["run_id"] = run_id
    provenance = updated.setdefault("provenance", {})
    provenance["run_id"] = run_id
    provenance["created_at"] = datetime.now(timezone.utc).isoformat()
    provenance["operator"] = operator
    provenance["generator_or_lab_notebook"] = notebook
    return updated


def build_report(payload_path: Path, apply: bool, output_payload: Path | None, updated_payload: dict[str, Any]) -> dict[str, Any]:
    same_run_issues = validate_same_run(updated_payload)
    identity_issues = [issue for issue in same_run_issues if issue != "template payloads cannot pass same-run consistency"]
    return {
        "result_type": "converter_post_layout_candidate_identity_initializer",
        "status": "identity_initializer_ready",
        "source_payload": str(payload_path.relative_to(ROOT)) if payload_path.is_relative_to(ROOT) else str(payload_path),
        "applied_to_source_payload": apply,
        "output_payload": str(output_payload.relative_to(ROOT)) if output_payload and output_payload.is_relative_to(ROOT) else str(output_payload) if output_payload else None,
        "same_run_identity_validation_passed_after_identity_fill": not identity_issues,
        "strict_same_run_validation_passed_after_identity_fill": not same_run_issues,
        "same_run_issues_after_identity_fill": same_run_issues,
        "same_run_identity_issues_after_identity_fill": identity_issues,
        "fields_initialized": [
            "converter_id",
            "extraction.extracted_netlist",
            "simulation.model_files[0]",
            "break_even_rerun.rerun_artifact",
            "provenance.created_at",
            "provenance.generator_or_lab_notebook",
            "provenance.operator",
            "provenance.run_id",
            "simulation.run_id",
            "energy.run_id",
            "latency.run_id",
            "noise.run_id",
            "area.run_id",
            "break_even_rerun.run_id",
        ],
        "remaining_boundary": "numeric evidence values and referenced files still have to be real before strict submission can pass",
        "claim_boundary": {
            "allowed": "fills consistent candidate identity, file names, provenance metadata, and shared run id when a real run exists",
            "not_allowed": "does not invent numeric post-layout values, does not create referenced files, does not remove template_only, and does not write accepted evidence",
        },
    }


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# Converter Post-Layout Candidate Identity Initializer",
        "",
        f"- status: `{report['status']}`",
        f"- source payload: `{report['source_payload']}`",
        f"- applied to source payload: `{report['applied_to_source_payload']}`",
        f"- same-run identity validation passed after identity fill: `{report['same_run_identity_validation_passed_after_identity_fill']}`",
        f"- strict same-run validation passed after identity fill: `{report['strict_same_run_validation_passed_after_identity_fill']}`",
        "",
        "This helper exists to reduce one specific manual error: using different names for the same run in different payload sections.",
        "",
        "## First Principle",
        "",
        "The first safe edit to a candidate package is identity, not performance. Identity says which converter was run, which files belong to that run, who or what produced it, and what single run id ties the sections together.",
        "",
        "This still does not make the payload evidence. Energy, latency, noise, area, extracted files, model files, and the source rerun artifact must still be real before strict submission can pass.",
        "",
        "## Fields Initialized",
        "",
        *[f"- `{field}`" for field in report["fields_initialized"]],
        "",
        "## Remaining Boundary",
        "",
        report["remaining_boundary"],
        "",
        "## Refused Claim",
        "",
        report["claim_boundary"]["not_allowed"],
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def run_self_test() -> None:
    source = load_json(DEFAULT_PAYLOAD)
    with tempfile.TemporaryDirectory(prefix="aimc-candidate-identity-") as tmp:
        payload_path = Path(tmp) / "payload.json"
        shutil.copy2(DEFAULT_PAYLOAD, payload_path)
        updated = apply_identity(
            source,
            run_id="identity-initializer-self-test-run",
            converter_id="identity-initializer-self-test-converter",
            operator="local self-test",
            notebook="scripts/initialize_converter_post_layout_candidate_identity.py --self-test",
            netlist="netlist/identity-initializer-self-test.sp",
            model_file="models/identity-initializer-self-test-model.sp",
            rerun_artifact="rerun/identity-initializer-self-test-rerun.json",
        )
        write_json(payload_path, updated)
        report = build_report(DEFAULT_PAYLOAD, False, None, updated)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    if not report["same_run_identity_validation_passed_after_identity_fill"]:
        raise SystemExit("identity initializer self-test failed same-run identity validation")
    print("converter_post_layout_candidate_identity_initializer")
    print(f"status,{report['status']}")
    print(f"same_run_identity_validation_passed,{report['same_run_identity_validation_passed_after_identity_fill']}")
    print(f"strict_same_run_validation_passed,{report['strict_same_run_validation_passed_after_identity_fill']}")
    print(f"applied_to_source_payload,{report['applied_to_source_payload']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize candidate post-layout identity fields with one shared run id.")
    parser.add_argument("--payload", type=Path, default=DEFAULT_PAYLOAD)
    parser.add_argument("--run-id")
    parser.add_argument("--converter-id")
    parser.add_argument("--operator")
    parser.add_argument("--notebook")
    parser.add_argument("--netlist")
    parser.add_argument("--model-file")
    parser.add_argument("--rerun-artifact")
    parser.add_argument("--output-payload", type=Path)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return 0
    required = ["run_id", "converter_id", "operator", "notebook", "netlist", "model_file", "rerun_artifact"]
    missing = [name.replace("_", "-") for name in required if not getattr(args, name)]
    if missing:
        raise SystemExit(f"missing required arguments: {', '.join(missing)}")
    payload_path = args.payload.resolve()
    source = load_json(payload_path)
    updated = apply_identity(
        source,
        run_id=args.run_id,
        converter_id=args.converter_id,
        operator=args.operator,
        notebook=args.notebook,
        netlist=args.netlist,
        model_file=args.model_file,
        rerun_artifact=args.rerun_artifact,
    )
    output = payload_path if args.apply else args.output_payload
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        write_json(output, updated)
    report = build_report(payload_path, args.apply, output, updated)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print("converter_post_layout_candidate_identity_initializer")
    print(f"status,{report['status']}")
    print(f"same_run_identity_validation_passed,{report['same_run_identity_validation_passed_after_identity_fill']}")
    print(f"strict_same_run_validation_passed,{report['strict_same_run_validation_passed_after_identity_fill']}")
    print(f"applied_to_source_payload,{report['applied_to_source_payload']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
