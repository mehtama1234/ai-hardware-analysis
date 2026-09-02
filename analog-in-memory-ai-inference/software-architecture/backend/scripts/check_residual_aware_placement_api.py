#!/usr/bin/env python3
from __future__ import annotations

import json
from urllib.request import urlopen


BASE_URL = "http://127.0.0.1:8025"
PACKAGE_ID = "pkg-e931662a01293df2"


def get_json(path: str) -> dict[str, object]:
    with urlopen(f"{BASE_URL}{path}", timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    bundle = get_json(f"/deployment-packages/{PACKAGE_ID}/artifacts")
    placement = get_json(f"/deployment-packages/{PACKAGE_ID}/hardware-placement")
    residual = get_json(f"/deployment-packages/{PACKAGE_ID}/residual-aware-placement")
    artifacts = bundle.get("artifacts") if isinstance(bundle.get("artifacts"), dict) else {}
    package = artifacts.get("package") if isinstance(artifacts.get("package"), dict) else {}
    saved_artifacts = package.get("saved_artifacts") if isinstance(package.get("saved_artifacts"), dict) else {}
    placement_rows = placement.get("placement_rows") if isinstance(placement.get("placement_rows"), list) else []
    residual_rows = residual.get("rows") if isinstance(residual.get("rows"), list) else []
    residual_summary = residual.get("summary") if isinstance(residual.get("summary"), dict) else {}
    source_policy = residual.get("source_matching_policy") if isinstance(residual.get("source_matching_policy"), dict) else {}

    require(artifacts.get("residual_aware_placement"), "artifact bundle missing residual_aware_placement payload")
    require(
        saved_artifacts.get("residual_aware_placement") == f"/deployment-packages/{PACKAGE_ID}/residual-aware-placement",
        "package saved_artifacts missing residual-aware placement link",
    )
    require(residual.get("available") is True, "residual-aware placement endpoint is not available")
    require(residual.get("result_type") == "residual_aware_placement_decisions", "wrong residual-aware result_type")
    require(residual.get("accepted_calibrated_source") == "deep_transformer_mlp_stack", "endpoint did not preserve deep transformer MLP-stack source match")
    require(source_policy.get("mode") == "fixed_weight_matmul_family_match", "endpoint missing source matching policy mode")
    require(source_policy.get("selected_source") == "deep_transformer_mlp_stack", "endpoint source policy selected wrong source")
    require(len(placement_rows) == len(residual_rows), "residual-aware rows do not match hardware-placement row count")
    require(residual_summary.get("residual_aware_analog_allowed", 0) >= 1, "no residual-aware analog-allowed rows")
    require(
        residual_summary.get("residual_aware_analog_allowed") <= residual_summary.get("structural_analog_candidates", 0),
        "residual-aware allowed rows cannot exceed structural candidates",
    )
    require(
        any(isinstance(row, dict) and row.get("evidence_tool") == "crosssim" for row in residual_rows),
        "residual-aware placement did not expose CrossSim evidence",
    )
    require(
        any(
            isinstance(row, dict)
            and row.get("residual_aware_decision") == "analog_allowed"
            and row.get("evidence_source") == "deep_transformer_mlp_stack"
            and row.get("source_match_policy") == "fixed_weight_matmul_family_match"
            for row in residual_rows
        ),
        "residual-aware placement did not expose source-matched deep transformer MLP-stack analog rows",
    )
    print("PASS residual_aware_placement_api")
    print(f"package,{PACKAGE_ID}")
    print(f"operators,{len(residual_rows)}")
    print(f"residual_aware_analog_allowed,{residual_summary.get('residual_aware_analog_allowed')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
