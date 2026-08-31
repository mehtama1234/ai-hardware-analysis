from __future__ import annotations

import math

from .common import Check, emit


LAB_ID = "comp-lab-07-distributed-collectives"


def ring_all_reduce(bytes_per_rank: int, ranks: int, bandwidth_gbps: float, latency_us: float) -> float:
    steps = 2 * (ranks - 1)
    bytes_on_link = 2 * bytes_per_rank * (ranks - 1) / ranks
    return steps * latency_us / 1e6 + bytes_on_link / (bandwidth_gbps * 1e9)


def tree_all_reduce(bytes_per_rank: int, ranks: int, bandwidth_gbps: float, latency_us: float) -> float:
    levels = math.ceil(math.log2(ranks))
    return 2 * levels * latency_us / 1e6 + 2 * bytes_per_rank * levels / (bandwidth_gbps * 1e9)


def topology_bandwidth(topology: str) -> float:
    return {"pcie": 64.0, "nvlink": 300.0, "infiniband": 200.0}.get(topology, 32.0)


def choose_collective(bytes_per_rank: int, ranks: int, topology: str) -> dict[str, object]:
    bandwidth = topology_bandwidth(topology)
    latency = 5.0 if topology != "pcie" else 9.0
    ring = ring_all_reduce(bytes_per_rank, ranks, bandwidth, latency)
    tree = tree_all_reduce(bytes_per_rank, ranks, bandwidth, latency)
    return {"topology": topology, "ring_ms": round(ring * 1000, 4), "tree_ms": round(tree * 1000, 4), "best": "ring" if ring < tree else "tree"}


def run() -> dict[str, object]:
    small = choose_collective(4 * 1024, 8, "pcie")
    large = choose_collective(128 * 1024 * 1024, 8, "nvlink")
    scale = [choose_collective(32 * 1024 * 1024, ranks, "infiniband") for ranks in [2, 4, 8, 16]]
    checks = [
        Check("small_payload_prefers_tree", small["best"] == "tree", str(small)).__dict__,
        Check("large_payload_prefers_ring", large["best"] == "ring", str(large)).__dict__,
        Check("latency_grows_with_ranks", scale[-1]["ring_ms"] > scale[0]["ring_ms"], str(scale)).__dict__,
        Check("topology_changes_bandwidth", topology_bandwidth("nvlink") > topology_bandwidth("pcie"), "nvlink > pcie").__dict__,
    ]
    return {
        "summary": "Models ring/tree all-reduce choices across payload size, rank count, and topology.",
        "results": {"small": small, "large": large, "scale": scale},
        "checks": checks,
    }


def main() -> int:
    return emit(LAB_ID, run())


if __name__ == "__main__":
    raise SystemExit(main())
