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

    def __init__(self, context=128):
        super().__init__()
        self.context = context
        self.embedding = nn.Embedding(len(self.alphabet), 32)
        self.position = nn.Embedding(context, 32)
        self.block = TinyTransformerBlock(32, 4, False, "sdpa")
        self.norm = nn.LayerNorm(32)
        self.head = nn.Linear(32, len(self.alphabet), bias=False)

    def forward(self, tokens, cache=None, *, cached=False):
        offset = 0 if cache is None else cache[0].shape[-2]
        if tokens.ndim != 2 or tokens.shape[1] < 1 or offset + tokens.shape[1] > self.context:
            raise ValueError("nonempty tokens must fit context")
        x = self.embedding(tokens) + self.position(torch.arange(offset, offset + tokens.shape[1], device=tokens.device))
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

    def __init__(self, device="cpu"):
        # Preserve the caller's global RNG state; no request mutates weights.
        with torch.random.fork_rng(devices=[]):
            torch.manual_seed(151)
            self.model = CharacterModel().eval()
        self.device = torch.device(device)
        if self.device.type == "cuda" and not torch.cuda.is_available():
            raise RuntimeError("CUDA device requested but CUDA is unavailable")
        self.model = self.model.to(self.device)
        self.backend = f"untrained-character-transformer-{self.device.type}-kv"

    def encode(self, prompt):
        if not isinstance(prompt, str) or not prompt:
            raise ValueError("prompt must be a nonempty string")
        return [self.model.alphabet.find(c) if c in self.model.alphabet else 0 for c in prompt.lower()]

    @torch.inference_mode()
    def generate(self, prompt, max_tokens, *, cached=True):
        ids = self.encode(prompt)
        if type(max_tokens) is not int or max_tokens < 1 or len(ids) + max_tokens > self.model.context:
            raise ValueError("positive max_tokens and prompt must fit 128-character context")
        tokens = torch.tensor([ids], dtype=torch.long, device=self.device)
        cache = None
        generated, logits_trace = [], []
        for _ in range(max_tokens):
            if cached:
                logits, cache = self.model(tokens if cache is None else tokens[:, -1:], cache, cached=True)
            else:
                logits = self.model(tokens)
            last = logits[:, -1]
            next_token = last.argmax(-1, keepdim=True)
            generated.append(int(next_token.item()))
            logits_trace.append(last.clone())
            tokens = torch.cat((tokens, next_token), dim=1)
        return generated, logits_trace

    def complete(self, prompt, max_tokens):
        generated, _ = self.generate(prompt, max_tokens)
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
