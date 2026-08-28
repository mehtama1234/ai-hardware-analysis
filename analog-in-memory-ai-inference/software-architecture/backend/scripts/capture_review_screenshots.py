import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen


SCREENSHOTS = [
    {
        "name": "company-roadmap-desktop.png",
        "url_path": "/company-roadmap-end-to-end.html",
        "viewport": "1440,1400",
    },
    {
        "name": "company-roadmap-mobile.png",
        "url_path": "/company-roadmap-end-to-end.html",
        "viewport": "390,1200",
    },
    {
        "name": "review-package-index-desktop.png",
        "url_path": "/review-package-demo/index.html",
        "viewport": "1440,1200",
    },
    {
        "name": "review-package-index-mobile.png",
        "url_path": "/review-package-demo/index.html",
        "viewport": "390,1200",
    },
]


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def check_server(base_url):
    try:
        with urlopen(f"{base_url}/company-roadmap-end-to-end.html", timeout=5) as response:
            body = response.read(2000).decode("utf-8", errors="replace")
    except URLError as exc:
        raise AssertionError(f"Static server is not reachable at {base_url}: {exc}") from exc
    assert_true("Analog" in body or "roadmap" in body.lower(), "Static server returned unexpected page content.")


def capture_screenshot(playwright_bin, base_url, output_dir, spec):
    output_path = output_dir / spec["name"]
    command = [
        playwright_bin,
        "screenshot",
        f"--viewport-size={spec['viewport']}",
        "--full-page",
        f"{base_url}{spec['url_path']}",
        str(output_path),
    ]
    subprocess.run(command, check=True)
    return {
        "file": str(output_path),
        "url": f"{base_url}{spec['url_path']}",
        "viewport": spec["viewport"],
        "bytes": output_path.stat().st_size,
    }


def main():
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description="Capture rendered screenshots for the demo review package.")
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:8080",
        help="Base URL for the running static server.",
    )
    parser.add_argument(
        "--output-dir",
        default=root / "review-package-demo" / "screenshots",
        type=Path,
        help="Directory where screenshots should be written.",
    )
    args = parser.parse_args()

    playwright_bin = shutil.which("playwright")
    assert_true(playwright_bin, "Playwright CLI is required. Run `playwright install chromium` if browsers are missing.")
    check_server(args.base_url)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    captures = [
        capture_screenshot(playwright_bin, args.base_url.rstrip("/"), args.output_dir, spec)
        for spec in SCREENSHOTS
    ]
    print(json.dumps({"result": "ok", "captures": captures}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, subprocess.CalledProcessError) as exc:
        print(f"screenshot capture failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
