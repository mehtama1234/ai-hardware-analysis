#!/usr/bin/env python3
"""Independently verify the register-peripheral RTL2GDS handoff."""
from __future__ import annotations
import argparse,json
from pathlib import Path

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument("handoff",type=Path); args=parser.parse_args(); report=json.loads(args.handoff.read_text(encoding="utf-8")); errors=[]
    if report.get("schema_version")!="register-peripheral-model-repair-rtl2gds-handoff-v1" or report.get("status")!="passed": errors.append("handoff is not a passed register package")
    if report.get("model",{}).get("repair_match") is not True or report.get("model",{}).get("grounded") is not True: errors.append("model repair is not accepted")
    retest=report.get("repair_retest",{}); 
    if retest.get("status")!="passed" or retest.get("model_generated") is not True or retest.get("original_unchanged") is not True: errors.append("repair retest is incomplete")
    formal=report.get("formal",{}); 
    if formal.get("status")!="passed" or formal.get("proof")!="proven" or formal.get("property_count",0)<3 or not all(item.get("passed") is True for item in formal.get("property_runs",[])): errors.append("formal property suite is incomplete")
    physical=report.get("physical",{}); 
    if physical.get("flow_status")!="flow completed" or physical.get("source_match") is not True or physical.get("lvs_errors")!=0 or physical.get("gds_present") is not True or physical.get("xor_report") is not True: errors.append("physical evidence is incomplete")
    if errors:
        for error in errors: print(f"ERROR: {error}")
        return 1
    print(json.dumps({"status":"passed","design":report.get("design"),"formal_properties":formal.get("property_count"),"lvs_errors":0,"source_match":True},sort_keys=True)); return 0

if __name__=="__main__": raise SystemExit(main())
