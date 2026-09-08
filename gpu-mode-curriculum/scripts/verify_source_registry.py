"""Validate the handbook topic inventory without implying source or GPU acceptance."""
import json
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "advanced-lab-phase/source-registry.json"


def validate(data):
    errors = []
    topics = data.get("topics")
    if not isinstance(topics, list) or len(topics) != 24:
        return [f"expected 24 topics, got {len(topics) if isinstance(topics, list) else 'non-list'}"]
    numbers = [item.get("number") for item in topics]
    if numbers != list(range(1, 25)):
        errors.append(f"topic numbers must be 1..24 in order, got {numbers}")
    required = {"number", "title", "source", "url", "source_status", "local_artifacts", "evidence_class", "prerequisites", "open_gate"}
    for item in topics:
        missing = sorted(required - item.keys())
        if missing:
            errors.append(f"topic {item.get('number')} missing {missing}")
        parsed = urlparse(item.get("url", ""))
        if parsed.scheme != "https" or not parsed.netloc:
            errors.append(f"topic {item.get('number')} has invalid HTTPS source URL")
        if not isinstance(item.get("local_artifacts"), list) or not isinstance(item.get("prerequisites"), list):
            errors.append(f"topic {item.get('number')} list fields malformed")
        for relative in item.get("local_artifacts", []):
            if not (ROOT / relative).exists():
                errors.append(f"topic {item.get('number')} missing local artifact {relative}")
    return errors


def main():
    data = json.loads(REGISTRY.read_text())
    errors = validate(data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"source registry valid: {len(data['topics'])} topics")
    return 0


if __name__ == "__main__":
    sys.exit(main())
