"""Padded CPU/Gloo inference reference with sharded linear expert ownership."""
import torch
import torch.distributed as dist


def local_contract(tokens, logits, local_weights, top_k, capacity, world):
    if any(not isinstance(t, torch.Tensor) for t in (tokens, logits, local_weights)):
        raise ValueError("tensor inputs required")
    if local_weights.ndim != 3:
        raise ValueError("weights must have three dimensions")
    local_experts, output_width, width = local_weights.shape
    if min(local_experts, output_width, width) < 1:
        raise ValueError("positive expert/feature dimensions required")
    experts = local_experts * world
    if tokens.ndim != 2 or tokens.shape[1] != width or logits.shape != (len(tokens), experts):
        raise ValueError("incompatible token/logit/expert shapes")
    if any(t.device.type != "cpu" or t.dtype != tokens.dtype for t in (tokens, logits, local_weights)):
        raise ValueError("matching CPU tensors required")
    if tokens.dtype not in (torch.float32, torch.float64) or any(not torch.isfinite(t).all() for t in (tokens, logits, local_weights)):
        raise ValueError("finite FP32/FP64 inputs required")
    if type(top_k) is not int or not 1 <= top_k <= experts or type(capacity) is not int or capacity < 0:
        raise ValueError("invalid routing/capacity contract")
    return (local_experts, output_width, width, str(tokens.dtype), top_k, capacity)


def agree_contract(tokens, logits, local_weights, top_k, capacity):
    """Trusted local Gloo peers exchange small metadata before tensor traffic."""
    try:
        local = {"contract": local_contract(tokens, logits, local_weights, top_k, capacity, dist.get_world_size())}
    except (ValueError, TypeError, RuntimeError) as exc:
        local = {"error": str(exc)}
    gathered = [None] * dist.get_world_size()
    dist.all_gather_object(gathered, local)
    failures = [(rank, data["error"]) for rank, data in enumerate(gathered) if "error" in data]
    if failures:
        raise ValueError(f"invalid rank input: {failures}")
    if any(data["contract"] != gathered[0]["contract"] for data in gathered):
        raise ValueError("ranks disagree on expert dimensions, dtype, top_k or capacity")


@torch.no_grad()
def distributed_linear(tokens, logits, local_weights, *, top_k, capacity):
    """Global token order is rank then local token; expert ownership is contiguous.

    Validate metadata collectively before padded payload exchanges. All ranks
    must still enter this call; process loss requires the process-group timeout.
    """
    rank, world = dist.get_rank(), dist.get_world_size()
    if dist.get_backend() != "gloo":
        raise ValueError("this reference accepts CPU/Gloo only")
    agree_contract(tokens, logits, local_weights, top_k, capacity)
    local_experts, output_width, width = local_weights.shape
    experts = local_experts * world

    selected = torch.argsort(logits, dim=1, descending=True, stable=True)[:, :top_k]
    gates = torch.softmax(logits.gather(1, selected), dim=1)
    assignments = [(selected == expert).nonzero(as_tuple=False) for expert in range(experts)]
    counts = torch.tensor([len(a) for a in assignments], dtype=torch.int64)
    all_counts = [torch.empty_like(counts) for _ in range(world)]
    dist.all_gather(all_counts, counts)
    prior = sum(all_counts[:rank], torch.zeros_like(counts))
    kept = [a[:max(0, capacity - int(prior[e]))] for e, a in enumerate(assignments)]
    accepted = torch.zeros_like(selected, dtype=torch.bool)
    output = tokens.new_zeros((len(tokens), output_width))
    if capacity == 0:
        return output, accepted

    # First dimension is destination rank, then expert-local index and slots.
    sends = tokens.new_zeros((world, local_experts, capacity, width))
    for expert, pairs in enumerate(kept):
        if len(pairs):
            owner, local = divmod(expert, local_experts)
            sends[owner, local, :len(pairs)] = tokens[pairs[:, 0]]
            accepted[pairs[:, 0], pairs[:, 1]] = True
    received = torch.empty_like(sends)
    dist.all_to_all_single(received.flatten(), sends.flatten())

    # Received first dimension is source rank. Only locally owned weights exist.
    replies = tokens.new_zeros((world, local_experts, capacity, output_width))
    for local in range(local_experts):
        replies[:, local] = received[:, local] @ local_weights[local].T
    returned = torch.empty_like(replies)
    dist.all_to_all_single(returned.flatten(), replies.flatten())
    for expert, pairs in enumerate(kept):
        if len(pairs):
            owner, local = divmod(expert, local_experts)
            ids, slots = pairs.unbind(dim=1)
            output.index_add_(0, ids, returned[owner, local, :len(pairs)] * gates[ids, slots, None])
    return output, accepted
