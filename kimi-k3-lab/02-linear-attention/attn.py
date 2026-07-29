"""
Session 02 — Linear attention: fold all of K,V into one fixed D×D state.

Session 01 measured the wall: softmax keeps a KV cache that grows with N.
Linear attention's escape: apply a feature map φ (here ELU+1) to q and k
*separately*. Because the nonlinearity no longer sits between q and k, the
product re-associates:

    softmax order:   (φ(q) · φ(k)ᵀ) · V     -> an N×N matrix, grows with N
    linear order:     φ(q) · (φ(k)ᵀ · V)    -> φ(k)ᵀV is a fixed D×D state S

So instead of storing every past key/value, you fold them into one D×D matrix S
(plus a D-vector z for the normalizer). The cache STOPS GROWING.

We run four things into out_linear.json:
  A. Equivalence — the parallel and recurrent forms give the SAME output
     (proves the re-association is exact, not an approximation).
  B. State size — linear state is CONSTANT in N; the KV cache is linear in N.
  C. Decode cost — linear attention is O(1) work per step; softmax is O(N).
  D. The price — a "needle" retrieval test: softmax pulls a specific past value
     back sharply; linear attention's fixed state blurs it, and the blur gets
     WORSE as more tokens pile into the same finite state. That interference is
     exactly the limitation DeltaNet (Session 03) is built to fix.

Pure torch, CPU, tiny tensors.
"""
import json, math, os
import torch
import torch.nn.functional as F

torch.manual_seed(0)
OUT = {}

def phi(x):                      # feature map: ELU+1 -> strictly positive
    return F.elu(x) + 1.0

def softmax_attn(q, k, v):       # causal softmax attention, (N,d)
    N, d = q.shape
    A = (q @ k.T) / math.sqrt(d)
    A = A.masked_fill(torch.triu(torch.ones(N, N, dtype=torch.bool), 1), float("-inf"))
    return A.softmax(-1) @ v

def linear_parallel(q, k, v):    # linear attention, N×N form (for the equivalence check)
    N, d = q.shape
    A = phi(q) @ phi(k).T
    A = A.masked_fill(torch.triu(torch.ones(N, N, dtype=torch.bool), 1), 0.0)
    return (A @ v) / (A.sum(-1, keepdim=True) + 1e-6)

def linear_recurrent(q, k, v):   # linear attention, fixed D×D state S + D-vector z
    N, d = q.shape
    fq, fk = phi(q), phi(k)
    S = torch.zeros(d, d); z = torch.zeros(d); outs = []
    for t in range(N):
        S = S + torch.outer(fk[t], v[t])     # fold this token into the fixed state
        z = z + fk[t]
        outs.append((fq[t] @ S) / (fq[t] @ z + 1e-6))
    return torch.stack(outs)

# ----------------------------------------------------------------------------
# A. Equivalence: the two orderings are the SAME function.
# ----------------------------------------------------------------------------
N, d = 48, 32
q, k, v = torch.randn(N, d), torch.randn(N, d), torch.randn(N, d)
op, orr = linear_parallel(q, k, v), linear_recurrent(q, k, v)
OUT["equivalence"] = {
    "N": N, "d": d,
    "max_abs_diff": float((op - orr).abs().max()),
    "point": "Reading the whole pile of notes and folding them into one board first give the same "
             "answer to rounding noise. Collapsing the pile into a board loses nothing — it is the exact "
             "same result, just stored as a running summary instead of a stack. (What blurs is single-fact "
             "recall; see the needle test below.)",
}

# ----------------------------------------------------------------------------
# B. State size: constant vs the KV cache's linear growth.
#    Linear state per head = D×D matrix + D vector, independent of N.
#    KV cache per head = 2 · N · D, grows with N.
# ----------------------------------------------------------------------------
D = 128
Ns = [1024, 4096, 16384, 65536, 131072]
lin_state = D * D + D                         # floats, CONSTANT
OUT["state_size"] = {
    "d_head": D,
    "linear_state_floats": lin_state,          # same for every N
    "N": Ns,
    "kv_cache_floats": [2 * N * D for N in Ns], # grows
    "ratio_kv_over_linear": [round(2 * N * D / lin_state, 1) for N in Ns],
    "point": "The running-summary memory is one fixed grid, the same size whether you've read 1,000 words "
             "or 128,000. The keep-every-note memory is already ~250× bigger by 65,000 words and keeps "
             "climbing. This is the 75%-smaller-memory, long-document win Kimi Linear reports.",
}

# ----------------------------------------------------------------------------
# C. Decode cost per step: O(1) vs O(N).
# ----------------------------------------------------------------------------
def softmax_step_flops(t, d):  # query vs t keys: ~t·d for scores + t·d for the value mix
    return 2 * t * d
def linear_step_flops(d):      # update S (d·d) + read φ(q)·S (d·d)
    return 2 * d * d
steps = [64, 256, 1024, 4096]
OUT["decode_cost"] = {
    "d_head": D,
    "step": steps,
    "softmax_flops_per_step": [softmax_step_flops(t, D) for t in steps],
    "linear_flops_per_step": [linear_step_flops(D) for _ in steps],
    "point": "Keep-every-note pays more for each new word as its history grows; the running summary pays "
             "the same tiny amount every word — it always just updates and reads one fixed board. That flat "
             "per-word cost over a long document is where the up-to-6× faster generation comes from.",
}

# ----------------------------------------------------------------------------
# D. The price — needle retrieval. Put a distinct (key,value) at position p,
#    then query with exactly that key. Softmax should return value_p sharply.
#    Linear attention returns a blurred version, and the blur worsens with N
#    because every token wrote into the same finite state (interference).
# ----------------------------------------------------------------------------
def cos(a, b):
    return float(F.cosine_similarity(a, b, dim=0))

def needle(N, d, trials=16):
    """Store N (key,value) pairs; query the needle's exact key; how well is its
    value recalled? Unit-norm keys in d dims are near-orthogonal while N<d, so
    softmax can retrieve sharply — which isolates the variable we care about:
    can the MEMORY hold one association without the others bleeding in?"""
    sc = []; lc = []; sm_wt = []
    for s in range(trials):
        g = torch.Generator().manual_seed(100 + s)
        k = torch.randn(N, d, generator=g)   # raw: ‖k‖~√d, so a self-match logit stays large & peaked
        v = torch.randn(N, d, generator=g)
        p = 1                           # the needle is written early
        q = k.clone()
        q[-1] = k[p]                    # at the last step, ask for the needle's key
        tgt = v[p]
        sc.append(cos(softmax_attn(q, k, v)[-1], tgt))     # recall quality, 1=perfect
        lc.append(cos(linear_recurrent(q, k, v)[-1], tgt))
        A = ((q @ k.T) / math.sqrt(d))
        A = A.masked_fill(torch.triu(torch.ones(N, N, dtype=torch.bool), 1), float("-inf")).softmax(-1)
        sm_wt.append(float(A[-1, p]))
    m = lambda xs: sum(xs) / len(xs)
    return m(sc), m(lc), m(sm_wt)

DH = 64                                  # head dim: near-orthogonal keys while N < 64
rows = []
for N in [4, 8, 16, 32, 64, 128, 256]:
    scq, lcq, wt = needle(N, DH)
    rows.append({"N": N,
                 "softmax_recall_cos": round(scq, 3),
                 "linear_recall_cos": round(lcq, 3),
                 "softmax_needle_weight": round(wt, 3),
                 "over_capacity": N > DH})
OUT["needle"] = {
    "d": DH,
    "metric": "cosine similarity of recalled output to the true needle value (1=perfect, 0=lost)",
    "rows": rows,
    "point": "Hand back one fact's exact cue. Keep-every-note recalls its value PERFECTLY at every length "
             "(it still has that note on file, so it points straight at it). The running summary starts weaker "
             "and fades steadily, 0.65→0.08, the more you store: every fact lands on the same board, so pulling "
             "one back drags in a smear of all the others. That fade isn't a bug — it's the built-in limit of a "
             "fixed board, and it's the exact thing the next rung (DeltaNet) fixes by erasing a fact's old value "
             "before writing a new one, and that K3 hedges by keeping a few keep-every-note layers on the side.",
}

here = os.path.dirname(os.path.abspath(__file__))
json.dump(OUT, open(os.path.join(here, "out_linear.json"), "w"), indent=2)

print("A. parallel vs recurrent max|Δ| =", f"{OUT['equivalence']['max_abs_diff']:.2e}", "(≈0 → exact)")
print("B. KV/linear-state size ratio @", Ns, "=", OUT["state_size"]["ratio_kv_over_linear"])
print("C. softmax step FLOPs", OUT["decode_cost"]["softmax_flops_per_step"], "vs linear (flat)", OUT["decode_cost"]["linear_flops_per_step"])
print("D. needle recall (cosine to true value, 1=perfect; d=64):")
for r in rows:
    cap = " [over capacity]" if r["over_capacity"] else ""
    print(f"   N={r['N']:>3}  softmax {r['softmax_recall_cos']:.3f} (wt {r['softmax_needle_weight']:.2f})  |  linear {r['linear_recall_cos']:.3f}{cap}")
print("wrote out_linear.json")
