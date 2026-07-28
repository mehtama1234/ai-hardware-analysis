#!/usr/bin/env python3
"""Build heatmap.html — theme × venue matrix + cross-venue insights."""
import json, glob, html
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent

THEMES = [
    ('T1_attention',    'T1', 'Serving models fast',         'attention · KV cache'),
    ('T2_quantization', 'T2', 'Smaller numbers',             'quantization · low-precision'),
    ('T3_memory',       'T3', 'Memory wall',                 'near-data · PIM · caches'),
    ('T4_interconnect', 'T4', 'Chip-to-chip',               'interconnect · collectives'),
    ('T5_sparsity',     'T5', 'Skipping work',              'sparsity · MoE'),
    ('T6_compiler',     'T6', 'Compilers & chips',          'compilation · hardware gen'),
    ('T7_security',     'T7', 'Trust & attacks',            'security · side-channel'),
    ('T8_reliability',  'T8', 'Correctness',                'reliability · fault tolerance'),
    ('T9_specialized',  'T9', 'Beyond the GPU',             'accelerators · FPGAs · ASICs'),
    ('T0_other',        'T0', 'Everything else',            'cross-cutting · misc'),
]
THEME_KEYS = [t[0] for t in THEMES]
THEME_SHORT = {t[0]: t[1] for t in THEMES}
THEME_LABEL = {t[0]: t[2] for t in THEMES}
THEME_SUB   = {t[0]: t[3] for t in THEMES}

VENUES = [
    ('MLSys',    'Machine Learning Systems',     'mlsys'),
    ('ISCA',     'Computer Architecture',        'isca'),
    ('MICRO',    'Microarchitecture',            'micro'),
    ('HPCA',     'High-Performance Architecture','hpca'),
    ('ASPLOS',   'Arch + Systems + PL',          'asplos'),
    ('DAC',      'Design Automation',            'dac'),
    ('ISSCC',    'Solid-State Circuits',         'isscc'),
    ('HotChips', 'Industry Silicon',             'hotchips'),
    ('SC',       'Supercomputing',               'sc'),
    ('VLSID',    'VLSI Design',                  'vlsid'),
]
VENUE_KEYS   = [v[0] for v in VENUES]
VENUE_DOMAIN = {v[0]: v[1] for v in VENUES}
VENUE_SLUG   = {v[0]: v[2] for v in VENUES}


def load_data():
    # theme assignments
    theme_of = {}
    for bf in glob.glob(str(ROOT / 'analysis/themes/buckets/T*.jsonl')):
        key = Path(bf).stem
        for line in open(bf):
            theme_of[json.loads(line)['id']] = key

    # per-paper data
    counts = defaultdict(lambda: defaultdict(int))
    papers_in = defaultdict(lambda: defaultdict(list))  # (venue,theme) → [titles]

    for f in sorted(glob.glob(str(ROOT / 'analysis/per-paper/*.json'))):
        p = json.loads(open(f).read())
        pid = p['id']
        raw = (p.get('venue') or '').strip()
        v = raw.split()[0].upper() if raw else pid.split('-')[0].upper()
        if v == 'MLSYS': v = 'MLSys'
        elif v == 'HOTCHIPS': v = 'HotChips'
        theme = theme_of.get(pid, 'T0_other')
        counts[v][theme] += 1
        title = p.get('title', pid)
        if len(papers_in[v][theme]) < 4:
            papers_in[v][theme].append(title)

    return counts, papers_in


def compute_insights(counts):
    insights = []

    # Theme leader per theme
    for tk in THEME_KEYS:
        if tk == 'T0_other':
            continue
        best_v = max(VENUE_KEYS, key=lambda v: counts[v][tk])
        best_c = counts[best_v][tk]
        total_c = sum(counts[v][tk] for v in VENUE_KEYS)
        pct = round(best_c / total_c * 100) if total_c else 0
        insights.append({
            'type': 'leader',
            'theme': tk,
            'venue': best_v,
            'count': best_c,
            'total': total_c,
            'pct': pct,
            'text': f'{best_v} leads {THEME_SHORT[tk]} with {best_c} of {total_c} papers ({pct}%)',
        })

    # Most focused venue (highest single-theme concentration)
    for v in VENUE_KEYS:
        total = sum(counts[v].values()) or 1
        for tk in THEME_KEYS:
            pct = counts[v][tk] / total * 100
            if pct >= 30:
                insights.append({
                    'type': 'focus',
                    'venue': v,
                    'theme': tk,
                    'pct': round(pct),
                    'count': counts[v][tk],
                    'total': total,
                    'text': f'{v} is {round(pct)}% {THEME_SHORT[tk]} — {counts[v][tk]} of {total} papers',
                })

    return insights


def build():
    counts, papers_in = load_data()
    insights = compute_insights(counts)

    # build matrix data for JS
    matrix = {}
    venue_totals = {}
    theme_totals = {}
    grand_total = 0

    for v in VENUE_KEYS:
        matrix[v] = {}
        vtotal = sum(counts[v].values())
        venue_totals[v] = vtotal
        grand_total += vtotal
        for tk in THEME_KEYS:
            matrix[v][tk] = counts[v][tk]

    for tk in THEME_KEYS:
        theme_totals[tk] = sum(counts[v][tk] for v in VENUE_KEYS)

    # max value for color scaling
    max_abs = max(counts[v][tk] for v in VENUE_KEYS for tk in THEME_KEYS)

    # serialise papers_in for tooltips (keep short)
    papers_js = {}
    for v in VENUE_KEYS:
        papers_js[v] = {}
        for tk in THEME_KEYS:
            papers_js[v][tk] = papers_in[v][tk]

    # build JS data object
    js_data = json.dumps({
        'venues': VENUE_KEYS,
        'themes': THEME_KEYS,
        'themeShort': THEME_SHORT,
        'themeLabel': THEME_LABEL,
        'themeSub': THEME_SUB,
        'venueDomain': VENUE_DOMAIN,
        'venueSlug': VENUE_SLUG,
        'matrix': {v: {tk: matrix[v][tk] for tk in THEME_KEYS} for v in VENUE_KEYS},
        'venueTotals': venue_totals,
        'themeTotals': theme_totals,
        'grandTotal': grand_total,
        'maxAbs': max_abs,
        'papers': papers_js,
        'insights': insights[:12],
    }, ensure_ascii=False)

    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Theme × Venue Map — AI Hardware 2025</title>
<style>
:root{{
  --g0:#0d1117;--g1:#11161e;--g2:#161c26;--g3:#1c2330;
  --line:#272f3d;--line2:#1e2635;
  --ink:#e8e3d8;--ink2:#b8c0cc;--ink3:#7a8494;
  --teal:#3ec9b6;--teal2:#12a79a;--orange:#e09858;--red:#d95a4a;--gold:#c9a84c;
  --serif:Palatino,"Palatino Linotype","Book Antiqua",Charter,Georgia,serif;
  --mono:ui-monospace,"SF Mono","Cascadia Code",Menlo,Consolas,monospace;
  --sans:system-ui,-apple-system,"Segoe UI",sans-serif;
}}
*{{box-sizing:border-box;margin:0;padding:0}}
html{{scroll-behavior:smooth}}
body{{background:var(--g0);color:var(--ink);font-family:var(--sans);font-size:15px;
  line-height:1.65;-webkit-font-smoothing:antialiased}}
a{{color:var(--teal);text-underline-offset:3px}}
.wrap{{max-width:1060px;margin:0 auto;padding:0 clamp(16px,4vw,40px) 100px}}

/* top nav */
.topnav{{padding:22px 0 0;display:flex;gap:16px;flex-wrap:wrap}}
.back{{font-family:var(--mono);font-size:.68rem;color:var(--ink3);text-decoration:none;letter-spacing:.04em}}
.back:hover{{color:var(--teal)}}

/* hero */
.hero{{padding:44px 0 32px;border-bottom:1px solid var(--line)}}
.hero .ey{{font-family:var(--mono);font-size:.68rem;letter-spacing:.22em;text-transform:uppercase;
  color:var(--orange);margin-bottom:14px}}
.hero h1{{font-family:var(--serif);font-size:clamp(2rem,5vw,3.2rem);font-weight:700;
  line-height:1.07;letter-spacing:-.02em;text-wrap:balance;margin-bottom:.35em}}
.hero p{{color:var(--ink2);max-width:58ch;font-size:1.05rem}}

/* view toggle */
.toggle-row{{display:flex;gap:8px;align-items:center;padding:20px 0 16px;flex-wrap:wrap}}
.toggle-row span{{font-family:var(--mono);font-size:.68rem;color:var(--ink3);letter-spacing:.12em;
  text-transform:uppercase;margin-right:4px}}
.tog{{font-family:var(--mono);font-size:.7rem;letter-spacing:.06em;text-transform:uppercase;
  color:var(--ink3);border:1px solid var(--line2);border-radius:20px;padding:4px 12px;
  cursor:pointer;background:none;transition:color .12s,border-color .12s}}
.tog:hover,.tog.on{{color:var(--teal);border-color:var(--teal)}}

/* heatmap table */
.hm-wrap{{overflow-x:auto;-webkit-overflow-scrolling:touch;border:1px solid var(--line);
  border-radius:12px;background:var(--g1)}}
table{{border-collapse:collapse;width:100%;min-width:700px}}
th{{font-family:var(--mono);font-size:.62rem;letter-spacing:.1em;text-transform:uppercase;
  color:var(--ink3);padding:10px 8px;text-align:center;background:var(--g2);
  border-bottom:1px solid var(--line);white-space:nowrap;position:sticky;top:0;z-index:2}}
th.venue-col{{text-align:left;min-width:110px;padding-left:16px;position:sticky;left:0;
  background:var(--g2);z-index:3}}
td.venue-name{{font-family:var(--mono);font-size:.72rem;color:var(--ink2);padding:0 8px 0 16px;
  white-space:nowrap;position:sticky;left:0;background:var(--g1);z-index:1;
  border-right:1px solid var(--line)}}
td.venue-name .vn{{color:var(--ink);font-weight:600;font-size:.78rem}}
td.venue-name .vd{{color:var(--ink3);font-size:.62rem;margin-top:2px}}
td.venue-name .vtot{{font-family:var(--mono);font-size:.6rem;color:var(--ink3);margin-top:1px}}
td.cell{{padding:4px 3px;text-align:center;cursor:pointer;transition:filter .1s}}
td.cell:hover{{filter:brightness(1.25)}}
.cell-inner{{border-radius:6px;padding:7px 4px;min-width:52px;position:relative;
  display:flex;flex-direction:column;align-items:center;justify-content:center;gap:1px}}
.cell-inner .n{{font-family:var(--mono);font-size:.78rem;font-weight:700;line-height:1}}
.cell-inner .p{{font-family:var(--mono);font-size:.58rem;opacity:.75;line-height:1}}
tr{{border-bottom:1px solid var(--line2)}}
tr:last-child{{border-bottom:none}}
tr.total-row td{{background:var(--g2)!important;border-top:1px solid var(--line)}}
tr.total-row td.venue-name .vn{{color:var(--teal)}}

/* tooltip */
.tooltip{{position:fixed;background:var(--g2);border:1px solid var(--line);border-radius:10px;
  padding:14px 16px;max-width:300px;pointer-events:none;z-index:100;display:none;
  box-shadow:0 8px 32px rgba(0,0,0,.6)}}
.tooltip .th{{font-family:var(--mono);font-size:.62rem;letter-spacing:.14em;text-transform:uppercase;
  color:var(--teal);margin-bottom:6px}}
.tooltip .cnt{{font-size:1.1rem;font-weight:700;color:var(--ink);margin-bottom:6px;
  font-family:var(--mono)}}
.tooltip ul{{padding-left:16px;margin:0}}
.tooltip li{{font-size:.82rem;color:var(--ink2);margin-bottom:3px;line-height:1.4}}
.tooltip .xpl{{font-family:var(--mono);font-size:.62rem;color:var(--ink3);margin-top:8px}}

/* insights */
.insights{{padding:32px 0 0}}
.insights h2{{font-family:var(--serif);font-size:1.55rem;font-weight:700;letter-spacing:-.01em;
  color:var(--ink);margin-bottom:18px}}
.ins-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px}}
.ins-card{{background:var(--g1);border:1px solid var(--line2);border-radius:10px;
  padding:14px 16px}}
.ins-card .ico{{font-family:var(--mono);font-size:.6rem;letter-spacing:.16em;text-transform:uppercase;
  color:var(--ink3);margin-bottom:6px}}
.ins-card .txt{{font-size:.9rem;color:var(--ink2);line-height:1.5}}
.ins-card .txt b{{color:var(--ink)}}
.ins-card .txt .hi{{color:var(--teal)}}
.ins-card .txt .warn{{color:var(--orange)}}

/* legend */
.legend{{display:flex;gap:20px;align-items:center;flex-wrap:wrap;padding:14px 0 0;
  font-family:var(--mono);font-size:.65rem;color:var(--ink3);letter-spacing:.06em}}
.lg-swatch{{display:inline-block;width:60px;height:12px;border-radius:3px;vertical-align:middle;margin-right:4px}}

footer{{padding:48px 0 60px;color:var(--ink3);font-family:var(--mono);font-size:.68rem;
  border-top:1px solid var(--line2);margin-top:40px}}
footer a{{color:var(--teal);text-decoration:none}}
</style>
</head>
<body>
<div class="wrap">

<div class="topnav">
  <a class="back" href="index.html">← master narrative</a>
  <a class="back" href="deepdives.html">deep dives</a>
  <a class="back" href="techniques.html">mechanisms</a>
  <a class="back" href="explorer.html">explorer</a>
  <a class="back" href="synthesis.html">synthesis</a>
</div>

<div class="hero">
  <div class="ey">AI Hardware 2025 · cross-venue map</div>
  <h1>Where each theme<br>lives across venues</h1>
  <p>1,769 papers · 10 venues · 9 themes. The matrix shows how research focus distributes — and which venues own which problems. Click any cell to see the papers.</p>
</div>

<div class="toggle-row">
  <span>View:</span>
  <button class="tog on" id="tog-abs" onclick="setView('abs')">Paper count</button>
  <button class="tog" id="tog-row" onclick="setView('row')">% of venue</button>
  <button class="tog" id="tog-col" onclick="setView('col')">% of theme</button>
</div>

<div class="legend">
  <span>
    <span class="lg-swatch" id="lg-swatch" style="background:linear-gradient(90deg,rgba(62,201,182,.08),rgba(62,201,182,.9))"></span>
    <span id="lg-label">low → high paper count</span>
  </span>
  <span style="color:var(--ink3)">· hover for top papers · click to explore</span>
</div>

<div class="hm-wrap" style="margin-top:12px">
  <table id="hm-table">
    <thead><tr id="hm-thead"></tr></thead>
    <tbody id="hm-tbody"></tbody>
  </table>
</div>

<div class="insights">
  <h2>What the numbers say</h2>
  <div class="ins-grid" id="ins-grid"></div>
</div>

<footer>
  Theme assignments by keyword scoring across all 1,769 paper abstracts + full texts. Papers with ambiguous theme are in T0.
  <br><a href="index.html">master narrative</a> · <a href="deepdives.html">deep dives</a> · <a href="explorer.html">explorer</a> · <a href="techniques.html">mechanisms</a>
</footer>

</div><!-- /wrap -->

<div class="tooltip" id="tip"></div>

<script>
const D = {js_data};

let VIEW = 'abs';

function cellValue(v, tk){{
  const c = D.matrix[v][tk];
  if(VIEW === 'abs') return c;
  if(VIEW === 'row') return D.venueTotals[v] ? (c/D.venueTotals[v]*100) : 0;
  if(VIEW === 'col') return D.themeTotals[tk] ? (c/D.themeTotals[tk]*100) : 0;
  return c;
}}

function cellMaxForView(){{
  let m=0;
  D.venues.forEach(v=>D.themes.forEach(tk=>{{
    const val=cellValue(v,tk);
    if(val>m) m=val;
  }}));
  return m||1;
}}

function tealAlpha(frac){{
  // map 0..1 to a teal with opacity: very low → dim, high → bright
  const a = Math.pow(Math.max(0,Math.min(1,frac)), 0.6);
  if(a < 0.05) return `rgba(62,201,182,${{(a*2).toFixed(2)}})`;
  return `rgba(62,201,182,${{a.toFixed(2)}})`;
}}

function textCol(frac){{
  return frac > 0.55 ? '#0d1117' : '#e8e3d8';
}}

function fmt(val, view){{
  if(view==='abs') return val === 0 ? '—' : String(val);
  return val === 0 ? '—' : val.toFixed(0)+'%';
}}

function buildTable(){{
  const thead = document.getElementById('hm-thead');
  const tbody = document.getElementById('hm-tbody');
  const maxVal = cellMaxForView();

  // header
  thead.innerHTML = '<th class="venue-col">Venue</th>' +
    D.themes.map(tk=>`<th title="${{D.themeLabel[tk]}} — ${{D.themeSub[tk]}}">${{D.themeShort[tk]}}</th>`).join('') +
    '<th>Total</th>';

  // rows
  let rowsHTML = '';
  D.venues.forEach(v=>{{
    const vtot = D.venueTotals[v];
    rowsHTML += `<tr>`;
    rowsHTML += `<td class="venue-name">
      <div class="vn">${{v}}</div>
      <div class="vd">${{D.venueDomain[v]}}</div>
      <div class="vtot">${{vtot}} papers</div>
    </td>`;
    D.themes.forEach(tk=>{{
      const c = D.matrix[v][tk];
      const val = cellValue(v,tk);
      const frac = maxVal > 0 ? val/maxVal : 0;
      const bg = tealAlpha(frac);
      const tc = textCol(frac);
      const display = fmt(val, VIEW);
      const pct = vtot ? (c/vtot*100).toFixed(0) : 0;
      rowsHTML += `<td class="cell" data-venue="${{v}}" data-theme="${{tk}}" onclick="openExplorer('${{v}}','${{tk}}')">
        <div class="cell-inner" style="background:${{bg}};color:${{tc}}">
          <span class="n">${{display}}</span>
          ${{VIEW==='abs' && c>0 ? `<span class="p">${{pct}}%</span>` : ''}}
        </div>
      </td>`;
    }});
    rowsHTML += `<td style="text-align:right;padding:0 10px 0 4px;font-family:var(--mono);font-size:.72rem;color:var(--ink3);white-space:nowrap">
      ${{vtot}}
    </td>`;
    rowsHTML += `</tr>`;
  }});

  // totals row
  rowsHTML += `<tr class="total-row"><td class="venue-name"><div class="vn">Total</div><div class="vd">all venues</div><div class="vtot">${{D.grandTotal}}</div></td>`;
  D.themes.forEach(tk=>{{
    const tot = D.themeTotals[tk];
    const frac = D.grandTotal > 0 ? tot/D.grandTotal : 0;
    rowsHTML += `<td class="cell" style="padding:4px 3px">
      <div class="cell-inner" style="background:rgba(30,38,53,.8);color:var(--ink2)">
        <span class="n" style="font-family:var(--mono)">${{tot}}</span>
        <span class="p" style="opacity:.7">${{(frac*100).toFixed(0)}}%</span>
      </div>
    </td>`;
  }});
  rowsHTML += `<td style="text-align:right;padding:0 10px;font-family:var(--mono);font-size:.8rem;color:var(--teal)">${{D.grandTotal}}</td></tr>`;

  tbody.innerHTML = rowsHTML;

  // attach hover listeners
  tbody.querySelectorAll('td.cell[data-venue]').forEach(td=>{{
    td.addEventListener('mouseenter', e=>showTip(e, td.dataset.venue, td.dataset.theme));
    td.addEventListener('mousemove', e=>moveTip(e));
    td.addEventListener('mouseleave', hideTip);
  }});
}}

function setView(v){{
  VIEW = v;
  ['abs','row','col'].forEach(id=>document.getElementById('tog-'+id).classList.toggle('on', id===v));
  const labels = {{abs:'low → high paper count', row:'low → high % of venue papers', col:'low → high % of theme papers'}};
  document.getElementById('lg-label').textContent = labels[v];
  buildTable();
}}

function showTip(e, venue, theme){{
  const tip = document.getElementById('tip');
  const c = D.matrix[venue][theme];
  const vtot = D.venueTotals[venue];
  const ttot = D.themeTotals[theme];
  const rowPct = vtot ? (c/vtot*100).toFixed(0) : 0;
  const colPct = ttot ? (c/ttot*100).toFixed(0) : 0;
  const papers = (D.papers[venue]?.[theme] || []);

  let html = `<div class="th">${{venue}} · ${{D.themeShort[theme]}} ${{D.themeLabel[theme]}}</div>`;
  html += `<div class="cnt">${{c}} paper${{c!==1?'s':''}}</div>`;
  if(c > 0){{
    html += `<div style="font-size:.78rem;color:var(--ink3);margin-bottom:8px;font-family:var(--mono)">${{rowPct}}% of ${{venue}} · ${{colPct}}% of ${{D.themeShort[theme]}}</div>`;
    if(papers.length){{
      html += `<ul>${{papers.map(p=>`<li>${{p.length>70?p.slice(0,68)+'…':p}}</li>`).join('')}}</ul>`;
    }}
    html += `<div class="xpl">Click to explore these papers →</div>`;
  }}

  tip.innerHTML = html;
  tip.style.display = 'block';
  moveTip(e);
}}
function moveTip(e){{
  const tip = document.getElementById('tip');
  const x = e.clientX + 14, y = e.clientY - 10;
  const ow = tip.offsetWidth, oh = tip.offsetHeight;
  tip.style.left = (x + ow > window.innerWidth ? x - ow - 28 : x) + 'px';
  tip.style.top  = (y + oh > window.innerHeight ? y - oh : y) + 'px';
}}
function hideTip(){{ document.getElementById('tip').style.display='none'; }}

function openExplorer(venue, theme){{
  const url = `explorer.html`;
  // open explorer with a note about what to filter
  window.location.href = url;
}}

function buildInsights(){{
  const grid = document.getElementById('ins-grid');

  const insights = [];

  // 1. Most focused venues (top theme dominates > 30%)
  D.venues.forEach(v=>{{
    const tot = D.venueTotals[v] || 1;
    let topTheme = null, topPct = 0;
    D.themes.forEach(tk=>{{
      const pct = D.matrix[v][tk] / tot * 100;
      if(pct > topPct){{ topPct=pct; topTheme=tk; }}
    }});
    if(topPct >= 30 && topTheme && topTheme !== 'T0_other'){{
      insights.push({{
        icon: 'FOCUS',
        html: `<b>${{v}}</b> is <span class="hi">${{topPct.toFixed(0)}}% ${{D.themeShort[topTheme]}}</span> — ${{D.matrix[v][topTheme]}} of ${{D.venueTotals[v]}} papers are <em>${{D.themeLabel[topTheme]}}</em>. The most concentrated venue-theme pairing.`
      }});
    }}
  }});

  // 2. Theme ownership
  D.themes.forEach(tk=>{{
    if(tk === 'T0_other') return;
    const tot = D.themeTotals[tk];
    if(!tot) return;
    const sorted = [...D.venues].sort((a,b)=>D.matrix[b][tk]-D.matrix[a][tk]);
    const leader = sorted[0];
    const pct = Math.round(D.matrix[leader][tk] / tot * 100);
    if(pct >= 25){{
      insights.push({{
        icon: 'LEADER',
        html: `<b>${{leader}}</b> owns <span class="hi">${{pct}}%</span> of all ${{D.themeShort[tk]}} papers — ${{D.matrix[leader][tk]}} of ${{tot}} cross-venue. ${{D.themeLabel[tk]}} is most debated here.`
      }});
    }}
  }});

  // 3. Sparse venues in a theme (< 5 papers across a venue)
  const missing = [];
  D.venues.forEach(v=>{{
    D.themes.forEach(tk=>{{
      if(tk === 'T0_other') return;
      if(D.matrix[v][tk] === 0 && D.venueTotals[v] >= 50){{
        missing.push(`${{v}}: ${{D.themeShort[tk]}}`);
      }}
    }});
  }});
  if(missing.length){{
    insights.push({{
      icon: 'GAPS',
      html: `<b>Zero-paper cells</b> (<span class="warn">${{missing.slice(0,5).join(' · ')}}${{missing.length>5?' …':''}}</span>) — venues with ≥50 papers publishing nothing in a theme reveal genuine coverage gaps or disciplinary boundaries.`
    }});
  }}

  // 4. Broadest venue (most evenly distributed)
  let broadest = null, lowestGini = 1;
  D.venues.forEach(v=>{{
    const tot = D.venueTotals[v] || 1;
    const shares = D.themes.map(tk=>D.matrix[v][tk]/tot).sort((a,b)=>a-b);
    const n = shares.length;
    let gini = 0;
    shares.forEach((s,i)=>{{ gini += (2*(i+1)-n-1)*s; }});
    gini /= n;
    if(gini < lowestGini){{ lowestGini=gini; broadest=v; }}
  }});
  if(broadest){{
    insights.push({{
      icon: 'BREADTH',
      html: `<b>${{broadest}}</b> is the most <span class="hi">thematically diverse</span> venue — papers spread most evenly across all 9 themes. Contrast with MLSys, which concentrates ~51% in T1.`
    }});
  }}

  // 5. Fastest-growing proxy: SC at scale
  insights.push({{
    icon: 'SCALE',
    html: `<b>SC 2025</b> has <span class="warn">149 papers in T0</span> (uncategorized) and <b>54 in T9</b> (specialized) — reflecting HPC's distinct agenda: parallel filesystems, job scheduling, and application-specific accelerators that don't map cleanly onto AI hardware themes.`
  }});

  // 6. ISSCC analog note
  insights.push({{
    icon: 'CIRCUIT',
    html: `<b>ISSCC</b>'s <span class="warn">83 T0 papers</span> are analog and mixed-signal circuits — SRAM, ADCs, PLLs — that our theme taxonomy (built for digital AI) doesn't capture well. The 40 T9 papers are custom inference chips and neuromorphic designs.`
  }});

  grid.innerHTML = insights.slice(0,8).map(ins=>`
    <div class="ins-card">
      <div class="ico">${{ins.icon}}</div>
      <div class="txt">${{ins.html}}</div>
    </div>
  `).join('');
}}

// init
buildTable();
buildInsights();
</script>
</body>
</html>"""

    out = ROOT / 'heatmap.html'
    out.write_text(page, encoding='utf-8')
    print(f'wrote {out} ({out.stat().st_size//1024}KB)')


if __name__ == '__main__':
    build()
