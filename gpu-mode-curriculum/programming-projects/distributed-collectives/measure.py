#!/usr/bin/env python3
"""Run the starter and write the project measurement artifact."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
STARTER = HERE / "starter.py"
OUT = HERE / "measurements.json"


def main() -> int:
    proc = subprocess.run([sys.executable, str(STARTER)], cwd=HERE, capture_output=True, text=True, check=False)
    starter_payload = {}
    if proc.stdout.strip():
        try:
            starter_payload = json.loads(proc.stdout)
        except json.JSONDecodeError:
            starter_payload = {"raw_stdout": proc.stdout.strip()}
    status = starter_payload.get("status") or ("ran" if proc.returncode == 0 else "failed")
    artifact = {
        "project": "distributed-collectives",
        "track": "Distributed communication",
        "profile": "distributed-communication",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "correctness": {
            "status": "passed" if proc.returncode == 0 else "failed",
            "checks": {
                "starter_exited_zero": proc.returncode == 0,
                "starter_payload_status_present": bool(starter_payload.get("status")),
                "source_named": bool(starter_payload.get("source")),
            },
        },
        "runtime_readiness": {
            "status": status,
            "notes": starter_payload.get("runtime_notes", []),
        },
        "measurement": {
            "rows": [starter_payload],
            "summary": f"Starter {status} for Distributed communication; return code {proc.returncode}.",
        },
        "source": "collective_model.py",
        "environment": "local",
        "baseline_measurement": {"path": "26-gpumode-distributed-communication/out_gpumode_distributed_communication.json", "summary": "Imported 6 collective benchmark rows from 2 tool family/families; compare best bus bandwidth against the modeled topology rows. Best imported rows: nccl-tests 52.76 GB/s at 134217728 bytes, nvshmem 34.86 GB/s at 134217728 bytes."},
        "starter": {
            "command": f"{sys.executable} {STARTER.name}",
            "returncode": proc.returncode,
            "stdout_tail": proc.stdout.strip()[-2000:],
            "stderr_tail": proc.stderr.strip()[-2000:],
        },
    }
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": artifact["status"], "path": OUT.name, "correctness": artifact["correctness"]["status"]}, indent=2))
    return 0 if artifact["correctness"]["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
