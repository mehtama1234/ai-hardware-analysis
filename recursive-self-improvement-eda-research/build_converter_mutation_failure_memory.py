#!/usr/bin/env python3
"""Build failure-aware memory for converter topology mutations.

This memory is deliberately separate from the workload-placement Q table:
converter geometry and feedback actions have different state/action semantics.
Only source artifacts with retained per-candidate outcomes enter the memory;
the result is proposal guidance, never runtime authorization.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCES = [
    ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/expanded-regulated-cascode-search.json",
    ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/regulated-geometry-linearization-search.json",
    ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/regulated-cascode-load-mutation-search.json",
    ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/differential-correction-base-mutation-search.json",
    ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/differential-correction-gate-bias-search.json",
    ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/differential-cascode-correction-search.json",
    ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/differential-feedback-correction-search.json",
    ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/differential-feedback-correction-width-refinement-search.json",
    ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/differential-feedback-finger-refinement-search.json",
    ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/differential-cascode-group-bias-search.json",
    ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/differential-active-feedback-search.json",
    ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/differential-active-feedback-refinement-search.json",
    ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/differential-active-feedback-shared-bias-search.json",
    ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/differential-active-feedback-mos-reference-search.json",
    ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/differential-active-feedback-mos-reference-geometry-stress.json",
    ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/differential-active-feedback-correction-width-search.json",
    ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/differential-active-feedback-gate-drive-search.json",
    ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/differential-active-feedback-input-pair-width-search.json",
    ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/differential-active-feedback-tail-width-search.json",
    ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/differential-active-feedback-grouped-reference-search.json",
    ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/differential-active-feedback-grouped-reference-sensitivity-search.json",
    ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/differential-active-feedback-group0-nmos-refinement.json",
    ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/differential-active-feedback-group0-nmos-lower-range-search.json",
    ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/differential-active-feedback-group0-nmos-min-geometry-search.json",
    ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/differential-active-feedback-group1-nmos-search.json",
    ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/differential-active-feedback-group2-nmos-search.json",
    ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/code-dependent-transfer-shaping-search.json",
    ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/residue-injection-topology-search.json",
    ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/code-dependent-residue-refinement.json",
    ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/segmented-residue-topology-search.json",
    ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/segmented-residue-branch-refinement.json",
    ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/source-degenerated-feedback-search.json",
    ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/charge-redistribution-search.json",
    ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/per-branch-feedback-trim-search.json",
]
MOS_REFERENCE_RESULTS = ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results"
DEFAULT_SOURCES.extend(
    path for path in sorted(MOS_REFERENCE_RESULTS.glob("differential-active-feedback-mos-reference-refinement-*.json"))
    if not path.name.endswith("-provenance.json")
)
DEFAULT_OUT = Path(__file__).resolve().parent / "converter-mutation-failure-memory.json"
SCHEMA_VERSION = "recursive_converter_mutation_failure_memory.v3"
ACTION_KEYS = (
    "bias_v", "feedback_gain", "regulated_target_v", "nmos_widths", "pmos_load_width",
    "correction_width", "finger_count", "correction_device", "correction_gate_fraction",
    "base_widths", "load_width", "correction_topology", "cascode_width", "cascode_bias_fraction",
    "feedback_resistance_ohm", "bias_resistance_ohm",
    "feedback_reference_fraction", "feedback_tail_gate_fraction", "feedback_input_width",
    "feedback_tail_width", "feedback_load_width", "feedback_compensation_cap",
    "feedback_reference_topology",
    "feedback_reference_pmos_width", "feedback_reference_nmos_width",
    "feedback_bias_topology", "feedback_tail_bias_resistance_ohm",
    "feedback_reference_divider_resistance_ohm",
    "source_degeneration_resistance_ohm",
    "charge_redistribution_cap",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def signature(row: dict) -> str:
    action = {key: row[key] for key in ACTION_KEYS if key in row}
    return json.dumps(action, sort_keys=True, separators=(",", ":"))


def outcome(row: dict) -> tuple[str, float | None, list[str]]:
    summary = row.get("summary", {})
    if not isinstance(summary, dict):
        summary = {}
    max_inl = summary.get("max_inl_lsb")
    errors = []
    finite_inl = None
    if isinstance(max_inl, (int, float)) and not isinstance(max_inl, bool):
        try:
            candidate_inl = float(max_inl)
        except (OverflowError, ValueError):
            candidate_inl = math.nan
        if math.isfinite(candidate_inl):
            finite_inl = candidate_inl
    valid_inl = finite_inl is not None
    if row.get("status") != "passed":
        errors.append("simulator_or_model_blocked")
    if summary.get("all_monotonic") is not True:
        errors.append("non_monotonic")
    if summary.get("all_settled") is not True:
        errors.append("settling_gate")
    if not valid_inl:
        errors.append("missing_or_nonfinite_inl")
    elif finite_inl > 0.5:
        errors.append("inl_gate")
    if not errors:
        return "eligible_for_further_gates", finite_inl, errors
    return "rejected", finite_inl if valid_inl else None, errors


def reference_voltage_summary(row: dict) -> dict:
    """Keep finite measured reference-node coverage compactly by PVT corner."""
    result = {}
    corners = row.get("corners", [])
    if not isinstance(corners, list):
        return result
    for corner in corners:
        if not isinstance(corner, dict) or not isinstance(corner.get("corner"), str):
            continue
        codes = corner.get("codes", [])
        if not isinstance(codes, list):
            continue
        values = []
        for code in codes:
            if not isinstance(code, dict):
                continue
            value = code.get("reference_voltage_v")
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                value = float(value)
                if math.isfinite(value):
                    values.append(value)
        if values:
            result[corner["corner"]] = {
                "measurement_count": len(values), "minimum_v": min(values),
                "maximum_v": max(values), "mean_v": sum(values) / len(values),
            }
    return result


def build(sources: list[Path]) -> dict:
    entries = []
    source_records = []
    for source in sources:
        if not source.is_file():
            continue
        document = json.loads(source.read_text())
        source_records.append({"path": str(source.relative_to(ROOT)), "sha256": digest(source)})
        for row in document.get("candidates", []):
            status, max_inl, reasons = outcome(row)
            entries.append({
                "family": document.get("schema_version", source.stem),
                "source": str(source.relative_to(ROOT)),
                "action": {key: row[key] for key in ACTION_KEYS if key in row},
                "signature": signature(row),
                "outcome": status,
                "max_inl_lsb": max_inl,
                "reference_voltage_summary_by_corner": reference_voltage_summary(row),
                "rejection_reasons": reasons,
            })

    grouped: dict[str, dict] = defaultdict(lambda: {"attempts": 0, "rejections": 0,
                                                      "best_max_inl_lsb": None,
                                                      "rejection_reasons": set()})
    for entry in entries:
        item = grouped[entry["signature"]]
        item["attempts"] += 1
        if entry["outcome"] == "rejected":
            item["rejections"] += 1
            item["rejection_reasons"].update(entry["rejection_reasons"])
        value = entry["max_inl_lsb"]
        if isinstance(value, (int, float)) and (item["best_max_inl_lsb"] is None or value < item["best_max_inl_lsb"]):
            item["best_max_inl_lsb"] = value
    memory = []
    for key, item in sorted(grouped.items()):
        memory.append({"signature": key, "attempts": item["attempts"],
                       "rejections": item["rejections"],
                       "safe_rate": (item["attempts"] - item["rejections"]) / item["attempts"],
                       "best_max_inl_lsb": item["best_max_inl_lsb"],
                       "rejection_reasons": sorted(item["rejection_reasons"])})
    rejected = sum(entry["outcome"] == "rejected" for entry in entries)
    return {
        "schema_version": SCHEMA_VERSION,
        "source_records": source_records,
        "entries": entries,
        "memory": memory,
        "summary": {"source_count": len(source_records), "entry_count": len(entries),
                     "unique_action_count": len(memory), "rejected_entry_count": rejected,
                     "eligible_entry_count": len(entries) - rejected,
                     "promotion_gate_lsb": 0.5},
        "claim_boundary": "Failure-aware proposal memory for simulator converter mutations only; it does not establish analog hardware, energy, runtime benefit, or deployment authorization.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, action="append", default=None)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    result = build(args.source or DEFAULT_SOURCES)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "passed" if result["summary"]["entry_count"] else "blocked",
                      "summary": result["summary"], "output": str(args.output)}, indent=2))
    return 0 if result["summary"]["entry_count"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
