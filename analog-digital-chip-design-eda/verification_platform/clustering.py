"""Deterministic regression failure clustering."""

from __future__ import annotations

from collections import defaultdict

from .triage import Failure


def cluster_failures(failures: list[Failure]) -> dict[str, list[Failure]]:
    """Group failures by observable mismatch, preserving input order within groups."""
    clusters: dict[str, list[Failure]] = defaultdict(list)
    for failure in failures:
        key = f"{failure.signal}:{failure.expected}->{failure.actual}"
        clusters[key].append(failure)
    return dict(clusters)
