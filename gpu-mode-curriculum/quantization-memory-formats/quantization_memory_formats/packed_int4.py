"""Row-wise symmetric int4 packing for weight-only experiments."""
from dataclasses import dataclass
import torch


@dataclass(frozen=True)
class PackedInt4:
    data: torch.Tensor       # uint8, two signed nibbles per column
    scales: torch.Tensor     # float scale per row
    shape: tuple

    @property
    def storage_bytes(self):
        return self.data.numel() + self.scales.numel() * self.scales.element_size()

    def dequantize(self, dtype=torch.float32):
        values = self.data
        low = (values & 0x0F).to(torch.int16)
        high = (values >> 4).to(torch.int16)
        low = torch.where(low >= 8, low - 16, low)
        high = torch.where(high >= 8, high - 16, high)
        out = torch.stack((low, high), dim=-1).reshape(self.shape).to(dtype)
        return out * self.scales[:, None].to(dtype)


def pack_int4(weight):
    """Pack a 2-D floating weight row-wise with signed range [-7, 7]."""
    if weight.ndim != 2 or weight.shape[1] % 2 or not weight.is_floating_point():
        raise ValueError('expected 2-D floating weight with an even column count')
    finite = torch.isfinite(weight)
    if not bool(finite.all()):
        raise ValueError('weight contains nonfinite values')
    maximum = weight.abs().amax(dim=1)
    scales = torch.where(maximum == 0, torch.ones_like(maximum), maximum / 7)
    q = torch.round(weight / scales[:, None]).clamp(-8, 7).to(torch.int16)
    # Negative nibbles use two's-complement representation.
    packed = ((q[:, 0::2] & 0x0F) | ((q[:, 1::2] & 0x0F) << 4)).to(torch.uint8)
    return PackedInt4(packed, scales, tuple(weight.shape))


def linear(x, packed, bias=None):
    """Reference dequantize-then-GEMM path; not a native int4 kernel."""
    if x.ndim != 2 or x.shape[1] != packed.shape[1]:
        raise ValueError('incompatible input shape')
    if bias is not None and bias.shape != (packed.shape[0],):
        raise ValueError('incompatible bias shape')
    return x @ packed.dequantize(x.dtype).t() + (bias if bias is not None else 0)
