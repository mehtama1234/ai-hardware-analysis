"""
Session 04 — Parallelizing DeltaNet: same answer, chunk-wise, fast to train.

DeltaNet (Session 03) has one practical flaw: it's SEQUENTIAL. Each step needs the
current board S to compute v_old = k·S, so you can't process a long prompt in parallel
— which makes training on GPUs slow. The fix (Yang et al.) is a chunk-wise
reparameterization: split the sequence into chunks of size C, do REAL attention inside
a chunk, carry a running state ACROSS chunks, and — crucially — compute the exact same
delta-rule output.

    inside a chunk:  masked Q·Kᵀ then ·(corrected V)   — the "score-first" order
    across chunks:   fold each chunk into the state S    — the "state-first" order

Chunk size C interpolates: C=1 is pure sequential DeltaNet, C=N is full attention.

We run into out_chunk.json:
  A. Equivalence — sequential vs chunked give the SAME output for every C (Δ≈0).
  B. Speed — chunked prefill is faster wall-clock than the sequential loop.
  C. The FLOP split — total work = a fixed state term (2·L·d²) + a growing score
     term (2·L·C·d); smaller C = fewer FLOPs, bigger C = better hardware use.

Pure torch, CPU, tiny tensors.
"""
import json, math, os, time
import torch
import torch.nn.functional as F

torch.manual_seed(0)
OUT = {}

def seq_delta(q, k, v, beta):
    """Plain sequential delta rule (the Session-03 recurrence), returns O."""
    N, d = q.shape
    S = torch.zeros(d, d); O = torch.zeros(N, d)
    for t in range(N):
        v_old = k[t] @ S
        u = beta[t] * (v[t] - v_old)
        S = S + torch.outer(k[t], u)
        O[t] = q[t] @ S
    return O

def chunk_delta(q, k, v, beta, C):
    """Chunk-wise delta rule (Yang et al.), vectorized. The per-chunk correction
    matrices T = (I + strictly-lower(Kβ Kᵀ))^{-1} are solved for ALL chunks at once
    (one batched triangular inverse); only the cross-chunk state carry stays a loop —
    and that loop is L/C long instead of L."""
    N, d = q.shape; nC = N // C
    qc = q.reshape(nC, C, d); kc = k.reshape(nC, C, d)
    vc = v.reshape(nC, C, d); bc = beta.reshape(nC, C)
    Kb = kc * bc[..., None]; Vb = vc * bc[..., None]          # (nC,C,d)
    I = torch.eye(C)
    A = (Kb @ kc.transpose(-1, -2)).tril(-1)                  # (nC,C,C) strictly lower
    T = torch.linalg.solve_triangular(I + A, I.expand(nC, C, C), upper=False)  # batched
    W = T @ Kb; U = T @ Vb                                    # (nC,C,d), all chunks parallel
    Amask = (qc @ kc.transpose(-1, -2)).tril()                # in-chunk masked scores, parallel
    S = torch.zeros(d, d); O = torch.zeros(nC, C, d)
    for i in range(nC):                                       # only L/C sequential steps
        u_i = U[i] - W[i] @ S
        O[i] = Amask[i] @ u_i + qc[i] @ S                     # o_intra + o_inter
        S = S + kc[i].T @ u_i                                 # fold chunk into state
    return O.reshape(N, d)

# ----------------------------------------------------------------------------
# A. Equivalence across chunk sizes.
# ----------------------------------------------------------------------------
N, d = 64, 32
g = torch.Generator().manual_seed(1)
q = F.normalize(F.silu(torch.randn(N, d, generator=g)), dim=-1)
k = F.normalize(F.silu(torch.randn(N, d, generator=g)), dim=-1)
v = torch.randn(N, d, generator=g)
beta = torch.sigmoid(torch.randn(N, generator=g))
ref = seq_delta(q, k, v, beta)
eq = []
for C in [1, 2, 4, 8, 16, 32, 64]:
    o = chunk_delta(q, k, v, beta, C)
    eq.append({"C": C, "max_abs_diff": float((o - ref).abs().max())})
OUT["equivalence"] = {
    "N": N, "d": d, "rows": eq,
    "point": "Every chunk size C reproduces the sequential delta rule to floating-point noise. "
             "C=1 is literally the sequential loop; C=N is one big chunk (full attention). The "
             "chunked form is not an approximation — it's the same function, re-scheduled so a GPU "
             "can do big matmuls instead of a long scalar recurrence.",
}

# ----------------------------------------------------------------------------
# B. Speed: sequential loop vs chunked prefill.
# ----------------------------------------------------------------------------
def timed(fn, reps=7):
    fn()  # warm up
    best = math.inf
    for _ in range(reps):
        t0 = time.perf_counter(); fn(); best = min(best, time.perf_counter() - t0)
    return best

CHUNK = 32
rows = []
for L in [128, 256, 512, 1024]:
    gg = torch.Generator().manual_seed(L)
    Q = F.normalize(F.silu(torch.randn(L, d, generator=gg)), dim=-1)
    K = F.normalize(F.silu(torch.randn(L, d, generator=gg)), dim=-1)
    Vv = torch.randn(L, d, generator=gg); B = torch.sigmoid(torch.randn(L, generator=gg))
    t_seq = timed(lambda: seq_delta(Q, K, Vv, B))
    t_chk = timed(lambda: chunk_delta(Q, K, Vv, B, CHUNK))
    rows.append({"L": L, "seq_depth": L, "chunk_depth": L // CHUNK, "depth_reduction": CHUNK,
                 "ms_sequential": round(t_seq*1e3, 2), "ms_chunked": round(t_chk*1e3, 2),
                 "speedup": round(t_seq/t_chk, 2)})
OUT["speed"] = {
    "d": d, "chunk_size": CHUNK, "rows": rows,
    "point": "The core win is the SEQUENTIAL DEPTH — the number of steps that must run one-after-another "
             "because each needs the previous state. Sequential DeltaNet has depth L; the chunked form has "
             "depth L/C (here 32× shorter), with all the within-chunk work as parallel matmuls. That shorter "
             "dependency chain is why it trains fast — and it shows up even here: replacing the L-step Python "
             "recurrence with L/C batched-matmul steps runs 8–20× faster on plain CPU. In production the same "
             "idea rides a fused GPU kernel (Kimi Linear's DPLR chunkwise kernel) at C≈64–128.",
}

# ----------------------------------------------------------------------------
# C. The FLOP split — why C is a knob, not a constant.
#    total ≈ 2·L·d²  (state work, independent of C)  +  2·L·C·d  (in-chunk scores).
# ----------------------------------------------------------------------------
L = 4096
split = []
for C in [1, 16, 64, 128, 512, L]:
    state = 2 * L * d * d
    score = 2 * L * C * d
    split.append({"C": C, "state_flops": state, "score_flops": score, "total": state + score,
                  "is_full_attention": C == L})
OUT["flop_split"] = {
    "L": L, "d": d, "rows": split,
    "point": "The fixed piece (2·L·d²) is the recurrent state work and ignores C entirely. The growing "
             "piece (2·L·C·d) is the little masked-attention triangles on the diagonal. C=1 minimizes "
             "FLOPs but is all tiny ops; C=L is full O(L²) attention. Kimi Linear picks C≈64–128 — big "
             "enough to fill tensor cores (its DPLR chunkwise kernel), small enough to stay near-linear.",
}

here = os.path.dirname(os.path.abspath(__file__))
json.dump(OUT, open(os.path.join(here, "out_chunk.json"), "w"), indent=2)

print("A. sequential vs chunked, max|Δ| by C:")
for r in eq:
    print(f"   C={r['C']:>3}  Δ={r['max_abs_diff']:.2e}")
print("B. prefill speed (chunk size 32):")
for r in rows:
    print(f"   L={r['L']:>4}  depth {r['seq_depth']}→{r['chunk_depth']}  |  seq {r['ms_sequential']:>7.2f}ms  chunk {r['ms_chunked']:>6.2f}ms  ({r['speedup']:.2f}×)")
print("C. FLOP split @ L=4096:")
for r in split:
    tag = " (=full attention)" if r["is_full_attention"] else ""
    print(f"   C={r['C']:>4}  state {r['state_flops']:,}  + score {r['score_flops']:,}  = {r['total']:,}{tag}")
print("wrote out_chunk.json")
