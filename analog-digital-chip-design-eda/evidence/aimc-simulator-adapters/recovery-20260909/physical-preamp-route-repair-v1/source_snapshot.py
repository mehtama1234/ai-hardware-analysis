#!/usr/bin/env python3
"""Repair contacts and route gaps in an isolated copy of the converter layout."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

from audit_extracted_converter_boundary import audit
from build_active_converter_macro_candidate import tcl_text, parse_drc, WORKBENCH


def add_rectangles(text, layer, rectangles):
    geometry = "\n".join("rect " + " ".join(map(str, rect)) for rect in rectangles)
    marker = f"<< {layer} >>"
    if marker in text:
        return text.replace(marker, marker + "\n" + geometry, 1)
    return text.replace("<< labels >>", marker + "\n" + geometry + "\n<< labels >>", 1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    sources = {}
    for path in args.source.glob("*.mag"):
        if path.stem.endswith("_flat"):
            continue
        shutil.copy2(path, output / path.name)
        sources[str(path.resolve())] = hashlib.sha256(path.read_bytes()).hexdigest()
    child = output / "sky130_transistor_active_isolation_pair.mag"
    text = child.read_text()
    contacts = [(560,330,620,390),(1780,330,1840,390)]
    for layer in ("pc", "locali", "mcon", "metal1", "via1"):
        text = add_rectangles(text, layer, contacts)
    text = add_rectangles(text, "metal2", [(560,250,620,390),(1780,250,1840,390)])
    child.write_text(text)
    top = output / "aimc_converter_macro_active_candidate.mag"
    text = top.read_text()
    drains = [(32770,670,32830,730),(33570,670,33630,730)]
    for layer in ("via1","metal2","via2","metal3","via3"):
        text = add_rectangles(text, layer, drains)
    text = add_rectangles(text,"metal4",[(32770,670,32830,1830),(33570,670,33630,2230),
                                        (3970,900,4030,1030),(15970,970,16030,1100)])
    top.write_text(text)
    netlist = output / "aimc_converter_macro_active_candidate_extracted.spice"
    tcl = output / "extract.tcl"
    tcl.write_text(tcl_text(netlist.name, output, True))
    proc = subprocess.run(["/home/mehtama1/eda-tools/magic-8.3.682/bin/magic", "-dnull", "-noconsole",
                           "-rcfile", str(WORKBENCH / ".magicrc"), str(tcl)], cwd=output,
                          text=True,capture_output=True,timeout=120)
    (output/"magic.stdout.log").write_text(proc.stdout)
    (output/"magic.stderr.log").write_text(proc.stderr)
    boundary = audit(netlist.read_text()) if netlist.exists() else None
    report = {"schema_version":"physical_preamp_connection_repair.v1", "source_layout_sha256":sources,
              "magic_returncode":proc.returncode,"drc_count":parse_drc(proc.stdout),"boundary_audit":boundary,
              "netlist":str(netlist),"netlist_sha256":hashlib.sha256(netlist.read_bytes()).hexdigest() if netlist.exists() else None,
              "generated_layout_sha256":{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in output.glob("*.mag")},
              "runner_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "changes":["add missing poly-to-metal gate contacts", "connect preamp drain metal1 to metal4",
                         "bridge route gaps at latch sense ports"],
              "accepted_converter":False,
              "claim_boundary":"Actual layout edit and fresh extraction; not full converter LVS, transfer, robustness or silicon qualification."}
    (output/"repair_result.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))


if __name__ == "__main__":
    main()
