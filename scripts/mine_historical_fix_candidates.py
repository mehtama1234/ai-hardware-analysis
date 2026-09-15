"""Mine real upstream fix commits into a reviewable benchmark input manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
REPOSITORIES = {
    "OpenLane": Path("/home/mehtama1/eda-tools/OpenLane"),
    "OpenROAD-flow-scripts": Path("/home/mehtama1/eda-tools/OpenROAD-flow-scripts"),
    "cross-sim": Path("/home/mehtama1/eda-tools/cross-sim"),
}
KEYWORDS = re.compile(r"\b(fix|fixed|bug|regression|correct|repair|hotfix|issue)\b", re.IGNORECASE)
VALIDATED = {
    ("OpenLane", "6042457d"),
    ("OpenROAD-flow-scripts", "c178fbb7"),
    ("OpenLane", "1c950442"),
    ("OpenROAD-flow-scripts", "304e5765"),
    ("OpenROAD-flow-scripts", "53d01015"),
    ("OpenLane", "9dbd8b5e"),
    ("OpenLane", "de7e2ca3"),
    ("OpenROAD-flow-scripts", "4b688827"),
    ("cross-sim", "adbf6800"),
    ("OpenLane", "54d5b5a3"),
    ("OpenLane", "09cfff0d"),
    ("OpenLane", "074a92b7"),
    ("OpenLane", "023f6673"),
    ("OpenLane", "1d46ea5f"), ("OpenLane", "24dcb51e"),
    ("OpenLane", "f507637d"), ("OpenLane", "6c80fdbc"),
    ("OpenLane", "b5b0bbdf"), ("OpenLane", "4eab9f70"),
    ("OpenLane", "0b94d33d"), ("OpenLane", "0e8827eb"),
    ("OpenLane", "5ba7fa07"), ("OpenLane", "4ced43c5"),
    ("OpenLane", "08587051"), ("OpenLane", "41ed0036"),
    ("OpenLane", "fe0ba006"), ("OpenROAD-flow-scripts", "bad83a4f1"),
    ("OpenLane", "0e33bf4c"), ("OpenLane", "c5763988"),
    ("OpenLane", "7ea7a2ae"), ("cross-sim", "d9548c0"),
    ("OpenLane", "cb59d1f8"), ("OpenLane", "0687a36b"),
    ("OpenLane", "f4f8dad8"), ("OpenLane", "18a1df43"),
    ("OpenLane", "281281cc"),
    ("OpenLane", "413d3010"),
    ("OpenLane", "e99deff7"),
    ("OpenLane", "4c1c6538"),
    ("OpenLane", "cb634fd5"),
    ("OpenLane", "48004937"),
    ("OpenLane", "d4b42bd1"),
    ("OpenLane", "a664c0e1"),
    ("OpenROAD-flow-scripts", "91844308"),
    ("OpenLane", "b43df386"),
    ("OpenLane", "c98a290f"),
    ("OpenLane", "5f20beb7"),
    ("OpenLane", "01e95109"),
    ("OpenLane", "11dcdbbc"),
    ("OpenLane", "14ef870b"),
}


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def matches_validated(item: dict[str, object]) -> bool:
    repository = str(item.get("repository"))
    commit = str(item.get("commit"))
    return any(repository == repo and commit.startswith(prefix) for repo, prefix in VALIDATED)


def mine(repository: str, path: Path, limit: int) -> list[dict[str, object]]:
    if not path.is_dir():
        return []
    text = subprocess.check_output(["git", "-C", str(path), "log", "--all", "--format=%H%x09%P%x09%s", f"-n{limit}"], text=True, stderr=subprocess.DEVNULL)
    candidates = []
    for line in text.splitlines():
        commit, parents, subject = line.split("\t", 2)
        if not KEYWORDS.search(subject):
            continue
        files = subprocess.check_output(["git", "-C", str(path), "diff-tree", "--no-commit-id", "--name-only", "-r", commit], text=True, stderr=subprocess.DEVNULL).splitlines()
        if not files:
            continue
        candidates.append({"repository": repository, "commit": commit, "parent": parents.split()[0] if parents else None, "subject": subject, "files": files, "validation_status": "candidate_only", "claim_boundary": "mined from upstream history; regression reproduction and repair validation still required"})
    return candidates


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, required=True); parser.add_argument("--limit-per-repository", type=int, default=300); args = parser.parse_args(); args.output = args.output.resolve(); args.output.mkdir(parents=True, exist_ok=True)
    candidates = []
    for name, path in REPOSITORIES.items(): candidates.extend(mine(name, path, args.limit_per_repository))
    candidates.sort(key=lambda item: (str(item["repository"]), str(item["commit"])))
    heldout = [item for item in candidates if not matches_validated(item) and int(hashlib.sha256(f"{item['repository']}:{item['commit']}".encode()).hexdigest()[:2], 16) < 51]
    heldout_keys = {(item["repository"], item["commit"]) for item in heldout}
    development = [item for item in candidates if (item["repository"], item["commit"]) not in heldout_keys]
    body = {"schema_version": "historical-fix-candidate-manifest-v1", "repositories": sorted(REPOSITORIES), "candidate_count": len(candidates), "candidates": candidates, "development_count": len(development), "development_keys": [[item["repository"], item["commit"]] for item in development], "heldout_count": len(heldout), "heldout_keys": [[item["repository"], item["commit"]] for item in heldout], "validated_replay_count": len(VALIDATED), "target_validated_replay_count": 50, "claim_boundary": "candidate inventory is discovery evidence only; candidate_only entries are not repair or correctness claims; held-out keys must not be used for development"}
    body["manifest_sha256"] = digest(body); output = args.output / "historical-fix-candidate-manifest.json"; output.write_text(json.dumps(body, indent=2, sort_keys=True) + "\n", encoding="utf-8"); print(json.dumps({"status": "passed" if len(candidates) >= 50 else "blocked", "candidate_count": len(candidates), "repositories": len(REPOSITORIES), "manifest": str(output)}, sort_keys=True)); return 0 if len(candidates) >= 50 else 1


if __name__ == "__main__":
    raise SystemExit(main())
