#!/usr/bin/env python3
"""Screen the latch-only reset-timing repair across process and temperature."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "evidence/aimc-simulator-adapters/isolated-latch-v2-transient/20260906T202600550851Z"
RUNNER = ROOT / "scripts/run_latch_repeated_readout.py"
PROFILES = [(corner, 27) for corner in ("tt", "ff", "ss", "fs", "sf")] + [("tt", -40), ("tt", 125)]


def main() -> int:
    out = ROOT / "evidence/aimc-simulator-adapters/latch-output-legality-screen" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    out.mkdir(parents=True, exist_ok=False)
    contract = {
        "schema_version": "latch_output_legality_screen.v1",
        "source_run": str(SOURCE),
        "runner_sha256": hashlib.sha256(RUNNER.read_bytes()).hexdigest(),
        "input_diffs_mv": [-0.5, 0.5, -0.5, 0.5],
        "reset_early_ns": 0.5,
        "clock_fall_ps": 1000,
        "receiver_added": False,
        "profiles": PROFILES,
        "claim_boundary": "Latch-only extracted diagnostic; ideal sources and no receiver, full converter, PVT mismatch, noise or silicon qualification.",
    }
    (out / "contract.json").write_text(json.dumps(contract, indent=2) + "\n")
    rows = []
    for corner, temperature in PROFILES:
        cmd = [sys.executable, str(RUNNER), str(SOURCE), "--input-diffs-mv", "-0.5", "0.5", "-0.5", "0.5",
               "--reset-early-ns", "0.5", "--clock-fall-ps", "1000", "--corner", corner,
               "--temperature-c", str(temperature), "--timeout-s", "90"]
        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=120)
        (out / f"{corner}-{temperature}.log").write_text(proc.stdout + proc.stderr)
        lines = proc.stdout.strip().splitlines()
        run = Path(lines[-1]) if lines else None
        row = {"corner": corner, "temperature_c": temperature, "returncode": proc.returncode, "measured": False}
        if run and run.is_relative_to(ROOT / "evidence/aimc-simulator-adapters/latch-repeated-readout") and (run / "result.json").exists():
            result = json.loads((run / "result.json").read_text())
            row.update({
                "run": str(run),
                "status": result.get("status"),
                "measured": len(result.get("rows", [])) == 4,
                "waveform_legal": result.get("waveform_legal", False),
                "all_rows_pass": bool(result.get("rows")) and all(r.get("pass", False) for r in result["rows"]),
                "min_output_v": min(result.get("node_voltage_extrema_v", {}).get(name, [None])[0] for name in ("v(out_p)", "v(out_n)")),
                "max_output_v": max(result.get("node_voltage_extrema_v", {}).get(name, [None, None])[1] for name in ("v(out_p)", "v(out_n)")),
                "result_sha256": hashlib.sha256((run / "result.json").read_bytes()).hexdigest(),
            })
        rows.append(row)
        print(json.dumps(row), flush=True)
    result = {
        "schema_version": "latch_output_legality_screen.v1",
        "status": "screen_complete_not_qualified",
        "repair_candidate": "reset_early_0.5ns_clock_fall_1000ps",
        "rows": rows,
        "all_profiles_waveform_legal": all(r.get("waveform_legal", False) for r in rows),
        "all_profiles_pass": all(r.get("all_rows_pass", False) for r in rows),
        "accepted_converter": False,
        "claim_boundary": contract["claim_boundary"],
    }
    (out / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
