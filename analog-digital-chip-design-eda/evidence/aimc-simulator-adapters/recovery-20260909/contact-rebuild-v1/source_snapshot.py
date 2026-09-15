#!/usr/bin/env python3
"""Apply explicit SKY130 contact enclosures to a new copy of the macro cells.

Dimensions are in the saved cells' 0.01 um coordinate grid. Full-cell DRC and
extracted connectivity must validate the output; this is not automatic signoff.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil


def rebuild(text, top=False):
    layers={}
    layer=None
    for line in text.splitlines():
        match=re.fullmatch(r'<< (.+) >>',line)
        if match: layer=match.group(1)
        elif line.startswith('rect '):
            layers.setdefault(layer,[]).append(tuple(map(int,line.split()[1:])))
    additions={}
    def expand(target,rect,margin):
        x1,y1,x2,y2=rect
        additions.setdefault(target,set()).add((x1-margin,y1-margin,x2+margin,y2+margin))
    # Contact enclosure requirements from the installed full-cell DRC report.
    for contact,targets in {
        'pc': [('polysilicon',5),('locali',8)],
        'ndc':[('locali',8)], 'pdc':[('locali',8)],
        'mcon':[('metal1',3)], 'viali':[('metal1',3)],
        'psubdiffcont':[('psubdiff',12),('locali',8)],
        'nsubdiffcont':[('nsubdiff',12),('locali',8)],
        'via1':[('metal1',3),('metal2',3)],
        'via2':[('metal2',5),('metal3',3)],
        'via3':[('metal3',3),('metal4',1)],
    }.items():
        for rect in layers.get(contact,[]):
            for target,margin in targets: expand(target,rect,margin)
    if top:
        # via4 is a large contact. Replace undersized cuts and route M5 with
        # 1.6 um width and separated tracks instead of widening into a short.
        for x1,y1,x2,y2 in layers.get('via4',[]):
            x,y=(x1+x2)//2,(y1+y2)//2
            old=f'rect {x1} {y1} {x2} {y2}'
            # Restrict replacement to the via4 layer below.
            layers['via4'] = layers.get('via4',[])
            expand('metal4',(x-59,y-59,x+59,y+59),5)
            expand('metal5',(x-59,y-59,x+59,y+59),21)
        via4=[((r[0]+r[2])//2-59,(r[1]+r[3])//2-59,
               (r[0]+r[2])//2+59,(r[1]+r[3])//2+59) for r in layers.get('via4',[])]
        text=re.sub(r'<< via4 >>\n.*?(?=<<)', '<< via4 >>\n'+''.join('rect '+' '.join(map(str,r))+'\n' for r in via4),text,flags=re.S)
        m5=[(3920,520,4080,1080),(3920,520,32880,680),(32720,520,32880,780),
            (15920,920,16080,1590),(15920,1430,33680,1590),(33520,620,33680,1590)]
        text=re.sub(r'<< metal5 >>\n.*?(?=<<)', '<< metal5 >>\n'+''.join('rect '+' '.join(map(str,r))+'\n' for r in m5),text,flags=re.S)
    for target,rects in additions.items():
        content=''.join('rect '+' '.join(map(str,r))+'\n' for r in sorted(rects))
        marker=f'<< {target} >>\n'
        if marker in text: text=text.replace(marker,marker+content,1)
        else: text=text.replace('<< labels >>',marker+content+'<< labels >>',1)
    return text


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    sources={}
    for p in args.source.glob('*.mag'):
        if p.stem.endswith('_flat'):continue
        sources[str(p.resolve())]=hashlib.sha256(p.read_bytes()).hexdigest()
        (args.output/p.name).write_text(rebuild(p.read_text(),p.stem=='aimc_converter_macro_active_candidate'))
    (args.output/'rebuild_provenance.json').write_text(json.dumps({'source_layout_sha256':sources,
        'generated_layout_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in args.output.glob('*.mag')},
        'accepted_converter':False,'status':'new_contact_geometry_requires_drc_extraction_and_electrical_checks'},indent=2)+'\n')
    shutil.copy2(Path(__file__),args.output/'source_snapshot.py')
    print(args.output)


if __name__=='__main__':main()
