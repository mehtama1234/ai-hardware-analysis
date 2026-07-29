import json, html
D = json.load(open("out_linear.json"))
EQ = D["equivalence"]; ST = D["state_size"]; DC = D["decode_cost"]; ND = D["needle"]
def esc(s): return html.escape(str(s))

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
            f"<text x='{W-pad}' y='{Y(rows[-1]['softmax_recall_cos'])-8:.1f}' fill='#4FA8B8' font-size='11' text-anchor='end' font-family=\"ui-monospace,monospace\">softmax</text>"
            f"<text x='{W-pad}' y='{Y(rows[-1]['linear_recall_cos'])+16:.1f}' fill='#E0748A' font-size='11' text-anchor='end' font-family=\"ui-monospace,monospace\">linear</text></svg>")

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
  <h1>Stop stacking notes. Keep one board.</h1>
  <p class="dek">Session 01 measured the wall: softmax keeps a KV cache that grows with every token. Linear attention is the escape — apply a simple function to the query and key <em>separately</em>, and the whole pile of past keys and values collapses into <b>one fixed-size board</b>. The cost stops growing. We run it, prove the collapse is <em>exact</em>, and then measure the price you pay for it.</p>
  <div class="run"><div class="rt">▶ We ran it · the four numbers</div>
  <p>Fixed-state form and the full-matrix form agree to <b>{EQ['max_abs_diff']:.0e}</b> (exact). The board is <b>constant</b> size while the KV cache is <b>{ST['ratio_kv_over_linear'][3]:,}× larger</b> by 65k tokens. Decode work per step is <b>flat</b> vs softmax's climbing cost. And the price: recalling one specific past value fades from <b>0.65 → 0.08</b> as the board fills.</p></div>
</header>

<section>
  <div class="eye">The trick · why the pile collapses</div>
  <h2>Move the nonlinearity, and the math re-associates</h2>
  <p>Softmax puts its nonlinearity (the exponential) <em>between</em> the query and key — you can't separate them, so you're stuck comparing every query to every stored key. Linear attention applies a function <span class="mono">φ</span> (here <span class="mono">ELU+1</span>, which just makes numbers positive) to the query and key <b>on their own</b>, before they meet. Now the multiplication order is free to change — and that changes everything:</p>
  <div class="eqn"><span class="g"># softmax order — build an N×N table, grows with N</span>
out = ( φ(q) · φ(k)ᵀ ) · V

<span class="g"># linear order — fold keys+values first into a fixed board S = φ(k)ᵀV</span>
out =   φ(q) · ( <span class="c">φ(k)ᵀ · V</span> )      <span class="g"># S is D×D, same size forever</span></div>
  <p>That parenthesis on the right — <span class="mono">S = φ(k)ᵀV</span> — is a <b>D×D board</b> that every new token just adds onto. No matter how long the text, S is the same size. To read, you multiply your query's features by the board. The growing stack of notes is gone, replaced by one running summary.</p>
  <div class="run"><div class="rt">▶ We ran it · the collapse is exact, not an approximation</div>
  <p>We computed both orderings on the same random tensors (N={EQ['N']}, d={EQ['d']}). Max difference between them: <b>{EQ['max_abs_diff']:.2e}</b> — floating-point noise. Re-associating loses <em>nothing</em> relative to linear attention's own full-matrix form. {esc(EQ['point'].split('(What')[0])}</p></div>
</section>

<section>
  <div class="eye">The win · what stops growing</div>
  <h2>One board, the same size at 1k or 128k tokens</h2>
  <p>Linear attention's entire memory is that one D×D board (plus a small vector for bookkeeping). Its size doesn't depend on the sequence length at all. The softmax KV cache, by contrast, adds a slot per token — so it pulls away fast:</p>
  <div class="card">{statebars()}
  <div class="mini" style="margin-top:12px">Floats stored per head (d_head={ST['d_head']}). {esc(ST['point'])}</div></div>
  <p class="mini">And per decode step, softmax must scan all its stored keys (work grows with N) while linear attention just updates and reads the one board — <b>flat</b> work per step: softmax {DC['softmax_flops_per_step'][0]:,} → {DC['softmax_flops_per_step'][-1]:,} FLOPs across the same steps where linear stays {DC['linear_flops_per_step'][0]:,}. Flat cost over a long context is where Kimi Linear's up-to-6× decode speedup and −75% KV cache come from.</p>
</section>

<section>
  <div class="eye">We ran it · the price of a fixed board</div>
  <h2>Ask for one specific memory — and watch it blur</h2>
  <p>Here's the catch, measured. We store N key→value pairs, then query with the <em>exact key</em> of one early "needle" and ask how well its value comes back (cosine to the true value; 1.0 = perfect). Softmax still has every note on file, so it points right at the needle. Linear attention folded everything onto one board — so recalling one value drags in a blur of all the others, and it gets worse as the board fills:</p>
  <div class="card">{needlesvg()}
  <div class="mini" style="margin-top:6px">x-axis = number of stored tokens N (log-spaced). <span style="color:var(--accent)">softmax</span> holds at ~1.0; <span style="color:var(--rose)">linear</span> fades as interference accumulates.</div></div>
  <div class="card" style="overflow-x:auto;margin-top:14px">
  <table>
    <tr><th>N stored</th><th>softmax weight on needle</th><th>softmax recall</th><th>linear recall</th></tr>
    {needletable()}
  </table></div>
  <div class="why"><h3>Why this is the whole rest of the story</h3><p>{esc(ND['point'])}</p></div>
</section>

<section>
  <div class="eye">See it · two ways to remember</div>
  <h2>Growing pile vs one folded board</h2>
  <p>The same information, two storage strategies — softmax keeps every note (the pile climbs); linear attention folds each note into a fixed board (it just glows brighter, never taller). Watch tokens arrive:</p>
  <div class="panel"><canvas data-anim="fold" height="300"></canvas>
    <div class="readout"><span id="fold-r">—</span></div>
  </div>
  <p class="mini">Left: the KV cache — one new card per token, forever. Right: the D×D board — every token folds in, size unchanged. The board is why the cost goes flat; the folding is why single memories blur.</p>
</section>

<section>
  <div class="eye">The one-line aha</div>
  <p class="aha">Move the nonlinearity off the query–key product and the past collapses into one fixed board — flat cost forever. But a single board can't hold each memory apart, so recall of any one fact blurs as it fills. The next rungs are all about <em>tending that board</em> so it stops blurring.</p>
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
    txt('softmax — KV cache',lc,26,C.rose,12.5,'center',true);
    txt('linear — fixed D×D board',rc,26,C.accent,12.5,'center',true);
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
