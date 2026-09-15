#!/usr/bin/env python3
"""Promote historical-fix discovery and split manifests into durable evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


def sha256(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("candidate_manifest", type=Path); parser.add_argument("queue", type=Path); parser.add_argument("--output-dir", type=Path, required=True); args = parser.parse_args()
    candidate = json.loads(args.candidate_manifest.read_text(encoding="utf-8")); queue = json.loads(args.queue.read_text(encoding="utf-8")); output = args.output_dir.resolve(); output.mkdir(parents=True, exist_ok=True)
    files = {"historical-fix-candidate-manifest.json": args.candidate_manifest.resolve(), "historical-replay-queue.json": args.queue.resolve()}; artifacts = {}
    for name, source in files.items():
        dest = output / name; shutil.copyfile(source, dest); artifacts[name] = {"path": name, "sha256": sha256(dest), "size_bytes": dest.stat().st_size}
    metric = {"candidate_count": candidate.get("candidate_count"), "repositories": sorted({item.get("repository") for item in candidate.get("candidates", [])}), "development_count": candidate.get("development_count"), "heldout_count": candidate.get("heldout_count"), "validated_replay_count": candidate.get("validated_replay_count"), "queue_size": queue.get("queue_size"), "queue_repositories": sorted({item.get("repository") for item in queue.get("queue", [])})}
    status = "passed" if (metric["candidate_count"] >= 50 and len(metric["repositories"]) >= 3 and metric["heldout_count"] >= 15 and metric["validated_replay_count"] >= 50 and metric["queue_size"] == len(queue.get("queue", []))) else "blocked"
    receipt = {"schema_version":"historical-breadth-evidence-v1","generated_at":datetime.now(timezone.utc).isoformat(),"status":status,"artifacts":artifacts,"metrics":metric,"claim_boundary":"Historical-fix inventory, split integrity, and replay-queue evidence only; candidate entries still require regression reconstruction and agent repair validation, not generalization or production signoff."}; receipt["receipt_sha256"] = hashlib.sha256(json.dumps(receipt,sort_keys=True,separators=(",",":")).encode()).hexdigest(); (output/"receipt.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8"); print(json.dumps({"status":status,"output":str(output),"metrics":metric},sort_keys=True)); return 0 if status=="passed" else 1


if __name__ == "__main__": raise SystemExit(main())
