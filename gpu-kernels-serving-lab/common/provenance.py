"""Bounded source provenance capture; deliberately excludes environment secrets."""
from __future__ import annotations

import hashlib
import platform
import subprocess
import sys
from pathlib import Path


def loaded_local_sources(repo: Path) -> set[Path]:
    """Snapshot imported Python sources in this repository, not site-packages."""
    repo = repo.resolve()
    result = set()
    for module in list(sys.modules.values()):
        filename = getattr(module, "__file__", None)
        if not isinstance(filename, str):
            continue
        path = Path(filename).resolve()
        if path.suffix != ".py" or not path.is_relative_to(repo) or not path.is_file():
            continue
        if "site-packages" in path.parts or ".venv" in path.parts:
            continue
        result.add(path)
    return result


def source_provenance(repo: Path, sources: list[Path]) -> dict:
    repo = repo.resolve()

    def git(*args: str) -> str | None:
        try:
            result = subprocess.run(["git", "-C", str(repo), *args],
                                    capture_output=True, text=True, timeout=10)
            return result.stdout.strip() if result.returncode == 0 else None
        except (OSError, subprocess.TimeoutExpired):
            return None

    files = {}
    explicit = set()
    for path in sources:
        path = path.resolve()
        path.relative_to(repo)  # Explicit out-of-tree sources remain an error.
        explicit.add(path)
    imported = loaded_local_sources(repo)
    for path in sorted(explicit | imported):
        relative = str(path.relative_to(repo))
        files[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    state = git("status", "--porcelain", "--untracked-files=normal")
    return {"git_revision": git("rev-parse", "HEAD"),
            "worktree_dirty": bool(state) if state is not None else None,
            "source_sha256": files, "python": sys.version,
            "imported_source_files": sorted(str(path.relative_to(repo)) for path in imported),
            "python_executable": sys.executable, "platform": platform.platform(),
            "invocation": [sys.executable, *sys.argv],
            "scope": "explicit sources plus imported local Python modules at capture time; excludes unexecuted branches, data files, third-party package sources and environment locks"}
