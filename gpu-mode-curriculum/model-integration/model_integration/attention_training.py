"""Paired multi-step training equivalence for the existing tiny transformer."""
import copy
import time
import torch

from .tiny_transformer import TinyTransformerBlock


def checked_error(actual, expected):
    if actual is None or expected is None:
        raise AssertionError("missing gradient or parameter")
    torch.testing.assert_close(actual, expected, atol=2e-6, rtol=2e-5)
    if not bool(torch.isfinite(actual).all()) or not bool(torch.isfinite(expected).all()):
        raise AssertionError("nonfinite result")
    return float((actual - expected).abs().max().item())


def run_training_case(sequence=17, steps=3, *, compile_candidate=False, benchmark=False, device="cpu"):
    if sequence < 1 or steps < 1:
        raise ValueError("positive sequence and steps required")
    device = torch.device(device)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA requested but no CUDA device is available")
    # Restore caller RNG state; inputs use an independent generator too.
    fork_devices = [device] if device.type == "cuda" else []
    with torch.random.fork_rng(devices=fork_devices):
        torch.manual_seed(71)
        reference = TinyTransformerBlock(16, 2, False, attention_backend="sdpa").to(device)
    candidate = copy.deepcopy(reference)
    candidate.attention_backend = "sdpa" if compile_candidate else "recomputed"
    candidate_execution = torch.compile(candidate, backend="inductor", fullgraph=True) if compile_candidate else candidate
    optimizers = [torch.optim.SGD(model.parameters(), lr=0.01, momentum=0.9)
                  for model in (reference, candidate)]
    generator = torch.Generator(device=device).manual_seed(72)
    rows = []
    for step in range(steps):
        x = torch.randn((2, sequence, 16), generator=generator, device=device)
        target = torch.randn((2, sequence, 16), generator=generator, device=device)
        inputs = [x.clone().requires_grad_(), x.clone().requires_grad_()]
        outputs, losses = [], []
        for model, optimizer, tensor in zip((reference, candidate_execution), optimizers, inputs):
            optimizer.zero_grad(set_to_none=True)
            output = model(tensor)
            loss = (output - target).square().mean()
            loss.backward()
            outputs.append(output)
            losses.append(loss)
        output_error = checked_error(outputs[1], outputs[0])
        loss_error = checked_error(losses[1], losses[0])
        input_gradient_error = checked_error(inputs[1].grad, inputs[0].grad)
        parameters = dict(candidate.named_parameters())
        gradient_errors = {name: checked_error(parameters[name].grad, param.grad)
                           for name, param in reference.named_parameters()}
        for optimizer in optimizers:
            optimizer.step()
        parameter_errors = {name: checked_error(parameters[name], param)
                            for name, param in reference.named_parameters()}
        momentum_errors = {name: checked_error(optimizers[1].state[parameters[name]]["momentum_buffer"],
                                               optimizers[0].state[param]["momentum_buffer"])
                           for name, param in reference.named_parameters()}
        rows.append({"step": step, "reference_loss": float(losses[0].item()),
            "candidate_loss": float(losses[1].item()), "loss_abs_error": loss_error,
            "output_max_abs_error": output_error, "input_gradient_max_abs_error": input_gradient_error,
            "parameter_gradient_errors": gradient_errors, "updated_parameter_errors": parameter_errors,
            "optimizer_momentum_errors": momentum_errors, "status": "passed"})
    timing = None
    if benchmark:
        models = (reference, candidate)
        executions = (reference, candidate_execution)
        model_states = [copy.deepcopy(model.state_dict()) for model in models]
        optimizer_states = [copy.deepcopy(optimizer.state_dict()) for optimizer in optimizers]
        samples = [[], []]
        for repeat in range(13):
            # Alternate order; restore identical per-backend starting state outside
            # the timing interval. Initial correctness checks already compare states.
            for index in ((0, 1) if repeat % 2 == 0 else (1, 0)):
                models[index].load_state_dict(model_states[index])
                optimizers[index].load_state_dict(copy.deepcopy(optimizer_states[index]))
                tensor = x.clone().requires_grad_()
                started = time.perf_counter()
                optimizers[index].zero_grad(set_to_none=True)
                loss = (executions[index](tensor) - target).square().mean()
                loss.backward()
                optimizers[index].step()
                if device.type == "cuda":
                    torch.cuda.synchronize(device)
                elapsed = time.perf_counter() - started
                if repeat >= 3:
                    samples[index].append(elapsed)
        timing = {"reference_seconds": samples[0], "candidate_seconds": samples[1],
                  "warmup_pairs": 3, "measured_pairs": 10, "order": "alternating reference/candidate",
                  "scope": "CPU host wall zero_grad, forward, MSE, backward and eager SGD step; state reset/input clone excluded; fixed final training batch; no compilation expected after correctness and warmup"}
    return {"sequence": sequence, "batch": 2, "hidden": 16, "heads": 2,
            "steps": rows, "evidence_kind": f"measured_{device.type}", "seed_model": 71,
            "seed_data": 72, "optimizer": "SGD lr=0.01 momentum=0.9",
            "reference": "PyTorch SDPA", "candidate": "Inductor compiled SDPA transformer" if compile_candidate else "blockwise recomputed PyTorch attention",
            "atol": 2e-6, "rtol": 2e-5, "status": "passed", "timing": timing,
            "device": str(device)}
