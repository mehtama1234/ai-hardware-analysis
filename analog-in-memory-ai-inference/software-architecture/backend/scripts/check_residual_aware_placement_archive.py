#!/usr/bin/env python3
import io
import json
import sys
import urllib.request
import zipfile


BASE_URL = "http://127.0.0.1:8025"
PACKAGE_ID = "pkg-e931662a01293df2"


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def request_json(path):
    with urllib.request.urlopen(f"{BASE_URL}{path}", timeout=10) as response:
        require(response.status == 200, f"{path} returned HTTP {response.status}")
        return json.loads(response.read().decode("utf-8"))


def request_bytes(path):
    with urllib.request.urlopen(f"{BASE_URL}{path}", timeout=10) as response:
        require(response.status == 200, f"{path} returned HTTP {response.status}")
        return response.read()


def main():
    residual = request_json(f"/deployment-packages/{PACKAGE_ID}/residual-aware-placement")
    require(residual.get("available") is True, "residual-aware placement endpoint is unavailable")
    require(residual.get("result_type") == "residual_aware_placement_decisions", "wrong endpoint result_type")
    residual_policy = residual.get("source_matching_policy") if isinstance(residual.get("source_matching_policy"), dict) else {}
    require(residual.get("accepted_calibrated_source") == "deep_transformer_mlp_stack", "endpoint did not preserve deep transformer MLP-stack source match")
    require(residual_policy.get("mode") == "fixed_weight_matmul_family_match", "endpoint missing source matching policy mode")

    archive_bytes = request_bytes(f"/deployment-packages/{PACKAGE_ID}/archive")
    archive = zipfile.ZipFile(io.BytesIO(archive_bytes))
    names = set(archive.namelist())
    require("residual-aware-placement.json" in names, "archive missing residual-aware-placement.json")
    require("claim-readiness.json" in names, "archive missing claim-readiness.json")

    archived = json.loads(archive.read("residual-aware-placement.json").decode("utf-8"))
    require(archived.get("result_type") == "residual_aware_placement_decisions", "wrong archive result_type")
    require(archived.get("available") is True, "archived residual-aware placement is unavailable")
    archived_policy = archived.get("source_matching_policy") if isinstance(archived.get("source_matching_policy"), dict) else {}
    require(archived.get("accepted_calibrated_source") == "deep_transformer_mlp_stack", "archive did not preserve deep transformer MLP-stack source match")
    require(archived_policy.get("mode") == "fixed_weight_matmul_family_match", "archive missing source matching policy mode")
    require(archived_policy.get("selected_source") == "deep_transformer_mlp_stack", "archive source policy selected wrong source")
    require(
        archived.get("summary", {}).get("residual_aware_analog_allowed", 0) >= 1,
        "archive has no residual-aware analog allowed rows",
    )
    require(
        archived.get("summary") == residual.get("summary"),
        "archive summary differs from residual-aware placement endpoint",
    )
    require(
        archived.get("source_matching_policy") == residual.get("source_matching_policy"),
        "archive source matching policy differs from endpoint",
    )
    claim_readiness = request_json(f"/deployment-packages/{PACKAGE_ID}/claim-readiness")
    archived_claim_readiness = json.loads(archive.read("claim-readiness.json").decode("utf-8"))
    require(
        archived_claim_readiness.get("summary") == claim_readiness.get("summary"),
        "archive claim-readiness summary differs from endpoint",
    )
    archived_claims = {claim.get("id"): claim for claim in archived_claim_readiness.get("lab_claims", [])}
    endpoint_claims = {claim.get("id"): claim for claim in claim_readiness.get("lab_claims", [])}
    for claim_id in ["C2", "C3"]:
        require(claim_id in archived_claims, f"archive missing {claim_id}")
        require(archived_claims[claim_id].get("status") == endpoint_claims.get(claim_id, {}).get("status"), f"archive {claim_id} status differs from endpoint")
    c2_issues = " ".join(archived_claims["C2"].get("quality_issues", []))
    c3_issues = " ".join(archived_claims["C3"].get("quality_issues", []))
    require("local simulation" in c2_issues, "archive C2 does not preserve local-runtime boundary")
    require("synchronized hardware measurement" in c3_issues, "archive C3 does not preserve power/thermal boundary")
    print("PASS residual_aware_placement_archive")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"FAIL residual_aware_placement_archive: {exc}", file=sys.stderr)
        raise
