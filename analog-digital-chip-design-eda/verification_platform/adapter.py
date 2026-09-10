"""Reusable customer-tool adapter contract over the provenance runner."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .ledger import ToolRun
from .runner import run_command


@dataclass(frozen=True)
class AdapterSpec:
    name: str
    executable: str
    expected_artifacts: tuple[str, ...] = ()


def execute_adapter(spec: AdapterSpec, args: list[str], *, run_root: str | Path, source_revision: str, timeout_seconds: float = 60.0) -> ToolRun:
    """Execute a named backend while preserving the common run contract."""
    if not spec.name or not spec.executable or any(not isinstance(arg, str) for arg in args):
        raise ValueError("adapter name, executable, and string args are required")
    return run_command([spec.executable, *args], tool=spec.name, run_root=run_root, source_revision=source_revision, timeout_seconds=timeout_seconds, expected_artifacts=list(spec.expected_artifacts))
