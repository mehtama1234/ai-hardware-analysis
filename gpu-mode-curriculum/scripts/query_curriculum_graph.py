#!/usr/bin/env python3
"""Query the generated GPUMODE curriculum graph."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "analysis" / "curriculum-graph.json"
WORKBENCH = ROOT / "analysis" / "gpu-systems-workbench.json"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def terms(value: str) -> list[str]:
    return [term for term in re.findall(r"[a-z0-9.+_-]+", value.lower()) if len(term) > 1]


def text_blob(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(f"{key} {text_blob(val)}" for key, val in value.items())
    if isinstance(value, list):
        return " ".join(text_blob(item) for item in value)
    return str(value)


def score_node(node: dict[str, Any], query_terms: list[str]) -> int:
    blob = text_blob(node).lower()
    score = 0
    for term in query_terms:
        if term == node.get("kind"):
            score += 4
        if term in node.get("id", ""):
            score += 3
        if term in str(node.get("label", "")).lower():
            score += 5
        if term in blob:
            score += 1
    return score


def edge_indexes(edges: list[dict[str, Any]]) -> tuple[dict[str, list[dict[str, Any]]], dict[str, list[dict[str, Any]]]]:
    outgoing: dict[str, list[dict[str, Any]]] = defaultdict(list)
    incoming: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for edge in edges:
        outgoing[edge["source"]].append(edge)
        incoming[edge["target"]].append(edge)
    return outgoing, incoming


def related_nodes(
    node: dict[str, Any],
    nodes: dict[str, dict[str, Any]],
    outgoing: dict[str, list[dict[str, Any]]],
    incoming: dict[str, list[dict[str, Any]]],
) -> dict[str, list[dict[str, Any]]]:
    related: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for edge in outgoing.get(node["id"], []):
        target = nodes.get(edge["target"])
        if target:
            related[edge["relation"]].append({**target, "edge": edge})
    for edge in incoming.get(node["id"], []):
        source = nodes.get(edge["source"])
        if source:
            related[f"incoming_{edge['relation']}"].append({**source, "edge": edge})
    return related


def matching_profiles(workbench: dict[str, Any], query_terms: list[str], limit: int) -> list[dict[str, Any]]:
    rows = []
    for profile in workbench.get("profiles", []):
        blob = text_blob(profile).lower()
        score = sum(1 for term in query_terms if term in blob)
        if score <= 0:
            continue
        rows.append(
            {
                "id": profile["id"],
                "label": profile["label"],
                "next_action": profile["next_action"],
                "score": score,
            }
        )
    return sorted(rows, key=lambda row: (-row["score"], row["id"]))[:limit]


def summarize_related(kind: str, rows: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    filtered = [row for row in rows if row.get("kind") == kind]
    return filtered[:limit]


def compact_result(query: str, limit: int) -> dict[str, Any]:
    graph = read_json(GRAPH)
    workbench = read_json(WORKBENCH) if WORKBENCH.exists() else {"profiles": []}
    nodes = {node["id"]: node for node in graph["nodes"]}
    outgoing, incoming = edge_indexes(graph["edges"])
    query_terms = terms(query)

    ranked = []
    for node in graph["nodes"]:
        score = score_node(node, query_terms)
        if score > 0:
            ranked.append((score, node))
    ranked.sort(key=lambda item: (-item[0], item[1]["kind"], item[1]["id"]))

    top_nodes = []
    for score, node in ranked[:limit]:
        related = related_nodes(node, nodes, outgoing, incoming)
        top_nodes.append(
            {
                "score": score,
                "node": node,
                "lessons": summarize_related("lesson", related.get("incoming_covers_topic", []) + related.get("incoming_teaches_concept", []) + related.get("prerequisite_for", []), limit),
                "candidate_lessons": summarize_related("lesson", related.get("incoming_candidate_lab", []), limit),
                "topics": summarize_related("topic", related.get("covers_topic", []) + related.get("incoming_includes_concept", []) + related.get("prepares_topic", []), limit),
                "concepts": summarize_related("concept", related.get("teaches_concept", []) + related.get("includes_concept", []), limit),
                "prerequisites": summarize_related("prerequisite", related.get("incoming_prerequisite_for", []) + related.get("incoming_prepares_topic", []), limit),
                "labs": summarize_related("lab", related.get("candidate_lab", []) + related.get("has_runnable_lab", []), limit),
            }
        )

    return {
        "query": query,
        "graph": {
            "node_count": graph["node_count"],
            "edge_count": graph["edge_count"],
            "top_topic_order": graph.get("practical_topic_order", [])[:5],
        },
        "matches": top_nodes,
        "profiles": matching_profiles(workbench, query_terms, limit),
    }


def print_node(row: dict[str, Any]) -> None:
    node = row["node"]
    print(f"- {node['kind']} {node['id']} [{row['score']}]: {node['label']}")
    if node.get("url"):
        print(f"  url: {node['url']}")
    for label, key in (
        ("prerequisites", "prerequisites"),
        ("lessons", "lessons"),
        ("candidate lessons", "candidate_lessons"),
        ("topics", "topics"),
        ("concepts", "concepts"),
        ("labs", "labs"),
    ):
        values = row.get(key, [])
        if not values:
            continue
        rendered = "; ".join(f"{item['label']} ({item['id']})" for item in values[:4])
        print(f"  {label}: {rendered}")


def print_markdown(result: dict[str, Any]) -> None:
    print("# Curriculum Graph Query")
    print()
    print(f"Query: {result['query']}")
    graph = result["graph"]
    print(f"Graph: {graph['node_count']} nodes, {graph['edge_count']} edges")
    print()
    print("## Practical Topic Order")
    for row in graph["top_topic_order"]:
        labs = ", ".join(row.get("implemented_labs", [])[:3])
        print(f"- {row['topic']}: {row['lesson_count']} lessons, {row['prerequisite_signal_count']} prerequisite signals, labs: {labs}")
    print()
    print("## Graph Matches")
    for row in result["matches"]:
        print_node(row)
    print()
    print("## Workbench Profiles")
    for profile in result["profiles"]:
        print(f"- {profile['id']}: {profile['label']}")
        print(f"  {profile['next_action']}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="Topic, lesson, concept, prerequisite, or lab phrase.")
    parser.add_argument("--limit", type=int, default=5, help="Maximum matches per section.")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of Markdown.")
    args = parser.parse_args()

    result = compact_result(args.query, max(1, args.limit))
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print_markdown(result)


if __name__ == "__main__":
    main()
