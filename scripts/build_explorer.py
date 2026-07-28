#!/usr/bin/env python3
"""Build a client-side searchable explorer for all analyzed AI-hardware papers.

Reads:  analysis/per-paper/<id>.json
        analysis/themes/deep/papers/<id>.json  (what_it_does, method_in_detail)
        analysis/themes/buckets/T*.jsonl        (theme assignments)
Writes: explorer.html
"""
import json, glob, html
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent
DEEP = ROOT / "analysis/themes/deep"
BUCK = ROOT / "analysis/themes/buckets"

THEME_LABELS = {
    "T1_attention":    "Serving models fast",
    "T2_quantization": "Smaller numbers",
    "T3_memory":       "Memory wall",
    "T4_interconnect": "Chip-to-chip",
    "T5_sparsity":     "Skipping work",
    "T6_compiler":     "Compilers & chips",
    "T7_security":     "Trust & attacks",
    "T8_reliability":  "Correctness",
    "T9_specialized":  "Beyond the GPU",
    "T0_other":        "Everything else",
}

THEME_SLUGS = {
    "T1_attention": "t1", "T2_quantization": "t2", "T3_memory": "t3",
    "T4_interconnect": "t4", "T5_sparsity": "t5", "T6_compiler": "t6",
    "T7_security": "t7", "T8_reliability": "t8", "T9_specialized": "t9",
    "T0_other": "t0",
}

def build_rows():
    # load theme assignments
    theme_of = {}
    for bf in glob.glob(str(BUCK / "T*.jsonl")):
        key = Path(bf).stem
        for l in open(bf):
            theme_of[json.loads(l)["id"]] = key

    rows = []
    for f in sorted(glob.glob(str(ROOT / "analysis/per-paper/*.json"))):
        p = json.loads(open(f).read())
        pid = p["id"]
        theme = theme_of.get(pid, "T0_other")

        # deep writeup
        dp_f = DEEP / "papers" / f"{pid}.json"
        dp = json.loads(dp_f.read_text()) if dp_f.exists() else {}

        # normalize venue
        raw_venue = (p.get("venue") or "").strip()
        venue = raw_venue.split()[0].upper() if raw_venue else pid.split("-")[0].upper()
        if venue == "MLSYS":
            venue = "MLSys"

        rows.append({
            "id": pid,
            "title": p.get("title", ""),
            "venue": venue,
            "conf": p.get("confidence", "low"),
            "theme": theme,
            "theme_label": THEME_LABELS.get(theme, theme),
            "theme_slug": THEME_SLUGS.get(theme, "t0"),
            "problem": p.get("problem", ""),
            "method": p.get("method", ""),
            "tags": p.get("tags", []),
            "technique": p.get("technique_category", []),
            "hw": p.get("hardware_target", []),
            "what": dp.get("what_it_does", ""),
            "detail": dp.get("method_in_detail", ""),
        })

    rows.sort(key=lambda r: (r["venue"], r["id"]))
    return rows


def render(rows):
    data_json = json.dumps(rows, ensure_ascii=False)

    venue_counts = defaultdict(int)
    theme_counts = defaultdict(int)
    for r in rows:
        venue_counts[r["venue"]] += 1
        theme_counts[r["theme"]] += 1

    venue_opts = "".join(
        f'<option value="{v}">{v} ({c})</option>'
        for v, c in sorted(venue_counts.items()))
    theme_opts = "".join(
        f'<option value="{k}">{THEME_LABELS[k]} ({theme_counts[k]})</option>'
        for k in THEME_LABELS if k in theme_counts)

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AI Hardware 2025 · Explorer</title>
<style>
:root{{
  --g0:#0f1218;--g1:#14171d;--g2:#1a1f28;--g3:#222834;
  --line:#2b323d;--line2:#20262f;
  --ink:#e8e4dc;--ink2:#b0b8c4;--ink3:#737d8a;
  --teal:#3fbfb0;--orange:#e09050;--red:#d95a4a;
  --serif:Palatino,"Palatino Linotype",Charter,Georgia,serif;
  --mono:ui-monospace,"SF Mono",Menlo,Consolas,monospace;
  --sans:system-ui,-apple-system,"Segoe UI",sans-serif;
}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--g0);color:var(--ink);font-family:var(--sans);font-size:15px;line-height:1.6;-webkit-font-smoothing:antialiased}}
/* layout */
.shell{{display:grid;grid-template-rows:auto 1fr;height:100vh}}
.topbar{{background:var(--g1);border-bottom:1px solid var(--line);padding:14px 20px;display:flex;align-items:center;gap:16px;flex-wrap:wrap}}
.topbar h1{{font-family:var(--serif);font-size:1.25rem;font-weight:600;color:var(--ink);white-space:nowrap}}
.topbar .count{{font-family:var(--mono);font-size:.72rem;color:var(--ink3);white-space:nowrap}}
.main{{display:grid;grid-template-columns:220px 1fr;min-height:0}}
/* sidebar */
.sidebar{{background:var(--g2);border-right:1px solid var(--line2);padding:16px;overflow-y:auto;display:flex;flex-direction:column;gap:18px}}
.sb-sect label{{font-family:var(--mono);font-size:.65rem;letter-spacing:.18em;text-transform:uppercase;color:var(--ink3);display:block;margin-bottom:8px}}
.sb-sect select{{width:100%;background:var(--g3);border:1px solid var(--line);border-radius:6px;color:var(--ink2);font-family:var(--sans);font-size:.82rem;padding:6px 8px;appearance:none;cursor:pointer}}
.sb-sect select:focus{{outline:2px solid var(--teal);outline-offset:1px}}
.chip-group{{display:flex;flex-direction:column;gap:5px}}
.chip{{display:flex;align-items:center;gap:7px;cursor:pointer;padding:4px 6px;border-radius:5px;font-size:.8rem;color:var(--ink2);user-select:none}}
.chip:hover{{background:var(--g3)}}
.chip input{{accent-color:var(--teal);cursor:pointer}}
.chip.active{{color:var(--ink)}}
/* search */
.search-wrap{{flex:1;min-width:180px;max-width:340px}}
#search{{width:100%;background:var(--g2);border:1px solid var(--line);border-radius:7px;color:var(--ink);font-family:var(--sans);font-size:.9rem;padding:7px 12px}}
#search::placeholder{{color:var(--ink3)}}
#search:focus{{outline:2px solid var(--teal);outline-offset:1px}}
/* list */
.list-wrap{{overflow-y:auto;padding:0 0 40px}}
.list{{}}
.row{{border-bottom:1px solid var(--line2);padding:16px 20px;cursor:pointer;transition:background .12s}}
.row:hover{{background:var(--g2)}}
.row.open{{background:var(--g2)}}
.row-head{{display:flex;align-items:baseline;gap:8px;flex-wrap:wrap;margin-bottom:5px}}
.badge{{font-family:var(--mono);font-size:.6rem;letter-spacing:.06em;text-transform:uppercase;padding:2px 7px;border-radius:4px;white-space:nowrap}}
.bv{{background:#1d2a38;color:#6ab0d4;border:1px solid #2a4257}}
.bt{{background:#1a2820;color:var(--teal);border:1px solid #213d33}}
.bc-hi{{background:#1a2820;color:var(--teal);border:1px solid #1f3d2d}}
.bc-lo{{background:var(--g3);color:var(--ink3);border:1px solid var(--line)}}
.row h3{{font-size:.97rem;color:var(--ink);font-weight:500;line-height:1.35;text-wrap:balance}}
.what{{font-size:.85rem;color:var(--ink2);margin-top:7px;line-height:1.55}}
.detail-box{{margin-top:12px;background:var(--g3);border:1px solid var(--line2);border-radius:8px;padding:14px 16px}}
.detail-box .lab{{font-family:var(--mono);font-size:.6rem;letter-spacing:.14em;text-transform:uppercase;color:var(--ink3);margin-bottom:7px}}
.detail-box p{{font-size:.83rem;color:var(--ink2);margin-bottom:.7em;line-height:1.58}}
.detail-box p:last-child{{margin:0}}
.detail-box p b{{color:var(--ink)}}
.deeplink{{font-family:var(--mono);font-size:.68rem;color:var(--teal);text-decoration:none;margin-top:10px;display:inline-block}}
.deeplink:hover{{text-decoration:underline}}
.empty{{padding:60px 20px;text-align:center;color:var(--ink3);font-family:var(--mono);font-size:.8rem}}
/* scrollbars */
::-webkit-scrollbar{{width:6px;height:6px}}
::-webkit-scrollbar-track{{background:transparent}}
::-webkit-scrollbar-thumb{{background:var(--line);border-radius:3px}}
@media(max-width:640px){{
  .main{{grid-template-columns:1fr}}
  .sidebar{{border-right:none;border-bottom:1px solid var(--line2);max-height:none}}
}}
</style>
</head>
<body>
<div class="shell">
  <div class="topbar">
    <h1>AI Hardware 2025</h1>
    <div class="search-wrap"><input id="search" type="search" placeholder="Search title, method, tag…" autocomplete="off"></div>
    <div class="count" id="showing">{len(rows)} papers</div>
  </div>
  <div class="main">
    <div class="sidebar">
      <div class="sb-sect">
        <label>Venue</label>
        <select id="fVenue">
          <option value="">All venues</option>
          {venue_opts}
        </select>
      </div>
      <div class="sb-sect">
        <label>Theme</label>
        <select id="fTheme">
          <option value="">All themes</option>
          {theme_opts}
        </select>
      </div>
      <div class="sb-sect">
        <label>Coverage</label>
        <div class="chip-group">
          <label class="chip"><input type="checkbox" id="fHi" checked> Full text read</label>
          <label class="chip"><input type="checkbox" id="fLo" checked> Abstract only</label>
        </div>
      </div>
    </div>
    <div class="list-wrap">
      <div class="list" id="list"></div>
      <div class="empty" id="empty" style="display:none">No papers match — try clearing a filter.</div>
    </div>
  </div>
</div>
<script>
const DATA = {data_json};

function esc(s){{
  const d=document.createElement('div');d.textContent=s||'';return d.innerHTML;
}}

function renderDetail(r){{
  if(!r.detail) return '';
  const paras = r.detail.split(/\n[\\s]*\n|(?<=[.])[\\s]*\n/).filter(Boolean).map(b=>{{
    b=b.trim();if(!b)return '';
    const m=b.match(/^([A-Z][A-Za-z /\\-]{{1,30}}?[.:])([ \\t]+)(.*)$/s);
    return m?`<p><b>${{esc(m[1])}}</b> ${{esc(m[3])}}</p>`:`<p>${{esc(b)}}</p>`;
  }}).join('');
  return `<div class="detail-box"><div class="lab">The method, in detail</div>${{paras}}</div>`;
}}

function renderRow(r, i){{
  const confBadge = r.conf==='high'
    ? '<span class="badge bc-hi">full text</span>'
    : '<span class="badge bc-lo">abstract</span>';
  const det = renderDetail(r);
  const deeplink = `<a class="deeplink" href="${{r.theme_slug}}-deepdive.html#${{r.id}}">→ deep dive page</a>`;
  return `<div class="row" id="row${{i}}" onclick="toggle(${{i}})">
    <div class="row-head">
      <span class="badge bv">${{esc(r.venue)}}</span>
      <span class="badge bt">${{esc(r.theme_label)}}</span>
      ${{confBadge}}
    </div>
    <h3>${{esc(r.title)}}</h3>
    ${{r.what ? `<div class="what">${{esc(r.what)}}</div>` : ''}}
    <div id="exp${{i}}" style="display:none">${{det}}${{deeplink}}</div>
  </div>`;
}}

function toggle(i){{
  const el=document.getElementById('exp'+i);
  const row=document.getElementById('row'+i);
  if(!el)return;
  const open=el.style.display!=='none';
  el.style.display=open?'none':'block';
  row.classList.toggle('open',!open);
}}

let visible=[];
function render(rows){{
  visible=rows;
  const list=document.getElementById('list');
  const empty=document.getElementById('empty');
  document.getElementById('showing').textContent=rows.length+' paper'+(rows.length!==1?'s':'');
  if(!rows.length){{list.innerHTML='';empty.style.display='';return;}}
  empty.style.display='none';
  list.innerHTML=rows.map((r,i)=>renderRow(r,i)).join('');
}}

function filter(){{
  const q=(document.getElementById('search').value||'').toLowerCase().trim();
  const v=document.getElementById('fVenue').value;
  const th=document.getElementById('fTheme').value;
  const hi=document.getElementById('fHi').checked;
  const lo=document.getElementById('fLo').checked;
  const res=DATA.filter(r=>{{
    if(!hi && r.conf==='high') return false;
    if(!lo && r.conf==='low') return false;
    if(v && r.venue!==v) return false;
    if(th && r.theme!==th) return false;
    if(q){{
      const hay=(r.title+' '+(r.what||'')+' '+(r.problem||'')+' '+(r.method||'')+' '+(r.tags||[]).join(' ')+' '+(r.technique||[]).join(' ')+' '+(r.hw||[]).join(' ')).toLowerCase();
      if(!hay.includes(q)) return false;
    }}
    return true;
  }});
  render(res);
}}

document.getElementById('search').addEventListener('input',filter);
document.getElementById('fVenue').addEventListener('change',filter);
document.getElementById('fTheme').addEventListener('change',filter);
document.getElementById('fHi').addEventListener('change',filter);
document.getElementById('fLo').addEventListener('change',filter);

function applyHash(){{
  const h=location.hash.replace(/^#/,'');
  if(!h) return;
  const params={{}};
  h.split('&').forEach(p=>{{const[k,v]=p.split('=');if(k&&v)params[k]=decodeURIComponent(v);}});
  if(params.venue){{
    const s=document.getElementById('fVenue');
    for(let i=0;i<s.options.length;i++)if(s.options[i].value===params.venue){{s.selectedIndex=i;break;}}
  }}
  if(params.theme){{
    const s=document.getElementById('fTheme');
    for(let i=0;i<s.options.length;i++)if(s.options[i].value===params.theme){{s.selectedIndex=i;break;}}
  }}
  if(params.q) document.getElementById('search').value=decodeURIComponent(params.q);
  filter();
  // scroll past header
  document.querySelector('.topbar')?.scrollIntoView();
}}

render(DATA);
applyHash();
</script>
</body>
</html>"""


def main():
    rows = build_rows()
    html_out = render(rows)
    out = ROOT / "explorer.html"
    out.write_text(html_out, encoding="utf-8")
    size_kb = out.stat().st_size // 1024
    print(f"wrote {out} ({size_kb}KB, {len(rows)} papers)")

if __name__ == "__main__":
    main()
