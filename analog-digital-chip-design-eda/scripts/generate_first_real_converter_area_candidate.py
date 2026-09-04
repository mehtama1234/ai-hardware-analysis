#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
CANDIDATE = EVIDENCE / "candidate-post-layout"
OBJECT_AUDIT = EVIDENCE / "first-real-converter-physical-object-audit.json"
STARTER_PAYLOAD = EVIDENCE / "starter-post-layout-candidate" / "payload.json"
OUT_JSON = EVIDENCE / "first-real-converter-area-candidate.json"
OUT_MD = EVIDENCE / "first-real-converter-area-candidate.md"
MEASUREMENT_JSON = CANDIDATE / "measurements" / "readout-area.json"


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"missing input artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def positive(value: Any, name: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0:
        raise SystemExit(f"{name} must be positive")
    return float(value)


def build_report() -> dict[str, Any]:
    object_audit = load_json(OBJECT_AUDIT)
    starter = load_json(STARTER_PAYLOAD)
    if object_audit.get("ready_for_b1") is not True:
        raise SystemExit("B1 physical object must be ready before generating B5 candidate area")
    area = starter["area"]
    adc_area = positive(area["adc_area_um2"], "adc_area_um2")
    dac_area = positive(area["dac_area_um2"], "dac_area_um2")
    measurement = {
        "result_type": "first_real_converter_readout_area_candidate",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "candidate_id": "aimc_readout_candidate_001",
        "run_id": "aimc_readout_candidate_001_starter_area_run001",
        "area_level": "starter_layout_boundary_estimate_tied_to_named_candidate_not_extracted_signoff_area",
        "source_area_artifact": rel(STARTER_PAYLOAD),
        "source_netlist": object_audit["expected_extracted_netlist"],
        "adc_area_um2": adc_area,
        "dac_area_um2": dac_area,
        "total_readout_area_um2": adc_area + dac_area,
        "method": area["method"],
        "replication_or_sharing_rule": area["replication_or_sharing_rule"],
        "strict_payload_ready": False,
        "why_not_strict": [
            "the source area is a starter macro boundary estimate",
            "the candidate does not carry DRC/LVS-clean physical area records",
            "the area was not recomputed from the assembled candidate layout boundary",
        ],
    }
    MEASUREMENT_JSON.parent.mkdir(parents=True, exist_ok=True)
    MEASUREMENT_JSON.write_text(json.dumps(measurement, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "result_type": "first_real_converter_area_candidate",
        "created_at": measurement["created_at"],
        "status": "b5_area_candidate_written_not_strict_extracted_area",
        "candidate_id": measurement["candidate_id"],
        "run_id": measurement["run_id"],
        "measurement_artifact": rel(MEASUREMENT_JSON),
        "source_area_artifact": rel(STARTER_PAYLOAD),
        "source_netlist": measurement["source_netlist"],
        "adc_area_um2": adc_area,
        "dac_area_um2": dac_area,
        "total_readout_area_um2": adc_area + dac_area,
        "strict_payload_ready": False,
        "claim_boundary": {
            "allowed": "creates a named-candidate area candidate from the starter layout boundary estimate",
            "not_allowed": "does not replace extracted signoff area, does not fill the strict payload, and does not write accepted post-layout evidence",
        },
        "why_not_strict": measurement["why_not_strict"],
    }


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# First Real Converter Area Candidate",
        "",
        f"- status: `{report['status']}`",
        f"- candidate id: `{report['candidate_id']}`",
        f"- run id: `{report['run_id']}`",
        f"- measurement artifact: `{report['measurement_artifact']}`",
        f"- source netlist: `{report['source_netlist']}`",
        f"- ADC area: `{report['adc_area_um2']}` um2",
        f"- DAC area: `{report['dac_area_um2']}` um2",
        f"- total readout area: `{report['total_readout_area_um2']}` um2",
        f"- strict payload ready: `{report['strict_payload_ready']}`",
        "",
        "## First Principle",
        "",
        "Area is chip space. A converter can look good in energy or timing and still be a bad system choice if the physical cells consume too much repeated space near every array or column group.",
        "",
        "This candidate binds the starter layout area estimate to the same named converter object used by B1 through B4. It is useful for the system discussion because object, energy, latency, noise, and area now point to one candidate name.",
        "",
        "## Why This Is Not Strict Yet",
        "",
    ]
    lines.extend(f"- {item}" for item in report["why_not_strict"])
    lines.extend([
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
    print("first_real_converter_area_candidate")
    print(f"status,{report['status']}")
    print(f"measurement_artifact,{report['measurement_artifact']}")
    print(f"total_readout_area_um2,{report['total_readout_area_um2']}")
    print(f"strict_payload_ready,{report['strict_payload_ready']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
