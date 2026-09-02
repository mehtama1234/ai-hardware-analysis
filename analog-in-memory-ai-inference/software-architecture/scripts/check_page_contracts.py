#!/usr/bin/env python3
"""Audit the analog AI workbench pages for the shared proof contract."""

from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CORE_HTML = [
    "connected-system-map.html",
    "master-review-path.html",
    "combined-system-end-to-end-workflow.html",
    "proof-ladder-step-by-step.html",
    "evidence-matrix-plan.html",
    "customer-workload-intake-plan.html",
    "timing-latency-budget-plan.html",
    "memory-technology-decision-plan.html",
    "benchmark-suite-plan.html",
    "simulator-calibration-plan.html",
    "simulation-as-compiler-hat-plan.html",
    "aihwkit-tool-stack-plan.html",
    "analog-mlir-to-silicon-compiler-plan.html",
    "hardware-tapeout-risk-roadmap.html",
    "analog-vs-digital-validation-process.html",
    "hybrid-benchmarking-practical-pipeline.html",
    "company-roadmap-end-to-end.html",
    "strategy-synthesis-and-next-pages.html",
    "physical-ai-opportunity-roadmap-digital-twins.html",
    "physical-ai-robot-learning-implications.html",
    "partner-ecosystem-variations.html",
    "investor-narrative-variations.html",
    "toolkit-results-first-principles.html",
    "simulation-to-silicon-first-principles-spec-review.html",
    "page-contract-audit.html",
]

CORE_MD = [
    "README.md",
    "end-to-end-goal.md",
    "architecture.md",
    "external-tool-integration-spec.md",
    "review-package-demo/README.md",
    "review-package-demo/executive-brief.md",
    "review-package-demo/engineering-work-queue.md",
    "review-package-demo/action-evidence-map.md",
    "review-package-demo/silicon-board-proof-map.md",
]

SKIP_PARTS = {
    ".data",
    ".venv",
    "__pycache__",
    "screenshots",
    "artifacts",
}

CONTRACT_GROUPS = {
    "object": ["object", "consumes"],
    "constraint": ["constraint", "checks", "risk", "boundary"],
    "design move": ["design move", "produces", "action", "move", "generate", "design verification"],
    "evidence": ["evidence", "artifact", "trace", "report"],
    "allowed claim": ["allowed claim", "supports", "supported", "safe claim", "can support", "allowed", "can say"],
    "refused claim": ["refused claim", "refuses", "blocked", "cannot claim", "does not prove"],
    "next handoff": ["next handoff", "handoff", "next page", "next artifact", "feeds", "next action", "next work", "next measurement"],
}

CRITICAL_BOUNDARY_FILES = [
    "evidence-matrix-plan.html",
    "timing-latency-budget-plan.html",
    "aihwkit-tool-stack-plan.html",
    "external-tool-integration-spec.md",
    "review-package-demo/action-evidence-map.md",
    "review-package-demo/silicon-board-proof-map.md",
]

UNSAFE_CLAIM_PATTERNS = [
    re.compile(r"\bchip is production ready\b", re.I),
    re.compile(r"\bchip is proven(?: on hardware)?\b", re.I),
    re.compile(r"\bchip has measured (?:power savings|task accuracy|performance)\b", re.I),
    re.compile(r"\bmeasured energy is supported\b", re.I),
    re.compile(r"\bmeasured board latency is supported\b", re.I),
    re.compile(r"\bproduction readiness is supported\b", re.I),
]

BLOCKING_CONTEXT = re.compile(
    r"\b(blocked|cannot|can not|do not say|refuse|refused|refuses|not prove|does not prove|stays blocked|remains blocked|not allowed|unsafe)\b",
    re.I,
)


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        for name, value in attrs:
            if name == "href" and value:
                self.hrefs.append(value)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def nearby_context(text: str, start: int, end: int, width: int = 180) -> str:
    return text[max(0, start - width) : min(len(text), end + width)]


def local_link_target_exists(source: Path, href: str) -> bool:
    if href.startswith(("http://", "https://", "mailto:", "#")):
        return True
    target = href.split("#", 1)[0]
    if not target:
        return True
    if target.startswith("../analog-digital-chip-design-eda"):
        return True
    return (source.parent / target).exists()


def check_html_links(path: Path, text: str) -> list[str]:
    parser = LinkParser()
    parser.feed(text)
    issues = []
    for href in parser.hrefs:
        if not local_link_target_exists(path, href):
            issues.append(f"{path.relative_to(ROOT)} links to missing target {href!r}")
    return issues


def check_contract_terms(path: Path, text: str) -> list[str]:
    lower = text.lower()
    role_table_contract = (
        all(term in lower for term in ["consumes", "produces", "refuses"])
        and any(term in lower for term in ["supports", "allowed"])
        and any(term in lower for term in ["next", "feeds", "handoff"])
    )
    if role_table_contract and any(term in lower for term in ["constraint", "checks", "risk", "boundary"]):
        return []
    missing = [
        group
        for group, aliases in CONTRACT_GROUPS.items()
        if not any(alias in lower for alias in aliases)
    ]
    if missing:
        return [f"{path.relative_to(ROOT)} is missing contract groups: {', '.join(missing)}"]
    return []


def check_system_map_link(path: Path, text: str) -> list[str]:
    rel = path.relative_to(ROOT).as_posix()
    if rel in {"connected-system-map.html", "page-contract-audit.html", "README.md"}:
        return []
    if "connected-system-map.html" not in text and "../connected-system-map.html" not in text:
        return [f"{rel} does not point back to connected-system-map.html"]
    return []


def check_boundary_language(path: Path, text: str) -> list[str]:
    lower = text.lower()
    required = ["measured", "blocked", "claim"]
    missing = [term for term in required if term not in lower]
    if missing:
        return [f"{path.relative_to(ROOT)} is missing measured-evidence boundary terms: {', '.join(missing)}"]
    return []


def check_unsafe_claims(path: Path, text: str) -> list[str]:
    issues = []
    for pattern in UNSAFE_CLAIM_PATTERNS:
        for match in pattern.finditer(text):
            context = nearby_context(text, match.start(), match.end())
            if not BLOCKING_CONTEXT.search(context):
                issues.append(
                    f"{path.relative_to(ROOT)} has unsafe claim wording without nearby blocked/refused context: "
                    f"{match.group(0)!r}"
                )
    return issues


def check_workbench_evidence_template_contract(text: str) -> list[str]:
    issues = []
    required_markers = [
        "const evidenceModeRequiredFields",
        'measured: {',
        'board_runtime: ["package_id", "workload_id", "board_id", "board_revision", "runtime_version", "runtime_trace_id", "latency_ms", "p50_latency_ms", "p95_latency_ms", "repetition_count", "start_timestamp", "end_timestamp", "host_overhead_boundary", "trace", "fallback_events", "provenance"]',
        'power_thermal: ["package_id", "workload_id", "board_id", "runtime_trace_id", "energy_uj", "average_power_mw", "peak_power_mw", "sampling_rate", "integration_start_timestamp", "integration_end_timestamp", "host_overhead_boundary", "power_trace", "temperature_trace", "measurement_setup", "provenance"]',
        "C3 remains needs-review unless this power file matches the runtime trace ID, package, workload, board, start time, and end time.",
        '["Package", detail.package_id]',
        '["Workload", detail.workload_id]',
        '["Power start", detail.integration_start_timestamp]',
        '["Power end", detail.integration_end_timestamp]',
        '["Measure level", detail.measurement_level]',
        "loadEvidenceTemplate();",
    ]
    for marker in required_markers:
        if marker not in text:
            issues.append(f"index.html missing frontend measured-evidence marker: {marker}")
    return issues


def check_workbench_review_path_contract(root: Path) -> list[str]:
    issues = []
    index_text = read_text(root / "index.html")
    master_text = read_text(root / "master-review-path.html")
    required_index_markers = [
        "simulator-to-placement boundary",
        "simulator-to-placement-decision-boundary.html",
        "Measured runtime and power claim path",
        "measured-runtime-power-claim-upgrade-path.html",
    ]
    required_master_markers = [
        "Current AIMC System State",
        "current-aimc-system-state.html",
        "Simulator To Placement Boundary",
        "Measured Runtime And Power Path",
        "AIHWKIT and CrossSim are installed and exercised through the current bridge.",
        "simulator-to-placement boundary",
        "measured-runtime/power path",
    ]
    for marker in required_index_markers:
        if marker not in index_text:
            issues.append(f"index.html missing AIMC review-path marker: {marker}")
    for marker in required_master_markers:
        if marker not in master_text:
            issues.append(f"master-review-path.html missing AIMC review-path marker: {marker}")
    for stale in [
        "AIHWKIT and CrossSim are checked but skipped",
        "records AIHWKIT as skipped",
        "records CrossSim as skipped",
    ]:
        if stale in index_text or stale in master_text:
            issues.append(f"old workbench still contains stale simulator status wording: {stale}")
    return issues


def main() -> int:
    issues: list[str] = []
    html_files = sorted({*CORE_HTML, *(
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("*.html")
        if not SKIP_PARTS.intersection(path.relative_to(ROOT).parts)
    )})
    md_files = sorted({*CORE_MD, *(
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("*.md")
        if not SKIP_PARTS.intersection(path.relative_to(ROOT).parts)
    )})

    for rel in html_files + md_files:
        path = ROOT / rel
        if not path.exists():
            issues.append(f"missing required page/spec: {rel}")
            continue
        text = read_text(path)
        issues.extend(check_contract_terms(path, text))
        issues.extend(check_system_map_link(path, text))
        issues.extend(check_unsafe_claims(path, text))
        if path.suffix == ".html":
            issues.extend(check_html_links(path, text))

    audit = ROOT / "page-contract-audit.html"
    if audit.exists():
        audit_text = read_text(audit)
        for stale in ['class="partial"', 'class="open"']:
            if stale in audit_text:
                issues.append(f"page-contract-audit.html still contains stale status marker {stale}")

    for rel in CRITICAL_BOUNDARY_FILES:
        path = ROOT / rel
        if path.exists():
            issues.extend(check_boundary_language(path, read_text(path)))

    index = ROOT / "index.html"
    if index.exists():
        issues.extend(check_workbench_evidence_template_contract(read_text(index)))
        issues.extend(check_workbench_review_path_contract(ROOT))

    if issues:
        print("FAIL page contract audit")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print("PASS page contract audit")
    print(f"checked_html={len(html_files)} checked_md={len(md_files)}")
    print("contract_groups=object,constraint,design_move,evidence,allowed_claim,refused_claim,next_handoff")
    print("measured_evidence_boundary=present")
    return 0


if __name__ == "__main__":
    sys.exit(main())
