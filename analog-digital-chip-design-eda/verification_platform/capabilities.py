"""Open-source backend capability discovery with explicit blocked states."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
import shutil
from typing import Iterable


@dataclass(frozen=True)
class ToolCapability:
    tool: str
    executable: str
    available: bool
    status: str


def discover_capabilities(tools: Iterable[tuple[str, str]] | None = None) -> list[ToolCapability]:
    """Discover executables without treating absence as a passing result."""
    requested = list(tools or [("iverilog", "iverilog"), ("verilator", "verilator"), ("yosys", "yosys"), ("sby", "sby")])
    if not requested:
        raise ValueError("at least one tool must be requested")
    result = []
    for name, executable in requested:
        if not name or not executable:
            raise ValueError("tool name and executable are required")
        available = shutil.which(executable) is not None
        result.append(ToolCapability(name, executable, available, "available" if available else "blocked"))
    return result


def write_capabilities(path: str | Path, capabilities: list[ToolCapability]) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps([asdict(item) for item in capabilities], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output
