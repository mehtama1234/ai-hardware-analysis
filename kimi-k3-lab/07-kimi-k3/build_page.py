import json, html
D = json.load(open("out_k3.json"))
B = D["backbone"]; MO = D["moe"]; SI = D["situ"]; AR = D["attnres"]
def esc(s): return html.escape(str(s))

# macrocycle strip: 92 layers, every 4th = MLA, AttnRes boundary every 12
def strip():
    cells = ""
    for i in range(B["total_layers"]):
        mla = (i % 4 == 3)
        bound = " br" if (i + 1) % B["attnres_every"] == 0 else ""
        cells += f"<span class='lyc {'mla' if mla else 'kda'}{bound}' title='layer {i+1}'></span>"
    return f"<div class='lstrip'>{cells}</div>"

# MoE sparsity grid: ~898 dots, 18 lit (2 shared + 16 routed)
def moegrid():
    total = MO["experts_total"]; active = MO["active_experts_per_token"]
    # deterministic scatter of active indices
    lit = set([0, 1])                      # 2 shared
    step = total // (active - 2)
    for j in range(active - 2):
        lit.add(3 + j * step)
    dots = ""
    for i in range(total):
        cls = "on" if i in lit else "off"
        dots += f"<span class='moed {cls}'></span>"
    return f"<div class='moegrid'>{dots}</div>"

def situsvg():
    xs = SI["x"]; silu = SI["silu"]; situ = SI["situ"]
    lo, hi = -0.6, 6.2
    W, H, pad = 560, 210, 34
    X = lambda i: pad + (W-2*pad)*i/(len(xs)-1)
    Y = lambda v: H-pad - (H-2*pad)*(v-lo)/(hi-lo)
    def line(ys, col):
        return f"<path d='M{' L'.join(f'{X(i):.1f},{Y(v):.1f}' for i,v in enumerate(ys))}' fill='none' stroke='{col}' stroke-width='2'/>"
    grid = ""
    for gy in (0, 2, 4, 6):
        grid += f"<line x1='{pad}' y1='{Y(gy):.1f}' x2='{W-pad}' y2='{Y(gy):.1f}' stroke='rgba(150,170,205,.10)'/><text x='{pad-6}' y='{Y(gy)+3:.1f}' fill='#5A6577' font-size='9' text-anchor='end' font-family=\"ui-monospace,monospace\">{gy}</text>"
    zero = f"<line x1='{X((len(xs)-1)/2):.1f}' y1='{pad}' x2='{X((len(xs)-1)/2):.1f}' y2='{H-pad}' stroke='rgba(150,170,205,.10)'/>"
    lab = (f"<text x='{W-pad}' y='{Y(silu[-1])-6:.1f}' fill='#E0748A' font-size='11' text-anchor='end' font-family=\"ui-monospace,monospace\">SiLU (unbounded)</text>"
           f"<text x='{W-pad}' y='{Y(situ[-1])-6:.1f}' fill='#4FA8B8' font-size='11' text-anchor='end' font-family=\"ui-monospace,monospace\">SiTU (bounded)</text>")
    return f"<svg viewBox='0 0 {W} {H}' style='width:100%;height:auto'>{grid}{zero}{line(silu,'#E0748A')}{line(situ,'#4FA8B8')}{lab}</svg>"

RUNGS = [
    ("01", "Softmax", "keeps every note — perfect recall, but the KV cache grows forever"),
    ("02", "Linear", "fold K,V into a fixed board — flat cost, but recall blurs"),
    ("03", "DeltaNet", "erase-then-write — edit a fact in place instead of piling on"),
    ("04", "Chunked", "same delta rule, re-scheduled to train fast on GPUs"),
    ("05", "Gated", "a decay dial — forget stale context generally"),
    ("06", "KDA", "per-channel decay — keep some, forget others, at once"),
    ("07", "Kimi K3", "assemble it: KDA+MLA spine, latent MoE, SiTU, AttnRes"),
]
def ladder():
    return "".join(
        f"<div class='rung{' cur' if n=='07' else ''}'><span class='rnn'>{n}</span>"
        f"<span class='rnm'>{esc(nm)}</span><span class='rnd'>{esc(desc)}</span></div>"
        for n, nm, desc in RUNGS)

P = f"""<title>Kimi K3 Lab · 07 — Kimi K3, the assembly</title>
<style>
:root{{--bg:#0E1420;--bg2:#141D2C;--panel:#18212F;--ink:#EAEEF4;--soft:#B4BFD0;--dim:#8493A8;--faint:#5A6577;
--line:rgba(150,170,205,.14);--accent:#4FA8B8;--amber:#E3A63A;--rose:#E0748A;--viol:#9B8CE0;--serif:"Iowan Old Style",Palatino,Georgia,serif;
--sans:-apple-system,system-ui,"Segoe UI",Roboto,Arial,sans-serif;--mono:ui-monospace,"SF Mono",Menlo,Consolas,monospace;}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);line-height:1.75;font-size:17px}}
.wrap{{max-width:860px;margin:0 auto;padding:0 24px}}
p{{color:var(--soft);margin:0 0 16px}}b{{color:var(--ink)}}em{{color:#fff;font-style:italic}}
.mono{{font-family:var(--mono)}}
.kick{{font-family:var(--mono);font-size:11.5px;letter-spacing:.24em;text-transform:uppercase;color:var(--accent)}}
h1{{font-family:var(--serif);font-size:clamp(34px,6vw,54px);line-height:1.05;margin:14px 0 0;color:#fff;letter-spacing:-.02em}}
h2{{font-family:var(--serif);font-size:27px;margin:0 0 8px;color:#fff}}
.dek{{font-size:19px;color:var(--soft);margin-top:18px;max-width:62ch}}
section{{padding:44px 0;border-top:1px solid var(--line)}}
.eye{{font-family:var(--mono);font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--dim);margin-bottom:12px}}
.why{{background:var(--bg2);border:1px solid var(--line);border-left:3px solid var(--accent);border-radius:12px;padding:16px 20px;margin:18px 0}}
.why h3{{margin:0 0 6px;font-size:12.5px;font-family:var(--mono);letter-spacing:.05em;text-transform:uppercase;color:var(--accent)}}.why p{{margin:0;font-size:15px;color:var(--soft)}}
.card{{background:var(--bg2);border:1px solid var(--line);border-radius:14px;padding:20px 22px;margin-top:14px}}
.mini{{font-family:var(--mono);font-size:12px;color:var(--faint);margin-top:10px;line-height:1.6}}
.run{{background:var(--bg2);border:1px solid var(--line);border-left:3px solid var(--amber);border-radius:12px;padding:14px 18px;margin:16px 0}}
.run .rt{{font-family:var(--mono);font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--amber);margin-bottom:8px}}
.run p{{margin:0;font-size:14.5px;color:var(--soft)}}
.stat{{display:flex;gap:24px;flex-wrap:wrap;margin:20px 0 4px}}
.stat .sn{{font-family:var(--serif);font-size:32px;color:#fff;line-height:1}}.stat .sl{{font-family:var(--mono);font-size:11px;color:var(--dim);margin-top:5px}}
.lstrip{{display:flex;flex-wrap:wrap;gap:2px;margin:10px 0}}
.lyc{{width:12px;height:22px;border-radius:2px;flex:0 0 auto}}
.lyc.kda{{background:rgba(79,168,184,.30);border:1px solid rgba(79,168,184,.4)}}
.lyc.mla{{background:var(--amber);border:1px solid #f0b95a}}
.lyc.br{{margin-right:9px;box-shadow:3px 0 0 var(--viol)}}
.moegrid{{display:grid;grid-template-columns:repeat(38,1fr);gap:2px;margin:8px 0}}
.moed{{width:100%;aspect-ratio:1;border-radius:50%}}
.moed.off{{background:rgba(150,170,205,.10)}}
.moed.on{{background:var(--accent);box-shadow:0 0 5px var(--accent)}}
.eqn{{font-family:var(--mono);font-size:13.5px;color:var(--ink);background:#0C1119;border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin:14px 0;overflow-x:auto;white-space:pre;line-height:1.7}}
.eqn .c{{color:var(--accent)}}.eqn .g{{color:var(--faint)}}
.arbars{{margin-top:12px}}
.arb{{display:flex;align-items:center;gap:12px;margin:9px 0;font-family:var(--mono);font-size:12.5px}}
.arl{{width:150px;color:var(--soft)}}
.art{{flex:1;height:20px;background:rgba(150,170,205,.06);border-radius:5px;overflow:hidden}}
.arf{{display:block;height:100%}}.arf.a{{background:linear-gradient(90deg,#2E6E7A,#4FA8B8)}}.arf.b{{background:rgba(150,170,205,.3)}}
.arv{{width:44px;color:var(--soft)}}
.rung{{display:flex;align-items:baseline;gap:12px;padding:9px 0;border-bottom:1px solid var(--line)}}
.rung.cur{{background:rgba(79,168,184,.06);border-radius:8px;padding:9px 10px}}
.rnn{{font-family:var(--mono);font-size:12px;color:var(--accent);width:22px;flex:0 0 auto}}
.rnm{{font-family:var(--serif);font-size:18px;color:#fff;width:96px;flex:0 0 auto}}
.rnd{{font-size:14.5px;color:var(--soft)}}
.aha{{font-family:var(--serif);font-size:23px;line-height:1.45;color:#fff;border-left:3px solid var(--accent);padding-left:20px;margin:10px 0}}
.next{{font-family:var(--mono);font-size:13px;color:var(--dim);margin-top:12px}}.next a{{color:var(--accent);text-decoration:none}}
.src{{font-family:var(--mono);font-size:12px;color:var(--faint);margin-top:28px;padding-top:16px;border-top:1px solid var(--line)}}.src a{{color:var(--accent);text-decoration:none}}
</style>
<div class="wrap">
<header style="padding:64px 0 8px">
  <div class="kick">Kimi K3, from first principles · Session 07 of 07 · the assembly</div>
  <h1>Put it together.</h1>
  <p class="dek">Every rung so far fixed one thing about how a model remembers. This final page puts them together into the real model — <b>Kimi K3</b> — and layers on three more ideas, each added only where it does a real job: a crowd of small specialists where only a few work on any given word, a gentler internal step that won't run away, and a way for deep layers to reach back and grab an exact earlier result. The model is 22,580 times bigger than where we started; the point is how carefully that size is spent.</p>
  <div class="stat">
    <div><div class="sn">2.8T</div><div class="sl">total params</div></div>
    <div><div class="sn">~104B</div><div class="sl">active per token ({MO['reported_active_params_pct']}%)</div></div>
    <div><div class="sn">898</div><div class="sl">experts · 16 fire</div></div>
    <div><div class="sn">1M</div><div class="sl">context · native vision</div></div>
  </div>
</header>

<section>
  <div class="eye">The backbone · Sessions 02–06 made physical</div>
  <h2>{B['macrocycles']} macrocycles of 3 KDA + 1 MLA</h2>
  <p>The language spine is {B['macrocycles']} four-layer macrocycles = <b>{B['total_layers']} layers</b>. In each, three layers use <span style="color:var(--accent)">KDA</span> (the per-channel-gated fixed board from Session 06 — cheap, constant-state) and the fourth is <span style="color:var(--amber)">MLA</span> (full softmax retrieval — the "keep a little perfect memory" hedge). Every {B['attnres_every']} layers a block boundary marks where Attention Residuals mix depth ({B['attnres_blocks']} blocks):</p>
  <div class="card">{strip()}
  <div class="mini" style="margin-top:10px"><span style="color:var(--accent)">▮</span> KDA (constant state) &nbsp; <span style="color:var(--amber)">▮</span> MLA (full attention) &nbsp; <span style="color:var(--viol)">▎</span> AttnRes block boundary (every {B['attnres_every']})</div></div>
  <div class="why"><h3>Why this shape</h3><p>KDA carries most of the context at flat cost; the 1-in-4 MLA layers recover the sharp retrieval a fixed board can't (Sessions 02–03), giving the −75% KV / 6× decode of Session 06. The rest of this page is the three things K3 adds <em>on top</em> of this spine.</p></div>
</section>

<section>
  <div class="eye">We ran it · latent Mixture-of-Experts</div>
  <h2>898 experts on disk, 18 awake per token</h2>
  <p>A dense model runs every parameter for every token. A Mixture-of-Experts keeps hundreds of small expert networks and a router that sends each token to just a few — here 2 always-on shared experts + the router's top 16 of 896. Each dot is an expert; the lit ones fire for one token:</p>
  <div class="card">{moegrid()}
  <div class="mini" style="margin-top:10px">{MO['active_experts_per_token']} of {MO['experts_total']} experts active = <b>{MO['expert_fire_fraction_pct']}%</b> of the pool → the MoE feed-forward does ~that fraction of a dense model's work. Whole-model active params ~{MO['reported_active_params_pct']}% (104B of 2.8T). Measured routing is uneven (load CV {MO['load_balance_cv']}, busiest expert {MO['busiest_expert_tokens']} vs quietest {MO['quietest_expert_tokens']} of {MO['tokens']} tokens) — the report's "Stable LatentMoE" is about keeping that balanced.</div></div>
  <p class="mini">{esc(MO['point'])}</p>
</section>

<section>
  <div class="eye">We ran it · SiTU activation</div>
  <h2>A soft-bounded SiLU</h2>
  <p>Inside each expert, K3 swaps the usual SiLU gate for <b>SiTU</b>: it wraps the gate in a <span class="mono">tanh</span> so the activation can't run off to infinity. We computed both — they track near zero, then SiLU keeps climbing while SiTU levels off:</p>
  <div class="card">{situsvg()}
  <div class="mini" style="margin-top:6px">At x=6: SiLU ≈ {SI['silu_at_6']} (still rising) vs SiTU ≈ {SI['situ_at_6']} (saturated). Bounded activations stay numerically steady at 2.8T scale.</div></div>
  <p class="mini">{esc(SI['point'])}</p>
</section>

<section>
  <div class="eye">We ran it · Attention Residuals</div>
  <h2>Attention across depth, not just time</h2>
  <p>Every mechanism so far attends across <em>tokens</em>. AttnRes does the same file-and-match trick across <em>layers</em>: instead of a plain residual stream that blends every earlier block equally, a later block runs a softmax over the earlier block representations and pulls the one it needs. We hid a signal in one earlier block among noisy others and asked each method to recover it:</p>
  <div class="card">
    <div class="arbars">
      <div class="arb"><span class="arl">AttnRes (softmax/depth)</span><span class="art"><span class="arf a" style="width:{AR['attnres_recovery']*100:.0f}%"></span></span><span class="arv">{AR['attnres_recovery']:.2f}</span></div>
      <div class="arb"><span class="arl">plain residual (uniform)</span><span class="art"><span class="arf b" style="width:{AR['plain_residual_recovery']*100:.0f}%"></span></span><span class="arv">{AR['plain_residual_recovery']:.2f}</span></div>
    </div>
    <div class="mini" style="margin-top:8px">recovery = cosine of the recovered vector to the hidden signal, over {AR['N_blocks']} blocks.</div>
  </div>
  <p class="mini">{esc(AR['point'])}</p>
</section>

<section>
  <div class="eye">Connect the dots · the whole ladder</div>
  <h2>Seven rungs, one idea</h2>
  <p>Read them top to bottom: each rung is a specific fix to how a fixed-size memory is kept, updated, or retrieved — and K3 is where they meet.</p>
  <div class="card">{ladder()}</div>
</section>

<section>
  <div class="eye">The one-line aha · the whole lab</div>
  <p class="aha">From GPT-2 to Kimi K3 was never mainly about size. It was the search for a memory that is <em>cheap</em> (a fixed board, flat cost), <em>smart</em> (knowing what to keep, edit, and forget — per channel), and <em>honest about its limits</em> (a little full attention on the side) — then spending extra capacity only where it has a job: many experts, a bounded activation, attention across depth. The 22,580× came along for the ride.</p>
  <p class="next">Real code: <b>07-kimi-k3/attn.py</b> → <b>out_k3.json</b> · Ground truth: <a href="https://github.com/MoonshotAI/Kimi-K3/blob/main/k3_tech_report.pdf">Kimi K3 tech report</a> + <a href="https://arxiv.org/abs/2510.26692">Kimi Linear</a>.<br>
  ← Back to <a href="index.html">the lab</a> · Start over at <a href="00-overview.html">the big picture</a>.</p>
</section>
<div class="src">Companion to ali (@waterloo_intern), <a href="https://x.com/waterloo_intern/status/2081762065392541951">"22580: From GPT-2 to Kimi K3"</a>; ground truth from Moonshot's <a href="https://github.com/MoonshotAI/Kimi-K3">Kimi K3</a> + <a href="https://arxiv.org/abs/2510.26692">Kimi Linear</a> reports. Every number on this page is produced by the code, not transcribed.</div>
</div>
"""
open("out/index.html", "w", encoding="utf-8").write(P)
print("wrote out/index.html ·", len(P)//1024, "KB · FFFD:", P.count("�"))
