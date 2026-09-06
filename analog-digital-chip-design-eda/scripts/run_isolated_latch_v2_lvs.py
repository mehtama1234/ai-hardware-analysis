#!/usr/bin/env python3
"""Compare the repaired extracted latch against its intended device schematic."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

from audit_isolated_latch_connectivity import audit

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "labs/analog/analog-in-memory-foundation-model-hardware"
CELL = "sky130_isolated_frontend_active_load_latch_v2"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-dir", type=Path,
                        help="Use an isolated paired-row layout/extraction instead of the preserved v2")
    args = parser.parse_args()
    candidate = args.candidate_dir.resolve() if args.candidate_dir else None
    if candidate:
        physical = json.loads((candidate / "result.json").read_text())
        for name in (f"{CELL}.mag", "extracted.spice"):
            if hashlib.sha256((candidate / name).read_bytes()).hexdigest() != physical.get("sha256", {}).get(name):
                raise SystemExit(f"Candidate physical-evidence hash mismatch: {name}")
        if not (physical["magic_returncode"] == 0 and physical["drc_errors"] == 0
                and physical["connectivity"]["topology_pass"] and physical["connectivity"]["body_ties_pass"]
                and physical["capacitance_export"]["pass"]):
            raise SystemExit("Candidate physical preflight failed")
    output = ROOT / "evidence/aimc-simulator-adapters/isolated-latch-v2-lvs" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    output.mkdir(parents=True, exist_ok=False)
    netgen = Path(os.environ.get("NETGEN_BIN", str(Path.home() / "eda-tools/netgen-1.5/bin/netgen")))
    pdk = Path(os.environ.get("PDK_ROOT", str(Path.home() / "eda-tools/pdks")))
    setup = pdk / "sky130A/libs.tech/netgen/sky130A_setup.tcl"
    sources = {
        "extracted.spice": LAB / f"layout-workbench/extracted/{CELL}_extracted.spice",
        "reference.spice": LAB / "spice/sky130_isolated_latch_v2_reference.spice",
        "layout.mag": LAB / f"layout-workbench/cells/{CELL}.mag",
    }
    if candidate:
        sources["extracted.spice"] = candidate / "extracted.spice"
        if (candidate / "reference.spice").exists():
            if hashlib.sha256((candidate / "reference.spice").read_bytes()).hexdigest() != physical["sha256"].get("reference.spice"):
                raise SystemExit("Candidate reference hash mismatch")
            sources["reference.spice"] = candidate / "reference.spice"
        sources["layout.mag"] = candidate / f"{CELL}.mag"
        sources["physical_check.json"] = candidate / "result.json"
        sources["magic.log"] = candidate / "magic.log"
    for name, source in sources.items():
        shutil.copy2(source, output / name)
    preflight = audit(output / "extracted.spice")
    # The retained transient extraction includes parasitic capacitors. Compare
    # MOS connectivity/dimensions in LVS; retain the exact unfiltered original
    # for transient use. No MOS terminal, property, or port is rewritten.
    lines = (output / "extracted.spice").read_text().splitlines()
    parasitics = [line for line in lines if line.lstrip().lower().startswith("c")]
    (output / "lvs_devices.spice").write_text("\n".join(line for line in lines if line not in parasitics) + "\n")
    command = [str(netgen), "-batch", "lvs", f"{output / 'lvs_devices.spice'} {CELL}",
               f"{output / 'reference.spice'} {CELL}", str(setup), str(output / "netgen.log")]
    proc = subprocess.run(command, cwd=output, capture_output=True, text=True,
                          timeout=60, env={**os.environ, "PDK_ROOT": str(pdk)})
    (output / "stdout.log").write_text(proc.stdout)
    (output / "stderr.log").write_text(proc.stderr)
    log = (output / "netgen.log").read_text() if (output / "netgen.log").exists() else ""
    matched = "Final result: Circuits match uniquely." in log and "Property errors were found" not in log
    passed = proc.returncode == 0 and matched and preflight["topology_pass"] and preflight["body_ties_pass"]
    report = {"status": "lvs_pass_subblock_only" if passed else "lvs_fail", "command": command,
              "candidate_directory": str(candidate) if candidate else None,
              "returncode": proc.returncode, "preflight": preflight, "matched_uniquely": matched,
              "lvs_view": "MOS devices and ports unchanged; extracted parasitic capacitor lines excluded from schematic comparison",
              "parasitic_capacitors_excluded_from_lvs": len(parasitics),
              "sha256": {name: hashlib.sha256((output / name).read_bytes()).hexdigest() for name in sources},
              "setup_sha256": hashlib.sha256(setup.read_bytes()).hexdigest(),
              "claim_boundary": "Same-candidate sub-block LVS only; no transistor transient or converter acceptance."}
    (output / "result.json").write_text(json.dumps(report, indent=2) + "\n")
    print(report["status"])
    print(output)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
