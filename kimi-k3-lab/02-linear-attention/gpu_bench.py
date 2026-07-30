"""One-shot GPU benchmark for the Kimi K3 lab.
Real autoregressive decode: FlashAttention softmax (torch SDPA) vs linear attention.
Measures ms/token and peak GPU memory as the context grows. Chatty; ~1 min."""
import torch, time, math, json
import torch.nn.functional as F

assert torch.cuda.is_available(), "no GPU"
dev = "cuda"; dt = torch.float16
name = torch.cuda.get_device_name(0)
print(f"[bench] GPU = {name}", flush=True)

D, H = 2048, 16          # model dim, heads
Dh = D // H              # head dim = 128
torch.manual_seed(0)
Wqkv = (torch.randn(D, 3*D, device=dev, dtype=dt) / math.sqrt(D))
Wo   = (torch.randn(D, D,   device=dev, dtype=dt) / math.sqrt(D))
state_MB = H*Dh*Dh*2/1e6   # linear state is fixed: H×Dh×Dh fp16

def decode_softmax(L):
    torch.cuda.reset_peak_memory_stats()
    Kc = torch.zeros(1, H, L, Dh, device=dev, dtype=dt)   # preallocated KV cache (fair)
    Vc = torch.zeros(1, H, L, Dh, device=dev, dtype=dt)
    x = torch.randn(1, D, device=dev, dtype=dt)
    torch.cuda.synchronize(); t0 = time.time()
    for i in range(L):
        q, k, v = (x @ Wqkv).split(D, -1)
        q = q.view(1, H, 1, Dh); k = k.view(1, H, 1, Dh); v = v.view(1, H, 1, Dh)
        Kc[:, :, i] = k[:, :, 0]; Vc[:, :, i] = v[:, :, 0]
        o = F.scaled_dot_product_attention(q, Kc[:, :, :i+1], Vc[:, :, :i+1])  # FlashAttention on GPU
        x = (o.reshape(1, D) @ Wo)
    torch.cuda.synchronize(); ms = (time.time()-t0)*1000
    return ms/L, torch.cuda.max_memory_allocated()/1e6

def decode_linear(L):
    torch.cuda.reset_peak_memory_stats()
    S = torch.zeros(1, H, Dh, Dh, device=dev, dtype=dt)   # fixed-size state
    Z = torch.zeros(1, H, Dh, device=dev, dtype=dt)
    x = torch.randn(1, D, device=dev, dtype=dt)
    torch.cuda.synchronize(); t0 = time.time()
    for i in range(L):
        q, k, v = (x @ Wqkv).split(D, -1)
        q = F.elu(q.view(1, H, Dh)) + 1; k = F.elu(k.view(1, H, Dh)) + 1; v = v.view(1, H, Dh)
        S = S + k.unsqueeze(-1) * v.unsqueeze(-2)          # fold token into fixed state
        Z = Z + k
        num = (q.unsqueeze(-2) @ S).squeeze(-2)
        den = (q * Z).sum(-1, keepdim=True) + 1e-4
        x = (num/den).reshape(1, D) @ Wo
    torch.cuda.synchronize(); ms = (time.time()-t0)*1000
    return ms/L, torch.cuda.max_memory_allocated()/1e6

# warmup
print("[bench] warmup…", flush=True); decode_softmax(64); decode_linear(64)

rows = []
for L in [1024, 4096, 16384]:
    sm_ms, sm_mem = decode_softmax(L)
    ln_ms, ln_mem = decode_linear(L)
    kv_MB = 2*L*H*Dh*2/1e6
    rows.append({"L": L,
                 "softmax_ms_per_tok": round(sm_ms, 4), "linear_ms_per_tok": round(ln_ms, 4),
                 "speedup": round(sm_ms/ln_ms, 2),
                 "softmax_kv_MB": round(kv_MB, 1), "linear_state_MB": round(state_MB, 2),
                 "mem_ratio": round(kv_MB/state_MB, 1)})
    print(f"[bench] L={L:>5}: softmax {sm_ms:.3f} ms/tok  linear {ln_ms:.3f} ms/tok  -> {sm_ms/ln_ms:.2f}x  |  KV {kv_MB:.0f}MB vs state {state_MB:.1f}MB", flush=True)

out = {"gpu": name, "d_model": D, "heads": H, "d_head": Dh, "dtype": "fp16",
       "linear_state_MB": round(state_MB, 2), "rows": rows}
print("===JSON===", flush=True)
print(json.dumps(out), flush=True)
print("===END===", flush=True)
print("[bench] done", flush=True)
