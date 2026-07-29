"""
Session 01 — The softmax baseline (GPT-2) and the KV-cache wall.

Everything after GPT-2 in the ali worklog is a reaction to ONE fact measured here:
the KV cache grows linearly with sequence length, and softmax decoding either
re-does O(N^2) work or pays that growing O(N) memory-bandwidth cost every step.

We don't assert this — we run it and record the real numbers into out_softmax.json:

  A. Real causal softmax attention weights on a tiny sequence (the mechanism).
  B. KV-cache size vs N, for GPT-2 (124M) and for a K3-scale config — real bytes.
  C. No-cache vs KV-cache decoding: wall-clock + FLOP counts, showing O(N^2) vs O(N).
  D. The 22,580x framing: GPT-2 param math vs Kimi K3's 2.8T.

Pure torch, CPU, tiny tensors — the *scaling shape* is architecture, not weights,
so a random-init module measures it honestly.
"""
import json, math, time, os
import torch
import torch.nn.functional as F

torch.manual_seed(0)
OUT = {}

# ----------------------------------------------------------------------------
# A. Real causal softmax attention — the GPT-2 mechanism, one head, tiny seq.
#    We show the actual post-softmax weight matrix (lower-triangular by the mask).
# ----------------------------------------------------------------------------
def causal_softmax_attn(q, k, v):
    # q,k,v: (T, d)
    T, d = q.shape
    att = (q @ k.transpose(-2, -1)) / math.sqrt(d)          # (T,T) scores
    mask = torch.triu(torch.ones(T, T, dtype=torch.bool), diagonal=1)
    att = att.masked_fill(mask, float("-inf"))
    att = F.softmax(att, dim=-1)                            # rows sum to 1
    return att @ v, att

T, d = 6, 16
q = torch.randn(T, d); k = torch.randn(T, d); v = torch.randn(T, d)
_, att = causal_softmax_attn(q, k, v)
OUT["attn_demo"] = {
    "T": T, "d_head": d,
    "weights": [[round(float(x), 4) for x in row] for row in att],
    "row_sums": [round(float(r.sum()), 4) for r in att],   # all 1.0 -> softmax is a normalized read
    "note": "Only the lower triangle is filled: each word can read itself and the words before it, never after. "
            "Each row's weights are shares of a whole, so they add up to 1.",
}

# ----------------------------------------------------------------------------
# B. KV cache size vs sequence length — the thing that GROWS.
#    bytes = 2 (K and V) * n_layer * n_head * d_head * N * bytes_per_elem
# ----------------------------------------------------------------------------
def kv_cache_bytes(N, n_layer, n_head, d_head, bytes_per=2):   # bf16 = 2 bytes
    return 2 * n_layer * n_head * d_head * N * bytes_per

# GPT-2 124M config (from the thread): 12 layers, 12 heads, d=768 -> d_head 64
gpt2 = dict(n_layer=12, n_head=12, d_head=64)
# A K3-scale attention config for illustration (large model, long context).
k3ish = dict(n_layer=61, n_head=64, d_head=128)

Ns = [1024, 4096, 16384, 65536, 131072]
OUT["kv_growth"] = {
    "formula": "bytes = 2 * n_layer * n_head * d_head * N * 2(bf16)",
    "gpt2_config": gpt2, "k3ish_config": k3ish,
    "N": Ns,
    "gpt2_MB":  [round(kv_cache_bytes(N, **gpt2)  / 1e6, 2) for N in Ns],
    "k3ish_GB": [round(kv_cache_bytes(N, **k3ish) / 1e9, 3) for N in Ns],
    "point": "The stack grows in a straight line with the amount of text. For a big model reading 128,000 words "
             "it is already tens of gigabytes — and every new word means hauling that whole pile out of memory again. "
             "That hauling is the wall; the next rung removes it by replacing the growing stack with one fixed-size summary.",
}

# ----------------------------------------------------------------------------
# C. No-cache vs KV-cache decoding — measured wall-clock + FLOPs.
#    Same math, two schedules. Without a cache, step t recomputes projections &
#    scores for all t tokens -> total work ~ sum_t t = O(N^2). With a cache, step
#    t only processes the new token against the stored past -> O(N) total.
# ----------------------------------------------------------------------------
D = 128
NH = 4
DH = D // NH
Wqkv = torch.randn(D, 3 * D) / math.sqrt(D)
Wo = torch.randn(D, D) / math.sqrt(D)

def project(x):                         # x: (t, D) -> q,k,v each (NH, t, DH)
    qkv = x @ Wqkv
    q, k, v = qkv.split(D, dim=-1)
    resh = lambda z: z.view(-1, NH, DH).transpose(0, 1)
    return resh(q), resh(k), resh(v)

def attn_block(q, k, v):                # multi-head causal softmax -> (t, D)
    t = q.shape[1]
    att = (q @ k.transpose(-2, -1)) / math.sqrt(DH)
    mask = torch.triu(torch.ones(t, t, dtype=torch.bool), diagonal=1)
    att = att.masked_fill(mask, float("-inf")).softmax(-1)
    y = att @ v                          # (NH, t, DH)
    return y.transpose(0, 1).contiguous().view(t, D) @ Wo

def decode_no_cache(seq):
    """Generate len(seq) steps; at each step reprocess the whole prefix from scratch."""
    flops = 0
    for t in range(1, seq.shape[0] + 1):
        x = seq[:t]                      # (t, D)
        q, k, v = project(x)             # recompute ALL projections
        _ = attn_block(q, k, v)
        flops += t * t                   # score matrix is t x t  (dominant term)
    return flops

def decode_kv_cache(seq):
    """Generate incrementally; keep K,V for the past, only project the new token."""
    flops = 0
    kc = torch.zeros(NH, 0, DH); vc = torch.zeros(NH, 0, DH)
    for t in range(seq.shape[0]):
        x = seq[t:t+1]                   # (1, D) — just the new token
        q, k, v = project(x)             # project ONLY the new token
        kc = torch.cat([kc, k], dim=1)   # append to cache
        vc = torch.cat([vc, v], dim=1)
        att = (q @ kc.transpose(-2, -1)) / math.sqrt(DH)   # (NH,1,t+1)
        _ = (att.softmax(-1) @ vc).transpose(0, 1).reshape(1, D) @ Wo
        flops += (t + 1)                 # one query vs t+1 keys
    return flops

def timed(fn, seq, reps=3):
    best = math.inf
    for _ in range(reps):
        t0 = time.perf_counter(); fn(seq); best = min(best, time.perf_counter() - t0)
    return best

seq_lens = [64, 128, 256, 512]
rows = []
for N in seq_lens:
    seq = torch.randn(N, D)
    f_no = decode_no_cache(seq); f_kv = decode_kv_cache(seq)
    t_no = timed(decode_no_cache, seq); t_kv = timed(decode_kv_cache, seq)
    rows.append({
        "N": N,
        "flops_no_cache": f_no, "flops_kv_cache": f_kv,
        "flops_ratio": round(f_no / f_kv, 2),
        "ms_no_cache": round(t_no * 1e3, 2), "ms_kv_cache": round(t_kv * 1e3, 2),
        "speedup": round(t_no / t_kv, 2),
    })
OUT["decode"] = {
    "config": {"D": D, "n_head": NH, "d_head": DH},
    "rows": rows,
    "point": "Re-reading everything means each new word re-processes the whole passage so far, so the total work "
             "piles up fast; keeping the notes means each word does a fixed small amount. The gap between them grows "
             "with the length — that gap is the wasted re-reading the notes remove, in exchange for a pile of memory "
             "the model has to carry.",
}

# ----------------------------------------------------------------------------
# D. The 22,580x framing — verify the thread's headline number.
# ----------------------------------------------------------------------------
# GPT-2 param math (thread config): vocab 50304, ctx 1024, n_layer 12, d 768.
V, ctx, L, dm = 50304, 1024, 12, 768
emb = V * dm + ctx * dm                       # token + learned positional embeddings
per_block = (3 * dm * dm + dm * dm)           # QKV proj + output proj (attn)
per_block += 2 * (dm * 4 * dm)                # MLP up + down (4x hidden)
gpt2_params = emb + L * per_block             # (ignores LN/bias — rounds to ~124M)
k3_params = 2.8e12
OUT["scale"] = {
    "gpt2_params_computed": int(gpt2_params),
    "gpt2_params_computed_M": round(gpt2_params / 1e6, 1),
    "gpt2_reported_M": 124,
    "kimi_k3_params": k3_params,
    "kimi_k3_params_T": 2.8,
    "ratio": round(k3_params / gpt2_params),
    "thread_ratio": 22580,
    "point": "124 million to 2.8 trillion internal settings is about 22,580 times bigger in seven years. The "
             "question this lab answers: is being bigger the whole story? It is not — each rung adds a specific "
             "new ability, in a specific place, for a specific job.",
}

here = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(here, "out_softmax.json"), "w") as f:
    json.dump(OUT, f, indent=2)

# console summary so the run is legible
print("A. causal softmax attn row sums:", OUT["attn_demo"]["row_sums"])
print("B. KV cache GB (k3ish) @", Ns, "=", OUT["kv_growth"]["k3ish_GB"])
print("C. decode no-cache vs kv-cache:")
for r in rows:
    print(f"   N={r['N']:>4}  FLOP ratio {r['flops_ratio']:>6}x  wall speedup {r['speedup']:>5}x")
print(f"D. GPT-2 {OUT['scale']['gpt2_params_computed_M']}M vs K3 2.8T  ->  ratio {OUT['scale']['ratio']:,} (thread: 22,580)")
print("wrote out_softmax.json")
