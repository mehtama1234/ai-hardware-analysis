import json, html
D = json.load(open("out_delta.json"))
OW = D["overwrite"]; ND = D["needle"]
def esc(s): return html.escape(str(s))

# overwrite bars: 3 methods x (new v2, old v1)
def owbars():
    order = [("deltanet", "DeltaNet"), ("softmax", "Softmax"), ("linear", "Linear")]
    out = ""
    for key, label in order:
        r = OW["results"][key]
        nv = max(0.0, r["cos_to_new_v2"]); ov = max(0.0, r["cos_to_old_v1"])
        out += (f"<div class='owrow'><div class='owl'>{label}</div>"
                f"<div class='owbars'>"
                f"<div class='owb'><span class='owt new'>new v2</span><span class='owtrack'><span class='owf new' style='width:{nv*100:.0f}%'></span></span><span class='owv'>{r['cos_to_new_v2']:+.2f}</span></div>"
                f"<div class='owb'><span class='owt old'>old v1</span><span class='owtrack'><span class='owf old' style='width:{ov*100:.0f}%'></span></span><span class='owv'>{r['cos_to_old_v1']:+.2f}</span></div>"
                f"</div></div>")
    return out

# 3-line needle SVG
def needlesvg():
    rows = ND["rows"]; n = len(rows)
    W, H, pad = 560, 190, 30
    X = lambda i: pad + (W-2*pad)*i/(n-1)
    Y = lambda v: H-pad - (H-2*pad)*max(0, min(1, v))
    def line(key, col):
        pts = "M" + " L".join(f"{X(i):.1f},{Y(r[key]):.1f}" for i, r in enumerate(rows))
        dots = "".join(f"<circle cx='{X(i):.1f}' cy='{Y(r[key]):.1f}' r='2.6' fill='{col}'/>" for i, r in enumerate(rows))
        return f"<path d='{pts}' fill='none' stroke='{col}' stroke-width='2'/>{dots}"
    grid = "".join(f"<line x1='{pad}' y1='{Y(g):.1f}' x2='{W-pad}' y2='{Y(g):.1f}' stroke='rgba(150,170,205,.10)'/>"
                   f"<text x='{pad-6}' y='{Y(g)+3:.1f}' fill='#5A6577' font-size='9' text-anchor='end' font-family=\"ui-monospace,monospace\">{g:.1f}</text>" for g in (0, 0.5, 1.0))
    xl = "".join(f"<text x='{X(i):.1f}' y='{H-8}' fill='#5A6577' font-size='10' text-anchor='middle' font-family=\"ui-monospace,monospace\">{r['N']}</text>" for i, r in enumerate(rows))
    leg = ("<text x='%.0f' y='18' fill='#4FA8B8' font-size='11' text-anchor='end' font-family=\"ui-monospace,monospace\">softmax</text>"
           "<text x='%.0f' y='34' fill='#9B8CE0' font-size='11' text-anchor='end' font-family=\"ui-monospace,monospace\">deltanet</text>"
           "<text x='%.0f' y='50' fill='#E0748A' font-size='11' text-anchor='end' font-family=\"ui-monospace,monospace\">linear</text>") % (W-pad, W-pad, W-pad)
    return (f"<svg viewBox='0 0 {W} {H}' style='width:100%;height:auto'>{grid}"
            f"{line('linear','#E0748A')}{line('deltanet','#9B8CE0')}{line('softmax','#4FA8B8')}{xl}{leg}</svg>")

DN = OW["results"]["deltanet"]; SM = OW["results"]["softmax"]

P = f"""<title>Kimi K3 Lab · 03 — DeltaNet</title>
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
.eqn .c{{color:var(--accent)}}.eqn .g{{color:var(--faint)}}.eqn .r{{color:var(--rose)}}
.owrow{{display:flex;gap:14px;align-items:center;margin:14px 0}}
.owl{{width:78px;font-family:var(--serif);font-size:17px;color:#fff;flex:0 0 auto}}
.owbars{{flex:1;display:flex;flex-direction:column;gap:6px}}
.owb{{display:flex;align-items:center;gap:10px;font-family:var(--mono);font-size:11.5px}}
.owt{{width:44px;color:var(--dim)}}.owt.new{{color:var(--accent)}}.owt.old{{color:var(--rose)}}
.owtrack{{flex:1;height:14px;background:rgba(150,170,205,.06);border-radius:4px;overflow:hidden}}
.owf{{display:block;height:100%}}.owf.new{{background:linear-gradient(90deg,#2E6E7A,#4FA8B8)}}.owf.old{{background:linear-gradient(90deg,#7a3540,#E0748A)}}
.owv{{width:48px;color:var(--soft)}}
.panel{{background:linear-gradient(180deg,#10161D,#0D131A);border:1px solid var(--line);border-radius:14px;padding:8px;margin-top:14px;overflow:hidden}}
.panel canvas{{display:block;width:100%;height:auto;border-radius:8px}}
.readout{{font-family:var(--mono);font-size:12px;color:var(--dim);padding:9px 12px 4px;min-height:18px}}.readout b{{color:var(--accent)}}
.aha{{font-family:var(--serif);font-size:22px;line-height:1.4;color:#fff;border-left:3px solid var(--accent);padding-left:18px;margin:8px 0}}
.next{{font-family:var(--mono);font-size:13px;color:var(--dim);margin-top:10px}}.next a{{color:var(--accent);text-decoration:none}}
.src{{font-family:var(--mono);font-size:12px;color:var(--faint);margin-top:28px;padding-top:16px;border-top:1px solid var(--line)}}.src a{{color:var(--accent);text-decoration:none}}
</style>
<div class="wrap">
<header style="padding:64px 0 8px">
  <div class="kick">Kimi K3, from first principles · Session 03 of 07</div>
  <h1>Don't pile on. Overwrite.</h1>
  <p class="dek">By this point our model keeps its whole memory as one fixed-size page — a running summary it writes each new fact onto, so the memory never grows. Useful, but it has a real weakness: because it only ever <em>adds</em>, writing the same thing twice leaves a blur of both. This rung teaches it a smarter move — to <b>rub out the old version of a fact before writing the new one</b> — turning a memory it could only pile onto into one it can actually correct.</p>
  <div class="run"><div class="rt">▶ We ran it · overwrite the same key twice</div>
  <p>File one answer under a label, then later file a <b>different</b> answer under the same label, and ask for it. The erase-first method returns the new answer cleanly — a <b>{DN['cos_to_new_v2']:+.2f}</b> match to it, only <b>{DN['cos_to_old_v1']:+.2f}</b> to the stale one it let go. The old add-only method kept both copies and hands back a blurred average ({SM['cos_to_new_v2']:+.2f} and {SM['cos_to_old_v1']:+.2f}, nearly the same) — it can't update, only accumulate.</p></div>
</header>

<section>
  <div class="eye">The rule · read, subtract, write</div>
  <h2>A finite board needs an eviction policy</h2>
  <p>Once memory is a fixed board, you can't keep adding forever — at some point new facts have to <em>take the place of</em> old ones. DeltaNet makes that explicit. For each token it treats the key as an address, reads what's there, and writes only the difference:</p>
  <div class="eqn"><span class="g"># plain linear attention — blind addition</span>
S = S + kᵀ v

<span class="g"># DeltaNet — read the address first, write only the delta</span>
v_old = <span class="c">k · S</span>            <span class="g"># what the board already says at key k</span>
u     = β ( v − <span class="r">v_old</span> )   <span class="g"># the correction: only what's new (β = write strength)</span>
S     = S + kᵀ <span class="c">u</span>          <span class="g"># same outer-product write, but of the delta</span></div>
  <p>If you write the same key again, <span class="mono">v_old</span> is the value you stored last time — so the subtraction cancels it and you're left holding just the new value. Old information is removed and new information is written in its place. <span class="mono">β</span> (a learned, per-token write strength) controls how forcefully; β=1 is a full replace.</p>
</section>

<section>
  <div class="eye">We ran it · update vs accumulate</div>
  <h2>Only DeltaNet actually updates a fact</h2>
  <p>The same overwrite experiment, all three mechanisms side by side. Blue = how much the recalled value resembles the <b>new</b> v2; red = how much it still resembles the <b>stale</b> v1. You want tall blue, no red:</p>
  <div class="card">{owbars()}</div>
  <p class="mini">{esc(OW['point'])}</p>
</section>

<section>
  <div class="eye">We ran it · does it also fix the blur?</div>
  <h2>Recall holds up far longer — but a single board still saturates</h2>
  <p>Back to Session 02's needle test (store N pairs, query one by its exact key), now with DeltaNet added. Subtracting-before-writing keeps correlated writes from stacking into a blur, so DeltaNet recalls <em>much</em> better than plain linear while the board isn't overfull:</p>
  <div class="card">{needlesvg()}
  <div class="mini" style="margin-top:6px">x = number of stored tokens N. <span style="color:var(--accent)">softmax</span> keeps every note (flat ~1.0); <span style="color:var(--viol)">deltanet</span> holds high then falls as the fixed board saturates; <span style="color:var(--rose)">linear</span> fades from the start.</div></div>
  <div class="why"><h3>The honest catch — and why the next rungs exist</h3><p>DeltaNet delays the blur but doesn't abolish it: one D×D board has finite capacity, so past ~d writes even DeltaNet's recall collapses (with a hard β=1 it can even churn the needle out entirely). It can replace a fact it has an address for, but it can't <em>fade the board generally</em> for a new topic. Those two gaps — needing to forget broadly, and needing finer control — are precisely what <b>gating</b> (Session 05) and <b>per-channel decay</b> (Session 06) add, and why K3 keeps a few full-attention layers on the side.</p></div>
</section>

<section>
  <div class="eye">See it · erase-then-write</div>
  <h2>The delta, drawn</h2>
  <p>Watch a repeated key. Linear (left) drops a second copy next to the first — two blobs, blurred readout. DeltaNet (right) first dims the old cell, then writes the new value into the same slot — one clean value:</p>
  <div class="panel"><canvas data-anim="delta" height="290"></canvas>
    <div class="readout"><span id="delta-r">—</span></div>
  </div>
  <p class="mini">Same address written twice. Addition keeps both (and averages on read); the delta rule evicts the old before writing the new.</p>
</section>

<section>
  <div class="eye">The one-line aha</div>
  <p class="aha">Reading a key's old value and subtracting it before you write turns a fixed board from an ever-blurrier sum into a memory you can actually <em>edit</em> — the difference between averaging two answers and correcting one.</p>
  <p class="next">Real code: <b>03-deltanet/attn.py</b> → <b>out_delta.json</b> · Source: ali §DeltaNet / Fast Weight Programmers (Schlag).<br>
  Next → <b>Session 04 · Parallelizing DeltaNet</b>: the delta rule is sequential (each step needs the current board) — a chunk-wise reparameterization makes it train fast on GPUs while computing the exact same thing.</p>
</section>
<div class="src">Companion to ali (@waterloo_intern), <a href="https://x.com/waterloo_intern/status/2081762065392541951">"22580"</a>. Numbers on this page are produced by the code, not transcribed.</div>
</div>
<script>
(function(){{
  const RM=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
  const MONO='ui-monospace,Menlo,Consolas,monospace';
  const C={{accent:'#4FA8B8',amber:'#E3A63A',rose:'#E0748A',viol:'#9B8CE0',ink:'#E7EFF1',mut:'#8B9BA2',dim:'#586770',line:'#243440'}};
  const cv=document.querySelector('canvas[data-anim=delta]'); if(!cv)return;
  let ctx,w,h;
  function fit(){{const dpr=Math.min(devicePixelRatio||1,2);w=cv.clientWidth;h=parseInt(cv.getAttribute('height'))||290;
    cv.width=w*dpr;cv.height=h*dpr;ctx=cv.getContext('2d');ctx.setTransform(dpr,0,0,dpr,0,0);}}
  fit();
  function txt(s,x,y,col,sz,al,bold){{ctx.save();ctx.font=(bold?'700 ':'')+sz+'px '+MONO;ctx.textAlign=al||'center';ctx.textBaseline='middle';ctx.fillStyle=col;ctx.fillText(s,x,y);ctx.restore();}}
  function slot(cx,cy,glow,col,label,alpha){{ctx.save();ctx.globalAlpha=alpha==null?1:alpha;
    ctx.shadowColor=col;ctx.shadowBlur=glow;ctx.strokeStyle=col;ctx.fillStyle=col.replace('rgb','rgba').replace(')',',.16)');
    ctx.lineWidth=1.6;const s=44,r=8,x=cx-s/2,y=cy-s/2;
    ctx.beginPath();ctx.moveTo(x+r,y);ctx.arcTo(x+s,y,x+s,y+s,r);ctx.arcTo(x+s,y+s,x,y+s,r);ctx.arcTo(x,y+s,x,y,r);ctx.arcTo(x,y,x+s,y,r);ctx.closePath();ctx.fill();ctx.stroke();ctx.restore();
    if(label) txt(label,cx,cy,'#fff',12,'center',true);}}
  const rose='rgb(224,116,138)',acc='rgb(79,168,184)',viol='rgb(155,140,224)';
  function draw(t){{
    ctx.clearRect(0,0,w,h);
    const per=RM?0:1.1, ph=RM?0.9:((t/per)%4)/4; // 0..1 across a 4-beat cycle
    const lc=w*0.27, rc=w*0.73, cy=h*0.46;
    txt('linear — add a second copy',lc,26,C.rose,12.5,'center',true);
    txt('DeltaNet — evict, then write',rc,26,C.viol,12.5,'center',true);
    // beat structure: write v1 (0-.25), write v2 same key (.25-.6), read (.6-1)
    const wrote1=ph>0.12, wrote2=ph>0.30, reading=ph>0.62;
    // LINEAR: two blobs appear and stay
    slot(lc-30,cy, wrote1?10:0, rose, 'v1', wrote1?1:0.15);
    slot(lc+30,cy, wrote2?10:0, rose, 'v2', wrote2?1:0.15);
    if(reading) txt('read → (v1+v2)/2  blurred',lc,cy+52,C.rose,11,'center');
    // DELTA: one slot; v1 then dims as v2 replaces
    let dimOld = wrote2? Math.min(1,(ph-0.30)/0.22):0; // 0..1 erase progress
    const showV2 = wrote2;
    if(!showV2){{ slot(rc,cy, wrote1?12:0, viol, 'v1', wrote1?1:0.15); }}
    else {{
      slot(rc,cy, 12, viol, '', 1);
      // crossfade label v1 -> v2
      ctx.save();ctx.globalAlpha=1-dimOld;txt('v1',rc,cy,'#fff',12,'center',true);ctx.restore();
      ctx.save();ctx.globalAlpha=dimOld;txt('v2',rc,cy,'#fff',12,'center',true);ctx.restore();
      if(dimOld>0.1&&dimOld<0.98) txt('− old, + new',rc,cy+40,C.viol,10.5,'center');
    }}
    if(reading) txt('read → v2  clean',rc,cy+52,C.accent,11,'center');
    const el=document.getElementById('delta-r');
    if(el){{ let msg = !wrote1?'writing v1 at key k…' : !wrote2?'now writing v2 at the SAME key k…' : reading? 'read k: linear returns the average of v1,v2; DeltaNet returns v2.' : 'DeltaNet subtracts the old v1, writes v2 in its place…';
      el.innerHTML=msg; }}
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
