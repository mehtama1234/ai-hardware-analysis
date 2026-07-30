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

## Status — all 7 sessions live
- [x] **00 — The big picture** (no-jargon conceptual spine: memory as the one problem)
- [x] **01 — Softmax baseline** (KV-cache growth, no-cache O(N²) vs cache O(N), the 22,580× framing)
- [x] **02 — Linear attention** (fixed D×D board, exact re-association, needle-recall fade 0.65→0.08)
- [x] **03 — DeltaNet** (overwrite: replace not average; needle recall holds far longer than linear)
- [x] **04 — Chunked DeltaNet** (seq≡chunked to 7e-7, depth L→L/C, 3–22× faster, FLOP split)
- [x] **05 — Gated DeltaNet** (decay dial forgets stale 0.46→0.02; α^Δ law verified to 4 dp)
- [x] **06 — KDA / Kimi Linear** (per-channel keep+forget 0.86 vs scalar 0.16; hybrid −75% KV)
- [x] **07 — Kimi K3** (23×(3 KDA+1 MLA), latent MoE 18/898, SiTU bounded, AttnRes 0.83 vs 0.48)

Sources: ali's X worklog + Kimi Linear (arXiv 2510.26692) + Kimi K3 tech report — see `source/OFFICIAL-SOURCES.md`.

**Bonus pages:** `08-beyond` (how K3 is trained) · `glossary` (plain phrases → real terms).

**Extra experiments** (beyond the one-per-rung runs):
- S02 · **capacity cliff** (`capacity.py`) — recall vs #facts; the cliff at the memory's width.
- S02 · **long-context GPU sweep** (`gpu_sweep.py`, Colab L4) — speedup crosses 6× ~50k, 30× at 256k.
- S02 · **real-GPU decode** (`gpu_bench.py`, L4) — flat vs climbing ms/word, measured.
- S03 · **associative recall, learned** (`recall_task.py`) — train models on "latest value wins": erase-first 100%, add-only 57%.
- S03 · **real-words overwrite** (`realwords.py`, GloVe) — decode recall to an actual word.
- S07 · **MoE load balance** (`moe_collapse.py`) — busiest expert 4.2×→2.9× fair share with balancing.

## Run
```bash
V=/home/manishmehta/projects/llm-from-scratch-lab/.venv-torch   # torch 2.13 CPU, py3.12 — reused
cd 01-softmax-baseline && $V/bin/python attn.py && $V/bin/python build_page.py
python3 build_site.py        # assemble site/
```
