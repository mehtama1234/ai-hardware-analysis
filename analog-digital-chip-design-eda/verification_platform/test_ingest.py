from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from verification_platform.ingest import ingest_markdown


def test_ingest_keeps_only_explicit_requirements(tmp_path):
    spec = tmp_path / "spec.md"
    spec.write_text("prose\nREQ-A: output is stable\nREQ-B: reset is safe\n", encoding="utf-8")
    ir = ingest_markdown(spec, root=tmp_path, source_revision="r1")
    assert [item.id for item in ir.requirements] == ["REQ-A", "REQ-B"]
    assert ir.requirements[0].source.path == "spec.md"
    assert len(ir.requirements[0].source.sha256) == 64


def test_ingest_rejects_unstructured_spec(tmp_path):
    spec = tmp_path / "spec.md"
    spec.write_text("The output should be safe.\n", encoding="utf-8")
    try:
        ingest_markdown(spec, root=tmp_path)
    except ValueError as exc:
        assert "no explicit requirements" in str(exc)
    else:
        raise AssertionError("unstructured prose must not become a requirement")
