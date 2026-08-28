import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path


REQUIRED_PAGE_MARKERS = [
    "Executive Read",
    "Engineering Read",
    "Demo Reading Path",
    "Package Source",
    "Artifact Count",
    "Proof Warning",
    "Review Rule",
    "Plain-Language Primer",
    "Top Blockers",
    "Why This Roadmap Exists Now",
    "Stack Change Map",
    "Modification Playbook",
    "Fourteen-Step User Journey",
    "Evidence Ladder",
    "What The Review Package Exports",
    "Readiness Audit Before Sharing",
    "Final Product Answer",
]

REQUIRED_TERM_MARKERS = [
    "Analog In-Memory Compute",
    "Hybrid Chip",
    "Compiler",
    "ADC And DAC",
    "Calibration",
    "Board Proof",
    "Power And Thermal Proof",
    "Transformer Or VLA Model",
    "Evidence Package",
    "USB, Ethernet, PCIe, JTAG, And UART",
]

REQUIRED_DYNAMIC_MARKERS = [
    "Artifact Status",
    "Artifact Source",
    "What This Supports",
    "What This Does Not Prove",
    "Missing Evidence",
    "Artifact Next Work",
    "Evidence This Step Needs",
    "Claims That Depend On It",
    "Diagram Links",
    "loadDemoPackageArtifactRecords",
    "renderPackageSummary",
    "dependencyList",
    "depends_on_steps",
    "unlocks_steps",
]

REQUIRED_MODIFICATION_PLAYBOOK_MARKERS = [
    "Plain meaning:",
    "Why we do it:",
    "What we reuse:",
    "What we build or modify:",
    "What the product shows:",
    "Proof required:",
    "Calibration And Chip Self-Checks",
    "Tiling And Bit-Slicing",
    "Transformer And VLA Partitioning",
    "ADC And DAC Scheduling",
    "Weight Update And Rollback Path",
    "Board Package And Hardware Run",
    "Backend Evidence Contract",
    "Frontend Review Experience",
]

REQUIRED_PACKAGE_INDEX_MARKERS = [
    "Demo Review Package",
    "Executive Answer",
    "End-To-End Goal",
    "Engineering Work Queue",
    "Journey Dependency Map",
    "Import Templates",
    "Proof warning:",
    "Executive Brief",
    "End-To-End Goal",
    "Engineering Queue",
    "Completion Audit",
    "Source Review",
    "Research Backlog",
    "Audience Export Map",
    "Reuse And Modification Map",
    "Action And Evidence Map",
    "Silicon To Board Proof Map",
    "Execution Roadmap",
    "Physical AI Opportunity Map",
    "Static Diagrams",
    "Rendered Screenshots",
    "Package Schema",
    "Raw Manifest",
    "Raw Final Answer",
    "Meeting Walkthrough",
    "Plain-Language Glossary",
    "Compiler placement",
    "Calibration trace",
    "Sensor path report",
]

REQUIRED_PACKAGE_INDEX_DYNAMIC_MARKERS = [
    "loadPackage",
    "renderSummary",
    "renderVerdict",
    "renderArtifacts",
    "renderDependencies",
    "What this supports:",
    "What this does not prove:",
    "Evidence this step needs:",
    "Claims that depend on it:",
    "Missing evidence:",
    "Next work:",
]

BROAD_CLAIM_WORDS = [
    "revolutionary",
    "unbeatable",
    "flawless",
    "seamless",
    "perfect",
    "guaranteed",
    "production-ready",
]

QUALIFYING_WORDS = [
    "not",
    "never",
    "avoid",
    "unless",
    "blocked",
    "candidate",
    "missing",
    "proof",
    "measured",
    "evidence",
]


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        text = data.strip()
        if text:
            self.parts.append(text)

    def text(self):
        return "\n".join(self.parts)


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def extract_text(html):
    parser = TextExtractor()
    parser.feed(html)
    return parser.text()


def sentence_for(text, start_index):
    left = max(text.rfind(".", 0, start_index), text.rfind("\n", 0, start_index))
    right_candidates = [index for index in [text.find(".", start_index), text.find("\n", start_index)] if index != -1]
    right = min(right_candidates) if right_candidates else len(text)
    return text[left + 1:right].strip()


def check_markers(text, markers, label):
    missing = [marker for marker in markers if marker not in text]
    assert_true(not missing, f"Missing {label}: {missing}")


def check_broad_claim_words(text):
    lowered = text.lower()
    failures = []
    for word in BROAD_CLAIM_WORDS:
        for match in re.finditer(rf"\b{re.escape(word)}\b", lowered):
            sentence = sentence_for(lowered, match.start())
            if not any(qualifier in sentence for qualifier in QUALIFYING_WORDS):
                failures.append({"word": word, "sentence": sentence})
    assert_true(not failures, f"Broad claim words need local qualification: {failures}")


def check_complete_sentence_density(text):
    sentence_count = len(re.findall(r"[.!?]", text))
    assert_true(sentence_count >= 120, "Roadmap page appears too short for the detailed readability contract.")


def main():
    parser = argparse.ArgumentParser(description="Validate the roadmap page readability contract.")
    parser.add_argument(
        "--html",
        default=Path(__file__).resolve().parents[2] / "company-roadmap-end-to-end.html",
        type=Path,
        help="Path to the roadmap HTML page.",
    )
    parser.add_argument(
        "--package-index",
        default=Path(__file__).resolve().parents[2] / "review-package-demo" / "index.html",
        type=Path,
        help="Path to the readable demo review package index.",
    )
    args = parser.parse_args()

    html = args.html.read_text()
    text = extract_text(html)
    check_markers(text, REQUIRED_PAGE_MARKERS, "page sections")
    check_markers(text, REQUIRED_TERM_MARKERS, "plain-language term explanations")
    check_markers(text, REQUIRED_MODIFICATION_PLAYBOOK_MARKERS, "modification playbook")
    check_markers(html, REQUIRED_DYNAMIC_MARKERS, "dynamic artifact UI markers")
    check_broad_claim_words(text)
    check_complete_sentence_density(text)

    package_index_html = args.package_index.read_text()
    package_index_text = extract_text(package_index_html)
    check_markers(package_index_text, REQUIRED_PACKAGE_INDEX_MARKERS, "package index sections")
    check_markers(package_index_html, REQUIRED_PACKAGE_INDEX_DYNAMIC_MARKERS, "package index dynamic markers")
    check_broad_claim_words(package_index_text)
    print("readability-contract-ok")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"readability contract failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
