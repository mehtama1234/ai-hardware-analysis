from pathlib import Path
import json

from .mutation import run_mutation, summarize_mutations, validate_mutation_suite


def _roots(tmp_path: Path):
    roots = {}
    for name in ("canonical", "baseline", "candidate"):
        roots[name] = tmp_path / name
        (roots[name] / "rtl").mkdir(parents=True)
        (roots[name] / "rtl/a.sv").write_text("assign q = d;\n", encoding="utf-8")
    return roots


def test_mutation_contract_requires_a_valid_baseline_and_detects_change(tmp_path: Path):
    roots = _roots(tmp_path)
    mutation = {
        "mutation_id": "remove-enable",
        "source_file": "rtl/a.sv",
        "from": "assign q = d;",
        "to": "assign q = MUTANT;",
        "command": ["python3", "-c", "import pathlib,sys; sys.exit(1 if 'MUTANT' in pathlib.Path('rtl/a.sv').read_text() else 0)"],
    }
    validate_mutation_suite({"schema_version": "mutation-suite-v1", "mutations": [mutation]})
    record = run_mutation(mutation, canonical_root=roots["canonical"], baseline_root=roots["baseline"], candidate_root=roots["candidate"], output_root=tmp_path / "run")
    result = record["result"]
    assert result["baseline_valid"] is True
    assert result["detected"] is True
    assert result["false_pass"] is False
    assert result["candidate_changed"] is True
    assert result["canonical_unchanged"] is True
    assert (tmp_path / "run/mutation-result.json").is_file()


def test_mutation_summary_blocks_false_pass(tmp_path: Path):
    roots = _roots(tmp_path)
    mutation = {
        "mutation_id": "ignored-mutant",
        "source_file": "rtl/a.sv",
        "from": "assign q = d;",
        "to": "assign q = 1'b0;",
        "command": ["python3", "-c", "pass"],
    }
    record = run_mutation(mutation, canonical_root=roots["canonical"], baseline_root=roots["baseline"], candidate_root=roots["candidate"], output_root=tmp_path / "run")
    report = summarize_mutations([record])
    assert report["false_pass_count"] == 1
    assert report["mutation_score"] == 0.0
    assert report["status"] == "blocked"
    assert report["by_source"]["rtl/a.sv"]["false_passes"] == 1
    assert report["by_source"]["rtl/a.sv"]["mutation_score"] == 0.0


def test_seeded_multi_design_suite_manifest_is_valid():
    root = Path(__file__).resolve().parents[1]
    suite = json.loads((root / "benchmarks/repository_scale/seeded_multi_mutation_suite.json").read_text(encoding="utf-8"))
    validate_mutation_suite(suite)
    assert len(suite["mutations"]) == 16
