# Kimi K3, from first principles — the lab

A hands-on companion to **ali (@waterloo_intern)'s** worklog
*"22580: From GPT-2 to Kimi K3, Explained"* (X, Jul 27 2026 — 5.2M views).
Original thread saved in [`source/`](source/).

The thread's thesis: **going from GPT-2 (2019) to Kimi K3 (2026) is not just 22,580× more
parameters.** Each architectural step changes *what the model stores, how it updates that
state, or how it retrieves information a fixed-size state cannot preserve.* This lab rebuilds
that ladder rung by rung — and **runs each mechanism for real** on tiny tensors so the claims
(fixed state, eviction, chunk-wise parallelism, per-channel decay) become measured numbers,
not assertions.

Same shape as `~/projects/llm-from-scratch-lab`: each session is a folder with a `*.py` that
does the **real** computation → `out_*.json`, a `build_page.py` that renders `out/index.html`
with the explanation embedded, and a top-level `build_site.py` that assembles the public site.

## The ladder (each rung fixes a concrete limitation of the one before)

| # | Session | Mechanism | Limitation it fixes |
|---|---------|-----------|---------------------|
| 01 | **Softmax baseline** | GPT-2 causal softmax attention + KV cache | (baseline) — but KV cache grows **O(N)**, a bandwidth wall |
| 02 | Linear attention | ELU+1 feature map, fold K,V into a fixed **D×D** state | kills the O(N) cache → but a less expressive kernel |
| 03 | DeltaNet | delta rule: read-old → subtract → write-new (eviction) | additive state interferes once at capacity |
| 04 | Chunked DeltaNet | Householder reparam → chunk-wise parallel prefill | delta rule is sequential → can't train efficiently |
| 05 | Gated DeltaNet | Mamba-2 decay + delta rule | delta can replace one fact but can't decay generally |
| 06 | KDA / Kimi Linear | **per-channel** fine-grained gating + MLA hybrid | one scalar decay is too coarse |
| 07 | **Kimi K3** | 23×(3 KDA + 1 MLA) macrocycles, latent MoE, SiTU, Gated MLA, AttnRes | put capacity where it has a functional role |

Scope: the full ladder, built as an interactive lab with real runs. Sessions land one at a time.

## Status
- [x] **01 — Softmax baseline** (KV-cache growth, no-cache O(N²) vs cache O(N) recompute, the 22,580× framing)
- [ ] 02 — Linear attention
- [ ] 03 — DeltaNet
- [ ] 04 — Chunked / parallel DeltaNet
- [ ] 05 — Gated DeltaNet
- [ ] 06 — KDA / Kimi Linear
- [ ] 07 — Kimi K3

## Run
```bash
V=/home/manishmehta/projects/llm-from-scratch-lab/.venv-torch   # torch 2.13 CPU, py3.12 — reused
cd 01-softmax-baseline && $V/bin/python attn.py && $V/bin/python build_page.py
python3 build_site.py        # assemble site/
```
