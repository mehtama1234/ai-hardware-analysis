"""Prevent validated historical replays from leaking into the held-out split."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

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
    ("OpenLane", "1d46ea5f"),
    ("OpenLane", "24dcb51e"),
    ("OpenLane", "f507637d"),
    ("OpenLane", "6c80fdbc"),
    ("OpenLane", "b5b0bbdf"),
    ("OpenLane", "4eab9f70"),
    ("OpenLane", "0b94d33d"),
    ("OpenLane", "0e8827eb"),
    ("OpenLane", "5ba7fa07"),
    ("OpenLane", "4ced43c5"),
    ("OpenLane", "08587051"),
    ("OpenLane", "41ed0036"),
    ("OpenLane", "fe0ba006"),
    ("OpenROAD-flow-scripts", "bad83a4f1"),
    ("OpenLane", "0e33bf4c"),
    ("OpenLane", "c5763988"),
    ("OpenLane", "7ea7a2ae"),
    ("cross-sim", "d9548c0"),
    ("OpenLane", "cb59d1f8"),
    ("OpenLane", "0687a36b"),
    ("OpenLane", "f4f8dad8"),
    ("OpenLane", "18a1df43"),
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


def matches_validated(key: tuple[object, object]) -> bool:
    return any(key[0] == repository and str(key[1]).startswith(commit) for repository, commit in VALIDATED)


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("manifest", type=Path); args = parser.parse_args(); manifest = json.loads(args.manifest.read_text(encoding="utf-8")); errors = []
    heldout = {tuple(item) for item in manifest.get("heldout_keys", [])}
    leaked = sorted(key for key in heldout if matches_validated(key))
    if leaked: errors.append(f"validated replay leaked into held-out split: {leaked}")
    if manifest.get("validated_replay_count") != len(VALIDATED): errors.append("validated replay count does not match registry")
    result = {"schema_version": "historical-replay-split-check-v1", "status": "passed" if not errors else "blocked", "validated_replay_count": len(VALIDATED), "heldout_leaks": leaked, "errors": errors, "manifest": str(args.manifest)}; result["check_sha256"] = digest(result); print(json.dumps(result, sort_keys=True)); return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
