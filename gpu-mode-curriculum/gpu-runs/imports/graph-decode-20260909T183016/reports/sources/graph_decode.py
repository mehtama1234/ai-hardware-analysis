"""Fixed-capacity GPT-2 decode, with the same step run eagerly or in a CUDA graph.

Prefill stays in Transformers. Decode uses the model's actual trained weights.
This deliberately supports ordinary eager GPT-2 only: no cross attention,
upcast/reordered attention, pruning, training, or per-slot admission yet.
"""
import math
import torch


class GraphDecode:
    def __init__(self, model, batch_size, capacity):
        config = model.config
        if model.training or config.add_cross_attention or config.reorder_and_upcast_attn:
            raise ValueError('requires eval GPT-2 without cross/upcast attention')
        if config._attn_implementation != 'eager' or any(b.attn.num_heads != config.n_head for b in model.transformer.h):
            raise ValueError('requires unpruned eager attention')
        if not 0 < capacity <= config.n_positions or batch_size < 1:
            raise ValueError('invalid batch/capacity')
        self.model, self.batch_size, self.capacity = model, batch_size, capacity
        device = next(model.parameters()).device
        shape = (batch_size, config.n_head, capacity, config.n_embd // config.n_head)
        self.keys = [torch.zeros(shape, dtype=model.dtype, device=device) for _ in model.transformer.h]
        self.values = [torch.zeros_like(k) for k in self.keys]
        self.ids = torch.zeros((batch_size, 1), dtype=torch.long, device=device)
        self.positions = torch.zeros_like(self.ids)
        self.cursor = torch.zeros(1, dtype=torch.long, device=device)
        self.mask = torch.zeros((batch_size, capacity), dtype=torch.bool, device=device)
        self.graph = None
        self.remaining = 0
        self.logits = None

    @torch.inference_mode()
    def prepare(self, encoded, max_new_tokens):
        ids, mask = encoded['input_ids'], encoded['attention_mask']
        width = ids.shape[1]
        if ids.shape[0] != self.batch_size or max_new_tokens < 1 or width + max_new_tokens > self.capacity:
            raise ValueError('request exceeds fixed batch/capacity')
        if not bool(((mask == 0) | (mask == 1)).all()) or not bool((mask[:, -1] == 1).all()):
            raise ValueError('requires nonempty left-padded prompts')
        if bool((mask[:, 1:] < mask[:, :-1]).any()):
            raise ValueError('requires contiguous left padding')
        positions = mask.long().cumsum(-1) - 1
        positions.masked_fill_(mask == 0, 1)
        out = self.model(input_ids=ids, attention_mask=mask, position_ids=positions, use_cache=True)
        for i, layer in enumerate(out.past_key_values.layers):
            self.keys[i].zero_()
            self.values[i].zero_()
            self.keys[i][:, :, :width].copy_(layer.keys)
            self.values[i][:, :, :width].copy_(layer.values)
        self.mask.zero_()
        self.mask[:, :width].copy_(mask.bool())
        self.cursor.fill_(width)
        self.positions.copy_(mask.long().sum(-1, keepdim=True))
        self.ids.copy_(out.logits[:, -1].argmax(-1, keepdim=True))
        self.remaining = max_new_tokens - 1
        return self.ids[:, 0].clone()

    def _step(self):
        core = self.model.transformer
        hidden = core.wte(self.ids) + core.wpe(self.positions)
        self.mask.index_fill_(1, self.cursor, True)
        for i, block in enumerate(core.h):
            residual = hidden
            q, k, v = block.attn.c_attn(block.ln_1(hidden)).split(self.model.config.n_embd, dim=2)
            def heads(x):
                return x.view(self.batch_size, 1, block.attn.num_heads, block.attn.head_dim).transpose(1, 2)
            q, k, v = heads(q), heads(k), heads(v)
            self.keys[i].index_copy_(2, self.cursor, k)
            self.values[i].index_copy_(2, self.cursor, v)
            scores = q @ self.keys[i].transpose(-1, -2)
            scaling = 1 / math.sqrt(block.attn.head_dim) if self.model.config.scale_attn_weights else 1.0
            if self.model.config.scale_attn_by_inverse_layer_idx:
                scaling /= float(i + 1)
            scores = scores * scaling
            scores = scores.masked_fill(~self.mask[:, None, None, :], torch.finfo(scores.dtype).min)
            weights = scores.softmax(-1).to(v.dtype)
            attention = (weights @ self.values[i]).transpose(1, 2).reshape(self.batch_size, 1, -1)
            hidden = residual + block.attn.c_proj(attention)
            hidden = hidden + block.mlp(block.ln_2(hidden))
        self.logits = self.model.lm_head(core.ln_f(hidden))[:, -1]
        self.ids.copy_(self.logits.argmax(-1, keepdim=True))
        self.positions.add_(1)
        self.cursor.add_(1)

    @torch.inference_mode()
    def capture(self):
        if self.ids.device.type != 'cuda':
            raise RuntimeError('CUDA required for graph capture')
        if self.graph is not None:
            raise RuntimeError('graph already captured')
        # Warm-up and capture mutate scratch state. prepare() must follow capture.
        stream = torch.cuda.Stream(device=self.ids.device)
        stream.wait_stream(torch.cuda.current_stream(self.ids.device))
        with torch.cuda.stream(stream):
            for _ in range(3):
                self.cursor.zero_()
                self.positions.zero_()
                self._step()
        torch.cuda.current_stream(self.ids.device).wait_stream(stream)
        torch.cuda.synchronize(self.ids.device)
        self.cursor.zero_()
        self.positions.zero_()
        graph = torch.cuda.CUDAGraph()
        with torch.cuda.graph(graph):
            self._step()
        self.graph = graph
        self.remaining = 0

    @torch.inference_mode()
    def step(self, use_graph=False):
        if self.remaining <= 0:
            raise RuntimeError('prepare required or generation budget exhausted')
        if use_graph:
            if self.graph is None:
                raise RuntimeError('capture required')
            self.graph.replay()
        else:
            self._step()
        self.remaining -= 1
        return self.ids[:, 0].clone()

    @torch.inference_mode()
    def generate(self, encoded, max_new_tokens, use_graph=False):
        tokens = [self.prepare(encoded, max_new_tokens)]
        for _ in range(max_new_tokens - 1):
            tokens.append(self.step(use_graph))
        return torch.stack(tokens, dim=1)
