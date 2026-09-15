"""Execute a registered customer adapter through the common evidence contract."""

from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path

from deployment.adapter_registry import adapter_spec
from verification_platform.adapter import execute_adapter

MAX_ADAPTER_ARGS = 64
MAX_ADAPTER_ARG_BYTES = 4096
MAX_ADAPTER_ARGS_BYTES = 65536


def validate_adapter_args(args: list[str]) -> None:
    if not isinstance(args, list) or len(args) > MAX_ADAPTER_ARGS:
        raise ValueError(f"adapter_args must contain at most {MAX_ADAPTER_ARGS} arguments")
    if any(not isinstance(arg, str) or not arg for arg in args):
        raise ValueError("adapter args must be a list of non-empty strings")
    if any(len(arg.encode("utf-8")) > MAX_ADAPTER_ARG_BYTES for arg in args):
        raise ValueError(f"each adapter argument must be at most {MAX_ADAPTER_ARG_BYTES} bytes")
    if sum(len(arg.encode("utf-8")) for arg in args) > MAX_ADAPTER_ARGS_BYTES:
        raise ValueError(f"adapter arguments must total at most {MAX_ADAPTER_ARGS_BYTES} bytes")


def execute_registered_adapter(*, name: str, args: list[str], run_root: str | Path, source_revision: str) -> dict[str, object]:
    """Run one registered adapter and persist its bounded result record."""
    validate_adapter_args(args)
    spec = adapter_spec(name)
    run = execute_adapter(spec, args, run_root=run_root, source_revision=source_revision)
    payload = asdict(run)
    output = Path(run_root) / "adapter-result.json"
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"status": run.status, "exit_code": run.exit_code, "tool": run.tool, "adapter_result": str(output)}
