import json, html
D = json.load(open("out_gated.json"))
CS = D["context_switch"]; DL = D["decay_law"]
def esc(s): return html.escape(str(s))

def switchsvg():
    rows = CS["rows"]; n = len(rows)
    W, H, pad = 560, 200, 34
    X = lambda i: pad + (W-2*pad)*i/(n-1)
    Y = lambda v: H-pad - (H-2*pad)*max(0, min(1, v))
    def line(key, col):
        pts = "M" + " L".join(f"{X(i):.1f},{Y(r[key]):.1f}" for i, r in enumerate(rows))
        dots = "".join(f"<circle cx='{X(i):.1f}' cy='{Y(r[key]):.1f}' r='2.8' fill='{col}'/>" for i, r in enumerate(rows))
        return f"<path d='{pts}' fill='none' stroke='{col}' stroke-width='2'/>{dots}"
    grid = "".join(f"<line x1='{pad}' y1='{Y(g):.1f}' x2='{W-pad}' y2='{Y(g):.1f}' stroke='rgba(150,170,205,.10)'/>"
                   f"<text x='{pad-6}' y='{Y(g)+3:.1f}' fill='#5A6577' font-size='9' text-anchor='end' font-family=\"ui-monospace,monospace\">{g:.1f}</text>" for g in (0, 0.5, 1.0))
    xl = "".join(f"<text x='{X(i):.1f}' y='{H-10}' fill='#5A6577' font-size='10' text-anchor='middle' font-family=\"ui-monospace,monospace\">{r['alpha']:.2f}</text>" for i, r in enumerate(rows))
    lab = ("<text x='%.0f' y='%.0f' fill='#4FA8B8' font-size='11' text-anchor='end' font-family=\"ui-monospace,monospace\">fresh B (keep)</text>"
           "<text x='%.0f' y='%.0f' fill='#E0748A' font-size='11' text-anchor='start' font-family=\"ui-monospace,monospace\">stale A (forget)</text>") % (
           W-pad, Y(rows[-1]['fresh_B_recall'])-8, X(1)+6, Y(rows[1]['stale_A_recall'])-8)
    xaxis = f"<text x='{W/2:.0f}' y='{H}' fill='#8493A8' font-size='10' text-anchor='middle' font-family=\"ui-monospace,monospace\">decay α  (1.0 = never forget  →  0.80 = forget fast)</text>"
    return (f"<svg viewBox='0 0 {W} {H+6}' style='width:100%;height:auto'>{grid}"
            f"{line('fresh_B_recall','#4FA8B8')}{line('stale_A_recall','#E0748A')}{xl}{lab}{xaxis}</svg>")

def decayrows():
    return "".join(f"<tr><td>{r['alpha']}</td><td class='mo'>{r['Delta']}</td>"
                   f"<td class='hi'>{r['measured_ratio']:.4f}</td>"
                   f"<td class='mo'>{r['predicted_alpha_pow_Delta']:.4f}</td>"
                   f"<td class='mo' style='color:var(--accent)'>{abs(r['measured_ratio']-r['predicted_alpha_pow_Delta']):.4f}</td></tr>"
                   for r in DL["rows"])

r1 = CS["rows"][0]; rlast = CS["rows"][-2]  # α=1.0 and α=0.90
P = f"""<title>Kimi K3 Lab · 05 — Gated DeltaNet</title>
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
.eqn .c{{color:var(--accent)}}.eqn .g{{color:var(--faint)}}.eqn .a{{color:var(--amber)}}
table{{width:100%;border-collapse:collapse;margin-top:8px;font-size:13.5px}}
th,td{{padding:8px 10px;text-align:right;border-bottom:1px solid var(--line)}}
th{{font-family:var(--mono);font-size:10.5px;letter-spacing:.06em;text-transform:uppercase;color:var(--dim);font-weight:600}}
td.mo{{font-family:var(--mono);color:var(--soft)}}td.hi{{font-family:var(--mono);color:var(--accent);font-weight:700}}
th:first-child,td:first-child{{text-align:left;color:var(--ink);font-family:var(--mono)}}
.panel{{background:linear-gradient(180deg,#10161D,#0D131A);border:1px solid var(--line);border-radius:14px;padding:8px;margin-top:14px;overflow:hidden}}
.panel canvas{{display:block;width:100%;height:auto;border-radius:8px}}
.readout{{font-family:var(--mono);font-size:12px;color:var(--dim);padding:9px 12px 4px;min-height:18px}}.readout b{{color:var(--accent)}}
.aha{{font-family:var(--serif);font-size:22px;line-height:1.4;color:#fff;border-left:3px solid var(--accent);padding-left:18px;margin:8px 0}}
.next{{font-family:var(--mono);font-size:13px;color:var(--dim);margin-top:10px}}.next a{{color:var(--accent);text-decoration:none}}
.src{{font-family:var(--mono);font-size:12px;color:var(--faint);margin-top:28px;padding-top:16px;border-top:1px solid var(--line)}}.src a{{color:var(--accent);text-decoration:none}}
</style>
<div class="wrap">
<header style="padding:64px 0 8px">
  <div class="kick">Kimi K3, from first principles · Session 05 of 07</div>
  <h1>Add a dial for forgetting.</h1>
  <p class="dek">Our model now keeps its memory as a single fixed-size page and can even correct an entry in place. But it has never been able to do one very ordinary thing: <em>forget</em>. When the subject changes, everything it wrote earlier just stays there, crowding out what matters now. This rung adds the missing skill — <b>a simple way to let old writing gently fade</b> so new material has room to land.</p>
  <div class="run"><div class="rt">▶ We ran it · forgetting on a dial</div>
  <p>Write about one topic, then a different one, then ask for the old one back. With forgetting turned off, the stale old topic is still fully present (a <b>{r1['stale_A_recall']:.2f}</b> match). Turn the forgetting up and it fades to <b>{rlast['stale_A_recall']:.2f}</b> — gone — while the fresh topic stays sharp (<b>{rlast['fresh_B_recall']:.2f}</b>). And a memory left alone for a while fades by an exactly predictable amount.</p></div>
</header>

<section>
  <div class="eye">The rule · fade, then write</div>
  <h2>One number that fades the whole page</h2>
  <p>The erase-first rule only touches the one label it's writing. The idea borrowed here is the opposite reflex — shrink <em>everything</em> a little on every step, so the page naturally makes room. This rung does both: fade first, then write.</p>
  <div class="eqn"><span class="g"># erase-first alone: fix one entry, never fade</span>
page = page + change-under-its-label

<span class="g"># with a forget dial: fade the WHOLE page a little, then write</span>
page = <span class="a">fade</span> × page + change-under-its-label     <span class="g"># fade near 1 → barely forgets · fade 0 → wipes the page</span></div>
  <p>Because the fade multiplies the <em>whole</em> page on every step, something written a while ago has been faded once for every step since — so its strength drops off steadily the longer ago it was written, unless it gets refreshed. Recent writing is loud; old writing quietly recedes. That is a general forgetting the erase-first rule alone could never do.</p>
</section>

<section>
  <div class="eye">We ran it · forget the old, keep the new</div>
  <h2>Turning the dial up clears stale material</h2>
  <p>We write an early fact about one topic, fill in with a batch about a second topic, then ask for each back. Watch what the forget dial does as we turn it from off (never forget) toward strong (forget fast): the <span style="color:var(--rose)">stale first topic</span> fades away while the <span style="color:var(--accent)">fresh second topic</span> stays sharp — until the forgetting gets so aggressive it starts eating the present too.</p>
  <div class="card">{switchsvg()}</div>
  <p class="mini">{esc(CS['point'])}</p>
</section>

<section>
  <div class="eye">We ran it · the fading law</div>
  <h2>A memory's strength is a running discount</h2>
  <p>To isolate the fading, we write one value, then take a number of steps that only fade (no new writing), and measure how much of it survives. It comes back scaled by exactly the fade multiplied by itself once for every step waited:</p>
  <div class="card" style="overflow-x:auto"><table>
    <tr><th>fade per step</th><th>steps waited</th><th>measured survival</th><th>predicted</th><th>difference</th></tr>
    {decayrows()}
  </table></div>
  <p class="mini">{esc(DL['point'])}</p>
</section>

<section>
  <div class="eye">See it · the fade dial</div>
  <h2>Old writes dim; new writes stay bright</h2>
  <p>The same page, now with a fade applied every step. Early cells (the old topic) dim toward black as time passes; the newest writing stays bright. That's what forgetting-in-general looks like — no address needed, the whole page just relaxes toward empty:</p>
  <div class="panel"><canvas data-anim="gate" height="290"></canvas>
    <div class="readout"><span id="gate-r">—</span></div>
  </div>
  <p class="mini">Each step multiplies every cell by the fade (just under 1). A cell that gets rewritten jumps back to full; one left alone keeps fading. The fade is learned and depends on what's being read — the model decides when to hold on and when to let go.</p>
</section>

<section>
  <div class="eye">The one-line takeaway</div>
  <p class="aha">One forget dial turns a memory that could only be overwritten into one that can also <em>let go</em> — fading the whole page a little each step so a new topic isn't buried under an old one. But it fades everything by the same amount, and not all memories deserve the same fate.</p>
  <p class="next">Real code: <b>05-gated-deltanet/attn.py</b> → <b>out_gated.json</b> · Source: ali's worklog; the fading idea comes from a model called Mamba.<br>
  Next → <b>Session 06</b>: one dial for the whole page is still blunt — the next rung gives every kind of information its own fade rate, so it can keep some things while dropping others.</p>
</section>
<div class="src">Companion to ali (@waterloo_intern), <a href="https://x.com/waterloo_intern/status/2081762065392541951">"22580"</a>. Numbers on this page are produced by the code, not transcribed.</div>
</div>
<script>
(function(){{
  const RM=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
  const MONO='ui-monospace,Menlo,Consolas,monospace';
  const C={{accent:'#4FA8B8',amber:'#E3A63A',rose:'#E0748A',viol:'#9B8CE0',ink:'#E7EFF1',mut:'#8B9BA2',dim:'#586770',line:'#243440'}};
  const cv=document.querySelector('canvas[data-anim=gate]'); if(!cv)return;
  let ctx,w,h; const G=6;
  function fit(){{const dpr=Math.min(devicePixelRatio||1,2);w=cv.clientWidth;h=parseInt(cv.getAttribute('height'))||290;
    cv.width=w*dpr;cv.height=h*dpr;ctx=cv.getContext('2d');ctx.setTransform(dpr,0,0,dpr,0,0);}}
  fit();
  // grid cells store a brightness; each step: multiply all by alpha, occasionally refresh one
  let cells=null, tick=-1;
  function reset(){{cells=[];for(let i=0;i<G*G;i++)cells.push(0.05+0.9*(((i*7)%13)/13));}}
  function txt(s,x,y,col,sz,al,bold){{ctx.save();ctx.font=(bold?'700 ':'')+sz+'px '+MONO;ctx.textAlign=al||'center';ctx.textBaseline='middle';ctx.fillStyle=col;ctx.fillText(s,x,y);ctx.restore();}}
  const alpha=0.86;
  function draw(t){{
    const step=RM?8:Math.floor(t/0.5);
    if(cells===null) reset();
    if(step!==tick){{ tick=step;
      if(!RM){{ for(let i=0;i<cells.length;i++) cells[i]*=alpha;          // decay all
                const j=(step*5+3)%(G*G); cells[j]=1.0; }}                 // refresh one (a new write)
    }}
    ctx.clearRect(0,0,w,h);
    const cs=Math.min(30,(h-120)/G), bw=cs*G, gx=w/2-bw/2, gy=54;
    txt('the memory page — faded a little every step',w/2,30,C.mut,12,'center');
    for(let i=0;i<G;i++)for(let j=0;j<G;j++){{
      const v=cells[i*G+j];
      ctx.save();ctx.fillStyle='rgba(227,166,58,'+Math.max(0.03,v).toFixed(3)+')';
      ctx.strokeStyle='rgba(10,15,25,.6)';ctx.lineWidth=1;
      ctx.fillRect(gx+j*cs,gy+i*cs,cs-2,cs-2);ctx.strokeRect(gx+j*cs,gy+i*cs,cs-2,cs-2);ctx.restore();
    }}
    ctx.save();ctx.strokeStyle=C.line;ctx.strokeRect(gx-5,gy-5,bw+10,bw+10);ctx.restore();
    txt('fade = '+alpha+' each step   (old writing fades to black · newest = full)',w/2,gy+bw+28,C.amber,12,'center');
    const bright=cells.filter(v=>v>0.4).length;
    const el=document.getElementById('gate-r');
    if(el) el.innerHTML='each step fades every cell to '+alpha+' of its brightness; one cell is refreshed to full. Bright (recent) cells: <b>'+bright+'</b> of '+(G*G)+' — the rest are fading away.';
  }}
  let raf,t0=performance.now();function frame(now){{draw((now-t0)/1000);raf=requestAnimationFrame(frame);}}
  const io=new IntersectionObserver(es=>es.forEach(e=>{{if(e.isIntersecting){{if(!raf){{t0=performance.now();raf=requestAnimationFrame(frame);}}}}else{{cancelAnimationFrame(raf);raf=0;}}}}),{{threshold:.12}});
  if(RM){{reset();draw(9);}} else io.observe(cv);
  let rt;addEventListener('resize',()=>{{clearTimeout(rt);rt=setTimeout(()=>{{fit();if(RM)draw(9);}},150);}});
}})();
</script>
"""
open("out/index.html", "w", encoding="utf-8").write(P)
print("wrote out/index.html ·", len(P)//1024, "KB · FFFD:", P.count("�"))
