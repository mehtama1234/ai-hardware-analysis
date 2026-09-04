#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
WORKBENCH = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware" / "layout-workbench"
PDK = Path.home() / "eda-tools" / "pdks" / "sky130A"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "analog-converter-sky130-workbench-env.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "analog-converter-sky130-workbench-env.md"

PDK_FILES = {
    "magic_rc": PDK / "libs.tech" / "magic" / "sky130A.magicrc",
    "magic_tech": PDK / "libs.tech" / "magic" / "sky130A.tech",
    "xschem_rc": PDK / "libs.tech" / "xschem" / "xschemrc",
    "ngspice_lib": PDK / "libs.tech" / "ngspice" / "sky130.lib.spice",
    "ngspice_tt": PDK / "libs.tech" / "ngspice" / "corners" / "tt.spice",
}

ENV_FILES = {
    ".magicrc": """# Local Magic setup for the AIMC converter layout workbench.
# This file points Magic at the installed Sky130A PDK.

source {magic_rc}
""",
    "sky130-ngspice.includes": """.lib {ngspice_lib} tt
.include {ngspice_tt}
""",
    "xschemrc.local": """# Local xschem setup for the AIMC converter layout workbench.
# Start xschem from this directory and use the installed Sky130A xschemrc.

source {xschem_rc}
""",
    "run-layout-env-check.sh": """#!/usr/bin/env bash
set -euo pipefail

echo "AIMC converter Sky130 workbench environment"
echo "workbench: $(pwd)"
test -f .magicrc
test -f xschemrc.local
test -f sky130-ngspice.includes
test -f "{magic_tech}"
test -f "{ngspice_lib}"
test -f "{ngspice_tt}"
command -v magic >/dev/null
command -v xschem >/dev/null
command -v ngspice >/dev/null
echo "ready_for_manual_layout_start=true"
echo "not_post_layout_evidence=true"
""",
}


def rel_or_abs(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def write_env_files() -> list[dict[str, Any]]:
    WORKBENCH.mkdir(parents=True, exist_ok=True)
    written = []
    format_values = {key: str(path) for key, path in PDK_FILES.items()}
    for name, template in ENV_FILES.items():
        path = WORKBENCH / name
        path.write_text(template.format(**format_values), encoding="utf-8")
        if name.endswith(".sh"):
            path.chmod(0o755)
        written.append({"path": rel_or_abs(path), "bytes": path.stat().st_size})
    return written


def physical_cell_count() -> int:
    patterns = ["*.sch", "*.mag", "*.gds", "*.lef", "*.dspf", "*.spef"]
    return sum(
        1
        for pattern in patterns
        for path in WORKBENCH.rglob(pattern)
        if path.is_file() and path.stat().st_size > 0 and path.name not in {".magicrc"}
    )


def build_report() -> dict[str, Any]:
    pdk_records = [
        {"name": name, "path": str(path), "exists": path.is_file(), "bytes": path.stat().st_size if path.is_file() else 0}
        for name, path in PDK_FILES.items()
    ]
    env_files = write_env_files()
    return {
        "result_type": "analog_converter_sky130_workbench_env",
        "status": "sky130_workbench_environment_ready_not_layout",
        "workbench": rel_or_abs(WORKBENCH),
        "env_file_count": len(env_files),
        "env_files": env_files,
        "pdk_files": pdk_records,
        "all_pdk_files_present": all(item["exists"] and item["bytes"] > 0 for item in pdk_records),
        "physical_converter_cell_count": physical_cell_count(),
        "ready_for_manual_layout_start": True,
        "candidate_evidence_written": False,
        "recommended_start_commands": [
            "cd labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench",
            "magic -dnull -noconsole",
            "xschem --rcfile xschemrc.local",
            "./run-layout-env-check.sh",
        ],
        "claim_boundary": {
            "allowed": "writes local Sky130 environment files for beginning converter layout work",
            "not_allowed": "does not draw converter cells, does not run DRC/LVS/extraction, does not write candidate evidence, and does not create accepted post-layout evidence",
        },
    }


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# Analog Converter Sky130 Workbench Environment",
        "",
        f"- status: `{report['status']}`",
        f"- workbench: `{report['workbench']}`",
        f"- environment file count: `{report['env_file_count']}`",
        f"- all PDK files present: `{report['all_pdk_files_present']}`",
        f"- physical converter cell count: `{report['physical_converter_cell_count']}`",
        f"- ready for manual layout start: `{report['ready_for_manual_layout_start']}`",
        f"- candidate evidence written: `{report['candidate_evidence_written']}`",
        "",
        "## First Principle",
        "",
        "The PDK tells the tools how to read process-specific shapes. The environment files put that knowledge next to the converter workbench, so a layout session starts from the same process, same model files, and same corner every time.",
        "",
        "This still does not create the converter. It only removes setup ambiguity before the manual or imported physical-cell step.",
        "",
        "## Environment Files",
        "",
    ]
    lines.extend(f"- `{item['path']}` ({item['bytes']} bytes)" for item in report["env_files"])
    lines.extend(["", "## PDK Files", ""])
    lines.extend(f"- {item['name']}: `{item['path']}` exists `{item['exists']}` bytes `{item['bytes']}`" for item in report["pdk_files"])
    lines.extend(["", "## Start Commands", ""])
    lines.extend(f"- `{command}`" for command in report["recommended_start_commands"])
    lines.extend(["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print("analog_converter_sky130_workbench_env")
    print(f"status,{report['status']}")
    print(f"workbench,{report['workbench']}")
    print(f"env_file_count,{report['env_file_count']}")
    print(f"all_pdk_files_present,{report['all_pdk_files_present']}")
    print(f"physical_converter_cell_count,{report['physical_converter_cell_count']}")
    print(f"candidate_evidence_written,{report['candidate_evidence_written']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
