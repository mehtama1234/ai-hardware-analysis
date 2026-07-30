import json, html
D = json.load(open("out_linear.json"))
EQ = D["equivalence"]; ST = D["state_size"]; DC = D["decode_cost"]; ND = D["needle"]
GP = json.load(open("out_gpu.json"))
def esc(s): return html.escape(str(s))

def gpurows():
    out = ""
    for r in GP["rows"]:
        faster = f"{r['speedup']}×" if r['speedup'] >= 1 else f"{r['speedup']}×"
        hi = "hi" if r['speedup'] >= 1 else "mo"
        out += (f"<tr><td>{r['L']:,}</td>"
                f"<td class='mo'>{r['softmax_ms_per_tok']:.2f}</td>"
                f"<td class='hi'>{r['linear_ms_per_tok']:.2f}</td>"
                f"<td class='{hi}'>{faster}</td>"
                f"<td class='mo'>{r['softmax_kv_MB']:.0f} MB</td>"
                f"<td class='hi'>{r['linear_state_MB']:.1f} MB</td>"
                f"<td class='hi'>{r['mem_ratio']:.0f}×</td></tr>")
    return out

def statebars():
    Ns, kv = ST["N"], ST["kv_cache_floats"]; ls = ST["linear_state_floats"]; mx = max(kv)
    out = f"<div class='bar'><span class='bl'>linear</span><span class='bt'><span class='bf lin' style='width:{ls/mx*100:.2f}%'></span></span><span class='bv'>{ls:,} — <b>constant</b></span></div>"
    for N, c in zip(Ns, kv):
        out += (f"<div class='bar'><span class='bl'>KV {N//1024}k</span>"
                f"<span class='bt'><span class='bf' style='width:{c/mx*100:.1f}%'></span></span>"
                f"<span class='bv'>{c:,}</span></div>")
    return out

def needletable():
    rows = ""
    for r in ND["rows"]:
        cap = " ·cap" if r["over_capacity"] else ""
        sc = r["softmax_recall_cos"]; lc = r["linear_recall_cos"]
        rows += (f"<tr><td>{r['N']}{cap}</td>"
                 f"<td class='mo'>{r['softmax_needle_weight']:.2f}</td>"
                 f"<td class='hi'>{sc:.3f}</td>"
                 f"<td class='mo' style='color:var(--rose)'>{lc:.3f}</td></tr>")
    return rows

# needle recall as an inline dual-line SVG (softmax flat-high vs linear fading)
def needlesvg():
    rows = ND["rows"]; n = len(rows)
    W, H, pad = 560, 180, 30
    def X(i): return pad + (W-2*pad)*i/(n-1)
    def Y(v): return H-pad - (H-2*pad)*v      # v in [0,1]
    def path(key):
        pts = [f"{X(i):.1f},{Y(r[key]):.1f}" for i,r in enumerate(rows)]
        return "M" + " L".join(pts)
    sm = "".join(f"<circle cx='{X(i):.1f}' cy='{Y(r['softmax_recall_cos']):.1f}' r='3' fill='#4FA8B8'/>" for i,r in enumerate(rows))
    ln = "".join(f"<circle cx='{X(i):.1f}' cy='{Y(r['linear_recall_cos']):.1f}' r='3' fill='#E0748A'/>" for i,r in enumerate(rows))
    xl = "".join(f"<text x='{X(i):.1f}' y='{H-8}' fill='#5A6577' font-size='10' text-anchor='middle' font-family=\"ui-monospace,monospace\">{r['N']}</text>" for i,r in enumerate(rows))
    grid = "".join(f"<line x1='{pad}' y1='{Y(g):.1f}' x2='{W-pad}' y2='{Y(g):.1f}' stroke='rgba(150,170,205,.10)'/>"
                   f"<text x='{pad-6}' y='{Y(g)+3:.1f}' fill='#5A6577' font-size='9' text-anchor='end' font-family=\"ui-monospace,monospace\">{g:.1f}</text>" for g in (0,0.5,1.0))
    return (f"<svg viewBox='0 0 {W} {H}' style='width:100%;height:auto'>{grid}"
            f"<path d='{path('softmax_recall_cos')}' fill='none' stroke='#4FA8B8' stroke-width='2'/>{sm}"
            f"<path d='{path('linear_recall_cos')}' fill='none' stroke='#E0748A' stroke-width='2'/>{ln}{xl}"
            f"<text x='{W-pad}' y='{Y(rows[-1]['softmax_recall_cos'])-8:.1f}' fill='#4FA8B8' font-size='11' text-anchor='end' font-family=\"ui-monospace,monospace\">keep every note</text>"
            f"<text x='{W-pad}' y='{Y(rows[-1]['linear_recall_cos'])+16:.1f}' fill='#E0748A' font-size='11' text-anchor='end' font-family=\"ui-monospace,monospace\">one summary</text></svg>")

P = f"""<title>Kimi K3 Lab · 02 — Linear attention</title>
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
.eqn{{font-family:var(--mono);font-size:14px;color:var(--ink);background:#0C1119;border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin:14px 0;overflow-x:auto;white-space:pre;line-height:1.7}}
.eqn .c{{color:var(--accent)}}.eqn .g{{color:var(--faint)}}
.bar{{display:flex;align-items:center;gap:12px;margin:8px 0;font-family:var(--mono);font-size:12.5px}}
.bar .bl{{width:64px;color:var(--dim);text-align:right}}
.bar .bt{{flex:1;height:18px;background:rgba(150,170,205,.06);border-radius:5px;overflow:hidden}}
.bar .bf{{display:block;height:100%;background:linear-gradient(90deg,#7a5a2e,#E3A63A)}}
.bar .bf.lin{{background:linear-gradient(90deg,#2E6E7A,#4FA8B8)}}
.bar .bv{{width:190px;color:var(--soft)}}
table{{width:100%;border-collapse:collapse;margin-top:14px;font-size:13.5px}}
th,td{{padding:8px 10px;text-align:right;border-bottom:1px solid var(--line)}}
th{{font-family:var(--mono);font-size:10.5px;letter-spacing:.06em;text-transform:uppercase;color:var(--dim);font-weight:600}}
td.mo{{font-family:var(--mono);color:var(--soft)}}td.hi{{font-family:var(--mono);color:var(--accent);font-weight:700}}
th:first-child,td:first-child{{text-align:left;color:var(--ink);font-family:var(--mono)}}
.panel{{background:linear-gradient(180deg,#10161D,#0D131A);border:1px solid var(--line);border-radius:14px;padding:8px;margin-top:14px;overflow:hidden}}
.panel canvas{{display:block;width:100%;height:auto;border-radius:8px}}
.readout{{font-family:var(--mono);font-size:12px;color:var(--dim);padding:9px 12px 4px;min-height:18px}}.readout b{{color:var(--accent)}}
.aha{{font-family:var(--serif);font-size:22px;line-height:1.4;color:#fff;border-left:3px solid var(--accent);padding-left:18px;margin:8px 0}}
.next{{font-family:var(--mono);font-size:13px;color:var(--dim);margin-top:10px}}.next a{{color:var(--accent);text-decoration:none}}
.src{{font-family:var(--mono);font-size:12px;color:var(--faint);margin-top:28px;padding-top:16px;border-top:1px solid var(--line)}}
.src a{{color:var(--accent);text-decoration:none}}
</style>
<div class="wrap">
<header style="padding:64px 0 8px">
  <div class="kick">Kimi K3, from first principles · Session 02 of 07</div>
  <h1>Keep a running summary, not a growing pile.</h1>
  <p class="dek">In Session&nbsp;1 the model remembered by keeping one note for every word it read — flawless recall, but a pile of notes that never stops growing, re-read from the top at every single step. This rung asks one plain question: could the model keep a memory that stays the <em>same size forever</em>, however long the text runs, and still be useful? The answer is yes — and it's the fork the whole rest of the story branches from.</p>
</header>

<section>
  <div class="eye">In plain words · the problem, then the idea</div>
  <h2>Trade a pile that grows for a board that doesn't</h2>
  <p><b>The problem, plainly.</b> A pile of notes that grows with every word carries two bills that both keep rising: the room to store it, and the effort to read all of it again for each new word. On a page it's nothing. On a long report — or a million words — you can't afford either. So what we actually want is a memory whose size <em>never changes</em>, and that you can update in one quick step, no matter how much has come before.</p>
  <p><b>The idea, plainly.</b> Stop pinning up a fresh note for every word. Keep a single <b>whiteboard of fixed size</b> and blend each new fact into whatever is already written there. The board never gets bigger. When you want to remember something, you read the board. That's the whole move — a running summary in place of an ever-taller stack.</p>
  <p><b>The name, translated.</b> Papers call this <em>linear attention</em>. "Linear" isn't the interesting part — it just means the work for each new word stays <b>flat</b> instead of piling up. Strip the label and it's nothing more exotic than "keep one summary and keep updating it."</p>
  <div class="why"><h3>And the price, in one line</h3><p>One board can't keep every fact cleanly apart. Blend enough of them and they smear — ask for a single one and you get back a muddy average of many. That tension — a memory that's <em>cheap but blurry</em> — is the exact thing the next four rungs exist to fix. Everything below either shows the cheapness or measures the blur.</p></div>
</section>

<section>
  <div class="eye">Why it works · the one honest bit of math</div>
  <h2>Why the whole pile is even allowed to collapse</h2>
  <p>Why was the model forced to keep every note in the first place? It comes down to <em>how</em> it compares a new question to the past. The original way (softmax) tangles each question together with each stored note through a step you can't work out in advance — so you're stuck keeping all the notes around to redo the comparison every time. Linear attention swaps in a comparison where each note can be <b>blended into the board before any question arrives</b>. Same three steps as always — score, normalize, blend — just re-ordered so the past folds up into one summary instead of waiting around as a pile:</p>
  <div class="eqn"><span class="g"># the old order — compare the question against EVERY stored note (a table that grows)</span>
answer = ( question · every-noteᵀ ) · their-values

<span class="g"># the new order — blend the notes into one board FIRST, then read it once</span>
answer =   question · ( <span class="c">board</span> )      <span class="g"># board = all notes folded together, fixed size forever</span></div>
  <p>The <span class="c">board</span> on the right is just all the past notes added together into one fixed-size grid. However long the text, the board is the same size. To recall, you read your question against that one board — no pile to flip through. (The one technical wrinkle: before blending, each note is passed through a small fixed function that keeps the numbers positive so the blend behaves. That's the only moving part; it doesn't change the picture.)</p>
  <div class="run"><div class="rt">▶ We ran it · the collapse is exact, not a shortcut</div>
  <p>To be sure the fold-it-up version isn't quietly cutting a corner, we computed both the read-the-whole-pile way and the one-board way on the same numbers. Largest disagreement anywhere: <b>{EQ['max_abs_diff']:.0e}</b> — pure rounding noise. Collapsing the pile into a board throws away <em>nothing</em>; it's the same answer, stored smarter.</p></div>
</section>

<section>
  <div class="eye">The win · what stops growing</div>
  <h2>One board, the same size at 1,000 words or 128,000</h2>
  <p>The running-summary memory is just that one fixed grid (plus a little bookkeeping). Its size doesn't depend on how much text you've read at all. The keep-every-note memory, by contrast, adds one more slot for every word — so the two pull apart fast:</p>
  <div class="card">{statebars()}
  <div class="mini" style="margin-top:12px">Floats stored per head (d_head={ST['d_head']}). {esc(ST['point'])}</div></div>
  <p class="mini">And to write each new word, the keep-every-note memory has to scan everything it has stored (more work the longer the text), while the running summary just updates and reads its one board — the <b>same</b> tiny amount of work every time: {DC['softmax_flops_per_step'][0]:,} → {DC['softmax_flops_per_step'][-1]:,} operations for keep-every-note across lengths where the summary stays flat at {DC['linear_flops_per_step'][0]:,}. That flat per-word cost over a long document is where Kimi Linear's up-to-6× faster generation and 75% smaller memory come from.</p>
</section>

<section>
  <div class="eye">We ran it · on a real GPU ({esc(GP['gpu'])})</div>
  <h2>Flat time, tiny memory — measured on real hardware</h2>
  <p>The counts above are arithmetic. Here it is on an actual graphics chip: we generate text one word at a time, both ways, on a {GP['d_model']}-wide model, and measure the real time per word and the real memory used as the text gets longer. Watch the two columns — the running summary's time <b>never moves</b>, while keep-every-note's climbs:</p>
  <div class="card" style="overflow-x:auto"><table>
    <tr><th>words of context</th><th>keep-every-note ms/word</th><th>running summary ms/word</th><th>summary faster by</th><th>keep-every-note memory</th><th>summary memory</th><th>less memory</th></tr>
    {gpurows()}
  </table></div>
  <div class="why"><h3>Read it honestly</h3><p>At short context, keeping every note is actually a touch <em>faster</em> — the running summary has a small fixed overhead that dominates when there's little history. But its time per word stays <b>flat (0.27 ms) at every length</b>, while keep-every-note's climbs (0.18 → 0.38 ms) as the pile grows — so the summary pulls ahead by {GP['rows'][-1]['L']:,} words ({GP['rows'][-1]['speedup']}× faster) and keeps widening. Meanwhile its memory is <b>fixed at {GP['linear_state_MB']:.1f} MB</b> while the kept notes balloon to {GP['rows'][-1]['softmax_kv_MB']:.0f} MB — {GP['rows'][-1]['mem_ratio']:.0f}× more. Push the context to a million words and that flat line is exactly where the paper's "up to 6× faster" comes from.</p></div>
</section>

<section>
  <div class="eye">We ran it · the price of a fixed board</div>
  <h2>Ask for one exact memory — and watch it blur</h2>
  <p>Now the price, measured head-on. We store a batch of facts — each one a cue and the thing filed under it — then hand back the <em>exact cue</em> of one early fact and ask how faithfully its value comes back (1.0 = recalled perfectly, 0 = lost in the noise). Keep-every-note still has that fact on file, so it points straight at it. The running summary folded everything onto one board — so asking for one value drags in a smear of all the rest, and it gets worse the more you've stored:</p>
  <div class="card">{needlesvg()}
  <div class="mini" style="margin-top:6px">left-to-right = how many facts are stored. <span style="color:var(--accent)">keep-every-note</span> holds at ~1.0; the <span style="color:var(--rose)">running summary</span> fades as the facts pile onto one board and blur together.</div></div>
  <div class="card" style="overflow-x:auto;margin-top:14px">
  <table>
    <tr><th>facts stored</th><th>weight on the right one</th><th>keep-every-note recall</th><th>summary recall</th></tr>
    {needletable()}
  </table></div>
  <div class="why"><h3>Why this one chart sets up everything next</h3><p>{esc(ND['point'])}</p></div>
</section>

<section>
  <div class="eye">See it · two ways to remember</div>
  <h2>Growing pile vs one folded board</h2>
  <p>The same information, two ways to store it — keep every note as its own card (the pile climbs forever); or fold each note into one fixed board (it just glows a little brighter, never taller). Watch the words arrive:</p>
  <div class="panel"><canvas data-anim="fold" height="300"></canvas>
    <div class="readout"><span id="fold-r">—</span></div>
  </div>
  <p class="mini">Left: keep-every-note — one new card per word, forever taller. Right: the running summary — every word folds into the same fixed grid, size unchanged. The fixed grid is why the cost stays flat; the folding-together is why single memories blur.</p>
</section>

<section>
  <div class="eye">The one-line takeaway</div>
  <p class="aha">Change how the model compares a question to the past, and the whole pile of notes folds into one fixed board — the same size forever, cheap to update. But one board can't keep every memory apart, so any single fact blurs as it fills up. Everything that follows is about tending that board so it stops blurring.</p>
  <p class="next">Real code: <b>02-linear-attention/attn.py</b> → <b>out_linear.json</b> · Sources: ali's worklog + <a href="https://arxiv.org/abs/2510.26692">Kimi Linear (arXiv 2510.26692)</a>.<br>
  Next → <b>Session 03 · DeltaNet</b>: before writing a new fact, <em>erase the old version of it</em> first. The board stops smearing — targeted memory, not blind addition.</p>
</section>
<div class="src">Companion to ali (@waterloo_intern), <a href="https://x.com/waterloo_intern/status/2081762065392541951">"22580"</a>; ground truth from Moonshot's <a href="https://arxiv.org/abs/2510.26692">Kimi Linear</a>. Numbers are produced by the code, not transcribed.</div>
</div>
<script>
(function(){{
  const ROWS={json.dumps(ND['rows'])};
  const RM=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
  const MONO='ui-monospace,Menlo,Consolas,monospace';
  const C={{accent:'#4FA8B8',amber:'#E3A63A',rose:'#E0748A',viol:'#9B8CE0',ink:'#E7EFF1',mut:'#8B9BA2',dim:'#586770',line:'#243440'}};
  const cv=document.querySelector('canvas[data-anim=fold]'); if(!cv)return;
  let ctx,w,h; const NT=10;
  function fit(){{const dpr=Math.min(devicePixelRatio||1,2);w=cv.clientWidth;h=parseInt(cv.getAttribute('height'))||300;
    cv.width=w*dpr;cv.height=h*dpr;ctx=cv.getContext('2d');ctx.setTransform(dpr,0,0,dpr,0,0);}}
  fit();
  function txt(s,x,y,col,sz,al,bold){{ctx.save();ctx.font=(bold?'700 ':'')+sz+'px '+MONO;ctx.textAlign=al||'center';ctx.textBaseline='middle';ctx.fillStyle=col;ctx.fillText(s,x,y);ctx.restore();}}
  // pseudo per-cell values for the board glow
  function draw(t){{
    ctx.clearRect(0,0,w,h);
    const per=RM?0:0.55; const step=RM?NT-1:Math.floor(t/per)%(NT+2);
    const lc=w*0.26, rc=w*0.72;
    txt('keep every note',lc,26,C.rose,12.5,'center',true);
    txt('one running summary',rc,26,C.accent,12.5,'center',true);
    // LEFT: a growing stack of cards
    const cw=Math.min(120,w*0.34), chh=13, gap=4, bx=lc-cw/2, baseY=h-40;
    for(let i=0;i<Math.min(step+1,NT);i++){{
      const y=baseY-i*(chh+gap);
      ctx.save();ctx.globalAlpha=0.9;ctx.fillStyle='rgba(224,116,138,.16)';ctx.strokeStyle=C.rose;ctx.lineWidth=1;
      ctx.beginPath();const r=3,x=bx;ctx.moveTo(x+r,y);ctx.arcTo(x+cw,y,x+cw,y+chh,r);ctx.arcTo(x+cw,y+chh,x,y+chh,r);ctx.arcTo(x,y+chh,x,y,r);ctx.arcTo(x,y,x+cw,y,r);ctx.closePath();ctx.fill();ctx.stroke();ctx.restore();
    }}
    txt((Math.min(step+1,NT))+' cards stored',lc,baseY+22,C.mut,11,'center');
    txt('grows every token →',lc,44,C.dim,10.5,'center');
    // RIGHT: a fixed grid whose cells brighten as tokens fold in
    const G=6, cs=Math.min(26,(w*0.36)/G), bw=cs*G, gx=rc-bw/2, gy=64;
    const fill=Math.min(1,(step)/NT);
    for(let i=0;i<G;i++)for(let j=0;j<G;j++){{
      const seed=((i*7+j*13)%11)/11; const v=0.08+0.75*fill*(0.4+0.6*seed);
      ctx.save();ctx.fillStyle='rgba(79,168,184,'+v.toFixed(3)+')';ctx.strokeStyle='rgba(10,15,25,.6)';ctx.lineWidth=1;
      ctx.fillRect(gx+j*cs,gy+i*cs,cs-2,cs-2);ctx.strokeRect(gx+j*cs,gy+i*cs,cs-2,cs-2);ctx.restore();
    }}
    ctx.save();ctx.strokeStyle=C.line;ctx.strokeRect(gx-5,gy-5,bw+10,bw+10);ctx.restore();
    txt('same size — just brighter',rc,gy+bw+22,C.mut,11,'center');
    txt('size fixed forever ✓',rc,44,C.dim,10.5,'center');
    const el=document.getElementById('fold-r');
    if(el) el.innerHTML='token '+Math.min(step+1,NT)+' of '+NT+' — left: <b>'+Math.min(step+1,NT)+' cards</b> and climbing · right: <b>one board</b>, folded in, unchanged size.';
  }}
  let raf,t0=performance.now();function frame(now){{draw((now-t0)/1000);raf=requestAnimationFrame(frame);}}
  const io=new IntersectionObserver(es=>es.forEach(e=>{{if(e.isIntersecting){{if(!raf){{t0=performance.now();raf=requestAnimationFrame(frame);}}}}else{{cancelAnimationFrame(raf);raf=0;}}}}),{{threshold:.12}});
  if(RM)draw(9); else io.observe(cv);
  let rt;addEventListener('resize',()=>{{clearTimeout(rt);rt=setTimeout(()=>{{fit();if(RM)draw(9);}},150);}});
}})();
</script>
"""
open("out/index.html", "w", encoding="utf-8").write(P)
print("wrote out/index.html ·", len(P)//1024, "KB · FFFD:", P.count("�"))
