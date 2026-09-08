"""Audit installed dependency closure; this is not a wheel-hashed lockfile."""
import importlib.metadata as metadata
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

ROOT = Path(__file__).resolve().parents[1]
ROOTS = ("torch", "numpy", "scikit-learn", "packaging")


def capture():
    pending = list(ROOTS)
    packages, problems = {}, []
    while pending:
        name = canonicalize_name(pending.pop())
        if name in packages:
            continue
        try:
            distribution = metadata.distribution(name)
        except metadata.PackageNotFoundError:
            packages[name] = {"installed": False}
            problems.append(f"missing required distribution: {name}")
            continue
        dependencies = []
        packages[name] = {"installed": True, "version": distribution.version,
                          "dependencies": dependencies}
        for raw in distribution.requires or []:
            requirement = Requirement(raw)
            if requirement.marker and not requirement.marker.evaluate({"extra": ""}):
                continue
            dependency = canonicalize_name(requirement.name)
            # Record names and constraints only, never direct URLs or environment
            # variables that could expose credentials from installation metadata.
            dependencies.append({"name": dependency, "specifier": str(requirement.specifier),
                                 "direct_url_redacted": requirement.url is not None})
            if requirement.url:
                problems.append(f"direct URL dependency needs separate reproducibility review: {name} -> {dependency}")
            try:
                version = metadata.version(dependency)
                if requirement.specifier and not requirement.specifier.contains(version, prereleases=True):
                    problems.append(f"constraint mismatch: {name} requires {dependency}{requirement.specifier}; installed {version}")
            except metadata.PackageNotFoundError:
                pass  # The traversal records a missing dependency once.
            pending.append(dependency)
    report = {"captured_at": datetime.now(timezone.utc).isoformat(),
              "python": sys.version, "platform": platform.platform(), "roots": ROOTS,
              "packages": dict(sorted(packages.items())), "problems": problems,
              "status": "installed_metadata_consistent" if not problems else "environment_review_required",
              "isolated_reproduction_accepted": False,
              "scope": "installed distribution metadata closure for active platform/default extras; not wheel provenance, optional lab dependencies, ABI validation or clean-environment reproduction"}
    folder = ROOT / "advanced-lab-phase"
    (folder / "environment-snapshot.json").write_text(json.dumps(report, indent=2) + "\n")
    pins = [f"{name}=={row['version']}" for name, row in sorted(packages.items()) if row.get("installed")]
    (folder / "observed-environment-constraints.txt").write_text(
        "# Observed installed versions, not an independently reproduced environment or hash lock.\n" +
        "# See environment-snapshot.json for missing dependencies and conflicts before using.\n" + "\n".join(pins) + "\n")
    print(report["status"], len(packages), "distributions")
    for problem in problems:
        print(problem)
    return report


if __name__ == "__main__":
    capture()
