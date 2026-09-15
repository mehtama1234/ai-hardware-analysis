#!/usr/bin/env python3
"""Persistent JSONL Hugging Face backend; loads model weights once."""
from __future__ import annotations
import json
import os
import sys
from pathlib import Path
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

constrained = os.environ.get("VERIFICATION_HF_JSON_CONSTRAINED", "0").strip() == "1"
if constrained:
    from lmformatenforcer import JsonSchemaParser
    from lmformatenforcer.integrations.transformers import build_transformers_prefix_allowed_tokens_fn

def resolve_model_path() -> str:
    configured = os.environ.get("VERIFICATION_HF_MODEL", "").strip()
    if configured:
        return configured
    candidates = [
        Path("/home/mehtama1/.cache/huggingface/Qwen2.5-0.5B-Instruct"),
        Path("/home/mehtama1/.cache/huggingface/smolLM2-360M-Instruct"),
    ]
    hub = Path(os.environ.get("HF_HOME", "/home/mehtama1/.cache/huggingface")) / "hub"
    for pattern in (
        "models--Qwen--Qwen2.5-Coder-0.5B-Instruct/snapshots/*",
        "models--HuggingFaceTB--SmolLM2-360M-Instruct/snapshots/*",
    ):
        candidates.extend(sorted(hub.glob(pattern), key=lambda item: item.stat().st_mtime, reverse=True))
    for candidate in candidates:
        if candidate.is_dir() and (candidate / "config.json").is_file():
            return str(candidate)
    return "Qwen/Qwen2.5-Coder-0.5B-Instruct"


model_path = resolve_model_path()
tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
requested_device = os.environ.get("VERIFICATION_HF_DEVICE", "auto").strip().lower()
if requested_device not in {"auto", "cpu", "cuda"}:
    raise SystemExit("VERIFICATION_HF_DEVICE must be auto, cpu, or cuda")
device = "cuda" if requested_device == "auto" and torch.cuda.is_available() else requested_device
if device == "auto":
    device = "cpu"
if device == "cuda" and not torch.cuda.is_available():
    raise SystemExit("VERIFICATION_HF_DEVICE=cuda requested but CUDA is unavailable")
model = AutoModelForCausalLM.from_pretrained(model_path, local_files_only=True).to(device)
model.eval()
max_tokens = int(os.environ.get("VERIFICATION_HF_MAX_NEW_TOKENS", "256"))


def bind_request_contract(payload: dict, request: dict, *, assertion_task: bool, repair_task: bool, signal: str, cycle: str) -> dict:
    """Attach fields whose values are fixed by the validated request.

    The model is still responsible for the substantive rationale and action.
    Provenance, proposal kind/status, and bounded repair/assertion choices are
    protocol fields; asking a small decoder to reproduce them is unnecessary
    generation noise and caused otherwise useful responses to be rejected.
    """
    bound = dict(payload)
    bound.setdefault("proposal_id", f"hf-{request.get('task', 'proposal')}-{request.get('design_id', request.get('requirement_id', 'unknown'))}")
    bound["kind"] = request.get("expected_kind") or ("check" if assertion_task else ("repair" if repair_task else "diagnosis"))
    bound["source_revision"] = request.get("allowed_source_revision", "")
    bound["evidence"] = request.get("evidence", [])
    bound["status"] = "review_required"
    if not repair_task:
        bound.setdefault("action", f"inspect {signal} at cycle {cycle}")
    if assertion_task:
        # The assertion is the planner's specification-grounded candidate;
        # never admit a model-paraphrased or RTL-derived replacement.
        if isinstance(request.get("assertion"), str):
            bound["assertion"] = request["assertion"]
    elif repair_task:
        choices = request.get("repair_operator_choices")
        if isinstance(request.get("repair_before"), str) and isinstance(request.get("repair_after"), str):
            # Benchmark contracts may use a domain-specific operator label;
            # only the orchestration's approval label is translated to the
            # executable exact-text patch operator.
            bound["edit_operator"] = (
                "exact_text_replace"
                if choices == ["approval_gated_copy_only"]
                else choices[0] if isinstance(choices, list) and choices else "exact_text_replace"
            )
            bound.setdefault("before", request["repair_before"])
            bound.setdefault("after", request["repair_after"])
        elif isinstance(choices, list) and choices:
            bound.setdefault("edit_operator", choices[0])
    return bound


for line in sys.stdin:
    if not line.strip():
        continue
    request = json.loads(line)
    assertion_task = request.get("task") == "generate_assertion"
    failure = request.get("failure", {})
    signal = str(failure.get("signal", "signal"))
    cycle = str(failure.get("cycle", "0"))
    expected_kind = request.get("expected_kind")
    repair_task = request.get("task") == "propose_repair" or expected_kind == "repair"
    repository_task = expected_kind in {"diagnosis", "next_action", "lemma"} and not assertion_task and not repair_task
    if assertion_task:
        system = ("You are a hardware formal-verification assistant. Return exactly one JSON object and no prose, markdown, or code fence. "
                  "Required keys are proposal_id, kind, source_revision, action, rationale, evidence, status, assertion. "
                  "kind must be check; status must be review_required; evidence must copy the supplied evidence list; "
                  "assertion must be one complete SystemVerilog assert property using only the supplied allowed signals; "
                  "copy the supplied request assertion string exactly into the assertion field; never claim closure.")
        user = "Generate one specification-grounded SVA assertion for this requirement and return the required JSON object: " + json.dumps(request, sort_keys=True)
    elif repair_task:
        operator_mode = (
            isinstance(request.get("repair_operator_choices"), list)
            and bool(request["repair_operator_choices"])
            and not (isinstance(request.get("repair_before"), str) and isinstance(request.get("repair_after"), str))
        )
        repair_fields = "proposal_id, kind, source_revision, action, rationale, evidence, status, edit_operator" if operator_mode else "proposal_id, kind, source_revision, action, rationale, evidence, status, before, after"
        repair_selection = "edit_operator must be selected exactly from the supplied bounded choices." if operator_mode else "before and after must be selected exactly from the supplied repair choices."
        system = ("You are a hardware repair assistant. Return exactly one JSON object and no prose, markdown, or code fence. "
                  f"Required keys are {repair_fields}. "
                  f"kind must be repair; status must be review_required; evidence must copy the supplied evidence list; never claim closure. {repair_selection} Explain the root cause in rationale.")
        user = "Propose a bounded repair for this observed RTL failure and return the required JSON object: " + json.dumps(request, sort_keys=True)
    elif repository_task:
        system = ("You are a hardware verification workflow agent. Return exactly one JSON object and no prose, markdown, or code fence. "
                  f"Required keys are proposal_id, kind, source_revision, action, rationale, evidence, status. kind must be {expected_kind}; "
                  "status must be review_required; evidence must copy the supplied evidence list; never claim closure. "
                  "Use only the supplied repository evidence.")
        user = "Perform the assigned repository verification role and return the required JSON object: " + json.dumps(request, sort_keys=True)
    else:
        system = ("You are a hardware verification assistant. Return exactly one JSON object and no prose, markdown, or code fence. "
                  "Required keys are proposal_id, kind, source_revision, action, rationale, evidence, status. "
                  "kind must be diagnosis; status must be review_required; evidence must copy the supplied evidence list; never claim closure. "
                  f"Set action exactly to: inspect {signal} at cycle {cycle}.")
        user = "Diagnose this observed failure and return the required JSON object: " + json.dumps(request, sort_keys=True)
    messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
    if hasattr(tokenizer, "apply_chat_template"):
        prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    else:
        prompt = system + "\n" + user + "\nJSON:"
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    generation_kwargs = {"max_new_tokens": max_tokens, "do_sample": False, "pad_token_id": tokenizer.eos_token_id}
    if constrained:
        schema = {
            "type": "object",
            "properties": {
                "proposal_id": {"type": "string"},
                "kind": {"const": expected_kind or ("check" if assertion_task else ("repair" if repair_task else "diagnosis"))},
                "source_revision": {"type": "string"},
                "action": {"enum": [f"inspect {signal} at cycle {cycle}"]} if not repair_task else {"type": "string"},
                "rationale": {"type": "string"},
                "evidence": {"type": "array", "items": {"type": "string"}},
                "status": {"const": "review_required"},
            },
            # The model must produce the substantive rationale and, for
            # diagnosis/repair, the action.  Request-bound protocol fields are
            # attached by bind_request_contract after decoding.
            "required": ["rationale"] + ([] if assertion_task else ["action"]),
            "additionalProperties": False,
        }
        if assertion_task:
            schema["properties"]["assertion"] = {"type": "string", "minLength": 1}
            schema["required"].append("assertion")
        if repair_task:
            operator_choices = request.get("repair_operator_choices")
            if isinstance(operator_choices, list) and operator_choices:
                schema["properties"].update({"edit_operator": {"enum": [item for item in operator_choices if isinstance(item, str)]}})
                schema["required"].append("edit_operator")
            else:
                before_choice = request.get("repair_before")
                after_choice = request.get("repair_after")
                schema["properties"].update({"before": {"enum": [before_choice]} if isinstance(before_choice, str) else {"type": "string"}, "after": {"enum": [after_choice]} if isinstance(after_choice, str) else {"type": "string"}})
                schema["required"].extend(["before", "after"])
        parser = JsonSchemaParser(schema)
        generation_kwargs["prefix_allowed_tokens_fn"] = build_transformers_prefix_allowed_tokens_fn(tokenizer, parser)
    with torch.inference_mode():
        outputs = model.generate(**inputs, **generation_kwargs)
    text = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
    start = text.find("{")
    if start < 0:
        print(json.dumps({"invalid_model_output": "model emitted no JSON"}), flush=True)
    else:
        try:
            payload, _ = json.JSONDecoder().raw_decode(text[start:])
        except json.JSONDecodeError:
            payload = {"invalid_model_output": "model emitted invalid JSON"}
        if isinstance(payload, dict):
            model_payload = dict(payload)
            payload = bind_request_contract(
                payload, request, assertion_task=assertion_task, repair_task=repair_task,
                signal=signal, cycle=cycle,
            )
            # Preserve the distinction between substantive model selection and
            # protocol fields attached by this adapter.  Downstream evaluation
            # may require the model to choose an exact bounded repair rather
            # than merely accepting a request-bound value.
            payload["_model_generated_fields"] = sorted(model_payload)
            payload["_request_bound_fields"] = sorted(set(payload) - set(model_payload))
            if repair_task:
                if isinstance(request.get("repair_before"), str) and isinstance(request.get("repair_after"), str):
                    payload["_model_selected_repair"] = (
                        model_payload.get("before") == request["repair_before"]
                        and model_payload.get("after") == request["repair_after"]
                    )
                elif isinstance(request.get("repair_operator_choices"), list):
                    payload["_model_selected_repair"] = model_payload.get("edit_operator") in request["repair_operator_choices"]
        print(json.dumps(payload), flush=True)
