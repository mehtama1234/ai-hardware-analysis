#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MEASURE = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware" / "measurements"
SIM_EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
PLACEMENT = MEASURE / "backend-hardware-placement.json"
BRIDGE = SIM_EVIDENCE / "calibrated-residual-governor-bridge.json"
JSON_OUT = SIM_EVIDENCE / "residual-aware-placement-decisions.json"
CSV_OUT = MEASURE / "residual-aware-placement-decisions.csv"
MD_OUT = SIM_EVIDENCE / "residual-aware-placement-decisions.md"


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


SOURCE_MATCHING_MODE = "fixed_weight_matmul_family_match"


def accepted_bridge_rows(bridge: dict[str, object]) -> list[dict[str, object]]:
    rows = bridge.get("rows") if isinstance(bridge.get("rows"), list) else []
    return [
        row
        for row in rows
        if isinstance(row, dict)
        and row.get("accepted_as_positive_evidence") is True
        and row.get("governor_decision") == 1
    ]


def placement_source_hint(placement: dict[str, object]) -> str:
    rows = placement.get("placement_rows") if isinstance(placement.get("placement_rows"), list) else []
    operator_ids = " ".join(
        str(row.get("operator_id", "")).lower()
        for row in rows
        if isinstance(row, dict)
    )
    if any(token in operator_ids for token in ["attention", "attn", "query", "key", "value", "q_proj", "k_proj", "v_proj"]):
        return "attention_block"
    if any(token in operator_ids for token in ["dense", "mlp", "ffn", "feed_forward", "matmul"]):
        return "deep_transformer_mlp_stack"
    return "fixed_weight_matmul"


def selection_reason(source_id: object) -> str:
    if source_id == "deep_transformer_mlp_stack":
        return (
            "Backend operators are dense fixed-weight MatMul rows, so the calibrated deep transformer-MLP stack is the closest available fixture. "
            "The one-block transformer-MLP source remains the next fallback, and attention projection evidence remains a general fixed-weight projection fallback."
        )
    if source_id == "transformer_mlp_block":
        return (
            "Backend operators are dense fixed-weight MatMul rows, so calibrated transformer-MLP fixed-weight MatMul evidence is the closest available fixture. "
            "Attention projection evidence remains a general fixed-weight projection fallback, but it is not used first for this dense MLP-shaped placement."
        )
    return "The selected calibrated source is the closest accepted fixed-weight MatMul-family fixture available for these placement rows."


def select_bridge_row(placement: dict[str, object], bridge: dict[str, object]) -> tuple[dict[str, object], dict[str, object]]:
    accepted = accepted_bridge_rows(bridge)
    if not accepted:
        raise ValueError("no accepted calibrated residual bridge row")
    hint = placement_source_hint(placement)

    def score(row: dict[str, object]) -> tuple[int, float]:
        source_id = str(row.get("source_id") or "")
        if hint == "deep_transformer_mlp_stack":
            preference = {
                "deep_transformer_mlp_stack": 0,
                "transformer_mlp_block": 1,
                "attention_block": 2,
            }
            source_score = preference.get(source_id, 3)
        elif hint == "attention_block":
            source_score = 0 if source_id == "attention_block" else 1
        else:
            source_score = 0
        return (source_score, float(row.get("residual_relative") or 1.0))

    selected = min(accepted, key=score)
    policy = {
        "mode": SOURCE_MATCHING_MODE,
        "placement_source_hint": hint,
        "selected_source": selected.get("source_id"),
        "selected_target": selected.get("target_object"),
        "selection_reason": selection_reason(selected.get("source_id")),
        "refused_inheritance": [
            "bias additions",
            "activation functions",
            "softmax",
            "dynamic attention score computation",
            "residual adds",
            "silicon or board performance",
        ],
        "accepted_sources_considered": [
            {
                "source_id": row.get("source_id"),
                "target_object": row.get("target_object"),
                "tool": row.get("tool"),
                "residual_q8": row.get("residual_q8"),
                "residual_relative": row.get("residual_relative"),
                "calibration_profile": row.get("calibration_profile"),
            }
            for row in accepted
        ],
    }
    return selected, policy


def decision_rows(placement: dict[str, object], bridge_row: dict[str, object], source_policy: dict[str, object]) -> list[dict[str, object]]:
    rows = placement.get("placement_rows") if isinstance(placement.get("placement_rows"), list) else []
    out: list[dict[str, object]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        governor = row.get("governor_fields") if isinstance(row.get("governor_fields"), dict) else {}
        structural_candidate = row.get("analog_candidate") is True and row.get("operator_kind") == "MatMul"
        if structural_candidate:
            calibrated_candidate = bool(bridge_row.get("accepted_as_positive_evidence"))
            final_decision = "analog_allowed" if calibrated_candidate else "digital_fallback"
            residual_q8 = int(bridge_row.get("residual_q8") or 0)
            sensitivity_q8 = int(bridge_row.get("sensitivity_q8") or governor.get("sensitivity_q8") or 0)
            evidence_tool = bridge_row.get("tool")
            evidence_source = bridge_row.get("source_id")
            evidence_target = bridge_row.get("target_object")
            evidence_profile = bridge_row.get("calibration_profile")
            source_match_reason = source_policy.get("selection_reason")
            reason = (
                "structural MatMul candidate and source-matched calibrated residual bridge passed"
                if calibrated_candidate
                else "structural MatMul candidate but calibrated residual bridge did not pass"
            )
        else:
            final_decision = "digital_fallback"
            residual_q8 = int(governor.get("residual_q8") or 0)
            sensitivity_q8 = int(governor.get("sensitivity_q8") or 0)
            evidence_tool = "not_used"
            evidence_source = "not_used"
            evidence_target = "not_used"
            evidence_profile = "not_used"
            source_match_reason = "calibrated MatMul evidence is not inherited by non-MatMul support operators"
            reason = row.get("digital_only_reason") or "not a structural analog candidate"
        out.append(
            {
                "operator_id": row.get("operator_id"),
                "operator_kind": row.get("operator_kind"),
                "structural_placement": row.get("placement"),
                "structural_analog_candidate": int(bool(row.get("analog_candidate"))),
                "residual_aware_decision": final_decision,
                "residual_q8": residual_q8,
                "sensitivity_q8": sensitivity_q8,
                "evidence_tool": evidence_tool,
                "evidence_source": evidence_source,
                "evidence_target": evidence_target,
                "calibration_profile": evidence_profile,
                "source_match_policy": source_policy.get("mode"),
                "source_match_reason": source_match_reason,
                "decision_reason": reason,
                "boundary": "backend operator shape plus calibrated simulator residual; not silicon or board measurement",
            }
        )
    return out


def write_csv(rows: list[dict[str, object]]) -> None:
    fieldnames = [
        "operator_id",
        "operator_kind",
        "structural_placement",
        "structural_analog_candidate",
        "residual_aware_decision",
        "residual_q8",
        "sensitivity_q8",
        "evidence_tool",
        "evidence_source",
        "evidence_target",
        "calibration_profile",
        "source_match_policy",
        "source_match_reason",
        "decision_reason",
        "boundary",
    ]
    with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(rows: list[dict[str, object]], bridge_row: dict[str, object], source_policy: dict[str, object]) -> None:
    lines = [
        "# Residual-Aware Placement Decisions",
        "",
        "This report joins structural placement with calibrated simulator evidence.",
        "",
        "The backend placement says which operators are shaped like analog work. The calibrated residual bridge says whether the available simulator evidence is strong enough to request analog service today.",
        "",
        "## Source Evidence",
        "",
        f"- placement: `{PLACEMENT.relative_to(ROOT)}`",
        f"- calibrated bridge: `{BRIDGE.relative_to(ROOT)}`",
        f"- accepted tool: `{bridge_row.get('tool')}`",
        f"- accepted source: `{bridge_row.get('source_id')}`",
        f"- accepted target: `{bridge_row.get('target_object')}`",
        f"- calibration profile: `{bridge_row.get('calibration_profile')}`",
        f"- residual q8: `{bridge_row.get('residual_q8')}`",
        f"- source matching policy: `{source_policy.get('mode')}`",
        f"- placement source hint: `{source_policy.get('placement_source_hint')}`",
        f"- selected source reason: {source_policy.get('selection_reason')}",
        "",
        "## Decisions",
        "",
        "| operator | kind | structural placement | structural candidate | residual-aware decision | residual q8 | evidence source | evidence tool |",
        "| --- | --- | --- | ---: | --- | ---: | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row['operator_id']} | {row['operator_kind']} | {row['structural_placement']} | "
            f"{row['structural_analog_candidate']} | {row['residual_aware_decision']} | "
            f"{row['residual_q8']} | {row['evidence_source']} | {row['evidence_tool']} |"
        )
    lines.extend(
        [
            "",
            "## First-Principles Reading",
            "",
            "Placement and acceptance are different decisions.",
            "",
            "A matrix multiply is a good structural match for an analog array because fixed weights can sit as conductances and input values can arrive as row voltages. That only says the operator has the right shape. It does not say the current analog path is accurate enough.",
            "",
            "The residual-aware decision adds the missing second step. It asks whether a calibrated simulator payload passed the strict evidence rule, then asks whether that payload is the right kind of source for the backend operator. In the current local run, the backend rows are dense MatMul rows, so the transformer-MLP source is selected ahead of the attention source even though both CrossSim rows pass. Non-MatMul rows stay digital because calibration evidence for a matrix multiply should not be used to justify bias, activation, softmax, dynamic attention work, or residual adds.",
            "",
            "## Refused Claim",
            "",
            "This does not prove analog macro layout, silicon calibration, board latency, board power, analog softmax, pretrained model accuracy, signoff, or tapeout readiness.",
            "",
        ]
    )
    MD_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    placement = load_json(PLACEMENT)
    bridge = load_json(BRIDGE)
    bridge_row, source_policy = select_bridge_row(placement, bridge)
    rows = decision_rows(placement, bridge_row, source_policy)
    if not rows:
        raise SystemExit("no placement rows found")
    analog_allowed = sum(1 for row in rows if row["residual_aware_decision"] == "analog_allowed")
    if analog_allowed < 1:
        raise SystemExit("no residual-aware analog placement decisions")
    JSON_OUT.write_text(
        json.dumps(
            {
                "result_type": "residual_aware_placement_decisions",
                "source_placement": str(PLACEMENT.relative_to(ROOT)),
                "source_calibrated_bridge": str(BRIDGE.relative_to(ROOT)),
                "accepted_calibrated_tool": bridge_row.get("tool"),
                "accepted_calibrated_source": bridge_row.get("source_id"),
                "accepted_calibrated_target": bridge_row.get("target_object"),
                "source_matching_policy": source_policy,
                "rows": rows,
                "summary": {
                    "operators": len(rows),
                    "structural_analog_candidates": sum(1 for row in rows if row["structural_analog_candidate"] == 1),
                    "residual_aware_analog_allowed": analog_allowed,
                    "digital_fallback": sum(1 for row in rows if row["residual_aware_decision"] == "digital_fallback"),
                },
                "claim_boundary": {
                    "allowed": "backend placement rows are filtered through calibrated simulator residual evidence",
                    "not_allowed": "does not prove silicon behavior, measured board performance, full compiler lowering, physical signoff, or production readiness",
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    write_csv(rows)
    write_markdown(rows, bridge_row, source_policy)
    print("residual_aware_placement_decisions")
    print(f"operators,{len(rows)}")
    print(f"structural_analog_candidates,{sum(1 for row in rows if row['structural_analog_candidate'] == 1)}")
    print(f"residual_aware_analog_allowed,{analog_allowed}")
    print(f"json,{JSON_OUT}")
    print(f"csv,{CSV_OUT}")
    print(f"markdown,{MD_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
