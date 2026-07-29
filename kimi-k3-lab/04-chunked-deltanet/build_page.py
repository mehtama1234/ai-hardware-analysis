import json, html
D = json.load(open("out_chunk.json"))
EQ = D["equivalence"]; SP = D["speed"]; FS = D["flop_split"]
def esc(s): return html.escape(str(s))

def eqrows():
    return "".join(f"<tr><td>{r['C']}</td><td class='hi'>{r['max_abs_diff']:.1e}</td>"
                   f"<td class='mo'>{'one word at a time' if r['C']==1 else ('whole text in one block' if r['C']==EQ['N'] else 'in blocks')}</td></tr>"
                   for r in EQ["rows"])

def speedrows():
    return "".join(f"<tr><td>{r['L']}</td><td class='mo'>{r['seq_depth']} → {r['chunk_depth']}</td>"
                   f"<td class='hi'>{r['depth_reduction']}×</td>"
                   f"<td class='mo'>{r['ms_sequential']:.1f}</td><td class='mo'>{r['ms_chunked']:.1f}</td>"
                   f"<td class='hi'>{r['speedup']:.1f}×</td></tr>" for r in SP["rows"])

def flopbars():
    mx = max(r["total"] for r in FS["rows"])
    out = ""
    for r in FS["rows"]:
        sp = r["state_flops"]/mx*100; scp = r["score_flops"]/mx*100
        tag = " = whole text" if r["is_full_attention"] else ""
        out += (f"<div class='fbar'><span class='fl'>block {r['C']}{tag}</span>"
                f"<span class='ft'><span class='ff st' style='width:{sp:.2f}%'></span>"
                f"<span class='ff sc' style='width:{scp:.2f}%'></span></span>"
                f"<span class='fv'>{r['total']/1e6:.1f}M</span></div>")
    return out

P = f"""<title>Kimi K3 Lab · 04 — Chunked DeltaNet</title>
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
.eqn{{font-family:var(--mono);font-size:13.5px;color:var(--ink);background:#0C1119;border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin:14px 0;overflow-x:auto;white-space:pre;line-height:1.7}}
.eqn .c{{color:var(--accent)}}.eqn .g{{color:var(--faint)}}.eqn .v{{color:var(--viol)}}
table{{width:100%;border-collapse:collapse;margin-top:8px;font-size:13.5px}}
th,td{{padding:8px 10px;text-align:right;border-bottom:1px solid var(--line)}}
th{{font-family:var(--mono);font-size:10.5px;letter-spacing:.06em;text-transform:uppercase;color:var(--dim);font-weight:600}}
td.mo{{font-family:var(--mono);color:var(--soft)}}td.hi{{font-family:var(--mono);color:var(--accent);font-weight:700}}
th:first-child,td:first-child{{text-align:left;color:var(--ink);font-family:var(--mono)}}
.fbar{{display:flex;align-items:center;gap:12px;margin:8px 0;font-family:var(--mono);font-size:12px}}
.fl{{width:120px;color:var(--dim);text-align:right}}
.ft{{flex:1;height:18px;background:rgba(150,170,205,.06);border-radius:5px;overflow:hidden;display:flex}}
.ff{{display:block;height:100%}}.ff.st{{background:#2E6E7A}}.ff.sc{{background:#E3A63A}}
.fv{{width:66px;color:var(--soft)}}
.leg{{font-family:var(--mono);font-size:11px;color:var(--faint);margin-top:6px}}
.leg .sw{{display:inline-block;width:10px;height:10px;border-radius:2px;vertical-align:middle;margin:0 4px 0 12px}}
.panel{{background:linear-gradient(180deg,#10161D,#0D131A);border:1px solid var(--line);border-radius:14px;padding:8px;margin-top:14px;overflow:hidden}}
.panel canvas{{display:block;width:100%;height:auto;border-radius:8px}}
.readout{{font-family:var(--mono);font-size:12px;color:var(--dim);padding:9px 12px 4px;min-height:18px}}.readout b{{color:var(--accent)}}
.aha{{font-family:var(--serif);font-size:22px;line-height:1.4;color:#fff;border-left:3px solid var(--accent);padding-left:18px;margin:8px 0}}
.next{{font-family:var(--mono);font-size:13px;color:var(--dim);margin-top:10px}}.next a{{color:var(--accent);text-decoration:none}}
.src{{font-family:var(--mono);font-size:12px;color:var(--faint);margin-top:28px;padding-top:16px;border-top:1px solid var(--line)}}.src a{{color:var(--accent);text-decoration:none}}
</style>
<div class="wrap">
<header style="padding:64px 0 8px">
  <div class="kick">Kimi K3, from first principles · Session 04 of 07</div>
  <h1>The same work — done in parallel.</h1>
  <p class="dek">The last rung gave our model a memory it can correct in place — but it has to do that <em>one word at a time</em>, each step waiting on the one before it. On long text, that waiting makes training painfully slow. This rung changes <b>nothing about the answer</b> and everything about the speed: it reorganizes the very same work so a computer can do it in big parallel batches instead of a single-file line.</p>
  <div class="run"><div class="rt">▶ We ran it · the headline</div>
  <p>The one-at-a-time version and the batched version give the <b>same answer</b> (they differ by about <b>{max(r['max_abs_diff'] for r in EQ['rows']):.0e}</b> — pure rounding). The batched version shortens the chain of steps that must wait for each other by about <b>{SP['rows'][0]['depth_reduction']}×</b>, and ran <b>{SP['rows'][2]['speedup']:.0f}×</b> faster even on an ordinary computer.</p></div>
</header>

<section>
  <div class="eye">The idea · careful work in blocks, a summary between them</div>
  <h2>Do the bookkeeping inside a block, pass a summary between blocks</h2>
  <p>Split the text into blocks of, say, a few dozen words. <b>Inside</b> a block, do the full careful bookkeeping among just those words — and because it's a small, self-contained group, a computer can do it all at once. <b>Between</b> blocks, fold the finished block into a short running <span class="mono">summary</span> and read that summary at the start of the next block. The only thing that still has to happen in order is block-to-block, so the chain of must-wait steps drops from one-per-word to one-per-block:</p>
  <div class="eqn"><span class="g"># for each block, computed in one parallel burst:</span>
corrections = this block's fixes, given the <span class="v">summary</span> handed in
inside      = careful bookkeeping among the words in THIS block (all at once)
carried-in  = what everything before the block contributes, read from the <span class="v">summary</span>
output      = inside + carried-in
<span class="v">summary</span>     = <span class="v">summary</span> + this block folded in      <span class="g"># handed to the next block</span></div>
  <p>The one clever step is working out a block's corrections in a single shot instead of word by word — a small, self-contained calculation we can run for every block at the same time. After that, only the summary hand-off from one block to the next stays a loop.</p>
</section>

<section>
  <div class="eye">We ran it · it's the same function</div>
  <h2>Every block size gives the same answer</h2>
  <p>We ran the plain one-word-at-a-time version and the in-blocks version on the same input, sweeping the block size from a single word (which is just the one-at-a-time version) up to the whole text in one block. The biggest disagreement anywhere is rounding noise:</p>
  <div class="card" style="overflow-x:auto"><table>
    <tr><th>block size</th><th>difference from one-at-a-time</th><th>what this size means</th></tr>
    {eqrows()}
  </table></div>
  <p class="mini">{esc(EQ['point'])}</p>
</section>

<section>
  <div class="eye">We ran it · the parallel win</div>
  <h2>The chain of must-wait steps shrinks with block size</h2>
  <p>The number that actually matters for training is how many steps must run one-after-another because each needs the result of the one before. Working in blocks cuts that chain from one-per-word to one-per-block — and even in plain Python on an ordinary computer, swapping the long word-by-word loop for a few block-sized batches ran several times faster:</p>
  <div class="card" style="overflow-x:auto"><table>
    <tr><th>text length</th><th>must-wait steps: word-by-word → in-blocks</th><th>shorter by</th><th>ms word-by-word</th><th>ms in-blocks</th><th>faster by</th></tr>
    {speedrows()}
  </table></div>
  <p class="mini">{esc(SP['point'])}</p>
</section>

<section>
  <div class="eye">We ran it · why C is a knob</div>
  <h2>One fixed cost, plus a cost that grows with block size</h2>
  <p>The total work splits in two. One part is <span style="color:#4FA8B8">fixed</span> — the running-summary bookkeeping — and doesn't care how big the blocks are. The other part is the <span style="color:var(--amber)">careful within-block work</span>, and it grows with the block size. So block size is a dial: tiny blocks do the least total work but in many small steps; a single block the size of the whole text is the old, expensive everything-compared-to-everything again:</p>
  <div class="card">{flopbars()}
  <div class="leg"><span class="sw" style="background:#2E6E7A"></span>fixed summary work<span class="sw" style="background:#E3A63A"></span>within-block work (grows with block size)</div></div>
  <p class="mini">{esc(FS['point'])}</p>
</section>

<section>
  <div class="eye">See it · chunked prefill</div>
  <h2>Blocks fill in parallel; the summary passes along</h2>
  <p>The text laid out in blocks. Inside each block, all the careful work lights up at once (in parallel). Between blocks, the running <span style="color:var(--viol)">summary</span> is handed forward — the one thread that still has to happen in order:</p>
  <div class="panel"><canvas data-anim="chunk" height="280"></canvas>
    <div class="readout"><span id="chunk-r">—</span></div>
  </div>
  <p class="mini">Left-to-right = the text. Each block does its full internal bookkeeping on its own; the glowing summary carries what's been learned so far across the block boundaries.</p>
</section>

<section>
  <div class="eye">The one-line takeaway</div>
  <p class="aha">Cut the text into blocks, do the exact same careful work inside each and pass a running summary between them, and the one-step-at-a-time chain collapses from one link per word to one per block — the same answer, now shaped like something a computer can train on fast.</p>
  <p class="next">Real code: <b>04-chunked-deltanet/attn.py</b> → <b>out_chunk.json</b> · Source: ali's worklog, on doing the delta rule in parallel blocks.<br>
  Next → <b>Session 05</b>: the memory can correct a fact it recognizes, but it can't clear itself for a brand-new topic. Add a dial that lets old material fade so it can forget on purpose.</p>
</section>
<div class="src">Companion to ali (@waterloo_intern), <a href="https://x.com/waterloo_intern/status/2081762065392541951">"22580"</a>; production algorithm from Moonshot's <a href="https://arxiv.org/abs/2510.26692">Kimi Linear</a> (DPLR). Numbers produced by the code.</div>
</div>
<script>
(function(){{
  const R={json.dumps(SP['rows'])};
  const RM=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
  const MONO='ui-monospace,Menlo,Consolas,monospace';
  const C={{accent:'#4FA8B8',amber:'#E3A63A',rose:'#E0748A',viol:'#9B8CE0',ink:'#E7EFF1',mut:'#8B9BA2',dim:'#586770',line:'#243440'}};
  const cv=document.querySelector('canvas[data-anim=chunk]'); if(!cv)return;
  let ctx,w,h; const NCH=4, CS=4; // 4 chunks of 4 tokens
  function fit(){{const dpr=Math.min(devicePixelRatio||1,2);w=cv.clientWidth;h=parseInt(cv.getAttribute('height'))||280;
    cv.width=w*dpr;cv.height=h*dpr;ctx=cv.getContext('2d');ctx.setTransform(dpr,0,0,dpr,0,0);}}
  fit();
  function txt(s,x,y,col,sz,al,bold){{ctx.save();ctx.font=(bold?'700 ':'')+sz+'px '+MONO;ctx.textAlign=al||'center';ctx.textBaseline='middle';ctx.fillStyle=col;ctx.fillText(s,x,y);ctx.restore();}}
  function draw(t){{
    ctx.clearRect(0,0,w,h);
    const per=RM?0:0.85; const active=RM?NCH-1:Math.floor(t/per)%(NCH+1);
    const marg=40, gap=18, cw=(w-2*marg-(NCH-1)*gap)/NCH, cell=Math.min(15,(cw-8)/CS), gy=70;
    txt('the text  →',marg,28,C.dim,12,'left');
    let sx=marg;
    for(let i=0;i<NCH;i++){{
      const done=i<active, cur=i===active;
      // chunk frame
      ctx.save();ctx.strokeStyle=cur?C.accent:(done?'rgba(79,168,184,.4)':C.line);ctx.lineWidth=cur?1.8:1.2;
      ctx.strokeRect(sx, gy, cw, cw); ctx.restore();
      // in-chunk masked-attention triangle (lower-tri cells)
      const bx=sx+(cw-cell*CS)/2, by=gy+(cw-cell*CS)/2;
      for(let r=0;r<CS;r++)for(let cc=0;cc<CS;cc++){{
        if(cc>r) continue;
        const lit=done||cur; const v=lit?(0.25+0.6*((r*3+cc*5)%7)/7):0.05;
        ctx.save();ctx.fillStyle='rgba(79,168,184,'+v.toFixed(3)+')';ctx.strokeStyle='rgba(10,15,25,.6)';ctx.lineWidth=.8;
        ctx.fillRect(bx+cc*cell,by+r*cell,cell-1.5,cell-1.5);ctx.strokeRect(bx+cc*cell,by+r*cell,cell-1.5,cell-1.5);ctx.restore();
      }}
      txt('block '+(i+1),sx+cw/2,gy+cw+16,cur?C.accent:C.mut,11,'center',cur);
      // state hand-off arrow from prev chunk
      if(i>0){{const ax=sx-gap, ay=gy+cw/2; const on=i<=active;
        ctx.save();ctx.globalAlpha=on?1:0.25;ctx.strokeStyle=C.viol;ctx.fillStyle=C.viol;ctx.lineWidth=2;
        ctx.beginPath();ctx.moveTo(ax-gap+6,ay);ctx.lineTo(ax+4,ay);ctx.stroke();
        ctx.beginPath();ctx.moveTo(ax+4,ay);ctx.lineTo(ax-2,ay-4);ctx.lineTo(ax-2,ay+4);ctx.closePath();ctx.fill();ctx.restore();
        if(on) txt('S',ax-gap/2,ay-10,C.viol,10,'center',true);
      }}
      sx+=cw+gap;
    }}
    txt('inside a block: all the careful work, at once (in parallel)',w/2,h-42,C.mut,11,'center');
    txt('between blocks: the summary passes along (in order — only '+NCH+' links, not '+(NCH*CS)+')',w/2,h-24,C.viol,11,'center');
    const el=document.getElementById('chunk-r');
    if(el) el.innerHTML='block '+Math.min(active+1,NCH)+' of '+NCH+' — its internal work computes in parallel; the <b>summary</b> carries what has been learned to the next. Must-wait links = '+NCH+', not '+(NCH*CS)+'.';
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
