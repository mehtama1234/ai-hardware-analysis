from dataclasses import dataclass


@dataclass(frozen=True)
class Request:
    prompt_tokens: int
    output_tokens: int
    shared_prefix_tokens: int = 0


def kv_blocks(requests: list[Request], block_size: int = 16) -> int:
    total = 0
    for req in requests:
        private_prompt = max(0, req.prompt_tokens - req.shared_prefix_tokens)
        total += (private_prompt + req.output_tokens + block_size - 1) // block_size
    return total


def main() -> None:
    requests = [Request(768, 96, 512), Request(896, 96, 512), Request(512, 128, 384)]
    print({"status": "ran", "requests": len(requests), "kv_blocks": kv_blocks(requests)})


if __name__ == "__main__":
    main()
