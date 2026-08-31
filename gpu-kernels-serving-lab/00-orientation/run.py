"""Session 00: inventory the local AI/GPU stack."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.gpu_info import collect_inventory


def main() -> None:
    inventory = collect_inventory("00-orientation")
    out = {**inventory, "inventory": inventory}
    path = Path(__file__).with_name("out_orientation.json")
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    torch = out["torch"]
    packages = out["software"]["packages"]
    print("wrote", path.name)
    print("torch:", torch.get("version"), "cuda_available:", torch.get("cuda_available"))
    print("transformers:", packages.get("transformers"), "vllm:", packages.get("vllm"))


if __name__ == "__main__":
    main()
