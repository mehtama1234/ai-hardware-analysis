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
NOISE_SOURCE = EVIDENCE / "converter-circuit-simulation-estimate.json"
OUT_JSON = EVIDENCE / "first-real-converter-noise-candidate.json"
OUT_MD = EVIDENCE / "first-real-converter-noise-candidate.md"
MEASUREMENT_JSON = CANDIDATE / "measurements" / "readout-noise.json"


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"missing input artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def number(value: Any, name: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise SystemExit(f"{name} must be numeric")
    return float(value)


def build_report() -> dict[str, Any]:
    object_audit = load_json(OBJECT_AUDIT)
    source = load_json(NOISE_SOURCE)
    if object_audit.get("ready_for_b1") is not True:
        raise SystemExit("B1 physical object must be ready before generating B4 candidate noise")
    estimate = source["estimate"]
    noise = estimate["noise"]
    target = estimate["target_boundary"]
    output_noise = number(noise["output_noise_rms"], "output_noise_rms")
    input_noise = number(noise["input_referred_noise"], "input_referred_noise")
    budget = number(target["output_noise_budget"], "output_noise_budget")
    measurement = {
        "result_type": "first_real_converter_readout_noise_candidate",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "candidate_id": "aimc_readout_candidate_001",
        "run_id": "aimc_readout_candidate_001_behavioral_noise_run001",
        "noise_level": "behavioral_circuit_estimate_tied_to_named_candidate_not_extracted_noise",
        "source_noise_artifact": rel(NOISE_SOURCE),
        "source_netlist": object_audit["expected_extracted_netlist"],
        "output_noise_rms": output_noise,
        "input_referred_noise": input_noise,
        "output_noise_budget": budget,
        "meets_output_noise_budget": output_noise <= budget,
        "method": noise["method"],
        "simulation_terms": source["simulation_terms"],
        "strict_payload_ready": False,
        "why_not_strict": [
            "the noise comes from a deterministic behavioral estimate",
            "the noise was not simulated through the assembled extracted candidate netlist",
            "device noise spectra, comparator offset distribution, mismatch, and clock feedthrough statistics are still absent",
        ],
    }
    MEASUREMENT_JSON.parent.mkdir(parents=True, exist_ok=True)
    MEASUREMENT_JSON.write_text(json.dumps(measurement, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "result_type": "first_real_converter_noise_candidate",
        "created_at": measurement["created_at"],
        "status": "b4_noise_candidate_written_not_strict_extracted_noise",
        "candidate_id": measurement["candidate_id"],
        "run_id": measurement["run_id"],
        "measurement_artifact": rel(MEASUREMENT_JSON),
        "source_noise_artifact": rel(NOISE_SOURCE),
        "source_netlist": measurement["source_netlist"],
        "output_noise_rms": output_noise,
        "input_referred_noise": input_noise,
        "output_noise_budget": budget,
        "meets_output_noise_budget": output_noise <= budget,
        "strict_payload_ready": False,
        "claim_boundary": {
            "allowed": "creates a named-candidate noise candidate from existing behavioral circuit noise evidence",
            "not_allowed": "does not replace extracted converter noise, does not fill the strict payload, and does not write accepted post-layout evidence",
        },
        "why_not_strict": measurement["why_not_strict"],
    }


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# First Real Converter Noise Candidate",
        "",
        f"- status: `{report['status']}`",
        f"- candidate id: `{report['candidate_id']}`",
        f"- run id: `{report['run_id']}`",
        f"- measurement artifact: `{report['measurement_artifact']}`",
        f"- source netlist: `{report['source_netlist']}`",
        f"- output noise RMS: `{report['output_noise_rms']}`",
        f"- input-referred noise: `{report['input_referred_noise']}`",
        f"- output noise budget: `{report['output_noise_budget']}`",
        f"- meets output noise budget: `{report['meets_output_noise_budget']}`",
        f"- strict payload ready: `{report['strict_payload_ready']}`",
        "",
        "## First Principle",
        "",
        "Noise is uncertainty in the value handed to the digital side. A converter can settle on time and still be unusable if the uncertainty is large enough to change the code or push the model state outside its error budget.",
        "",
        "This candidate binds the existing behavioral noise estimate to the same named converter object used by B1, B2, and B3. It keeps the useful number visible while refusing to call it extracted noise.",
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
    print("first_real_converter_noise_candidate")
    print(f"status,{report['status']}")
    print(f"measurement_artifact,{report['measurement_artifact']}")
    print(f"output_noise_rms,{report['output_noise_rms']}")
    print(f"meets_output_noise_budget,{report['meets_output_noise_budget']}")
    print(f"strict_payload_ready,{report['strict_payload_ready']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
