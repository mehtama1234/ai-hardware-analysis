"""Validate a complete local CPU wheel set and emit a hash-checked pip lock."""
import argparse
import hashlib
import json
import zipfile
from email.parser import Parser
from pathlib import Path

from packaging.requirements import Requirement
from packaging.tags import sys_tags
from packaging.utils import canonicalize_name, parse_wheel_filename

ROOT = Path(__file__).resolve().parents[1]


def inspect_wheel(path):
    name, version, _, tags = parse_wheel_filename(path.name)
    if not set(tags) & set(sys_tags()):
        raise ValueError(f"wheel incompatible with this interpreter: {path.name}")
    with zipfile.ZipFile(path) as archive:
        candidates = [name for name in archive.namelist() if name.endswith(".dist-info/METADATA")]
        if len(candidates) != 1:
            raise ValueError(f"expected exactly one wheel METADATA: {path.name}")
        metadata = Parser().parsestr(archive.read(candidates[0]).decode("utf-8"))
    if canonicalize_name(metadata["Name"]) != name or metadata["Version"] != str(version):
        raise ValueError(f"filename/metadata mismatch: {path.name}")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return {"name": name, "version": str(version), "filename": path.name,
            "sha256": digest.hexdigest(), "bytes": path.stat().st_size,
            "requires": metadata.get_all("Requires-Dist", [])}


def build_lock(directory, requirements):
    expected = {}
    for line in requirements.read_text().splitlines():
        if line.strip() and not line.startswith("#"):
            requirement = Requirement(line)
            expected[canonicalize_name(requirement.name)] = requirement
    wheels = {}
    for path in sorted(directory.glob("*.whl")):
        row = inspect_wheel(path)
        if row["name"] in wheels:
            raise ValueError(f"duplicate distribution: {row['name']}")
        wheels[row["name"]] = row
    if set(wheels) != set(expected):
        raise ValueError(f"wheel set differs from pins: missing={sorted(set(expected)-set(wheels))}, extra={sorted(set(wheels)-set(expected))}")
    for name, row in wheels.items():
        if not expected[name].specifier.contains(row["version"]):
            raise ValueError(f"wheel version differs from pin: {name}")
        for raw in row["requires"]:
            requirement = Requirement(raw)
            if requirement.marker and not requirement.marker.evaluate({"extra": ""}):
                continue
            dependency = canonicalize_name(requirement.name)
            if requirement.url or dependency not in wheels or not requirement.specifier.contains(wheels[dependency]["version"]):
                raise ValueError(f"unsatisfied wheel dependency: {name} -> {dependency}")
    lines = ["# CPython 3.10 Linux x86_64 CPU checkpoint; exact inspected wheels.",
             "# Install with --no-index --find-links WHEEL_DIRECTORY --require-hashes."]
    lines.extend(f"{name}=={row['version']} --hash=sha256:{row['sha256']}" for name, row in sorted(wheels.items()))
    # Do not publish raw dependency metadata, which can contain direct URLs.
    manifest = [{k: v for k, v in row.items() if k != "requires"} for _, row in sorted(wheels.items())]
    return "\n".join(lines) + "\n", manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wheel_directory", type=Path)
    args = parser.parse_args()
    requirements = ROOT / "advanced-lab-phase/cpu-requirements.txt"
    lock, manifest = build_lock(args.wheel_directory, requirements)
    (ROOT / "advanced-lab-phase/cpu-wheel-lock.txt").write_text(lock)
    report = {"wheels": manifest, "requirements_sha256": hashlib.sha256(requirements.read_bytes()).hexdigest(),
              "wheel_set_validated": True, "hash_locked_installation_accepted": False,
              "scope": "exact wheel bytes, names, versions, platform compatibility and active default dependencies checked; no installation executed by this builder"}
    (ROOT / "advanced-lab-phase/cpu-wheel-manifest.json").write_text(json.dumps(report, indent=2) + "\n")
    print("validated", len(manifest), "wheels", sum(row["bytes"] for row in manifest), "bytes")


if __name__ == "__main__":
    main()
