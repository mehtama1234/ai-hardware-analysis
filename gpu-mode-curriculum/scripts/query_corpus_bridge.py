#!/usr/bin/env python3
"""Query generated GPUMODE lesson to AI-hardware corpus bridges."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BRIDGES = ROOT / "analysis" / "lesson-corpus-bridges.json"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def text_blob(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(f"{key} {text_blob(val)}" for key, val in value.items())
    if isinstance(value, list):
        return " ".join(text_blob(item) for item in value)
    return str(value)


def query_terms(query: str) -> list[str]:
    return [term for term in re.findall(r"[a-z0-9.+_-]+", query.lower()) if len(term) > 1]


def score(row: dict[str, Any], terms: list[str]) -> int:
    blob = text_blob(row).lower()
    return sum(1 for term in terms if term in blob)


def compact(query: str, limit: int) -> dict[str, Any]:
    data = read_json(BRIDGES)
    terms = query_terms(query)
    paper_matches = []
    for paper in data.get("papers", []):
        match_score = score(paper, terms)
        if match_score > 0:
            paper_matches.append((match_score, paper))
    lesson_matches = []
    for lesson in data.get("lessons", []):
        match_score = score(lesson, terms)
        if match_score > 0:
            lesson_matches.append((match_score, lesson))
    paper_matches.sort(key=lambda row: (-row[0], row[1]["venue"], row[1]["title"]))
    lesson_matches.sort(key=lambda row: (-row[0], row[1]["index"]))
    return {
        "query": query,
        "coverage": {
            "paper_count": data.get("paper_count", 0),
            "lesson_count": data.get("lesson_count", 0),
            "link_count": data.get("link_count", 0),
        },
        "papers": [{"score": score, **paper} for score, paper in paper_matches[:limit]],
        "lessons": [{"score": score, **lesson} for score, lesson in lesson_matches[:limit]],
    }


def print_markdown(result: dict[str, Any]) -> None:
    print("# Corpus Bridge Query")
    print()
    print(f"Query: {result['query']}")
    coverage = result["coverage"]
    print(
        f"Coverage: {coverage['paper_count']} papers, "
        f"{coverage['lesson_count']} lessons, {coverage['link_count']} links"
    )
    print()
    print("## Papers")
    for paper in result["papers"]:
        print(f"- {paper['venue']}: {paper['title']} [{paper['score']}]")
        print(f"  {paper['path']}")
        for lesson in paper.get("linked_lessons", [])[:3]:
            evidence = ", ".join(lesson.get("matched_terms", [])[:6])
            print(f"  lesson #{lesson['index']}: {lesson['title']} ({evidence})")
    print()
    print("## Lessons")
    for lesson in result["lessons"]:
        print(f"- #{lesson['index']}: {lesson['title']} [{lesson['score']}]")
        for paper in lesson.get("top_papers", [])[:3]:
            evidence = ", ".join(paper.get("matched_terms", [])[:6])
            print(f"  {paper['venue']}: {paper['title']} ({evidence})")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="Paper, lesson, topic, technique, hardware, or workload phrase.")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = compact(args.query, max(1, args.limit))
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print_markdown(result)


if __name__ == "__main__":
    main()
