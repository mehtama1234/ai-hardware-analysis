#!/usr/bin/env python3
"""Extract an existing rebuilt macro without editing its layout or netlist."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

from build_active_converter_macro_candidate import WORKBENCH,tcl_text
from audit_extracted_converter_boundary import audit


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate-dir',type=Path,required=True)
    args=parser.parse_args();p=args.candidate_dir.resolve()
    if not (p/'aimc_converter_macro_active_candidate.mag').exists():
        raise ValueError('top layout missing')
    net=p/'aimc_converter_macro_active_candidate_extracted.spice'
    if net.exists(): raise ValueError('netlist already exists; preserve it and use a new candidate directory')
    tcl=p/'extract.tcl';tcl.write_text(tcl_text(net.name,p,True))
    result=subprocess.run(['/home/mehtama1/eda-tools/magic-8.3.682/bin/magic','-dnull','-noconsole',
                           '-rcfile',str(WORKBENCH/'.magicrc'),str(tcl)],cwd=p,capture_output=True,text=True,
                          timeout=120,env={**os.environ,'PDK_ROOT':'/home/mehtama1/eda-tools/pdks'})
    (p/'extraction.stdout.log').write_text(result.stdout);(p/'extraction.stderr.log').write_text(result.stderr)
    if result.returncode or not net.exists(): raise RuntimeError('extraction failed; inspect logs')
    report={**audit(net.read_text()),'netlist':str(net),'netlist_sha256':hashlib.sha256(net.read_bytes()).hexdigest()}
    (p/'extraction_audit.json').write_text(json.dumps(report,indent=2)+'\n')
    shutil.copy2(Path(__file__),p/'extraction_source_snapshot.py')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
