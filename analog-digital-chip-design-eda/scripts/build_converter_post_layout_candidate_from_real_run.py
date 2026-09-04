#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from preflight_converter_post_layout_payload import build_report as build_preflight_report
from preview_converter_post_layout_submission import build_report as build_preview_report
from submit_converter_post_layout_payload import DEFAULT_OUT_DIR
from validate_converter_post_layout_same_run import validate_same_run
from validate_converter_post_layout_payload import SCHEMA, load_json, validate_payload, validate_referenced_files


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "evidence" / "aimc-simulator-adapters" / "candidate-post-layout"
PAYLOAD = WORKSPACE / "payload.json"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-real-candidate-builder.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-real-candidate-builder.md"


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def copy_into(source: Path, target_dir: Path) -> Path:
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / source.name
    if source.resolve() != target.resolve():
        shutil.copy2(source, target)
    return target


def positive(value: float, name: str) -> float:
    if value <= 0:
        raise SystemExit(f"{name} must be positive")
    return value


def numeric_noise(value: float, name: str) -> float:
    if value < 0:
        raise SystemExit(f"{name} must be non-negative")
    return value


def payload_ref(path: Path, payload_path: Path) -> str:
    resolved = path.resolve()
    payload_dir = payload_path.resolve().parent
    return str(resolved.relative_to(payload_dir)) if resolved.is_relative_to(payload_dir) else rel(resolved)


def build_payload(args: argparse.Namespace, netlist: Path, model_file: Path, rerun_artifact: Path, payload_path: Path) -> dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    replacement_decision = args.replacement_decision
    return {
        "result_type": "converter_post_layout_evidence",
        "converter_id": args.converter_id,
        "measurement_level": args.measurement_level,
        "target_boundary": {
            "adc_bits": 12,
            "dac_bits": 10,
            "output_noise_budget": 0.004,
        },
        "extraction": {
            "extracted_netlist": payload_ref(netlist, payload_path),
            "parasitic_format": args.parasitic_format,
            "includes_row_dac": True,
            "includes_sar_readout": True,
            "includes_shared_mux": True,
            "includes_references": True,
            "includes_sample_path": True,
        },
        "simulation": {
            "simulator": args.simulator,
            "command": args.command,
            "process_corner": args.process_corner,
            "voltage_v": args.voltage_v,
            "temperature_c": args.temperature_c,
            "model_files": [payload_ref(model_file, payload_path)],
            "run_id": args.run_id,
        },
        "energy": {
            "adc_energy_per_conversion": args.adc_energy_per_conversion,
            "dac_energy_per_row_drive": args.dac_energy_per_row_drive,
            "energy_unit": "joule",
            "method": args.energy_method,
            "run_id": args.run_id,
        },
        "latency": {
            "adc_comparisons": 12,
            "conversion_time_ns": args.conversion_time_ns,
            "settling_time_ns": args.settling_time_ns,
            "method": args.latency_method,
            "run_id": args.run_id,
        },
        "noise": {
            "output_noise_rms": args.output_noise_rms,
            "input_referred_noise": args.input_referred_noise,
            "meets_output_noise_budget": args.output_noise_rms <= 0.004,
            "method": args.noise_method,
            "run_id": args.run_id,
        },
        "area": {
            "adc_area_um2": args.adc_area_um2,
            "dac_area_um2": args.dac_area_um2,
            "replication_or_sharing_rule": "64 rows, 4 columns, 4 converter instances, 16 outputs per conversion cost",
            "method": args.area_method,
            "run_id": args.run_id,
        },
        "sharing": {
            "rows_served": 64,
            "columns_served": 4,
            "outputs_per_conversion_cost": 16,
            "converter_instances": 4,
        },
        "break_even_rerun": {
            "rerun_artifact": payload_ref(rerun_artifact, payload_path),
            "uses_extracted_energy": True,
            "uses_extracted_latency": True,
            "uses_extracted_noise": True,
            "uses_extracted_area": True,
            "uses_same_sharing_rule": True,
            "replacement_decision": replacement_decision,
            "run_id": args.run_id,
        },
        "provenance": {
            "created_at": now,
            "generator_or_lab_notebook": args.notebook,
            "operator": args.operator,
            "source_schema": rel(SCHEMA),
            "run_id": args.run_id,
        },
        "claim_boundary": {
            "allowed": "candidate payload assembled from named real post-layout or measured-silicon files for strict preflight",
            "not_allowed": "does not write accepted evidence, does not bypass strict submission, and does not prove another converter or workload",
        },
    }


def validate_real_payload(payload: dict[str, Any], payload_path: Path) -> list[str]:
    schema = load_json(SCHEMA)
    issues = validate_payload(payload, schema)
    issues.extend(validate_referenced_files(payload, payload_path))
    issues.extend(validate_same_run(payload))
    if payload.get("template_only") is True:
        issues.append("template payloads cannot be submitted")
    return issues


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Converter Post-Layout Real Candidate Builder",
        "",
        f"- status: `{report['status']}`",
        f"- self-test: `{report['self_test']}`",
        f"- temporary fixture persisted: `{report['temporary_fixture_persisted']}`",
        f"- wrote payload: `{report['wrote_payload']}`",
        f"- candidate payload: `{report['candidate_payload']}`",
        f"- strict validation passed: `{report['strict_validation_passed']}`",
        f"- strict issue count: `{report['strict_issue_count']}`",
        f"- preview status before removal: `{report.get('preview_status_before_removal')}`",
        f"- preview would write accepted evidence before removal: `{report.get('preview_would_write_accepted_evidence_before_removal')}`",
        f"- preview strict issue count before removal: `{report.get('preview_strict_issue_count_before_removal')}`",
        "",
        "This builder turns a real run into the candidate payload shape used by preflight and strict submission.",
        "",
        "## First Principle",
        "",
        "A real run should be copied into the candidate workspace as a small packet: one payload, one extracted netlist, one model or measurement file, and one source rerun artifact. The payload should name one converter and one run id. The values should be numeric before the submitter is allowed to write accepted evidence.",
        "",
        "The builder can assemble that packet. It cannot make the files true. The files and numbers must already come from the post-layout simulation or measured-silicon run.",
        "",
        "## Copied Files",
        "",
        *[f"- `{path}`" for path in report["copied_files"]],
        "",
        "## Strict Issues",
        "",
    ]
    if report["strict_issues"]:
        lines.extend(f"- {issue}" for issue in report["strict_issues"])
    else:
        lines.append("- none")
    lines.extend([
        "",
        "## Next Command",
        "",
        f"`{report['next_command']}`",
        "",
        "## Refused Claim",
        "",
        report["claim_boundary"]["not_allowed"],
        "",
    ])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the candidate post-layout payload from real files and numeric converter terms.")
    parser.add_argument("--netlist", type=Path)
    parser.add_argument("--model-file", type=Path)
    parser.add_argument("--rerun-artifact", type=Path)
    parser.add_argument("--converter-id")
    parser.add_argument("--run-id")
    parser.add_argument("--measurement-level", choices=["post_layout_simulation", "measured_silicon"], default="post_layout_simulation")
    parser.add_argument("--parasitic-format")
    parser.add_argument("--simulator")
    parser.add_argument("--command")
    parser.add_argument("--process-corner")
    parser.add_argument("--voltage-v", type=float)
    parser.add_argument("--temperature-c", type=float)
    parser.add_argument("--adc-energy-per-conversion", type=float)
    parser.add_argument("--dac-energy-per-row-drive", type=float)
    parser.add_argument("--conversion-time-ns", type=float)
    parser.add_argument("--settling-time-ns", type=float)
    parser.add_argument("--output-noise-rms", type=float)
    parser.add_argument("--input-referred-noise", type=float)
    parser.add_argument("--adc-area-um2", type=float)
    parser.add_argument("--dac-area-um2", type=float)
    parser.add_argument("--replacement-decision", choices=["replace_converter_break_even_assumption", "keep_digital_fallback"])
    parser.add_argument("--energy-method")
    parser.add_argument("--latency-method")
    parser.add_argument("--noise-method")
    parser.add_argument("--area-method")
    parser.add_argument("--operator")
    parser.add_argument("--notebook")
    parser.add_argument("--workspace", type=Path, default=WORKSPACE)
    parser.add_argument("--output-payload", type=Path)
    parser.add_argument("--dry-run", action="store_true", help="Validate and report without writing the candidate payload.")
    parser.add_argument("--self-test", action="store_true", help="Build a complete temporary candidate package and verify strict validation without touching the canonical workspace.")
    return parser.parse_args()


def require_args(args: argparse.Namespace) -> None:
    required = [
        "netlist",
        "model_file",
        "rerun_artifact",
        "converter_id",
        "run_id",
        "parasitic_format",
        "simulator",
        "command",
        "process_corner",
        "voltage_v",
        "temperature_c",
        "adc_energy_per_conversion",
        "dac_energy_per_row_drive",
        "conversion_time_ns",
        "settling_time_ns",
        "output_noise_rms",
        "input_referred_noise",
        "adc_area_um2",
        "dac_area_um2",
        "replacement_decision",
        "energy_method",
        "latency_method",
        "noise_method",
        "area_method",
        "operator",
        "notebook",
    ]
    missing = [name.replace("_", "-") for name in required if getattr(args, name) is None]
    if missing:
        raise SystemExit(f"missing required arguments: {', '.join(missing)}")


def run_builder(args: argparse.Namespace) -> dict[str, Any]:
    require_args(args)
    for name in ["netlist", "model_file", "rerun_artifact"]:
        path = getattr(args, name).resolve()
        if not path.is_file():
            raise SystemExit(f"{name.replace('_', '-')} must point to an existing file: {path}")
    positive(args.voltage_v, "voltage-v")
    positive(args.adc_energy_per_conversion, "adc-energy-per-conversion")
    positive(args.dac_energy_per_row_drive, "dac-energy-per-row-drive")
    positive(args.conversion_time_ns, "conversion-time-ns")
    positive(args.settling_time_ns, "settling-time-ns")
    positive(args.adc_area_um2, "adc-area-um2")
    positive(args.dac_area_um2, "dac-area-um2")
    numeric_noise(args.output_noise_rms, "output-noise-rms")
    numeric_noise(args.input_referred_noise, "input-referred-noise")

    workspace = args.workspace.resolve()
    output_payload = args.output_payload.resolve() if args.output_payload else workspace / "payload.json"
    copied_netlist = copy_into(args.netlist.resolve(), workspace / "netlist")
    copied_model = copy_into(args.model_file.resolve(), workspace / "models")
    copied_rerun = copy_into(args.rerun_artifact.resolve(), workspace / "rerun")
    payload = build_payload(args, copied_netlist, copied_model, copied_rerun, output_payload)
    if not args.dry_run:
        output_payload.parent.mkdir(parents=True, exist_ok=True)
        output_payload.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    issues = validate_real_payload(payload, output_payload)
    preflight = build_preflight_report(output_payload) if output_payload.exists() else {"status": "not_run_dry_run_without_payload"}
    report = {
        "result_type": "converter_post_layout_real_candidate_builder",
        "status": "candidate_payload_built" if not args.dry_run and not issues else "candidate_payload_not_ready",
        "self_test": bool(getattr(args, "self_test", False)),
        "temporary_fixture_persisted": None,
        "wrote_payload": not args.dry_run,
        "candidate_payload": rel(output_payload),
        "copied_files": [rel(copied_netlist), rel(copied_model), rel(copied_rerun)],
        "strict_validation_passed": not issues,
        "strict_issue_count": len(issues),
        "strict_issues": issues,
        "preflight_status_after_write": preflight.get("status"),
        "workspace": rel(workspace),
        "next_command": f"python3 scripts/preview_converter_post_layout_submission.py --payload {rel(output_payload)}",
        "claim_boundary": {
            "allowed": "assembles a candidate payload from existing real files and numeric converter terms",
            "not_allowed": "does not write accepted evidence, does not bypass strict submission, and does not prove the input files came from silicon or layout",
        },
    }
    if getattr(args, "emit_report", True):
        write_report(report)
    return report


def run_self_test() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="aimc-real-candidate-builder-") as tmp:
        root = Path(tmp)
        source = root / "source"
        source.mkdir()
        netlist = source / "self-test-extracted.sp"
        model = source / "self-test-model.sp"
        rerun = source / "self-test-rerun.json"
        netlist.write_text("* self-test extracted netlist\n", encoding="utf-8")
        model.write_text(".model self_test_model nmos\n", encoding="utf-8")
        rerun.write_text(json.dumps({"result_type": "self_test_source_rerun", "run_id": "real-candidate-builder-self-test-run"}) + "\n", encoding="utf-8")
        args = argparse.Namespace(
            netlist=netlist,
            model_file=model,
            rerun_artifact=rerun,
            converter_id="real-candidate-builder-self-test-converter",
            run_id="real-candidate-builder-self-test-run",
            measurement_level="post_layout_simulation",
            parasitic_format="extracted-spice",
            simulator="ngspice",
            command="ngspice self-test-extracted.sp",
            process_corner="tt",
            voltage_v=0.8,
            temperature_c=25.0,
            adc_energy_per_conversion=1.0e-12,
            dac_energy_per_row_drive=1.0e-13,
            conversion_time_ns=5.0,
            settling_time_ns=2.0,
            output_noise_rms=0.001,
            input_referred_noise=0.001,
            adc_area_um2=1000.0,
            dac_area_um2=500.0,
            replacement_decision="keep_digital_fallback",
            energy_method="self-test integrated supply windows",
            latency_method="self-test threshold crossing",
            noise_method="self-test rms output noise",
            area_method="self-test extracted area",
            operator="local self-test",
            notebook="scripts/build_converter_post_layout_candidate_from_real_run.py --self-test",
            workspace=root / "candidate-post-layout",
            output_payload=None,
            dry_run=False,
            self_test=True,
            emit_report=True,
        )
        report = run_builder(args)
        preview = build_preview_report((root / "candidate-post-layout" / "payload.json").resolve(), DEFAULT_OUT_DIR)
        report["temporary_workspace"] = report["workspace"]
        report["temporary_candidate_payload"] = report["candidate_payload"]
        report["temporary_copied_files"] = list(report["copied_files"])
        report["preview_status_before_removal"] = preview.get("status")
        report["preview_would_write_accepted_evidence_before_removal"] = preview.get("would_write_accepted_evidence")
        report["preview_strict_issue_count_before_removal"] = preview.get("strict_issue_count")
        report["preview_would_write_files_before_removal"] = preview.get("would_write_files")
    report["self_test"] = True
    report["temporary_fixture_persisted"] = False
    report["candidate_payload"] = "temporary self-test payload removed"
    report["workspace"] = "temporary self-test workspace removed"
    report["copied_files"] = []
    report["next_command"] = "python3 scripts/build_converter_post_layout_candidate_from_real_run.py --netlist REAL.sp --model-file MODEL.sp --rerun-artifact RERUN.json ..."
    write_report(report)
    if not report["strict_validation_passed"]:
        raise SystemExit("real candidate builder self-test failed strict validation")
    return report


def main() -> int:
    args = parse_args()
    report = run_self_test() if args.self_test else run_builder(args)
    print("converter_post_layout_real_candidate_builder")
    print(f"status,{report['status']}")
    print(f"wrote_payload,{report['wrote_payload']}")
    print(f"strict_validation_passed,{report['strict_validation_passed']}")
    print(f"strict_issue_count,{report['strict_issue_count']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0 if report["strict_validation_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
