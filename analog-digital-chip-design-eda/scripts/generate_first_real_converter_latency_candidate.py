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
ROW_DAC = EVIDENCE / "row-dac-settling-spice-evidence.json"
SAR_READOUT = EVIDENCE / "sar-readout-spice-evidence.json"
SHARED_LOADING = EVIDENCE / "shared-converter-loading-spice-evidence.json"
OUT_JSON = EVIDENCE / "first-real-converter-latency-candidate.json"
OUT_MD = EVIDENCE / "first-real-converter-latency-candidate.md"
MEASUREMENT_JSON = CANDIDATE / "measurements" / "readout-latency.json"


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"missing input artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def positive_target_value(payload: dict[str, Any], key: str) -> float:
    target = payload.get("target") if isinstance(payload.get("target"), dict) else {}
    value = target.get(key)
    if not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0:
        raise SystemExit(f"missing positive target {key}")
    return float(value)


def build_report() -> dict[str, Any]:
    object_audit = load_json(OBJECT_AUDIT)
    row_dac = load_json(ROW_DAC)
    sar = load_json(SAR_READOUT)
    shared = load_json(SHARED_LOADING)
    if object_audit.get("ready_for_b1") is not True:
        raise SystemExit("B1 physical object must be ready before generating B3 candidate latency")
    settling_time_ns = positive_target_value(row_dac, "settling_time_ns")
    sar_conversion_time_ns = positive_target_value(sar, "conversion_time_ns")
    shared_conversion_time_ns = positive_target_value(shared, "conversion_time_ns")
    conversion_time_ns = max(sar_conversion_time_ns, shared_conversion_time_ns)
    measurement = {
        "result_type": "first_real_converter_readout_latency_candidate",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "candidate_id": "aimc_readout_candidate_001",
        "run_id": "aimc_readout_candidate_001_simple_load_latency_run001",
        "latency_level": "simple_load_spice_tied_to_named_candidate_not_extracted_timing",
        "source_netlist": object_audit["expected_extracted_netlist"],
        "source_artifacts": {
            "row_dac_settling": rel(ROW_DAC),
            "sar_readout": rel(SAR_READOUT),
            "shared_converter_loading": rel(SHARED_LOADING),
        },
        "settling_time_ns": settling_time_ns,
        "conversion_time_ns": conversion_time_ns,
        "total_before_digital_value_ns": settling_time_ns + conversion_time_ns,
        "adc_comparisons": 12,
        "method": "use local row-settling and sampled-readout SPICE timing windows and bind them to the named candidate object",
        "strict_payload_ready": False,
        "why_not_strict": [
            "the timing windows come from simple source/load SPICE decks",
            "the conversion timing was not measured through the assembled extracted candidate netlist",
            "comparator metastability, reference settling, clocking, and full SAR control timing are still absent",
        ],
    }
    MEASUREMENT_JSON.parent.mkdir(parents=True, exist_ok=True)
    MEASUREMENT_JSON.write_text(json.dumps(measurement, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "result_type": "first_real_converter_latency_candidate",
        "created_at": measurement["created_at"],
        "status": "b3_latency_candidate_written_not_strict_extracted_timing",
        "candidate_id": measurement["candidate_id"],
        "run_id": measurement["run_id"],
        "measurement_artifact": rel(MEASUREMENT_JSON),
        "source_netlist": measurement["source_netlist"],
        "settling_time_ns": settling_time_ns,
        "conversion_time_ns": conversion_time_ns,
        "total_before_digital_value_ns": measurement["total_before_digital_value_ns"],
        "strict_payload_ready": False,
        "claim_boundary": {
            "allowed": "creates a named-candidate latency candidate from existing simple-load SPICE timing evidence",
            "not_allowed": "does not replace extracted converter timing, does not fill the strict payload, and does not write accepted post-layout evidence",
        },
        "why_not_strict": measurement["why_not_strict"],
    }


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# First Real Converter Latency Candidate",
        "",
        f"- status: `{report['status']}`",
        f"- candidate id: `{report['candidate_id']}`",
        f"- run id: `{report['run_id']}`",
        f"- measurement artifact: `{report['measurement_artifact']}`",
        f"- source netlist: `{report['source_netlist']}`",
        f"- settling time: `{report['settling_time_ns']}` ns",
        f"- conversion time: `{report['conversion_time_ns']}` ns",
        f"- total time before digital value: `{report['total_before_digital_value_ns']}` ns",
        f"- strict payload ready: `{report['strict_payload_ready']}`",
        "",
        "## First Principle",
        "",
        "Latency is the wait between asking the analog path for a value and having a digital value that can be used. For this converter path, that wait has two parts: the row/sample voltage must settle, then the readout must make its timed decisions.",
        "",
        "This candidate binds the local 4 ns settling window and 12 ns readout window to the same named converter object used by B1 and B2. It is useful because the system can now talk about object, energy, and time using the same candidate name.",
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
    print("first_real_converter_latency_candidate")
    print(f"status,{report['status']}")
    print(f"measurement_artifact,{report['measurement_artifact']}")
    print(f"total_before_digital_value_ns,{report['total_before_digital_value_ns']}")
    print(f"strict_payload_ready,{report['strict_payload_ready']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
