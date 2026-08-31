def ring_all_reduce_seconds(bytes_per_rank: int, ranks: int, bandwidth_gbps: float, latency_us: float) -> float:
    steps = 2 * (ranks - 1)
    bytes_on_link = 2 * bytes_per_rank * (ranks - 1) / ranks
    return steps * latency_us / 1e6 + bytes_on_link / (bandwidth_gbps * 1e9)


def main() -> None:
    seconds = ring_all_reduce_seconds(128 * 1024 * 1024, ranks=8, bandwidth_gbps=300, latency_us=4)
    print({"status": "ran", "ring_all_reduce_ms": round(seconds * 1000, 4)})


if __name__ == "__main__":
    main()
