#!/usr/bin/env python3
"""Run full-cell Magic DRC and record rule regions rather than a selected-box count."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

from build_active_converter_macro_candidate import WORKBENCH


def parse_full_cell_drc(stdout):
    rules = [{"rule":m.group(1),"regions":int(m.group(2))}
             for m in re.finditer(r"^DRC_RULE\t([^\n]+)\t(\d+)\s*$",stdout,re.MULTILINE)]
    tiles = [int(n) for n in re.findall(r"has (\d+) error tiles",stdout)]
    complete = "DRC_AUDIT_COMPLETE" in stdout
    return {"completed":complete,"error_tiles":max(tiles) if tiles else None,
            "rule_regions":rules,"rule_region_count":sum(r["regions"] for r in rules),
            "drc_pass":complete and not rules and not any(tiles)}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    output=args.output.resolve();output.mkdir(parents=True,exist_ok=False)
    sources={}
    for p in args.source.glob("*.mag"):
        if p.stem.endswith("_flat"): continue
        shutil.copy2(p,output/p.name)
        sources[str(p.resolve())]=hashlib.sha256(p.read_bytes()).hexdigest()
    if not (output/'aimc_converter_macro_active_candidate.mag').is_file():
        raise ValueError("expected top layout missing; refusing to audit an empty cell")
    for copied in output.glob('*.mag'):
        for cell in re.findall(r'^use\s+(\S+)',copied.read_text(),re.MULTILINE):
            if not (output/(cell+'.mag')).is_file():
                raise ValueError(f"referenced child layout missing: {cell}")
    tcl=output/'audit.tcl'
    tcl.write_text('''drc on
load aimc_converter_macro_active_candidate -force
select top cell
flatten aimc_converter_macro_active_candidate_flat
load aimc_converter_macro_active_candidate_flat -force
select top cell
drc check
drc catchup
foreach {why boxes} [drc listall why] {puts "DRC_RULE\t$why\t[llength $boxes]"}
puts DRC_AUDIT_COMPLETE
quit -noprompt
''')
    proc=subprocess.run(['/home/mehtama1/eda-tools/magic-8.3.682/bin/magic','-dnull','-noconsole',
                         '-rcfile',str(WORKBENCH/'.magicrc'),str(tcl)],cwd=output,text=True,capture_output=True,
                        timeout=120,env={**os.environ,'PDK_ROOT':'/home/mehtama1/eda-tools/pdks'})
    (output/'stdout.log').write_text(proc.stdout);(output/'stderr.log').write_text(proc.stderr)
    result={**parse_full_cell_drc(proc.stdout),'source_layout_sha256':sources,'returncode':proc.returncode,
            'scope':'full flattened cell after DRC queue completion; not LVS, electrical validation or signoff',
            'runner_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    result['drc_pass'] = result['drc_pass'] and proc.returncode == 0
    (output/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    shutil.copy2(Path(__file__),output/'source_snapshot.py')
    print(json.dumps({k:v for k,v in result.items() if k not in ('source_layout_sha256','rule_regions')},indent=2))
    if not result['completed']: raise SystemExit(1)


if __name__ == '__main__': main()
