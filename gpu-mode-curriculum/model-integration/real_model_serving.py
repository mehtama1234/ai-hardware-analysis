"""Local-only Hugging Face causal-LM adapter for the serving boundary.

The adapter deliberately keeps model loading and request execution explicit.
It is useful for connecting a real trained checkpoint to the teaching HTTP
server, but ``transformers.generate`` is not interruptible in the middle of a
call; cancellation is therefore reported as boundary-only.
"""

from __future__ import annotations

import threading
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


class HuggingFaceGenerator:
    """Small synchronous adapter implementing the mini-server generator API."""

    cancellation_mode = "boundary-only"

    def __init__(
        self,
        model_path: str | Path,
        *,
        device: str = "cpu",
        use_cache: bool = True,
        chat_template: bool = True,
    ) -> None:
        self.model_path = str(Path(model_path).expanduser().resolve())
        self.device = torch.device(device)
        if self.device.type == "cuda" and not torch.cuda.is_available():
            raise RuntimeError("CUDA device requested but CUDA is unavailable")
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_path, local_files_only=True
        )
        if self.tokenizer.pad_token_id is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        self.tokenizer.padding_side = "left"
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_path, local_files_only=True, torch_dtype=torch.float32
        ).to(self.device).eval()
        self.use_cache = bool(use_cache)
        self.chat_template = bool(chat_template and self.tokenizer.chat_template)
        self.model_name = Path(self.model_path).name
        self.backend = f"huggingface-{self.model_name}-{'cached' if self.use_cache else 'uncached'}"
        self._lock = threading.Lock()

    def _format(self, prompt: str) -> str:
        if self.chat_template:
            return self.tokenizer.apply_chat_template(
                [{"role": "user", "content": prompt}],
                tokenize=False,
                add_generation_prompt=True,
            )
        return prompt

    def encode(self, prompt: str) -> list[int]:
        if not isinstance(prompt, str) or not prompt:
            raise ValueError("prompt must be a nonempty string")
        return self.tokenizer(self._format(prompt), add_special_tokens=False)["input_ids"]

    def _generate(self, prompts: list[str], max_tokens: int) -> list[list[int]]:
        if type(max_tokens) is not int or not 1 <= max_tokens <= 128:
            raise ValueError("max_tokens must be an integer from 1 to 128")
        formatted = [self._format(prompt) for prompt in prompts]
        batch = self.tokenizer(
            formatted,
            return_tensors="pt",
            padding=True,
            truncation=False,
            add_special_tokens=False,
        )
        batch = {key: value.to(self.device) for key, value in batch.items()}
        padded_length = batch["input_ids"].shape[1]
        with self._lock, torch.inference_mode():
            output = self.model.generate(
                **batch,
                max_new_tokens=max_tokens,
                do_sample=False,
                use_cache=self.use_cache,
                pad_token_id=self.tokenizer.pad_token_id,
            )
        return [row[padded_length:].tolist() for row in output]

    def complete(self, prompt: str, max_tokens: int, *, cancel_event=None) -> dict:
        if cancel_event is not None and cancel_event.is_set():
            raise RuntimeError("request cancelled before model boundary")
        generated = self._generate([prompt], max_tokens)[0]
        return {
            "text": self.tokenizer.decode(generated, skip_special_tokens=True),
            "generated_tokens": len(generated),
            "prompt_tokens": len(self.encode(prompt)),
            "backend": self.backend,
        }

    def complete_batch(self, prompts: list[str], max_tokens: int, *, cancel_events=None) -> dict:
        if not prompts:
            raise ValueError("prompts must be nonempty")
        if cancel_events and any(event.is_set() for event in cancel_events):
            raise RuntimeError("batch cancelled before model boundary")
        generated = self._generate(prompts, max_tokens)
        return {
            "choices": [
                {
                    "index": index,
                    "text": self.tokenizer.decode(tokens, skip_special_tokens=True),
                    "finish_reason": "length",
                }
                for index, tokens in enumerate(generated)
            ],
            "completion_tokens": sum(len(tokens) for tokens in generated),
            "prefix_tokens_reused": 0,
            "batch_mode": "transformers-batched",
            "backend": self.backend,
        }

