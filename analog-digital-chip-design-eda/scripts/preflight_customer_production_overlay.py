"""Validate the rendered customer-production Kubernetes overlay semantics."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import yaml


def validate(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    if "replace-out-of-band" in text or "password:" in text.lower():
        errors.append("rendered production input contains a credential placeholder or password")
    documents = [item for item in yaml.safe_load_all(text) if item]
    deployment = next((item for item in documents if item.get("kind") == "Deployment" and item.get("metadata", {}).get("name") == "verification-pilot"), None)
    cron = next((item for item in documents if item.get("kind") == "CronJob" and item.get("metadata", {}).get("name") == "verification-postgres-backup"), None)
    if deployment is None:
        errors.append("verification-pilot Deployment is missing")
    else:
        containers = deployment.get("spec", {}).get("template", {}).get("spec", {}).get("containers", [])
        api = next((item for item in containers if item.get("name") == "api"), None)
        if api is None:
            errors.append("API container is missing")
        else:
            env = {item.get("name"): item for item in api.get("env", [])}
            for name, value in (("VERIFICATION_DEPLOYMENT_TIER", "customer-production"), ("VERIFICATION_EVIDENCE_STORE_PROVIDER", "object-store"), ("VERIFICATION_REQUIRE_IDENTITY_TOKEN", "true")):
                if env.get(name, {}).get("value") != value:
                    errors.append(f"API environment must set {name}={value}")
            for name in ("VERIFICATION_EVIDENCE_STORE_BUCKET", "VERIFICATION_REVIEWER_ROLE", "VERIFICATION_OPERATOR_ROLE", "VERIFICATION_PROJECT_SUBJECTS", "VERIFICATION_IDENTITY_ISSUER", "VERIFICATION_IDENTITY_AUDIENCE", "VERIFICATION_IDENTITY_JWKS_URL", "VERIFICATION_EXECUTION_WORKSPACE", "VERIFICATION_EXECUTION_NETWORK_POLICY", "VERIFICATION_JOB_MAX_WORKSPACE_BYTES", "VERIFICATION_JOB_MAX_FILE_BYTES", "VERIFICATION_OBSERVABILITY_ENDPOINT", "VERIFICATION_LOGS_ENDPOINT", "VERIFICATION_ALERTMANAGER_ENDPOINT", "VERIFICATION_SLO_OWNER", "VERIFICATION_EDA_ADAPTERS", "VERIFICATION_BACKUP_POLICY", "VERIFICATION_DR_RPO_MINUTES", "VERIFICATION_DR_RTO_MINUTES"):
                if name not in env:
                    errors.append(f"API environment is missing {name}")
            refs = {item.get("valueFrom", {}).get("configMapKeyRef", {}).get("name") for item in api.get("env", [])}
            if "verification-production-config" not in refs:
                errors.append("API must reference verification-production-config")
            secret_refs = {item.get("valueFrom", {}).get("secretKeyRef", {}).get("name") for item in api.get("env", [])}
            if "verification-production-database" not in secret_refs:
                errors.append("API must reference verification-production-database")
    if cron is None:
        errors.append("verification-postgres-backup CronJob is missing")
    else:
        serialized = str(cron)
        if "verification-production-database" not in serialized or "verification-production-config" not in serialized:
            errors.append("backup CronJob must reference production Secret and ConfigMap")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rendered", type=Path)
    args = parser.parse_args()
    errors = validate(args.rendered)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"PASS: customer-production overlay preflight ({args.rendered})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
