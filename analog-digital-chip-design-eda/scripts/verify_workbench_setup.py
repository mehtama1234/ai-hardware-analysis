"""Exercise first-session setup against a real isolated service (no worker required)."""
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


def main():
    with tempfile.TemporaryDirectory(prefix='workbench-setup-') as directory:
        service.JOB_ROOT = Path(directory) / 'jobs'
        os.environ['VERIFICATION_SERVICE_API_KEY'] = 'browser-test-key'
        os.environ['VERIFICATION_EDA_ADAPTERS'] = '[{"name":"pilot-sim","kind":"simulation","executable":"iverilog","version":"open-source"}]'
        sock = socket.socket(); sock.bind(('127.0.0.1', 0))
        origin = 'http://127.0.0.1:' + str(sock.getsockname()[1])
        server = uvicorn.Server(uvicorn.Config(service.app, log_level='error'))
        thread = threading.Thread(target=server.run, kwargs={'sockets': [sock]}, daemon=True); thread.start()
        try:
            deadline = time.monotonic() + 10
            while not server.started:
                if time.monotonic() > deadline: raise RuntimeError('Service failed to start')
                time.sleep(.05)
            with sync_playwright() as p:
                browser = p.chromium.launch(executable_path=os.environ.get('WORKBENCH_CHROMIUM'), args=['--no-sandbox'])
                page = browser.new_page(viewport={'width':1440,'height':1024})
                errors=[];page.on('pageerror',lambda e: errors.append(str(e)))
                page.goto(origin+'/workbench/')
                page.get_by_role('button',name='Connection',exact=True).click()
                page.get_by_label('API key',exact=True).fill('wrong-key')
                page.get_by_role('button',name='Connect',exact=True).click()
                page.get_by_role('alert').filter(has_text='authentication failed').wait_for()
                page.get_by_label('API key',exact=True).fill('browser-test-key')
                page.get_by_role('button',name='Connect',exact=True).click()
                page.wait_for_url(lambda url: '?api=' in url)
                print('Connected with tab-scoped credentials', flush=True)
                page.get_by_role('button',name='+ New project').click()
                page.get_by_label('Project name',exact=True).fill('Browser pilot')
                page.get_by_label('Project ID',exact=True).fill('browser_pilot')
                page.get_by_role('button',name='Create project',exact=True).click()
                page.wait_for_url(lambda url: 'project=browser_pilot' in url)
                print('Created project', flush=True)
                for name,kind,content in [
                    ('counter.sv','rtl','module counter(output wire done); assign done=1; endmodule'),
                    ('tb.sv','testbench','module tb; wire done; counter dut(done); initial begin #1; if (!done) $fatal(1,"FAILED"); $finish; end endmodule')]:
                    page.get_by_role('button',name='Upload artifact',exact=True).click()
                    page.get_by_label('Filename',exact=True).fill(name)
                    page.get_by_label('Artifact kind',exact=True).select_option(kind)
                    page.get_by_label('Content',exact=True).fill(content)
                    page.locator('dialog').get_by_role('button',name='Upload artifact',exact=True).click()
                    page.locator('dialog').wait_for(state='hidden')
                    page.locator('.collateral-row').filter(has_text=name).wait_for()
                    print('Uploaded '+name, flush=True)
                page.get_by_role('button',name='Run verification').click()
                page.get_by_label('Check',exact=True).select_option('project-simulation')
                page.locator('[name="rtl"] option').first.wait_for(state='attached')
                page.locator('[name="testbenches"] option').first.wait_for(state='attached')
                assert 'Contract: verification-platform-contract-v1' in page.locator('#runInputStatus').inner_text()
                assert 'pilot-sim (simulation open-source): available' in page.locator('#runInputStatus').inner_text()
                page.get_by_role('button',name='Queue run',exact=True).click()
                page.locator('dialog').wait_for(state='hidden')
                jobs=service.list_jobs(project_id='browser_pilot')
                assert len(jobs)==1 and jobs[0]['status']=='queued',jobs
                assert jobs[0]['artifact_id'] and jobs[0]['testbench_artifact_id']
                page.reload()
                page.locator('#connectionState').wait_for()
                assert any(word in page.locator('#connectionState').inner_text().lower() for word in ('loaded', 'connected'))
                assert 'browser-test-key' not in page.url
                assert not page.locator('.detail-head .badge').is_visible()
                page.get_by_role('button', name='Cancel run', exact=False).click()
                page.get_by_text('cancelled', exact=True).wait_for()
                assert service.list_jobs(project_id='browser_pilot')[0]['status']=='cancelled'
                assert not errors, errors
                out=ROOT/'.artifacts'/'workbench-browser';out.mkdir(parents=True,exist_ok=True)
                page.screenshot(path=str(out/'setup-connected.png'))
                browser.close()
                print('Passed real-service setup: rejected bad key, connected, created project, uploaded RTL/checker, queued one bound run, reloaded authenticated session; no page errors.')
        finally:
            server.should_exit=True;thread.join(timeout=10);sock.close()


if __name__=='__main__': main()
