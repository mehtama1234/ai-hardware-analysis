#!/usr/bin/env python3
"""Run a bounded Netgen topology smoke test for the active isolation pair."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKBENCH = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware" / "layout-workbench"
EXTRACTED = WORKBENCH / "extracted" / "sky130_transistor_active_isolation_pair_extracted.spice"
PDK_ROOT = Path(os.environ.get("PDK_ROOT", str(Path.home() / "eda-tools" / "pdks")))
NETGEN_BIN = Path(os.environ.get("NETGEN_BIN", str(Path.home() / "eda-tools" / "netgen-1.5" / "bin" / "netgen")))
SETUP = PDK_ROOT / "sky130A" / "libs.tech" / "netgen" / "sky130A_setup.tcl"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "active-isolation-pair-lvs-smoke.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "active-isolation-pair-lvs-smoke.md"
CELL = "sky130_transistor_active_isolation_pair"

REFERENCE = """* Independent topology reference for a Netgen smoke test.
.subckt sky130_transistor_active_isolation_pair iso_tail iso_p iso_n sense_p sense_n
X0 iso_tail sense_n iso_n vsub sky130_fd_pr__nfet_01v8
X1 iso_p sense_p iso_tail vsub sky130_fd_pr__nfet_01v8
.ends sky130_transistor_active_isolation_pair
"""


def main() -> int:
    required = (EXTRACTED, SETUP, NETGEN_BIN)
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        report = {
            "result_type": "active_isolation_pair_lvs_smoke",
            "status": "lvs_smoke_blocked_missing_input",
            "missing": missing,
            "accepted_ready_now": False,
        }
        OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        OUT_MD.write_text("# Active Isolation Pair LVS Smoke\n\nStatus: blocked; missing input.\n", encoding="utf-8")
        print(f"status,{report['status']}")
        return 1

    with tempfile.TemporaryDirectory(prefix="aimc-netgen-") as temp:
        temp_dir = Path(temp)
        reference = temp_dir / "reference.spice"
        log = temp_dir / "netgen.log"
        reference.write_text(REFERENCE, encoding="utf-8")
        command = [
            str(NETGEN_BIN),
            "-batch",
            "lvs",
            f"{EXTRACTED} {CELL}",
            f"{reference} {CELL}",
            str(SETUP),
            str(log),
        ]
        proc = subprocess.run(command, cwd=WORKBENCH, text=True, capture_output=True, check=False, env={**os.environ, "PDK_ROOT": str(PDK_ROOT)})
        output = proc.stdout + proc.stderr
        log_text = log.read_text(encoding="utf-8", errors="replace") if log.exists() else ""
        combined = output + log_text
        matched = "Final result: Circuits match uniquely." in combined
        device_count_seen = "Number of devices: 2" in combined
        net_count_seen = "Number of nets: 6" in combined
        report = {
            "result_type": "active_isolation_pair_lvs_smoke",
            "status": "active_isolation_pair_lvs_smoke_passed_not_converter_signoff" if proc.returncode == 0 and matched and device_count_seen and net_count_seen else "active_isolation_pair_lvs_smoke_failed",
            "cell": CELL,
            "returncode": proc.returncode,
            "netgen_version": output.splitlines()[0] if output.splitlines() else None,
            "matched_uniquely": matched,
            "extracted_device_count_seen": 2 if device_count_seen else None,
            "extracted_net_count_seen": 6 if net_count_seen else None,
            "command": " ".join(command),
            "accepted_ready_now": False,
            "claim_boundary": {
                "allowed": "shows that Netgen can parse the extracted active isolation-pair subcell and match its two-device, six-net topology against an independent smoke-test reference",
                "not_allowed": "does not prove the full converter schematic, converter LVS, matching, parasitic accuracy, post-layout behavior, silicon behavior, or signoff readiness",
            },
            "output_tail": combined[-4000:],
        }

    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "\n".join(
            [
                "# Active Isolation Pair LVS Smoke",
                "",
                f"- status: `{report['status']}`",
                f"- cell: `{CELL}`",
                f"- unique match: `{report['matched_uniquely']}`",
                f"- extracted devices seen: `{report['extracted_device_count_seen']}`",
                f"- extracted nets seen: `{report['extracted_net_count_seen']}`",
                "",
                "This is a bounded subcell topology smoke test. It is not full converter LVS or post-layout acceptance.",
                "",
                "## Refused claim",
                "",
                report["claim_boundary"]["not_allowed"],
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"status,{report['status']}")
    print(f"matched_uniquely,{report['matched_uniquely']}")
    print(f"devices_seen,{report['extracted_device_count_seen']}")
    print(f"nets_seen,{report['extracted_net_count_seen']}")
    return 0 if report["status"].endswith("passed_not_converter_signoff") else 1


if __name__ == "__main__":
    raise SystemExit(main())
