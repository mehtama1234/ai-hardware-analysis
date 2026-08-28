import argparse
import json
import sys
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen
from zipfile import ZipFile


REQUIRED_ARTIFACT_FIELDS = {
    "schema_version",
    "artifact_id",
    "step",
    "title",
    "proof_level",
    "status",
    "plain_reading",
    "what_this_supports",
    "what_this_does_not_prove",
    "missing_evidence",
    "next_actions",
}

REQUIRED_JOURNEY_STEP_FIELDS = {
    "title",
    "phase",
    "intro",
    "question",
    "evidence",
    "next",
    "primary",
    "secondary",
    "result",
    "missing",
    "artifact",
    "proof_level",
    "upstream_evidence",
    "downstream_claims",
    "depends_on_steps",
    "unlocks_steps",
}

REQUIRED_IMPORT_TEMPLATES = [
    "import-templates/README.md",
    "import-templates/compiler-placement.template.json",
    "import-templates/analog-error-simulation.template.json",
    "import-templates/board-runtime-trace.template.json",
    "import-templates/power-thermal-report.template.json",
    "import-templates/calibration-trace.template.json",
    "import-templates/weight-update-report.template.json",
    "import-templates/sensor-path-report.template.json",
    "import-templates/task-accuracy-report.template.json",
]

REQUIRED_SCREENSHOTS = {
    "screenshots/company-roadmap-desktop.png": (1440, 1000),
    "screenshots/company-roadmap-mobile.png": (390, 1000),
    "screenshots/review-package-index-desktop.png": (1440, 1000),
    "screenshots/review-package-index-mobile.png": (390, 1000),
}

REQUIRED_FINAL_BLOCKED_CLAIM_MARKERS = [
    "full VLA readiness",
    "measured power",
    "adaptive update readiness",
]

FORBIDDEN_SAFE_CLAIM_MARKERS = [
    "chip is production-ready",
    "production-ready",
    "full VLA readiness",
    "full VLA workload runs",
    "measured power",
    "measured chip performance",
    "board measured lower energy",
    "calibration is proven",
    "adaptive updates are proven",
    "adaptive update readiness",
    "ready for all",
]


def load_json(path):
    return json.loads(path.read_text())


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def check_png_not_blank(path):
    try:
        from PIL import Image, ImageStat
    except ImportError as exc:
        raise AssertionError("Pillow is required for screenshot content validation.") from exc

    with Image.open(path) as image:
        rgb_image = image.convert("RGB")
        scale = min(240 / rgb_image.width, 1600 / rgb_image.height, 1.0)
        thumbnail_width = max(1, int(rgb_image.width * scale))
        thumbnail_height = max(1, int(rgb_image.height * scale))
        thumbnail = rgb_image.resize((thumbnail_width, thumbnail_height))
        stat = ImageStat.Stat(thumbnail)
        try:
            pixels = list(thumbnail.get_flattened_data())
        except AttributeError:
            pixels = list(thumbnail.getdata())

    channel_ranges = []
    for channel_index in range(3):
        values = [pixel[channel_index] for pixel in pixels]
        channel_ranges.append(max(values) - min(values))
    assert_true(
        max(channel_ranges) >= 35,
        f"Screenshot appears blank or too uniform: {path} ranges={channel_ranges}",
    )
    assert_true(
        max(stat.stddev) >= 3.0,
        f"Screenshot has too little contrast: {path} stddev={stat.stddev}",
    )
    visible_content = sum(
        1
        for red, green, blue in pixels
        if min(red, green, blue) < 210 or abs(red - green) > 12 or abs(green - blue) > 12
    )
    assert_true(
        visible_content / len(pixels) >= 0.01,
        f"Screenshot has too little visible content: {path}",
    )


def text_blob(value):
    if isinstance(value, dict):
        return " ".join(text_blob(item) for item in value.values())
    if isinstance(value, list):
        return " ".join(text_blob(item) for item in value)
    return str(value)


def check_artifact_claim_boundaries(artifact_name, artifact):
    for field in [
        "what_this_supports",
        "what_this_does_not_prove",
        "missing_evidence",
        "next_actions",
    ]:
        assert_true(
            isinstance(artifact.get(field), list) and artifact[field],
            f"{artifact_name} must have non-empty {field}.",
        )

    support_text = text_blob(artifact["what_this_supports"]).lower()
    forbidden_support_markers = [
        "production-ready",
        "full vla readiness",
        "measured chip performance",
        "measured power",
        "adaptive updates are proven",
    ]
    leaked = [marker for marker in forbidden_support_markers if marker in support_text]
    assert_true(not leaked, f"{artifact_name} support text overclaims: {leaked}")


def check_final_claim_boundary(final):
    for field in ["fit", "safe_claim", "do_not_claim", "proof_have", "proof_missing"]:
        assert_true(field in final, f"final_answer.json missing {field}.")
    assert_true(final["fit"] == "partial", "Demo final answer should remain partial fit.")

    safe_text = text_blob(final["safe_claim"]).lower()
    forbidden = [marker for marker in FORBIDDEN_SAFE_CLAIM_MARKERS if marker.lower() in safe_text]
    assert_true(not forbidden, f"Final safe claims include blocked wording: {forbidden}")

    blocked_text = text_blob(final["do_not_claim"]).lower()
    missing_blocked = [
        marker for marker in REQUIRED_FINAL_BLOCKED_CLAIM_MARKERS if marker.lower() not in blocked_text
    ]
    assert_true(not missing_blocked, f"Final blocked claims missing markers: {missing_blocked}")

    missing_text = text_blob(final["proof_missing"]).lower()
    for marker in ["board runtime trace", "power and thermal trace", "task accuracy result"]:
        assert_true(marker in missing_text, f"Final proof_missing must keep {marker} visible.")


def check_static_package(package_dir):
    package_docs = {
        "executive-brief.md": ["Current Answer", "What Is Safe To Say", "What Is Not Safe To Say", "Top Blockers"],
        "end-to-end-meaty-goal.md": ["End-To-End Meaty Goal", "Executive Goal", "Developer Goal", "Diagrams And Animations", "Acceptance Bar"],
        "meeting-walkthrough.md": ["20-Minute Walkthrough", "Before The Meeting", "Audience-Specific Use", "Closeout Sentence"],
        "research-backlog.md": ["Research Backlog", "Source Standards", "Research Passes", "What Research Can Change"],
        "plain-language-glossary.md": ["Plain-Language Glossary", "Analog In-Memory Compute", "ADC And DAC", "USB, Ethernet, PCIe, JTAG, And UART"],
        "audience-export-map.md": ["Audience Export Map", "Customer Technical Team", "Engineering Lead", "Shared Rule"],
        "reuse-modification-map.md": ["Reuse And Modification Map", "What We Must Own", "What We Should Not Build From Scratch First", "Product Meaning"],
        "action-evidence-map.md": ["Action And Evidence Map", "Run Actions", "Import Actions", "What The Backend Must Enforce"],
        "silicon-board-proof-map.md": ["Silicon To Board Proof Map", "End-To-End Hardware Proof Path", "Minimum Hardware Evidence Set", "Product Meaning"],
        "execution-roadmap.md": ["Execution Roadmap", "Phase 1: Proof Workbench", "Cross-Phase Owners", "Program Review Questions"],
        "physical-ai-opportunity-map.md": ["Physical AI Opportunity Map", "Best First Targets", "First-Market Filter", "Recommended First Wedge"],
        "static-diagrams.md": ["Static Diagrams", "Diagram 1: Full Product Flow", "Diagram 3: Proof Ladder", "Diagram 6: What The Company Must Own"],
        "rendered-screenshots.md": ["Rendered Screenshots", "Screenshot Set", "Review Use", "capture_review_screenshots.py", "Visual QA Checklist", "Claim Boundary"],
        "engineering-work-queue.md": ["Build Now", "Backend Work", "Frontend Work", "Test Work"],
        "completion-audit.md": ["Current Verdict", "Requirement Audit", "What Is Proven By The Current Package", "What Is Not Proven Yet", "Claim Rule", "selected blocked-claim leakage", "Physical AI opportunity focus"],
        "source-review-register.md": ["Source Use Rules", "Checked Examples", "Unchecked Or Hidden By Default", "Package Rule"],
        "import-templates/README.md": ["compiler-placement.template.json", "calibration-trace.template.json", "sensor-path-report.template.json"],
    }
    for doc_name, markers in package_docs.items():
        doc_path = package_dir / doc_name
        assert_true(doc_path.exists(), f"{doc_name} is missing.")
        doc_text = doc_path.read_text()
        for marker in markers:
            assert_true(marker in doc_text, f"{doc_name} missing marker: {marker}")

    schema_path = package_dir / "schema.md"
    assert_true(schema_path.exists(), "Package schema.md is missing.")
    schema_text = schema_path.read_text()
    for marker in [
        "Manifest",
        "Step Artifact",
        "Alignment Rule",
        "Journey Dependency Fields",
        "Claim Rule",
        "what_this_supports",
        "what_this_does_not_prove",
        "upstream_evidence",
        "downstream_claims",
    ]:
        assert_true(marker in schema_text, f"Package schema.md missing marker: {marker}")

    manifest = load_json(package_dir / "manifest.json")
    assert_true(manifest["schema_version"] == "review_package_manifest.v1", "Manifest schema mismatch.")
    artifacts = manifest["artifacts"]
    assert_true(len(artifacts) == 14, "Manifest must list 14 artifacts.")
    assert_true(manifest["artifact_count"] == len(artifacts), "Manifest artifact_count mismatch.")

    seen = set()
    for index, artifact_name in enumerate(artifacts, start=1):
        artifact_path = package_dir / artifact_name
        assert_true(artifact_path.exists(), f"Missing artifact file: {artifact_name}")
        artifact = load_json(artifact_path)
        missing = REQUIRED_ARTIFACT_FIELDS - set(artifact)
        assert_true(not missing, f"{artifact_name} missing fields: {sorted(missing)}")
        assert_true(artifact["schema_version"] == "roadmap_step_artifact.v1", f"{artifact_name} schema mismatch.")
        assert_true(artifact["step"] == index, f"{artifact_name} step mismatch.")
        assert_true(artifact["artifact_id"] not in seen, f"Duplicate artifact id: {artifact['artifact_id']}")
        check_artifact_claim_boundaries(artifact_name, artifact)
        seen.add(artifact["artifact_id"])

    for template_name in REQUIRED_IMPORT_TEMPLATES:
        template_path = package_dir / template_name
        assert_true(template_path.exists(), f"Missing import template: {template_name}")
        if template_name.endswith(".json"):
            template = load_json(template_path)
            assert_true(template["schema_version"] == "evidence_import_template.v1", f"{template_name} schema mismatch.")
            assert_true(template.get("source_id"), f"{template_name} source_id missing.")
            assert_true(template.get("artifact_name"), f"{template_name} artifact_name missing.")
            assert_true(template.get("plain_reading"), f"{template_name} plain_reading missing.")
            assert_true(isinstance(template.get("required_fields"), list) and template["required_fields"], f"{template_name} required_fields missing.")
            assert_true(isinstance(template.get("template_payload"), dict), f"{template_name} template_payload missing.")
            assert_true(template.get("claim_rule"), f"{template_name} claim_rule missing.")

    for screenshot_name, (min_width, min_height) in REQUIRED_SCREENSHOTS.items():
        screenshot_path = package_dir / screenshot_name
        assert_true(screenshot_path.exists(), f"Missing screenshot: {screenshot_name}")
        assert_true(screenshot_path.stat().st_size > 10_000, f"Screenshot appears too small: {screenshot_name}")
        header = screenshot_path.read_bytes()[:24]
        assert_true(header.startswith(b"\x89PNG\r\n\x1a\n"), f"Screenshot is not a PNG: {screenshot_name}")
        width = int.from_bytes(header[16:20], "big")
        height = int.from_bytes(header[20:24], "big")
        assert_true(width >= min_width, f"Screenshot width too small for {screenshot_name}: {width}")
        assert_true(height >= min_height, f"Screenshot height too small for {screenshot_name}: {height}")
        check_png_not_blank(screenshot_path)
    return manifest


def check_journey_alignment(package_dir, journey_path):
    manifest = load_json(package_dir / "manifest.json")
    journey = load_json(journey_path)
    steps = journey.get("steps") or []
    assert_true(journey.get("schema_version") == "roadmap_journey_demo.v1", "Journey schema mismatch.")
    assert_true(len(steps) == 14, "Journey must contain 14 steps.")
    assert_true(len(steps) == len(manifest["artifacts"]), "Journey and manifest artifact counts differ.")

    for index, (step, artifact_name) in enumerate(zip(steps, manifest["artifacts"]), start=1):
        missing_step_fields = REQUIRED_JOURNEY_STEP_FIELDS - set(step)
        assert_true(not missing_step_fields, f"Step {index} missing fields: {sorted(missing_step_fields)}")
        assert_true(
            isinstance(step["upstream_evidence"], list) and step["upstream_evidence"],
            f"Step {index} must list upstream evidence.",
        )
        assert_true(
            isinstance(step["downstream_claims"], list) and step["downstream_claims"],
            f"Step {index} must list downstream claims.",
        )
        assert_true(isinstance(step["depends_on_steps"], list), f"Step {index} must list dependency step numbers.")
        assert_true(isinstance(step["unlocks_steps"], list), f"Step {index} must list unlocked step numbers.")
        linked_steps = step["depends_on_steps"] + step["unlocks_steps"]
        assert_true(
            all(isinstance(step_number, int) and 1 <= step_number <= 14 for step_number in linked_steps),
            f"Step {index} has invalid dependency links.",
        )
        artifact = load_json(package_dir / artifact_name)
        expected_filename = Path(artifact_name).name
        assert_true(step["artifact"] == expected_filename, f"Step {index} artifact filename mismatch.")
        assert_true(step["proof_level"] == artifact["proof_level"], f"Step {index} proof level mismatch.")
        assert_true(step["title"] == artifact["title"], f"Step {index} title mismatch.")
        assert_true(artifact["step"] == index, f"Artifact {artifact_name} step mismatch.")

    final = load_json(package_dir / "artifacts" / "final_answer.json")
    check_final_claim_boundary(final)


def check_archive(package_dir, journey_path, archive_path):
    assert_true(archive_path.exists(), f"Package archive is missing: {archive_path}")
    manifest = load_json(package_dir / "manifest.json")
    expected_entries = {
        "review-package-demo/README.md",
        "review-package-demo/manifest.json",
        "review-package-demo/schema.md",
        "review-package-demo/index.html",
        "review-package-demo/executive-brief.md",
        "review-package-demo/end-to-end-meaty-goal.md",
        "review-package-demo/meeting-walkthrough.md",
        "review-package-demo/research-backlog.md",
        "review-package-demo/plain-language-glossary.md",
        "review-package-demo/audience-export-map.md",
        "review-package-demo/reuse-modification-map.md",
        "review-package-demo/action-evidence-map.md",
        "review-package-demo/silicon-board-proof-map.md",
        "review-package-demo/execution-roadmap.md",
        "review-package-demo/physical-ai-opportunity-map.md",
        "review-package-demo/static-diagrams.md",
        "review-package-demo/rendered-screenshots.md",
        "review-package-demo/engineering-work-queue.md",
        "review-package-demo/completion-audit.md",
        "review-package-demo/source-review-register.md",
        "roadmap-journey-demo.json",
    }
    expected_entries.update(f"review-package-demo/{artifact_name}" for artifact_name in manifest["artifacts"])
    expected_entries.update(f"review-package-demo/{template_name}" for template_name in REQUIRED_IMPORT_TEMPLATES)
    expected_entries.update(f"review-package-demo/{screenshot_name}" for screenshot_name in REQUIRED_SCREENSHOTS)

    with ZipFile(archive_path) as archive:
        actual_entries = set(archive.namelist())

    missing_entries = expected_entries - actual_entries
    assert_true(not missing_entries, f"Package archive missing entries: {sorted(missing_entries)}")
    extra_archives = [entry for entry in actual_entries if entry.endswith(".zip")]
    assert_true(not extra_archives, f"Package archive should not contain nested zip files: {extra_archives}")
    assert_true(
        len(actual_entries) == len(expected_entries),
        f"Package archive entry count mismatch: expected {len(expected_entries)}, got {len(actual_entries)}",
    )


def fetch_json(url):
    with urlopen(url, timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


def check_live_endpoints(base_url):
    package = fetch_json(f"{base_url.rstrip('/')}/roadmap-demo-package")
    assert_true(package["result_type"] == "roadmap_demo_review_package", "Package endpoint result_type mismatch.")
    assert_true(package["artifact_count"] == 14, "Package endpoint artifact_count mismatch.")
    assert_true(len(package["artifact_records"]) == 14, "Package endpoint artifact_records mismatch.")

    final = fetch_json(f"{base_url.rstrip('/')}/roadmap-demo-package/artifacts/final_answer")
    assert_true(final["result_type"] == "roadmap_demo_review_artifact", "Final artifact endpoint result_type mismatch.")
    assert_true(final["artifact"]["fit"] == "partial", "Final artifact fit should be partial for the demo package.")


def main():
    parser = argparse.ArgumentParser(description="Validate the roadmap demo review package.")
    parser.add_argument(
        "--package-dir",
        default=Path(__file__).resolve().parents[2] / "review-package-demo",
        type=Path,
        help="Path to the demo review package directory.",
    )
    parser.add_argument(
        "--base-url",
        default=None,
        help="Optional running backend base URL, for example http://127.0.0.1:8020.",
    )
    parser.add_argument(
        "--journey",
        default=Path(__file__).resolve().parents[2] / "roadmap-journey-demo.json",
        type=Path,
        help="Path to the roadmap journey demo contract.",
    )
    parser.add_argument(
        "--archive",
        default=Path(__file__).resolve().parents[2] / "review-package-demo" / "demo-analog-roadmap-001-package.zip",
        type=Path,
        help="Path to the generated demo review package archive.",
    )
    args = parser.parse_args()

    manifest = check_static_package(args.package_dir)
    check_journey_alignment(args.package_dir, args.journey)
    check_archive(args.package_dir, args.journey, args.archive)
    live_status = "not requested"
    if args.base_url:
        try:
            check_live_endpoints(args.base_url)
            live_status = "ok"
        except URLError as exc:
            raise AssertionError(f"Could not reach backend at {args.base_url}: {exc}") from exc

    print(
        json.dumps(
            {
                "result": "ok",
                "package_id": manifest["package_id"],
                "artifact_count": manifest["artifact_count"],
                "archive": str(args.archive),
                "live_endpoint_check": live_status,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"smoke failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
