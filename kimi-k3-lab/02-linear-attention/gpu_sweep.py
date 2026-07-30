"""Long-context GPU sweep for the Kimi K3 lab.
Same decode as gpu_bench, extended to long context: watch linear's flat per-token
time pull further and further ahead of softmax as context grows toward the regime
where the paper reports up to 6x. Chatty; a couple of minutes."""
import torch, time, math, json
import torch.nn.functional as F

assert torch.cuda.is_available(), "no GPU"
dev = "cuda"; dt = torch.float16
name = torch.cuda.get_device_name(0)
print(f"[sweep] GPU = {name}", flush=True)

D, H = 2048, 16; Dh = D // H
torch.manual_seed(0)
Wqkv = (torch.randn(D, 3*D, device=dev, dtype=dt) / math.sqrt(D))
Wo   = (torch.randn(D, D,   device=dev, dtype=dt) / math.sqrt(D))
state_MB = H*Dh*Dh*2/1e6

def decode_softmax(L, measure=256):
    # prefill a KV cache of length L-measure, then time `measure` decode steps
    Kc = torch.zeros(1, H, L, Dh, device=dev, dtype=dt)
    Vc = torch.zeros(1, H, L, Dh, device=dev, dtype=dt)
    x = torch.randn(1, D, device=dev, dtype=dt)
    start = L - measure
    # fill the prefix quickly with random k/v (content doesn't affect timing shape)
    Kc[:, :, :start] = torch.randn(1, H, start, Dh, device=dev, dtype=dt)
    Vc[:, :, :start] = torch.randn(1, H, start, Dh, device=dev, dtype=dt)
    torch.cuda.synchronize(); t0 = time.time()
    for i in range(start, L):
        q, k, v = (x @ Wqkv).split(D, -1)
        q = q.view(1, H, 1, Dh); Kc[:, :, i] = k.view(1, H, Dh); Vc[:, :, i] = v.view(1, H, Dh)
        o = F.scaled_dot_product_attention(q, Kc[:, :, :i+1], Vc[:, :, :i+1])
        x = o.reshape(1, D) @ Wo
    torch.cuda.synchronize(); return (time.time()-t0)*1000/measure

def decode_linear(L, measure=256):
    S = torch.randn(1, H, Dh, Dh, device=dev, dtype=dt) * 0.01
    Z = torch.randn(1, H, Dh, device=dev, dtype=dt) * 0.01
    x = torch.randn(1, D, device=dev, dtype=dt)
    torch.cuda.synchronize(); t0 = time.time()
    for _ in range(measure):                       # linear per-step cost is L-independent
        q, k, v = (x @ Wqkv).split(D, -1)
        q = F.elu(q.view(1, H, Dh)) + 1; k = F.elu(k.view(1, H, Dh)) + 1; v = v.view(1, H, Dh)
        S = S + k.unsqueeze(-1) * v.unsqueeze(-2); Z = Z + k
        num = (q.unsqueeze(-2) @ S).squeeze(-2); den = (q * Z).sum(-1, keepdim=True) + 1e-4
        x = (num/den).reshape(1, D) @ Wo
    torch.cuda.synchronize(); return (time.time()-t0)*1000/measure

print("[sweep] warmup…", flush=True); decode_softmax(512); decode_linear(512)
ln = decode_linear(1024)   # flat; measure once
rows = []
for L in [4096, 16384, 65536, 131072, 262144]:
    sm = decode_softmax(L)
    kv_MB = 2*L*H*Dh*2/1e6
    rows.append({"L": L, "softmax_ms_per_tok": round(sm, 4), "linear_ms_per_tok": round(ln, 4),
                 "speedup": round(sm/ln, 2), "softmax_kv_MB": round(kv_MB, 1),
                 "mem_ratio": round(kv_MB/state_MB, 1)})
    print(f"[sweep] L={L:>7}: softmax {sm:.3f} ms/tok  linear {ln:.3f}  -> {sm/ln:.2f}x  |  KV {kv_MB:.0f}MB", flush=True)

out = {"gpu": name, "d_model": D, "heads": H, "d_head": Dh, "linear_state_MB": round(state_MB, 2), "rows": rows}
print("===JSON===", flush=True); print(json.dumps(out), flush=True); print("===END===", flush=True)
print("[sweep] done", flush=True)
