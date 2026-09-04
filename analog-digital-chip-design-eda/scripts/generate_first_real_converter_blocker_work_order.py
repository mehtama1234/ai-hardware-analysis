#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
REHEARSAL = EVIDENCE / "first-real-converter-rehearsal-payload.json"
PACKET = EVIDENCE / "first-real-converter-candidate-packet.json"
OUT_JSON = EVIDENCE / "first-real-converter-blocker-work-order.json"
OUT_MD = EVIDENCE / "first-real-converter-blocker-work-order.md"


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"missing required evidence: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def work_items(run_id: str) -> list[dict[str, Any]]:
    return [
        {
            "id": "B1",
            "blocker": "converter_object",
            "status": "open",
            "question": "What physical object is the converter/readout candidate?",
            "experiment": "Build or select one extracted netlist that includes row DAC, SAR/readout, shared mux, references, and sample path under one subckt or manifest.",
            "output_artifact": "evidence/aimc-simulator-adapters/candidate-post-layout/netlist/aimc_readout_candidate_001_extracted.spice",
            "payload_fields": [
                "extraction.extracted_netlist",
                "extraction.includes_row_dac",
                "extraction.includes_sar_readout",
                "extraction.includes_shared_mux",
                "extraction.includes_references",
                "extraction.includes_sample_path",
            ],
            "acceptance_check": "strict payload no longer reports any extraction.includes_* failure and the netlist path exists",
            "simple_meaning": "The candidate must be one inspectable circuit object, not separate loose evidence fragments.",
        },
        {
            "id": "B2",
            "blocker": "adc_energy",
            "status": "open",
            "question": "How much supply energy does the readout decision spend?",
            "experiment": "Run a supply-current integration deck over the ADC/comparator decision window for the same run id.",
            "output_artifact": "evidence/aimc-simulator-adapters/candidate-post-layout/measurements/readout-energy.json",
            "payload_fields": [
                "energy.adc_energy_per_conversion",
                "energy.dac_energy_per_row_drive",
                "energy.method",
                "energy.run_id",
            ],
            "acceptance_check": "ADC and DAC energy are positive joule values and energy.run_id equals provenance.run_id",
            "simple_meaning": "The converter cost is voltage times supply current over the event, not a guessed label.",
        },
        {
            "id": "B3",
            "blocker": "conversion_latency",
            "status": "open",
            "question": "When is the digital value safe to read?",
            "experiment": "Measure row settling plus readout/comparator/SAR decision time in one transient run.",
            "output_artifact": "evidence/aimc-simulator-adapters/candidate-post-layout/measurements/readout-latency.json",
            "payload_fields": [
                "latency.conversion_time_ns",
                "latency.settling_time_ns",
                "latency.method",
                "latency.run_id",
            ],
            "acceptance_check": "conversion_time_ns and settling_time_ns are positive and measured from the same command/run id",
            "simple_meaning": "Latency is the wait between asking for a value and having a value the digital side can trust.",
        },
        {
            "id": "B4",
            "blocker": "noise",
            "status": "open",
            "question": "How uncertain is the produced digital value?",
            "experiment": "Measure or simulate output noise and input-referred noise at the readout boundary for the same circuit and run id.",
            "output_artifact": "evidence/aimc-simulator-adapters/candidate-post-layout/measurements/readout-noise.json",
            "payload_fields": [
                "noise.output_noise_rms",
                "noise.input_referred_noise",
                "noise.meets_output_noise_budget",
                "noise.run_id",
            ],
            "acceptance_check": "output_noise_rms is numeric, input_referred_noise is numeric, and output_noise_rms <= 0.004",
            "simple_meaning": "The model sees noise as a wrong or uncertain number, so the converter must keep that uncertainty inside the model budget.",
        },
        {
            "id": "B5",
            "blocker": "area",
            "status": "open",
            "question": "How much physical space does the ADC/readout and DAC/row-drive path consume?",
            "experiment": "Compute area from the selected physical cells or extracted layout boundary for the same candidate object.",
            "output_artifact": "evidence/aimc-simulator-adapters/candidate-post-layout/measurements/readout-area.json",
            "payload_fields": [
                "area.adc_area_um2",
                "area.dac_area_um2",
                "area.method",
                "area.run_id",
            ],
            "acceptance_check": "ADC and DAC area are positive square-micron values tied to the same candidate id",
            "simple_meaning": "Area is the chip space paid for the circuit; if it must be repeated too often, the system cost changes.",
        },
        {
            "id": "B6",
            "blocker": "break_even",
            "status": "open",
            "question": "Do the measured converter numbers change the analog-versus-digital decision?",
            "experiment": "Rerun converter break-even using the measured energy, latency, noise, area, and same sharing rule.",
            "output_artifact": "evidence/aimc-simulator-adapters/candidate-post-layout/rerun/aimc_readout_candidate_001_break_even_rerun.json",
            "payload_fields": [
                "break_even_rerun.rerun_artifact",
                "break_even_rerun.uses_extracted_energy",
                "break_even_rerun.uses_extracted_latency",
                "break_even_rerun.uses_extracted_noise",
                "break_even_rerun.uses_extracted_area",
                "break_even_rerun.run_id",
            ],
            "acceptance_check": "rerun artifact exists, all uses_extracted_* fields are true, and break_even_rerun.run_id equals provenance.run_id",
            "simple_meaning": "Accepted evidence must change or confirm the system decision, not just sit beside it.",
        },
    ]


def build_work_order() -> dict[str, Any]:
    rehearsal = load_json(REHEARSAL)
    packet = load_json(PACKET)
    run_id = str(packet["proposed_run_id"])
    items = work_items(run_id)
    strict_categories = sorted({issue.get("category") for issue in rehearsal.get("strict_issues", []) if isinstance(issue, dict)})
    return {
        "result_type": "first_real_converter_blocker_work_order",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "six_experiment_work_order_ready",
        "source_rehearsal": rel(REHEARSAL),
        "source_packet": rel(PACKET),
        "candidate_id": packet["candidate_id"],
        "run_id": run_id,
        "rehearsal_strict_issue_count": rehearsal["strict_issue_count"],
        "work_item_count": len(items),
        "strict_issue_categories": strict_categories,
        "work_items": items,
        "next_payload_check": "python3 scripts/preflight_converter_post_layout_payload.py evidence/aimc-simulator-adapters/candidate-post-layout/payload.json",
        "claim_boundary": {
            "allowed": "turns the remaining rehearsal blockers into six concrete measurement/build work items for the first real converter candidate",
            "not_allowed": "does not create the missing measurements, does not modify the canonical candidate payload, and does not write accepted post-layout evidence",
        },
    }


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# First Real Converter Blocker Work Order",
        "",
        f"- status: `{report['status']}`",
        f"- candidate id: `{report['candidate_id']}`",
        f"- run id: `{report['run_id']}`",
        f"- rehearsal strict issue count: `{report['rehearsal_strict_issue_count']}`",
        f"- work item count: `{report['work_item_count']}`",
        "",
        "## First Principle",
        "",
        "The remaining failures are not one problem. They are six different measurements or build tasks. A complete converter claim needs one physical object, energy, latency, noise, area, and a rerun that uses those values.",
        "",
        "Each item below says what question must be answered, what experiment answers it, what file should be produced, and which payload fields that file unlocks.",
        "",
        "## Work Items",
        "",
    ]
    for item in report["work_items"]:
        lines.extend([
            f"### {item['id']}. {item['blocker']}",
            "",
            f"- status: `{item['status']}`",
            f"- question: {item['question']}",
            f"- experiment: {item['experiment']}",
            f"- output artifact: `{item['output_artifact']}`",
            f"- acceptance check: {item['acceptance_check']}",
            f"- simple meaning: {item['simple_meaning']}",
            "- payload fields:",
        ])
        lines.extend(f"  - `{field}`" for field in item["payload_fields"])
        lines.append("")
    lines.extend([
        "## Next Payload Check",
        "",
        f"`{report['next_payload_check']}`",
        "",
        "## Refused Claim",
        "",
        report["claim_boundary"]["not_allowed"],
        "",
    ])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_work_order()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print("first_real_converter_blocker_work_order")
    print(f"status,{report['status']}")
    print(f"candidate_id,{report['candidate_id']}")
    print(f"rehearsal_strict_issue_count,{report['rehearsal_strict_issue_count']}")
    print(f"work_item_count,{report['work_item_count']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
