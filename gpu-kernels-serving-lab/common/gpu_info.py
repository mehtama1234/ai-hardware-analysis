"""Hardware and software inventory helpers.

The lab should produce useful evidence on any machine. If CUDA, ROCm, JAX, vLLM,
or Transformers are missing, the helpers record that as a skip/status result
instead of failing the whole tutorial.
"""

from __future__ import annotations

import importlib.metadata
import json
import platform
import shutil
import subprocess
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any


PACKAGES = [
    "torch",
    "triton",
    "transformers",
    "accelerate",
    "bitsandbytes",
    "vllm",
    "jax",
    "jaxlib",
]


def _run(cmd: list[str], timeout: int = 5) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except Exception as exc:  # pragma: no cover - defensive environment capture
        return 1, "", str(exc)


def _version(package: str) -> str | None:
    try:
        return importlib.metadata.version(package)
    except importlib.metadata.PackageNotFoundError:
        return None


def software_inventory() -> dict[str, Any]:
    return {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "packages": {name: _version(name) for name in PACKAGES},
    }


def torch_inventory() -> dict[str, Any]:
    out: dict[str, Any] = {"installed": False}
    try:
        import torch  # type: ignore
    except Exception as exc:
        out["import_error"] = str(exc)
        return out

    out.update(
        {
            "installed": True,
            "version": getattr(torch, "__version__", None),
            "cuda_available": bool(torch.cuda.is_available()),
            "cuda_version": getattr(torch.version, "cuda", None),
            "hip_version": getattr(torch.version, "hip", None),
            "mps_available": bool(
                hasattr(torch.backends, "mps") and torch.backends.mps.is_available()
            ),
            "devices": [],
        }
    )
    if torch.cuda.is_available():
        for idx in range(torch.cuda.device_count()):
            props = torch.cuda.get_device_properties(idx)
            out["devices"].append(
                {
                    "index": idx,
                    "name": torch.cuda.get_device_name(idx),
                    "total_memory_mb": round(props.total_memory / 1e6, 1),
                    "major": props.major,
                    "minor": props.minor,
                    "multi_processor_count": props.multi_processor_count,
                }
            )
    return out


def command_inventory() -> dict[str, Any]:
    commands: dict[str, Any] = {}
    for name, cmd in {
        "nvidia-smi": ["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"],
        "nvcc": ["nvcc", "--version"],
        "hipcc": ["hipcc", "--version"],
        "rocminfo": ["rocminfo"],
    }.items():
        path = shutil.which(cmd[0])
        entry: dict[str, Any] = {"path": path}
        if path:
            code, stdout, stderr = _run(cmd, timeout=8)
            entry.update({"returncode": code, "stdout_head": stdout.splitlines()[:5]})
            if stderr:
                entry["stderr_head"] = stderr.splitlines()[:5]
        commands[name] = entry
    return commands


def jax_inventory() -> dict[str, Any]:
    out: dict[str, Any] = {"installed": False}
    try:
        import jax  # type: ignore
    except Exception as exc:
        out["import_error"] = str(exc)
        return out

    devices = []
    for dev in jax.devices():
        devices.append(
            {
                "platform": getattr(dev, "platform", None),
                "device_kind": getattr(dev, "device_kind", str(dev)),
                "id": getattr(dev, "id", None),
            }
        )
    out.update({"installed": True, "version": getattr(jax, "__version__", None), "devices": devices})
    return out


@dataclass
class LabInventory:
    session: str
    timestamp: str
    host: str
    software: dict[str, Any]
    torch: dict[str, Any]
    jax: dict[str, Any]
    commands: dict[str, Any]
    boundary: str


def collect_inventory(session: str) -> dict[str, Any]:
    inv = LabInventory(
        session=session,
        timestamp=datetime.now(timezone.utc).isoformat(),
        host=platform.node(),
        software=software_inventory(),
        torch=torch_inventory(),
        jax=jax_inventory(),
        commands=command_inventory(),
        boundary=(
            "This inventory proves which local runtimes and accelerator interfaces are "
            "available for later tutorials. It does not benchmark model throughput or "
            "prove CUDA/ROCm correctness."
        ),
    )
    return asdict(inv)


def main() -> None:
    print(json.dumps(collect_inventory("inventory"), indent=2))


if __name__ == "__main__":
    main()

