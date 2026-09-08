"""CPU mathematical MoE reference with explicit unique routing and capacity."""
import torch


def routed_linear(tokens, logits, expert_weights, *, top_k, capacity):
    """Route T-by-D tokens through E linear experts of shape E-by-O-by-D.

    Select distinct experts by descending logits, breaking ties by expert index.
    Normalize selected logits before dropping. Each expert accepts its first
    `capacity` assignments in token order; dropped mass is not renormalized.
    Routing indices and capacity decisions are discrete, not differentiable.
    """
    tensors = (tokens, logits, expert_weights)
    if any(not isinstance(t, torch.Tensor) for t in tensors):
        raise ValueError("expected tensors")
    if tokens.ndim != 2 or logits.ndim != 2 or expert_weights.ndim != 3:
        raise ValueError("expected tokens[T,D], logits[T,E], weights[E,O,D]")
    count, width = tokens.shape
    experts, output_width, input_width = expert_weights.shape
    if min(width, experts, output_width) < 1 or input_width != width or logits.shape != (count, experts):
        raise ValueError("incompatible or empty feature/expert dimensions")
    if type(top_k) is not int or not 1 <= top_k <= experts:
        raise ValueError("top_k must be an integer in [1,E]")
    if type(capacity) is not int or capacity < 0:
        raise ValueError("capacity must be a nonnegative integer")
    if any(t.device.type != "cpu" or t.dtype != tokens.dtype for t in tensors) or tokens.dtype not in (torch.float32, torch.float64):
        raise ValueError("CPU FP32/FP64 tensors with identical dtype required")
    if any(not torch.isfinite(t).all() for t in tensors):
        raise ValueError("non-finite input")

    selected = torch.argsort(logits, dim=1, descending=True, stable=True)[:, :top_k]
    gates = torch.softmax(logits.gather(1, selected), dim=1)
    accepted = torch.zeros((count, top_k), dtype=torch.bool)
    output = tokens.new_zeros((count, output_width))
    # Preserve zero derivatives even when every assignment is dropped.
    output = output + sum((t * 0).sum() for t in tensors)
    offered_loads, accepted_loads = [], []
    for expert in range(experts):
        assignments = (selected == expert).nonzero(as_tuple=False)
        offered_loads.append(len(assignments))
        kept = assignments[:capacity]
        accepted_loads.append(len(kept))
        if len(kept):
            token_ids, slots = kept.unbind(dim=1)
            accepted[token_ids, slots] = True
            computed = tokens[token_ids] @ expert_weights[expert].T
            output = output.index_add(0, token_ids, computed * gates[token_ids, slots, None])
    return output, {"expert_indices": selected, "gates": gates,
                    "accepted": accepted, "offered_loads": offered_loads,
                    "accepted_loads": accepted_loads,
                    "dropped_assignments": count * top_k - sum(accepted_loads)}
