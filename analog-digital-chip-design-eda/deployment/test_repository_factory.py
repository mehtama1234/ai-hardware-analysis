import pytest

import deployment.repository_factory as repository_factory
from deployment.production_config import DeploymentConfig
from deployment.repository_factory import RepositoryBundle, build_repositories


def test_factory_selects_atomic_pilot_bundle(tmp_path):
    bundle = build_repositories(tmp_path / "jobs.sqlite", tmp_path / "collateral")
    assert isinstance(bundle, RepositoryBundle)
    assert bundle.backend == "sqlite-pilot"
    assert all(callable(getattr(item, "get", None)) for item in (bundle.queue, bundle.projects, bundle.collateral))
    assert callable(bundle.evidence.put)


def test_factory_selects_all_managed_repositories_as_one_bundle(monkeypatch, tmp_path):
    monkeypatch.setenv("VERIFICATION_DATABASE_URL", "postgresql://db.internal/verification")
    monkeypatch.setenv("VERIFICATION_EVIDENCE_STORE_BUCKET", "customer-evidence")
    monkeypatch.setattr(
        repository_factory,
        "load_deployment_config",
        lambda: DeploymentConfig(tier="customer-production", ready=True, missing=()),
    )
    selected = []

    class _Queue:
        def __init__(self, dsn, migrate=False): selected.append(("queue", dsn, migrate))

    class _Projects:
        def __init__(self, dsn, migrate=False): selected.append(("projects", dsn, migrate))

    class _Collateral:
        def __init__(self, dsn, root, object_store, migrate=False): selected.append(("collateral", dsn, root, object_store, migrate))

    class _Evidence:
        def __init__(self, bucket): selected.append(("evidence", bucket))

    monkeypatch.setattr(repository_factory, "PostgresJobQueue", _Queue)
    monkeypatch.setattr(repository_factory, "PostgresProjectStore", _Projects)
    monkeypatch.setattr(repository_factory, "PostgresCollateralStore", _Collateral)
    monkeypatch.setattr(repository_factory, "S3EvidenceStore", _Evidence)

    bundle = build_repositories(tmp_path / "jobs.sqlite", tmp_path / "collateral", migrate=True)

    assert bundle.backend == "postgresql"
    assert [item[0] for item in selected] == ["evidence", "queue", "projects", "collateral"]
    assert selected[0] == ("evidence", "customer-evidence")
    assert all(item[-1] is True for item in selected[1:])


def test_factory_refuses_incomplete_customer_configuration(monkeypatch, tmp_path):
    monkeypatch.setattr(
        repository_factory,
        "load_deployment_config",
        lambda: DeploymentConfig(tier="customer-production", ready=False, missing=("managed database",)),
    )
    with pytest.raises(RuntimeError, match="managed database"):
        build_repositories(tmp_path / "jobs.sqlite", tmp_path / "collateral")
