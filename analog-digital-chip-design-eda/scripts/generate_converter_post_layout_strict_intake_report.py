#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DRY_RUN = ROOT / "evidence" / "aimc-simulator-adapters" / "dry-run"
FAKE_PAYLOAD = DRY_RUN / "converter-post-layout-evidence.shape-only-missing-files.json"
VALIDATOR = ROOT / "scripts" / "validate_converter_post_layout_payload.py"
RERUN = ROOT / "scripts" / "rerun_converter_break_even_from_post_layout_payload.py"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-strict-intake-report.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-strict-intake-report.md"


def write_fake_payload() -> None:
    run_id = "shape-only-dry-run-missing-files"
    payload = {
        "result_type": "converter_post_layout_evidence",
        "converter_id": "shape-only-missing-files-not-evidence",
        "measurement_level": "post_layout_simulation",
        "target_boundary": {
            "adc_bits": 12,
            "dac_bits": 10,
            "output_noise_budget": 0.004,
        },
        "extraction": {
            "extracted_netlist": "missing/post-layout/converter_extracted.sp",
            "parasitic_format": "extracted_spice",
            "includes_row_dac": True,
            "includes_sar_readout": True,
            "includes_shared_mux": True,
            "includes_references": True,
            "includes_sample_path": True,
        },
        "simulation": {
            "simulator": "ngspice",
            "command": "ngspice -b missing/post-layout/converter_extracted.sp",
            "process_corner": "tt",
            "voltage_v": 1.8,
            "temperature_c": 25.0,
            "model_files": ["missing/pdk/models/tt.sp"],
            "run_id": run_id,
        },
        "energy": {
            "adc_energy_per_conversion": 4.0e-12,
            "dac_energy_per_row_drive": 2.0e-13,
            "energy_unit": "joule",
            "method": "shape-only fixture with plausible positive numbers; not evidence",
            "run_id": run_id,
        },
        "latency": {
            "adc_comparisons": 12,
            "conversion_time_ns": 24.0,
            "settling_time_ns": 8.0,
            "method": "shape-only fixture with plausible positive numbers; not evidence",
            "run_id": run_id,
        },
        "noise": {
            "output_noise_rms": 0.003,
            "input_referred_noise": 0.001,
            "meets_output_noise_budget": True,
            "method": "shape-only fixture with plausible positive numbers; not evidence",
            "run_id": run_id,
        },
        "area": {
            "adc_area_um2": 1200.0,
            "dac_area_um2": 800.0,
            "replication_or_sharing_rule": "64 rows, 4 columns, 4 converter instances, 16 outputs per conversion cost",
            "method": "shape-only fixture with plausible positive numbers; not evidence",
            "run_id": run_id,
        },
        "sharing": {
            "rows_served": 64,
            "columns_served": 4,
            "outputs_per_conversion_cost": 16,
            "converter_instances": 4,
        },
        "break_even_rerun": {
            "rerun_artifact": "missing/reports/converter_break_even_rerun.json",
            "uses_extracted_energy": True,
            "uses_extracted_latency": True,
            "uses_extracted_noise": True,
            "uses_extracted_area": True,
            "uses_same_sharing_rule": True,
            "replacement_decision": "keep_digital_fallback",
            "run_id": run_id,
        },
        "provenance": {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "generator_or_lab_notebook": "scripts/generate_converter_post_layout_strict_intake_report.py",
            "operator": "local dry-run",
            "source_schema": "sources/evidence/converter-post-layout-evidence-schema.json",
            "run_id": run_id,
        },
        "claim_boundary": {
            "allowed": "tests that shape-correct payloads still need real referenced files under strict intake",
            "not_allowed": "not post-layout evidence, not measured silicon, not a converter replacement result",
        },
    }
    DRY_RUN.mkdir(parents=True, exist_ok=True)
    FAKE_PAYLOAD.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run(args: list[str]) -> dict[str, object]:
    result = subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=False)
    return {
        "command": args,
        "returncode": result.returncode,
        "stdout": result.stdout.strip().splitlines(),
        "stderr": result.stderr.strip().splitlines(),
    }


def main() -> None:
    write_fake_payload()
    shape_check = run(["python3", str(VALIDATOR), str(FAKE_PAYLOAD)])
    strict_check = run(["python3", str(VALIDATOR), "--require-files", "--expect-reject", str(FAKE_PAYLOAD)])
    strict_rerun_check = run(["python3", str(RERUN), "--require-files", "--expect-reject", str(FAKE_PAYLOAD)])
    shape_passed = shape_check["returncode"] == 0 and any("PASS converter_post_layout_payload_validator" in line for line in shape_check["stdout"])
    strict_rejected = strict_check["returncode"] == 0 and any("PASS converter_post_layout_payload_rejected" in line for line in strict_check["stdout"])
    rerun_rejected = strict_rerun_check["returncode"] == 0 and any("PASS converter_post_layout_break_even_rerun_rejected" in line for line in strict_rerun_check["stdout"])
    payload = {
        "result_type": "converter_post_layout_strict_intake_report",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "strict_file_intake_ready_waiting_for_real_artifacts" if shape_passed and strict_rejected and rerun_rejected else "strict_file_intake_failed",
        "shape_only_payload": str(FAKE_PAYLOAD.relative_to(ROOT)),
        "shape_validation_passed": shape_passed,
        "strict_validation_rejected_missing_files": strict_rejected,
        "strict_rerun_rejected_missing_files": rerun_rejected,
        "checks": {
            "shape_validation": shape_check,
            "strict_validation": strict_check,
            "strict_rerun": strict_rerun_check,
        },
        "claim_boundary": {
            "allowed": "proves that real-intake mode requires referenced extraction, model, and rerun files to exist",
            "not_allowed": "does not provide post-layout evidence and does not make a converter replacement decision",
        },
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Converter Post-Layout Strict Intake",
        "",
        "This report checks the file boundary for future post-layout converter evidence.",
        "",
        f"- status: `{payload['status']}`",
        f"- shape-only payload: `{payload['shape_only_payload']}`",
        f"- shape validation passed: `{payload['shape_validation_passed']}`",
        f"- strict validation rejected missing files: `{payload['strict_validation_rejected_missing_files']}`",
        f"- strict rerun rejected missing files: `{payload['strict_rerun_rejected_missing_files']}`",
        "",
        "## First-Principles Reading",
        "",
        "A payload can have the right numbers and still fail as evidence. If the extracted netlist path is missing, the converter is not inspectable. If model files are missing, the process corner is only a label. If the break-even rerun artifact is missing, the replacement decision cannot be audited.",
        "",
        "Strict intake therefore adds a file test after the field test. The ordinary validator checks the payload shape, units, numeric bounds, and sharing rule. The strict mode also checks that the extracted netlist, model files, and break-even rerun artifact exist.",
        "",
        "## Refused Claim",
        "",
        payload["claim_boundary"]["not_allowed"],
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    if payload["status"] != "strict_file_intake_ready_waiting_for_real_artifacts":
        raise SystemExit("strict post-layout intake checks failed")
    print("converter_post_layout_strict_intake")
    print(f"status,{payload['status']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")


if __name__ == "__main__":
    main()
