#!/usr/bin/env python3
"""Compare the active macro against the existing independent latch schematic plus preamp."""

import argparse
import hashlib
import json
import re
from pathlib import Path
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--netlist',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--preamp-fingers',type=int,default=1)
    parser.add_argument('--cell',default=None,
                        help='Top-level extracted/reference cell name; defaults to the first subcircuit.')
    parser.add_argument('--preamp-length',type=float,default=0.6)
    args=parser.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    if args.preamp_fingers < 1:
        raise SystemExit('--preamp-fingers must be positive')
    if args.preamp_length <= 0:
        raise SystemExit('--preamp-length must be positive')
    ref=ROOT/'labs/analog/analog-in-memory-foundation-model-hardware/spice/sky130_isolated_latch_v2_reference.spice'
    shutil.copy2(args.netlist,out/'extracted.spice');shutil.copy2(ref,out/'latch_reference.spice')
    lines=args.netlist.read_text().splitlines()
    cell = args.cell or next((match.group(1) for line in lines
                              for match in [re.match(r"\.subckt\s+(\S+)", line)]
                              if match), None)
    if not cell:
        raise SystemExit('could not identify extracted top-level subcircuit')
    retained=[line for line in lines if not line.lstrip().lower().startswith('c')]
    (out/'devices.spice').write_text('\n'.join(retained)+'\n')
    reference=f'''* Intended active macro: existing independent latch circuit and added differential pair.
.include latch_reference.spice
.subckt {cell} vss vdd row_drive sar_comparator_input
+ decision_p decision_n reset eval vss_escape latch_sense_p_ext latch_sense_n_ext
+ iso_tail_ext tail_ext vdd_ext preamp_iso_tail_ext
Xcore decision_p decision_n latch_sense_p_ext latch_sense_n_ext tail_ext reset
+ vdd_ext vss_escape eval row_drive sar_comparator_input iso_tail_ext vdd_ext
+ sky130_isolated_frontend_active_load_latch_v2
{chr(10).join(f'Xpreamp_p_{index} latch_sense_p_ext row_drive preamp_iso_tail_ext vss_escape sky130_fd_pr__nfet_01v8 w=1.2 l={args.preamp_length:g}' for index in range(args.preamp_fingers))}
{chr(10).join(f'Xpreamp_n_{index} latch_sense_n_ext sar_comparator_input preamp_iso_tail_ext vss_escape sky130_fd_pr__nfet_01v8 w=1.2 l={args.preamp_length:g}' for index in range(args.preamp_fingers))}
.ends {cell}
'''
    (out/'macro_reference.spice').write_text(reference)
    setup=Path('/home/mehtama1/eda-tools/pdks/sky130A/libs.tech/netgen/sky130A_setup.tcl')
    command=['/home/mehtama1/eda-tools/netgen-1.5/bin/netgen','-batch','lvs',
             f'{out / "devices.spice"} {cell}',f'{out / "macro_reference.spice"} {cell}',str(setup),str(out/'netgen.log')]
    proc=subprocess.run(command,cwd=out,capture_output=True,text=True,timeout=90)
    (out/'stdout.log').write_text(proc.stdout);(out/'stderr.log').write_text(proc.stderr)
    log=(out/'netgen.log').read_text() if (out/'netgen.log').exists() else ''
    passed=proc.returncode==0 and 'Final result: Circuits match uniquely.' in log and 'Property errors were found' not in log
    report={'status':'active_transistor_macro_lvs_pass' if passed else 'active_transistor_macro_lvs_failed',
            'matched_uniquely':passed,'returncode':proc.returncode,'command':command,
            'parasitic_capacitors_excluded':len(lines)-len(retained),'extracted_netlist_sha256':hashlib.sha256(args.netlist.read_bytes()).hexdigest(),
            'latch_reference_sha256':hashlib.sha256(ref.read_bytes()).hexdigest(),
            'setup_sha256':hashlib.sha256(setup.read_bytes()).hexdigest(),'accepted_converter':False,
            'preamp_fingers':args.preamp_fingers,'preamp_length':args.preamp_length,'cell':cell,
            'claim_boundary':'Active transistor connectivity/dimensions versus intended schematic; parasitic capacitors excluded without editing MOS lines. Starter DAC/SAR/mux regions have no functional devices. Not complete converter LVS or electrical qualification.'}
    (out/'result.json').write_text(json.dumps(report,indent=2)+'\n');shutil.copy2(Path(__file__),out/'source_snapshot.py')
    print(json.dumps(report,indent=2))
    if not passed:raise SystemExit(1)


if __name__=='__main__':main()
