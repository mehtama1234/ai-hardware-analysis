"""
Session 02 extra — the capacity cliff.

A fixed-size memory can only hold so much. Here we measure exactly how much:
store N random key->value facts in a fixed board of width d, then ask for them
back and score the recall. As N climbs past d, recall falls off a cliff. We run
both the plain "add-only" board and the "erase-first" board (Session 03's delta
rule) so you can see erase-first pushes the cliff out but can't abolish it.

Pure torch, CPU.
"""
import json, math, os
import torch
import torch.nn.functional as F

torch.manual_seed(0)
def phi(x): return F.elu(x) + 1.0
def proc(x): return F.normalize(F.silu(x), dim=-1)
def cos(a, b): return float(F.cosine_similarity(a, b, dim=0))

def add_only_recall(k, v, probe_idx):
    fk = phi(k); S = fk.T @ v; z = fk.sum(0)
    out = []
    for i in probe_idx:
        fq = phi(k[i]); out.append(cos((fq @ S) / (fq @ z + 1e-6), v[i]))
    return sum(out) / len(out)

def erase_first_recall(k, v, probe_idx, beta=1.0):
    d = k.shape[1]; fk = proc(k); S = torch.zeros(d, d)
    for t in range(k.shape[0]):
        v_old = fk[t] @ S
        S = S + torch.outer(fk[t], beta * (v[t] - v_old))
    out = [cos(proc(k[i]) @ S, v[i]) for i in probe_idx]
    return sum(out) / len(out)

D = 64
Ns = [8, 16, 32, 48, 64, 96, 128, 192, 256]
rows = []
for N in Ns:
    add_s, er_s = [], []
    for s in range(10):
        g = torch.Generator().manual_seed(s)
        k = torch.randn(N, D, generator=g); v = torch.randn(N, D, generator=g)
        probe = list(range(min(N, 24)))
        add_s.append(add_only_recall(k, v, probe))
        er_s.append(erase_first_recall(k, v, probe))
    rows.append({"N": N, "over_capacity": N > D,
                 "add_only_recall": round(sum(add_s)/len(add_s), 3),
                 "erase_first_recall": round(sum(er_s)/len(er_s), 3)})

OUT = {"d": D, "rows": rows,
       "point": (f"The board is {D} wide. While you store fewer than ~{D} facts, the erase-first board recalls "
                 "them well; the plain add-only board is already fuzzy. As the count climbs past the board's "
                 f"width ({D}), both fall off a cliff — there is simply no more room, and every stored fact starts "
                 "smearing into the others. Erase-first pushes the cliff out (it wastes less room on redundancy) but "
                 "cannot abolish it: a fixed board has a hard capacity, which is why a real model also keeps a few "
                 "keep-everything layers and forgets on purpose.")}

here = os.path.dirname(os.path.abspath(__file__))
json.dump(OUT, open(os.path.join(here, "out_capacity.json"), "w"), indent=2)
print(f"capacity cliff (board width d={D}):")
for r in rows:
    tag = " <-- over capacity" if r["over_capacity"] else ""
    print(f"  N={r['N']:>3}  add-only {r['add_only_recall']:.3f}  erase-first {r['erase_first_recall']:.3f}{tag}")
print("wrote out_capacity.json")
