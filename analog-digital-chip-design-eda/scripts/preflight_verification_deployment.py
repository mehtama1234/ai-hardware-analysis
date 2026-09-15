"""Validate the verification pilot release package before cluster rollout."""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_ARTIFACTS = (
    "RECOVERY_RUNBOOK.md",
    "CUSTOM_ADAPTER_GUIDE.md",
    "PILOT_MEASUREMENT_PLAN.md",
    "pilot-scorecard-template.json",
    "PRODUCTION_MIGRATION_PLAN.md",
    "observability/verification-pilot-dashboard.json",
    "observability/prometheus.yml",
    "observability/docker-compose.observability.yml",
)


def _documents(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as stream:
        return [item for item in yaml.safe_load_all(stream) if item]


def validate(manifest_dir: Path = ROOT / "deployment" / "kubernetes") -> list[str]:
    errors: list[str] = []
    manifest = manifest_dir / "verification-pilot.yaml"
    overlay = manifest_dir / "kustomization.yaml"
    for required in (manifest, overlay):
        if not required.is_file():
            errors.append(f"missing deployment file: {required}")
    for name in REQUIRED_ARTIFACTS:
        if not (ROOT / "deployment" / name).is_file():
            errors.append(f"missing operational artifact: deployment/{name}")
    if errors:
        return errors

    docs = _documents(manifest)
    pvc = next((d for d in docs if d.get("kind") == "PersistentVolumeClaim"), None)
    deployment = next((d for d in docs if d.get("kind") == "Deployment"), None)
    service = next((d for d in docs if d.get("kind") == "Service"), None)
    network_policy = next((d for d in docs if d.get("kind") == "NetworkPolicy"), None)
    if not pvc:
        errors.append("manifest must define a PersistentVolumeClaim")
    if not deployment:
        errors.append("manifest must define a Deployment")
        return errors
    if not service:
        errors.append("manifest must define a Service")
    if not network_policy:
        errors.append("manifest must define an egress NetworkPolicy")
    elif network_policy.get("spec", {}).get("policyTypes") != ["Egress"]:
        errors.append("NetworkPolicy must declare Egress policy type")
    pod = deployment.get("spec", {}).get("template", {}).get("spec", {})
    containers = pod.get("containers", [])
    by_name = {c.get("name"): c for c in containers}
    if not {"api", "worker"}.issubset(by_name):
        errors.append("Deployment must contain api and worker containers")
    else:
        images = {by_name[name].get("image") for name in ("api", "worker")}
        if len(images) != 1:
            errors.append("api and worker must use the same pinned image")
        image = next(iter(images))
        if not image or image.endswith(":latest") or "@sha256:" not in image and ":" not in image:
            errors.append("container image must use an immutable release tag or digest")
        api_env = {entry.get("name"): entry.get("value") for entry in by_name["api"].get("env", [])}
        if api_env.get("VERIFICATION_SERVICE_API_KEY_FILE") != "/run/secrets/api-key":
            errors.append("api must read VERIFICATION_SERVICE_API_KEY_FILE from the mounted secret")
        api_probe = by_name["api"].get("readinessProbe", {})
        live_probe = by_name["api"].get("livenessProbe", {})
        if api_probe.get("httpGet", {}).get("path") != "/readyz":
            errors.append("api readiness probe must use /readyz")
        if live_probe.get("httpGet", {}).get("path") != "/healthz":
            errors.append("api liveness probe must use /healthz")
    secret_refs = [v.get("secret", {}).get("secretName") for v in pod.get("volumes", [])]
    if "verification-pilot-api" not in secret_refs:
        errors.append("Deployment must reference the out-of-band verification-pilot-api secret")
    if not pod.get("securityContext", {}).get("runAsNonRoot"):
        errors.append("pod must run as non-root")
    if pod.get("securityContext", {}).get("seccompProfile", {}).get("type") != "RuntimeDefault":
        errors.append("pod must use the RuntimeDefault seccomp profile")
    if pod.get("automountServiceAccountToken") is not False:
        errors.append("pod must disable service-account token automount")
    for container in containers:
        security = container.get("securityContext", {})
        if security.get("allowPrivilegeEscalation") is not False:
            errors.append(f"{container.get('name')} must forbid privilege escalation")
        if security.get("readOnlyRootFilesystem") is not True:
            errors.append(f"{container.get('name')} must use a read-only root filesystem")
        if security.get("capabilities", {}).get("drop") != ["ALL"]:
            errors.append(f"{container.get('name')} must drop all Linux capabilities")
        if not any(mount.get("name") == "tmp" and mount.get("mountPath") == "/tmp" for mount in container.get("volumeMounts", [])):
            errors.append(f"{container.get('name')} must mount the temporary workspace at /tmp")
        resources = container.get("resources", {})
        if "ephemeral-storage" not in resources.get("requests", {}) or "ephemeral-storage" not in resources.get("limits", {}):
            errors.append(f"{container.get('name')} must bound ephemeral storage")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest-dir", type=Path, default=ROOT / "deployment" / "kubernetes")
    parser.add_argument("--render", action="store_true", help="also run kubectl kustomize when available")
    parser.add_argument("--image", help="also require an already-built local image (for example verification-pilot:0.1.0-local)")
    args = parser.parse_args()
    errors = validate(args.manifest_dir)
    if not errors and args.render:
        try:
            subprocess.run(["kubectl", "kustomize", str(args.manifest_dir)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        except FileNotFoundError:
            errors.append("kubectl is required when --render is supplied")
        except subprocess.CalledProcessError as exc:
            errors.append(f"kubectl kustomize failed: {exc.stderr.strip()}")
    if not errors and args.image:
        try:
            subprocess.run(["docker", "image", "inspect", args.image], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        except FileNotFoundError:
            errors.append("docker is required when --image is supplied")
        except subprocess.CalledProcessError:
            errors.append(f"required local image is unavailable: {args.image}")
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print(f"PASS: verification deployment preflight ({args.manifest_dir})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
