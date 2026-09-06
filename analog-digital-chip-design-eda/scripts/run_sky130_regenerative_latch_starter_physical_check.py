#!/usr/bin/env python3
"""DRC/extract a bounded real-device regenerative-latch starter cell."""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKBENCH = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware" / "layout-workbench"
CELL_DIR = WORKBENCH / "cells"
EXTRACT_DIR = WORKBENCH / "extracted"
CELL = "sky130_regenerative_latch_starter"
EXTRACTED = EXTRACT_DIR / f"{CELL}_extracted.spice"
EXT = CELL_DIR / f"{CELL}.ext"
MAGIC_BIN = Path(os.environ.get("MAGIC_BIN", str(Path.home() / "eda-tools" / "magic-8.3.682" / "bin" / "magic")))
PDK_ROOT = Path(os.environ.get("PDK_ROOT", str(Path.home() / "eda-tools" / "pdks")))
MAGIC_RC = Path(os.environ.get("MAGIC_RC", str(PDK_ROOT / "sky130A" / "libs.tech" / "magic" / "sky130A.magicrc")))
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-regenerative-latch-starter-physical-check.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-regenerative-latch-starter-physical-check.md"


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def main() -> int:
    commands = "\n".join([
        f"path search +{CELL_DIR}", f"load {CELL} -force", "select top cell",
        "drc on", "drc catchup", "drc count", "extract all", "ext2spice lvs",
        "ext2spice cthresh 0", "ext2spice rthresh 0", f"ext2spice -o {EXTRACTED.name}",
        "quit -noprompt", "",
    ])
    proc = subprocess.run([str(MAGIC_BIN), "-dnull", "-noconsole", "-rcfile", str(MAGIC_RC)],
                          cwd=EXTRACT_DIR, input=commands, text=True, capture_output=True,
                          check=False, env={**os.environ, "PDK_ROOT": str(PDK_ROOT)}, timeout=60)
    output = proc.stdout + proc.stderr
    matches = re.findall(r"Total DRC errors found:\s*(\d+)", output, re.I)
    ext_text = EXT.read_text(encoding="utf-8", errors="replace") if EXT.exists() else ""
    devices = [line for line in ext_text.splitlines() if line.startswith("device msubckt sky130_fd_pr__nfet_01v8")]
    nets = {name: any(f'"{name}"' in line for line in devices) or any(f'"{name}"' in line for line in ext_text.splitlines() if line.startswith(("port ", "equiv "))) for name in ("sense_p", "sense_n", "out_p", "out_n", "tail")}
    feedback_gate_labels = sum(any(f'"{name}"' in line for line in devices) for name in ("out_p", "out_n")) == 2
    quoted_devices = [re.findall(r'"([^"]+)"', line) for line in devices]
    output_drain_net_names_resolved = any(values[-1:] == ["out_p"] for values in quoted_devices) and any(values[-1:] == ["out_n"] for values in quoted_devices)
    cross_coupled_feedback = feedback_gate_labels and output_drain_net_names_resolved
    drc_errors = int(matches[-1]) if matches else None
    passed = proc.returncode == 0 and drc_errors == 0 and EXTRACTED.exists() and len(devices) == 4 and all(nets.values())
    report = {
        "result_type": "sky130_regenerative_latch_starter_physical_check",
        "status": "regenerative_latch_starter_extracted_drc_clean_feedback_verified_not_transient_or_converter_signoff" if passed and cross_coupled_feedback else ("regenerative_latch_starter_extracted_drc_clean_feedback_routing_open" if passed else "regenerative_latch_starter_incomplete"),
        "cell": CELL, "layout": rel(CELL_DIR / f"{CELL}.mag"), "extracted": rel(EXTRACTED),
        "magic_returncode": proc.returncode, "drc_error_count": drc_errors,
        "extracted_exists": EXTRACTED.exists(), "nfet_device_count": len(devices),
        "named_net_presence": nets, "feedback_gate_labels_present": feedback_gate_labels,
        "output_drain_net_names_resolved": output_drain_net_names_resolved,
        "cross_coupled_feedback_extracted": cross_coupled_feedback,
        "accepted_post_layout_written": False,
        "claim_boundary": {
            "allowed": "shows four real Sky130 NMOS shapes can be extracted as a bounded regenerative-latch starter with distinct input/output/tail nets and cross-coupled output-to-gate connectivity",
            "not_allowed": "does not prove transient regeneration, comparator noise/offset, LVS against a schematic, SAR conversion, full converter signoff, or accepted post-layout evidence",
        },
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text("\n".join([
        "# Sky130 Regenerative Latch Starter Physical Check", "",
        f"- status: `{report['status']}`", f"- DRC errors: `{drc_errors}`",
        f"- extracted NFET devices: `{len(devices)}`", f"- named nets present: `{nets}`", "",
        "This is the first real-device regenerative-latch physical slice. Magic extraction records distinct input/output/common-tail nets and the intended feedback-gate labels. Output-to-gate feedback routing, transient regeneration, and full comparator/converter acceptance remain open.",
        "", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], "",
    ]), encoding="utf-8")
    print(f"status,{report['status']}")
    print(f"drc_errors,{drc_errors}")
    print(f"nfet_device_count,{len(devices)}")
    print(f"json,{OUT_JSON}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
