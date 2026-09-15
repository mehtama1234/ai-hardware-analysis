"""Validated customer EDA adapter discovery for deployment-time capability UI."""

from __future__ import annotations

import json
import math
import os
import re
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path

from verification_platform.adapter import AdapterSpec


@dataclass(frozen=True)
class RegisteredAdapter:
    name: str
    kind: str
    executable: str
    version: str | None
    available: bool
    status: str
    expected_artifacts: tuple[str, ...] = ()
    timeout_seconds: float = 1800.0


def discover_registered_adapters(raw: str | None = None) -> list[RegisteredAdapter]:
    """Parse ``VERIFICATION_EDA_ADAPTERS`` without exposing secrets.

    The variable is deployment configuration, not a credential channel. Each
    entry contains only identity and executable metadata; availability is
    checked locally so the workbench can distinguish configured from blocked.
    """
    encoded = os.environ.get("VERIFICATION_EDA_ADAPTERS", "") if raw is None else raw
    if not encoded.strip():
        return []
    try:
        entries = json.loads(encoded)
    except json.JSONDecodeError as error:
        raise ValueError("VERIFICATION_EDA_ADAPTERS must be a JSON array") from error
    if not isinstance(entries, list):
        raise ValueError("VERIFICATION_EDA_ADAPTERS must be a JSON array")
    result: list[RegisteredAdapter] = []
    seen: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("each EDA adapter must be an object")
        name, kind, executable = (str(entry.get(field, "")).strip() for field in ("name", "kind", "executable"))
        version = entry.get("version")
        raw_artifacts = entry.get("expected_artifacts", [])
        if not isinstance(raw_artifacts, list) or any(not isinstance(path, str) or not path.strip() for path in raw_artifacts):
            raise ValueError("adapter expected_artifacts must be a list of non-empty strings")
        expected_artifacts = tuple(path.strip() for path in raw_artifacts)
        for path in expected_artifacts:
            candidate = Path(path)
            if candidate.is_absolute() or ".." in candidate.parts:
                raise ValueError("adapter expected_artifacts must stay inside the job workspace")
        raw_timeout = entry.get("timeout_seconds", 1800.0)
        if isinstance(raw_timeout, bool):
            raise ValueError("adapter timeout_seconds must be a finite positive number")
        try:
            timeout_seconds = float(raw_timeout)
        except (TypeError, ValueError) as error:
            raise ValueError("adapter timeout_seconds must be a finite positive number") from error
        if not math.isfinite(timeout_seconds) or timeout_seconds <= 0 or timeout_seconds > 86400:
            raise ValueError("adapter timeout_seconds must be between 0 and 86400")
        if not name or not re.fullmatch(r"[A-Za-z0-9_.:-]{1,80}", name) or name in seen:
            raise ValueError("adapter names must be unique and use safe characters")
        if not kind or not re.fullmatch(r"[A-Za-z0-9_.:-]{1,40}", kind):
            raise ValueError("adapter kind is required and must use safe characters")
        if not executable or "/" in executable or "\\" in executable:
            raise ValueError("adapter executable must be a command name")
        if version is not None and not isinstance(version, str):
            raise ValueError("adapter version must be a string")
        seen.add(name)
        available = shutil.which(executable) is not None
        result.append(RegisteredAdapter(name, kind, executable, version, available, "available" if available else "blocked", expected_artifacts, timeout_seconds))
    return result


def adapter_payload(raw: str | None = None) -> list[dict[str, object]]:
    return [asdict(item) for item in discover_registered_adapters(raw)]


def adapter_spec(name: str, raw: str | None = None) -> AdapterSpec:
    """Resolve a registered adapter into the common execution contract."""
    if not isinstance(name, str) or not name.strip():
        raise ValueError("adapter name is required")
    matches = [item for item in discover_registered_adapters(raw) if item.name == name]
    if not matches:
        raise ValueError(f"adapter is not registered: {name}")
    item = matches[0]
    return AdapterSpec(item.name, item.executable, expected_artifacts=item.expected_artifacts, timeout_seconds=item.timeout_seconds)
