#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
WORKBENCH = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware" / "layout-workbench"
STARTER_WORKSPACE = ROOT / "evidence" / "aimc-simulator-adapters" / "starter-post-layout-candidate"
SOURCE_RERUN = WORKBENCH / "extracted" / "starter-layout-source-break-even-rerun.json"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-starter-post-layout-candidate.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-starter-post-layout-candidate.md"


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def write_source_rerun(run_id: str) -> None:
    SOURCE_RERUN.parent.mkdir(parents=True, exist_ok=True)
    SOURCE_RERUN.write_text(
        json.dumps(
            {
                "result_type": "starter_layout_source_break_even_rerun",
                "run_id": run_id,
                "source": "workbench starter layout smoke",
                "replacement_decision": "keep_digital_fallback",
                "claim_boundary": {
                    "allowed": "source-side rerun record for testing candidate packet mechanics",
                    "not_allowed": "not accepted post-layout evidence and not proof of production converter economics",
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def build_report() -> dict[str, Any]:
    run_id = "starter-layout-smoke-sky130-001"
    write_source_rerun(run_id)
    payload = STARTER_WORKSPACE / "payload.json"
    builder = [
        sys.executable,
        "scripts/build_converter_post_layout_candidate_from_real_run.py",
        "--workspace",
        str(STARTER_WORKSPACE),
        "--netlist",
        str(WORKBENCH / "extracted" / "aimc_converter_macro_layout_smoke.spice"),
        "--model-file",
        str(WORKBENCH / "sky130-ngspice.includes"),
        "--rerun-artifact",
        str(SOURCE_RERUN),
        "--converter-id",
        "aimc_converter_macro_starter_layout_smoke",
        "--run-id",
        run_id,
        "--measurement-level",
        "post_layout_simulation",
        "--parasitic-format",
        "extracted-spice",
        "--simulator",
        "magic-ext2spice",
        "--command",
        "python3 scripts/run_converter_starter_layout_smoke.py",
        "--process-corner",
        "sky130A_tt_1p8V_25C",
        "--voltage-v",
        "1.8",
        "--temperature-c",
        "25",
        "--adc-energy-per-conversion",
        "2.0e-12",
        "--dac-energy-per-row-drive",
        "4.0e-13",
        "--conversion-time-ns",
        "12",
        "--settling-time-ns",
        "3",
        "--output-noise-rms",
        "0.001",
        "--input-referred-noise",
        "0.001",
        "--adc-area-um2",
        "1200",
        "--dac-area-um2",
        "700",
        "--replacement-decision",
        "keep_digital_fallback",
        "--energy-method",
        "starter payload uses bounded local estimate values; not extracted supply integration",
        "--latency-method",
        "starter payload uses bounded local estimate values; not transistor timing signoff",
        "--noise-method",
        "starter payload uses bounded local estimate values; not post-layout noise simulation",
        "--area-method",
        "starter payload uses named starter macro boundary area estimate; not extracted signoff area",
        "--operator",
        "local starter-candidate builder",
        "--notebook",
        "scripts/build_converter_starter_post_layout_candidate.py",
    ]
    builder_run = run(builder)
    preflight_json = OUT_JSON.with_name("converter-starter-post-layout-candidate-preflight.json")
    preflight_md = OUT_MD.with_name("converter-starter-post-layout-candidate-preflight.md")
    preflight = run(
        [
            sys.executable,
            "scripts/preflight_converter_post_layout_payload.py",
            str(payload),
            "--json-output",
            str(preflight_json),
            "--markdown-output",
            str(preflight_md),
        ]
    )
    preview_json = OUT_JSON.with_name("converter-starter-post-layout-candidate-preview.json")
    preview_md = OUT_MD.with_name("converter-starter-post-layout-candidate-preview.md")
    preview = run(
        [
            sys.executable,
            "scripts/preview_converter_post_layout_submission.py",
            "--payload",
            str(payload),
            "--json-output",
            str(preview_json),
            "--markdown-output",
            str(preview_md),
        ]
    )
    preflight_report = json.loads(preflight_json.read_text(encoding="utf-8")) if preflight_json.exists() else {}
    preview_report = json.loads(preview_json.read_text(encoding="utf-8")) if preview_json.exists() else {}
    accepted_dir = ROOT / "evidence" / "aimc-simulator-adapters" / "accepted-post-layout"
    return {
        "result_type": "converter_starter_post_layout_candidate",
        "status": "starter_candidate_packet_ready_not_accepted_evidence"
        if builder_run.returncode == 0 and preflight_report.get("status") == "ready_for_strict_submission"
        else "starter_candidate_packet_not_ready",
        "workspace": rel(STARTER_WORKSPACE),
        "payload": rel(payload),
        "source_rerun": rel(SOURCE_RERUN),
        "builder_returncode": builder_run.returncode,
        "builder_stdout_tail": builder_run.stdout[-2000:],
        "builder_stderr_tail": builder_run.stderr[-2000:],
        "preflight_returncode": preflight.returncode,
        "preflight_status": preflight_report.get("status"),
        "preflight_issue_count": preflight_report.get("issue_count"),
        "preview_returncode": preview.returncode,
        "preview_status": preview_report.get("status"),
        "preview_would_write_accepted_evidence": preview_report.get("would_write_accepted_evidence"),
        "canonical_accepted_post_layout_exists": accepted_dir.exists(),
        "writes_canonical_candidate_post_layout": False,
        "writes_accepted_post_layout": False,
        "claim_boundary": {
            "allowed": "proves extracted starter layout files can be shaped into a strict candidate packet in a separate starter workspace",
            "not_allowed": "does not submit accepted evidence, does not prove production converter physics, and does not replace the canonical post-layout evidence gate",
        },
    }


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# Converter Starter Post-Layout Candidate",
        "",
        f"- status: `{report['status']}`",
        f"- workspace: `{report['workspace']}`",
        f"- payload: `{report['payload']}`",
        f"- preflight status: `{report['preflight_status']}`",
        f"- preflight issue count: `{report['preflight_issue_count']}`",
        f"- preview status: `{report['preview_status']}`",
        f"- preview would write accepted evidence: `{report['preview_would_write_accepted_evidence']}`",
        f"- writes canonical candidate post-layout: `{report['writes_canonical_candidate_post_layout']}`",
        f"- writes accepted post-layout: `{report['writes_accepted_post_layout']}`",
        "",
        "## First Principle",
        "",
        "A candidate packet is the bridge between layout files and system claims. It must name the extracted circuit, the model setup, the numeric costs, the sharing rule, and the rerun that follows from those costs.",
        "",
        "This page proves that bridge mechanics using the starter layout cells. It deliberately keeps the result outside the canonical candidate folder because the starter shapes are not production converter circuits.",
        "",
        "This is not production converter physics. It is a packet and preflight proof for extracted starter files.",
        "",
        "## Refused Claim",
        "",
        report["claim_boundary"]["not_allowed"],
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print("converter_starter_post_layout_candidate")
    print(f"status,{report['status']}")
    print(f"preflight_status,{report['preflight_status']}")
    print(f"preflight_issue_count,{report['preflight_issue_count']}")
    print(f"preview_would_write_accepted_evidence,{report['preview_would_write_accepted_evidence']}")
    print(f"writes_accepted_post_layout,{report['writes_accepted_post_layout']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0 if report["status"] == "starter_candidate_packet_ready_not_accepted_evidence" else 1


if __name__ == "__main__":
    raise SystemExit(main())
