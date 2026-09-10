"""SVA compilation adapter with explicit tool capability reporting."""

from __future__ import annotations

from pathlib import Path

from .ledger import ToolRun
from .runner import run_command


def compile_sva_with_iverilog(source: str | Path, *, run_root: str | Path, source_revision: str = "unknown", timeout_seconds: float = 60.0) -> ToolRun:
    """Attempt compilation and preserve Icarus's SVA capability result."""
    output = Path(run_root) / "sva.vvp"
    return run_command(["iverilog", "-g2012", "-o", str(output), str(source)], tool="iverilog-sva", run_root=run_root, source_revision=source_revision, timeout_seconds=timeout_seconds)


def compile_sva_with_verilator(source: str | Path, *, run_root: str | Path, source_revision: str = "unknown", timeout_seconds: float = 60.0) -> ToolRun:
    """Attempt Verilator lint and preserve whether this install supports the SVA subset."""
    return run_command(["verilator", "--lint-only", str(source)], tool="verilator-sva", run_root=run_root, source_revision=source_revision, timeout_seconds=timeout_seconds)
