#!/usr/bin/env python3
"""Compare solver refinements without calling peak agreement qualification."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil

ROOT=Path(__file__).resolve().parents[1]


def read_run(path):
    contract=json.loads((path/"contract.json").read_text())
    result=json.loads((path/"result.json").read_text())
    for name,digest in contract["sha256"].items():
        if hashlib.sha256((path/name).read_bytes()).hexdigest()!=digest:
            raise ValueError(f"Changed source artifact: {path/name}")
    if hashlib.sha256((path/"waveform.raw").read_bytes()).hexdigest()!=result["waveform_sha256"]:
        raise ValueError("Changed waveform")
    deck=(path/"deck.spice").read_text().replace(str(path),"RUN")
    # Only solver directives and isolated output location may differ.
    normalized=re.sub(r"(?m)^\.(options|tran) .*\n","",deck)
    return contract,result,normalized


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runs",type=Path,nargs="+")
    args=parser.parse_args()
    if len(args.runs)<2:
        parser.error("At least two runs required")
    paths=[p.resolve() for p in args.runs]
    loaded=[read_run(p) for p in paths]
    base_c,base_r,base_deck=loaded[0]
    for contract,result,deck in loaded[1:]:
        if deck!=base_deck or contract["sha256"]["circuit.spice"]!=base_c["sha256"]["circuit.spice"]:
            raise ValueError("Circuit/stimulus changed; not a solver-only comparison")
        if contract["model_file_sha256"]!=base_c["model_file_sha256"]:
            raise ValueError("Model provenance changed")
        if result["node_extrema_v"].keys()!=base_r["node_extrema_v"].keys():
            raise ValueError("Observables changed")
    rows=[]
    for path,(contract,result,_) in zip(paths,loaded):
        rows.append({"run":str(path),"solver":contract.get("solver","legacy: inspect exact deck"),
                     "status":result["status"],"strict_saved_node_envelope_pass":result["strict_saved_node_envelope_pass"],
                     "node_extrema_v":result["node_extrema_v"],
                     "extrema_delta_from_first_v":{k:[v[i]-base_r["node_extrema_v"][k][i] for i in (0,1)]
                                                  for k,v in result["node_extrema_v"].items()},
                     "source_sha256":{name:hashlib.sha256((path/name).read_bytes()).hexdigest()
                                      for name in ("contract.json","result.json","waveform.raw")}})
    out=ROOT/"evidence/aimc-simulator-adapters/capture-solver-comparison"/datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    out.mkdir(parents=True,exist_ok=False)
    shutil.copy2(__file__,out/"comparator.py")
    (out/"result.json").write_text(json.dumps({"status":"solver_comparison_only","accepted_converter":False,
        "runs":rows,"boundary":"Observed sampled extrema differences only; no convergence tolerance or qualification inferred."},indent=2)+"\n")
    print(out)


if __name__=="__main__":
    main()
