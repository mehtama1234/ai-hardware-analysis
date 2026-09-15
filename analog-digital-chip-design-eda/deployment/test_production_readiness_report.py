from pathlib import Path
from hashlib import sha256

from scripts.report_production_readiness import build_report


def test_readiness_report_distinguishes_open_customer_gates(tmp_path: Path):
    checklist = tmp_path / "checklist.md"
    checklist.write_text("# Readiness\n\n## Verified\n- [x] API tests\n\n## Required\n- [ ] Managed database\n- [ ] Signed pilot\n", encoding="utf-8")
    report = build_report(checklist)
    assert report["schema_version"] == "verification-production-readiness-v1"
    assert report["verified_count"] == 1
    assert report["open_count"] == 2
    assert report["customer_production_ready"] is False
    assert report["open_controls"] == ["Managed database", "Signed pilot"]
    assert report["checklist_sha256"] == sha256(checklist.read_bytes()).hexdigest()
    payload = {key: value for key, value in report.items() if key != "readiness_sha256"}
    assert report["readiness_sha256"] == sha256(__import__("json").dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
