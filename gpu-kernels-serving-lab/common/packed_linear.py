"""Inference-only packed storage; each call reconstructs FP32 weights."""
import copy
import torch
from torch import nn

from .packed_int4 import PackedInt4, pack_int4, unpack_int4


class PackedInt4Linear(nn.Module):
    def __init__(self, linear: nn.Linear, block=32):
        super().__init__()
        packed = pack_int4(linear.weight.detach(), block)
        self.in_features, self.out_features = linear.in_features, linear.out_features
        self.block = block
        self.register_buffer("payload", packed.payload)
        self.register_buffer("scales", packed.scales)
        self.register_buffer("bias", linear.bias.detach().clone() if linear.bias is not None else None)
        self.eval()

    def get_extra_state(self):
        return {"format": "local-int4-offset-nibbles-v1", "block": self.block,
                "shape": [self.out_features, self.in_features]}

    def set_extra_state(self, state):
        if state != self.get_extra_state():
            raise ValueError("packed linear metadata does not match destination architecture")

    @torch.no_grad()
    def forward(self, x):
        if self.training:
            raise ValueError("packed linear is inference-only; call eval()")
        if x.dtype != torch.float32 or x.device != self.payload.device:
            raise ValueError("FP32 input on the packed-weight device required")
        weights = unpack_int4(PackedInt4(self.payload, self.scales,
                                        (self.out_features, self.in_features), self.block))
        return torch.nn.functional.linear(x, weights, self.bias)


def converted_copy(model, block=32):
    """Copy a model and replace every Linear; do not alter the source model."""
    result = copy.deepcopy(model)
    def replace(module):
        if isinstance(module, nn.Linear):
            return PackedInt4Linear(module, block)
        for name, child in list(module.named_children()):
            setattr(module, name, replace(child))
        return module
    return replace(result).eval()


def tensor_storage_bytes(model):
    """Unique live parameter/buffer backing storage, excluding Python metadata."""
    storage = {}
    for tensor in (*model.parameters(), *model.buffers()):
        allocation = tensor.untyped_storage()
        storage[(str(tensor.device), allocation.data_ptr())] = allocation.nbytes()
    return sum(storage.values())
