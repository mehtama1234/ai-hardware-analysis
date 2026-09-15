#!/usr/bin/env python3
"""Build the guarded model-to-chip qualification decision.

This joins the workload contract to the *measured* circuit evidence.  It is
deliberately conservative: a measured but rejected corner or mismatch run is
reported as evidence of the open gate, never converted into a pass.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def load(path: Path) -> dict:
    with path.open() as f:
        return json.load(f)


def digest(obj: dict) -> str:
    body = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(body).hexdigest()


def corner(path: Path, root: Path) -> dict:
    d = load(path)
    return {
        "path": str(path.relative_to(root)),
        "status": d.get("status"),
        "measured": bool(d.get("measured")),
        "accepted": d.get("status") == "continuous_physical_sar_nominal_map_passed"
        and bool(d.get("all_conversions_correct"))
        and bool(d.get("conversion_coverage_complete")),
        "decision_values": d.get("decision_values"),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[3])
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--campaign-summary", type=Path, help="Optional downloaded Colab corner campaign summary")
    args = ap.parse_args()
    root = args.repo_root
    eda = root / "analog-digital-chip-design-eda/evidence/aimc-simulator-adapters"
    qual = root / "analog-in-memory-ai-inference/software-architecture/experiments/gpt2-hybrid-v1/qualification"

    nominal = eda / "colab-sky130-continuous-physical-sar-five-pwl50ps-clock100ps-cpu.json"
    ss = eda / "colab-sky130-continuous-sar-ss162-pwl02-clock02-cpu.json"
    sf = eda / "colab-sky130-continuous-sar-sf180-pwl02-clock02-cpu.json"
    ff = eda / "colab-ff-corner-api-20260910.json"
    fs = eda / "colab-fs-corner-api-20260910.json"
    mismatch = eda / "colab-mismatch-calibrated5-20260910-trial-000.json"
    energy = eda / "converter-supply-energy-spice-evidence.json"
    workload = qual / "profile-driven-workload-trace.json"
    cost = qual / "projection-cost-model.json"

    corners = {name: corner(path, root) for name, path in {"TT": nominal, "SS": ss, "SF": sf, "FF": ff, "FS": fs}.items() if path.exists()}
    campaign = None
    if args.campaign_summary and args.campaign_summary.exists():
        campaign = load(args.campaign_summary)
        for name, key in (("FS", "fs"), ("FF", "ff")):
            report = campaign.get("cases", {}).get(key, {}).get("report")
            if report is None:
                artifact = campaign.get("cases", {}).get(key, {}).get("artifact")
                candidates = []
                if artifact:
                    candidates.append(Path(artifact))
                    candidates.append(args.campaign_summary.parent / Path(artifact).name)
                for candidate in candidates:
                    if candidate.exists():
                        report = load(candidate)
                        break
            if report:
                corners[name] = {
                    "path": str(args.campaign_summary),
                    "status": report.get("status"),
                    "measured": bool(report.get("measured")),
                    "accepted": report.get("status") == "continuous_physical_sar_nominal_map_passed"
                    and bool(report.get("all_conversions_correct"))
                    and bool(report.get("conversion_coverage_complete")),
                    "decision_values": report.get("decision_values"),
                    "campaign_case": key,
                }
    md = load(mismatch) if mismatch.exists() else {}
    en = load(energy) if energy.exists() else {}
    wl = load(workload) if workload.exists() else {}
    cm = load(cost) if cost.exists() else {}
    mismatch_pass = bool(md.get("all_conversions_correct")) and md.get("status") == "continuous_physical_sar_nominal_map_passed"
    energy_simple_load_only = en.get("summary", {}).get("status") == "converter_supply_energy_spice_complete_simple_load"
    physical_checks = {
        "nominal_continuous_sar": corners.get("TT", {}).get("accepted", False),
        "all_pvt_corners_accepted": all(x["accepted"] for x in corners.values()) and len(corners) == 5,
        "mismatch_yield_campaign_accepted": mismatch_pass,
        "matched_converter_energy": bool(cm.get("coefficients")) and not cm.get("missing_coefficients"),
    }
    open_items = [k for k, passed in physical_checks.items() if not passed]
    result = {
        "schema_version": "physical-qualification-gate-v0.1",
        "result_type": "guarded_model_to_chip_qualification_gate",
        "decision": "authorized_analog_execution" if not open_items else "retain_native_digital_gpu_execution",
        "workload": {"source": str(workload.relative_to(root)), "vectors": wl.get("totals", {}).get("vectors"), "trace_digest": digest(wl) if wl else None},
        "campaign_summary": str(args.campaign_summary) if campaign else None,
        "circuit_evidence": {"corners": corners, "mismatch_trial": {"path": str(mismatch.relative_to(root)), "status": md.get("status"), "all_conversions_correct": md.get("all_conversions_correct")}, "simple_load_energy": {"path": str(energy.relative_to(root)), "status": en.get("summary", {}).get("status"), "worst_total_energy_j": en.get("summary", {}).get("worst_total_energy_j")}},
        "checks": physical_checks,
        "open_items": open_items,
        "next_actions": [
            "Run a fresh FS/FF calibrated continuous-SAR campaign with one-to-one code-map acceptance.",
            "Run an independent mismatch population and report legal-map yield without per-trial remap.",
            "Replace simple-load energy with matched extracted converter/array/controller coefficients.",
            "Only then populate projection-cost-model.json and replay the GPT-2 trace for analog-vs-digital break-even.",
        ],
        "claim_boundary": "Software and nominal circuit evidence do not authorize an analog GPT-2 claim while any PVT, mismatch, or matched-energy gate is open.",
    }
    result["artifact_sha256"] = digest(result)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"decision": result["decision"], "open_items": open_items, "output": str(args.output)}, indent=2))


if __name__ == "__main__":
    main()
