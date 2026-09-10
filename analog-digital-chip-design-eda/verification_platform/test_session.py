from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from verification_platform.session import VerificationSession


def test_session_requires_monotonic_evidence_lifecycle(tmp_path):
    session = VerificationSession(session_id="seeded-counter", run_root=tmp_path, source_revision="r1")
    for stage in ("planned", "executed", "triaged", "repair_review", "retested", "closed"):
        session.advance(stage, metadata={"actor": "agent" if stage != "repair_review" else "human"})
    path = session.write()
    payload = path.read_text(encoding="utf-8")
    assert session.stage == "closed"
    assert "session_sha256" in payload


def test_session_rejects_skipping_review_stage(tmp_path):
    session = VerificationSession(session_id="s", run_root=tmp_path, source_revision="r1")
    session.advance("planned")
    try:
        session.advance("triaged")
    except ValueError as exc:
        assert "invalid transition" in str(exc)
    else:
        raise AssertionError("session must not skip execution")
