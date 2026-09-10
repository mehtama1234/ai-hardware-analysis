from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from verification_platform.retrieval import build_retrieval_index, retrieve


def test_retrieval_returns_evidence_linked_snippet(tmp_path):
    spec = tmp_path / "spec.md"
    spec.write_text("REQ-RESET: counter must reset to zero\nREQ-HOLD: counter holds when enable is low\n", encoding="utf-8")
    index = build_retrieval_index([spec], root=tmp_path, source_revision="r1")
    hits = retrieve(index, "enable low", limit=1)
    assert hits[0]["path"] == "spec.md"
    assert hits[0]["line"] == 2
    assert hits[0]["evidence"]["sha256"]
