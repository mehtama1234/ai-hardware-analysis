#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROGRESS = ROOT / "scripts" / "generate_converter_post_layout_candidate_progress_report.py"
CURRENT_PAYLOAD = ROOT / "evidence" / "aimc-simulator-adapters" / "candidate-post-layout" / "payload.json"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-progress-gate.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-progress-gate.md"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def build_complete_fixture(tmpdir: Path) -> tuple[Path, Path, Path]:
    run_id = "candidate-gate-complete-fixture-run"
    workspace = tmpdir / "candidate-post-layout"
    (workspace / "netlist").mkdir(parents=True)
    (workspace / "models").mkdir(parents=True)
    (workspace / "rerun").mkdir(parents=True)
    payload_path = workspace / "payload.json"
    readme = workspace / "README.md"
    netlist = workspace / "netlist" / "extracted-row-dac-sar.sp"
    model = workspace / "models" / "tt-models.sp"
    rerun = workspace / "rerun" / "source-break-even-rerun.json"
    readme.write_text(
        "# Complete Temporary Candidate\n\n"
        "This fixture exists only to prove candidate readiness state transitions. "
        "It must not be submitted as accepted converter evidence.\n",
        encoding="utf-8",
    )
    netlist.write_text("* extracted converter fixture for readiness gate\n.END\n", encoding="utf-8")
    model.write_text("* model fixture for readiness gate\n.MODEL nch NMOS\n", encoding="utf-8")
    rerun.write_text(json.dumps({"result_type": "source_break_even_rerun_fixture", "status": "available"}) + "\n", encoding="utf-8")
    payload = load_json(CURRENT_PAYLOAD)
    payload.update(
        {
            "template_only": False,
            "converter_id": "progress-gate-complete-fixture",
            "measurement_level": "post_layout_simulation",
        }
    )
    payload["extraction"].update(
        {
            "extracted_netlist": "netlist/extracted-row-dac-sar.sp",
            "parasitic_format": "extracted_spice",
        }
    )
    payload["simulation"].update(
        {
            "simulator": "fixture-ngspice",
            "command": "ngspice -b netlist/extracted-row-dac-sar.sp",
            "process_corner": "tt",
            "voltage_v": 0.8,
            "temperature_c": 25.0,
            "model_files": ["models/tt-models.sp"],
            "run_id": run_id,
        }
    )
    payload["energy"].update(
        {
            "adc_energy_per_conversion": 1.6e-12,
            "dac_energy_per_row_drive": 2.0e-13,
            "run_id": run_id,
        }
    )
    payload["latency"].update(
        {
            "conversion_time_ns": 8.0,
            "settling_time_ns": 2.0,
            "run_id": run_id,
        }
    )
    payload["noise"].update(
        {
            "output_noise_rms": 0.003,
            "input_referred_noise": 0.0007,
            "run_id": run_id,
        }
    )
    payload["area"].update(
        {
            "adc_area_um2": 420.0,
            "dac_area_um2": 180.0,
            "run_id": run_id,
        }
    )
    payload["break_even_rerun"].update(
        {
            "rerun_artifact": "rerun/source-break-even-rerun.json",
            "replacement_decision": "keep_digital_fallback",
            "run_id": run_id,
        }
    )
    payload["provenance"].update(
        {
            "created_at": "2026-08-30T00:00:00Z",
            "generator_or_lab_notebook": "generate_converter_post_layout_candidate_progress_gate.py",
            "operator": "local-ci",
            "run_id": run_id,
        }
    )
    payload["claim_boundary"] = {
        "allowed": "use this complete temporary fixture only to test readiness state transitions",
        "not_allowed": "does not prove real post-layout physics and must not be submitted as accepted converter evidence",
    }
    payload_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return workspace, payload_path, rerun


def main() -> None:
    current_run = run([sys.executable, str(PROGRESS)])
    current_progress = load_json(ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-progress-report.json")
    with tempfile.TemporaryDirectory(prefix="candidate-progress-gate-") as tmp:
        tmpdir = Path(tmp)
        workspace, _payload_path, _rerun = build_complete_fixture(tmpdir)
        audit_json = tmpdir / "audit.json"
        audit_md = tmpdir / "audit.md"
        checklist_json = tmpdir / "checklist.json"
        checklist_md = tmpdir / "checklist.md"
        progress_json = tmpdir / "progress.json"
        progress_md = tmpdir / "progress.md"
        audit_run = run([
            sys.executable,
            "scripts/audit_converter_post_layout_candidate_workspace.py",
            "--workspace",
            str(workspace),
            "--json-output",
            str(audit_json),
            "--markdown-output",
            str(audit_md),
        ])
        try:
            shutil.copy2(audit_json, ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-workspace-audit.json")
            checklist_run = run([sys.executable, "scripts/generate_converter_post_layout_candidate_fill_checklist.py"])
            shutil.copy2(ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-fill-checklist.json", checklist_json)
            shutil.copy2(ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-fill-checklist.md", checklist_md)
            progress_run = run([sys.executable, str(PROGRESS)])
            shutil.copy2(ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-progress-report.json", progress_json)
            shutil.copy2(ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-progress-report.md", progress_md)
            complete_progress = load_json(progress_json)
        finally:
            # Restore canonical scaffold-derived artifacts before writing the proof report.
            run([sys.executable, "scripts/audit_converter_post_layout_candidate_workspace.py"])
            run([sys.executable, "scripts/generate_converter_post_layout_candidate_fill_checklist.py"])
            run([sys.executable, str(PROGRESS)])

    current_not_ready = (
        current_run.returncode == 0
        and current_progress.get("status") == "candidate_waiting_for_real_values"
        and current_progress.get("ready_for_preflight") is False
        and int(current_progress.get("open_checklist_items") or 0) >= 25
    )
    complete_ready = (
        audit_run.returncode == 0
        and checklist_run.returncode == 0
        and progress_run.returncode == 0
        and complete_progress.get("status") == "candidate_ready_for_preflight"
        and bool(complete_progress.get("ready_for_preflight")) is True
        and int(complete_progress.get("open_checklist_items", -1)) == 0
    )
    report = {
        "result_type": "converter_post_layout_candidate_progress_gate",
        "status": "progress_gate_passed" if current_not_ready and complete_ready else "progress_gate_failed",
        "current_candidate_not_ready": current_not_ready,
        "temporary_complete_candidate_ready": complete_ready,
        "current_candidate_status": current_progress.get("status"),
        "current_open_checklist_items": current_progress.get("open_checklist_items"),
        "temporary_complete_candidate_status": complete_progress.get("status"),
        "temporary_complete_ready_for_preflight": complete_progress.get("ready_for_preflight"),
        "temporary_complete_open_checklist_items": complete_progress.get("open_checklist_items"),
        "temporary_audit_returncode": audit_run.returncode,
        "temporary_checklist_returncode": checklist_run.returncode,
        "temporary_progress_returncode": progress_run.returncode,
        "synthetic_accepted_evidence_persisted": (ROOT / "evidence" / "aimc-simulator-adapters" / "accepted-post-layout").exists(),
        "source_progress_report": "evidence/aimc-simulator-adapters/converter-post-layout-candidate-progress-report.json",
        "claim_boundary": {
            "allowed": "proves the progress report distinguishes an incomplete scaffold from a complete temporary package",
            "not_allowed": "does not submit the temporary package, does not create accepted converter evidence, and does not prove real post-layout physics",
        },
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Converter Post-Layout Candidate Progress Gate",
        "",
        f"- status: `{report['status']}`",
        f"- current candidate not ready: `{report['current_candidate_not_ready']}`",
        f"- temporary complete candidate ready: `{report['temporary_complete_candidate_ready']}`",
        f"- current open checklist items: `{report['current_open_checklist_items']}`",
        f"- temporary complete open checklist items: `{report['temporary_complete_open_checklist_items']}`",
        f"- synthetic accepted evidence persisted: `{report['synthetic_accepted_evidence_persisted']}`",
        "",
        "This gate checks the progress reporter itself. The real candidate package must remain not ready while it still contains placeholders. A temporary complete package must flip the same reporter to ready without submitting accepted evidence.",
        "",
        "## First Principle",
        "",
        "A status page is useful only if it can move when the evidence changes. If it always says not ready, it is just a warning sign. If it says ready for the scaffold, it is unsafe. This gate proves both sides: the scaffold stays closed, and a complete packet opens the preflight door.",
        "",
        "## Refused Claim",
        "",
        report["claim_boundary"]["not_allowed"],
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    if report["status"] != "progress_gate_passed":
        raise SystemExit("converter post-layout candidate progress gate failed")
    print("converter_post_layout_candidate_progress_gate")
    print(f"status,{report['status']}")
    print(f"current_candidate_not_ready,{report['current_candidate_not_ready']}")
    print(f"temporary_complete_candidate_ready,{report['temporary_complete_candidate_ready']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")


if __name__ == "__main__":
    main()
