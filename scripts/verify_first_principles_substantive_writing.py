#!/usr/bin/env python3
"""Structural guard for the first-principles writing pass.

This checks minimum substance and citation shape. It does not establish that an
interpretation is correct; human/source-text review remains required.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
FILES = {
    "osdi_main": (ROOT / "analysis/osdi-2025-first-principles-main-essay.md", 1800),
    "osdi_subthemes": (ROOT / "analysis/osdi-2025-first-principles-subthemes.md", 2300),
    "asplos_main": (ROOT / "analysis/asplos-2025-first-principles-main-essay.md", 2100),
    "asplos_subthemes": (ROOT / "analysis/asplos-2025-first-principles-subthemes.md", 3000),
    "cross_atlas": (ROOT / "analysis/osdi-asplos-2025-first-principles-cross-atlas-synthesis.md", 1200),
    "service_traces": (ROOT / "analysis/osdi-asplos-2025-first-principles-service-traces.md", 1500),
}
LEDGER = ROOT / "analysis/osdi-2025-first-principles-evidence-ledger.md"
MATRIX = ROOT / "analysis/osdi-2025-first-principles-record-review-matrix.md"
CLAIM_BRIDGE = ROOT / "analysis/osdi-2025-first-principles-claim-to-evidence.md"
PROSE_AUDIT = ROOT / "analysis/osdi-2025-first-principles-prose-evidence-audit.md"
SENTENCE_REVIEW = ROOT / "analysis/osdi-2025-first-principles-sentence-level-evidence-review.md"
EVAL_SCOPE_REVIEW = ROOT / "analysis/osdi-2025-first-principles-evaluation-scope-review.md"
ALL_EVAL_SCOPE_REVIEW = ROOT / "analysis/osdi-2025-first-principles-all-paper-evaluation-scope.md"
RESULT_ANCHOR_REVIEW = ROOT / "analysis/osdi-2025-first-principles-result-anchor-review.md"
SOURCE_TEXT_AUDIT = ROOT / "metadata/osdi-2025-first-principles-source-text-audit.json"
RESULT_QUALITY_REVIEW = ROOT / "analysis/osdi-2025-first-principles-result-reference-quality.md"
ASPLOS_ADJ = ROOT / "analysis/asplos-2025-first-principles-source-backed-adjudication.md"
ASPLOS_ABSTRACT_ADJ = ROOT / "analysis/asplos-2025-first-principles-abstract-adjudication.md"
OSDI_PASSAGES = ROOT / "metadata/osdi-2025-first-principles-source-passage-candidates.json"
OSDI_ADJ = ROOT / "metadata/osdi-2025-first-principles-source-backed-adjudication.json"
OSDI_SECTION_EVIDENCE = ROOT / "metadata/osdi-2025-first-principles-section-evidence.json"
OSDI_EVAL_EVIDENCE = ROOT / "metadata/osdi-2025-first-principles-evaluation-evidence.json"
ASPLOS_PASSAGES = ROOT / "metadata/asplos-2025-first-principles-source-passage-index.json"
ASPLOS_ABSTRACTS = ROOT / "metadata/asplos-2025-first-principles-abstract-evidence-index.json"
ASPLOS_QUEUE = ROOT / "analysis/asplos-2025-first-principles-assignment-review-queue.md"
ASPLOS_EXTERNAL_ABSTRACTS = ROOT / "metadata/asplos-2025-first-principles-external-abstract-evidence.json"
ASPLOS_ARTIFACT_ADJ = ROOT / "analysis/asplos-2025-first-principles-artifact-adjudication.md"
ASPLOS_ASSIGNMENTS = ROOT / "metadata/asplos-2025-first-principles-taxonomy-assignments.json"
ASPLOS_CONCEPT_INVENTORY = ROOT / "analysis/asplos-2025-first-principles-concept-inventory.md"
ASPLOS_CAUSAL_LEDGER = ROOT / "metadata/asplos-2025-first-principles-causal-ledger.json"
OSDI_CAUSAL_LEDGER = ROOT / "metadata/osdi-2025-first-principles-causal-ledger.json"
CAUSAL_GAP_AUDIT = ROOT / "metadata/first-principles-causal-ledger-gap-audit.json"
SERVICE_TRACES = ROOT / "analysis/osdi-asplos-2025-first-principles-service-traces.md"
SUBTHEME_DEPTH_NOTES = ROOT / "analysis/asplos-2025-first-principles-subtheme-depth-notes.md"
OSDI_SUBTHEME_DEPTH_NOTES = ROOT / "analysis/osdi-2025-first-principles-subtheme-depth-notes.md"
BANNED = re.compile(r"\b(?:holistic|seamless|leverage|delve|foster|genuinely|novel|robustly)\b", re.I)
ID = re.compile(r"\b(?:osdi|asplos)-2025-\d{3}\b")
results = []
failed = False

ledger_ok = LEDGER.exists()
ledger_links = []
if ledger_ok:
    ledger_text = LEDGER.read_text()
    ledger_links = re.findall(r"\]\((\.\./[^)]+)\)", ledger_text)
    ledger_ok = len(ledger_links) >= 24 and all((LEDGER.parent / link).exists() for link in ledger_links)
results.append({"file": str(LEDGER.relative_to(ROOT)), "local_links": len(ledger_links),
                "minimum_links": 24, "pass": ledger_ok})
failed |= not ledger_ok

matrix_ok = MATRIX.exists()
matrix_links = []
if matrix_ok:
    matrix_text = MATRIX.read_text()
    matrix_links = re.findall(r"\]\((\.\./analysis/per-paper/osdi-2025-\d{3}\.md)\)", matrix_text)
    matrix_ok = len(set(matrix_links)) == 53 and len(matrix_links) == 53 and all((MATRIX.parent / link).exists() for link in matrix_links)
results.append({"file": str(MATRIX.relative_to(ROOT)), "paper_links": len(matrix_links),
                "required_papers": 53, "pass": matrix_ok})
failed |= not matrix_ok

bridge_ok = CLAIM_BRIDGE.exists()
bridge_rows = 0
if bridge_ok:
    bridge_text = CLAIM_BRIDGE.read_text()
    bridge_rows = len(re.findall(r"^\| (?:[^|]+) \| \[", bridge_text, re.M))
    bridge_ok = bridge_rows >= 24
results.append({"file": str(CLAIM_BRIDGE.relative_to(ROOT)), "claim_evidence_rows": bridge_rows,
                "minimum_rows": 24, "pass": bridge_ok})
failed |= not bridge_ok

prose_audit_ok = PROSE_AUDIT.exists()
prose_audit_rows = 0
if prose_audit_ok:
    prose_audit_text = PROSE_AUDIT.read_text()
    prose_audit_rows = len(re.findall(r"^\| osdi-2025-\d{3} —", prose_audit_text, re.M))
    prose_audit_ok = (prose_audit_rows == 53 and " | no |" not in prose_audit_text)
results.append({"file": str(PROSE_AUDIT.relative_to(ROOT)), "paper_rows": prose_audit_rows,
                "required_rows": 53, "pass": prose_audit_ok})
failed |= not prose_audit_ok

sentence_review_ok = SENTENCE_REVIEW.exists()
sentence_review_rows = 0
if sentence_review_ok:
    sentence_review_text = SENTENCE_REVIEW.read_text()
    sentence_review_rows = len(re.findall(r"^\|[^|]+\| \[", sentence_review_text, re.M))
    sentence_review_ok = sentence_review_rows == 26 and "abstract mechanism supported" in sentence_review_text
results.append({"file": str(SENTENCE_REVIEW.relative_to(ROOT)), "sentence_review_rows": sentence_review_rows,
                "required_rows": 26, "pass": sentence_review_ok})
failed |= not sentence_review_ok

eval_scope_ok = EVAL_SCOPE_REVIEW.exists()
eval_scope_rows = 0
if eval_scope_ok:
    eval_scope_text = EVAL_SCOPE_REVIEW.read_text()
    eval_scope_rows = len(re.findall(r"^\|[^|]+\| \[", eval_scope_text, re.M))
    eval_scope_ok = eval_scope_rows == 26 and "Required limit" in eval_scope_text
results.append({"file": str(EVAL_SCOPE_REVIEW.relative_to(ROOT)), "evaluation_scope_rows": eval_scope_rows,
                "required_rows": 26, "pass": eval_scope_ok})
failed |= not eval_scope_ok

all_eval_scope_ok = ALL_EVAL_SCOPE_REVIEW.exists()
all_eval_scope_rows = 0
if all_eval_scope_ok:
    all_eval_scope_text = ALL_EVAL_SCOPE_REVIEW.read_text()
    all_eval_scope_rows = len(re.findall(r"^\| \[", all_eval_scope_text, re.M))
    all_eval_scope_ok = all_eval_scope_rows == 53
results.append({"file": str(ALL_EVAL_SCOPE_REVIEW.relative_to(ROOT)), "evaluation_scope_rows": all_eval_scope_rows,
                "required_rows": 53, "pass": all_eval_scope_ok})
failed |= not all_eval_scope_ok

result_anchor_ok = RESULT_ANCHOR_REVIEW.exists()
result_anchor_rows = 0
if result_anchor_ok:
    result_anchor_text = RESULT_ANCHOR_REVIEW.read_text()
    result_anchor_rows = len(re.findall(r"^\| \[", result_anchor_text, re.M))
    result_anchor_ok = result_anchor_rows == 53
results.append({"file": str(RESULT_ANCHOR_REVIEW.relative_to(ROOT)), "result_anchor_rows": result_anchor_rows,
                "required_rows": 53, "pass": result_anchor_ok})
failed |= not result_anchor_ok

source_text_ok = SOURCE_TEXT_AUDIT.exists()
source_text_count = 0
if source_text_ok:
    import json
    source_text_report = json.loads(SOURCE_TEXT_AUDIT.read_text())
    source_text_count = source_text_report.get("counts", {}).get("records", 0)
    source_text_ok = (source_text_count == 53 and
                      all((ROOT / row.get("path", "")).exists() for row in source_text_report.get("rows", [])))
results.append({"file": str(SOURCE_TEXT_AUDIT.relative_to(ROOT)), "durable_source_text_records": source_text_count,
                "required_records": 53, "pass": source_text_ok})
failed |= not source_text_ok

result_quality_ok = RESULT_QUALITY_REVIEW.exists()
result_quality_rows = 0
if result_quality_ok:
    result_quality_text = RESULT_QUALITY_REVIEW.read_text()
    result_quality_rows = len(re.findall(r"^\| \[", result_quality_text, re.M))
    result_quality_ok = result_quality_rows == 53
results.append({"file": str(RESULT_QUALITY_REVIEW.relative_to(ROOT)), "result_quality_rows": result_quality_rows,
                "required_rows": 53, "pass": result_quality_ok})
failed |= not result_quality_ok

asplos_adj_ok = ASPLOS_ADJ.exists()
asplos_ids = set()
expected_source_records = 0
if asplos_adj_ok:
    import json
    source_support = json.loads((ROOT / "metadata/asplos-2025-first-principles-source-text-support-audit.json").read_text())
    expected_source_records = source_support.get("summary", {}).get("extracted_records", 0)
    asplos_ids = set(re.findall(r"asplos-2025-\d{3}", ASPLOS_ADJ.read_text()))
    asplos_adj_ok = len(asplos_ids) == expected_source_records
results.append({"file": str(ASPLOS_ADJ.relative_to(ROOT)), "source_text_records": len(asplos_ids),
                "required_records": expected_source_records,
                "pass": asplos_adj_ok})
failed |= not asplos_adj_ok

abstract_adj_ok = ASPLOS_ABSTRACT_ADJ.exists()
abstract_ids = set()
if abstract_adj_ok:
    abstract_ids = set(re.findall(r"asplos-2025-\d{3}", ASPLOS_ABSTRACT_ADJ.read_text()))
abstract_evidence_source = ROOT / "metadata/asplos-2025-first-principles-abstract-evidence-index.json"
expected_abstract_records = 0
if abstract_evidence_source.exists():
    import json
    expected_abstract_records = json.loads(abstract_evidence_source.read_text()).get("counts", {}).get("with_abstract", 0)
abstract_adj_ok = len(abstract_ids) == expected_abstract_records
results.append({"file": str(ASPLOS_ABSTRACT_ADJ.relative_to(ROOT)), "corrected_records": len(abstract_ids),
                "expected_records": expected_abstract_records, "pass": abstract_adj_ok})
failed |= not abstract_adj_ok

passage_ok = OSDI_PASSAGES.exists()
passage_count = 0
if passage_ok:
    import json
    passage_report = json.loads(OSDI_PASSAGES.read_text())
    passage_count = sum(row.get("status") == "candidate-passages-found" for row in passage_report.get("rows", []))
    passage_ok = passage_count == 53 and all(row.get("passages") for row in passage_report.get("rows", []))
results.append({"file": str(OSDI_PASSAGES.relative_to(ROOT)), "candidate_passage_records": passage_count,
                "required_records": 53, "pass": passage_ok})
failed |= not passage_ok

osdi_adj_ok = OSDI_ADJ.exists()
osdi_adj_count = 0
if osdi_adj_ok:
    import json
    osdi_adj_report = json.loads(OSDI_ADJ.read_text())
    osdi_adj_count = osdi_adj_report.get("counts", {}).get("records", 0)
    osdi_adj_ok = (osdi_adj_count == 53 and
                   osdi_adj_report.get("counts", {}).get("needs_section_confirmation") == 0 and
                   osdi_adj_report.get("counts", {}).get("section_confirmation_completed") == 53)
results.append({"file": str(OSDI_ADJ.relative_to(ROOT)), "record_mechanism_adjudications": osdi_adj_count,
                "required_records": 53, "pass": osdi_adj_ok})
failed |= not osdi_adj_ok

osdi_section_ok = OSDI_SECTION_EVIDENCE.exists()
osdi_section_count = 0
if osdi_section_ok:
    import json
    section_report = json.loads(OSDI_SECTION_EVIDENCE.read_text())
    osdi_section_count = section_report.get("counts", {}).get("records", 0)
    osdi_section_ok = (osdi_section_count == 53 and
                       section_report.get("counts", {}).get("with_abstract") == 53 and
                       section_report.get("counts", {}).get("with_mechanism_candidates") == 53)
results.append({"file": str(OSDI_SECTION_EVIDENCE.relative_to(ROOT)), "primary_pdf_section_records": osdi_section_count,
                "required_records": 53, "pass": osdi_section_ok})
failed |= not osdi_section_ok

eval_ok = OSDI_EVAL_EVIDENCE.exists()
eval_count = 0
if eval_ok:
    import json
    eval_report = json.loads(OSDI_EVAL_EVIDENCE.read_text())
    eval_count = eval_report.get("counts", {}).get("records", 0)
    eval_ok = (eval_count == 53 and
               eval_report.get("counts", {}).get("evaluation_sections_found") == 53 and
               eval_report.get("counts", {}).get("with_numeric_tokens") == 53)
results.append({"file": str(OSDI_EVAL_EVIDENCE.relative_to(ROOT)), "primary_pdf_evaluation_records": eval_count,
                "required_records": 53, "pass": eval_ok})
failed |= not eval_ok

asplos_passage_ok = ASPLOS_PASSAGES.exists()
asplos_passage_count = 0
if asplos_passage_ok:
    import json
    asplos_passage_report = json.loads(ASPLOS_PASSAGES.read_text())
    asplos_passage_count = asplos_passage_report.get("counts", {}).get("with_passages", 0)
    asplos_passage_ok = asplos_passage_count == asplos_passage_report.get("counts", {}).get("records", 0) == expected_source_records
results.append({"file": str(ASPLOS_PASSAGES.relative_to(ROOT)), "source_text_passage_records": asplos_passage_count,
                "required_records": expected_source_records, "pass": asplos_passage_ok})
failed |= not asplos_passage_ok

abstract_evidence_ok = ASPLOS_ABSTRACTS.exists()
abstract_evidence_count = 0
if abstract_evidence_ok:
    import json
    abstract_evidence_report = json.loads(ASPLOS_ABSTRACTS.read_text())
    abstract_evidence_count = abstract_evidence_report.get("counts", {}).get("with_abstract", 0)
abstract_evidence_ok = abstract_evidence_count == expected_abstract_records
results.append({"file": str(ASPLOS_ABSTRACTS.relative_to(ROOT)), "abstract_evidence_records": abstract_evidence_count,
                "required_records": expected_abstract_records, "pass": abstract_evidence_ok})
failed |= not abstract_evidence_ok

external_abstract_ok = ASPLOS_EXTERNAL_ABSTRACTS.exists()
external_abstract_count = 0
if external_abstract_ok:
    import json
    external_report = json.loads(ASPLOS_EXTERNAL_ABSTRACTS.read_text())
    external_rows = external_report.get("rows", [])
    external_abstract_count = len(external_rows)
    required_external = {"asplos-2025-031", "asplos-2025-074", "asplos-2025-157"}
    external_abstract_ok = ({row.get("paper_id") for row in external_rows} == required_external and
                            all(row.get("abstract") and row.get("abstract_source_url") and
                                row.get("evidence_level") == "abstract-only" for row in external_rows))
results.append({"file": str(ASPLOS_EXTERNAL_ABSTRACTS.relative_to(ROOT)),
                "external_abstract_records": external_abstract_count, "required_records": 3,
                "pass": external_abstract_ok})
failed |= not external_abstract_ok

queue_ok = ASPLOS_QUEUE.exists()
queue_records = 0
if queue_ok:
    queue_text = ASPLOS_QUEUE.read_text()
    queue_records = len(re.findall(r"\| \[asplos-2025-\d{3} —", queue_text))
    required_queue_ids = {"asplos-2025-031", "asplos-2025-074", "asplos-2025-157"}
    queue_ids = set(re.findall(r"\[(asplos-2025-\d{3}) —", queue_text))
    queue_ok = (queue_records == 3 and queue_ids == required_queue_ids and
                all(re.search(rf"\[{paper_id} —[^\n]+\]\([^\n]+\) \| `[^`]+` \| external abstract \|", queue_text)
                    for paper_id in required_queue_ids) and
                queue_text.count("obtain and read paper text; verify mechanism, baselines, and evaluation boundary") == 3)
    for forbidden in ("lidar", "always-on low-resolution", "doubling the work done per cycle", "optimal tiling strategy"):
        deep_files = [ROOT / "analysis/themes/deep/papers/asplos-2025-031.json",
                      ROOT / "analysis/themes/deep/papers/asplos-2025-157.json"]
        if any(forbidden in path.read_text().lower() for path in deep_files if path.exists()):
            queue_ok = False
results.append({"file": str(ASPLOS_QUEUE.relative_to(ROOT)), "unadjudicated_records": queue_records,
                "required_records": 3, "pass": queue_ok})
failed |= not queue_ok

artifact_ok = ASPLOS_ARTIFACT_ADJ.exists()
artifact_ids = set()
if artifact_ok:
    artifact_ids = set(re.findall(r"asplos-2025-\d{3}", ASPLOS_ARTIFACT_ADJ.read_text()))
    artifact_ok = artifact_ids == {"asplos-2025-020", "asplos-2025-033", "asplos-2025-099", "asplos-2025-123", "asplos-2025-152"}
results.append({"file": str(ASPLOS_ARTIFACT_ADJ.relative_to(ROOT)),
                "artifact_records": len(artifact_ids), "required_records": 5,
                "pass": artifact_ok})
failed |= not artifact_ok

# Abstract corrections must carry an evidence-boundary note; do not silently
# treat an abstract-only reassignment as a full-paper adjudication.
assignment_provenance_ok = ASPLOS_ASSIGNMENTS.exists()
corrected_assignment_count = 0
false_previous_count = 0
if assignment_provenance_ok:
    import json
    assignment_rows = json.loads(ASPLOS_ASSIGNMENTS.read_text()).get("assignments", [])
    corrected = [row for row in assignment_rows
                 if row.get("assignment_status") == "abstract-corrected-second-pass"]
    upgraded = [row for row in assignment_rows
                if row.get("assignment_status") == "primary-paper-adjudicated-third-pass"]
    expected_source_upgrades = {
        "asplos-2025-004", "asplos-2025-005", "asplos-2025-067",
        "asplos-2025-078", "asplos-2025-082", "asplos-2025-095",
        "asplos-2025-114", "asplos-2025-135", "asplos-2025-143",
    }
    upgraded_ids = {row.get("id") for row in upgraded}
    corrected_assignment_count = len(corrected)
    false_previous_count = sum("previous_primary_subtheme_id" in row for row in corrected)
    assignment_provenance_ok = (
        corrected_assignment_count == 77 and
        upgraded_ids == expected_source_upgrades and
        false_previous_count == 0 and
        all(row.get("correction_provenance") for row in corrected) and
        all(row.get("evidence_basis") == ["local_primary_source_text"] and
            row.get("source_text_path") and row.get("source_adjudication_reason")
            for row in upgraded)
    )
results.append({"file": str(ASPLOS_ASSIGNMENTS.relative_to(ROOT)),
                "abstract_corrected_assignments": corrected_assignment_count,
                "source_upgraded_assignments": len(upgraded),
                "required_source_upgrades": len(expected_source_upgrades),
                "false_previous_fields": false_previous_count,
                "pass": assignment_provenance_ok})
failed |= not assignment_provenance_ok

concept_inventory_ok = ASPLOS_CONCEPT_INVENTORY.exists()
concept_count = 0
if concept_inventory_ok:
    concept_text = ASPLOS_CONCEPT_INVENTORY.read_text()
    concept_count = len(re.findall(r"^## ", concept_text, re.M))
    required_concepts = {"State", "Dependency", "Queue", "Residency", "Transfer", "Admission",
                         "Uncertainty", "Failure model", "Recovery", "Observability", "Tail latency",
                         "Goodput", "Operating point"}
    headings = set(re.findall(r"^## (.+)$", concept_text, re.M))
    concept_inventory_ok = concept_count >= 28 and required_concepts <= headings
results.append({"file": str(ASPLOS_CONCEPT_INVENTORY.relative_to(ROOT)),
                "concept_entries": concept_count, "minimum_entries": 28,
                "pass": concept_inventory_ok})
failed |= not concept_inventory_ok

causal_ledger_ok = ASPLOS_CAUSAL_LEDGER.exists()
causal_ledger_count = 0
if causal_ledger_ok:
    import json
    causal_report = json.loads(ASPLOS_CAUSAL_LEDGER.read_text())
    causal_rows = causal_report.get("rows", [])
    causal_ledger_count = len(causal_rows)
    required_fields = {"requested_result", "blocking_pressure", "changed_mechanism",
                       "new_cost_or_failure_boundary", "reported_outcome", "evidence_boundary"}
    causal_ledger_ok = (causal_report.get("counts", {}).get("records") == 179 and
                        causal_ledger_count == 179 and
                        all(required_fields <= set(row) for row in causal_rows))
results.append({"file": str(ASPLOS_CAUSAL_LEDGER.relative_to(ROOT)),
                "causal_ledger_records": causal_ledger_count, "required_records": 179,
                "pass": causal_ledger_ok})
failed |= not causal_ledger_ok

osdi_causal_ok = OSDI_CAUSAL_LEDGER.exists()
osdi_causal_count = 0
if osdi_causal_ok:
    import json
    osdi_causal_report = json.loads(OSDI_CAUSAL_LEDGER.read_text())
    osdi_causal_rows = osdi_causal_report.get("rows", [])
    osdi_causal_count = len(osdi_causal_rows)
    osdi_required_fields = {"requested_result", "blocking_pressure", "changed_mechanism",
                            "new_cost_or_failure_boundary", "reported_outcome", "evidence_boundary"}
    osdi_causal_ok = (osdi_causal_report.get("counts", {}).get("records") == 53 and
                      osdi_causal_count == 53 and
                      all(osdi_required_fields <= set(row) for row in osdi_causal_rows))
results.append({"file": str(OSDI_CAUSAL_LEDGER.relative_to(ROOT)),
                "causal_ledger_records": osdi_causal_count, "required_records": 53,
                "pass": osdi_causal_ok})
failed |= not osdi_causal_ok

causal_gap_ok = CAUSAL_GAP_AUDIT.exists()
causal_gap_statuses = []
if causal_gap_ok:
    import json
    gap_report = json.loads(CAUSAL_GAP_AUDIT.read_text())
    gap_rows = gap_report.get("reports", [])
    causal_gap_statuses = [r.get("status") for r in gap_rows]
    causal_gap_ok = ({r.get("ledger") for r in gap_rows} == {
        "metadata/osdi-2025-first-principles-causal-ledger.json",
        "metadata/asplos-2025-first-principles-causal-ledger.json"} and
        causal_gap_statuses == ["all-fields-present", "all-fields-present"] and
        all(not r.get(k) for r in gap_rows for k in (
            "missing_requested_result", "missing_blocking_pressure", "missing_changed_mechanism",
            "missing_new_cost_or_failure_boundary", "missing_reported_outcome")))
results.append({"file": str(CAUSAL_GAP_AUDIT.relative_to(ROOT)),
                "ledger_reports": len(causal_gap_statuses),
                "required_reports": 2, "pass": causal_gap_ok})
failed |= not causal_gap_ok

trace_ok = SERVICE_TRACES.exists()
trace_count = 0
if trace_ok:
    trace_text = SERVICE_TRACES.read_text()
    trace_count = len(re.findall(r"^## Trace \d+:", trace_text, re.M))
    trace_ok = trace_count >= 4 and all(term in trace_text for term in (
        "admission", "placement", "movement", "execution", "recovery", "delivery"))
results.append({"file": str(SERVICE_TRACES.relative_to(ROOT)),
                "end_to_end_trace_count": trace_count, "minimum_traces": 4,
                "pass": trace_ok})
failed |= not trace_ok

depth_ok = SUBTHEME_DEPTH_NOTES.exists()
depth_sections = 0
depth_text = ""
if depth_ok:
    depth_text = SUBTHEME_DEPTH_NOTES.read_text()
    depth_sections = len(re.findall(r"^## \d+\. ", depth_text, re.M))
    depth_ok = (depth_sections == 24 and
                all(depth_text.count(term) >= 24 for term in (
                    "Starting condition", "Mechanism", "Failure boundary", "Neighbor")))
results.append({"file": str(SUBTHEME_DEPTH_NOTES.relative_to(ROOT)),
                "depth_sections": depth_sections, "required_sections": 24,
                "required_fields": ["Starting condition", "Mechanism", "Failure boundary", "Neighbor"],
                "pass": depth_ok})
failed |= not depth_ok

osdi_depth_ok = OSDI_SUBTHEME_DEPTH_NOTES.exists()
osdi_depth_sections = 0
if osdi_depth_ok:
    osdi_depth_text = OSDI_SUBTHEME_DEPTH_NOTES.read_text()
    osdi_depth_sections = len(re.findall(r"^## \d+\. ", osdi_depth_text, re.M))
    osdi_depth_lower = osdi_depth_text.lower()
    osdi_depth_parts = re.split(r"^## \d+\. .*$", osdi_depth_text, flags=re.M)[1:]
    osdi_depth_ok = (osdi_depth_sections == 24 and
                     len(osdi_depth_parts) == 24 and
                     all(len(re.findall(r"\b\w+[\w'-]*\b", part)) >= 60
                         for part in osdi_depth_parts) and
                     osdi_depth_lower.count("pressure") >= 24 and
                     osdi_depth_lower.count("neighbor") >= 24 and
                     osdi_depth_lower.count("evidence") >= 6)
results.append({"file": str(OSDI_SUBTHEME_DEPTH_NOTES.relative_to(ROOT)),
                "depth_sections": osdi_depth_sections, "required_sections": 24,
                "required_fields": ["pressure", "Mechanism", "fails", "neighbor", "Evidence"],
                "pass": osdi_depth_ok})
failed |= not osdi_depth_ok

for name, (path, minimum) in FILES.items():
    text = path.read_text()
    words = len(re.findall(r"\b\w+[\w'-]*\b", text))
    headings = len(re.findall(r"^### ", text, re.M))
    terms = sorted(set(m.group(0).lower() for m in BANNED.finditer(text)))
    needed = 24 if name.endswith("subthemes") else 0
    section_count = len(re.findall(r"^## (?:\d+\. )", text, re.M)) if name.startswith("asplos") else headings
    ok = path.exists() and words >= minimum and section_count >= needed and not terms
    results.append({"file": str(path.relative_to(ROOT)), "words": words,
                    "h3_headings": headings, "minimum_words": minimum,
                    "required_sections": needed, "banned_terms": terms, "pass": ok})
    failed |= not ok

# Every named local paper ID in the essays must resolve to a paper record.
for name, (path, _) in FILES.items():
    text = path.read_text()
    ids = sorted(set(ID.findall(text)))
    unresolved = []
    for paper_id in ids:
        if not (ROOT / "analysis/per-paper" / f"{paper_id}.json").exists():
            unresolved.append(paper_id)
    results.append({"file": str(path.relative_to(ROOT)), "paper_ids": len(ids),
                    "unresolved_ids": unresolved, "pass": not unresolved})
    failed |= bool(unresolved)

print({"check": "structural-writing-check", "results": results,
       "interpretation_warning": "Pass means minimum structure and local ID resolution only; it does not establish evidence quality or correct taxonomy assignments.",
       "pass": not failed})
sys.exit(1 if failed else 0)
