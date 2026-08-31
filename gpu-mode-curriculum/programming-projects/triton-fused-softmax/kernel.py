import torch

try:
    import triton
    import triton.language as tl
except Exception:  # pragma: no cover - import depends on environment.
    triton = None
    tl = None


def torch_softmax(x: torch.Tensor) -> torch.Tensor:
    return torch.softmax(x, dim=-1)


def main() -> None:
    x = torch.randn((4, 128), dtype=torch.float32)
    y = torch_softmax(x)
    print({"status": "cpu-baseline", "shape": list(y.shape), "row0_sum": round(float(y[0].sum()), 6)})


if __name__ == "__main__":
    main()
