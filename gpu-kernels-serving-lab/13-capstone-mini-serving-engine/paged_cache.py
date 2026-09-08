"""Reference paged KV-cache allocator for serving exercises.

Pages are fixed-size token blocks. A sequence owns a page table and logical
length; appending can span pages, while gather reconstructs the contiguous
oracle used by the compact transformer. This is CPU reference code, not a CUDA
kernel or a production eviction policy.
"""
from __future__ import annotations

from dataclasses import dataclass
import torch


@dataclass(frozen=True)
class SequenceHandle:
    sequence_id: int


class PagedKVCache:
    def __init__(self, *, capacity_pages: int, page_size: int, heads: int, head_dim: int,
                 dtype=torch.float32, device="cpu"):
        if min(capacity_pages, page_size, heads, head_dim) < 1:
            raise ValueError("cache dimensions must be positive")
        self.capacity_pages = capacity_pages
        self.page_size = page_size
        self.heads = heads
        self.head_dim = head_dim
        self.device = torch.device(device)
        self.keys = torch.empty((capacity_pages, heads, page_size, head_dim), dtype=dtype, device=device)
        self.values = torch.empty_like(self.keys)
        self.free_pages = list(range(capacity_pages))
        self.sequences: dict[int, tuple[list[int], int]] = {}
        self.next_id = 0

    def allocate(self) -> SequenceHandle:
        handle = SequenceHandle(self.next_id); self.next_id += 1
        self.sequences[handle.sequence_id] = ([], 0)
        return handle

    def append(self, handle: SequenceHandle, keys: torch.Tensor, values: torch.Tensor) -> None:
        if handle.sequence_id not in self.sequences:
            raise KeyError("unknown or freed sequence")
        if keys.shape != values.shape or keys.ndim != 3 or keys.shape[0:] != (self.heads, keys.shape[1], self.head_dim):
            raise ValueError("keys and values must be [heads, tokens, head_dim] with matching shape")
        if keys.device != self.device or values.device != self.device:
            raise ValueError("cache tensors must use cache device")
        pages, length = self.sequences[handle.sequence_id]
        needed = (length + keys.shape[1] + self.page_size - 1) // self.page_size
        if needed > len(pages):
            acquire = needed - len(pages)
            if acquire > len(self.free_pages):
                raise MemoryError("paged KV cache capacity exhausted")
            pages = pages + [self.free_pages.pop(0) for _ in range(acquire)]
        for offset in range(keys.shape[1]):
            logical = length + offset
            page_index, in_page = divmod(logical, self.page_size)
            page = pages[page_index]
            self.keys[page, :, in_page, :] = keys[:, offset, :]
            self.values[page, :, in_page, :] = values[:, offset, :]
        self.sequences[handle.sequence_id] = (pages, length + keys.shape[1])

    def gather(self, handle: SequenceHandle) -> tuple[torch.Tensor, torch.Tensor]:
        if handle.sequence_id not in self.sequences:
            raise KeyError("unknown or freed sequence")
        pages, length = self.sequences[handle.sequence_id]
        key = torch.empty((self.heads, length, self.head_dim), dtype=self.keys.dtype, device=self.device)
        value = torch.empty_like(key)
        for logical in range(length):
            page_index, in_page = divmod(logical, self.page_size)
            page = pages[page_index]
            key[:, logical, :] = self.keys[page, :, in_page, :]
            value[:, logical, :] = self.values[page, :, in_page, :]
        return key, value

    def length(self, handle: SequenceHandle) -> int:
        if handle.sequence_id not in self.sequences:
            raise KeyError("unknown or freed sequence")
        return self.sequences[handle.sequence_id][1]

    def free(self, handle: SequenceHandle) -> None:
        pages, _ = self.sequences.pop(handle.sequence_id)
        self.free_pages.extend(pages)
        self.free_pages.sort()

    def snapshot(self) -> dict:
        return {"capacity_pages": self.capacity_pages, "free_pages": len(self.free_pages),
                "active_sequences": len(self.sequences),
                "allocated_pages": sum(len(pages) for pages, _ in self.sequences.values())}
