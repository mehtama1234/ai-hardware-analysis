import json, html
D = json.load(open("out_k3.json"))
B = D["backbone"]; MO = D["moe"]; SI = D["situ"]; AR = D["attnres"]
ME = json.load(open("out_moe.json"))
def esc(s): return html.escape(str(s))

def loadbars():
    # per-expert usage, both ways, sorted descending — show the lopsided profile
    def bars(usage, col):
        u = sorted(usage, reverse=True); mx = max(u)
        return "".join(f"<span style='display:inline-block;width:{100/len(u):.2f}%;height:{max(2,v/mx*46):.0f}px;"
                       f"background:{col};vertical-align:bottom'></span>" for v in u)
    nb = ME["no_balance"]["usage_per_expert"]; wb = ME["with_balance"]["usage_per_expert"]
    return (f"<div style='margin:6px 0'><div class='mini' style='margin:0 0 4px'>no balancing — busiest {ME['no_balance']['busiest_expert_share_pct']}% ({ME['no_balance']['max_over_mean_load']}× fair)</div>"
            f"<div style='height:48px;display:flex;align-items:flex-end;gap:1px'>{bars(nb,'#E0748A')}</div></div>"
            f"<div style='margin:12px 0 0'><div class='mini' style='margin:0 0 4px'>with balancing — busiest {ME['with_balance']['busiest_expert_share_pct']}% ({ME['with_balance']['max_over_mean_load']}× fair)</div>"
            f"<div style='height:48px;display:flex;align-items:flex-end;gap:1px'>{bars(wb,'#4FA8B8')}</div></div>")

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
    lab = (f"<text x='{W-pad}' y='{Y(silu[-1])-6:.1f}' fill='#E0748A' font-size='11' text-anchor='end' font-family=\"ui-monospace,monospace\">the usual squash (climbs)</text>"
           f"<text x='{W-pad}' y='{Y(situ[-1])-6:.1f}' fill='#4FA8B8' font-size='11' text-anchor='end' font-family=\"ui-monospace,monospace\">the new one (levels off)</text>")
    return f"<svg viewBox='0 0 {W} {H}' style='width:100%;height:auto'>{grid}{zero}{line(silu,'#E0748A')}{line(situ,'#4FA8B8')}{lab}</svg>"

RUNGS = [
    ("01", "Keep every note", "perfect recall — but the pile of notes grows forever"),
    ("02", "One running summary", "fold everything into a fixed page — flat cost, but recall blurs"),
    ("03", "Erase, then write", "replace a fact in place instead of piling on top"),
    ("04", "Work in blocks", "the same thing, reorganized to train fast in parallel"),
    ("05", "A forget dial", "fade the whole page to clear out stale material"),
    ("06", "A dial per slot", "keep some kinds of memory while dropping others, at once"),
    ("07", "Kimi K3", "put it together: mostly-cheap memory, a crowd of specialists, reach-back across depth"),
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
.rnm{{font-family:var(--serif);font-size:17px;color:#fff;width:150px;flex:0 0 auto}}
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
  <div class="eye">The backbone · everything so far, stacked up</div>
  <h2>Mostly cheap memory, with full memory mixed in</h2>
  <p>The model's spine is {B['macrocycles']} repeating groups of four layers = <b>{B['total_layers']} layers</b>. In each group, three layers use the <span style="color:var(--accent)">cheap fixed-page memory</span> we built over the last rungs, and the fourth is a <span style="color:var(--amber)">full keep-everything layer</span> — the "keep a little perfect memory" hedge. Every {B['attnres_every']} layers a marker shows where the model is allowed to reach back across depth (more on that below):</p>
  <div class="card">{strip()}
  <div class="mini" style="margin-top:10px"><span style="color:var(--accent)">▮</span> cheap page (fixed size) &nbsp; <span style="color:var(--amber)">▮</span> full memory (keeps everything) &nbsp; <span style="color:var(--viol)">▎</span> reach-back marker (every {B['attnres_every']} layers)</div></div>
  <div class="why"><h3>Why this shape</h3><p>The cheap layers carry most of the text at flat cost; the 1-in-4 full layers recover the sharp recall a fixed page can't (Sessions 02–03), which is where the 75%-smaller memory and up-to-6× faster generation of Session 06 come from. The rest of this page is the three things the model adds <em>on top</em> of this spine.</p></div>
</section>

<section>
  <div class="eye">We ran it · a crowd of specialists</div>
  <h2>898 specialists on hand, 18 awake per word</h2>
  <p>An ordinary model runs every one of its internal parts for every word. This one instead keeps hundreds of small specialist sub-networks and a chooser that sends each word to just a few — here 2 that are always on, plus the chooser's top 16 of the other 896. Each dot is a specialist; the lit ones wake up for one word:</p>
  <div class="card">{moegrid()}
  <div class="mini" style="margin-top:10px">{MO['active_experts_per_token']} of {MO['experts_total']} specialists awake = <b>{MO['expert_fire_fraction_pct']}%</b> of them → the specialist stage does about that fraction of an ordinary model's work. Across the whole model, roughly {MO['reported_active_params_pct']}% of its parts run for any given word (104 billion of 2.8 trillion). The chooser isn't perfectly even (busiest specialist handled {MO['busiest_expert_tokens']} words, quietest {MO['quietest_expert_tokens']}, of {MO['tokens']}) — keeping that balanced is a big part of the real design.</div></div>
  <p class="mini">{esc(MO['point'])}</p>
</section>

<section>
  <div class="eye">We ran it · why the crowd needs balancing</div>
  <h2>Left alone, the load goes lopsided</h2>
  <p>There's a catch to a crowd of specialists, and we can train a small one to show it. Real text is uneven — some kinds of word are far more common — so if the chooser just follows demand, a few popular specialists get swamped while the rest sit nearly idle. We trained a small chooser on deliberately lopsided data, once with no balancing and once with a small "spread the load" incentive. Each bar is one specialist's share of the work, tallest first:</p>
  <div class="card">{loadbars()}</div>
  <p class="mini">{esc(ME['point'])}</p>
</section>

<section>
  <div class="eye">We ran it · a self-limiting squash</div>
  <h2>A squash that knows its own ceiling</h2>
  <p>Deep inside, every model has a little "squash" step that reshapes each number before passing it on. The usual one keeps climbing without limit; this model swaps in a version (called SiTU) that levels off. We computed both — they match near zero, then the old one keeps rising while the new one flattens out:</p>
  <div class="card">{situsvg()}
  <div class="mini" style="margin-top:6px">Far out (at 6): the old squash ≈ {SI['silu_at_6']} and still climbing, versus the new one ≈ {SI['situ_at_6']}, leveled off. A squash that can't run away keeps the numbers steady in a model this size.</div></div>
  <p class="mini">{esc(SI['point'])}</p>
</section>

<section>
  <div class="eye">We ran it · reaching back across depth</div>
  <h2>Reaching back to an exact earlier layer</h2>
  <p>Every trick so far reached across <em>words</em>. This one (called attention residuals) does the same look-up across <em>layers</em>: instead of a deep layer getting an equal blend of everything the earlier layers produced, it can score them and pull out the one earlier result it actually needs. We hid a useful result in one earlier layer among noisy ones and asked each approach to recover it:</p>
  <div class="card">
    <div class="arbars">
      <div class="arb"><span class="arl">reach back to the right layer</span><span class="art"><span class="arf a" style="width:{AR['attnres_recovery']*100:.0f}%"></span></span><span class="arv">{AR['attnres_recovery']:.2f}</span></div>
      <div class="arb"><span class="arl">equal blend of all layers</span><span class="art"><span class="arf b" style="width:{AR['plain_residual_recovery']*100:.0f}%"></span></span><span class="arv">{AR['plain_residual_recovery']:.2f}</span></div>
    </div>
    <div class="mini" style="margin-top:8px">recovery = how close the recovered result is to the hidden one, across {AR['N_blocks']} layers (1 = exact).</div>
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
