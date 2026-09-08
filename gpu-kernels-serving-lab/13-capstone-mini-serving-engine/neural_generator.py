"""Real, untrained character-level transformer for serving mechanics, not quality.

No downloads, shared prefix cache, continuous batching or GPU speedup claims.
Each request owns its append-only KV tensors. Equal-length batch requests use a
shared batched decode path; variable-length batches retain an explicit serial
fallback because this teaching model has no padding/length mask implementation.
"""
from pathlib import Path
import sys

import torch
from torch import nn

_HERE = Path(__file__).resolve()
_MODEL_INTEGRATION_CANDIDATES = (
    _HERE.parents[2] / "gpu-mode-curriculum" / "model-integration",
    _HERE.parents[2] / "model-integration",
)
for _candidate in _MODEL_INTEGRATION_CANDIDATES:
    if (_candidate / "model_integration").exists():
        sys.path.insert(0, str(_candidate))
        break
from model_integration.tiny_transformer import TinyTransformerBlock


class CharacterModel(nn.Module):
    alphabet = "? abcdefghijklmnopqrstuvwxyz0123456789.,!\n"

    def __init__(self, context=128, hidden=32, heads=4):
        super().__init__()
        self.context = context
        self.hidden = hidden
        self.embedding = nn.Embedding(len(self.alphabet), hidden)
        self.position = nn.Embedding(context, hidden)
        self.block = TinyTransformerBlock(hidden, heads, False, "sdpa")
        self.norm = nn.LayerNorm(hidden)
        self.head = nn.Linear(hidden, len(self.alphabet), bias=False)

    def forward(self, tokens, cache=None, *, cached=False, preallocated_cache=None):
        if preallocated_cache is not None:
            offset = preallocated_cache[2]
        else:
            offset = 0 if cache is None else cache[0].shape[-2]
        if tokens.ndim != 2 or tokens.shape[1] < 1 or offset + tokens.shape[1] > self.context:
            raise ValueError("nonempty tokens must fit context")
        x = self.embedding(tokens) + self.position(torch.arange(offset, offset + tokens.shape[1], device=tokens.device))
        if preallocated_cache is not None:
            cache_k, cache_v, offset = preallocated_cache
            x, next_offset = self.block.forward_cached_preallocated(x, cache_k, cache_v, offset)
            return self.norm(x).matmul(self.head.weight.t()), (cache_k, cache_v, next_offset)
        if cached:
            x, cache = self.block.forward_cached(x, cache)
        else:
            if cache is not None:
                raise ValueError("cache requires cached=True")
            x = self.block(x)
        logits = self.head(self.norm(x))
        return (logits, cache) if cached else logits


class NeuralGenerator:
    model_name = "gpu-lab-untrained-character-transformer"

    def __init__(self, device="cpu", *, hidden=32, heads=4, seed=151):
        # Preserve the caller's global RNG state; no request mutates weights.
        with torch.random.fork_rng(devices=[]):
            torch.manual_seed(seed)
            self.model = CharacterModel(hidden=hidden, heads=heads).eval()
        self.device = torch.device(device)
        if self.device.type == "cuda" and not torch.cuda.is_available():
            raise RuntimeError("CUDA device requested but CUDA is unavailable")
        self.model = self.model.to(self.device)
        self.backend = f"untrained-character-transformer-{self.device.type}-kv-h{hidden}"
        self._cuda_graph_cache = {}
        self._cuda_graph_batch_cache = {}
        self._cuda_graph_single_cache = {}

    def encode(self, prompt):
        if not isinstance(prompt, str) or not prompt:
            raise ValueError("prompt must be a nonempty string")
        return [self.model.alphabet.find(c) if c in self.model.alphabet else 0 for c in prompt.lower()]

    @torch.inference_mode()
    def _build_cuda_graph_bundle(self, prompt: str, max_tokens: int) -> dict:
        """Capture one fixed-offset CUDA graph per decode step.

        Each graph owns the same static input/cache/output addresses but writes
        a different fixed KV slot and uses a fixed attention prefix length.
        Capturing per offset keeps replay graph-safe while preserving the
        device-resident token chain. Capture/setup is intentionally outside the
        steady-state timing path and is a fallback cost for a new bucket.
        """
        if self.device.type != "cuda":
            raise RuntimeError("CUDA Graph decode requires a CUDA device")
        if not hasattr(torch.cuda, "CUDAGraph"):
            raise RuntimeError("CUDA Graph support is unavailable")
        ids = self.encode(prompt)
        if len(ids) + max_tokens > self.model.context:
            raise ValueError("prompt and max_tokens exceed model context")
        heads = self.model.block.heads
        head_dim = self.model.block.hidden // heads
        cache_k = torch.empty((1, heads, self.model.context, head_dim), device=self.device)
        cache_v = torch.empty_like(cache_k)
        prompt_tokens = torch.tensor([ids], dtype=torch.long, device=self.device)
        prefill_logits, prefill_state = self.model(
            prompt_tokens, preallocated_cache=(cache_k, cache_v, 0)
        )
        first_logits = prefill_logits[:, -1].clone()
        first_token = prefill_logits[:, -1].argmax(-1, keepdim=True)
        seed_k = cache_k.clone()
        seed_v = cache_v.clone()
        static_input = torch.empty((1, 1), dtype=torch.long, device=self.device)
        static_next = torch.empty_like(static_input)
        static_logits = torch.empty((1, self.model.alphabet.__len__()), device=self.device)
        graphs = []
        warm_token = first_token.clone()
        torch.cuda.synchronize()
        for step in range(max_tokens - 1):
            offset = len(ids) + step
            static_input.copy_(warm_token)
            graph = torch.cuda.CUDAGraph()
            with torch.cuda.graph(graph):
                logits, _ = self.model(
                    static_input, preallocated_cache=(cache_k, cache_v, offset)
                )
                static_logits.copy_(logits[:, -1])
                static_next.copy_(static_logits.argmax(-1, keepdim=True))
            torch.cuda.synchronize()
            warm_token = static_next.clone()
            graphs.append(graph)
        cache_k.copy_(seed_k)
        cache_v.copy_(seed_v)
        static_input.copy_(first_token)
        torch.cuda.synchronize()
        return {
            "graphs": graphs,
            "cache_k": cache_k,
            "cache_v": cache_v,
            "seed_k": seed_k,
            "seed_v": seed_v,
            "static_input": static_input,
            "static_next": static_next,
            "static_logits": static_logits,
            "first_logits": first_logits,
            "first_token": first_token,
            "capture_steps": max_tokens - 1,
            "prompt_tokens": len(ids),
        }

    def _cuda_graph_bundle(self, prompt: str, max_tokens: int) -> dict:
        key = (prompt, max_tokens, self.model.hidden, self.model.block.heads)
        bundle = self._cuda_graph_cache.get(key)
        if bundle is None:
            bundle = self._build_cuda_graph_bundle(prompt, max_tokens)
            self._cuda_graph_cache[key] = bundle
        return bundle

    @torch.inference_mode()
    def _build_cuda_graph_batch_bundle(self, prompts: list[str], max_tokens: int) -> dict:
        """Capture a fixed batch-size graph bucket for equal-length prompts."""
        if self.device.type != "cuda":
            raise RuntimeError("CUDA Graph decode requires a CUDA device")
        ids = [self.encode(prompt) for prompt in prompts]
        if not ids or len({len(row) for row in ids}) != 1:
            raise ValueError("CUDA Graph batch buckets require equal-length prompts")
        if len(ids[0]) + max_tokens > self.model.context:
            raise ValueError("prompt and max_tokens exceed model context")
        batch = len(ids)
        heads = self.model.block.heads
        head_dim = self.model.block.hidden // heads
        cache_k = torch.empty((batch, heads, self.model.context, head_dim), device=self.device)
        cache_v = torch.empty_like(cache_k)
        prompt_tokens = torch.tensor(ids, dtype=torch.long, device=self.device)
        prefill_logits, _ = self.model(prompt_tokens, preallocated_cache=(cache_k, cache_v, 0))
        first_logits = prefill_logits[:, -1].clone()
        first_token = prefill_logits[:, -1].argmax(-1, keepdim=True)
        seed_k = cache_k.clone()
        seed_v = cache_v.clone()
        static_input = torch.empty((batch, 1), dtype=torch.long, device=self.device)
        static_next = torch.empty_like(static_input)
        static_logits = torch.empty((batch, len(self.model.alphabet)), device=self.device)
        graphs = []
        warm_token = first_token.clone()
        torch.cuda.synchronize()
        for step in range(max_tokens - 1):
            static_input.copy_(warm_token)
            offset = len(ids[0]) + step
            graph = torch.cuda.CUDAGraph()
            with torch.cuda.graph(graph):
                logits, _ = self.model(static_input, preallocated_cache=(cache_k, cache_v, offset))
                static_logits.copy_(logits[:, -1])
                static_next.copy_(static_logits.argmax(-1, keepdim=True))
            torch.cuda.synchronize()
            warm_token = static_next.clone()
            graphs.append(graph)
        cache_k.copy_(seed_k)
        cache_v.copy_(seed_v)
        static_input.copy_(first_token)
        torch.cuda.synchronize()
        return {
            "graphs": graphs, "cache_k": cache_k, "cache_v": cache_v,
            "seed_k": seed_k, "seed_v": seed_v,
            "static_input": static_input, "static_next": static_next,
            "static_logits": static_logits, "first_logits": first_logits,
            "first_token": first_token, "batch": batch,
        }

    def _cuda_graph_batch_bundle(self, prompts: list[str], max_tokens: int) -> dict:
        key = (tuple(prompts), max_tokens, self.model.hidden, self.model.block.heads)
        bundle = self._cuda_graph_batch_cache.get(key)
        if bundle is None:
            bundle = self._build_cuda_graph_batch_bundle(prompts, max_tokens)
            self._cuda_graph_batch_cache[key] = bundle
        return bundle

    @torch.inference_mode()
    def generate_batch_cuda_graph(self, prompts: list[str], max_tokens: int) -> list[list[int]]:
        bundle = self._cuda_graph_batch_bundle(prompts, max_tokens)
        bundle["cache_k"].copy_(bundle["seed_k"])
        bundle["cache_v"].copy_(bundle["seed_v"])
        bundle["static_input"].copy_(bundle["first_token"])
        generated = [bundle["first_token"].clone()]
        for graph in bundle["graphs"]:
            graph.replay()
            generated.append(bundle["static_next"].clone())
            bundle["static_input"].copy_(bundle["static_next"])
        return torch.cat(generated, dim=1).tolist()

    @torch.inference_mode()
    def _generate_cuda_graph(self, prompt: str, max_tokens: int):
        bundle = self._cuda_graph_bundle(prompt, max_tokens)
        bundle["cache_k"].copy_(bundle["seed_k"])
        bundle["cache_v"].copy_(bundle["seed_v"])
        bundle["static_input"].copy_(bundle["first_token"])
        generated = [bundle["first_token"].clone()]
        logits_trace = [bundle["first_logits"].clone()]
        for graph in bundle["graphs"]:
            graph.replay()
            logits_trace.append(bundle["static_logits"].clone())
            generated.append(bundle["static_next"].clone())
            bundle["static_input"].copy_(bundle["static_next"])
        return torch.cat(generated, dim=1)[0].tolist(), logits_trace

    @torch.inference_mode()
    def _build_cuda_graph_single_bundle(self, prompt: str, max_tokens: int) -> dict:
        """Capture an entire fixed-length decode chain in one CUDA graph."""
        if self.device.type != "cuda" or not hasattr(torch.cuda, "CUDAGraph"):
            raise RuntimeError("single CUDA graph decode requires CUDA graph support")
        ids = self.encode(prompt)
        if len(ids) + max_tokens > self.model.context:
            raise ValueError("prompt and max_tokens exceed model context")
        heads = self.model.block.heads
        head_dim = self.model.hidden // heads
        cache_k = torch.empty((1, heads, self.model.context, head_dim), device=self.device)
        cache_v = torch.empty_like(cache_k)
        prompt_tokens = torch.tensor([ids], dtype=torch.long, device=self.device)
        prefill_logits, _ = self.model(prompt_tokens, preallocated_cache=(cache_k, cache_v, 0))
        first_token = prefill_logits[:, -1].argmax(-1, keepdim=True)
        seed_k = cache_k.clone()
        seed_v = cache_v.clone()
        static_input = torch.empty((1, 1), dtype=torch.long, device=self.device)
        static_next = torch.empty_like(static_input)
        static_logits = torch.empty((1, len(self.model.alphabet)), device=self.device)
        static_tokens = torch.empty((1, max_tokens), dtype=torch.long, device=self.device)

        def run_chain() -> None:
            static_tokens[:, 0:1].copy_(first_token)
            static_input.copy_(first_token)
            for step in range(1, max_tokens):
                logits, _ = self.model(
                    static_input,
                    preallocated_cache=(cache_k, cache_v, len(ids) + step - 1),
                )
                static_logits.copy_(logits[:, -1])
                static_next.copy_(static_logits.argmax(-1, keepdim=True))
                static_tokens[:, step].copy_(static_next)
                static_input.copy_(static_next)

        for _ in range(2):
            run_chain()
        cache_k.copy_(seed_k)
        cache_v.copy_(seed_v)
        torch.cuda.synchronize()
        graph = torch.cuda.CUDAGraph()
        with torch.cuda.graph(graph):
            run_chain()
        torch.cuda.synchronize()
        return {
            "graph": graph, "cache_k": cache_k, "cache_v": cache_v,
            "seed_k": seed_k, "seed_v": seed_v, "static_input": static_input,
            "static_tokens": static_tokens, "first_token": first_token,
        }

    def _cuda_graph_single_bundle(self, prompt: str, max_tokens: int) -> dict:
        key = (prompt, max_tokens, self.model.hidden, self.model.block.heads)
        bundle = self._cuda_graph_single_cache.get(key)
        if bundle is None:
            bundle = self._build_cuda_graph_single_bundle(prompt, max_tokens)
            self._cuda_graph_single_cache[key] = bundle
        return bundle

    @torch.inference_mode()
    def generate_cuda_graph_single(self, prompt: str, max_tokens: int) -> list[int]:
        """Replay one graph for the complete fixed-length decode chain."""
        bundle = self._cuda_graph_single_bundle(prompt, max_tokens)
        bundle["cache_k"].copy_(bundle["seed_k"])
        bundle["cache_v"].copy_(bundle["seed_v"])
        bundle["graph"].replay()
        return bundle["static_tokens"][0].tolist()

    @torch.inference_mode()
    def generate(self, prompt, max_tokens, *, cached=True, cache_storage="dynamic"):
        ids = self.encode(prompt)
        if type(max_tokens) is not int or max_tokens < 1 or len(ids) + max_tokens > self.model.context:
            raise ValueError("positive max_tokens and prompt must fit 128-character context")
        tokens = torch.tensor([ids], dtype=torch.long, device=self.device)
        cache = None
        if cache_storage not in {"dynamic", "preallocated", "cuda_graph"}:
            raise ValueError("cache_storage must be dynamic, preallocated, or cuda_graph")
        if cache_storage == "cuda_graph":
            if not cached:
                raise ValueError("cuda_graph requires cached=True")
            return self._generate_cuda_graph(prompt, max_tokens)
        if cached and cache_storage == "preallocated":
            head_dim = self.model.block.hidden // self.model.block.heads
            cache = (
                torch.empty((1, self.model.block.heads, self.model.context, head_dim), device=self.device),
                torch.empty((1, self.model.block.heads, self.model.context, head_dim), device=self.device),
                0,
            )
        generated_device, logits_trace = [], []
        for _ in range(max_tokens):
            if cached:
                input_tokens = tokens if cache is None or cache_storage == "preallocated" and cache[2] == 0 else tokens[:, -1:]
                if cache_storage == "preallocated":
                    logits, cache = self.model(input_tokens, preallocated_cache=cache)
                else:
                    logits, cache = self.model(input_tokens, cache, cached=True)
            else:
                logits = self.model(tokens)
            last = logits[:, -1]
            next_token = last.argmax(-1, keepdim=True)
            # Keep sampling on device; converting every token with ``item``
            # forces a host synchronization on each decode step.
            generated_device.append(next_token)
            logits_trace.append(last.clone())
            tokens = torch.cat((tokens, next_token), dim=1) if not cached else next_token
        generated = torch.cat(generated_device, dim=1)[0].tolist()
        return generated, logits_trace

    def complete(self, prompt, max_tokens, *, cache_storage="dynamic"):
        generated, _ = self.generate(prompt, max_tokens, cache_storage=cache_storage)
        return {"text": "".join(self.model.alphabet[i] for i in generated),
                "generated_tokens": len(generated), "prompt_tokens": len(self.encode(prompt)),
                "backend": self.backend}

    @torch.inference_mode()
    def stream(self, prompt, max_tokens, *, cached=True):
        """Yield one token event at a time for the bounded streaming endpoint."""
        ids = self.encode(prompt)
        if type(max_tokens) is not int or max_tokens < 1 or len(ids) + max_tokens > self.model.context:
            raise ValueError("positive max_tokens and prompt must fit 128-character context")
        tokens = torch.tensor([ids], dtype=torch.long, device=self.device)
        cache = None
        for index in range(max_tokens):
            if cached:
                logits, cache = self.model(tokens if cache is None else tokens[:, -1:], cache, cached=True)
            else:
                logits = self.model(tokens)
            next_token = logits[:, -1].argmax(-1, keepdim=True)
            token_id = int(next_token.item())
            yield {"index": index, "token": self.model.alphabet[token_id], "token_id": token_id}
            tokens = torch.cat((tokens, next_token), dim=1)

    def complete_batch(self, prompts, max_tokens):
        if not isinstance(prompts, list) or not prompts:
            raise ValueError("prompts must be a nonempty list")
        encoded = [self.encode(prompt) for prompt in prompts]
        if len({len(ids) for ids in encoded}) == 1:
            generated = self.generate_batch(prompts, max_tokens)
            mode = "vectorized"
            choices = [{"index": index, "text": "".join(self.model.alphabet[i] for i in tokens), "finish_reason": "length"}
                       for index, tokens in enumerate(generated)]
        else:
            mode = "serial-fallback"
            choices = []
            for index, prompt in enumerate(prompts):
                result = self.complete(prompt, max_tokens)
                choices.append({"index": index, "text": result["text"], "finish_reason": "length"})
        return {"choices": choices, "completion_tokens": len(prompts) * max_tokens,
                "prefix_tokens_reused": 0, "batch_mode": mode, "backend": self.backend}

    @torch.inference_mode()
    def generate_batch(self, prompts, max_tokens, *, cached=True):
        """Decode equal-length prompts as one tensor batch.

        A shared cache tuple has shape ``[batch, heads, sequence, head_dim]``.
        Equal prompt lengths are required so the prefill has no padding tokens;
        variable-length request batching must use a length-aware/paged cache,
        which this compact teaching model intentionally does not pretend to
        implement.
        """
        if not isinstance(prompts, list) or not prompts:
            raise ValueError("prompts must be a nonempty list")
        ids = [self.encode(prompt) for prompt in prompts]
        if len({len(row) for row in ids}) != 1:
            raise ValueError("generate_batch requires equal-length prompts")
        if type(max_tokens) is not int or max_tokens < 1 or len(ids[0]) + max_tokens > self.model.context:
            raise ValueError("positive max_tokens and prompts must fit 128-character context")
        tokens = torch.tensor(ids, dtype=torch.long, device=self.device)
        generated = [[] for _ in prompts]
        cache = None
        for _ in range(max_tokens):
            if cached:
                logits, cache = self.model(tokens if cache is None else tokens[:, -1:], cache, cached=True)
            else:
                logits = self.model(tokens)
            next_tokens = logits[:, -1].argmax(-1, keepdim=True)
            for index, token in enumerate(next_tokens[:, 0].tolist()):
                generated[index].append(int(token))
            tokens = torch.cat((tokens, next_tokens), dim=1)
        return generated
