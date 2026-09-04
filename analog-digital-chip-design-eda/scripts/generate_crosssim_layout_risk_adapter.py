#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MEASURE = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware" / "measurements"
SIM_EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
RESIDUAL = SIM_EVIDENCE / "residual-aware-placement-decisions.json"
TILE = MEASURE / "tile-operating-point.csv"
JSON_OUT = SIM_EVIDENCE / "crosssim-layout-risk-adapter.json"
CSV_OUT = MEASURE / "crosssim-layout-risk-adapter.csv"
MD_OUT = SIM_EVIDENCE / "crosssim-layout-risk-adapter.md"


def load_residual() -> dict[str, object]:
    return json.loads(RESIDUAL.read_text(encoding="utf-8"))


def load_tile() -> dict[str, str]:
    with TILE.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise SystemExit(f"missing tile operating point rows: {TILE}")
    return rows[0]


def as_float(row: dict[str, str], key: str, default: float = 0.0) -> float:
    try:
        return float(row.get(key, default))
    except (TypeError, ValueError):
        return default


def as_int(row: dict[str, str], key: str, default: int = 0) -> int:
    try:
        return int(float(row.get(key, default)))
    except (TypeError, ValueError):
        return default


def analog_rows(residual: dict[str, object]) -> list[dict[str, object]]:
    rows = residual.get("rows") if isinstance(residual.get("rows"), list) else []
    selected = [
        row
        for row in rows
        if isinstance(row, dict)
        and row.get("residual_aware_decision") == "analog_allowed"
        and row.get("evidence_tool") == "crosssim"
    ]
    if not selected:
        raise SystemExit("no CrossSim-backed analog-allowed rows found")
    return selected


def infer_dims(operator_id: str) -> tuple[int, int]:
    if operator_id == "dense1.matmul":
        return (4, 4)
    if operator_id == "dense2.matmul":
        return (4, 2)
    return (4, 4)


def risk_level(score: int) -> str:
    if score >= 8:
        return "blocked"
    if score >= 4:
        return "review"
    return "bounded"


def row_record(row: dict[str, object], tile: dict[str, str]) -> dict[str, object]:
    input_dim, output_dim = infer_dims(str(row.get("operator_id")))
    adc_bits = as_int(tile, "adc_bits")
    dac_bits = as_int(tile, "dac_bits")
    row_wire_ohm = as_float(tile, "row_drop_case_ohm")
    row_drop_pct = as_float(tile, "spice_row_drop_loss_pct")
    converter_error = as_float(tile, "converter_relative_error")
    converter_energy_relative = as_float(tile, "converter_energy_relative")
    residual_q8 = int(row.get("residual_q8") or 0)
    sensitivity_q8 = int(row.get("sensitivity_q8") or 0)

    bit_slices = max(1, math.ceil(8 / max(dac_bits, 1)))
    column_current_min_ua = round(output_dim * 0.8, 3)
    column_current_typ_ua = round(output_dim * input_dim * 1.25, 3)
    column_current_max_ua = round(output_dim * input_dim * 2.6, 3)

    issues: list[str] = []
    if adc_bits < 7:
        issues.append("ADC range is coarse for a positive analog claim")
    if dac_bits < 6:
        issues.append("DAC precision needs digital scaling and error budget")
    if row_drop_pct > 5.0:
        issues.append("row-wire loss is visible and must stay in the layout boundary")
    if converter_error > 0.08:
        issues.append("converter error is a first-order part of the analog result")
    if sensitivity_q8 > 160:
        issues.append("model sensitivity is high enough that small physical shifts need review")

    score = len(issues) + (1 if column_current_max_ua > 32.0 else 0) + (1 if bit_slices > 1 else 0)
    level = risk_level(score)
    return {
        "operator_id": row.get("operator_id"),
        "operator_kind": row.get("operator_kind"),
        "evidence_source": row.get("evidence_source"),
        "evidence_target": row.get("evidence_target"),
        "calibration_profile": row.get("calibration_profile"),
        "source_match_policy": row.get("source_match_policy"),
        "array": {
            "rows": input_dim,
            "columns": output_dim,
            "mapped_operation": "fixed-weight MatMul",
            "weight_storage": "signed weights represented as conductance-coded terms before digital correction",
        },
        "converter": {
            "adc_bits": adc_bits,
            "dac_bits": dac_bits,
            "bit_slices": bit_slices,
            "adc_range": "bounded by local tile operating point; no measured silicon range",
            "dac_precision": "activation code is split into DAC-driven row-voltage steps",
            "converter_relative_error": converter_error,
            "converter_energy_relative": converter_energy_relative,
        },
        "wire": {
            "row_wire_case_ohm": row_wire_ohm,
            "spice_row_drop_loss_pct": row_drop_pct,
            "assumption": "single local row-drop case, not extracted routed macro parasitics",
        },
        "column_current": {
            "min_ua": column_current_min_ua,
            "typ_ua": column_current_typ_ua,
            "max_ua": column_current_max_ua,
            "assumption": "local dimension-scaled estimate for review; not measured current",
        },
        "model_boundary": {
            "residual_q8": residual_q8,
            "sensitivity_q8": sensitivity_q8,
            "accepted_tool": "crosssim",
            "accepted_residual_boundary": "residual-aware placement allowed this row, but layout risk is checked separately",
        },
        "risk": {
            "level": level,
            "score": score,
            "issues": issues,
        },
        "claim_effect": "physical layout risk record only; does not upgrade to analog macro signoff",
    }


def write_csv(records: list[dict[str, object]]) -> None:
    fieldnames = [
        "operator_id",
        "rows",
        "columns",
        "adc_bits",
        "dac_bits",
        "bit_slices",
        "row_wire_case_ohm",
        "spice_row_drop_loss_pct",
        "column_current_min_ua",
        "column_current_typ_ua",
        "column_current_max_ua",
        "residual_q8",
        "sensitivity_q8",
        "risk_level",
        "risk_score",
    ]
    with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow(
                {
                    "operator_id": record["operator_id"],
                    "rows": record["array"]["rows"],
                    "columns": record["array"]["columns"],
                    "adc_bits": record["converter"]["adc_bits"],
                    "dac_bits": record["converter"]["dac_bits"],
                    "bit_slices": record["converter"]["bit_slices"],
                    "row_wire_case_ohm": record["wire"]["row_wire_case_ohm"],
                    "spice_row_drop_loss_pct": record["wire"]["spice_row_drop_loss_pct"],
                    "column_current_min_ua": record["column_current"]["min_ua"],
                    "column_current_typ_ua": record["column_current"]["typ_ua"],
                    "column_current_max_ua": record["column_current"]["max_ua"],
                    "residual_q8": record["model_boundary"]["residual_q8"],
                    "sensitivity_q8": record["model_boundary"]["sensitivity_q8"],
                    "risk_level": record["risk"]["level"],
                    "risk_score": record["risk"]["score"],
                }
            )


def write_markdown(records: list[dict[str, object]], residual: dict[str, object]) -> None:
    lines = [
        "# CrossSim Layout-Risk Adapter",
        "",
        "This report separates model residual evidence from physical layout risk.",
        "",
        "CrossSim can say whether the fixed-weight MatMul output stayed close to the digital reference under the current simulator assumptions. It does not prove that a real macro layout has acceptable wire drop, converter range, bit slicing, column current, extraction, DRC, LVS, or silicon behavior.",
        "",
        "## Source Evidence",
        "",
        f"- residual-aware placement: `{RESIDUAL.relative_to(ROOT)}`",
        f"- tile operating point: `{TILE.relative_to(ROOT)}`",
        f"- accepted source: `{residual.get('accepted_calibrated_source')}`",
        f"- accepted tool: `{residual.get('accepted_calibrated_tool')}`",
        f"- source matching policy: `{residual.get('source_matching_policy', {}).get('mode')}`",
        "",
        "## Layout-Risk Rows",
        "",
        "| operator | array | ADC | DAC | bit slices | row wire ohm | row-drop loss % | column current range uA | risk |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for record in records:
        current = record["column_current"]
        lines.append(
            f"| {record['operator_id']} | {record['array']['rows']}x{record['array']['columns']} | "
            f"{record['converter']['adc_bits']} | {record['converter']['dac_bits']} | {record['converter']['bit_slices']} | "
            f"{record['wire']['row_wire_case_ohm']} | {record['wire']['spice_row_drop_loss_pct']:.3f} | "
            f"{current['min_ua']}-{current['max_ua']} | {record['risk']['level']} |"
        )
    lines.extend(
        [
            "",
            "## First-Principles Reading",
            "",
            "An analog MatMul row is not one object. It is a chain.",
            "",
            "A weight becomes conductance. An activation becomes a row voltage. Each cell turns voltage and conductance into current. The column sums current. The ADC turns that current back into a number. The digital side rescales, corrects, accumulates, and decides whether the result can stay in the model path.",
            "",
            "The residual score checks the end of that chain. The layout-risk record checks the middle of the chain. A low residual is still incomplete if the assumed row wire, converter range, bit slicing, or column current would be unrealistic in layout.",
            "",
            "## Refused Claim",
            "",
            "This record does not prove analog macro layout, routed parasitic extraction, DRC, LVS, calibrated silicon, measured latency, measured energy, package reliability, production readiness, or tapeout readiness.",
            "",
        ]
    )
    MD_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    residual = load_residual()
    tile = load_tile()
    records = [row_record(row, tile) for row in analog_rows(residual)]
    payload = {
        "result_type": "crosssim_layout_risk_adapter",
        "schema_version": "crosssim-layout-risk-adapter-v0.1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_artifacts": {
            "residual_aware_placement": str(RESIDUAL.relative_to(ROOT)),
            "tile_operating_point": str(TILE.relative_to(ROOT)),
        },
        "accepted_calibrated_source": residual.get("accepted_calibrated_source"),
        "accepted_calibrated_tool": residual.get("accepted_calibrated_tool"),
        "source_matching_policy": residual.get("source_matching_policy", {}).get("mode"),
        "rows": records,
        "summary": {
            "operators": len(records),
            "bounded": sum(1 for row in records if row["risk"]["level"] == "bounded"),
            "review": sum(1 for row in records if row["risk"]["level"] == "review"),
            "blocked": sum(1 for row in records if row["risk"]["level"] == "blocked"),
        },
        "claim_boundary": {
            "allowed": "records layout-risk assumptions for CrossSim-backed analog-allowed MatMul rows",
            "not_allowed": "does not prove analog macro layout, extraction, DRC/LVS, calibrated silicon, measured board performance, or production readiness",
        },
    }
    JSON_OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv(records)
    write_markdown(records, residual)
    print("crosssim_layout_risk_adapter")
    print(f"operators,{len(records)}")
    print(f"review,{payload['summary']['review']}")
    print(f"blocked,{payload['summary']['blocked']}")
    print(f"json,{JSON_OUT}")
    print(f"csv,{CSV_OUT}")
    print(f"markdown,{MD_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
