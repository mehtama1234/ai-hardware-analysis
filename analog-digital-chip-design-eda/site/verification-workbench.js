function credentialScope(){return new URLSearchParams(location.search).get('api')||location.origin;}
function getApiKey(){return sessionStorage.getItem('workbench.apiKey:'+credentialScope())||'';}
function getProjectKey(){return sessionStorage.getItem('workbench.projectKey:'+credentialScope())||'';}

const demo={name:'Orion_NPU',pass_rate:72,blocking_issues:3,evidence_coverage:86,failures:[{id:'npu_conv_fp16_saturation_v2',priority:'P0',meta:'1 failing assertion · 0/3 seeds passing · 2h ago'},{id:'npu_dma_stress_random',priority:'P1',meta:'4 failing assertions · 1/5 seeds passing · 3h ago'},{id:'npu_pooling_accuracy',priority:'P1',meta:'2 failing assertions · 0/2 seeds passing · 5h ago'}]};const $=s=>document.querySelector(s);const toast=m=>{const t=$('#toast');if(!t)return;t.setAttribute('role','status');t.setAttribute('aria-live','polite');t.setAttribute('aria-atomic','true');t.textContent=String(m);t.classList.add('show');setTimeout(()=>t.classList.remove('show'),2400)};
// View identity is invalidated before any asynchronously loaded evidence changes.
const mode = new URLSearchParams(location.search).has('api') ? 'live' : 'sample';
let selectionVersion = 0;
let selectedJob = null;
const escapeHTML = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
async function fetchWithTimeout(url, options = {}, timeoutMs = 8000) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try { return await fetch(url, {...options, signal: controller.signal}); }
  finally { clearTimeout(timer); }
}
function clearReviewState(message) {
  selectionVersion++;
  selectedJob = null;
  for (const key of ['workbenchReport','workbenchReportJob','repairProposal','baselineJob','retestJob','selectedArtifact']) delete window[key];
  for (const id of ['signoffButton','bundleButton','previewBundle']) { const node=$('#'+id); if(node) node.disabled = true; }
  const reportState=$('#reportState'); if(reportState) reportState.textContent = 'No report selected';
  const reportSummary=$('#reportSummary'); if(reportSummary) reportSummary.textContent = message;
  const artifactInspector=$('#artifactInspector'); if(artifactInspector) artifactInspector.hidden = true;
  const comparisonDetail=$('#comparisonDetail'); if(comparisonDetail) comparisonDetail.hidden = true;
  document.querySelector('.approval')?.classList.remove('show');
  const repairButton=$('#repairButton'); if(repairButton) { repairButton.textContent = 'Create repair proposal'; repairButton.onclick = createRepairProposal; }
}
function showMissingEvidence(message) {
  $('#evidenceView').hidden = true;
  $('#alternateView').hidden = false;
  $('#alternateView').textContent = message;
}

// Install the safe run-list renderer before the initial hydration call below.
// The setup module also installs this renderer, but the base page must never
// briefly render API-controlled job fields through an HTML string.
function renderJobsSafe(jobs) {
  const wrap = $('#jobsWrap');
  if (!wrap) return;
  wrap.replaceChildren();
  if (!Array.isArray(jobs) || !jobs.length) {
    const empty = document.createElement('div'); empty.className = 'empty'; empty.textContent = 'No jobs for this project yet.'; wrap.append(empty); return;
  }
  const table = document.createElement('table'); table.className = 'jobs';
  const head = document.createElement('thead'); const header = document.createElement('tr');
  for (const label of ['Job', 'Kind', 'Status', 'Created']) { const cell = document.createElement('th'); cell.textContent = label; header.append(cell); }
  head.append(header); table.append(head);
  const body = document.createElement('tbody');
  for (const job of jobs.slice(0, 8)) {
    const row = document.createElement('tr'); const idCell = document.createElement('td');
    const button = document.createElement('button'); button.className = 'secondary job-select'; button.dataset.job = String(job.id || '');
    button.textContent = String(job.id || 'unknown').slice(0, 10); button.setAttribute('aria-label', 'Inspect run ' + String(job.id || 'unknown').slice(0, 10));
    button.onclick = () => inspectJob(job.id); idCell.append(button);
    const kind = document.createElement('td'); kind.textContent = String(job.kind || 'Not reported');
    const statusCell = document.createElement('td'); const status = document.createElement('span'); status.className = 'job-status ' + String(job.status || 'unknown').replace(/[^a-z0-9_-]/gi, ''); status.textContent = String(job.status || 'unknown'); statusCell.append(status);
    const created = document.createElement('td'); created.textContent = job.created_at ? new Date(job.created_at).toLocaleString() : 'Not reported';
    row.append(idCell, kind, statusCell, created); body.append(row);
  }
  table.append(body); wrap.append(table);
}
renderJobs = renderJobsSafe;

function ensureBackendPanel() {
  if ($('#backendPanel')) return;
  const anchor = document.querySelector('.workspace');
  if (!anchor) return;
  const panel = document.createElement('section');
  panel.id = 'backendPanel';
  panel.className = 'panel';
  panel.style.marginBottom = '18px';
  const head = document.createElement('div'); head.className = 'panel-head';
  const title = document.createElement('div'); const heading = document.createElement('h2'); heading.textContent = 'Execution backends';
  const help = document.createElement('small'); help.textContent = 'Capability evidence · inspect before launching'; title.append(heading, help);
  const summary = document.createElement('span'); summary.id = 'backendSummary'; summary.textContent = 'Loading…'; head.append(title, summary);
  const list = document.createElement('div'); list.id = 'backendList'; list.style.cssText = 'display:grid;gap:8px';
  const loading = document.createElement('div'); loading.className = 'empty'; loading.textContent = 'Loading registered tools…'; list.append(loading);
  panel.append(head, list);
  anchor.before(panel);
}

function renderBackends(payload) {
  ensureBackendPanel();
  const list = $('#backendList');
  const summary = $('#backendSummary');
  if (!list || !summary) return;
  list.replaceChildren();
  const adapters = Array.isArray(payload?.eda_adapters) ? payload.eda_adapters : [];
  if (!adapters.length) {
    summary.textContent = payload?.error ? 'Unavailable' : 'No registered adapters';
    const empty = document.createElement('p');
    empty.className = 'empty';
    empty.textContent = payload?.error || 'Register a simulator, formal, regression, or artifact adapter before starting customer work.';
    list.append(empty);
    return;
  }
  const available = adapters.filter(item => item.available === true).length;
  summary.textContent = `${available}/${adapters.length} available`;
  const chooser = document.createElement('label');
  chooser.style.cssText = 'display:grid;gap:5px;padding:10px 14px;border:1px solid var(--line);border-radius:8px;background:#fafbff;font-size:12px;font-weight:650';
  chooser.textContent = 'Adapter for the next customer run';
  const select = document.createElement('select');
  select.id = 'adapterSelect';
  select.setAttribute('aria-label', 'Select customer execution adapter');
  const placeholder = document.createElement('option');
  placeholder.value = '';
  placeholder.textContent = available ? 'Choose an available adapter' : 'No available adapter';
  select.append(placeholder);
  for (const adapter of adapters.filter(item => item.available === true)) {
    const option = document.createElement('option');
    option.value = adapter.name || '';
    option.textContent = `${adapter.name || 'Unnamed adapter'} · ${adapter.kind || 'tool'}`;
    select.append(option);
  }
  select.value = sessionStorage.getItem('workbench.adapter:'+credentialScope()) || '';
  select.onchange = () => sessionStorage.setItem('workbench.adapter:'+credentialScope(), select.value);
  chooser.append(select);
  const argsLabel = document.createElement('span');
  argsLabel.textContent = 'Non-secret arguments (JSON array; credentials belong in the deployment secret manager)';
  argsLabel.style.cssText = 'margin-top:4px;color:var(--muted);font-size:11px;font-weight:500';
  const argsInput = document.createElement('input');
  argsInput.id = 'adapterArgsInput';
  argsInput.type = 'text';
  argsInput.placeholder = '["--batch"]';
  argsInput.setAttribute('aria-label', 'Non-secret customer adapter arguments as JSON');
  argsInput.style.cssText = 'border:1px solid var(--line);border-radius:6px;padding:8px;background:#fff;font:12px ui-monospace,SFMono-Regular,Menlo,monospace;color:var(--ink)';
  chooser.append(argsLabel, argsInput);
  list.append(chooser);
  for (const adapter of adapters) {
    const row = document.createElement('div');
    row.style.cssText = 'display:grid;grid-template-columns:minmax(120px,1fr) auto;gap:4px 14px;padding:10px 14px;border:1px solid var(--line);border-radius:8px;background:#fff';
    const name = document.createElement('b');
    name.textContent = `${adapter.name || 'Unnamed adapter'} · ${adapter.kind || 'tool'}`;
    const status = document.createElement('span');
    status.textContent = adapter.available === true ? 'Available' : 'Blocked';
    status.style.color = adapter.available === true ? 'var(--good)' : 'var(--warn)';
    status.style.fontWeight = '700';
    const detail = document.createElement('small');
    const artifacts = Array.isArray(adapter.expected_artifacts) && adapter.expected_artifacts.length ? adapter.expected_artifacts.join(', ') : 'No expected artifacts declared';
    detail.textContent = `${adapter.executable || 'executable unavailable'} · timeout ${adapter.timeout_seconds || 'not set'}s · outputs: ${artifacts}`;
    detail.style.color = 'var(--muted)';
    row.append(name, status, detail);
    list.append(row);
  }
}

async function loadCapabilities() {
  ensureBackendPanel();
  const q = new URLSearchParams(location.search);
  if (mode === 'sample') {
    renderBackends({eda_adapters: [
      {name: 'iverilog-reference', kind: 'simulation', executable: 'iverilog', available: true, expected_artifacts: ['simulation/result.json', 'simulation/waveform.vcd'], timeout_seconds: 1800},
      {name: 'verilator-reference', kind: 'lint', executable: 'verilator', available: true, expected_artifacts: [], timeout_seconds: 600},
      {name: 'customer-formal', kind: 'formal', executable: 'customer-formal', available: false, expected_artifacts: ['formal/result.json'], timeout_seconds: 3600}
    ]});
    return;
  }
  const api = q.get('api');
  if (!api) { renderBackends({error: 'Connect to the verification service to inspect registered tools.'}); return; }
  try {
    const response = await fetchWithTimeout(api + '/v1/capabilities', {headers: {'X-Project-Key': getProjectKey(), 'X-API-Key': getApiKey()}});
    if (!response.ok) throw new Error(`Service returned ${response.status}`);
    renderBackends(await response.json());
  } catch (error) {
    renderBackends({error: `Capability data unavailable · ${error.message}`});
  }
}

function ensureReadinessPanel() {
  if ($('#commercialReadiness')) return;
  const anchor = $('#backendPanel') || document.querySelector('.workspace');
  if (!anchor) return;
  const panel = document.createElement('section');
  panel.id = 'commercialReadiness';
  panel.className = 'panel';
  panel.style.marginBottom = '18px';
  const head = document.createElement('div'); head.className = 'panel-head';
  const title = document.createElement('div'); const heading = document.createElement('h2'); heading.textContent = 'Commercial readiness';
  const help = document.createElement('small'); help.textContent = 'Release controls · infrastructure and pilot boundary'; title.append(heading, help);
  const summary = document.createElement('span'); summary.id = 'readinessSummary'; summary.textContent = 'Loading…'; head.append(title, summary);
  const body = document.createElement('div'); body.id = 'readinessBody'; body.style.cssText = 'padding:14px 18px';
  const loading = document.createElement('div'); loading.className = 'empty'; loading.textContent = 'Loading readiness evidence…'; body.append(loading);
  panel.append(head, body);
  anchor.after(panel);
}

function renderReleaseReadiness(data) {
  ensureReadinessPanel();
  const summary = $('#readinessSummary');
  const body = $('#readinessBody');
  if (!summary || !body) return;
  body.replaceChildren();
  if (data?.error) {
    summary.textContent = 'Unavailable';
    const error = document.createElement('p'); error.className = 'evidence-missing'; error.textContent = data.error; body.append(error); return;
  }
  const ready = data.customer_production_ready === true;
  summary.textContent = ready ? 'Production ready' : `${data.verified_count || 0}/${data.control_count || 0} verified · ${data.open_count || 0} open`;
  summary.style.color = ready ? 'var(--good)' : 'var(--warn)';
  summary.style.fontWeight = '700';
  const claim = document.createElement('p'); claim.textContent = data.claim_boundary || 'Readiness is evidence-bound; open controls require deployment proof.'; claim.style.color = 'var(--muted)'; body.append(claim);
  const open = Array.isArray(data.open_controls) ? data.open_controls : [];
  if (open.length) {
    const heading = document.createElement('b'); heading.textContent = 'Open controls'; body.append(heading);
    const list = document.createElement('ul'); list.style.cssText = 'margin:8px 0 0;padding-left:20px;color:var(--muted);font-size:12px';
    for (const item of open) { const row = document.createElement('li'); row.textContent = item; list.append(row); }
    body.append(list);
  }
}

async function loadReleaseReadiness() {
  ensureReadinessPanel();
  const q = new URLSearchParams(location.search);
  if (mode === 'sample') { renderReleaseReadiness({customer_production_ready: false, control_count: 0, verified_count: 0, open_count: 0, claim_boundary: 'Sample workspace only; no production-readiness claim is made.'}); return; }
  const api = q.get('api');
  if (!api) { renderReleaseReadiness({error: 'Connect to the verification service to inspect release readiness.'}); return; }
  try {
    const response = await fetchWithTimeout(api + '/v1/readiness', {headers: {'X-Project-Key': getProjectKey(), 'X-API-Key': getApiKey()}});
    if (!response.ok) throw new Error(`Service returned ${response.status}`);
    renderReleaseReadiness(await response.json());
  } catch (error) { renderReleaseReadiness({error: `Readiness data unavailable · ${error.message}`}); }
}

function ensureScorecardPanel() {
  if ($('#pilotScorecard')) return;
  const anchor = $('#commercialReadiness') || $('#backendPanel') || document.querySelector('.workspace');
  if (!anchor) return;
  const panel = document.createElement('section'); panel.id = 'pilotScorecard'; panel.className = 'panel'; panel.style.marginBottom = '18px';
  const head = document.createElement('div'); head.className = 'panel-head';
  const title = document.createElement('div'); const heading = document.createElement('h2'); heading.textContent = 'Pilot measurement';
  const help = document.createElement('small'); help.textContent = 'Proof-of-value evidence · bounded summaries'; title.append(heading, help);
  const summary = document.createElement('span'); summary.id = 'scorecardSummary'; summary.textContent = 'Loading…'; head.append(title, summary);
  const body = document.createElement('div'); body.id = 'scorecardBody'; body.style.cssText = 'padding:14px 18px';
  const loading = document.createElement('div'); loading.className = 'empty'; loading.textContent = 'Loading scorecard evidence…'; body.append(loading);
  panel.append(head, body);
  anchor.after(panel);
}

function renderScorecard(data) {
  ensureScorecardPanel(); const summary = $('#scorecardSummary'); const body = $('#scorecardBody'); if (!summary || !body) return;
  body.replaceChildren();
  if (data?.error) { summary.textContent = 'Unavailable'; const error = document.createElement('p'); error.className = 'evidence-missing'; error.textContent = data.error; body.append(error); return; }
  const pilot = data.pilot || {}; summary.textContent = data.finalized === true ? `Finalized · n=${pilot.sample_size || 0}` : `Draft · n=${pilot.sample_size || 0}`; summary.style.color = data.finalized === true ? 'var(--good)' : 'var(--warn)'; summary.style.fontWeight = '700';
  const claim = document.createElement('p'); claim.textContent = data.claim_boundary || 'Scorecard values remain bounded to supplied observations.'; claim.style.color = 'var(--muted)'; body.append(claim);
  const table = document.createElement('table'); table.className = 'jobs'; const head = document.createElement('tr'); for (const label of ['Metric', 'Baseline', 'Workbench', 'Evidence']) { const cell = document.createElement('th'); cell.textContent = label; head.append(cell); } const thead = document.createElement('thead'); thead.append(head); table.append(thead);
  const rows = document.createElement('tbody'); for (const metric of (Array.isArray(data.metrics) ? data.metrics : [])) { const row = document.createElement('tr'); for (const value of [metric.name || 'Unnamed', metric.baseline_median ?? 'Not collected', metric.workbench_median ?? 'Not collected', String(metric.evidence_count ?? 0)]) { const cell = document.createElement('td'); cell.textContent = String(value); row.append(cell); } rows.append(row); } table.append(rows); body.append(table);
}

async function loadScorecard() {
  ensureScorecardPanel(); const q = new URLSearchParams(location.search);
  if (mode === 'sample') { renderScorecard({finalized: false, pilot: {sample_size: 5}, metrics: [{name: 'triage_latency', baseline_median: null, workbench_median: null, evidence_count: 0}], claim_boundary: 'Draft sample only; baseline and customer ROI have not been collected.'}); return; }
  const api = q.get('api'); if (!api) { renderScorecard({error: 'Connect to the verification service to inspect pilot measurements.'}); return; }
  try { const response = await fetchWithTimeout(api + '/v1/pilot/scorecard', {headers: {'X-Project-Key': getProjectKey(), 'X-API-Key': getApiKey()}}); if (!response.ok) throw new Error(`Service returned ${response.status}`); renderScorecard(await response.json()); } catch (error) { renderScorecard({error: `Scorecard unavailable · ${error.message}`}); }
}

function ensureAgenticClosurePanel() {
  if ($('#agenticClosure')) return;
  const anchor = $('#pilotScorecard') || $('#commercialReadiness') || $('#backendPanel') || document.querySelector('.workspace');
  if (!anchor) return;
  const panel = document.createElement('section'); panel.id = 'agenticClosure'; panel.className = 'panel'; panel.style.marginBottom = '18px';
  const head = document.createElement('div'); head.className = 'panel-head';
  const title = document.createElement('div'); const heading = document.createElement('h2'); heading.textContent = 'Agentic hardware closure';
  const help = document.createElement('small'); help.textContent = 'Hash-bound claims · human approval required'; title.append(heading, help);
  const summary = document.createElement('span'); summary.id = 'agenticClosureSummary'; summary.textContent = 'Loading…'; head.append(title, summary);
  const body = document.createElement('div'); body.id = 'agenticClosureBody'; body.style.cssText = 'padding:14px 18px';
  panel.append(head, body); anchor.after(panel);
}

function renderAgenticClosure(data) {
  ensureAgenticClosurePanel(); const summary = $('#agenticClosureSummary'); const body = $('#agenticClosureBody'); if (!summary || !body) return;
  body.replaceChildren();
  if (data?.error) { summary.textContent = 'Unavailable'; summary.style.color = 'var(--warn)'; const error = document.createElement('p'); error.className = 'evidence-missing'; error.textContent = data.error; body.append(error); return; }
  const decision = String(data.release_decision || 'not reported'); summary.textContent = decision.replaceAll('_', ' '); summary.style.color = decision === 'review_required' ? 'var(--warn)' : 'var(--brand)'; summary.style.fontWeight = '700';
  const grid = document.createElement('div'); grid.style.cssText = 'display:grid;grid-template-columns:repeat(4,1fr);gap:9px';
  const claims = data.claims || {};
  for (const [name, claim] of Object.entries(claims)) { const card = document.createElement('div'); card.style.cssText = 'border:1px solid var(--line);border-radius:7px;padding:9px'; const label = document.createElement('b'); label.textContent = name.replaceAll('_', ' '); const status = document.createElement('div'); status.textContent = String(claim?.status || 'not reported'); status.style.cssText = 'margin-top:5px;color:var(--muted);font-size:11px'; card.append(label, status); grid.append(card); }
  body.append(grid); const boundary = document.createElement('p'); boundary.textContent = data.claim_boundary || 'Analog authorization remains disabled.'; boundary.style.color = 'var(--muted)'; body.append(boundary);
  if (mode === 'live' && data.manifest_sha256) {
    const actions = document.createElement('div'); actions.className = 'actions';
    for (const [approved, label] of [[true, 'Approve closure'], [false, 'Reject closure']]) {
      const button = document.createElement('button'); button.type = 'button'; button.className = approved ? 'primary' : 'secondary'; button.textContent = label;
      button.onclick = async () => {
        const reviewStartedAt = new Date().toISOString();
        const reviewer = prompt('Reviewer identity'); if (!reviewer?.trim()) return;
        const notes = prompt('Review note'); if (notes === null || !notes.trim()) return;
        const api = new URLSearchParams(location.search).get('api');
        try {
          const response = await fetchWithTimeout(api + '/v1/agentic-closure/signoff', {method: 'POST', headers: {'Content-Type': 'application/json', 'X-Project-Key': getProjectKey(), 'X-API-Key': getApiKey()}, body: JSON.stringify({reviewer: reviewer.trim(), notes: notes.trim(), approved, manifest_sha256: data.manifest_sha256, review_started_at: reviewStartedAt})});
          if (!response.ok) throw new Error(`Service returned ${response.status}`);
          toast(label + ' recorded'); await loadAgenticClosure();
        } catch (error) { toast('Signoff failed · ' + error.message); }
      };
      actions.append(button);
    }
    body.append(actions);
  }
}

async function loadAgenticClosure() {
  ensureAgenticClosurePanel(); const q = new URLSearchParams(location.search);
  if (mode === 'sample') { renderAgenticClosure({release_decision: 'sample_only', claims: {digital_verification: {status: 'illustrative'}, physical_layout: {status: 'illustrative'}, analog_hardware: {status: 'unauthorized'}, measured_hardware: {status: 'unsupported'}}, claim_boundary: 'Sample workspace only; no agentic closure or analog authorization claim is made.'}); return; }
  const api = q.get('api'); if (!api) { renderAgenticClosure({error: 'Connect to the verification service to inspect agentic closure.'}); return; }
  try { const response = await fetchWithTimeout(api + '/v1/agentic-closure', {headers: {'X-Project-Key': getProjectKey(), 'X-API-Key': getApiKey()}}); if (!response.ok) throw new Error(`Service returned ${response.status}`); renderAgenticClosure(await response.json()); } catch (error) { renderAgenticClosure({error: `Agentic closure unavailable · ${error.message}`}); }
}
document.documentElement.dataset.mode = mode;
$('#workspaceMode').textContent = mode === 'sample'
  ? 'Sample workspace · illustrative data · no verification has been executed'
  : 'Connected workspace · loading service data';

async function createProject(){const q=new URLSearchParams(location.search),api=q.get('api'),key=getApiKey();if(!api){toast('Demo mode cannot create projects');return}const name=prompt('Project name');if(!name?.trim())return;const id=name.trim().toLowerCase().replace(/[^a-z0-9_-]+/g,'_');try{const r=await fetch(api+'/v1/projects',{method:'POST',headers:{'Content-Type':'application/json','X-Project-Key':getProjectKey(),'X-API-Key':key},body:JSON.stringify({id,name:name.trim()})});if(!r.ok)throw new Error(await r.text());await loadProjects();$('#projectSelect').value=id;$('#projectSelect').dispatchEvent(new Event('change'));toast('Project created: '+name.trim())}catch(e){toast('Project creation failed: '+e.message)}}async function loadProjects(){
 const q=new URLSearchParams(location.search),api=q.get('api');
 let projects=[{id:'Orion_NPU',name:'Orion_NPU · sample'}];
 if(mode==='live') {
   projects=[];
   try {
     const r=await fetch(api+'/v1/projects',{headers:{'X-Project-Key':getProjectKey(),'X-API-Key':getApiKey(),'X-Request-ID':'workbench-'+crypto.randomUUID()}});
     if(!r.ok)throw new Error('Service returned '+r.status);
     projects=await r.json();
   } catch(e) { $('#workspaceMode').textContent='Connection failed · '+e.message+' · reconnect to load projects'; }
 }
 const select=$('#projectSelect');
 select.replaceChildren(...projects.map(p=>new Option(p.name,p.id)));
 if(q.get('project'))select.value=q.get('project');
 select.onchange=()=>{
   clearReviewState('Project changed. Select a run to inspect its report.');
   const next=new URL(location.href);
   for(const key of ['job','artifact','tb','tbs','before','after','baseline','retest'])next.searchParams.delete(key);
   next.searchParams.set('project',select.value);
   location.assign(next.href);
 };
}

$('#newProject').onclick=createProject;loadProjects();function renderFailures(data){
 const list=$('#failureList');list.replaceChildren();
 data.failures.forEach((f,i)=>{const b=document.createElement('button');b.className='failure'+(i===0?' selected':'');b.dataset.failure=String(f.id);const title=document.createElement('div');title.className='failure-title';const id=document.createElement('span');id.textContent=String(f.id);const badge=document.createElement('span');badge.className='badge '+(f.priority==='P0'?'p0':'p1');badge.textContent=String(f.priority);title.append(id,badge);const meta=document.createElement('div');meta.className='failure-meta';meta.textContent=String(f.meta||'');b.append(title,meta);list.append(b);b.onclick=()=>{
   clearReviewState('Selection changed. Load evidence for the selected run.');
   document.querySelectorAll('.failure').forEach(x=>x.classList.toggle('selected',x===b));
   $('#failureHeading').textContent=data.failures[i].id;
   $('#failureSubhead').textContent='Sample failure · '+data.failures[i].priority;
   $('#failureHeading').parentElement.parentElement.querySelector('.badge')?.replaceChildren(document.createTextNode(data.failures[i].priority));
   $('#evidenceView').hidden=i!==0;
   $('#alternateView').hidden=i===0;
   if(i!==0)showMissingEvidence('No evidence fixture is attached to this sample failure. The previous failure’s evidence has been cleared.');
 };});
 $('#failureCount').textContent=data.failures.length+' listed';
}
async function hydrate(){
 loadCapabilities();
 loadReleaseReadiness();
 loadScorecard();
 loadAgenticClosure();
 if(mode==='sample'){renderFailures(demo);return;}
 clearReviewState('Select a terminal run to load its evidence.');
 showMissingEvidence('Select a run. No evidence has been loaded.');
 $('#failureHeading').textContent='No run selected';
 $('#failureSubhead').textContent='Evidence will be bound to the selected run';
 $('#failureList').replaceChildren(); $('#failureCount').textContent='Not loaded';
 for(const id of ['passRate','blocking','evidenceCoverage','coverageValue','closureOpen','formalValue','integrityValue'])$('#'+id).textContent='Not reported';
 const q=new URLSearchParams(location.search),api=q.get('api'),project=q.get('project');
 if(!project){$('#workspaceMode').textContent='Connected workspace · select or create a project';return;}
 try {
   const r=await fetch(api+'/v1/projects/'+encodeURIComponent(project)+'/dashboard',{headers:{'X-Project-Key':getProjectKey(),'X-API-Key':getApiKey(),'X-Request-ID':'workbench-'+crypto.randomUUID()}});
   if(!r.ok)throw new Error('Service returned '+r.status);
   const d=await r.json();
   $('#crumbProject').textContent=d.project.name;
   $('#workspaceMode').textContent='Connected workspace · '+d.project.name+' · no sample results';
   $('#connectionState').textContent='Project data loaded';
 }catch(e){$('#crumbProject').textContent=project||'Unavailable';$('#workspaceMode').textContent='Project unavailable · '+e.message+' · no sample fallback';$('#connectionState').textContent='Connection requires attention';}
}

function renderCollateral(items){
 window.workbenchCollateral=items;
 const list=$('#collateralList');list.replaceChildren();
 if(!items.length){list.textContent='No collateral uploaded for this project yet.';if(mode==='live'){const runButton=$('#runButton');if(runButton)runButton.disabled=true;const status=document.querySelector('.status-line');if(status)status.lastChild.textContent=' Setup required · upload RTL';}return;}
 if(mode==='live'){const hasRtl=items.some(item=>item.kind==='rtl');const runButton=$('#runButton');if(runButton)runButton.disabled=!hasRtl;const status=document.querySelector('.status-line');if(status)status.lastChild.textContent=hasRtl?' Ready · select a verification run':' Setup required · upload RTL';}
 for(const a of items){
  const row=document.createElement('button');row.className='collateral-row';
  for(const value of [a.name,a.kind,a.ingested===true?'Sample: ingested':a.ingested===false?'Sample: needs ingest':'Ingestion status not loaded',a.sha256||a.id||'Hash unavailable']){
   const cell=document.createElement('span');cell.textContent=value;row.append(cell);
  }
  row.onclick=()=>inspectArtifact(a);list.append(row);
 }
}
function inspectArtifact(a){
 window.selectedArtifact=a;
 const box=$('#artifactInspector');box.hidden=false;box.replaceChildren();
 const title=document.createElement('h3');title.textContent=a.name;box.append(title);
 for(const value of ['Kind: '+a.kind,'Version: '+(a.version||'Not reported'),'Content hash: '+(a.sha256||'Not reported')]){
  const line=document.createElement('p');line.textContent=value;box.append(line);
 }
 const actions=document.createElement('div');actions.className='actions';
 for(const [action,label] of [['ingest','Ingest artifact'],['plan','Create plan'],['generate','Generate review artifacts']]){
  const button=document.createElement('button');button.className='secondary';button.textContent=label;
  button.onclick=()=>runArtifactAction(action);actions.append(button);
 }
 box.append(actions);box.scrollIntoView({block:'nearest'});
}
async function runArtifactAction(action){
 const artifact=window.selectedArtifact,project=new URLSearchParams(location.search).get('project');
 if(!artifact||!project){toast('Select a live project artifact first');return;}
 try{const response=await fetch(new URLSearchParams(location.search).get('api')+'/v1/projects/'+encodeURIComponent(project)+'/collateral/'+encodeURIComponent(artifact.id)+'/'+action,{method:'POST',headers:{'X-Project-Key':getProjectKey(),'X-API-Key':getApiKey()}});if(!response.ok)throw new Error('service returned '+response.status);const result=await response.json();await loadCollateral();const refreshed=(window.workbenchCollateral||[]).find(item=>item.id===artifact.id);if(refreshed)inspectArtifact(refreshed);const output=document.createElement('pre');output.textContent=JSON.stringify(result,null,2);$('#artifactInspector').append(output);toast(action+' completed; result retained for review');}catch(e){toast(action+' failed: '+e.message);}
}
async function uploadCollateral(){const q=new URLSearchParams(location.search),api=q.get('api'),project=q.get('project'),key=getApiKey();if(!api||!project){toast('Demo mode cannot upload collateral');return}const name=prompt('Artifact filename');if(!name?.trim())return;const kind=prompt('Artifact kind (rtl, testbench, specification)','rtl')||'rtl';const content=prompt('Paste artifact content');if(content===null)return;try{const r=await fetch(api+'/v1/projects/'+encodeURIComponent(project)+'/collateral',{method:'POST',headers:{'Content-Type':'application/json','X-Project-Key':getProjectKey(),'X-API-Key':key},body:JSON.stringify({name:name.trim(),kind,version:'1',content})});if(!r.ok)throw new Error(await r.text());await loadCollateral();toast('Artifact uploaded and hash recorded')}catch(e){toast('Upload failed: '+e.message)}}async function loadCollateral(){const q=new URLSearchParams(location.search),api=q.get('api'),project=q.get('project'),key=getApiKey();$('#collateralList').innerHTML='<div class="empty">Loading project collateral…</div>';if(mode==='live'&&!project){renderCollateral([]);return;}if(mode==='sample'){renderCollateral([{name:'npu_mac.sv',kind:'rtl',ingested:true,sha256:'sha256:3f1d8f0a91c0'},{name:'npu_conv_fp16_saturation_v2.sv',kind:'testbench',ingested:true,sha256:'sha256:9a33e18d4f20'},{name:'verification-plan.md',kind:'specification',ingested:false,sha256:'sha256:42ce7d1a0b88'}]);return}try{const r=await fetch(api+'/v1/projects/'+encodeURIComponent(project)+'/collateral',{headers:{'X-Project-Key':getProjectKey(),'X-API-Key':key}});if(!r.ok)throw new Error('collateral unavailable');renderCollateral(await r.json())}catch(e){$('#connectionState').textContent=e.message.includes('401')?'Unauthorized · reconnect required':'Stale · retrying';renderCollateral([]);toast('Could not load collateral: '+e.message)}}function renderJobs(jobs){if(!jobs.length){$('#jobsWrap').innerHTML='<div class="empty">No jobs for this project yet.</div>';return}$('#jobsWrap').innerHTML='<table class="jobs"><thead><tr><th>Job</th><th>Kind</th><th>Status</th><th>Created</th></tr></thead><tbody>'+jobs.slice(0,8).map(j=>'<tr><td><button class="secondary job-select" data-job="'+j.id+'">'+j.id.slice(0,10)+'</button></td><td>'+j.kind+'</td><td><span class="job-status '+j.status+'">'+j.status+'</span></td><td>'+new Date(j.created_at).toLocaleString()+'</td></tr>').join('')+'</tbody></table>';document.querySelectorAll('.job-select').forEach(b=>b.onclick=()=>inspectJob(b.dataset.job))}async function inspectJob(jobId){
 clearReviewState('Run changed. Load a report for this run.');
 const version=selectionVersion;
 showMissingEvidence('Loading selected run…');
 $('#failureHeading').textContent=jobId;$('#failureSubhead').textContent='Loading run identity';
 if(mode==='sample'){
  $('#failureSubhead').textContent='Sample run · no execution artifacts attached';
  showMissingEvidence('This sample row has no durable event payload. No live result is implied.');return;
 }
 const q=new URLSearchParams(location.search);
 const setEvidenceCursor=(key,value)=>{const next=new URL(location.href);if(value===null||value===undefined)next.searchParams.delete(key);else next.searchParams.set(key,String(value));history.replaceState({},'',next.pathname+next.search+next.hash);};
 try{
  const r=await fetch(q.get('api')+'/v1/jobs/'+encodeURIComponent(jobId),{headers:{'X-Project-Key':getProjectKey(),'X-API-Key':getApiKey()}});
  if(!r.ok)throw new Error('Service returned '+r.status);
  const j=await r.json();
  if(version!==selectionVersion)return;
  if(j.project_id!==q.get('project'))throw new Error('Run belongs to another project');
  selectedJob=j;window.selectedJob=j;
  $('#failureSubhead').textContent=j.kind+' · '+j.status;
  const evidenceResponse=await fetch(q.get('api')+'/v1/jobs/'+encodeURIComponent(jobId)+'/evidence',{headers:{'X-Project-Key':getProjectKey(),'X-API-Key':getApiKey()}});
  if(!evidenceResponse.ok)throw new Error('Evidence service returned '+evidenceResponse.status);
  const evidence=await evidenceResponse.json();
  if(version!==selectionVersion)return;
  const view=$('#evidenceView');view.hidden=false;view.replaceChildren();
  const intro=document.createElement('div');intro.className='run-evidence-summary';
  const heading=document.createElement('h3');heading.textContent=j.kind+' · '+j.status;intro.append(heading);
  const identity=document.createElement('p');identity.textContent='Run '+j.id+' · RTL '+(j.artifact_id||'not recorded')+' · checker '+(j.testbench_artifact_id||'not recorded');intro.append(identity);
  const outcome=document.createElement('p');outcome.className=j.error?'evidence-missing':'evidence-good';outcome.textContent=j.error?'Execution could not establish verification evidence: '+j.error:(j.status==='passed'?'Design check completed successfully. Review scope and artifacts below.':j.status==='failed'?'Design check produced a failure. Inspect the captured evidence below.':'Execution status: '+j.status);intro.append(outcome);view.append(intro);
  const resultFile=evidence.files['project-simulation-result.json']||evidence.files['project-regression-result.json'];
  if(resultFile){const result=document.createElement('pre');result.textContent=resultFile.text;view.append(result);}
  for(const [role,artifact] of Object.entries(evidence.artifacts||{})){
   const source=document.createElement('details');source.open=role==='rtl';const label=document.createElement('summary');label.textContent=role.toUpperCase()+' · '+(artifact.name||artifact.id)+' · '+(artifact.sha256||'hash unavailable');source.append(label);
   const code=document.createElement('div'); code.className='source-code';
   const lines=String(artifact.content||'Artifact content unavailable for this run.').split(/\r?\n/).slice(0,600);
   lines.forEach((line,index)=>{const row=document.createElement('div');row.className='source-line';const number=document.createElement('button');number.type='button';number.className='source-line-number';number.textContent=String(index+1);number.setAttribute('aria-label','Inspect '+(artifact.name||role)+' line '+(index+1));number.onclick=()=>{setEvidenceCursor('source',role+':'+(index+1));const inspector=$('#artifactInspector');if(!inspector)return;inspector.hidden=false;inspector.replaceChildren();const title=document.createElement('b');title.textContent=(artifact.name||role)+' · line '+(index+1);const detail=document.createElement('p');detail.textContent=line||' ';const provenance=document.createElement('p');provenance.className='hash';provenance.textContent='Run '+j.id+' · '+(artifact.sha256||'hash unavailable');inspector.append(title,detail,provenance);};const text=document.createElement('code');text.textContent=line;row.append(number,text);code.append(row);});
   source.append(code);view.append(source);
  }
  const requestedSource=q.get('source');if(requestedSource){const [sourceRole,lineNumber]=requestedSource.split(':');const sourceButton=view.querySelector('.source-line-number[aria-label*="'+sourceRole.toUpperCase()+'"]');const buttons=[...view.querySelectorAll('.source-line-number')];const target=buttons.find(button=>button.getAttribute('aria-label')?.endsWith(' line '+lineNumber));if(target)target.click();}
  const log=evidence.files['simulation/stdout.log'];
  if(log){const logBox=document.createElement('pre');logBox.textContent='Simulation output\n'+log.text;view.append(logBox);}
  const waveform=document.createElement('p');waveform.textContent=evidence.waveform.present?'Waveform evidence present: simulation/waveform.vcd':'Waveform evidence unavailable for this run.';waveform.className=evidence.waveform.present?'evidence-good':'evidence-missing';view.append(waveform);
  if(evidence.waveform.present){
   const waveDetails=document.createElement('details'); waveDetails.open=true;
   const summary=document.createElement('summary'); summary.textContent='Waveform signals · '+(evidence.waveform.signals||[]).length+' captured'; waveDetails.append(summary);
   const signalNav=document.createElement('div'); signalNav.className='wave-signal-nav'; signalNav.setAttribute('aria-label','Select waveform signal');
   const waveDetail=document.createElement('pre'); waveDetail.className='wave-detail'; waveDetail.setAttribute('aria-live','polite');
   const excerpt=evidence.waveform.excerpt||'';
   const selectSignal=(signal,button)=>{
    setEvidenceCursor('signal',signal);signalNav.querySelectorAll('button').forEach(node=>node.classList.toggle('active',node===button));
    const lines=excerpt.split(/\r?\n/).filter(line=>line.toLowerCase().includes(String(signal).toLowerCase()));
    waveDetail.textContent='Signal '+signal+' · '+(lines.length?'matching VCD records':'no sampled transition in bounded excerpt')+'\n'+(lines.slice(0,20).join('\n')||'The captured excerpt does not include this signal transition.');
   };
   for(const signal of (evidence.waveform.signals||[])){
    const button=document.createElement('button'); button.type='button'; button.className='secondary wave-signal'; button.textContent=signal; button.setAttribute('aria-label','Inspect waveform signal '+signal); button.onclick=()=>selectSignal(signal,button); signalNav.append(button);
   }
   waveDetails.append(signalNav); waveDetails.append(waveDetail);
   const requestedSignal=q.get('signal');const first=requestedSignal?[...signalNav.querySelectorAll('button')].find(button=>button.textContent===requestedSignal):null;const fallback=signalNav.querySelector('button');if(first) first.click();else if(fallback) fallback.click();else waveDetail.textContent=excerpt||'Waveform content unavailable';
   view.append(waveDetails);
  }
  const timeline=document.createElement('details');timeline.open=true;const timelineSummary=document.createElement('summary');timelineSummary.textContent='Durable event history · '+(j.events||[]).length+' recorded';timeline.append(timelineSummary);const eventList=document.createElement('div');eventList.className='event-list';
  for(const [index,event] of (j.events||[]).entries()){
   const eventButton=document.createElement('button');eventButton.type='button';eventButton.className='secondary event-record';const status=event.status||event.event||'event';const stamp=event.at||event.timestamp||event.created_at||'';eventButton.textContent=(index+1)+'. '+status+(stamp?' · '+stamp:'');eventButton.setAttribute('aria-label','Inspect durable event '+(index+1)+' '+status);eventButton.onclick=()=>{setEvidenceCursor('event',index+1);const inspector=$('#artifactInspector');if(!inspector)return;inspector.hidden=false;inspector.replaceChildren();const title=document.createElement('b');title.textContent='Run '+j.id+' · event '+(index+1);const detail=document.createElement('pre');detail.textContent=JSON.stringify(event,null,2);const boundary=document.createElement('p');boundary.className='hash';boundary.textContent='Event is recorded in the selected run history; it does not expand the evidence claim by itself.';inspector.append(title,detail,boundary);};eventList.append(eventButton);
  }
  if(!(j.events||[]).length){const empty=document.createElement('p');empty.className='evidence-missing';empty.textContent='No durable events were recorded for this run.';eventList.append(empty);}else if(q.get('event')){const requested=eventList.querySelectorAll('button')[Number(q.get('event'))-1];if(requested)requested.click();}timeline.append(eventList);view.append(timeline);
 }catch(e){if(version===selectionVersion)showMissingEvidence('Could not load selected run: '+e.message);}
}
async function loadJobs(){const q=new URLSearchParams(location.search),api=q.get('api'),project=q.get('project'),key=getApiKey();$('#jobsWrap').innerHTML='<div class="empty">Loading durable runs…</div>';if(mode==='live'&&!project){renderJobs([]);return;}if(mode==='sample'){renderJobs([{id:'demo-8932',kind:'project-simulation',status:'failed',created_at:new Date(Date.now()-7200000).toISOString()},{id:'demo-8911',kind:'project-formal-proof',status:'passed',created_at:new Date(Date.now()-14400000).toISOString()}]);return}try{const r=await fetch(api+'/v1/jobs?project_id='+encodeURIComponent(project),{headers:{'X-Project-Key':getProjectKey(),'X-API-Key':key}});if(!r.ok)throw new Error('jobs unavailable');renderJobs(await r.json());$('#pipelineUpdated').textContent='Updated '+new Date().toLocaleTimeString();$('#connectionState').textContent='Live API connected'}catch(e){$('#pipelineUpdated').textContent=e.message.includes('401')?'Unauthorized · reconnect required':'Stale · retrying';renderJobs([]);toast('Could not refresh runs: '+e.message)}}function navigate(view, push=true){
 const targets={overview:'.main',sources:'#collateralPanel',runs:'#runsPanel',debug:'#failureHeading',coverage:'#closurePanel',reports:'#reportPanel'};
 const target=document.querySelector(targets[view]||'.main') || document.querySelector('main');
 document.querySelectorAll('.nav button').forEach(b=>{b.classList.toggle('active',b.dataset.view===view);b.setAttribute('aria-current',b.dataset.view===view?'page':'false');});
 if(push)history.pushState({},'',location.pathname+location.search+'#'+view);
 target.tabIndex=-1;target.focus({preventScroll:true});target.scrollIntoView({block:'start'});
}
document.querySelectorAll('.nav button').forEach(b=>b.onclick=()=>navigate(b.dataset.view));
window.addEventListener('popstate',()=>navigate(location.hash.slice(1)||'overview',false));

document.querySelectorAll('.tabs button').forEach(b=>b.onclick=()=>{document.querySelectorAll('.tabs button').forEach(x=>x.classList.remove('active'));b.classList.add('active');const evidence=b.dataset.tab==='evidence';$('#evidenceView').hidden=!evidence;$('#alternateView').hidden=evidence;if(evidence){if(mode==='live'||$('#failureHeading').textContent!==demo.failures[0].id)showMissingEvidence('No rendered evidence is available for this selection yet.');return;}const report=window.workbenchReport;const diagnosis=report?.diagnosis?.summary||report?.failure?.message||'No diagnosis report loaded for this run.';const formal=report?.formal?.status||'Not reported';const closure=report?.closure?.open??'not reported';const boundary=report?.claim_boundary||'Claims remain bound to the available artifacts.';const counterexample=report?.formal?.counterexample||report?.failure?.counterexample||'No counterexample payload attached';const solver=report?.formal?.solver||report?.execution?.tools?.join(', ')||'Solver evidence not reported';$('#alternateView').innerHTML='<h3>'+b.textContent+'</h3><p>'+diagnosis+'</p><div class="prov-row"><span>Formal result</span><b>'+formal+'</b></div><div class="prov-row"><span>Solver evidence</span><b>'+solver+'</b></div><div class="prov-row"><span>Counterexample</span><b>'+counterexample+'</b></div><div class="prov-row"><span>Closure items open</span><b>'+closure+'</b></div><div class="prov-row"><span>Claim boundary</span><b>'+boundary+'</b></div>'});document.querySelectorAll('.provenance .prov-row').forEach(row=>{row.classList.add('evidence-link');row.tabIndex=0;row.onclick=()=>{const label=row.querySelector('span')?.textContent||'Evidence';const value=row.querySelector('b')?.textContent||'';$('#artifactInspector').hidden=false;$('#artifactInspector').innerHTML='<b>'+label+'</b><p>'+value+'</p><p class="hash">Evidence remains bound to the selected run; export the bundle for the immutable file.</p>';toast('Opened '+label+' evidence')};row.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();row.click()}}});async function createRepairProposal(){const q=new URLSearchParams(location.search),api=q.get('api'),project=q.get('project'),job=q.get('job'),key=getApiKey();if(!api||!project||!job){$('#approval').classList.add('show');$('#repairButton').textContent='Approve & run retest';$('#repairButton').onclick=approveRepair;toast('Review-only repair proposal created in demo mode');return}try{const r=await fetch(api+'/v1/jobs/'+encodeURIComponent(job)+'/repair-retest',{method:'POST',headers:{'Content-Type':'application/json','X-Project-Key':getProjectKey(),'X-API-Key':key},body:JSON.stringify({before:q.get('before')||'ACC_OVERFLOW',after:q.get('after')||'ACC_SATURATED',rationale:'Saturation guard ordering suggested by linked assertion, waveform, and signal cone.',approved:false})});if(!r.ok)throw new Error(await r.text());window.repairProposal=await r.json();$('#approval').classList.add('show');$('#repairButton').textContent='Approve & run retest';$('#repairButton').onclick=approveRepair;toast('Review-only proposal created; approval required')}catch(e){toast('Repair proposal failed: '+e.message)}}async function approveRepair(){if(!confirm('Approve this exact repair and enqueue a retest?'))return;const q=new URLSearchParams(location.search),api=q.get('api'),project=q.get('project'),job=q.get('job'),key=getApiKey();if(!api||!project||!job){$('#approval').textContent='Demo approval recorded. Retest remains simulated.';toast('Demo repair approved');return}try{const r=await fetch(api+'/v1/jobs/'+encodeURIComponent(job)+'/repair-retest',{method:'POST',headers:{'Content-Type':'application/json','X-Project-Key':getProjectKey(),'X-API-Key':key},body:JSON.stringify({before:q.get('before')||'ACC_OVERFLOW',after:q.get('after')||'ACC_SATURATED',rationale:'Approved after evidence review.',approved:true})});if(!r.ok)throw new Error(await r.text());const result=await r.json();window.retestJob=result.retest_job?.id;window.baselineJob=job;$('#approval').textContent='Repair approved. Retest job '+(result.retest_job?.id||'created')+' is queued.';$('#repairButton').disabled=true;$('#reportState').textContent='Retest queued';loadJobs();toast('Approved repair retest queued')}catch(e){toast('Retest failed: '+e.message)}}$('#repairButton').onclick=createRepairProposal;$('#debugButton').onclick=()=>toast('Debug session seeded from the selected failure');async function loadReport(){const q=new URLSearchParams(location.search),api=q.get('api'),project=q.get('project'),key=getApiKey();if(!api||!project){window.workbenchReport={diagnosis:{summary:'Demo diagnosis: accumulator overflow follows a one-cycle saturation-guard ordering issue.'},formal:{status:'bounded'},closure:{open:3},claim_boundary:'Simulation evidence is not exhaustive functional coverage or hardware qualification.'};$('#reportState').textContent='Demo report';$('#reportSummary').textContent='Demo report: 3 blockers, 72% pass rate, 86% provenance-linked evidence.';$('#signoffButton').disabled=true;$('#bundleButton').disabled=true;$('#previewBundle').disabled=true;$('#reportSummary').textContent+=' Sample only: no signed or downloadable run package exists.';toast('Loaded sample report');return}try{const jr=await fetch(api+'/v1/jobs?project_id='+encodeURIComponent(project),{headers:{'X-Project-Key':getProjectKey(),'X-API-Key':key}});if(!jr.ok)throw new Error('jobs unavailable');const jobs=(await jr.json()).filter(j=>['passed','failed'].includes(j.status));if(!jobs.length)throw new Error('no terminal jobs');const latest=jobs[0];const rr=await fetch(api+'/v1/jobs/'+latest.id+'/proof-of-value',{headers:{'X-Project-Key':getProjectKey(),'X-API-Key':key}});if(!rr.ok)throw new Error('PoV report unavailable');const report=await rr.json();window.workbenchReport=report;window.workbenchReportJob=latest.id;const cov=report.coverage||{};$('#coverageValue').textContent=cov.percentage==null?'Not reported':cov.percentage+'%';$('#closureOpen').textContent=report.closure?.open??'Not reported';$('#formalValue').textContent=report.formal?.status||'Not reported';$('#integrityValue').textContent=report.artifact_integrity?.valid?'Verified':'Review';$('#bundleButton').disabled=false;$('#previewBundle').disabled=false;$('#reportState').textContent='Bound to '+latest.id.slice(0,10);$('#reportSummary').textContent='Run '+latest.kind+' · '+latest.status+' · '+Object.keys(report.claims||report).length+' report fields';$('#signoffButton').disabled=false;toast('PoV report loaded with run identity')}catch(e){$('#reportState').textContent='Report unavailable';toast('Could not load PoV: '+e.message)}}async function signoff(){if(!window.workbenchReportJob){toast('Load a PoV report first');return}if(!confirm('Sign off this exact evidence package as reviewed?'))return;const q=new URLSearchParams(location.search),api=q.get('api'),key=getApiKey();if(!api){$('#reportState').textContent='Demo signoff recorded';toast('Demo signoff recorded');return}try{const r=await fetch(api+'/v1/jobs/'+window.workbenchReportJob+'/signoff',{method:'POST',headers:{'Content-Type':'application/json','X-Project-Key':getProjectKey(),'X-API-Key':key},body:JSON.stringify({reviewer:'verification-lead',notes:'Reviewed in Verification Workbench against linked evidence.',approved:true})});if(!r.ok)throw new Error(await r.text());$('#reportState').textContent='Signed off · hash-bound';toast('Signoff recorded against report hash')}catch(e){toast('Signoff failed: '+e.message)}}async function previewBundle(){const q=new URLSearchParams(location.search),api=q.get('api'),key=getApiKey();if(!window.workbenchReportJob){toast('Load a PoV report first');return}if(!api){$('#reportSummary').textContent='Demo bundle: manifest, logs, waveform, diagnosis, closure, and PoV report.';toast('Demo bundle contents previewed');return}try{const r=await fetch(api+'/v1/jobs/'+window.workbenchReportJob+'/bundle',{headers:{'X-Project-Key':getProjectKey(),'X-API-Key':key}});if(!r.ok)throw new Error('bundle unavailable');const b=await r.json();$('#reportSummary').textContent='Bundle contains '+b.bundle_files+' files · '+(b.missing_files?.length||0)+' missing · '+Object.keys(b.evidence||{}).length+' evidence pointers.';toast('Bundle contents previewed')}catch(e){toast('Bundle preview failed: '+e.message)}}async function downloadBundle(){const q=new URLSearchParams(location.search),api=q.get('api'),key=getApiKey();if(!window.workbenchReportJob){toast('Load a PoV report first');return}if(!api){toast('Demo bundle is represented by the run evidence above');return}try{const r=await fetch(api+'/v1/jobs/'+window.workbenchReportJob+'/bundle/download',{headers:{'X-Project-Key':getProjectKey(),'X-API-Key':key}});if(!r.ok)throw new Error('bundle unavailable');const blob=await r.blob(),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='verification-'+window.workbenchReportJob+'.zip';a.click();URL.revokeObjectURL(url);toast('Evidence bundle download started')}catch(e){toast('Bundle download failed: '+e.message)}}async function compareRetest(){const q=new URLSearchParams(location.search),api=q.get('api'),baseline=q.get('baseline')||window.baselineJob,retest=q.get('retest')||window.retestJob,key=getApiKey();if(!api||!baseline||!retest){toast('Add baseline and retest query values for a live comparison');return}try{const r=await fetch(api+'/v1/jobs/'+encodeURIComponent(baseline)+'/compare/'+encodeURIComponent(retest),{headers:{'X-Project-Key':getProjectKey(),'X-API-Key':key}});if(!r.ok)throw new Error('comparison unavailable');const d=await r.json();const m=d.metrics||d;const b=d.baseline||{};const t=d.retest||{};$('#comparisonDetail').hidden=false;$('#comparisonResolved').textContent=(m.failure_resolved??m.failures_resolved)?'Resolved':'Still failing';$('#comparisonDelta').textContent=(m.coverage_delta_percentage_points??m.coverage_delta??'reported')+' pts';$('#comparisonBaseline').textContent=(b.report_sha256||'not reported').slice(0,12);$('#comparisonRetest').textContent=(t.report_sha256||'not reported').slice(0,12);$('#reportState').textContent='Baseline vs retest loaded';$('#reportSummary').textContent='Captured simulation comparison · claim boundary preserved';toast('Baseline versus retest comparison loaded')}catch(e){toast('Comparison failed: '+e.message)}}async function artifactAction(action){const a=window.selectedArtifact;if(!a){toast('Select an artifact first');return}const q=new URLSearchParams(location.search),api=q.get('api'),project=q.get('project'),key=getApiKey();if(!api||!project){toast('Demo '+action+' action recorded');return}try{const r=await fetch(api+'/v1/projects/'+encodeURIComponent(project)+'/collateral/'+encodeURIComponent(a.id)+'/'+action,{method:'POST',headers:{'X-Project-Key':getProjectKey(),'X-API-Key':key}});if(!r.ok)throw new Error(await r.text());window.artifactActionResult=await r.json();const result=document.createElement('pre');result.textContent=JSON.stringify(window.artifactActionResult,null,2);$('#artifactInspector').append(result);toast(action+' completed');loadCollateral()}catch(e){toast(action+' failed: '+e.message)}}$('#collateralSearch').oninput=e=>{const q=e.target.value.toLowerCase();document.querySelectorAll('.collateral-row').forEach(r=>r.hidden=!r.textContent.toLowerCase().includes(q))};$('#uploadCollateral').onclick=uploadCollateral;$('#loadCollateral').onclick=loadCollateral;loadCollateral();$('#loadReport').onclick=loadReport;$('#previewBundle').onclick=previewBundle;$('#bundleButton').onclick=downloadBundle;$('#compareButton').onclick=compareRetest;$('#signoffButton').onclick=signoff;$('#refreshRuns').onclick=loadJobs;loadJobs();setInterval(()=>{if(new URLSearchParams(location.search).get('api'))loadJobs()},5000);$('#runButton').onclick=async()=>{const q=new URLSearchParams(location.search),api=q.get('api'),project=q.get('project'),artifact=q.get('artifact'),tb=q.get('tb'),kind=$('#jobKind').value,key=getApiKey();const needsTb=kind==='project-simulation',needsTbs=kind==='project-regression';if(!api||!project||!artifact||(needsTb&&!tb)||(needsTbs&&!q.get('tbs'))){toast('Demo run queued; provide live API, project, artifact, and required testbench IDs');return}try{const payload={kind,project_id:project,artifact_id:artifact,idempotency_key:'workbench-'+Date.now()};if(needsTb)payload.testbench_artifact_id=tb;if(needsTbs)payload.testbench_artifact_ids=q.get('tbs').split(',').filter(Boolean);if(kind==='project-formal-proof'){payload.formal_signal=q.get('signal')||'result';payload.formal_expected=q.get('expected')||'0';payload.formal_sequence=Number(q.get('sequence')||3)}const r=await fetch(api+'/v1/jobs',{method:'POST',headers:{'Content-Type':'application/json','X-Project-Key':getProjectKey(),'X-API-Key':key},body:JSON.stringify(payload)});if(!r.ok)throw new Error(await r.text());const job=await r.json();toast('Job '+job.id.slice(0,8)+' queued');const run=await fetch(api+'/v1/jobs/'+job.id+'/run-async',{method:'POST',headers:{'X-Project-Key':getProjectKey(),'X-API-Key':key}});if(!run.ok)throw new Error(await run.text());toast(kind+' worker started; open Runs to monitor it')}catch(e){toast('Could not start live job: '+e.message)}};hydrate();
// Safe run-list renderer: service-controlled identifiers are always text.
function renderJobs(jobs){const wrap=$('#jobsWrap');if(!wrap)return;wrap.replaceChildren();if(!jobs.length){wrap.textContent='No jobs for this project yet.';return;}const table=document.createElement('table');table.className='jobs';const head=document.createElement('thead'),header=document.createElement('tr');for(const label of ['Job','Kind','Status','Created']){const cell=document.createElement('th');cell.textContent=label;header.append(cell);}head.append(header);table.append(head);const body=document.createElement('tbody');for(const job of jobs.slice(0,8)){const row=document.createElement('tr'),idCell=document.createElement('td'),button=document.createElement('button');button.type='button';button.className='secondary job-select';button.dataset.job=String(job.id||'');button.textContent=String(job.id||'').slice(0,10);button.onclick=()=>inspectJob(String(job.id||''));idCell.append(button);const kind=document.createElement('td');kind.textContent=String(job.kind||'unknown');const statusCell=document.createElement('td'),status=document.createElement('span');status.className='job-status '+String(job.status||'unknown');status.textContent=String(job.status||'unknown');statusCell.append(status);const created=document.createElement('td'),date=new Date(job.created_at);created.textContent=Number.isNaN(date.getTime())?'Not reported':date.toLocaleString();row.append(idCell,kind,statusCell,created);body.append(row);}table.append(body);wrap.append(table);}

// Selected-run report binding follows the selected terminal job.
async function loadSelectedReport(){
 const q=new URLSearchParams(location.search),api=q.get('api'),project=q.get('project');
 if(!api||!project){$('#reportState').textContent='Sample report';$('#reportSummary').textContent='Illustrative report only. It cannot be signed or downloaded.';$('#signoffButton').disabled=true;$('#bundleButton').disabled=true;$('#previewBundle').disabled=true;toast('Sample report is not signable');return;}
 try{
  const response=await fetch(api+'/v1/jobs?project_id='+encodeURIComponent(project),{headers:{'X-Project-Key':getProjectKey(),'X-API-Key':getApiKey()}});if(!response.ok)throw new Error('jobs unavailable');
  const jobs=(await response.json()).filter(j=>['passed','failed'].includes(j.status));const id=window.selectedJob?.id||q.get('job');const job=id?jobs.find(j=>j.id===id):jobs[0];if(!job)throw new Error('Select a terminal run before loading its report');
  const endpoint=job.kind==='project-regression'?'regression-proof-of-value':'proof-of-value';const reportResponse=await fetch(api+'/v1/jobs/'+encodeURIComponent(job.id)+'/'+endpoint,{headers:{'X-Project-Key':getProjectKey(),'X-API-Key':getApiKey()}});if(!reportResponse.ok)throw new Error('PoV report unavailable for '+job.kind);
  const report=await reportResponse.json();window.workbenchReport=report;window.workbenchReportJob=job.id;const coverage=report.coverage||{};$('#coverageValue').textContent=coverage.percentage==null?'Not reported':coverage.percentage+'%';$('#closureOpen').textContent=report.closure?.open??'Not reported';$('#formalValue').textContent=report.formal?.status||'Not reported';$('#integrityValue').textContent=report.artifact_integrity?.valid===true?'Verified':report.artifact_integrity?.valid===false?'Invalid':'Not reported';$('#bundleButton').disabled=false;$('#previewBundle').disabled=false;$('#signoffButton').disabled=false;$('#reportState').textContent='Bound to '+job.id.slice(0,10);$('#reportSummary').textContent='Run '+job.kind+' · '+job.status+' · '+Object.keys(report).length+' report fields';toast('Report loaded for selected run');
 }catch(e){$('#reportState').textContent='Report unavailable';$('#signoffButton').disabled=true;toast('Could not load PoV: '+e.message);}
}
$('#loadReport').onclick=loadSelectedReport;

// Analysis content can contain model or tool output. Re-render it through
// text nodes after the legacy tab handler runs so markup is never interpreted.
function renderAnalysisSafely(button){
 const report=window.workbenchReport||{};
 const view=$('#alternateView');if(!view)return;
 view.replaceChildren();
 const heading=document.createElement('h3');heading.textContent=button?.textContent||'Analysis';view.append(heading);
 const diagnosis=document.createElement('p');diagnosis.textContent=report.diagnosis?.summary||report.failure?.message||'No diagnosis report loaded for this run.';view.append(diagnosis);
 const values=[['Formal result',report.formal?.status||'Not reported'],['Solver evidence',report.formal?.solver||report.execution?.tools?.join(', ')||'Solver evidence not reported'],['Counterexample',report.formal?.counterexample||report.failure?.counterexample||'No counterexample payload attached'],['Closure items open',report.closure?.open??'not reported'],['Claim boundary',report.claim_boundary||'Claims remain bound to the available artifacts.']];
 for(const [label,value] of values){const row=document.createElement('div');row.className='prov-row evidence-link';row.tabIndex=0;const name=document.createElement('span');name.textContent=label;const detail=document.createElement('b');detail.textContent=String(value);row.append(name,detail);row.onclick=()=>inspectAnalysisEvidence(label,String(value));row.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();row.click();}};view.append(row);}
}
function inspectAnalysisEvidence(label,value){
 const inspector=$('#artifactInspector');if(!inspector)return;inspector.hidden=false;inspector.replaceChildren();
 const title=document.createElement('b');title.textContent=label;const detail=document.createElement('p');detail.textContent=value;const boundary=document.createElement('p');boundary.className='hash';boundary.textContent='Evidence remains bound to the selected run; export the bundle for the immutable file.';inspector.append(title,detail,boundary);toast('Opened '+label+' evidence');
}
document.querySelector('.tabs')?.addEventListener('click',event=>{
 const button=event.target.closest('button[data-tab]');if(button?.dataset.tab==='analysis')renderAnalysisSafely(button);
});

const auditAction=document.createElement('button');auditAction.type='button';auditAction.className='secondary';auditAction.id='auditButton';auditAction.textContent='Export audit';
const auditState=document.createElement('small');auditState.id='auditState';auditState.className='hash';auditState.setAttribute('aria-live','polite');auditState.textContent='Audit not exported';
document.querySelector('.report-actions')?.append(auditAction,auditState);
auditAction.onclick=async()=>{
 const q=new URLSearchParams(location.search),api=q.get('api'),project=q.get('project');
 if(!api||!project){toast('Audit export requires a connected project');return;}
 try{const response=await fetch(api+'/v1/projects/'+encodeURIComponent(project)+'/audit?limit=500',{headers:{'X-Project-Key':getProjectKey(),'X-API-Key':getApiKey()}});if(!response.ok)throw new Error('audit unavailable');const payload=await response.json();const blob=new Blob([JSON.stringify(payload,null,2)],{type:'application/json'});const url=URL.createObjectURL(blob),link=document.createElement('a');link.href=url;link.download='verification-audit-'+project+'.json';link.click();URL.revokeObjectURL(url);auditState.textContent='Audit '+payload.total+' entries · '+(payload.truncated?'truncated · ':'')+String(payload.export_sha256||'digest unavailable').slice(0,16);toast('Project audit export downloaded');}catch(error){auditState.textContent='Audit export unavailable';toast('Audit export failed: '+error.message);}
};

// Make unavailable actions visually match their semantic state, especially
// the run action before live collateral is uploaded.
const disabledStyle=document.createElement('style');
disabledStyle.textContent='button:disabled{cursor:not-allowed;opacity:.52;filter:grayscale(.35)}button:disabled:focus-visible{outline:2px solid var(--muted);outline-offset:2px}';
document.head.append(disabledStyle);

// Keep the adapter affordance deployment-driven. A connected URL selects the
// registered name and optional JSON argument list without hard-coding tools.
const adapterSelector = $('#jobKind');
if (adapterSelector && ![...adapterSelector.options].some(option => option.value === 'customer-adapter')) {
  const option = document.createElement('option');
  option.value = 'customer-adapter';
  option.textContent = 'Customer adapter';
  adapterSelector.append(option);
}
const defaultRunHandler = $('#runButton')?.onclick;
if ($('#runButton') && defaultRunHandler) {
  $('#runButton').onclick = async event => {
    if ($('#jobKind').value !== 'customer-adapter') return defaultRunHandler(event);
    const q = new URLSearchParams(location.search), api = q.get('api'), project = q.get('project'), adapter = q.get('adapter') || sessionStorage.getItem('workbench.adapter:'+credentialScope()), key = getApiKey();
    if (!api || !project || !adapter) { toast('Select a connected project and adapter before running'); return; }
    let args;
    try { args = JSON.parse($('#adapterArgsInput')?.value || '[]'); } catch (_) { toast('Adapter arguments must be a JSON array'); return; }
    if (!Array.isArray(args) || args.some(arg => typeof arg !== 'string' || !arg)) { toast('Adapter arguments must be non-empty strings'); return; }
    const argumentBytes = args.map(arg => new TextEncoder().encode(arg).length);
    if (args.length > 64) { toast('Adapter arguments exceed the 64-argument limit'); return; }
    if (argumentBytes.some(size => size > 4096)) { toast('One adapter argument exceeds the 4 KiB limit'); return; }
    if (argumentBytes.reduce((sum, size) => sum + size, 0) > 65536) { toast('Adapter arguments exceed the 64 KiB total limit'); return; }
    try {
      const response = await fetch(api + '/v1/jobs', {method:'POST', headers:{'Content-Type':'application/json','X-Project-Key':getProjectKey(),'X-API-Key':key}, body:JSON.stringify({kind:'customer-adapter', project_id:project, adapter_name:adapter, adapter_args:args, artifact_id:q.get('artifact') || null, idempotency_key:'workbench-adapter-'+Date.now()})});
      if (!response.ok) throw new Error(await response.text());
      const job = await response.json();
      toast('Customer adapter job ' + job.id.slice(0, 8) + ' queued');
      const started = await fetch(api + '/v1/jobs/' + job.id + '/run-async', {method:'POST', headers:{'X-Project-Key':getProjectKey(),'X-API-Key':key}});
      if (!started.ok) throw new Error(await started.text());
      toast('Adapter worker started; monitor Runs for evidence');
    } catch (error) { toast('Could not start adapter: ' + error.message); }
  };
}
