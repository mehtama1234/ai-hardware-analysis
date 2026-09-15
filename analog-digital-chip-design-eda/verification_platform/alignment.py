"""Conservative cross-language signal alignment for debug traces."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import re
from functools import lru_cache
from typing import Iterable


@dataclass(frozen=True)
class Alignment:
    reference: str
    rtl: str | None
    score: float
    status: str
    reasons: tuple[str, ...]
    candidates: tuple[dict[str, object], ...] = ()
    score_components: dict[str, float] | None = None

    def record(self) -> dict[str, object]:
        payload = asdict(self)
        payload["reasons"] = list(self.reasons)
        payload["candidates"] = list(self.candidates)
        payload["score_components"] = dict(self.score_components or {})
        return payload


def _canonical_name(name: str) -> str:
    value = re.sub(r"^(gld|golden|ref|rtl|dut)[_$]", "", name.lower())
    return re.sub(r"[^a-z0-9]", "", value)


def _trace_score(left: Iterable[tuple[int, str]], right: Iterable[tuple[int, str]]) -> float:
    a, b = list(left), list(right)
    if not a or not b or len(a) != len(b):
        return 0.0
    same = sum(x == y for x, y in zip(a, b))
    return same / len(a)


def _candidate(
    reference: str,
    rtl: str,
    reference_trace: list[tuple[int, str]],
    rtl_trace: list[tuple[int, str]],
    reference_neighbors: set[str] | None = None,
    rtl_neighbors: set[str] | None = None,
    reference_features: dict[str, object] | None = None,
    rtl_features: dict[str, object] | None = None,
) -> tuple[float, list[str], dict[str, float]]:
    reasons: list[str] = []
    name = 1.0 if _canonical_name(reference) == _canonical_name(rtl) else 0.0
    trace = _trace_score(reference_trace, rtl_trace)
    structural = None
    if reference_neighbors is not None and rtl_neighbors is not None:
        left = {_canonical_name(item) for item in reference_neighbors}
        right = {_canonical_name(item) for item in rtl_neighbors}
        structural = 1.0 if not left and not right else len(left & right) / len(left | right) if left | right else 0.0
    if name:
        reasons.append("canonical_name_match")
    if trace:
        reasons.append("cycle_trace_agreement")
    if structural is None:
        score = 0.55 * name + 0.45 * trace
        components = {"canonical_name": name, "cycle_trace": trace}
    else:
        score = 0.4 * name + 0.3 * trace + 0.3 * structural
        components = {"canonical_name": name, "cycle_trace": trace, "structural_neighbor": structural}
        if structural:
            reasons.append("structural_neighbor_similarity")
    role = None
    if reference_features is not None and rtl_features is not None:
        role = 1.0 if reference_features.get("kind") == rtl_features.get("kind") else 0.0
        reference_type = reference_features.get("cell_type")
        rtl_type = rtl_features.get("cell_type")
        if reference_type is not None or rtl_type is not None:
            role = (role + (1.0 if reference_type == rtl_type else 0.0)) / 2.0
        degree_left = int(reference_features.get("in_degree", 0)) + int(reference_features.get("out_degree", 0))
        degree_right = int(rtl_features.get("in_degree", 0)) + int(rtl_features.get("out_degree", 0))
        degree = 1.0 - min(abs(degree_left - degree_right), 4) / 4.0
        role = 0.5 * role + 0.5 * degree
        score = 0.85 * score + 0.15 * role
        components["node_role_and_degree"] = round(role, 6)
        if role:
            reasons.append("cdfg_node_role_and_degree_similarity")
    return round(score, 6), reasons, components


def _maximum_weight_matching(
    references: list[str],
    rtl_names: list[str],
    scores: dict[tuple[str, str], float],
) -> dict[str, str]:
    """Return a deterministic one-to-one assignment maximizing total score.

    The problem is intentionally kept small and exact: debug alignment should
    not silently depend on greedy iteration order.  Leaving a reference
    unmatched is allowed, so a weak match cannot displace a stronger one.
    """
    index = {name: position for position, name in enumerate(rtl_names)}

    @lru_cache(maxsize=None)
    def solve(position: int, used_mask: int) -> tuple[float, tuple[int | None, ...]]:
        if position == len(references):
            return 0.0, ()
        reference = references[position]
        best_score, best_tail = solve(position + 1, used_mask)
        best = (best_score, (None, *best_tail))
        for rtl in rtl_names:
            bit = 1 << index[rtl]
            if used_mask & bit:
                continue
            tail_score, tail = solve(position + 1, used_mask | bit)
            candidate = (scores[(reference, rtl)] + tail_score, (index[rtl], *tail))
            # Prefer higher score, then lexicographically smaller assignment;
            # this makes the artifact reproducible when scores are equal.
            if candidate[0] > best[0] or (candidate[0] == best[0] and tuple(-1 if x is None else x for x in candidate[1]) < tuple(-1 if x is None else x for x in best[1])):
                best = candidate
        return best

    _, assignment = solve(0, 0)
    return {reference: rtl_names[index_value] for reference, index_value in zip(references, assignment) if index_value is not None}


def align_signals(
    reference_traces: dict[str, list[tuple[int, str]]],
    rtl_traces: dict[str, list[tuple[int, str]]],
    *,
    explicit: dict[str, str] | None = None,
    reference_neighbors: dict[str, set[str]] | None = None,
    rtl_neighbors: dict[str, set[str]] | None = None,
    reference_features: dict[str, dict[str, object]] | None = None,
    rtl_features: dict[str, dict[str, object]] | None = None,
    ambiguity_epsilon: float = 0.01,
) -> dict[str, object]:
    """Return best signal matches and disclose ties instead of guessing."""
    explicit = explicit or {}
    alignments: list[Alignment] = []
    used: set[str] = set()
    automatic_references = [reference for reference in sorted(reference_traces) if reference not in explicit]
    automatic_rtl = [rtl for rtl in sorted(rtl_traces) if rtl not in set(explicit.values())]
    scores: dict[tuple[str, str], float] = {}
    reasons_by_pair: dict[tuple[str, str], list[str]] = {}
    components_by_pair: dict[tuple[str, str], dict[str, float]] = {}
    for reference in automatic_references:
        for rtl in automatic_rtl:
            score, reasons, components = _candidate(reference, rtl, reference_traces[reference], rtl_traces[rtl], (reference_neighbors or {}).get(reference) if reference_neighbors is not None else None, (rtl_neighbors or {}).get(rtl) if rtl_neighbors is not None else None, (reference_features or {}).get(reference) if reference_features is not None else None, (rtl_features or {}).get(rtl) if rtl_features is not None else None)
            scores[(reference, rtl)] = score
            reasons_by_pair[(reference, rtl)] = reasons
            components_by_pair[(reference, rtl)] = components
    matching = _maximum_weight_matching(automatic_references, automatic_rtl, scores)
    for reference in sorted(reference_traces):
        if reference in explicit:
            target = explicit[reference]
            if target not in rtl_traces:
                alignments.append(Alignment(reference, None, 0.0, "ambiguous", ("explicit_target_missing",)))
                continue
            score, reasons, components = _candidate(reference, target, reference_traces[reference], rtl_traces[target], reference_features=(reference_features or {}).get(reference) if reference_features is not None else None, rtl_features=(rtl_features or {}).get(target) if rtl_features is not None else None)
            alignments.append(Alignment(reference, target, score, "explicit", tuple(["human_mapping", *reasons]), score_components=components))
            used.add(target)
            continue
        candidates = [
            {"rtl": rtl, "score": scores[(reference, rtl)], "reasons": reasons_by_pair[(reference, rtl)], "score_components": components_by_pair[(reference, rtl)]}
            for rtl in automatic_rtl
            if rtl not in used
        ]
        candidates.sort(key=lambda item: (-float(item["score"]), str(item["rtl"])))
        if not candidates or float(candidates[0]["score"]) == 0.0:
            alignments.append(Alignment(reference, None, 0.0, "unresolved", ("no_positive_candidate",), tuple(candidates)))
            continue
        top = float(candidates[0]["score"])
        tied = [item for item in candidates if top - float(item["score"]) <= ambiguity_epsilon]
        if len(tied) > 1:
            alignments.append(Alignment(reference, None, top, "ambiguous", ("top_candidates_tied",), tuple(tied)))
            continue
        target = matching.get(reference)
        if target is None:
            alignments.append(Alignment(reference, None, top, "unresolved", ("globally_displaced_by_stronger_match",), tuple(candidates)))
            continue
        selected = next(item for item in candidates if item["rtl"] == target)
        alignments.append(Alignment(reference, target, float(selected["score"]), "aligned", tuple(["global_max_weight_match", *selected["reasons"]]), tuple(candidates), dict(selected["score_components"])))
        used.add(target)
    result: dict[str, object] = {"schema_version": "signal-alignment-v1", "alignments": [item.record() for item in alignments]}
    result["aligned_count"] = sum(item.status in {"aligned", "explicit"} for item in alignments)
    result["ambiguous_count"] = sum(item.status == "ambiguous" for item in alignments)
    result["unresolved_count"] = sum(item.status == "unresolved" for item in alignments)
    result["alignment_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return result


def align_cdfg_signals(
    reference_cdfg: dict[str, object],
    rtl_cdfg: dict[str, object],
    reference_traces: dict[str, list[tuple[int, str]]],
    rtl_traces: dict[str, list[tuple[int, str]]],
    *,
    explicit: dict[str, str] | None = None,
    ambiguity_epsilon: float = 0.01,
) -> dict[str, object]:
    """Align trace signals using adjacency extracted from two CDFG artifacts."""
    def validate_graph(graph: dict[str, object], label: str) -> None:
        if not isinstance(graph, dict):
            raise ValueError(f"{label} CDFG must be an object")
        if not isinstance(graph.get("nodes"), list) or not isinstance(graph.get("edges"), list):
            raise ValueError(f"{label} CDFG must contain node and edge lists")
        digest = graph.get("cdfg_sha256")
        if not isinstance(digest, str) or not digest:
            raise ValueError(f"{label} CDFG must carry cdfg_sha256")
        body = {key: value for key, value in graph.items() if key != "cdfg_sha256"}
        expected = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        if digest != expected:
            raise ValueError(f"{label} CDFG digest does not match its contents")

    validate_graph(reference_cdfg, "reference")
    validate_graph(rtl_cdfg, "RTL")

    def neighbors(graph: dict[str, object]) -> dict[str, set[str]]:
        node_labels: dict[str, str] = {}
        for item in graph["nodes"]:
            if not isinstance(item, dict) or item.get("id") is None:
                continue
            node_id = str(item["id"])
            # Parser CDFGs expose hierarchical IDs but retain a short node
            # name.  Use the short name for trace-facing adjacency while
            # retaining the ID as a fallback for generic CDFG producers.
            node_labels[node_id] = str(item.get("name", node_id))
        result = {label: set() for label in node_labels.values()}
        for edge in graph.get("edges", []):
            if not isinstance(edge, dict):
                continue
            source, target = edge.get("source"), edge.get("target")
            source_label, target_label = node_labels.get(str(source)), node_labels.get(str(target))
            if source_label is not None and target_label is not None:
                result[source_label].add(target_label)
                result[target_label].add(source_label)
        return result

    def graph_features(graph: dict[str, object], trace_names: set[str]) -> dict[str, dict[str, object]]:
        nodes = [item for item in graph["nodes"] if isinstance(item, dict) and item.get("id") is not None]
        by_label: dict[str, dict[str, object]] = {}
        for node in nodes:
            node_id = str(node["id"])
            name = str(node.get("name", node_id))
            labels = {node_id, name}
            if ":signal:" in node_id:
                labels.add(node_id.split(":signal:", 1)[1])
            for label in labels:
                by_label[label] = node
        in_degree = {str(node["id"]): 0 for node in nodes}
        out_degree = {str(node["id"]): 0 for node in nodes}
        for edge in graph["edges"]:
            if not isinstance(edge, dict):
                continue
            source, target = str(edge.get("source")), str(edge.get("target"))
            if source in out_degree:
                out_degree[source] += 1
            if target in in_degree:
                in_degree[target] += 1
        result: dict[str, dict[str, object]] = {}
        for trace_name in trace_names:
            node = by_label.get(trace_name)
            if node is None:
                continue
            node_id = str(node["id"])
            result[trace_name] = {
                "kind": node.get("kind"), "cell_type": node.get("cell_type"),
                "in_degree": in_degree.get(node_id, 0), "out_degree": out_degree.get(node_id, 0),
            }
        return result

    alignment = align_signals(
        reference_traces,
        rtl_traces,
        explicit=explicit,
        reference_neighbors=neighbors(reference_cdfg),
        rtl_neighbors=neighbors(rtl_cdfg),
        reference_features=graph_features(reference_cdfg, set(reference_traces)),
        rtl_features=graph_features(rtl_cdfg, set(rtl_traces)),
        ambiguity_epsilon=ambiguity_epsilon,
    )
    result: dict[str, object] = {
        "schema_version": "cdfg-signal-alignment-v1",
        "reference_cdfg_sha256": reference_cdfg.get("cdfg_sha256"),
        "rtl_cdfg_sha256": rtl_cdfg.get("cdfg_sha256"),
        "reference_node_count": len(neighbors(reference_cdfg)),
        "rtl_node_count": len(neighbors(rtl_cdfg)),
        "reference_edge_count": len([edge for edge in reference_cdfg.get("edges", []) if isinstance(edge, dict)]),
        "rtl_edge_count": len([edge for edge in rtl_cdfg.get("edges", []) if isinstance(edge, dict)]),
        "cdfg_validation": {"reference": "passed", "rtl": "passed"},
        "alignment": alignment,
        "claim_boundary": "deterministic CDFG-adjacency-assisted signal alignment; not proof of semantic equivalence or complete cross-language data-flow correspondence",
    }
    result["alignment_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return result


def aligned_state_frontier(
    reference_traces: dict[str, list[tuple[int, str]]],
    rtl_traces: dict[str, list[tuple[int, str]]],
    alignment: dict[str, object],
) -> dict[str, object]:
    """Find the earliest divergence across all approved aligned state pairs.

    Ambiguous or unresolved mappings are evidence gaps, not candidates for
    guessing.  A frontier is returned only when every admitted pair has a
    comparable, timestamp-aligned trace.
    """
    records = alignment.get("alignments")
    if not isinstance(records, list):
        return {"status": "blocked", "reason": "alignment artifact has no records"}
    frontiers: list[dict[str, object]] = []
    for record in records:
        if not isinstance(record, dict):
            return {"status": "blocked", "reason": "alignment record is malformed"}
        if record.get("status") in {"ambiguous", "unresolved"}:
            return {"status": "blocked", "reason": "alignment contains unresolved mappings", "reference": record.get("reference")}
        reference = record.get("reference")
        rtl = record.get("rtl")
        if not isinstance(reference, str) or not isinstance(rtl, str):
            return {"status": "blocked", "reason": "aligned record has no signal pair"}
        if reference not in reference_traces or rtl not in rtl_traces:
            return {"status": "blocked", "reason": "aligned trace is missing", "reference": reference, "rtl": rtl}
        observed, expected = rtl_traces[rtl], reference_traces[reference]
        for index, (actual, wanted) in enumerate(zip(observed, expected)):
            if actual[0] != wanted[0]:
                return {"status": "unreliable", "reason": "trace timestamps are not aligned", "reference": reference, "rtl": rtl, "index": index}
            if actual[1] != wanted[1]:
                frontiers.append({"reference": reference, "rtl": rtl, "index": index, "cycle": index, "time": actual[0], "observed": actual[1], "reference_value": wanted[1], "prior_cycles_agreed": index})
                break
        else:
            if len(observed) != len(expected):
                return {"status": "incomplete", "reason": "aligned trace lengths differ", "reference": reference, "rtl": rtl}
    if not frontiers:
        return {"status": "identical", "pairs_checked": len(records)}
    first = min(frontiers, key=lambda item: (int(item["time"]), str(item["reference"]), str(item["rtl"])))
    ordered = sorted(frontiers, key=lambda item: (int(item["time"]), str(item["reference"]), str(item["rtl"])))
    return {"status": "diverged", "pairs_checked": len(records), "divergences": ordered, "divergence_count": len(ordered), **first}


def write_alignment(path: str, result: dict[str, object]) -> None:
    from pathlib import Path
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
