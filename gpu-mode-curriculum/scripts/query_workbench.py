#!/usr/bin/env python3
"""Query the generated GPU systems workbench from a bottleneck description."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from build_workbench import OUT_JSON, PROFILES, build, score_text, text_blob


def profile_query_score(profile: dict[str, Any], query: str) -> int:
    terms = query.lower().replace("/", " ").replace("-", " ").split()
    score = score_text(query, profile["query_terms"])
    score += score_text(text_blob(profile["query_terms"]), terms)
    score += score_text(text_blob(profile["lesson_topics"]), terms)
    score += score_text(text_blob(profile["lesson_concepts"]), terms)
    score += score_text(profile["label"], terms)
    return score


def load_workbench() -> dict[str, Any]:
    if not OUT_JSON.exists():
        build()
    return json.loads(OUT_JSON.read_text(encoding="utf-8"))


def choose_profile(workbench: dict[str, Any], query: str) -> dict[str, Any]:
    profile_defs = {profile["id"]: profile for profile in PROFILES}
    ranked = []
    for profile in workbench["profiles"]:
        score = profile_query_score(profile_defs[profile["id"]], query)
        score += score_text(text_blob(profile["recommended_lessons"][:3]), query.lower().split())
        score += score_text(text_blob(profile["recommended_labs"][:3]), query.lower().split())
        ranked.append((score, profile))
    ranked.sort(key=lambda item: (-item[0], item[1]["id"]))
    return ranked[0][1] if ranked and ranked[0][0] > 0 else workbench["profiles"][0]


def compact(profile: dict[str, Any], query: str) -> dict[str, Any]:
    return {
        "query": query,
        "matched_bottleneck_class": profile["id"],
        "label": profile["label"],
        "diagnosis": profile["diagnosis"],
        "next_action": profile["next_action"],
        "lessons": profile["recommended_lessons"][:5],
        "labs": profile["recommended_labs"][:4],
        "measurements": profile["latest_measurements"][:4],
        "tutorial_sources": profile.get("tutorial_sources", [])[:4],
        "exercise_path": profile.get("exercise_path", {}),
        "papers": profile["related_papers"][:4],
    }


def print_markdown(result: dict[str, Any]) -> None:
    print(f"# {result['label']}")
    print()
    print(f"Query: {result['query']}")
    print(f"Bottleneck class: {result['matched_bottleneck_class']}")
    print()
    print(result["diagnosis"])
    print()
    print(f"Next action: {result['next_action']}")
    print()
    print("## Labs")
    for lab in result["labs"]:
        impl = f" -> {lab['implemented_as']}" if lab.get("implemented_as") else ""
        print(f"- {lab['id']} [{lab['status']}]{impl}: {lab['deliverable']}")
    print()
    print("## Lessons")
    for lesson in result["lessons"]:
        print(f"- {lesson['index']}: {lesson['title']} ({lesson['url']})")
    print()
    print("## Measurements")
    for measurement in result["measurements"]:
        cuda = f", cuda={measurement['cuda_status']}" if measurement.get("cuda_status") else ""
        print(f"- {measurement['path']} [{measurement['status']}{cuda}]: {measurement['summary']}")
    print()
    print("## Tutorial Sources")
    for source in result["tutorial_sources"]:
        print(f"- {source['provider']}: {source['title']} ({source['url']})")
        print(f"  {source['why']}")
    print()
    path = result.get("exercise_path", {})
    if path:
        print("## End-To-End Exercise Path")
        lab = path.get("lab", {})
        source = path.get("source_reading", {})
        measurement = path.get("measurement", {})
        print(f"Source: {source.get('provider', '')}: {source.get('title', '')}")
        print(f"Run: {lab.get('command', '')}")
        print(f"Artifact: {measurement.get('path', '')}")
        for step in path.get("steps", [])[:5]:
            print(f"- {step}")
        print()
    print("## Papers")
    for paper in result["papers"]:
        print(f"- {paper['venue']}: {paper['title']} [{paper['confidence']}]")
        links = paper.get("linked_lessons", [])[:2]
        for lesson in links:
            evidence = ", ".join(lesson.get("matched_concepts") or lesson.get("matched_topics") or lesson.get("matched_terms", []))
            print(f"  lesson #{lesson['index']}: {lesson['title']} ({evidence})")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="Model/operator/bottleneck description, e.g. 'kv cache decode latency'.")
    parser.add_argument("--json", action="store_true", help="Print compact JSON instead of Markdown.")
    args = parser.parse_args()

    workbench = load_workbench()
    profile = choose_profile(workbench, args.query)
    result = compact(profile, args.query)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print_markdown(result)


if __name__ == "__main__":
    main()
