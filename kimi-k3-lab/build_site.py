import os, html, json, re
ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(ROOT, "site")
os.makedirs(SITE, exist_ok=True)

# Rich plain-language "in plain words" sections (drafted by Haiku, curated), keyed by
# output filename. Injected right after each page's <header>, plus the takeaway swap.
_pw_path = os.path.join(ROOT, "plain_words.json")
PLAIN = json.load(open(_pw_path, encoding="utf-8")) if os.path.exists(_pw_path) else {}

def inject_plain_words(doc, fn):
    e = PLAIN.get(fn)
    if not e:
        return doc
    esc = html.escape
    sec = (
        '<section>\n'
        '  <div class="eye">In plain words · the problem, then the idea</div>\n'
        f'  <h2>{esc(e["heading"])}</h2>\n'
        f'  <p>{esc(e["where"])}</p>\n'
        f'  <p><b>The problem.</b> {esc(e["problem"])}</p>\n'
        f'  <p><b>The idea.</b> {esc(e["idea"])}</p>\n'
        f'  <p><b>The name, translated.</b> {esc(e["term"])}</p>\n'
        f'  <div class="why"><h3>What it still can\'t do</h3><p>{esc(e["price"])}</p></div>\n'
        '</section>'
    )
    doc = doc.replace('</header>', '</header>\n' + sec, 1)
    if e.get("aha"):
        doc = re.sub(r'(<p class="aha">).*?(</p>)',
                     lambda m: m.group(1) + esc(e["aha"]) + m.group(2),
                     doc, count=1, flags=re.S)
    return doc

# (out_file, source_html, title, subtitle, emoji, status)
SESSIONS = [
 ("00-overview.html", "00-overview/out/index.html",
  "Start here · the big picture", "No jargon: the one problem the whole GPT-2→K3 lineage solves — how to remember cheaply and smartly — and every rung as an answer to it. Read this first.", "🗺️", "live"),
 ("01-softmax.html", "01-softmax-baseline/out/index.html",
  "The softmax baseline", "GPT-2 attention and the KV-cache wall — the fact every later rung reacts to. Real weights, real cache-growth, no-cache O(N²) vs cache O(N).", "🧱", "live"),
 ("02-linear.html", "02-linear-attention/out/index.html",
  "Linear attention", "ELU+1 folds K,V into a fixed D×D board — the cache stops growing. Real runs: exact re-association, flat decode cost, and the needle-recall fade (0.65→0.08) that prices the tradeoff.", "➗", "live"),
 ("03-deltanet.html", "03-deltanet/out/index.html",
  "DeltaNet", "The delta rule: read-old → subtract → write-new. Real runs: overwrite the same key twice (DeltaNet replaces cleanly, softmax only averages) + needle recall that holds far longer than linear.", "✏️", "live"),
 ("04-chunked.html", "04-chunked-deltanet/out/index.html",
  "Chunked DeltaNet", "Chunk-wise reparameterization → parallel prefill. Real runs: sequential vs chunked identical to 7e-7 across all C, sequential depth cut 32× (L→L/C), 3–22× faster, and the state/score FLOP split.", "🧩", "live"),
 ("05-gated.html", "05-gated-deltanet/out/index.html",
  "Gated DeltaNet", "Mamba-2 decay meets the delta rule. Real runs: a decay dial that forgets stale context (recall 0.46→0.02) while keeping fresh recall sharp, and the α^Δ survival law verified to 4 decimals.", "🎚️", "live"),
 ("06-kda.html", "06-kda-kimi-linear/out/index.html",
  "KDA / Kimi Linear", "Per-channel decay + MLA hybrid. Real runs: per-channel keeps AND forgets (goal 0.86 vs best scalar 0.16), and the 3 KDA:1 MLA interleave reproduces the paper's −75% KV cache.", "🧬", "live"),
 ("07-kimi-k3.html", "07-kimi-k3/out/index.html",
  "Kimi K3", "The assembly: 23×(3 KDA + 1 MLA) macrocycles, latent MoE (18 of 898 fire), SiTU bounded activation, AttnRes across depth (recovery 0.83 vs 0.48). The whole ladder, connected.", "🌐", "live"),
]

def nav(cur_title):
    links = "".join(
        f'<a href="{fn}" style="color:{"#fff;font-weight:600" if t==cur_title else "#8493A8"};text-decoration:none">{html.escape(t)}</a>'
        for fn, src, t, *_ in SESSIONS if fn)
    return ('<nav style="display:flex;gap:16px;flex-wrap:wrap;align-items:center;font-family:ui-monospace,Menlo,monospace;font-size:12.5px;'
            'padding:14px 0;border-bottom:1px solid rgba(150,170,205,.16);margin-bottom:4px">'
            '<a href="index.html" style="color:#4FA8B8;text-decoration:none;font-weight:700">◆ Kimi K3 Lab</a>'
            f'<span style="margin-left:auto;display:flex;gap:16px">{links}</span></nav>')

for fn, src, t, sub, emoji, status in SESSIONS:
    if not fn:
        continue
    doc = open(os.path.join(ROOT, src), encoding="utf-8").read()
    doc = doc.replace('<div class="wrap">', '<div class="wrap">\n' + nav(t), 1)
    doc = inject_plain_words(doc, fn)
    open(os.path.join(SITE, fn), "w", encoding="utf-8").write(doc)

# landing page
def card(i, fn, t, sub, emoji, status):
    n = f"{i:02d}"
    dis = status != "live"
    inner = (f'<div style="display:flex;align-items:baseline;gap:10px">'
             f'<span style="font-family:var(--mono);font-size:12px;color:var(--accent)">{n}</span>'
             f'<span style="font-size:22px">{emoji}</span>'
             f'<span style="font-family:var(--serif);font-size:21px;color:#fff">{html.escape(t)}</span>'
             f'{"" if not dis else "<span style=\"margin-left:auto;font-family:var(--mono);font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:var(--faint);border:1px solid var(--line);border-radius:20px;padding:2px 9px\">soon</span>"}'
             f'</div>'
             f'<p style="margin:10px 0 0;font-size:14.5px;color:var(--soft);line-height:1.6">{html.escape(sub)}</p>')
    style = ("display:block;text-decoration:none;background:var(--bg2);border:1px solid var(--line);border-radius:14px;"
             "padding:18px 20px;transition:border-color .15s") + (";opacity:.55" if dis else "")
    if dis:
        return f'<div style="{style}">{inner}</div>'
    return f'<a href="{fn}" style="{style}" onmouseover="this.style.borderColor=\'var(--accent)\'" onmouseout="this.style.borderColor=\'var(--line)\'">{inner}</a>'

cards = "\n".join(card(i, *s[:1]+s[2:]) if False else card(i, s[0], s[2], s[3], s[4], s[5]) for i, s in enumerate(SESSIONS))

LAND = f"""<title>Kimi K3, from first principles — the lab</title>
<style>
:root{{--bg:#0E1420;--bg2:#141D2C;--ink:#EAEEF4;--soft:#B4BFD0;--dim:#8493A8;--faint:#5A6577;
--line:rgba(150,170,205,.14);--accent:#4FA8B8;--serif:"Iowan Old Style",Palatino,Georgia,serif;
--sans:-apple-system,system-ui,"Segoe UI",Roboto,Arial,sans-serif;--mono:ui-monospace,"SF Mono",Menlo,Consolas,monospace;}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);line-height:1.7}}
.wrap{{max-width:820px;margin:0 auto;padding:64px 24px 80px}}
.kick{{font-family:var(--mono);font-size:11.5px;letter-spacing:.24em;text-transform:uppercase;color:var(--accent)}}
h1{{font-family:var(--serif);font-size:clamp(34px,6vw,52px);line-height:1.05;margin:14px 0 0;color:#fff;letter-spacing:-.02em}}
.dek{{font-size:19px;color:var(--soft);margin:18px 0 0;max-width:64ch}}
.grid{{display:grid;gap:12px;margin-top:34px}}
.foot{{font-family:var(--mono);font-size:12px;color:var(--faint);margin-top:34px;padding-top:18px;border-top:1px solid var(--line)}}
.foot a{{color:var(--accent);text-decoration:none}}
b{{color:var(--ink)}}em{{color:#fff;font-style:italic}}
</style>
<div class="wrap">
  <div class="kick">Hands-on companion</div>
  <h1>Kimi K3, from first principles.</h1>
  <p class="dek">The path from GPT-2 (2019) to Kimi K3 (2026) is a <b>22,580×</b> jump in parameters — but the worklog's claim is that scale isn't the story. Each architectural rung changes <em>what the model stores, how it updates that state, or how it retrieves what a fixed-size state can't hold</em>. This lab rebuilds the ladder and <b>runs every rung for real</b> — the claims become measured numbers.</p>
  <div class="grid">
  {cards}
  </div>
  <div class="foot">Companion to ali (@waterloo_intern), <a href="https://x.com/waterloo_intern/status/2081762065392541951">"22580: From GPT-2 to Kimi K3, Explained"</a>. Built the way <span style="color:var(--dim)">~/projects/llm-from-scratch-lab</span> is: one concept per session, real runs, explanation in the page.</div>
</div>
"""
open(os.path.join(SITE, "index.html"), "w", encoding="utf-8").write(LAND)
print("wrote site/index.html +", sum(1 for s in SESSIONS if s[0]), "session page(s)")
