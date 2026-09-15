"""Build independently runnable research frontends from local evidence snapshots."""
from pathlib import Path
import json, hashlib, os, re
from html import escape
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
INF=ROOT/'analog-in-memory-ai-inference'
EDA=ROOT/'analog-digital-chip-design-eda'
DEC=INF/'software-architecture/experiments/gpt2-hybrid-v1/decisions/20260909-finite-reference-holdout'
def read(p): return json.loads(p.read_text())
def title(p):
 m=re.search(r'<title>(.*?)</title>',p.read_text(errors='replace'),re.S)
 return re.sub(r'\s+',' ',m.group(1)) if m else p.stem.replace('-',' ').title()
for kind,base,folder,brand,pages in [
 ('inference',INF,'studio','Inference Studio',[('index','Overview'),('workload','Model & workload'),('mapping','Tile mapping'),('calibration','Calibration & quality'),('runtime','Execution decision'),('evidence','Evidence library')]),
 ('silicon',EDA,'workbench','Silicon Workbench',[('index','Overview'),('converter','Converter qualification'),('verification','Physical verification'),('experiments','Experiment explorer'),('handoff','Hardware handoff'),('evidence','Evidence library')])]:
 out=base/folder;out.mkdir(exist_ok=True)
 files={'decision':DEC/'decision.json','quality':DEC/'quality.json','binding':DEC/'nominal_reference_binding.json','plan':DEC/'quality_plan.json','compiler':DEC/'compiler.json','physical':EDA/'evidence/aimc-simulator-adapters/converter-physical-repair-current.json'}
 if kind=='inference': files['qualification_matrix']=INF/'software-architecture/experiments/gpt2-hybrid-v1/qualification/matrix.json'
 if kind=='silicon': files['system']=EDA/'evidence/aimc-hardware-lab/current-aimc-system-state.json'
 data={key:read(path) for key,path in files.items()}
 data['sources']={key:{'href':os.path.relpath(path,out),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'file':path.name} for key,path in files.items()}
 docs=(INF/'software-architecture').glob('*.html') if kind=='inference' else (EDA/'site').glob('*.html')
 data['library']=[{'title':title(p),'href':os.path.relpath(p,out)} for p in sorted(docs)]
 if kind=='inference':
  qualification_readme=INF/'software-architecture/experiments/gpt2-hybrid-v1/qualification/README.md'
  data['library'].insert(0, {'title':'GPT-2 converter qualification matrix','href':os.path.relpath(qualification_readme,out)})
 data['links']={'original':'../index.html' if kind=='inference' else '../site/index.html','peer':'../../analog-digital-chip-design-eda/workbench/index.html' if kind=='inference' else '../../analog-in-memory-ai-inference/studio/index.html','deepseek':'../../../DeepSeek-From-Scratch/integration/index.html','workbench':'../software-architecture/index.html' if kind=='inference' else '../site/verification-workbench.html'}
 (out/'data.js').write_text('window.RESEARCH_DATA='+json.dumps(data,separators=(',',':'))+';\n')
 for asset in ['studio.css','studio.js']:(out/asset).write_text((HERE/asset).read_text())
 for page,label in pages:
  nav=''.join(f'<a href="{slug}.html" '+('aria-current="page"' if slug==page else '')+f'><span>{i:02d}</span>{escape(name)}</a>' for i,(slug,name) in enumerate(pages))
  (out/f'{page}.html').write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(label)} — {brand}</title><link rel="stylesheet" href="studio.css"><script defer src="data.js"></script><script defer src="studio.js"></script></head><body class="{kind}" data-page="{page}"><a class="skip" href="#main">Skip to content</a><aside class="sidebar"><a class="wordmark" href="index.html">{'ANALOG / AI' if kind=='inference' else 'SILICON / LAB'}<small>{brand}</small></a><div class="nav-caption">{'MODEL TO EXECUTION' if kind=='inference' else 'CIRCUIT TO QUALIFICATION'}</div><nav aria-label="Project navigation">{nav}</nav><div class="sidebar-foot"><span class="eyebrow">CONNECTED INVESTIGATION</span><a href="{data['links']['peer']}">{'Silicon Workbench' if kind=='inference' else 'Inference Studio'} ↗</a><a href="{data['links']['deepseek']}">DeepSeek model lab ↗</a><a href="{data['links']['original']}">Original research index ↗</a></div></aside><div class="workspace"><header class="topbar"><span>{brand} <span class="slash">/</span> {escape(label)}</span><span class="snapshot">SAVED EVIDENCE · 2026-09-09</span></header><main id="main" tabindex="-1"></main><footer><span>Research evidence · numerical, simulated, and physical claims stay separate.</span><a href="evidence.html">Inspect the sources ↗</a></footer></div><noscript><p>Enable JavaScript to explore the evidence, or <a href="{data['links']['original']}">open the research index</a>.</p></noscript></body></html>''')
 print(f'Built {brand}: {len(pages)} pages, {len(data["library"])} research links')
