#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_converter_post_layout_payload.py"
RERUN = ROOT / "scripts" / "rerun_converter_break_even_from_post_layout_payload.py"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-positive-path-report.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-positive-path-report.md"


def run(args: list[str]) -> dict[str, object]:
    result = subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=False)
    return {
        "command": args,
        "returncode": result.returncode,
        "stdout": result.stdout.strip().splitlines(),
        "stderr": result.stderr.strip().splitlines(),
    }


def write_positive_fixture(workdir: Path) -> tuple[Path, Path]:
    run_id = "synthetic-positive-path-same-run"
    netlist = workdir / "converter_extracted.sp"
    model = workdir / "tt_model.sp"
    prior_rerun = workdir / "source_break_even_rerun.json"
    payload_path = workdir / "synthetic_converter_post_layout_payload.json"
    rerun_out = workdir / "computed_break_even_rerun.json"
    netlist.write_text("* synthetic extracted converter netlist for guard testing only\n.end\n", encoding="utf-8")
    model.write_text("* synthetic model file for guard testing only\n.model nch nmos\n", encoding="utf-8")
    prior_rerun.write_text('{"synthetic": true, "replacement_decision": "keep_digital_fallback"}\n', encoding="utf-8")
    payload = {
        "result_type": "converter_post_layout_evidence",
        "converter_id": "synthetic-positive-path-not-evidence",
        "measurement_level": "post_layout_simulation",
        "target_boundary": {
            "adc_bits": 12,
            "dac_bits": 10,
            "output_noise_budget": 0.004,
        },
        "extraction": {
            "extracted_netlist": str(netlist),
            "parasitic_format": "extracted_spice",
            "includes_row_dac": True,
            "includes_sar_readout": True,
            "includes_shared_mux": True,
            "includes_references": True,
            "includes_sample_path": True,
        },
        "simulation": {
            "simulator": "ngspice",
            "command": f"ngspice -b {netlist}",
            "process_corner": "tt",
            "voltage_v": 1.8,
            "temperature_c": 25.0,
            "model_files": [str(model)],
            "run_id": run_id,
        },
        "energy": {
            "adc_energy_per_conversion": 4.0e-12,
            "dac_energy_per_row_drive": 2.0e-13,
            "energy_unit": "joule",
            "method": "temporary synthetic fixture for command-path testing only",
            "run_id": run_id,
        },
        "latency": {
            "adc_comparisons": 12,
            "conversion_time_ns": 24.0,
            "settling_time_ns": 8.0,
            "method": "temporary synthetic fixture for command-path testing only",
            "run_id": run_id,
        },
        "noise": {
            "output_noise_rms": 0.003,
            "input_referred_noise": 0.001,
            "meets_output_noise_budget": True,
            "method": "temporary synthetic fixture for command-path testing only",
            "run_id": run_id,
        },
        "area": {
            "adc_area_um2": 1200.0,
            "dac_area_um2": 800.0,
            "replication_or_sharing_rule": "64 rows, 4 columns, 4 converter instances, 16 outputs per conversion cost",
            "method": "temporary synthetic fixture for command-path testing only",
            "run_id": run_id,
        },
        "sharing": {
            "rows_served": 64,
            "columns_served": 4,
            "outputs_per_conversion_cost": 16,
            "converter_instances": 4,
        },
        "break_even_rerun": {
            "rerun_artifact": str(prior_rerun),
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
            "generator_or_lab_notebook": "scripts/generate_converter_post_layout_positive_path_report.py",
            "operator": "temporary synthetic command-path fixture",
            "source_schema": "sources/evidence/converter-post-layout-evidence-schema.json",
            "run_id": run_id,
        },
        "claim_boundary": {
            "allowed": "tests that strict validation and break-even rerun can execute when referenced files exist",
            "not_allowed": "not post-layout evidence, not measured silicon, not a converter replacement result",
        },
    }
    payload_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload_path, rerun_out


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="aimc-post-layout-positive-") as tmp:
        tmp_path = Path(tmp)
        payload_path, rerun_out = write_positive_fixture(tmp_path)
        validation = run(["python3", str(VALIDATOR), "--require-files", str(payload_path)])
        rerun = run(["python3", str(RERUN), "--require-files", str(payload_path), "--output", str(rerun_out)])
        rerun_payload = json.loads(rerun_out.read_text(encoding="utf-8")) if rerun_out.exists() else {}
    validation_passed = validation["returncode"] == 0 and any("PASS converter_post_layout_payload_validator" in line for line in validation["stdout"])
    rerun_passed = rerun["returncode"] == 0 and any("PASS converter_post_layout_break_even_rerun" in line for line in rerun["stdout"])
    payload = {
        "result_type": "converter_post_layout_positive_path_report",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "strict_positive_path_proven_with_temporary_synthetic_files" if validation_passed and rerun_passed else "strict_positive_path_failed",
        "temporary_fixture_persisted": False,
        "strict_validation_passed": validation_passed,
        "strict_rerun_passed": rerun_passed,
        "rerun_replacement_decision": (rerun_payload.get("summary") or {}).get("replacement_decision") if isinstance(rerun_payload.get("summary"), dict) else None,
        "checks": {
            "strict_validation": validation,
            "strict_rerun": rerun,
        },
        "claim_boundary": {
            "allowed": "proves the strict validator and rerun script have a working positive command path when referenced files exist",
            "not_allowed": "does not save or claim a real post-layout payload, extracted netlist, process model, measured silicon result, or replacement decision",
        },
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Converter Post-Layout Positive Path",
        "",
        "This report proves the strict intake can also accept a complete command-path fixture.",
        "",
        f"- status: `{payload['status']}`",
        f"- temporary fixture persisted: `{payload['temporary_fixture_persisted']}`",
        f"- strict validation passed: `{payload['strict_validation_passed']}`",
        f"- strict rerun passed: `{payload['strict_rerun_passed']}`",
        f"- rerun replacement decision: `{payload['rerun_replacement_decision']}`",
        "",
        "## First-Principles Reading",
        "",
        "A guard must prove both sides. It should reject incomplete evidence, and it should also accept a complete object when every referenced file exists. Otherwise the project only knows how to say no.",
        "",
        "This check creates temporary synthetic files for an extracted netlist, model file, payload, and prior rerun artifact. It runs strict validation and the break-even rerun against those files, records the result, and then lets the temporary directory disappear. That proves the command path works while not saving synthetic evidence as a reusable converter result.",
        "",
        "## Refused Claim",
        "",
        payload["claim_boundary"]["not_allowed"],
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    if payload["status"] != "strict_positive_path_proven_with_temporary_synthetic_files":
        raise SystemExit("strict positive path failed")
    print("converter_post_layout_positive_path")
    print(f"status,{payload['status']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")


if __name__ == "__main__":
    main()
