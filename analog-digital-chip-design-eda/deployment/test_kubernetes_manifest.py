from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parent / "kubernetes"


def _documents():
    return [item for item in yaml.safe_load_all((ROOT / "verification-pilot.yaml").read_text()) if item]


def test_pilot_manifest_is_pinned_and_persistent():
    documents = _documents()
    deployment = next(item for item in documents if item["kind"] == "Deployment")
    containers = deployment["spec"]["template"]["spec"]["containers"]
    images = {container["image"] for container in containers}
    assert images == {"verification-pilot:0.1.0"}
    assert all(":" in image and "latest" not in image for image in images)
    assert any(item["kind"] == "PersistentVolumeClaim" for item in documents)
    assert not any(item["kind"] == "Secret" for item in documents)
    assert all("readinessProbe" in container or container["name"] == "worker" for container in containers)
    assert next(item for item in documents if item["kind"] == "Deployment")["spec"]["template"]["spec"]["securityContext"]["runAsNonRoot"] is True
    pod = next(item for item in documents if item["kind"] == "Deployment")["spec"]["template"]["spec"]
    assert pod["automountServiceAccountToken"] is False
    assert pod["securityContext"]["seccompProfile"]["type"] == "RuntimeDefault"
    for container in containers:
        assert container["securityContext"]["allowPrivilegeEscalation"] is False
        assert container["securityContext"]["readOnlyRootFilesystem"] is True
        assert container["securityContext"]["capabilities"]["drop"] == ["ALL"]
        assert any(mount["name"] == "tmp" and mount["mountPath"] == "/tmp" for mount in container["volumeMounts"])
        assert "ephemeral-storage" in container["resources"]["requests"]
        assert "ephemeral-storage" in container["resources"]["limits"]
    assert any(volume["name"] == "tmp" and "emptyDir" in volume for volume in pod["volumes"])
    policy = next(item for item in documents if item["kind"] == "NetworkPolicy")
    assert policy["spec"]["policyTypes"] == ["Egress"]
    assert policy["spec"]["egress"][0]["ports"] == [{"protocol": "UDP", "port": 53}, {"protocol": "TCP", "port": 53}]
    assert all(any(item.get("name") == "VERIFICATION_EXECUTION_WORKSPACE" and item.get("value") == "disposable" for item in container["env"]) for container in containers)
    assert all(any(item.get("name") == "VERIFICATION_EXECUTION_NETWORK_POLICY" and item.get("value") == "deny-by-default" for item in container["env"]) for container in containers)


def test_kustomization_promotes_the_same_image_name():
    config = yaml.safe_load((ROOT / "kustomization.yaml").read_text())
    assert "verification-pilot.yaml" in config["resources"]
    image = next(item for item in config["images"] if item["name"] == "verification-pilot")
    assert image["newName"] == "verification-pilot"
    assert image["newTag"] != "latest"


def test_dockerfile_pins_base_image_digest():
    dockerfile = (ROOT.parent / "Dockerfile").read_text()
    assert "FROM python:3.11-slim@sha256:" in dockerfile
    assert "util-linux" in dockerfile


def test_production_config_example_has_no_real_credentials_and_required_keys():
    example = (ROOT / "verification-production-config.example.yaml").read_text()
    for key in ("evidence-store-bucket", "backup-policy", "dr-rpo-minutes", "dr-rto-minutes", "identity-issuer", "identity-audience", "identity-jwks-url", "reviewer-role", "operator-role", "project-subjects", "observability-endpoint", "execution-workspace", "execution-network-policy"):
        assert key in example
    assert "replace-out-of-band" in example
    assert "password" not in example.lower()


def test_production_overlay_consumes_external_config_and_backup():
    overlay = ROOT / "production"
    kustomization = yaml.safe_load((overlay / "kustomization.yaml").read_text())
    assert "../base" in kustomization["resources"]
    assert "../backup" in kustomization["resources"]
    assert "load-restrictor LoadRestrictionsNone" in (ROOT / "README.md").read_text()
    patch = (overlay / "deployment-production-patch.yaml").read_text()
    for value in ("customer-production", "verification-production-config", "verification-production-database", "VERIFICATION_REQUIRE_IDENTITY_TOKEN", "VERIFICATION_OPERATOR_ROLE", "VERIFICATION_PROJECT_SUBJECTS", "VERIFICATION_EXECUTION_WORKSPACE"):
        assert value in patch
    cron = (ROOT / "verification-backup-cronjob.yaml").read_text()
    assert "verification-production-database" in cron
