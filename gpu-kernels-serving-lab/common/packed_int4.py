"""Teaching format: signed symmetric INT4, two offset-coded nibbles per byte.

Per-block FP32 scales, codes -7..7 encoded as code+8, low nibble first.
This is a local format, not NVFP4, MXFP4, or a vendor kernel layout.
"""
from dataclasses import dataclass
import math
import torch


@dataclass(frozen=True)
class PackedInt4:
    payload: torch.Tensor
    scales: torch.Tensor
    shape: tuple[int, ...]
    block: int

    @property
    def tensor_storage_bytes(self):
        """Actual backing-storage bytes; excludes Python objects/shape metadata."""
        return self.payload.untyped_storage().nbytes() + self.scales.untyped_storage().nbytes()


@torch.no_grad()
def pack_int4(weights, block=32):
    if not isinstance(block, int) or isinstance(block, bool) or block < 1:
        raise ValueError("block must be a positive integer")
    if weights.dtype != torch.float32 or weights.numel() == 0 or not bool(torch.isfinite(weights).all()):
        raise ValueError("nonempty finite FP32 weights required")
    flat = weights.flatten()
    count = flat.numel()
    padded = torch.nn.functional.pad(flat, (0, (-count) % block)).reshape(-1, block)
    maxima = padded.abs().amax(dim=1)
    scales = (maxima / 7).clamp_min(torch.finfo(torch.float32).tiny)
    scales = torch.where(maxima == 0, torch.ones_like(scales), scales).contiguous()
    signed = (padded / scales[:, None]).round().clamp(-7, 7).to(torch.int16).flatten()[:count]
    codes = (signed + 8).to(torch.uint8)
    if count % 2:
        codes = torch.cat((codes, codes.new_tensor([8])))
    payload = (codes[::2] | (codes[1::2] << 4)).contiguous()
    return PackedInt4(payload, scales, tuple(weights.shape), block)


@torch.no_grad()
def unpack_int4(packed):
    count = math.prod(packed.shape)
    if not isinstance(packed.block, int) or isinstance(packed.block, bool) or packed.block < 1:
        raise ValueError("invalid block")
    if count < 1 or any(not isinstance(n, int) or n < 1 for n in packed.shape):
        raise ValueError("invalid shape")
    if packed.payload.dtype != torch.uint8 or packed.payload.ndim != 1 or packed.payload.numel() != (count + 1) // 2:
        raise ValueError("invalid payload")
    if packed.scales.dtype != torch.float32 or packed.scales.shape != ((count + packed.block - 1) // packed.block,) or \
       packed.scales.device != packed.payload.device or not bool(torch.isfinite(packed.scales).all()) or not bool((packed.scales > 0).all()):
        raise ValueError("invalid scales")
    codes = torch.stack((packed.payload & 15, packed.payload >> 4), dim=1).flatten()[:count]
    if bool((codes == 0).any()):
        raise ValueError("reserved nibble code 0")
    signed = codes.to(torch.float32) - 8
    scales = packed.scales.repeat_interleave(packed.block)[:count]
    return (signed * scales).reshape(packed.shape)
