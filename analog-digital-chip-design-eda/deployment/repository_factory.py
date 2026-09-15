"""Atomic repository selection for pilot and customer-production tiers."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from deployment.collateral_store import CollateralStore
from deployment.job_queue import DurableJobQueue
from deployment.project_store import ProjectStore
from deployment.postgres_job_queue import PostgresJobQueue
from deployment.postgres_project_store import PostgresCollateralStore, PostgresProjectStore
from deployment.production_config import load_deployment_config
from deployment.evidence_store import FilesystemEvidenceStore, S3EvidenceStore


@dataclass(frozen=True)
class RepositoryBundle:
    queue: object
    projects: object
    collateral: object
    evidence: object
    backend: str


def build_repositories(database: str | Path, collateral_root: str | Path, *, migrate: bool = False) -> RepositoryBundle:
    config = load_deployment_config()
    if config.tier == "customer-production":
        import os
        dsn = os.environ.get("VERIFICATION_DATABASE_URL", "")
        if not config.ready:
            raise RuntimeError("customer-production repository configuration is incomplete: " + ", ".join(config.missing))
        evidence = S3EvidenceStore(os.environ.get("VERIFICATION_EVIDENCE_STORE_BUCKET", ""))
        return RepositoryBundle(
            queue=PostgresJobQueue(dsn, migrate=migrate),
            projects=PostgresProjectStore(dsn, migrate=migrate),
            collateral=PostgresCollateralStore(dsn, collateral_root, object_store=evidence, migrate=migrate),
            evidence=evidence,
            backend="postgresql",
        )
    evidence = FilesystemEvidenceStore(Path(collateral_root).parent / "evidence")
    return RepositoryBundle(
        queue=DurableJobQueue(database),
        projects=ProjectStore(database),
        collateral=CollateralStore(database, collateral_root),
        evidence=evidence,
        backend="sqlite-pilot",
    )
