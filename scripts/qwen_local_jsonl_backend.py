#!/usr/bin/env python3
"""Resident local Qwen JSONL adapter for supplemental CPU-only evaluation.

The adapter emits only reviewable proposal objects.  It never applies a patch
and never upgrades a proposal into verification closure.  The model path is
intentionally supplied by the environment so the committed repository does
not embed a machine-local cache path as evidence.
"""
from __future__ import annotations

import json
import os
import re
import sys
import traceback

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


MODEL_PATH = os.environ.get("QWEN_LOCAL_MODEL_PATH", "").strip()
if not MODEL_PATH:
    raise SystemExit("QWEN_LOCAL_MODEL_PATH is required")
torch.set_num_threads(int(os.environ.get("QWEN_CPU_THREADS", "2")))
try:
    MAX_NEW_TOKENS = max(16, int(os.environ.get("QWEN_MAX_NEW_TOKENS", "192")))
except ValueError:
    MAX_NEW_TOKENS = 192
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, local_files_only=True)
model = AutoModelForCausalLM.from_pretrained(MODEL_PATH, local_files_only=True, torch_dtype=torch.float32)
model.eval()


def extract_json(text: str) -> dict[str, object]:
    candidates = re.findall(r"\{.*\}", text, flags=re.DOTALL)
    if not candidates:
        raise ValueError("model emitted no JSON object")
    for candidate in reversed(candidates):
        try:
            value = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            return value
    raise ValueError("model emitted no parseable JSON object")


def complete(request: dict[str, object]) -> dict[str, object]:
    role = str(request.get("role", ""))
    expected_kind = str(request.get("expected_kind", ""))
    required = {
        "proposal_id": "short stable identifier",
        "kind": expected_kind,
        "source_revision": str(request.get("allowed_source_revision", "")),
        "action": "one bounded review-only action",
        "rationale": "evidence-grounded rationale; do not claim closure",
        "evidence": request.get("evidence", []),
        "status": "review_required",
    }
    if role == "repair_proposer":
        required["repair_choice"] = "declared_repair or reject_repair"
        prompt_suffix = " For repair_choice, output exactly one of the literal strings declared_repair or reject_repair; never repeat the explanatory label."
    else:
        prompt_suffix = ""
    prompt = (
        "Return exactly one JSON object and no markdown. You are a bounded hardware verification agent. "
        "Use only the supplied request. Do not invent evidence, file names, line numbers, test results, "
        "or closure claims. The JSON must contain these fields and values/types:\n"
        + json.dumps(required, sort_keys=True)
        + "\nREQUEST:\n"
        + json.dumps(request, sort_keys=True)
        + prompt_suffix
    )
    messages = [
        {"role": "system", "content": "Output one conservative reviewable proposal JSON object."},
        {"role": "user", "content": prompt},
    ]
    encoded = tokenizer.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt")
    input_ids = encoded["input_ids"] if hasattr(encoded, "__getitem__") else encoded
    with torch.no_grad():
        generated = model.generate(input_ids, attention_mask=encoded.get("attention_mask"), max_new_tokens=MAX_NEW_TOKENS, do_sample=False, pad_token_id=tokenizer.eos_token_id)
    text = tokenizer.decode(generated[0][input_ids.shape[-1]:], skip_special_tokens=True)
    if os.environ.get("QWEN_DEBUG_RAW") == "1":
        print(f"QWEN_RAW role={role}: {text!r}", file=sys.stderr, flush=True)
    payload = extract_json(text)
    # Bind transport-invariant fields from the request rather than asking a
    # small local model to copy them reliably.  The substantive fields remain
    # model-generated, especially repair_choice; the metadata makes this
    # distinction auditable to agent_team.py.
    generated_fields = sorted(payload)
    bound = {
        "proposal_id": f"qwen-{request.get('role', 'agent')}-{request.get('task_id', 'task')}",
        "kind": expected_kind,
        "source_revision": request.get("allowed_source_revision", ""),
        "evidence": request.get("evidence", []),
        "status": "review_required",
    }
    payload.update(bound)
    payload["_model_generated_fields"] = generated_fields
    payload["_request_bound_fields"] = sorted(bound)
    return payload


for line in sys.stdin:
    try:
        request = json.loads(line)
        payload = complete(request)
        print(json.dumps(payload, sort_keys=True), flush=True)
    except Exception as exc:  # the platform records invalid/blocked transport output
        if os.environ.get("QWEN_DEBUG_RAW") == "1":
            traceback.print_exc(file=sys.stderr)
        print(json.dumps({"error": f"qwen-local-backend:{type(exc).__name__}:{exc}"}), flush=True)
