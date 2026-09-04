#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "evidence" / "aimc-simulator-adapters" / "candidate-post-layout"
PAYLOAD = WORKSPACE / "payload.json"
README = WORKSPACE / "README.md"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-workspace.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-workspace.md"
PREFLIGHT = ROOT / "scripts" / "preflight_converter_post_layout_payload.py"
SUBMIT = ROOT / "scripts" / "submit_converter_post_layout_payload.py"


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=False)


def main() -> None:
    for subdir in ["netlist", "models", "rerun"]:
        (WORKSPACE / subdir).mkdir(parents=True, exist_ok=True)
        (WORKSPACE / subdir / ".gitkeep").write_text("", encoding="utf-8")

    payload = {
        "template_only": True,
        "result_type": "converter_post_layout_evidence",
        "converter_id": "replace-with-real-converter-id",
        "measurement_level": "post_layout_simulation",
        "target_boundary": {
            "adc_bits": 12,
            "dac_bits": 10,
            "output_noise_budget": 0.004,
        },
        "extraction": {
            "extracted_netlist": "netlist/replace-with-extracted-netlist.sp",
            "parasitic_format": "replace-with-spef-dspf-or-extracted-spice",
            "includes_row_dac": True,
            "includes_sar_readout": True,
            "includes_shared_mux": True,
            "includes_references": True,
            "includes_sample_path": True,
        },
        "simulation": {
            "simulator": "replace-with-simulator",
            "command": "replace-with-reproducible-command",
            "process_corner": "replace-with-corner-or-measurement-condition",
            "voltage_v": "replace-with-numeric-supply",
            "temperature_c": "replace-with-numeric-temperature",
            "model_files": ["models/replace-with-model-file.sp"],
            "run_id": "replace-with-shared-run-id",
        },
        "energy": {
            "adc_energy_per_conversion": "replace-with-positive-joules",
            "dac_energy_per_row_drive": "replace-with-positive-joules",
            "energy_unit": "joule",
            "method": "replace with supply integration method over the named conversion windows",
            "run_id": "replace-with-shared-run-id",
        },
        "latency": {
            "adc_comparisons": 12,
            "conversion_time_ns": "replace-with-positive-ns",
            "settling_time_ns": "replace-with-positive-ns",
            "method": "replace with timing measurement method",
            "run_id": "replace-with-shared-run-id",
        },
        "noise": {
            "output_noise_rms": "replace-with-rms-at-or-below-0.004",
            "input_referred_noise": "replace-with-input-referred-noise",
            "meets_output_noise_budget": True,
            "method": "replace with readout noise measurement method",
            "run_id": "replace-with-shared-run-id",
        },
        "area": {
            "adc_area_um2": "replace-with-positive-area",
            "dac_area_um2": "replace-with-positive-area",
            "replication_or_sharing_rule": "64 rows, 4 columns, 4 converter instances, 16 outputs per conversion cost",
            "method": "replace with extracted or measured area source",
            "run_id": "replace-with-shared-run-id",
        },
        "sharing": {
            "rows_served": 64,
            "columns_served": 4,
            "outputs_per_conversion_cost": 16,
            "converter_instances": 4,
        },
        "break_even_rerun": {
            "rerun_artifact": "rerun/replace-with-source-break-even-rerun.json",
            "uses_extracted_energy": True,
            "uses_extracted_latency": True,
            "uses_extracted_noise": True,
            "uses_extracted_area": True,
            "uses_same_sharing_rule": True,
            "replacement_decision": "replace-with-replace-or-keep-digital-fallback",
            "run_id": "replace-with-shared-run-id",
        },
        "provenance": {
            "created_at": "replace-with-run-timestamp",
            "generator_or_lab_notebook": "replace-with-script-or-notebook",
            "operator": "replace-with-person-or-ci-job",
            "source_schema": "sources/evidence/converter-post-layout-evidence-schema.json",
            "run_id": "replace-with-shared-run-id",
        },
        "claim_boundary": {
            "allowed": "use this as a starting workspace only",
            "not_allowed": "this scaffold is not evidence, is marked template_only, and must fail preflight/submission until real values and files replace placeholders",
        },
    }
    PAYLOAD.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    README.write_text(
        "\n".join([
            "# Candidate Converter Post-Layout Workspace",
            "",
            "This folder is a staging area for a real converter post-layout or measured-silicon package.",
            "",
            "Replace `payload.json` placeholders with real values. Put the extracted netlist under `netlist/`, model or measurement setup files under `models/`, and the source break-even rerun artifact under `rerun/`. Use one shared `run_id` across provenance, simulation, energy, latency, noise, area, and break-even rerun fields.",
            "",
            "Run preflight before submission:",
            "",
            "```bash",
            "python3 scripts/preflight_converter_post_layout_payload.py evidence/aimc-simulator-adapters/candidate-post-layout/payload.json",
            "```",
            "",
            "Only after preflight reports ready should the payload be submitted.",
            "",
            "## Refused Claim",
            "",
            "This workspace is not evidence. It is a staging folder and the default payload is intentionally rejected.",
            "",
        ]),
        encoding="utf-8",
    )

    preflight = run([sys.executable, str(PREFLIGHT), str(PAYLOAD), "--expect-not-ready"])
    submission = run([sys.executable, str(SUBMIT), str(PAYLOAD), "--expect-reject"])
    report = {
        "result_type": "converter_post_layout_candidate_workspace",
        "status": "candidate_workspace_ready_not_evidence" if preflight.returncode == 0 and submission.returncode == 0 else "candidate_workspace_failed",
        "workspace": str(WORKSPACE.relative_to(ROOT)),
        "payload": str(PAYLOAD.relative_to(ROOT)),
        "preflight_rejects_default_payload": preflight.returncode == 0,
        "submission_rejects_default_payload": submission.returncode == 0,
        "next_command": "python3 scripts/preflight_converter_post_layout_payload.py evidence/aimc-simulator-adapters/candidate-post-layout/payload.json",
        "claim_boundary": {
            "allowed": "provides a concrete staging folder for a future real payload",
            "not_allowed": "does not claim extracted post-layout evidence exists and does not write accepted evidence",
        },
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "\n".join([
            "# Converter Post-Layout Candidate Workspace",
            "",
            f"- status: `{report['status']}`",
            f"- workspace: `{report['workspace']}`",
            f"- payload: `{report['payload']}`",
            f"- preflight rejects default payload: `{report['preflight_rejects_default_payload']}`",
            f"- submission rejects default payload: `{report['submission_rejects_default_payload']}`",
            "",
            "This is the concrete staging folder for the first real converter package. It keeps the file layout simple: payload, extracted netlist, model files, break-even rerun artifact, and one shared run id across every value section.",
            "",
            "## First Principle",
            "",
            "A real evidence packet is a small filesystem, not just one number. The JSON says what is being claimed. The netlist or measurement files show the physical object. The model files define the electrical conditions. The rerun artifact shows the system-level decision that follows from those numbers.",
            "",
            "The default workspace is intentionally rejected. That prevents an empty folder from looking like a completed post-layout run.",
            "",
            "## Next Command",
            "",
            f"`{report['next_command']}`",
            "",
            "## Refused Claim",
            "",
            report["claim_boundary"]["not_allowed"],
            "",
        ]),
        encoding="utf-8",
    )
    if report["status"] != "candidate_workspace_ready_not_evidence":
        raise SystemExit("converter post-layout candidate workspace failed")
    print("converter_post_layout_candidate_workspace")
    print(f"status,{report['status']}")
    print(f"workspace,{WORKSPACE}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")


if __name__ == "__main__":
    main()
