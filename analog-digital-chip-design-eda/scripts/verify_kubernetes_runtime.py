#!/usr/bin/env python3
"""Verify a disposable Kubernetes verification-pilot deployment runtime."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess


def _kubectl(*args: str) -> object:
    result = subprocess.run(["kubectl", *args, "-o", "json"], check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def verify(namespace: str, deployment: str, output: Path) -> dict[str, object]:
    payload = _kubectl("-n", namespace, "get", "deployment", deployment)
    spec = payload["spec"]["template"]["spec"]
    containers = {item["name"]: item for item in spec["containers"]}
    status = payload.get("status", {})
    checks = {
        "available_replicas": status.get("availableReplicas", 0) >= 1,
        "all_containers_ready": status.get("readyReplicas", 0) >= 1 and len(containers) == 2,
        "non_root": spec.get("securityContext", {}).get("runAsNonRoot") is True and spec.get("securityContext", {}).get("runAsUser") == 10001,
        "runtime_default_seccomp": spec.get("securityContext", {}).get("seccompProfile", {}).get("type") == "RuntimeDefault",
        "service_account_token_disabled": spec.get("automountServiceAccountToken") is False,
        "read_only_roots": all(item.get("securityContext", {}).get("readOnlyRootFilesystem") is True for item in containers.values()),
        "privilege_escalation_disabled": all(item.get("securityContext", {}).get("allowPrivilegeEscalation") is False for item in containers.values()),
        "current_image": all(item.get("image") == "verification-pilot-current:latest" for item in containers.values()),
    }
    result = {
        "schema_version": "verification-kubernetes-runtime-v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "namespace": namespace,
        "deployment": deployment,
        "observed_replicas": {key: status.get(key, 0) for key in ("replicas", "readyReplicas", "availableReplicas")},
        "checks": checks,
        "verified": all(checks.values()),
        "evidence_sha256": hashlib.sha256(json.dumps(checks, sort_keys=True).encode()).hexdigest(),
        "claim_boundary": "Disposable kind-cluster pod policy and startup only; this does not prove persistent volumes, namespace sandbox capability, managed dependencies, HA, or customer production readiness.",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("namespace")
    parser.add_argument("deployment")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = verify(args.namespace, args.deployment, args.output)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["verified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
