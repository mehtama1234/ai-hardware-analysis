#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SMOKE_DIR = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware" / "tool-smoke" / "magic-sky130-extraction"
PDK_MAGIC_RC = Path.home() / "eda-tools" / "pdks" / "sky130A" / "libs.tech" / "magic" / "sky130A.magicrc"
PDK_ROOT = Path.home() / "eda-tools" / "pdks"
LOCAL_MAGIC = Path.home() / "eda-tools" / "magic-8.3.682" / "bin" / "magic"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "magic-sky130-extraction-smoke.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "magic-sky130-extraction-smoke.md"


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def write_smoke_tcl() -> Path:
    SMOKE_DIR.mkdir(parents=True, exist_ok=True)
    tcl = SMOKE_DIR / "run-smoke.tcl"
    tcl.write_text(
        "\n".join(
            [
                "drc off",
                "load aimc_magic_smoke_wire -force",
                "box 0 0 200 40",
                "paint metal1",
                "label smoke_node center metal1",
                "port make",
                "save aimc_magic_smoke_wire",
                "extract all",
                "ext2spice lvs",
                "ext2spice cthresh 0",
                "ext2spice rthresh 0",
                "ext2spice -o aimc_magic_smoke_wire.spice",
                "quit -noprompt",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return tcl


def run_magic(tcl: Path) -> dict[str, Any]:
    magic_bin = Path(os.environ.get("MAGIC_BIN", str(LOCAL_MAGIC if LOCAL_MAGIC.is_file() else "magic")))
    command = [str(magic_bin), "-dnull", "-noconsole", "-rcfile", str(PDK_MAGIC_RC), str(tcl)]
    env = {**os.environ, "PDK_ROOT": str(PDK_ROOT)}
    proc = subprocess.run(command, cwd=SMOKE_DIR, text=True, capture_output=True, check=False, env=env)
    return {
        "command": " ".join(command),
        "magic_binary": str(magic_bin),
        "returncode": proc.returncode,
        "stdout_tail": proc.stdout[-2000:],
        "stderr_tail": proc.stderr[-2000:],
    }


def build_report() -> dict[str, Any]:
    tcl = write_smoke_tcl()
    run = run_magic(tcl)
    expected = {
        "magic_cell": SMOKE_DIR / "aimc_magic_smoke_wire.mag",
        "extract_file": SMOKE_DIR / "aimc_magic_smoke_wire.ext",
        "spice_file": SMOKE_DIR / "aimc_magic_smoke_wire.spice",
    }
    outputs = [
        {"name": name, "path": rel(path), "present": path.is_file() and path.stat().st_size > 0, "bytes": path.stat().st_size if path.is_file() else 0}
        for name, path in expected.items()
    ]
    passed = run["returncode"] == 0 and all(item["present"] for item in outputs)
    return {
        "result_type": "magic_sky130_extraction_smoke",
        "status": "magic_sky130_extraction_smoke_passed_not_converter_evidence" if passed else "magic_sky130_extraction_smoke_failed",
        "smoke_dir": rel(SMOKE_DIR),
        "pdk_magic_rc": str(PDK_MAGIC_RC),
        "pdk_root": str(PDK_ROOT),
        "preferred_local_magic": str(LOCAL_MAGIC),
        "preferred_local_magic_present": LOCAL_MAGIC.is_file(),
        "pdk_magic_rc_present": PDK_MAGIC_RC.is_file(),
        "run": run,
        "outputs": outputs,
        "passed": passed,
        "converter_cell_names_touched": [],
        "writes_candidate_post_layout_evidence": False,
        "claim_boundary": {
            "allowed": "proves Magic can load the Sky130 setup, save a tiny non-converter cell, extract it, and write SPICE",
            "not_allowed": "does not prove a DAC, ADC, mux, converter macro, extracted converter payload, area record, break-even rerun, or accepted post-layout evidence",
        },
    }


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# Magic Sky130 Extraction Smoke",
        "",
        f"- status: `{report['status']}`",
        f"- passed: `{report['passed']}`",
        f"- smoke dir: `{report['smoke_dir']}`",
        f"- PDK Magic rc present: `{report['pdk_magic_rc_present']}`",
        f"- writes candidate post-layout evidence: `{report['writes_candidate_post_layout_evidence']}`",
        "",
        "## First Principle",
        "",
        "Before a real converter can be extracted, the tool must be able to read the process rules, save a layout cell, derive an extracted circuit view, and write SPICE. This smoke test proves only that tool path.",
        "",
        "It uses a tiny metal wire, not a converter. That keeps the tool proof separate from the circuit proof.",
        "",
        "## Command",
        "",
        f"`{report['run']['command']}`",
        "",
        "## Outputs",
        "",
    ]
    lines.extend(f"- {item['name']}: `{item['path']}` present `{item['present']}` bytes `{item['bytes']}`" for item in report["outputs"])
    lines.extend(
        [
            "",
            "## Refused Claim",
            "",
            report["claim_boundary"]["not_allowed"],
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print("magic_sky130_extraction_smoke")
    print(f"status,{report['status']}")
    print(f"passed,{report['passed']}")
    print(f"returncode,{report['run']['returncode']}")
    print(f"writes_candidate_post_layout_evidence,{report['writes_candidate_post_layout_evidence']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
