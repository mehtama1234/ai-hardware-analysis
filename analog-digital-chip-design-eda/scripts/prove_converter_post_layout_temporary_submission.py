#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from build_converter_post_layout_candidate_from_real_run import run_builder
from preview_converter_post_layout_submission import build_report as build_preview_report


ROOT = Path(__file__).resolve().parents[1]
ACCEPTED = ROOT / "evidence" / "aimc-simulator-adapters" / "accepted-post-layout"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-temporary-submission-proof.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-temporary-submission-proof.md"


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def source_files(root: Path) -> tuple[Path, Path, Path]:
    source = root / "source"
    source.mkdir()
    netlist = source / "temp-submit-extracted.sp"
    model = source / "temp-submit-model.sp"
    rerun = source / "temp-submit-source-rerun.json"
    netlist.write_text("* temporary strict submission proof extracted netlist\n.end\n", encoding="utf-8")
    model.write_text("* temporary strict submission proof model file\n.model temp_submit_model nmos\n", encoding="utf-8")
    rerun.write_text(json.dumps({"result_type": "temporary_source_rerun", "run_id": "temporary-submission-proof-run"}) + "\n", encoding="utf-8")
    return netlist, model, rerun


def build_args(root: Path, netlist: Path, model: Path, rerun: Path) -> argparse.Namespace:
    return argparse.Namespace(
        netlist=netlist,
        model_file=model,
        rerun_artifact=rerun,
        converter_id="temporary-submission-proof-converter",
        run_id="temporary-submission-proof-run",
        measurement_level="post_layout_simulation",
        parasitic_format="extracted-spice",
        simulator="ngspice",
        command="ngspice temp-submit-extracted.sp",
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
        energy_method="temporary submission proof integrated supply windows",
        latency_method="temporary submission proof threshold crossing",
        noise_method="temporary submission proof rms output noise",
        area_method="temporary submission proof extracted area",
        operator="local temporary submission proof",
        notebook="scripts/prove_converter_post_layout_temporary_submission.py",
        workspace=root / "candidate-post-layout",
        output_payload=None,
        dry_run=False,
        self_test=True,
        emit_report=False,
    )


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Converter Post-Layout Temporary Submission Proof",
        "",
        f"- status: `{report['status']}`",
        f"- builder strict validation passed: `{report['builder_strict_validation_passed']}`",
        f"- preview would write accepted evidence: `{report['preview_would_write_accepted_evidence']}`",
        f"- temporary submit passed: `{report['temporary_submit_passed']}`",
        f"- temporary accepted files written: `{report['temporary_accepted_file_count']}`",
        f"- canonical accepted evidence exists after proof: `{report['canonical_accepted_evidence_exists_after_proof']}`",
        f"- temporary fixture persisted: `{report['temporary_fixture_persisted']}`",
        "",
        "This proof runs the final mechanical path in a temporary directory. It builds a complete candidate payload, previews submission, runs the strict submitter into a temporary accepted directory, checks that the expected files were written there, and then lets the temporary directory disappear.",
        "",
        "## First Principle",
        "",
        "The real submitter should be able to write accepted evidence only after the candidate package is complete. This proof checks that the write path works without using the canonical accepted-evidence directory.",
        "",
        "## Temporary Accepted Files",
        "",
        *[f"- `{path}`" for path in report["temporary_accepted_files"]],
        "",
        "## Refused Claim",
        "",
        report["claim_boundary"]["not_allowed"],
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="aimc-temp-submit-proof-") as tmp:
        root = Path(tmp)
        netlist, model, rerun = source_files(root)
        builder = run_builder(build_args(root, netlist, model, rerun))
        payload_path = root / "candidate-post-layout" / "payload.json"
        temp_accepted = root / "accepted-post-layout"
        preview = build_preview_report(payload_path, temp_accepted)
        submit = run([
            sys.executable,
            "scripts/submit_converter_post_layout_payload.py",
            str(payload_path),
            "--output-dir",
            str(temp_accepted),
        ])
        accepted_files = sorted(path for path in temp_accepted.glob("*.json") if path.is_file())
        temporary_submit_passed = submit.returncode == 0 and len(accepted_files) == 2
        temporary_accepted_files = [str(path) for path in accepted_files]
    report = {
        "result_type": "converter_post_layout_temporary_submission_proof",
        "status": "temporary_submission_path_proven" if builder.get("strict_validation_passed") and preview.get("would_write_accepted_evidence") and temporary_submit_passed and not ACCEPTED.exists() else "temporary_submission_path_failed",
        "builder_strict_validation_passed": builder.get("strict_validation_passed"),
        "builder_strict_issue_count": builder.get("strict_issue_count"),
        "preview_status": preview.get("status"),
        "preview_would_write_accepted_evidence": preview.get("would_write_accepted_evidence"),
        "preview_strict_issue_count": preview.get("strict_issue_count"),
        "temporary_submit_passed": temporary_submit_passed,
        "temporary_accepted_file_count": len(temporary_accepted_files),
        "temporary_accepted_files": temporary_accepted_files,
        "temporary_fixture_persisted": False,
        "canonical_accepted_evidence_exists_after_proof": ACCEPTED.exists(),
        "submit_returncode": submit.returncode,
        "submit_stdout": submit.stdout.strip().splitlines(),
        "submit_stderr": submit.stderr.strip().splitlines(),
        "claim_boundary": {
            "allowed": "proves the builder, preview, and strict submitter can write accepted evidence into a temporary output directory when the package is complete",
            "not_allowed": "does not create canonical accepted evidence, does not prove the temporary files are real layout or silicon, and does not upgrade the converter claim",
        },
    }
    write_report(report)
    if report["status"] != "temporary_submission_path_proven":
        raise SystemExit("temporary submission path proof failed")
    print("converter_post_layout_temporary_submission_proof")
    print(f"status,{report['status']}")
    print(f"temporary_submit_passed,{report['temporary_submit_passed']}")
    print(f"temporary_accepted_file_count,{report['temporary_accepted_file_count']}")
    print(f"canonical_accepted_evidence_exists_after_proof,{report['canonical_accepted_evidence_exists_after_proof']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
