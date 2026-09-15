"""Behavioral smoke checks; requires Playwright and its Chromium browser.

Optionally set WORKBENCH_CHROMIUM to an installed Chromium executable.
"""
import json, threading, os
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root/'site')))
threading.Thread(target=server.serve_forever,daemon=True).start()
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path=os.environ.get('WORKBENCH_CHROMIUM'),args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':1440,'height':1024}); errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 url=f'http://127.0.0.1:{server.server_port}/verification-workbench.html'
 page.goto(url)
 assert page.locator('[data-context="project"]').inner_text()=='Orion_NPU'
 assert page.locator('[data-context="evidence"]').inner_text()=='Illustrative sample'
 assert 'Explore the sample journey' in page.locator('[data-context="next"]').inner_text()
 assert page.locator('.confidence').inner_text()=='Assessment: review required'
 assert page.locator('#backendPanel').is_visible()
 assert '2/3 available' in page.locator('#backendSummary').inner_text()
 assert 'customer-formal' in page.locator('#backendList').inner_text()
 assert page.locator('#commercialReadiness').is_visible()
 assert 'Sample workspace only' in page.locator('#readinessBody').inner_text()
 assert 'Draft · n=5' in page.locator('#scorecardSummary').inner_text()
 assert 'baseline and customer ROI have not been collected' in page.locator('#scorecardBody').inner_text()
 page.locator('.top-actions .search').fill('pooling')
 assert page.locator('#failureList .failure:visible').count()==1
 page.locator('.top-actions .search').fill('no-such-evidence')
 assert 'No matching runs' in page.locator('#connectionState').inner_text()
 page.locator('.top-actions .search').fill('')
 page.locator('.failure').nth(1).click()
 assert not page.locator('#evidenceView').is_visible()
 assert 'No evidence fixture' in page.locator('#alternateView').inner_text()
 page.locator('[data-tab="evidence"]').click()
 assert not page.locator('#evidenceView').is_visible()
 page.evaluate("window.workbenchReport={execution:{status:'failed'},claim_boundary:'<img src=x onerror=alert(1)>'}")
 page.locator('[data-tab="analysis"]').click()
 assert page.locator('#alternateView img').count()==0
 assert '<img src=x' in page.locator('#alternateView').inner_text()
 page.locator('.collateral-row').first.click()
 assert page.locator('#artifactInspector').is_visible()
 page.locator('#collateralSearch').fill('no-matching-file')
 assert page.locator('.collateral-row:visible').count()==0
 page.locator('[data-view="reports"]').click()
 assert page.evaluate('scrollY')>0
 page.locator('#loadReport').click()
 assert page.locator('#signoffButton').is_disabled()
 page.set_viewport_size({'width':390,'height':844})
 assert page.locator('.nav').is_visible()
 unnamed=page.locator('input,select,textarea').evaluate_all("els => els.filter(e => !e.labels?.length && !e.getAttribute('aria-label') && !e.getAttribute('aria-labelledby')).map(e => e.outerHTML)")
 assert not unnamed, 'unnamed form controls: '+json.dumps(unnamed)
 page.keyboard.press('Tab')
 assert page.locator(':focus').count()==1
 page.route('**/v1/**',lambda r:r.fulfill(status=401,json={'detail':'invalid key'}))
 page.goto(url+'?api='+f'http://127.0.0.1:{server.server_port}'+'&project=missing')
 page.wait_for_function("document.querySelector('#workspaceMode').textContent.includes('unavailable') || document.querySelector('#workspaceMode').textContent.includes('failed')")
 assert not page.locator('.metrics').is_visible()
 assert not page.locator('#evidenceView').is_visible()
 assert page.locator('.failure').count()==0
 assert page.locator('#projectSelect option').count()==0
 assert not errors,errors
 timeout_page=browser.new_page(viewport={'width':1440,'height':1024});timeout_errors=[];timeout_page.on('pageerror',lambda e:timeout_errors.append(str(e)))
 mock_origin='http://mock-verification.local'
 timeout_job={'id':'formal-timeout-1','project_id':'timeout','kind':'project-formal-proof','status':'blocked','artifact_id':'rtl-timeout','created_at':'2026-09-09T00:00:00Z','events':[{'status':'queued'},{'status':'running'},{'status':'blocked'}],'error':'formal solver exceeded the configured timeout'}
 def timeout_route(route):
  u=route.request.url
  if u.endswith('/v1/projects'): return route.fulfill(json=[{'id':'timeout','name':'Timeout project'}])
  if u.endswith('/dashboard'): return route.fulfill(json={'project':{'id':'timeout','name':'Timeout project'},'collateral_count':0,'jobs':{}})
  if '/v1/jobs?' in u: return route.fulfill(json=[timeout_job])
  if u.endswith('/evidence'): return route.fulfill(json={'job':timeout_job,'artifacts':{},'files':{},'waveform':{'present':False,'path':'simulation/waveform.vcd'}})
  if u.endswith('/v1/jobs/formal-timeout-1'): return route.fulfill(json=timeout_job)
  return route.fulfill(status=404,json={'detail':'mock route missing'})
 timeout_page.route('**/v1/**',timeout_route);timeout_page.goto(url+'?api='+mock_origin+'&project=timeout');timeout_page.locator('.job-select').first.click();timeout_page.wait_for_function("window.selectedJob && window.selectedJob.id");assert 'formal solver exceeded' in timeout_page.locator('#evidenceView').inner_text();assert timeout_page.locator('#signoffButton').is_disabled();assert not timeout_errors,timeout_errors;timeout_page.close()
 wave_page=browser.new_page(viewport={'width':1440,'height':1024});wave_errors=[];wave_page.on('pageerror',lambda e:wave_errors.append(str(e)))
 wave_job={'id':'waveform-run-1','project_id':'wave','kind':'project-simulation','status':'failed','artifact_id':'rtl-wave','created_at':'2026-09-09T00:00:00Z','events':[{'status':'queued','at':'2026-09-09T00:00:00Z'},{'status':'failed','at':'2026-09-09T00:00:02Z'}]}
 def wave_route(route):
  u=route.request.url
  if u.endswith('/v1/projects'): return route.fulfill(json=[{'id':'wave','name':'Wave project'}])
  if '/v1/jobs?' in u: return route.fulfill(json=[wave_job])
  if u.endswith('/evidence'): return route.fulfill(json={'job':wave_job,'artifacts':{'rtl':{'name':'counter.sv','sha256':'abc123','content':'module counter;\n  assign done = 1\'b1;\nendmodule'}},'files':{},'waveform':{'present':True,'signals':['clk','done'],'excerpt':'$var wire 1 ! done $end\n1!\n0!'}})
  if u.endswith('/v1/jobs/waveform-run-1'): return route.fulfill(json=wave_job)
  return route.fulfill(status=404,json={'detail':'mock route missing'})
 wave_page.route('**/v1/**',wave_route);wave_page.goto(url+'?api='+mock_origin+'&project=wave');wave_page.locator('.job-select').first.click();wave_page.wait_for_function("window.selectedJob && window.selectedJob.id");assert wave_page.locator('.wave-signal').count()==2, 'waveform signal controls missing: '+wave_page.locator('#evidenceView').inner_text();wave_page.get_by_role('button',name='Inspect waveform signal done').click();assert 'Signal done' in wave_page.locator('.wave-detail').inner_text() and wave_page.evaluate("new URLSearchParams(location.search).get('signal')")=='done';wave_page.get_by_role('button',name='Inspect counter.sv line 2').click();assert 'counter.sv · line 2' in wave_page.locator('#artifactInspector').inner_text() and wave_page.evaluate("new URLSearchParams(location.search).get('source')")=='rtl:2';wave_page.get_by_role('button',name='Inspect durable event 2 failed').click();assert 'event 2' in wave_page.locator('#artifactInspector').inner_text() and wave_page.evaluate("new URLSearchParams(location.search).get('event')")=='2';wave_page.reload();wave_page.wait_for_function("window.selectedJob && window.selectedJob.id");assert 'event 2' in wave_page.locator('#artifactInspector').inner_text();assert not wave_errors,wave_errors;wave_page.close()
 seq_page=browser.new_page(viewport={'width':1440,'height':1024});seq_errors=[];seq_page.on('pageerror',lambda e:seq_errors.append(str(e)))
 def seq_route(route):
  u=route.request.url
  if u.endswith('/v1/projects'): return route.fulfill(json=[{'id':'seq','name':'Sequence project'}])
  if '/v1/jobs?' in u: return route.fulfill(json=[])
  return route.fulfill(status=404,json={'detail':'mock route missing'})
 seq_page.route('**/v1/**',seq_route);seq_page.goto(url+'?api='+mock_origin+'&project=seq');seq_page.wait_for_function("document.querySelector('#projectSelect option')")
 seq_page.evaluate("""async()=>{const real=window.fetch;let call=0;window.fetch=(url,opts)=>{if(String(url).includes('/v1/jobs?')){const n=++call;return new Promise(resolve=>setTimeout(()=>resolve({ok:true,json:async()=>[{id:n===1?'old-response':'new-response',kind:'project-simulation',status:'passed',created_at:'2026-09-09T00:00:00Z'}]}),n===1?250:0));}return real(url,opts)};await Promise.all([loadJobs(),loadJobs()]);}""")
 assert seq_page.locator('.job-select').first.inner_text()=='new-respon'
 seq_page.evaluate("""async()=>{const real=window.fetch;const jobs={old:{id:'old-run',project_id:'seq',kind:'project-simulation',status:'failed',events:[]},new:{id:'new-run',project_id:'seq',kind:'project-simulation',status:'passed',events:[]}};window.fetch=(url,opts)=>{const text=String(url);for(const key of ['old','new'])if(text.endsWith('/v1/jobs/'+key)){return new Promise(resolve=>setTimeout(()=>resolve({ok:true,json:async()=>jobs[key]}),key==='old'?250:0));}if(text.endsWith('/evidence')){const key=text.includes('/old/')?'old':'new';return Promise.resolve({ok:true,json:async()=>({job:jobs[key],artifacts:{},files:{},waveform:{present:false}})});}return real(url,opts)};await Promise.all([inspectJob('old'),inspectJob('new')]);}""")
 assert seq_page.evaluate('window.selectedJob?.id')=='new-run', {'heading':seq_page.locator('#failureHeading').inner_text(),'selected':seq_page.evaluate('window.selectedJob'),'errors':seq_errors}
 seq_page.evaluate("""async()=>{const real=window.fetch;let call=0;window.fetch=(url,opts)=>{if(String(url).includes('/v1/jobs?')){const project=new URL(url).searchParams.get('project_id');const n=++call;return new Promise(resolve=>setTimeout(()=>resolve({ok:true,json:async()=>[{id:project+'-run',kind:'project-simulation',status:'passed',created_at:'2026-09-09T00:00:00Z'}]}),project==='old-project'?250:0));}return real(url,opts)};history.pushState({},'',location.pathname+'?api='+encodeURIComponent('http://mock-verification.local')+'&project=old-project');const old=loadJobs();history.pushState({},'',location.pathname+'?api='+encodeURIComponent('http://mock-verification.local')+'&project=new-project');const fresh=loadJobs();await Promise.all([old,fresh]);} """)
 assert seq_page.locator('.job-select').first.inner_text()=='new-projec', 'stale project response replaced current project'
 assert not seq_errors,seq_errors;seq_page.close()
 disconnect_page=browser.new_page(viewport={'width':1440,'height':1024});disconnect_errors=[];disconnect_page.on('pageerror',lambda e:disconnect_errors.append(str(e)))
 disconnect_job={'id':'known-run-1','project_id':'disconnect','kind':'project-simulation','status':'passed','created_at':'2026-09-09T00:00:00Z','events':[]}
 def disconnect_route(route):
  u=route.request.url
  if u.endswith('/v1/projects'): return route.fulfill(json=[{'id':'disconnect','name':'Disconnect project'}])
  if '/v1/jobs?' in u: return route.fulfill(json=[disconnect_job])
  return route.fulfill(status=404,json={'detail':'mock route missing'})
 disconnect_page.route('**/v1/**',disconnect_route);disconnect_page.goto(url+'?api='+mock_origin+'&project=disconnect');disconnect_page.locator('.job-select').first.wait_for();disconnect_page.evaluate("""async()=>{const real=window.fetch;window.fetch=(url,opts)=>String(url).includes('/v1/jobs?')?Promise.reject(new Error('connection reset')):real(url,opts);await loadJobs();}""");assert disconnect_page.locator('.job-select').first.inner_text()=='known-run-', disconnect_page.locator('.job-select').first.inner_text();assert 'Stale' in disconnect_page.locator('#pipelineUpdated').inner_text(), disconnect_page.locator('#pipelineUpdated').inner_text();disconnect_page.evaluate("""async()=>{window.fetch=(url,opts)=>String(url).includes('/v1/jobs?')?Promise.resolve({ok:false,status:401}):Promise.resolve({ok:true,json:async()=>[]});await loadJobs();}""");assert disconnect_page.locator('.job-select').first.inner_text()=='known-run-';assert 'Unauthorized' in disconnect_page.locator('#pipelineUpdated').inner_text();assert not disconnect_errors,disconnect_errors;disconnect_page.close()
 cov_page=browser.new_page(viewport={'width':1440,'height':1024});cov_errors=[];cov_page.on('pageerror',lambda e:cov_errors.append(str(e)))
 cov_job={'id':'coverage-run-1','project_id':'coverage','kind':'project-simulation','status':'passed','artifact_id':'rtl-cov','created_at':'2026-09-09T00:00:00Z','events':[]}
 def cov_route(route):
  u=route.request.url
  if u.endswith('/v1/projects'): return route.fulfill(json=[{'id':'coverage','name':'Coverage project'}])
  if '/v1/jobs?' in u: return route.fulfill(json=[cov_job])
  if '/v1/projects/coverage/audit' in u: return route.fulfill(json={'schema_version':'verification-audit-v1','project_id':'coverage','total':1,'entries':[{'job_id':'coverage-run-1','status':'passed','request_id':'audit-1'}],'truncated':False})
  if u.endswith('/v1/jobs/coverage-run-1'): return route.fulfill(json=cov_job)
  if u.endswith('/proof-of-value'): return route.fulfill(json={'coverage':{},'closure':{'open':0},'formal':{'status':'passed'},'artifact_integrity':{'valid':True}})
  if u.endswith('/signoff'): return route.fulfill(json={'valid':False,'status':'approved','reviewer':'unknown','report_sha256':'tampered'})
  if u.endswith('/evidence'): return route.fulfill(json={'job':cov_job,'artifacts':{},'files':{},'waveform':{'present':False}})
  return route.fulfill(status=404,json={'detail':'mock route missing'})
 cov_page.route('**/v1/**',cov_route);cov_page.goto(url+'?api='+mock_origin+'&project=coverage');cov_page.locator('.job-select').first.click();cov_page.wait_for_function("window.selectedJob && window.selectedJob.id");cov_page.get_by_role('button',name='Load latest PoV').click();cov_page.wait_for_function("document.querySelector('#reportState').textContent.includes('Invalid signoff receipt')");assert cov_page.locator('#coverageValue').inner_text()=='Not reported';assert cov_page.locator('#signoffButton').is_disabled();cov_page.evaluate("""()=>{window.baselineJob='baseline';window.retestJob='retest';const real=window.fetch;window.fetch=(url,opts)=>String(url).includes('/compare/')?Promise.resolve({ok:true,json:async()=>({metrics:{scope_comparable:false},claim_boundary:'incomparable scope'})}):real(url,opts)}""");cov_page.get_by_role('button',name='Compare retest').click();cov_page.wait_for_function("document.querySelector('#reportState').textContent.includes('Incomparable retest')");assert cov_page.locator('#signoffButton').is_disabled();assert not cov_errors,cov_errors
 with cov_page.expect_download() as audit_download:
  cov_page.get_by_role('button',name='Export audit').click()
 assert audit_download.value.suggested_filename=='verification-audit-coverage.json'
 assert '1 entries' in cov_page.locator('#auditState').inner_text()
 cov_page.close()
 readiness_page=browser.new_page(viewport={'width':1440,'height':1024});readiness_errors=[];readiness_page.on('pageerror',lambda e:readiness_errors.append(str(e)))
 def readiness_route(route):
  u=route.request.url
  if u.endswith('/v1/projects'): return route.fulfill(json=[{'id':'ready','name':'Readiness project'}])
  if u.endswith('/dashboard'): return route.fulfill(json={'project':{'id':'ready','name':'Readiness project'},'collateral_count':0,'jobs':{}})
  if u.endswith('/v1/capabilities'): return route.fulfill(json={'eda_adapters':[{'name':'customer-sim','kind':'simulation','executable':'customer-sim','available':True,'expected_artifacts':['simulation/result.json'],'timeout_seconds':120}]})
  if u.endswith('/v1/readiness'): return route.fulfill(json={'schema_version':'verification-production-readiness-v1','control_count':10,'verified_count':8,'open_count':2,'open_controls':['managed database','signed pilot'],'customer_production_ready':False,'claim_boundary':'Deployment evidence summary only.'})
  if u.endswith('/v1/pilot/scorecard'): return route.fulfill(json={'schema_version':'verification-pilot-scorecard-v1','pilot':{'sample_size':20},'finalized':True,'metrics':[{'name':'triage_latency','baseline_median':10,'workbench_median':5,'evidence_count':20}],'claim_boundary':'Measured fixture only.'})
  if '/v1/jobs?' in u: return route.fulfill(json=[])
  return route.fulfill(status=404,json={'detail':'mock route missing'})
 readiness_page.route('**/v1/**',readiness_route);readiness_page.goto(url+'?api='+mock_origin+'&project=ready');readiness_page.wait_for_function("document.querySelector('#readinessSummary') && document.querySelector('#readinessSummary').textContent.includes('8/10')");assert 'managed database' in readiness_page.locator('#readinessBody').inner_text();assert 'customer-sim' in readiness_page.locator('#backendList').inner_text();assert not readiness_errors,readiness_errors;readiness_page.close()
 out=root/'.artifacts'/'workbench-browser';out.mkdir(parents=True,exist_ok=True)
 page.screenshot(path=str(out/'live-unavailable.png'))
 print('Passed: global search/no-match state, selection isolation, in-flight run selection ordering, evidence tab guard, section navigation, sample report guard, mobile navigation, failed-live no sample fallback, blocked formal timeout, missing-coverage boundary, invalid signoff receipt, waveform signal inspection, source-line inspection, durable-event inspection, delayed-refresh ordering, disconnect and auth-expiry recovery; no page errors')
 browser.close()
server.shutdown()
