#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ADAPTER_DIR = ROOT / "evidence" / "aimc-simulator-adapters"
SIM_SCHEMA = ROOT / "sources" / "evidence" / "analog-simulator-adapter-output-schema.json"
POST_LAYOUT_SCHEMA = ROOT / "sources" / "evidence" / "converter-post-layout-evidence-schema.json"
OUT_JSON = ADAPTER_DIR / "simulator-to-post-layout-gap-audit.json"
OUT_MD = ADAPTER_DIR / "simulator-to-post-layout-gap-audit.md"

POST_LAYOUT_EVIDENCE_FIELDS = [
    "extracted_netlist",
    "parasitic_format",
    "process_corner",
    "model_files",
    "adc_energy_per_conversion",
    "dac_energy_per_row_drive",
    "conversion_time_ns",
    "settling_time_ns",
    "output_noise_rms",
    "input_referred_noise",
    "adc_area_um2",
    "dac_area_um2",
    "replication_or_sharing_rule",
    "rerun_artifact",
    "same_run_id",
]


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def simulator_payloads() -> list[dict[str, Any]]:
    payloads = []
    for path in sorted(ADAPTER_DIR.glob("*.json")):
        try:
            payload = load_json(path)
        except json.JSONDecodeError:
            continue
        if payload.get("result_type") != "analog_simulator_adapter_output":
            continue
        provenance = payload.get("provenance") if isinstance(payload.get("provenance"), dict) else {}
        accuracy = payload.get("accuracy_impact") if isinstance(payload.get("accuracy_impact"), dict) else {}
        error_model = payload.get("error_model") if isinstance(payload.get("error_model"), dict) else {}
        payloads.append({
            "path": rel(path),
            "tool": provenance.get("tool") or error_model.get("tool"),
            "tool_version": provenance.get("tool_version"),
            "measurement_level": provenance.get("measurement_level"),
            "target_object": error_model.get("target_object"),
            "pass": accuracy.get("pass"),
            "final_residual_relative": error_model.get("final_residual_relative"),
            "final_residual_q8": error_model.get("final_residual_q8"),
            "can_support_simulator_claim": accuracy.get("pass") is True,
            "can_support_post_layout_converter_claim": False,
            "reason_post_layout_claim_blocked": "simulator payload has no extracted converter netlist, parasitic format, converter physical values, or same-run break-even rerun artifact",
        })
    return payloads


def build_report() -> dict[str, Any]:
    sim_schema = load_json(SIM_SCHEMA)
    post_layout_schema = load_json(POST_LAYOUT_SCHEMA)
    payloads = simulator_payloads()
    supporting_simulator_payloads = [payload for payload in payloads if payload["can_support_simulator_claim"]]
    blocked_post_layout_payloads = [payload for payload in payloads if not payload["can_support_post_layout_converter_claim"]]
    return {
        "result_type": "simulator_to_post_layout_gap_audit",
        "status": "simulator_evidence_present_post_layout_converter_evidence_missing",
        "simulator_schema": rel(SIM_SCHEMA),
        "post_layout_schema": rel(POST_LAYOUT_SCHEMA),
        "simulator_required_top_level_fields": sim_schema.get("required_top_level_fields", []),
        "post_layout_required_top_level_fields": post_layout_schema.get("required_top_level_fields", []),
        "post_layout_evidence_fields_not_supplied_by_simulator_payloads": POST_LAYOUT_EVIDENCE_FIELDS,
        "simulator_payload_count": len(payloads),
        "supporting_simulator_payload_count": len(supporting_simulator_payloads),
        "post_layout_converter_ready_payload_count": 0,
        "blocked_post_layout_payload_count": len(blocked_post_layout_payloads),
        "payloads": payloads,
        "bridge_rule": {
            "simulator_payload_can_do": "show that a named simulator ran a bounded analog compute fixture and report residual error",
            "post_layout_payload_must_do": "show what the converter layout became, which physical equations were used, what energy/latency/noise/area were measured, and whether those values changed the break-even decision",
            "handoff": "use simulator residual evidence to choose which operators deserve layout work, then use the post-layout builder only after extracted converter artifacts and same-run numeric values exist",
        },
        "claim_boundary": {
            "allowed": "connects existing AIHWKIT/CrossSim evidence to the post-layout evidence contract and names the missing physical fields",
            "not_allowed": "does not treat AIHWKIT or CrossSim output residuals as extracted layout, measured converter energy, measured latency, measured area, or accepted post-layout evidence",
        },
    }


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# Simulator To Post-Layout Gap Audit",
        "",
        f"- status: `{report['status']}`",
        f"- simulator payload count: `{report['simulator_payload_count']}`",
        f"- supporting simulator payload count: `{report['supporting_simulator_payload_count']}`",
        f"- post-layout converter ready payload count: `{report['post_layout_converter_ready_payload_count']}`",
        f"- blocked post-layout payload count: `{report['blocked_post_layout_payload_count']}`",
        "",
        "## First Principle",
        "",
        "A simulator run and a post-layout converter run answer different questions. The simulator run asks how much an analog matrix operation changes the output. The post-layout converter run asks what the physical converter costs after layout, extraction, and corner setup. A low residual can justify trying analog placement. It cannot by itself justify the converter energy, latency, noise, or area claim.",
        "",
        "## Missing Physical Fields",
        "",
        *[f"- `{field}`" for field in report["post_layout_evidence_fields_not_supplied_by_simulator_payloads"]],
        "",
        "## Payload Boundary",
        "",
    ]
    for payload in report["payloads"]:
        lines.extend([
            f"### {payload['path']}",
            "",
            f"- tool: `{payload['tool']}`",
            f"- measurement level: `{payload['measurement_level']}`",
            f"- simulator claim support: `{payload['can_support_simulator_claim']}`",
            f"- post-layout converter claim support: `{payload['can_support_post_layout_converter_claim']}`",
            f"- residual: `{payload['final_residual_relative']}` q8 `{payload['final_residual_q8']}`",
            "",
        ])
    lines.extend([
        "## Handoff Rule",
        "",
        report["bridge_rule"]["handoff"],
        "",
        "## Refused Claim",
        "",
        report["claim_boundary"]["not_allowed"],
        "",
    ])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print("simulator_to_post_layout_gap_audit")
    print(f"status,{report['status']}")
    print(f"simulator_payload_count,{report['simulator_payload_count']}")
    print(f"supporting_simulator_payload_count,{report['supporting_simulator_payload_count']}")
    print(f"post_layout_converter_ready_payload_count,{report['post_layout_converter_ready_payload_count']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
