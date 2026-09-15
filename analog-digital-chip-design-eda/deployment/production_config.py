"""Fail-closed deployment configuration contract.

The open-source pilot deliberately runs with local SQLite/filesystem state. A
customer deployment must opt into a separate tier and declare the managed
boundaries that make the same API contract safe to operate beyond one pod.
This module validates declarations only; provider implementations and their
runtime drills remain deployment-specific.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
import os
import re
from urllib.parse import urlparse


@dataclass(frozen=True)
class DeploymentConfig:
    tier: str
    ready: bool
    missing: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "tier": self.tier,
            "ready": self.ready,
            "missing": list(self.missing),
            "managed_contract_required": self.tier == "customer-production",
        }


def _truthy(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def _postgres_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"postgres", "postgresql"} and bool(parsed.hostname)


def _https_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.hostname)


def load_deployment_config() -> DeploymentConfig:
    tier = os.environ.get("VERIFICATION_DEPLOYMENT_TIER", "pilot").strip().lower() or "pilot"
    if tier not in {"pilot", "customer-production"}:
        return DeploymentConfig(tier=tier, ready=False, missing=("VERIFICATION_DEPLOYMENT_TIER must be pilot or customer-production",))
    if tier == "pilot":
        return DeploymentConfig(tier=tier, ready=True, missing=())

    required: list[str] = []
    if not _postgres_url(os.environ.get("VERIFICATION_DATABASE_URL", "")):
        required.append("VERIFICATION_DATABASE_URL (postgres:// or postgresql://)")
    if os.environ.get("VERIFICATION_EVIDENCE_STORE_PROVIDER", "").strip().lower() != "object-store":
        required.append("VERIFICATION_EVIDENCE_STORE_PROVIDER=object-store")
    if not os.environ.get("VERIFICATION_EVIDENCE_STORE_BUCKET", "").strip():
        required.append("VERIFICATION_EVIDENCE_STORE_BUCKET")
    if not _truthy("VERIFICATION_REQUIRE_IDENTITY_SUBJECT"):
        required.append("VERIFICATION_REQUIRE_IDENTITY_SUBJECT=true")
    if not os.environ.get("VERIFICATION_REVIEWER_ROLE", "").strip():
        required.append("VERIFICATION_REVIEWER_ROLE")
    if not os.environ.get("VERIFICATION_OPERATOR_ROLE", "").strip():
        required.append("VERIFICATION_OPERATOR_ROLE")
    if not _https_url(os.environ.get("VERIFICATION_IDENTITY_ISSUER", "")):
        required.append("VERIFICATION_IDENTITY_ISSUER (https://...)")
    if not os.environ.get("VERIFICATION_IDENTITY_AUDIENCE", "").strip():
        required.append("VERIFICATION_IDENTITY_AUDIENCE")
    if not _https_url(os.environ.get("VERIFICATION_IDENTITY_JWKS_URL", "")):
        required.append("VERIFICATION_IDENTITY_JWKS_URL (https://...) ")
    if not _truthy("VERIFICATION_REQUIRE_IDENTITY_TOKEN"):
        required.append("VERIFICATION_REQUIRE_IDENTITY_TOKEN=true")
    project_subjects = os.environ.get("VERIFICATION_PROJECT_SUBJECTS", "").strip()
    try:
        mapping = json.loads(project_subjects)
        valid_mapping = isinstance(mapping, dict) and bool(mapping) and all(
            isinstance(project, str) and isinstance(subjects, list) and subjects and all(isinstance(subject, str) and subject.strip() for subject in subjects)
            for project, subjects in mapping.items()
        )
    except json.JSONDecodeError:
        valid_mapping = False
    if not valid_mapping:
        required.append("VERIFICATION_PROJECT_SUBJECTS (non-empty JSON project-to-subject mapping)")
    if os.environ.get("VERIFICATION_EXECUTION_SANDBOX", "").strip().lower() != "isolated":
        required.append("VERIFICATION_EXECUTION_SANDBOX=isolated")
    if os.environ.get("VERIFICATION_EXECUTION_WORKSPACE", "").strip().lower() != "disposable":
        required.append("VERIFICATION_EXECUTION_WORKSPACE=disposable")
    if os.environ.get("VERIFICATION_EXECUTION_NETWORK_POLICY", "").strip().lower() != "deny-by-default":
        required.append("VERIFICATION_EXECUTION_NETWORK_POLICY=deny-by-default")
    quota_values: dict[str, int] = {}
    for name in ("VERIFICATION_JOB_MAX_WORKSPACE_BYTES", "VERIFICATION_JOB_MAX_FILE_BYTES"):
        try:
            value = int(os.environ.get(name, ""))
        except ValueError:
            value = 0
        quota_values[name] = value
        if value <= 0:
            required.append(f"{name} (positive byte quota)")
    if quota_values.get("VERIFICATION_JOB_MAX_WORKSPACE_BYTES", 0) > 0 and quota_values.get("VERIFICATION_JOB_MAX_FILE_BYTES", 0) > quota_values["VERIFICATION_JOB_MAX_WORKSPACE_BYTES"]:
        required.append("VERIFICATION_JOB_MAX_FILE_BYTES must not exceed VERIFICATION_JOB_MAX_WORKSPACE_BYTES")
    if not os.environ.get("VERIFICATION_OBSERVABILITY_ENDPOINT", "").strip():
        required.append("VERIFICATION_OBSERVABILITY_ENDPOINT")
    if not os.environ.get("VERIFICATION_LOGS_ENDPOINT", "").strip():
        required.append("VERIFICATION_LOGS_ENDPOINT")
    if not os.environ.get("VERIFICATION_ALERTMANAGER_ENDPOINT", "").strip():
        required.append("VERIFICATION_ALERTMANAGER_ENDPOINT")
    if not os.environ.get("VERIFICATION_SLO_OWNER", "").strip():
        required.append("VERIFICATION_SLO_OWNER")
    adapters_raw = os.environ.get("VERIFICATION_EDA_ADAPTERS", "").strip()
    try:
        adapters = json.loads(adapters_raw)
        valid_adapters = isinstance(adapters, list) and bool(adapters) and all(
            isinstance(item, dict) and all(str(item.get(field, "")).strip() for field in ("name", "kind", "executable"))
            for item in adapters
        )
    except json.JSONDecodeError:
        valid_adapters = False
    if not valid_adapters:
        required.append("VERIFICATION_EDA_ADAPTERS (non-empty JSON customer adapter registry)")
    backup_policy = os.environ.get("VERIFICATION_BACKUP_POLICY", "").strip().lower()
    retention = re.fullmatch(r"daily-(\d+)d", backup_policy)
    if not retention or int(retention.group(1)) < 7:
        required.append("VERIFICATION_BACKUP_POLICY=daily-Nd (N>=7)")
    for name in ("VERIFICATION_DR_RPO_MINUTES", "VERIFICATION_DR_RTO_MINUTES"):
        try:
            value = int(os.environ.get(name, ""))
        except ValueError:
            value = 0
        if value <= 0 or value > 1440:
            required.append(f"{name} (1..1440)")
    return DeploymentConfig(tier=tier, ready=not required, missing=tuple(required))
