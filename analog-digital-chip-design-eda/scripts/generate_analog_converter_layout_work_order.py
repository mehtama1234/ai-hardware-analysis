#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "analog-converter-layout-work-order.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "analog-converter-layout-work-order.md"

STARTING_DECKS = [
    "labs/analog/analog-in-memory-foundation-model-hardware/spice/row_dac_settling_10bit.sp",
    "labs/analog/analog-in-memory-foundation-model-hardware/spice/sar_readout_12bit.sp",
    "labs/analog/analog-in-memory-foundation-model-hardware/spice/shared_converter_loading.sp",
    "labs/analog/analog-in-memory-foundation-model-hardware/spice/converter_supply_energy.sp",
]

DELIVERABLES = [
    {
        "name": "row_dac_layout",
        "target": "10-bit row-drive DAC path",
        "candidate_file": "evidence/aimc-simulator-adapters/candidate-post-layout/netlist/row_dac_extracted.sp",
        "payload_fields": ["extraction.extracted_netlist", "energy.dac_energy_per_row_drive", "latency.settling_time_ns"],
        "acceptance": "extracted netlist exists, includes row DAC path, and reports positive DAC row-drive energy and settling time",
    },
    {
        "name": "sar_readout_layout",
        "target": "12-bit sample/readout ADC path",
        "candidate_file": "evidence/aimc-simulator-adapters/candidate-post-layout/netlist/sar_readout_extracted.sp",
        "payload_fields": ["energy.adc_energy_per_conversion", "latency.conversion_time_ns", "noise.output_noise_rms"],
        "acceptance": "extracted netlist exists, includes sample path and SAR readout, and output noise is at or below 0.004 RMS",
    },
    {
        "name": "shared_mux_layout",
        "target": "shared converter mux and loading path",
        "candidate_file": "evidence/aimc-simulator-adapters/candidate-post-layout/netlist/shared_converter_mux_extracted.sp",
        "payload_fields": ["sharing.outputs_per_conversion_cost", "area.replication_or_sharing_rule"],
        "acceptance": "extracted netlist includes shared mux loading and preserves the 16-output sharing rule used by break-even",
    },
    {
        "name": "converter_macro_area",
        "target": "combined DAC, ADC, reference, mux, and sample layout boundary",
        "candidate_file": "evidence/aimc-simulator-adapters/candidate-post-layout/models/converter_layout_area_record.json",
        "payload_fields": ["area.adc_area_um2", "area.dac_area_um2"],
        "acceptance": "positive ADC and DAC area values come from the layout or extracted macro boundary",
    },
    {
        "name": "same_run_break_even_rerun",
        "target": "break-even decision using extracted converter values",
        "candidate_file": "evidence/aimc-simulator-adapters/candidate-post-layout/rerun/converter-post-layout-break-even-rerun.json",
        "payload_fields": ["break_even_rerun.rerun_artifact", "break_even_rerun.replacement_decision", "break_even_rerun.run_id"],
        "acceptance": "rerun artifact uses extracted energy, latency, noise, area, and the same sharing rule as the payload",
    },
]


def rel_exists(path: str) -> bool:
    full = ROOT / path
    return full.exists() and full.stat().st_size > 0


def layout_file_count() -> int:
    patterns = ["*.sch", "*.mag", "*.gds", "*.def", "*.lef", "*.dspf", "*.spef"]
    roots = [ROOT / "labs" / "analog", ROOT / "evidence" / "aimc-simulator-adapters" / "candidate-post-layout"]
    count = 0
    for root in roots:
        if not root.exists():
            continue
        for pattern in patterns:
            count += sum(1 for path in root.rglob(pattern) if path.is_file() and path.stat().st_size > 0)
    return count


def build_report() -> dict[str, Any]:
    starting_decks = [{"path": path, "exists": rel_exists(path)} for path in STARTING_DECKS]
    all_starting_decks_exist = all(item["exists"] for item in starting_decks)
    return {
        "result_type": "analog_converter_layout_work_order",
        "status": "layout_work_order_ready_waiting_for_converter_layout",
        "starting_spice_decks": starting_decks,
        "all_starting_spice_decks_exist": all_starting_decks_exist,
        "repo_local_analog_layout_file_count": layout_file_count(),
        "candidate_workspace": "evidence/aimc-simulator-adapters/candidate-post-layout",
        "deliverables": DELIVERABLES,
        "deliverable_count": len(DELIVERABLES),
        "strict_payload_after_work_order": [
            "python3 scripts/build_converter_post_layout_candidate_from_real_run.py --workspace evidence/aimc-simulator-adapters/candidate-post-layout ...",
            "python3 scripts/run_converter_post_layout_candidate_readiness.py",
            "python3 scripts/submit_converter_post_layout_payload.py evidence/aimc-simulator-adapters/candidate-post-layout/payload.json",
        ],
        "claim_boundary": {
            "allowed": "turns existing converter SPICE evidence into a concrete analog layout and extraction work order",
            "not_allowed": "does not create layout, does not create extracted netlists, does not fill measured values, and does not submit accepted post-layout evidence",
        },
    }


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# Analog Converter Layout Work Order",
        "",
        f"- status: `{report['status']}`",
        f"- all starting SPICE decks exist: `{report['all_starting_spice_decks_exist']}`",
        f"- repo-local analog layout file count: `{report['repo_local_analog_layout_file_count']}`",
        f"- deliverable count: `{report['deliverable_count']}`",
        "",
        "## First Principle",
        "",
        "The existing SPICE decks test behavior. A post-layout claim needs geometry. Geometry adds wire capacitance, wire resistance, device area, placement distance, reference loading, mux loading, and extracted timing. The work order exists to move from behavior decks to extracted converter objects without confusing the two.",
        "",
        "## Starting Decks",
        "",
    ]
    lines.extend(f"- `{item['path']}` exists `{item['exists']}`" for item in report["starting_spice_decks"])
    lines.extend(["", "## Deliverables", ""])
    for item in report["deliverables"]:
        lines.extend([
            f"### {item['name']}",
            "",
            f"- target: {item['target']}",
            f"- candidate file: `{item['candidate_file']}`",
            f"- payload fields: `{', '.join(item['payload_fields'])}`",
            f"- acceptance: {item['acceptance']}",
            "",
        ])
    lines.extend([
        "## Strict Payload Commands After Layout",
        "",
        *[f"- `{command}`" for command in report["strict_payload_after_work_order"]],
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
    print("analog_converter_layout_work_order")
    print(f"status,{report['status']}")
    print(f"all_starting_spice_decks_exist,{report['all_starting_spice_decks_exist']}")
    print(f"repo_local_analog_layout_file_count,{report['repo_local_analog_layout_file_count']}")
    print(f"deliverable_count,{report['deliverable_count']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
