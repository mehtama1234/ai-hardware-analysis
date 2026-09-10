"""Token-weighted evaluation with nonduplicated targets and bounded context."""
import math
import torch
import torch.nn.functional as F


@torch.no_grad()
def evaluate_tokens(model, tokens, *, sequence=64, device='cpu'):
    """Evaluate every target after token zero, resetting context per block.

    Adjacent blocks share one input token, never a scored target. This policy
    must stay fixed across arms; it is not sliding full-context perplexity.
    """
    if type(sequence) is not int or sequence < 1 or len(tokens) < 2:
        raise ValueError('positive sequence and at least two tokens required')
    was_training = model.training
    model.eval()
    rows = []
    try:
        for start in range(0, len(tokens) - 1, sequence):
            ids = torch.as_tensor(tokens[start:start + sequence + 1], dtype=torch.long, device=device).unsqueeze(0)
            logits = model(input_ids=ids[:, :-1], use_cache=False).logits
            nll = F.cross_entropy(logits.reshape(-1, logits.shape[-1]), ids[:, 1:].reshape(-1), reduction='sum')
            value = float(nll)
            if not math.isfinite(value):
                raise ValueError('nonfinite evaluation loss')
            rows.append({'target_start': start + 1, 'target_end': start + ids.numel(),
                'targets': ids.numel() - 1, 'nll_sum': value})
    finally:
        model.train(was_training)
    count = sum(row['targets'] for row in rows)
    mean = sum(row['nll_sum'] for row in rows) / count
    return {'targets': count, 'mean_nll': mean, 'perplexity': math.exp(mean) if mean < 700 else None,
        'context_policy': 'reset per block; one overlapping input; every target scored once', 'blocks': rows}
