import json, shutil, subprocess, sys
from pathlib import Path
import tempfile
sys.path.insert(0, str(Path(__file__).parent))

from validate_pilot import _summary_digest, validate

def test_clean_checkout_validation_passes():
    root = Path(__file__).parent
    subprocess.run([sys.executable, str(root / "run_pilot.py")], check=True, capture_output=True, text=True)
    result = subprocess.run([sys.executable, str(root / "validate_pilot.py")], check=False, capture_output=True, text=True)
    assert result.returncode == 0
    report = json.loads((root / "runs/latest/clean-checkout-validation.json").read_text())
    assert report["valid"] is True
    assert report["session_digest_valid"] is True
    assert report["release_digest_valid"] is True
    assert report["session_stages"][-1] == "closed"
    assert all(report["agent_proposals"].values())
    assert all(check["valid"] for check in report["manifests"].values())
    assert report["taxonomy_valid"] is True
    assert report["taxonomy_digest_valid"] is True
    assert report["scope_comparable"] is True
    assert all(report["next_test_proposals"].values())


def test_clean_checkout_rejects_duplicate_fault_class():
    root = Path(__file__).parent
    with tempfile.TemporaryDirectory(prefix="taxonomy-tamper-") as temp:
        bundle = Path(temp) / "bundle"
        shutil.copytree(root.parent, bundle / "benchmarks")
        taxonomy_path = bundle / "benchmarks" / "multi_design_pilot" / "fault-taxonomy.json"
        taxonomy = json.loads(taxonomy_path.read_text())
        taxonomy["designs"]["seeded_signed"] = taxonomy["designs"]["seeded_counter"]
        taxonomy_path.write_text(json.dumps(taxonomy))
        result = validate(bundle)
        assert result["taxonomy_valid"] is False
        assert result["valid"] is False


def test_clean_checkout_rejects_changed_retest_scope():
    root = Path(__file__).parent
    with tempfile.TemporaryDirectory(prefix="scope-tamper-") as temp:
        bundle = Path(temp) / "bundle"
        shutil.copytree(root.parent, bundle / "benchmarks")
        summary_path = bundle / "benchmarks" / "multi_design_pilot" / "runs" / "latest" / "pilot-summary.json"
        summary = json.loads(summary_path.read_text())
        summary["results"][0]["retest_scope_id"] = "tampered-scope"
        summary["results"][0]["scope_comparable"] = False
        summary["summary_sha256"] = _summary_digest(summary)
        summary_path.write_text(json.dumps(summary))
        result = validate(bundle)
        assert result["scope_comparable"] is False
        assert result["valid"] is False
