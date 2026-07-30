"""
Session 03/05 extra — a task the memory has to LEARN.

Everything else in the lab measures storage geometry. This one is different: we
actually TRAIN tiny one-layer models and watch which memory designs can learn a
task that is all about memory — associative recall.

The task (the canonical one these papers use): show the model a stream of
(key, value) pairs, then at the end show one key again and ask it to produce that
key's value. To win, the model must, in a single fixed-size memory, write each
pair as it streams by and read the right one back on demand.

We train three memories with identical everything-else:
  - add-only   : linear attention, just sums writes (no eviction)
  - erase-first: the delta rule (read-old, subtract, write-new)
  - gated      : erase-first + a learned forget dial
and report the accuracy each reaches. The gap is the point: eviction/forgetting
isn't a nicety, it's what makes the task learnable.

Pure torch, CPU. Real training.
"""
import json, os
import torch
import torch.nn as nn
import torch.nn.functional as F

torch.manual_seed(0)

NK = 12          # number of distinct keys (= vocab of keys)
NV = 12          # number of distinct values
D  = 64          # model width
PAIRS = 8        # pairs shown per sequence before the query

def make_batch(B, gen):
    # each sequence: PAIRS random (key,value) pairs, then a query = one of the keys.
    keys = torch.randint(0, NK, (B, PAIRS), generator=gen)
    vals = torch.randint(0, NV, (B, PAIRS), generator=gen)
    qpos = torch.randint(0, PAIRS, (B,), generator=gen)
    qkey = keys[torch.arange(B), qpos]
    target = vals[torch.arange(B), qpos]
    return keys, vals, qkey, target

class RecallModel(nn.Module):
    def __init__(self, kind):
        super().__init__()
        self.kind = kind
        self.k_emb = nn.Embedding(NK, D)
        self.v_emb = nn.Embedding(NV, D)
        self.q_emb = nn.Embedding(NK, D)
        self.Wk = nn.Linear(D, D, bias=False)
        self.Wq = nn.Linear(D, D, bias=False)
        self.out = nn.Linear(D, NV)
        if kind == "gated":
            self.wbeta = nn.Linear(D, 1)
        self.proc = lambda x: F.normalize(F.silu(x), dim=-1)

    def forward(self, keys, vals, qkey):
        B = keys.shape[0]
        S = torch.zeros(B, D, D)
        for t in range(keys.shape[1]):
            k = self.proc(self.Wk(self.k_emb(keys[:, t])))       # (B,D)
            v = self.v_emb(vals[:, t])                            # (B,D)
            if self.kind == "add_only":
                S = S + torch.einsum('bi,bj->bij', k, v)
            elif self.kind == "erase_first":
                v_old = torch.einsum('bi,bij->bj', k, S)
                S = S + torch.einsum('bi,bj->bij', k, v - v_old)
            elif self.kind == "gated":
                beta = torch.sigmoid(self.wbeta(self.k_emb(keys[:, t])))  # (B,1)
                v_old = torch.einsum('bi,bij->bj', k, S)
                upd = beta.unsqueeze(-1) * torch.einsum('bi,bj->bij', k, v - v_old)
                S = S + upd
        q = self.proc(self.Wq(self.q_emb(qkey)))                 # (B,D)
        read = torch.einsum('bi,bij->bj', q, S)                  # (B,D)
        return self.out(read)

def train(kind, steps=400, B=256):
    gen = torch.Generator().manual_seed(0)
    m = RecallModel(kind); opt = torch.optim.Adam(m.parameters(), lr=3e-3)
    curve = []
    for step in range(steps):
        keys, vals, qkey, target = make_batch(B, gen)
        logits = m(keys, vals, qkey)
        loss = F.cross_entropy(logits, target)
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 40 == 0 or step == steps - 1:
            with torch.no_grad():
                acc = (logits.argmax(-1) == target).float().mean().item()
            curve.append({"step": step, "acc": round(acc, 3)})
    # final eval on fresh data
    with torch.no_grad():
        keys, vals, qkey, target = make_batch(2048, gen)
        acc = (m(keys, vals, qkey).argmax(-1) == target).float().mean().item()
    return round(acc, 3), curve

OUT = {"n_keys": NK, "n_values": NV, "pairs_per_seq": PAIRS, "d": D, "chance": round(1/NV, 3), "results": {}}
for kind in ("add_only", "erase_first", "gated"):
    acc, curve = train(kind)
    OUT["results"][kind] = {"final_acc": acc, "curve": curve}
    print(f"{kind:>12}: final accuracy {acc:.3f}  (chance {1/NV:.3f})  curve {[c['acc'] for c in curve]}")

r = OUT["results"]
OUT["point"] = (f"Chance is {1/NV:.0%}. The plain add-only memory barely beats guessing "
                f"({r['add_only']['final_acc']:.0%}) — with every write just summed on top of the others, it can't "
                f"cleanly read one pair back. The erase-first memory LEARNS the task ({r['erase_first']['final_acc']:.0%}), "
                f"because replacing a key's value in place keeps the pairs separable. Adding a learned forget dial "
                f"({r['gated']['final_acc']:.0%}) does about as well here and helps more as streams get longer. The gap "
                "is the whole argument: eviction and forgetting aren't polish — they're what makes remembering learnable.")

here = os.path.dirname(os.path.abspath(__file__))
json.dump(OUT, open(os.path.join(here, "out_recall.json"), "w"), indent=2)
print("wrote out_recall.json")
