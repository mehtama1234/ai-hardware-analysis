"""Smoke-test a deployed customer-production verification endpoint."""
from __future__ import annotations

import argparse
import json
from urllib.request import Request, urlopen

RUNTIME_SCHEMA_PATH = "deployment/observability/verification-customer-production-runtime.schema.json"


def validate_payloads(readiness: dict, contract: dict, metrics: str, sandbox: dict | None = None) -> list[str]:
    errors: list[str] = []
    if readiness.get("status") != "ready":
        errors.append("/readyz did not report ready")
    if readiness.get("deployment") != "customer-production":
        errors.append("/readyz did not report customer-production")
    if not readiness.get("deployment_config", {}).get("ready"):
        errors.append("deployment configuration is not ready")
    if contract.get("schema_version") != "verification-platform-contract-v1":
        errors.append("unexpected platform contract schema")
    safety = contract.get("execution_safety", {})
    for key, expected in (("shell", "disabled"), ("symlink_outputs", "blocked")):
        if safety.get(key) != expected:
            errors.append(f"execution safety {key} guarantee is missing")
    for metric in ("verification_queue_capacity", "verification_backup_age_seconds", "verification_backup_rpo_seconds"):
        if metric not in metrics:
            errors.append(f"Prometheus metric {metric} is missing")
    if sandbox is not None and sandbox.get("verified") is not True:
        errors.append("execution sandbox runtime probe did not pass")
    return errors


def validate_http_statuses(statuses: dict[str, str]) -> list[str]:
    """Require successful responses for every preflight endpoint."""
    return [f"{name} returned HTTP {status}" for name, status in statuses.items() if status != "200"]


def _get(base_url: str, path: str, headers: dict[str, str]) -> tuple[object, str]:
    request = Request(base_url.rstrip("/") + path, headers=headers)
    with urlopen(request, timeout=10) as response:  # nosec B310 - endpoint supplied by operator
        body = response.read().decode("utf-8")
    return (json.loads(body) if path != "/metrics/prometheus" else body), str(response.status)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base_url")
    parser.add_argument("--api-key")
    parser.add_argument("--bearer-token")
    parser.add_argument("--sandbox-probe", action="store_true", help="run the local namespace capability probe as part of acceptance")
    args = parser.parse_args()
    headers = {}
    if args.api_key:
        headers["X-API-Key"] = args.api_key
    if args.bearer_token:
        headers["Authorization"] = "Bearer " + args.bearer_token
    stage = "readyz"
    try:
        readiness, readiness_status = _get(args.base_url, "/readyz", headers)
        stage = "contract"
        contract, contract_status = _get(args.base_url, "/v1/contract", headers)
        stage = "metrics"
        metrics, metrics_status = _get(args.base_url, "/metrics/prometheus", headers)
        status_errors = validate_http_statuses({"/readyz": readiness_status, "/v1/contract": contract_status, "/metrics/prometheus": metrics_status})
        sandbox = None
        if args.sandbox_probe:
            stage = "execution-sandbox"
            try:
                from scripts.verify_execution_sandbox_runtime import probe
            except ModuleNotFoundError:
                # Standalone execution puts this directory, rather than the
                # repository root, on sys.path.
                from verify_execution_sandbox_runtime import probe
            sandbox = probe()
        errors = status_errors + validate_payloads(readiness, contract, metrics, sandbox)
    except Exception as error:
        print(json.dumps({"schema_version": "verification-customer-production-runtime-v1", "schema_path": RUNTIME_SCHEMA_PATH, "status": "blocked", "error_type": type(error).__name__, "stage": stage}, sort_keys=True))
        return 2
    if errors:
        print(json.dumps({"schema_version": "verification-customer-production-runtime-v1", "schema_path": RUNTIME_SCHEMA_PATH, "status": "blocked", "errors": errors}, sort_keys=True))
        return 1
    checks = ["readyz", "contract", "prometheus"]
    if args.sandbox_probe:
        checks.append("execution-sandbox")
    print(json.dumps({"schema_version": "verification-customer-production-runtime-v1", "schema_path": RUNTIME_SCHEMA_PATH, "status": "passed", "deployment": "customer-production", "contract": contract["schema_version"], "checks": checks}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
