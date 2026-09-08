"""Verify isolation and reproduce the CPU checkpoint; current source tree only."""
import hashlib
import importlib.metadata as metadata
import json
import argparse
import site
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from packaging.requirements import Requirement
import torch
import sklearn

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
REQUIREMENTS = ROOT / "advanced-lab-phase/cpu-requirements.txt"
WHEEL_LOCK = ROOT / "advanced-lab-phase/cpu-wheel-lock.txt"
WHEEL_MANIFEST = ROOT / "advanced-lab-phase/cpu-wheel-manifest.json"


def main():
    parser = argparse.ArgumentParser(description="Verify an isolated CPU environment and run the advanced checkpoint")
    parser.add_argument("--timeout", type=int, default=1800,
                        help="checkpoint timeout in seconds (default: 1800)")
    args = parser.parse_args()
    prefix = Path(sys.prefix).resolve()
    cfg = prefix / "pyvenv.cfg"
    checks = {"virtual_environment": sys.prefix != sys.base_prefix,
              "system_site_packages_disabled": cfg.exists() and "include-system-site-packages = false" in cfg.read_text().lower(),
              "user_site_disabled": site.ENABLE_USER_SITE is False,
              "torch_loaded_from_environment": Path(torch.__file__).resolve().is_relative_to(prefix),
              "sklearn_loaded_from_environment": Path(sklearn.__file__).resolve().is_relative_to(prefix),
              "cpu_only_torch": torch.version.cuda is None and not torch.cuda.is_available()}
    versions = {}
    for line in REQUIREMENTS.read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        requirement = Requirement(line)
        try:
            version = metadata.version(requirement.name)
        except metadata.PackageNotFoundError:
            version = None
        versions[requirement.name] = version
        checks[f"pin:{requirement.name}"] = version is not None and requirement.specifier.contains(version)
    pip_check = subprocess.run([sys.executable, "-m", "pip", "check"], capture_output=True, text=True, timeout=60)
    checks["pip_check"] = pip_check.returncode == 0
    report = {"started_at": datetime.now(timezone.utc).isoformat(), "checks": checks,
              "python_executable": sys.executable, "python_prefix": sys.prefix,
              "python_base_prefix": sys.base_prefix, "versions": versions,
              "requirements_sha256": hashlib.sha256(REQUIREMENTS.read_bytes()).hexdigest(),
              "wheel_lock_sha256": hashlib.sha256(WHEEL_LOCK.read_bytes()).hexdigest(),
              "wheel_manifest_sha256": hashlib.sha256(WHEEL_MANIFEST.read_bytes()).hexdigest(),
              "pip_check": {"returncode": pip_check.returncode, "stdout": pip_check.stdout, "stderr": pip_check.stderr},
              "fresh_checkout_accepted": False, "full_goal_accepted": False,
              "scope": "isolated CPU package environment using current worktree; not clean checkout, hashed wheel lock, GPU validation or independent host reproduction"}
    if all(checks.values()):
        command = [sys.executable, str(ROOT / "scripts/run_advanced_evidence_regression.py")]
        print("isolation and pins passed; running full checkpoint", flush=True)
        try:
            started = time.time()
            result = subprocess.run(command, cwd=REPO, capture_output=True, text=True, timeout=args.timeout)
            report["execution"] = {"command": command, "returncode": result.returncode,
                                   "stdout": result.stdout, "stderr": result.stderr}
            path = ROOT / "advanced-lab-phase/executable-checkpoint.json"
            checkpoint = json.loads(path.read_text()) if path.exists() else {}
            checks["checkpoint_succeeded"] = result.returncode == 0 and checkpoint.get("status") == "checkpoint_passed"
            checks["checkpoint_regenerated"] = path.exists() and path.stat().st_mtime >= started
            checks["checkpoint_used_this_interpreter"] = bool(checkpoint.get("steps")) and all(
                step.get("command", [None])[0] == sys.executable for step in checkpoint.get("steps", []))
            report["checkpoint_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None
        except (subprocess.TimeoutExpired, OSError, ValueError) as exc:
            checks["checkpoint_succeeded"] = False
            report["execution_error"] = str(exc)
    report["isolated_cpu_checkpoint_accepted"] = all(checks.values())
    report["completed_at"] = datetime.now(timezone.utc).isoformat()
    output = ROOT / "advanced-lab-phase/isolated-cpu-reproduction.json"
    output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print("isolated_cpu_checkpoint_accepted", report["isolated_cpu_checkpoint_accepted"], output)
    return 0 if report["isolated_cpu_checkpoint_accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
