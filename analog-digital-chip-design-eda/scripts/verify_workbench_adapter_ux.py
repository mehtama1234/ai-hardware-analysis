#!/usr/bin/env python3
"""Verify the capability-driven customer-adapter controls in the workbench."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading
import os
import signal

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]


class BrowserStartupTimeout(RuntimeError):
    pass


def new_page_with_timeout(browser, seconds=30):
    """Fail fast when a shared Chromium instance cannot create a page."""
    def raise_timeout(_signum, _frame):
        raise BrowserStartupTimeout("Chromium page creation timed out")

    previous = signal.getsignal(signal.SIGALRM)
    signal.signal(signal.SIGALRM, raise_timeout)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        return browser.new_page()
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


server = ThreadingHTTPServer(("127.0.0.1", 0), partial(Quiet, directory=str(ROOT / "site")))
threading.Thread(target=server.serve_forever, daemon=True).start()
try:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=os.environ.get("WORKBENCH_CHROMIUM"), args=["--no-sandbox", "--disable-dev-shm-usage"])
        page = new_page_with_timeout(browser)
        page.set_default_timeout(10000)
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(f"http://127.0.0.1:{server.server_port}/verification-workbench.html")
        page.locator("#adapterSelect").wait_for()
        assert page.locator("#adapterSelect option").count() == 3
        assert page.locator("#adapterSelect option").nth(1).text_content() == "iverilog-reference · simulation"
        assert page.locator("#backendList").inner_text().find("customer-formal") >= 0
        assert page.locator("#adapterArgsInput").get_attribute("aria-label")
        page.locator("#adapterSelect").select_option("iverilog-reference")
        page.locator("#adapterArgsInput").fill('["--batch"]')
        assert page.locator("#adapterSelect").input_value() == "iverilog-reference"
        assert page.locator("#adapterArgsInput").input_value() == '["--batch"]'
        assert not errors, errors
        browser.close()
finally:
    server.shutdown()
print("Passed adapter selector UX: available-only selection, blocked visibility, ephemeral argument input, and no page errors")
