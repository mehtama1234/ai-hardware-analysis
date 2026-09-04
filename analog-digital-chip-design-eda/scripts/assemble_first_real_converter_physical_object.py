#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LAB_EXTRACTED = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware" / "layout-workbench" / "extracted"
CANDIDATE = ROOT / "evidence" / "aimc-simulator-adapters" / "candidate-post-layout"
NETLIST = CANDIDATE / "netlist" / "aimc_readout_candidate_001_extracted.spice"
MANIFEST = CANDIDATE / "netlist" / "aimc_readout_candidate_001_manifest.json"
REPORT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "first-real-converter-physical-object-assembly.json"
REPORT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "first-real-converter-physical-object-assembly.md"

SOURCES = [
    LAB_EXTRACTED / "row_dac_10b_layout_smoke.spice",
    LAB_EXTRACTED / "sar_readout_12b_layout_smoke.spice",
    LAB_EXTRACTED / "shared_converter_mux_layout_smoke.spice",
    LAB_EXTRACTED / "aimc_converter_macro_layout_smoke.spice",
]


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def source_text(path: Path) -> str:
    if not path.exists():
        raise SystemExit(f"missing source extraction: {path}")
    return path.read_text(encoding="utf-8")


def assemble() -> dict[str, object]:
    NETLIST.parent.mkdir(parents=True, exist_ok=True)
    created_at = datetime.now(timezone.utc).isoformat()
    chunks = [
        "* First real converter candidate physical object.",
        "* Assembled from local Sky130 Magic ext2spice starter cells.",
        "* This is a B1 physical-object artifact, not accepted converter evidence.",
        "* Required parts named in this file: row_dac, sar_readout, shared_mux, references, sample_path.",
        "",
    ]
    for source in SOURCES:
        chunks.extend([
            f"* begin source: {rel(source)}",
            source_text(source).strip(),
            f"* end source: {rel(source)}",
            "",
        ])
    chunks.extend([
        ".subckt aimc_readout_candidate_001 vss vdd row_drive column_sense digital_code_out sample_clock vrefp vrefn",
        "* row_dac: extracted starter row DAC cell drives the row voltage.",
        "Xdac vss row_drive vdd row_dac_10b",
        "* shared_mux: extracted starter shared mux cell loads the column bus.",
        "Xmux vss column_sense vdd shared_converter_mux",
        "* sar_readout: extracted starter sampled readout cell observes the muxed sense node.",
        "Xsar vss column_sense vdd sar_readout_12b",
        "* sample_path: starter macro parasitic object ties row drive, column sense, output, and sample clock.",
        "Xmacro vss vdd row_drive column_sense digital_code_out sample_clock aimc_converter_macro",
        "* references: vrefp and vrefn are explicit candidate reference pins for later ADC/DAC decks.",
        "Crefp vrefp vss 1f",
        "Crefn vrefn vss 1f",
        ".ends aimc_readout_candidate_001",
        "",
    ])
    NETLIST.write_text("\n".join(chunks), encoding="utf-8")
    manifest = {
        "result_type": "first_real_converter_physical_object_manifest",
        "created_at": created_at,
        "candidate_id": "aimc_readout_candidate_001",
        "status": "b1_physical_object_assembled_from_starter_extractions_not_accepted_evidence",
        "netlist": rel(NETLIST),
        "sources": [rel(path) for path in SOURCES],
        "included_parts": ["row_dac", "sar_readout", "shared_mux", "references", "sample_path"],
        "claim_boundary": {
            "allowed": "provides one named extracted starter converter object for the B1 physical-object blocker",
            "not_allowed": "does not prove energy, latency, noise, area, break-even replacement, or accepted post-layout converter evidence",
        },
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def write_report(manifest: dict[str, object]) -> None:
    report = {
        "result_type": "first_real_converter_physical_object_assembly",
        "created_at": manifest["created_at"],
        "status": manifest["status"],
        "candidate_id": manifest["candidate_id"],
        "netlist": manifest["netlist"],
        "manifest": rel(MANIFEST),
        "sources": manifest["sources"],
        "included_parts": manifest["included_parts"],
        "claim_boundary": manifest["claim_boundary"],
    }
    REPORT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# First Real Converter Physical Object Assembly",
        "",
        f"- status: `{report['status']}`",
        f"- candidate id: `{report['candidate_id']}`",
        f"- netlist: `{report['netlist']}`",
        f"- manifest: `{report['manifest']}`",
        "",
        "## First Principle",
        "",
        "The first converter blocker asks for one object. A number such as energy or noise only has meaning if it belongs to a named circuit. This assembly creates that named circuit from the local extracted starter cells.",
        "",
        "The result is still narrow. It closes the object-name problem, not the measurement problem. The next blockers must still measure energy, latency, noise, and area on this same object.",
        "",
        "## Source Extractions",
        "",
    ]
    lines.extend(f"- `{path}`" for path in report["sources"])
    lines.extend([
        "",
        "## Included Parts",
        "",
    ])
    lines.extend(f"- `{part}`" for part in report["included_parts"])
    lines.extend([
        "",
        "## Refused Claim",
        "",
        report["claim_boundary"]["not_allowed"],
        "",
    ])
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    manifest = assemble()
    write_report(manifest)
    print("first_real_converter_physical_object_assembly")
    print(f"status,{manifest['status']}")
    print(f"netlist,{NETLIST}")
    print(f"manifest,{MANIFEST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
