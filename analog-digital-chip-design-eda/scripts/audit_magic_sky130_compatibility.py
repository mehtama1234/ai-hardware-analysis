#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SYSTEM_MAGIC = Path(shutil.which("magic") or "/usr/bin/magic")
LOCAL_MAGIC = Path.home() / "eda-tools" / "magic" / "bin" / "magic"
INSTALL_SCRIPT = ROOT / "scripts" / "install_local_magic_from_source.sh"
SMOKE_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "magic-sky130-extraction-smoke.json"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "magic-sky130-compatibility.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "magic-sky130-compatibility.md"


def version(path: Path) -> str:
    if not path.is_file():
        return "missing"
    proc = subprocess.run([str(path), "--version"], text=True, capture_output=True, check=False)
    return (proc.stdout or proc.stderr).strip() or f"returncode {proc.returncode}"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def build_report() -> dict[str, Any]:
    smoke = load_json(SMOKE_JSON)
    local_present = LOCAL_MAGIC.is_file()
    smoke_passed = smoke.get("passed") is True
    if smoke_passed:
        status = "magic_sky130_extraction_path_ready_not_converter_evidence"
        observed_blocker = "The local Magic binary is installed and the tiny Sky130 extraction smoke passes. The remaining blocker is the absence of real converter layout cells and extracted converter artifacts."
    elif local_present:
        status = "local_magic_installed_sky130_smoke_not_passing"
        observed_blocker = "The local Magic binary is installed, but the tiny Sky130 extraction smoke is not passing yet. Converter extraction should wait until this tool path is clean."
    else:
        status = "local_magic_upgrade_needed_for_sky130_extraction"
        observed_blocker = "Ubuntu package provides Magic 8.3.105; the Sky130 extraction smoke currently fails while loading/parsing the Sky130 tech extraction section."
    return {
        "result_type": "magic_sky130_compatibility",
        "status": status,
        "system_magic": str(SYSTEM_MAGIC),
        "system_magic_version": version(SYSTEM_MAGIC),
        "local_magic": str(LOCAL_MAGIC),
        "local_magic_present": local_present,
        "local_magic_version": version(LOCAL_MAGIC),
        "install_script": rel(INSTALL_SCRIPT),
        "install_command": "MAGIC_PREFIX=$HOME/eda-tools/magic MAGIC_SRC=$HOME/eda-tools/magic-src ./scripts/install_local_magic_from_source.sh",
        "smoke_status": smoke.get("status", "missing"),
        "smoke_passed": smoke.get("passed"),
        "smoke_returncode": (smoke.get("run") or {}).get("returncode") if isinstance(smoke.get("run"), dict) else None,
        "smoke_magic_binary": (smoke.get("run") or {}).get("magic_binary") if isinstance(smoke.get("run"), dict) else "missing",
        "observed_blocker": observed_blocker,
        "claim_boundary": {
            "allowed": "records whether the local Magic/Sky130 extraction path is compatible enough to attempt converter extraction",
            "not_allowed": "does not install tools by itself, does not create converter layout, and does not write post-layout evidence",
        },
    }


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# Magic Sky130 Compatibility",
        "",
        f"- status: `{report['status']}`",
        f"- system Magic: `{report['system_magic']}`",
        f"- system Magic version: `{report['system_magic_version']}`",
        f"- local Magic: `{report['local_magic']}`",
        f"- local Magic present: `{report['local_magic_present']}`",
        f"- local Magic version: `{report['local_magic_version']}`",
        f"- smoke status: `{report['smoke_status']}`",
        f"- smoke passed: `{report['smoke_passed']}`",
        f"- smoke return code: `{report['smoke_returncode']}`",
        f"- smoke Magic binary: `{report['smoke_magic_binary']}`",
        "",
        "## First Principle",
        "",
        "Extraction is a contract between the layout tool and the process file. If the tool cannot read the process extraction rules, it cannot turn shapes into circuit equations.",
        "",
        "The converter cells are still missing, but this is a separate blocker: even a tiny non-converter extraction smoke currently fails with the installed Magic binary.",
        "",
        "## Upgrade Command",
        "",
        f"`{report['install_command']}`",
        "",
        "## Observed Blocker",
        "",
        report["observed_blocker"],
        "",
        "## Refused Claim",
        "",
        report["claim_boundary"]["not_allowed"],
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print("magic_sky130_compatibility")
    print(f"status,{report['status']}")
    print(f"system_magic_version,{report['system_magic_version']}")
    print(f"local_magic_present,{report['local_magic_present']}")
    print(f"smoke_passed,{report['smoke_passed']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
