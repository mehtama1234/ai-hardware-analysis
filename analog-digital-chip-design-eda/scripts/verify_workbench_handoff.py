"""Browser-level evidence report, bundle preview, and signoff check."""

import os
from pathlib import Path
import socket
import sys
import tempfile
import threading
import time

import uvicorn
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from deployment import verification_service as service
from deployment import worker

def wait_for_text(page, selector, predicate, timeout=8):
    deadline = time.monotonic() + timeout
    locator = page.locator(selector)
    while time.monotonic() < deadline:
        if predicate(locator.inner_text()):
            return
        page.wait_for_timeout(100)
    raise AssertionError(f"Timed out waiting for {selector}: {locator.inner_text()!r}")


def main():
    with tempfile.TemporaryDirectory(prefix="workbench-handoff-") as directory:
        jobs = Path(directory) / "jobs"
        service.JOB_ROOT = jobs
        worker.JOB_ROOT = jobs
        os.environ["VERIFICATION_SERVICE_API_KEY"] = "handoff-browser-key"
        project = service.create_project(service.ProjectRequest(id="handoff", name="Handoff"))
        service.create_project(service.ProjectRequest(id="second", name="Second project"))
        rtl = service.add_collateral(project["id"], service.CollateralRequest(name="dut.sv", kind="rtl", content="module dut(output wire done); assign done = 1'b1; endmodule\n"))
        tb = service.add_collateral(project["id"], service.CollateralRequest(name="tb.sv", kind="testbench", content=(
            "module tb; wire done; dut d(done); initial begin $dumpfile(\"waveform.vcd\"); $dumpvars(0,tb); #1; "
            "if (!done) $display(\"FAIL cycle=1 signal=done expected=1 actual=0\"); else $display(\"PASS\"); $finish; end endmodule\n")))
        job = service.create_job(service.JobRequest(kind="project-simulation", project_id="handoff", artifact_id=rtl["id"], testbench_artifact_id=tb["id"]))
        worker.process_once(job_timeout_seconds=30)
        assert service.get_job(job["id"])["status"] == "passed"

        sock = socket.socket(); sock.bind(("127.0.0.1", 0))
        origin = "http://127.0.0.1:" + str(sock.getsockname()[1])
        server = uvicorn.Server(uvicorn.Config(service.app, log_level="error"))
        thread = threading.Thread(target=server.run, kwargs={"sockets": [sock]}, daemon=True); thread.start()
        try:
            deadline = time.monotonic() + 10
            while not server.started:
                if time.monotonic() > deadline: raise RuntimeError("service did not start")
                time.sleep(.05)
            with sync_playwright() as p:
                browser = p.chromium.launch(executable_path=os.environ.get("WORKBENCH_CHROMIUM"), args=["--no-sandbox"])
                page = browser.new_page(viewport={"width": 1440, "height": 1024})
                page.set_default_timeout(8000)
                errors=[]; page.on("pageerror", lambda error: errors.append(str(error)))
                page.goto(origin + "/workbench/")
                print("Opened service workbench", flush=True)
                page.evaluate("([origin,key]) => sessionStorage.setItem('workbench.apiKey:'+origin,key)", [origin, "handoff-browser-key"])
                page.goto(origin + "/workbench/verification-workbench.html?api=" + origin + "&project=handoff")
                print("Opened connected project", flush=True)
                page.locator(".job-select").first.wait_for()
                print("Run row loaded", flush=True)
                page.locator(".job-select").first.click()
                page.wait_for_url(lambda url: "job=" in url)
                print("Run evidence loaded", flush=True)
                assert 'job=' in page.url
                page.reload()
                wait_for_text(page, '#failureHeading', lambda value: value == job["id"])
                assert page.locator('#failureHeading').inner_text() == job["id"]
                print("Run context restored after reload", flush=True)
                page.get_by_role("button", name="Load latest PoV", exact=True).click()
                print("Requested PoV", flush=True)
                page.get_by_text("Bound to "+job["id"][:10], exact=False).wait_for()
                print("PoV loaded", flush=True)
                page.get_by_role("button", name="Preview bundle", exact=True).click()
                print("Requested bundle", flush=True)
                page.get_by_text("Bundle for "+job["id"], exact=False).wait_for()
                print("Bundle loaded", flush=True)
                with page.expect_download() as download_info:
                    page.get_by_role("button", name="Download bundle", exact=True).click()
                download=download_info.value
                assert download.suggested_filename == "verification-"+job["id"]+".zip"
                print("Downloaded immutable bundle", flush=True)
                page.get_by_role("button", name="Sign off package", exact=True).click()
                print("Opened signoff", flush=True)
                page.get_by_label("Reviewer name", exact=True).fill("verification lead")
                page.get_by_label("Review notes", exact=True).fill("Reviewed the selected run, waveform availability, scope, and remaining obligations.")
                page.get_by_label("Decision", exact=True).select_option("true")
                page.get_by_role("button", name="Record decision", exact=True).click()
                print("Recorded signoff", flush=True)
                wait_for_text(page, '#reportState', lambda value: 'Approved' in value or 'Review required' in value)
                print("Signoff state visible", flush=True)
                assert (jobs / job["id"] / "pilot-signoff.json").is_file()
                page.reload()
                wait_for_text(page, '#failureHeading', lambda value: value == job["id"])
                page.get_by_role("button", name="Load latest PoV", exact=True).click()
                wait_for_text(page, '#reportState', lambda value: 'Approved' in value)
                print("Restored signoff receipt after reload", flush=True)
                page.locator("#projectSelect").evaluate("el=>el.value='second'")
                print("Requested project switch", flush=True)
                page.goto(origin + "/workbench/verification-workbench.html?api=" + origin + "&project=second", wait_until="domcontentloaded")
                page.wait_for_url(lambda url: "project=second" in url)
                wait_for_text(page, '#failureHeading', lambda value: value == 'No run selected')
                assert not page.locator("#evidenceView").is_visible()
                assert page.locator("#reportState").inner_text() == "No report selected"
                assert page.locator("#artifactInspector").get_attribute("hidden") is not None
                assert page.locator("#runButton").is_disabled()
                assert "Setup required" in page.locator(".status-line").inner_text()
                assert not errors, errors
                out=ROOT/".artifacts"/"workbench-browser"; out.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(out/"handoff-signed.png"))
                browser.close()
                print("Passed browser handoff: selected run, restored it after reload, loaded run-bound PoV, previewed bundle inventory, recorded reviewer decision, and isolated state on project switch; no page errors.")
        finally:
            server.should_exit=True; thread.join(timeout=10); sock.close()


if __name__ == "__main__": main()
