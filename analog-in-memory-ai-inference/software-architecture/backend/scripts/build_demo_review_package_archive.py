import argparse
import json
import sys
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from smoke_roadmap_demo_package import check_journey_alignment, check_static_package


REQUIRED_PACKAGE_FILES = [
    "README.md",
    "manifest.json",
    "schema.md",
    "index.html",
    "executive-brief.md",
    "end-to-end-meaty-goal.md",
    "meeting-walkthrough.md",
    "research-backlog.md",
    "plain-language-glossary.md",
    "audience-export-map.md",
    "reuse-modification-map.md",
    "action-evidence-map.md",
    "silicon-board-proof-map.md",
    "execution-roadmap.md",
    "physical-ai-opportunity-map.md",
    "static-diagrams.md",
    "rendered-screenshots.md",
    "engineering-work-queue.md",
    "completion-audit.md",
    "source-review-register.md",
]
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
REQUIRED_SCREENSHOTS = [
    "screenshots/company-roadmap-desktop.png",
    "screenshots/company-roadmap-mobile.png",
    "screenshots/review-package-index-desktop.png",
    "screenshots/review-package-index-mobile.png",
]


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def build_archive(package_dir, journey_path, output_path):
    manifest = check_static_package(package_dir)
    check_journey_alignment(package_dir, journey_path)

    entries = []
    for relative_name in REQUIRED_PACKAGE_FILES:
        source_path = package_dir / relative_name
        assert_true(source_path.exists(), f"Missing package file: {relative_name}")
        entries.append((source_path, f"review-package-demo/{relative_name}"))

    for relative_name in REQUIRED_IMPORT_TEMPLATES:
        source_path = package_dir / relative_name
        assert_true(source_path.exists(), f"Missing import template file: {relative_name}")
        entries.append((source_path, f"review-package-demo/{relative_name}"))

    for relative_name in REQUIRED_SCREENSHOTS:
        source_path = package_dir / relative_name
        assert_true(source_path.exists(), f"Missing screenshot file: {relative_name}")
        entries.append((source_path, f"review-package-demo/{relative_name}"))

    for artifact_name in manifest["artifacts"]:
        source_path = package_dir / artifact_name
        assert_true(source_path.exists(), f"Missing artifact file: {artifact_name}")
        entries.append((source_path, f"review-package-demo/{artifact_name}"))

    assert_true(journey_path.exists(), f"Missing journey file: {journey_path}")
    entries.append((journey_path, "roadmap-journey-demo.json"))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output_path, "w", compression=ZIP_DEFLATED) as archive:
        for source_path, archive_name in entries:
            archive.write(source_path, archive_name)

    return {
        "result": "ok",
        "package_id": manifest["package_id"],
        "archive_path": str(output_path),
        "entry_count": len(entries),
        "artifact_count": manifest["artifact_count"],
        "entries": [archive_name for _, archive_name in entries],
    }


def main():
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description="Build the demo roadmap review package archive.")
    parser.add_argument(
        "--package-dir",
        default=root / "review-package-demo",
        type=Path,
        help="Path to the demo review package directory.",
    )
    parser.add_argument(
        "--journey",
        default=root / "roadmap-journey-demo.json",
        type=Path,
        help="Path to the roadmap journey demo contract.",
    )
    parser.add_argument(
        "--output",
        default=root / "review-package-demo" / "demo-analog-roadmap-001-package.zip",
        type=Path,
        help="Path for the generated zip archive.",
    )
    args = parser.parse_args()

    result = build_archive(args.package_dir, args.journey, args.output)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"archive build failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
