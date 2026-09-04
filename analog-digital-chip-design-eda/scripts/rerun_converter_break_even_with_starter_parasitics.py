#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "evidence" / "aimc-simulator-adapters" / "aihwkit-converter-break-even.json"
PARASITIC = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-starter-parasitic-load-estimate.json"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-starter-parasitic-break-even-rerun.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-starter-parasitic-break-even-rerun.md"


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_report() -> dict[str, Any]:
    base = load(BASE)
    parasitic = load(PARASITIC)
    pin_energy_j = float(parasitic["total_estimated_pin_charge_energy_j"])
    max_settle_s = float(parasitic["max_settle_0p1pct_s"])
    base_energy_unit_j = 1e-12
    parasitic_energy_units = pin_energy_j / base_energy_unit_j
    scenarios = []
    for item in base["scenarios"]:
        sharing = float(item["amortized_outputs_per_conversion"])
        parasitic_per_output = parasitic_energy_units / sharing
        adjusted = float(item["target_analog_energy_per_output"]) + parasitic_per_output
        digital = float(item["digital_energy_per_output"])
        scenarios.append(
            {
                "name": item["name"],
                "rows": item["rows"],
                "amortized_outputs_per_conversion": item["amortized_outputs_per_conversion"],
                "base_target_analog_energy_per_output": item["target_analog_energy_per_output"],
                "starter_parasitic_energy_per_output": parasitic_per_output,
                "adjusted_target_analog_energy_per_output": adjusted,
                "digital_energy_per_output": digital,
                "adjusted_margin_vs_digital_per_output": digital - adjusted,
                "adjusted_beats_digital": digital > adjusted,
            }
        )
    first_passing = next((item for item in scenarios if item["adjusted_beats_digital"]), None)
    return {
        "result_type": "converter_starter_parasitic_break_even_rerun",
        "status": "starter_parasitic_break_even_rerun_complete_not_accepted_evidence",
        "source_artifacts": {
            "base_break_even": rel(BASE),
            "starter_parasitic_load_estimate": rel(PARASITIC),
        },
        "base_energy_unit_j": base_energy_unit_j,
        "starter_total_pin_charge_energy_j": pin_energy_j,
        "starter_total_pin_charge_energy_in_base_units": parasitic_energy_units,
        "starter_max_settle_0p1pct_s": max_settle_s,
        "scenario_count": len(scenarios),
        "passing_scenario_count": sum(1 for item in scenarios if item["adjusted_beats_digital"]),
        "first_passing_scenario": first_passing["name"] if first_passing else None,
        "scenarios": scenarios,
        "replacement_decision": "keep_digital_fallback_until_real_converter_post_layout_measurement",
        "candidate_post_layout_written": False,
        "accepted_post_layout_written": False,
        "claim_boundary": {
            "allowed": "shows how extracted starter capacitance would perturb the local break-even scenarios if one normalized energy unit is one picojoule",
            "not_allowed": "does not replace real ADC/DAC energy, transistor settling, noise, supply-current integration, physical area signoff, or accepted post-layout evidence",
        },
    }


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# Converter Starter Parasitic Break-Even Rerun",
        "",
        f"- status: `{report['status']}`",
        f"- base energy unit J: `{report['base_energy_unit_j']:.6e}`",
        f"- starter total pin charge energy J: `{report['starter_total_pin_charge_energy_j']:.6e}`",
        f"- starter total pin charge energy in base units: `{report['starter_total_pin_charge_energy_in_base_units']:.6e}`",
        f"- starter max settle 0.1 percent s: `{report['starter_max_settle_0p1pct_s']:.6e}`",
        f"- passing scenario count: `{report['passing_scenario_count']}` of `{report['scenario_count']}`",
        f"- first passing scenario: `{report['first_passing_scenario']}`",
        f"- replacement decision: `{report['replacement_decision']}`",
        f"- candidate post-layout written: `{report['candidate_post_layout_written']}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        "",
        "## First Principle",
        "",
        "A parasitic load changes the break-even question only through the extra charge that must be moved and the extra time needed to settle that charge. If the load is tiny next to the converter energy model, it should not change the scenario decision. If it is large, it can erase the energy margin that made analog look useful.",
        "",
        "This rerun keeps that accounting honest. It adds only the extracted starter capacitance energy. It does not pretend that capacitance is the full converter, because a converter also needs transistor switching, references, comparator decisions, mismatch, and supply-current integration.",
        "",
        "## Scenario Table",
        "",
        "| scenario | sharing | base analog/output | added parasitic/output | adjusted analog/output | digital/output | adjusted margin | beats digital |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for item in report["scenarios"]:
        lines.append(
            f"| {item['name']} | {item['amortized_outputs_per_conversion']} | "
            f"`{item['base_target_analog_energy_per_output']:.6f}` | "
            f"`{item['starter_parasitic_energy_per_output']:.6e}` | "
            f"`{item['adjusted_target_analog_energy_per_output']:.6f}` | "
            f"`{item['digital_energy_per_output']:.6f}` | "
            f"`{item['adjusted_margin_vs_digital_per_output']:.6f}` | "
            f"`{item['adjusted_beats_digital']}` |"
        )
    lines.extend(["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print("converter_starter_parasitic_break_even_rerun")
    print(f"status,{report['status']}")
    print(f"starter_total_pin_charge_energy_j,{report['starter_total_pin_charge_energy_j']:.6e}")
    print(f"passing_scenario_count,{report['passing_scenario_count']}")
    print(f"first_passing_scenario,{report['first_passing_scenario']}")
    print(f"replacement_decision,{report['replacement_decision']}")
    print(f"candidate_post_layout_written,{report['candidate_post_layout_written']}")
    print(f"accepted_post_layout_written,{report['accepted_post_layout_written']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
