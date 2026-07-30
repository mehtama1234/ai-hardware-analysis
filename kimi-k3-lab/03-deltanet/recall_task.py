"""
Session 03/05 extra — a task the memory has to LEARN.

Everything else in the lab measures storage geometry. This one is different: we
actually TRAIN tiny one-layer models and watch which memory designs can learn a
task that is all about memory — associative recall.

The task: stream (key, value) pairs where keys come from a small set — so the same
key shows up several times with different values, as facts do when they get updated.
Then ask for one key, and the right answer is the value from its LATEST appearance.
To win, the model must not just store pairs but keep the CURRENT value for each key
as new ones overwrite the old — the exact thing the delta rule is built for.

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

NK = 4           # SMALL key vocab, so keys repeat within a stream (overwrites happen)
NV = 16          # distinct values
D  = 48          # model width
PAIRS = 10       # pairs streamed before the query — keys repeat, so "latest wins"

def make_batch(B, gen):
    # each sequence: PAIRS (key,value) pairs with keys drawn from a SMALL set, so a
    # key usually appears several times with different values. The query asks for a
    # key, and the correct answer is the value from its LAST occurrence — so the
    # model must UPDATE, not just accumulate.
    keys = torch.randint(0, NK, (B, PAIRS), generator=gen)
    vals = torch.randint(0, NV, (B, PAIRS), generator=gen)
    qkey = torch.randint(0, NK, (B,), generator=gen)
    target = torch.zeros(B, dtype=torch.long)
    for b in range(B):
        occ = (keys[b] == qkey[b]).nonzero()
        if len(occ) == 0:                       # ensure the queried key appears
            keys[b, -1] = qkey[b]; occ = (keys[b] == qkey[b]).nonzero()
        target[b] = vals[b, occ[-1].item()]     # value of the LAST occurrence
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

def train(kind, steps=250, B=96):
    gen = torch.Generator().manual_seed(0)
    m = RecallModel(kind); opt = torch.optim.Adam(m.parameters(), lr=3e-3)
    curve = []
    for step in range(steps):
        keys, vals, qkey, target = make_batch(B, gen)
        logits = m(keys, vals, qkey)
        loss = F.cross_entropy(logits, target)
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 25 == 0 or step == steps - 1:
            with torch.no_grad():
                acc = (logits.argmax(-1) == target).float().mean().item()
            curve.append({"step": step, "acc": round(acc, 3)})
    with torch.no_grad():
        keys, vals, qkey, target = make_batch(1024, gen)
        acc = (m(keys, vals, qkey).argmax(-1) == target).float().mean().item()
    return round(acc, 3), curve

OUT = {"n_keys": NK, "n_values": NV, "pairs_per_seq": PAIRS, "d": D, "chance": round(1/NV, 3), "results": {}}
for kind in ("add_only", "erase_first", "gated"):
    acc, curve = train(kind)
    OUT["results"][kind] = {"final_acc": acc, "curve": curve}
    print(f"{kind:>12}: final accuracy {acc:.3f}  (chance {1/NV:.3f})  curve {[c['acc'] for c in curve]}", flush=True)

r = OUT["results"]
OUT["point"] = (f"Random guessing scores {1/NV:.0%}. The plain add-only memory reaches only "
                f"{r['add_only']['final_acc']:.0%}: because it just sums every write, when a key appears several times "
                f"it ends up holding a blur of all that key's values and can't say which was latest. The erase-first "
                f"memory reaches {r['erase_first']['final_acc']:.0%} — writing each value in place of the old one keeps "
                f"only the current answer. The learned forget dial reaches {r['gated']['final_acc']:.0%}. The gap is the "
                "whole argument: being able to overwrite isn't polish, it's what makes 'remember the latest value' learnable at all.")

here = os.path.dirname(os.path.abspath(__file__))
json.dump(OUT, open(os.path.join(here, "out_recall.json"), "w"), indent=2)
print("wrote out_recall.json")
