/* Setup forms share the current project's API context; credentials never enter URLs. */
const setupDialog = document.createElement('dialog');
setupDialog.className = 'setup-dialog';
setupDialog.setAttribute('aria-labelledby', 'setupTitle');
document.body.append(setupDialog);

function setupField(form, label, name, {type = 'text', value = '', required = true, options, help} = {}) {
  const wrapper = document.createElement('label');
  wrapper.textContent = label;
  const input = document.createElement(options ? 'select' : type === 'textarea' ? 'textarea' : 'input');
  input.name = name;
  input.setAttribute('aria-label', label);
  if (input.tagName === 'INPUT') input.type = type;
  input.required = required;
  if (options) for (const option of options) input.add(new Option(option.label, option.value));
  if (type !== 'file') input.value = value;
  wrapper.append(input); form.append(wrapper);
  if (help) { const p = document.createElement('p'); p.className = 'help'; p.textContent = help; form.append(p); }
  return input;
}

function setupForm(title, description, submitLabel, build, submit) {
  setupDialog.replaceChildren();
  const form = document.createElement('form');
  const heading = document.createElement('h2'); heading.id = 'setupTitle'; heading.textContent = title;
  const help = document.createElement('p'); help.className = 'help'; help.textContent = description;
  form.append(heading, help);
  build(form);
  const error = document.createElement('p'); error.className = 'form-error'; error.setAttribute('role', 'alert');
  const actions = document.createElement('div'); actions.className = 'actions';
  const cancel = document.createElement('button'); cancel.type = 'button'; cancel.className = 'secondary'; cancel.textContent = 'Cancel'; cancel.onclick = () => setupDialog.close();
  const send = document.createElement('button'); send.type = 'submit'; send.className = 'primary'; send.textContent = submitLabel;
  actions.append(cancel, send); form.append(error, actions); setupDialog.append(form);
  form.onsubmit = async event => {
    event.preventDefault(); error.textContent = ''; send.disabled = true;
    try { await submit(new FormData(form), form); }
    catch (e) { error.textContent = e.message; }
    finally { send.disabled = false; }
  };
  setupDialog.showModal();
}

async function setupRequest(path, {method = 'GET', body, origin, apiKey, projectKey} = {}) {
  const api = origin ?? new URLSearchParams(location.search).get('api');
  if (!api) throw new Error('Connect to a verification service first.');
  let response;
  try {
    response = await fetch(api + path, {method, headers: {
      'Content-Type': 'application/json', 'X-API-Key': apiKey ?? getApiKey(),
      'X-Project-Key': projectKey ?? getProjectKey(),
      'X-Request-ID': 'workbench-' + crypto.randomUUID()
    }, ...(body === undefined ? {} : {body: JSON.stringify(body)})});
  } catch (_) { throw new Error('Cannot reach this service. Check the address and connection. For a same-origin connection, open the service’s /workbench/ page.'); }
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    const detail = typeof payload.detail === 'string' ? payload.detail : JSON.stringify(payload.detail || 'Request failed');
    const requestId = response.headers.get('X-Request-ID');
    throw new Error((response.status === 401 ? 'API authentication failed. ' : response.status === 403 ? 'Project access denied. ' : '') + detail + (requestId ? ' (request ' + requestId + ')' : ''));
  }
  return response.json();
}

function connectWorkspace() {
  setupForm('Connect verification service', 'Your credentials stay in this browser tab’s session and are scoped to the service address. Sample data will not fill missing service results.', 'Connect', form => {
    setupField(form, 'Service address', 'origin', {type: 'url', value: new URLSearchParams(location.search).get('api') || location.origin});
    setupField(form, 'API key', 'apiKey', {type: 'password', required: false});
    setupField(form, 'Project key (if required)', 'projectKey', {type: 'password', required: false});
  }, async data => {
    const url = new URL(data.get('origin'));
    if (!['http:', 'https:'].includes(url.protocol) || url.username || url.password || url.search || url.hash || url.pathname !== '/') throw new Error('Use a service origin such as http://localhost:8000, without credentials, path, or query.');
    const origin = url.origin;
    const projects = await setupRequest('/v1/projects', {origin, apiKey: data.get('apiKey'), projectKey: data.get('projectKey')});
    sessionStorage.setItem('workbench.apiKey:' + origin, data.get('apiKey'));
    sessionStorage.setItem('workbench.projectKey:' + origin, data.get('projectKey'));
    const next = new URL(location.href); next.search = ''; next.hash = '';
    next.searchParams.set('api', origin);
    if (projects.length) next.searchParams.set('project', projects[0].id);
    location.assign(next.href);
  });
}

function newProjectForm() {
  if (mode !== 'live') { connectWorkspace(); return; }
  setupForm('Create project', 'Keep each design and its verification history in a separate project.', 'Create project', form => {
    setupField(form, 'Project name', 'name');
    const id = setupField(form, 'Project ID', 'id', {help: 'Letters, numbers, hyphens, and underscores. Used in durable run identities.'});
    id.pattern = '[A-Za-z0-9_-]+';
  }, async data => {
    const project = await setupRequest('/v1/projects', {method: 'POST', body: {name: data.get('name').trim(), id: data.get('id')}});
    const next = new URL(location.href); next.search = ''; next.hash = '';
    next.searchParams.set('api', credentialScope()); next.searchParams.set('project', project.id);
    location.assign(next.href);
  });
}

function uploadArtifactForm() {
  if (mode !== 'live') { connectWorkspace(); return; }
  const project = new URLSearchParams(location.search).get('project');
  if (!project) { newProjectForm(); return; }
  setupForm('Upload design input', 'Upload or paste one versioned artifact. Its content hash is recorded before ingestion; uploading does not mean its requirements are verified.', 'Upload artifact', form => {
    const name = setupField(form, 'Filename', 'name');
    setupField(form, 'Artifact kind', 'kind', {value: 'rtl', options: [
      {label: 'RTL', value: 'rtl'}, {label: 'Testbench / procedural checker', value: 'testbench'}, {label: 'Specification', value: 'specification'}]});
    setupField(form, 'Version', 'version', {value: '1'});
    const file = setupField(form, 'Choose text file (optional)', 'file', {type: 'file', required: false});
    const content = setupField(form, 'Content', 'content', {type: 'textarea'});
    file.onchange = async () => {
      if (!file.files.length) return;
      if (file.files[0].size > 1024 * 1024) { file.setCustomValidity('Choose a file of at most 1 MB.'); file.reportValidity(); return; }
      file.setCustomValidity(''); name.value = file.files[0].name; content.value = await file.files[0].text();
    };
  }, async data => {
    await setupRequest('/v1/projects/' + encodeURIComponent(project) + '/collateral', {method: 'POST', body: {
      name: data.get('name'), kind: data.get('kind'), version: data.get('version'), content: data.get('content')
    }});
    setupDialog.close(); await loadCollateral(); navigate('sources'); toast('Artifact uploaded. Select it to inspect and ingest.');
  });
}

async function newRunForm() {
  if (mode !== 'live') { connectWorkspace(); return; }
  const project = new URLSearchParams(location.search).get('project');
  if (!project) { newProjectForm(); return; }
  setupForm('Configure verification run', 'Choose immutable inputs. The run records these artifact identities. Procedural simulation checks only exercised behavior; bounded proof applies only to its configured bound.', 'Queue run', form => {
    const status = document.createElement('p'); status.className = 'help'; status.id = 'runInputStatus'; status.textContent = 'Loading project artifacts and tool capabilities…'; form.append(status);
    const kind = setupField(form, 'Check', 'kind', {value: $('#jobKind').value, options: [
      {value:'project-compile',label:'Compile RTL'}, {value:'project-lint',label:'Lint RTL'},
      {value:'project-simulation',label:'Simulation / procedural checker'}, {value:'project-regression',label:'Regression'},
      {value:'project-formal',label:'Formal preflight'}, {value:'project-formal-proof',label:'Bounded invariant proof'}]});
    const rtl = setupField(form, 'RTL version', 'rtl', {options: []});
    const testbenches = setupField(form, 'Testbench / checker versions', 'testbenches', {options: [], required: false});
    const signal = setupField(form, 'Invariant signal', 'signal', {required:false});
    const expected = setupField(form, 'Expected value', 'expected', {required:false});
    const bound = setupField(form, 'Proof bound', 'bound', {type:'number',value:'3',required:false}); bound.min='1'; bound.step='1';
    const update = () => {
      const sim = ['project-simulation','project-regression'].includes(kind.value);
      testbenches.parentElement.hidden=!sim; testbenches.required=sim; testbenches.multiple=kind.value==='project-regression';
      for(const input of [signal,expected,bound]){input.parentElement.hidden=kind.value!=='project-formal-proof';input.required=kind.value==='project-formal-proof';}
    };
    kind.onchange=update; update();
    Promise.all([setupRequest('/v1/projects/'+encodeURIComponent(project)+'/collateral'), setupRequest('/v1/capabilities'), setupRequest('/v1/contract')]).then(([items,caps,contract])=>{
      if(!form.isConnected)return;
      for(const a of items){const target=a.kind==='rtl'?rtl:a.kind==='testbench'?testbenches:null;if(target)target.add(new Option(a.name+' · v'+a.version+' · '+a.sha256.slice(0,10),a.id));}
      const tools=caps.capabilities.map(c=>c.tool+': '+(c.available?'available':'unavailable'));
      const adapters=(caps.eda_adapters||[]).map(c=>c.name+' ('+c.kind+(c.version?' '+c.version:'')+'): '+(c.available?'available':'blocked'));
      status.textContent='Contract: '+(contract.schema_version||'unknown')+' · Tools: '+tools.concat(adapters.length?['Customer adapters: '+adapters.join(', ')]:[]).join(' · ')+(rtl.options.length?'':' · Upload RTL before queuing a run.');
    }).catch(e=>{if(form.isConnected)status.textContent='Could not load inputs: '+e.message;});
  }, async (data, form) => {
    const kind=data.get('kind');
    const payload={project_id:project,kind,artifact_id:data.get('rtl'),idempotency_key:form.dataset.requestId || crypto.randomUUID()};
    form.dataset.requestId=payload.idempotency_key;
    if(kind==='project-simulation')payload.testbench_artifact_id=data.get('testbenches');
    if(kind==='project-regression')payload.testbench_artifact_ids=data.getAll('testbenches');
    if(kind==='project-formal-proof'){payload.formal_signal=data.get('signal');payload.formal_expected=data.get('expected');payload.formal_sequence=Number(data.get('bound'));}
    // Once creation succeeds, retrying submission must reuse the same job.
    let jobId=form.dataset.jobId;
    let createdJob;
    if(!jobId){createdJob=await setupRequest('/v1/jobs',{method:'POST',body:payload});jobId=createdJob.id;form.dataset.jobId=jobId;}
    await setupRequest('/v1/jobs/'+encodeURIComponent(jobId)+'/run-async',{method:'POST'});
    setupDialog.close();await loadJobs();await inspectJob(jobId);navigate('debug');
    toast('Run queued'+(createdJob?.request_id?' · request '+createdJob.request_id:'')+'. A durable worker must claim it before execution starts.');
  });
}

const connectionButton=document.createElement('button');connectionButton.className='connection-button';connectionButton.textContent='Connection';connectionButton.onclick=connectWorkspace;
document.querySelector('.top-actions').prepend(connectionButton);
// Keep the identity needed for every consequential decision visible while the
// user scrolls through the long-form pilot surface. Values are derived from
// the current URL and rendered state; no example evidence is synthesized.
const contextBar=document.createElement('section');contextBar.className='workspace-context';contextBar.setAttribute('aria-label','Current verification context');
const contextStyle=document.createElement('style');contextStyle.textContent='.workspace-context{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px;margin:0 0 16px;padding:10px 12px;border:1px solid var(--line);border-radius:8px;background:#fff;box-shadow:0 2px 8px rgba(25,35,55,.04)}.workspace-context .context-item{min-width:0}.workspace-context .context-label{display:block;color:var(--muted);font-size:10px;text-transform:uppercase;letter-spacing:.06em}.workspace-context .context-value{display:block;margin-top:3px;font-size:12px;font-weight:700;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.workspace-context .context-next{color:var(--brand)}@media(max-width:720px){.workspace-context{grid-template-columns:repeat(2,minmax(0,1fr));position:sticky;top:0;z-index:3}}';document.head.append(contextStyle);
for(const [label,key] of [['Project','project'],['Run','run'],['Evidence','evidence'],['Next action','next']]){const item=document.createElement('div');item.className='context-item';const title=document.createElement('span');title.className='context-label';title.textContent=label;const value=document.createElement('span');value.className='context-value'+(key==='next'?' context-next':'');value.dataset.context=key;value.textContent='Not selected';item.append(title,value);contextBar.append(item);}
document.querySelector('.content')?.prepend(contextBar);
const confidenceLabel=document.querySelector('.confidence');
if(confidenceLabel) confidenceLabel.textContent='Assessment: review required';
function refreshWorkspaceContext(){
 const q=new URLSearchParams(location.search),project=q.get('project')||$('#crumbProject')?.textContent||'Not selected',job=window.selectedJob?.id||q.get('job');
 const report=$('#reportState')?.textContent||'';const evidence=job?(report&&!/No report selected|No report loaded|unavailable/i.test(report)?'Run evidence + report state':'Run selected · evidence pending'):(mode==='sample'?'Illustrative sample':'No run selected');
 const next=job?(window.workbenchReportJob?'Review report or compare retest':'Inspect evidence and decide next check'):(mode==='live'?'Select a terminal run':'Explore the sample journey');
 const values={project,run:job?String(job).slice(0,14):'Not selected',evidence,next};for(const [key,value] of Object.entries(values)){const node=contextBar.querySelector('[data-context="'+key+'"]');if(node)node.textContent=String(value);}
}
const contextObserver=new MutationObserver(refreshWorkspaceContext);for(const selector of ['#crumbProject','#failureHeading','#reportState','#workspaceMode']){const node=$(selector);if(node)contextObserver.observe(node,{childList:true,characterData:true,subtree:true});}refreshWorkspaceContext();
const liveStatus=document.querySelector('.status-line');if(liveStatus){liveStatus.setAttribute('role','status');liveStatus.setAttribute('aria-live','polite');}
const globalSearch=document.querySelector('.top-actions .search');
if(globalSearch){
  globalSearch.setAttribute('aria-controls','failureList jobsWrap collateralList');
  function applyGlobalSearch(){
    const query=globalSearch.value.trim().toLowerCase();let matches=0;
    for(const node of document.querySelectorAll('#failureList .failure, #jobsWrap .job-select, #collateralList .collateral-row')){const parent=node.closest('tr')||node;const hit=!query||parent.textContent.toLowerCase().includes(query);parent.hidden=!hit;if(hit)matches++;}
    const status=$('#connectionState');if(status&&query)status.textContent=matches?matches+' matching result'+(matches===1?'':'s'):'No matching runs, failures, or collateral';
    const runs=$('#jobsWrap');if(runs&&query&&!matches&&document.querySelectorAll('#failureList .failure, #jobsWrap .job-select, #collateralList .collateral-row').length){runs.dataset.searchEmpty='true';}
  }
  globalSearch.oninput=applyGlobalSearch;
  const safeRenderJobs=(items)=>{const wrap=$('#jobsWrap');wrap.replaceChildren();if(!items.length){const empty=document.createElement('div');empty.className='empty';empty.textContent='No jobs for this project yet.';wrap.append(empty);return;}const table=document.createElement('table');table.className='jobs';const head=document.createElement('thead');const header=document.createElement('tr');for(const label of ['Job','Kind','Status','Created']){const cell=document.createElement('th');cell.textContent=label;header.append(cell);}head.append(header);table.append(head);const body=document.createElement('tbody');for(const job of items.slice(0,8)){const row=document.createElement('tr');const idCell=document.createElement('td');const button=document.createElement('button');button.className='secondary job-select';button.dataset.job=job.id;button.textContent=String(job.id).slice(0,10);button.setAttribute('aria-label','Inspect run '+String(job.id).slice(0,10));button.onclick=()=>inspectJob(job.id);idCell.append(button);const kindCell=document.createElement('td');kindCell.textContent=job.kind||'Not reported';const statusCell=document.createElement('td');const status=document.createElement('span');status.className='job-status '+String(job.status||'unknown').replace(/[^a-z0-9_-]/gi,'');status.textContent=job.status||'unknown';statusCell.append(status);const createdCell=document.createElement('td');createdCell.textContent=job.created_at?new Date(job.created_at).toLocaleString():'Not reported';row.append(idCell,kindCell,statusCell,createdCell);body.append(row);}table.append(body);wrap.append(table);};
  const renderJobsWithSearch=safeRenderJobs;renderJobs=(items)=>{renderJobsWithSearch(items);applyGlobalSearch();};
  const renderCollateralWithSearch=renderCollateral;renderCollateral=(items)=>{renderCollateralWithSearch(items);applyGlobalSearch();};
}
let jobsRequestGeneration=0;
const originalLoadJobs=loadJobs;
loadJobs=async function loadJobsSequenced(){
  const generation=++jobsRequestGeneration;
  const q=new URLSearchParams(location.search),api=q.get('api'),project=q.get('project');
  if(mode==='sample'||(mode==='live'&&!project)){return originalLoadJobs();}
  try{
    const response=await fetch(api+'/v1/jobs?project_id='+encodeURIComponent(project),{headers:{'X-Project-Key':getProjectKey(),'X-API-Key':getApiKey(),'X-Request-ID':'workbench-'+crypto.randomUUID()}});
    if(!response.ok)throw new Error(response.status===401?'401 Unauthorized':'jobs unavailable');
    const jobs=await response.json();
    if(generation!==jobsRequestGeneration||project!==new URLSearchParams(location.search).get('project'))return;
    renderJobs(jobs);$('#pipelineUpdated').textContent='Updated '+new Date().toLocaleTimeString();$('#connectionState').textContent='Live API connected';
  }catch(e){
    if(generation!==jobsRequestGeneration)return;
    $('#pipelineUpdated').textContent=e.message.includes('401')?'Unauthorized · reconnect required':'Stale · retrying';
    toast('Could not refresh runs: '+e.message);
  }
};
$('#refreshRuns').onclick=()=>loadJobs();
$('#newProject').onclick=newProjectForm;
$('#uploadCollateral').onclick=uploadArtifactForm;
$('#runButton').onclick=newRunForm;
const sourcesButton=document.createElement('button');sourcesButton.textContent='Sources & plan';sourcesButton.dataset.view='sources';sourcesButton.onclick=()=>navigate('sources');document.querySelector('.nav').append(sourcesButton);

async function loadSelectedReport(){
  const q=new URLSearchParams(location.search), api=q.get('api'), project=q.get('project');
  if(!api || !project){
    $('#reportState').textContent='Sample report';
    $('#reportSummary').textContent='Illustrative report only. It cannot be signed or downloaded.';
    $('#signoffButton').disabled=true; $('#bundleButton').disabled=true; $('#previewBundle').disabled=true;
    toast('Sample report is not signable'); return;
  }
  try {
    const response=await fetch(api+'/v1/jobs?project_id='+encodeURIComponent(project),{headers:{'X-Project-Key':getProjectKey(),'X-API-Key':getApiKey(),'X-Request-ID':'workbench-'+crypto.randomUUID()}});
    if(!response.ok) throw new Error('jobs unavailable');
    const jobs=(await response.json()).filter(j=>['passed','failed'].includes(j.status));
    const id=window.selectedJob?.id || q.get('job');
    const job=id ? jobs.find(j=>j.id===id) : jobs[0];
    if(!job) throw new Error('Select a terminal run before loading its report');
    const endpoint=job.kind==='project-regression'?'regression-proof-of-value':'proof-of-value';
    const reportResponse=await fetch(api+'/v1/jobs/'+encodeURIComponent(job.id)+'/'+endpoint,{headers:{'X-Project-Key':getProjectKey(),'X-API-Key':getApiKey(),'X-Request-ID':'workbench-'+crypto.randomUUID()}});
    if(!reportResponse.ok) throw new Error('PoV report unavailable for '+job.kind);
    const report=await reportResponse.json(); window.workbenchReport=report; window.workbenchReportJob=job.id;
    const coverage=report.coverage||{};
    $('#coverageValue').textContent=coverage.reported===false||coverage.percentage==null?'Not reported':coverage.percentage+'%';
    $('#closureOpen').textContent=report.closure?.open??'Not reported';
    $('#formalValue').textContent=report.formal?.status||'Not reported';
    $('#integrityValue').textContent=report.artifact_integrity?.valid===true?'Verified':report.artifact_integrity?.valid===false?'Invalid':'Not reported';
    $('#bundleButton').disabled=false; $('#previewBundle').disabled=false; $('#signoffButton').disabled=false;
    let receipt=null; try { receipt=await setupRequest('/v1/jobs/'+encodeURIComponent(job.id)+'/signoff'); } catch(_) { /* no receipt yet is a normal pre-signoff state */ }
    $('#reportState').textContent='Bound to '+job.id.slice(0,10);
    $('#reportSummary').textContent='Run '+job.kind+' · '+job.status+' · '+Object.keys(report).length+' report fields';
    if(receipt?.valid===true){ $('#reportState').textContent='Approved · report hash '+(receipt.report_sha256||report.report_sha256||'').slice(0,12); $('#reportSummary').textContent='Reviewer '+receipt.reviewer+' · recorded '+new Date(receipt.signed_at).toLocaleString(); }
    else if(receipt && receipt.valid===false){ $('#reportState').textContent='Invalid signoff receipt'; $('#reportSummary').textContent='The stored reviewer receipt failed integrity verification. Re-review is required before relying on this package.'; $('#signoffButton').disabled=true; }
    toast('Report loaded for selected run');
  } catch(e) { $('#reportState').textContent='Report unavailable'; $('#signoffButton').disabled=true; toast('Could not load PoV: '+e.message); }
}
$('#loadReport').onclick=loadSelectedReport;

function openRepairReview(){
  const job=window.selectedJob;
  if(mode!=='live' || !job){ toast('Select a failed live simulation run before proposing a repair'); return; }
  if(job.status!=='failed' || job.kind!=='project-simulation'){ toast('A failed project simulation is required'); return; }
  setupForm('Propose a repair', 'This creates a review-only proposal. The exact text replacement and rationale will be hashed before approval.', 'Create proposal', form=>{
    setupField(form,'Current text','before',{help:'Enter one exact occurrence from the selected RTL version.'});
    setupField(form,'Proposed text','after');
    setupField(form,'Rationale','rationale',{type:'textarea',help:'Explain why this change addresses the selected evidence.'});
  }, async data=>{
    const q=new URLSearchParams(location.search);
    const response=await setupRequest('/v1/jobs/'+encodeURIComponent(job.id)+'/repair-retest',{method:'POST',body:{before:data.get('before'),after:data.get('after'),rationale:data.get('rationale'),approved:false}});
    window.repairProposal=response;
    const proposal=response.proposal||{};const box=$('#approval');box.classList.add('show');box.replaceChildren();
    const title=document.createElement('b');title.textContent='Review-only proposal · '+(proposal.status||'review_required');box.append(title);
    const diff=document.createElement('pre');diff.textContent='- '+proposal.before+'\n+ '+proposal.after+'\n\nRationale: '+proposal.rationale+'\n\nProposal SHA-256: '+(proposal.proposal_sha256||'not reported')+'\nOccurrences: '+proposal.occurrences;box.append(diff);
    const approve=document.createElement('button');approve.className='primary';approve.textContent='Approve exact proposal & queue retest';approve.onclick=approveExactRepair;box.append(approve);
    setupDialog.close();toast(proposal.status==='review_required'?'Proposal needs correction before approval':'Proposal ready for review');
  });
}

async function approveExactRepair(){
  const job=window.selectedJob, proposal=window.repairProposal?.proposal;
  if(!job||!proposal||proposal.status!=='review_required' || proposal.occurrences!==1){toast('Only a single-match review proposal can be approved');return;}
  if(!confirm('Approve the exact diff shown and enqueue its retest?'))return;
  try{
    const result=await setupRequest('/v1/jobs/'+encodeURIComponent(job.id)+'/repair-retest',{method:'POST',body:{before:proposal.before,after:proposal.after,rationale:proposal.rationale,proposal_sha256:proposal.proposal_sha256,approved:true}});
    window.baselineJob=job.id;window.retestJob=result.retest_job?.id;window.repairProposal=result;
    $('#approval').textContent='Approved exact proposal. Retest '+(result.retest_job?.id||'was not created')+' is queued.';
    $('#repairButton').disabled=true;$('#reportState').textContent='Retest queued from '+job.id.slice(0,10);await loadJobs();toast('Exact repair approved; retest queued');
  }catch(e){toast('Retest was not queued: '+e.message);}
}

$('#repairButton').onclick=openRepairReview;

async function previewSelectedBundle(){
  const jobId=window.workbenchReportJob;
  if(mode!=='live'||!jobId){toast('Load a live terminal report before previewing a bundle');return;}
  try{
    const bundle=await setupRequest('/v1/jobs/'+encodeURIComponent(jobId)+'/bundle');
    const box=$('#reportSummary');box.textContent='Bundle for '+jobId+' · '+bundle.bundle_files+' files · '+(bundle.missing_files?.length||0)+' missing';
    const detail=document.createElement('pre');detail.textContent=(bundle.files||[]).join('\n')+(bundle.missing_files?.length?'\n\nMissing:\n'+bundle.missing_files.join('\n'):'');
    $('#comparisonDetail').hidden=false;$('#comparisonDetail').replaceChildren(detail);toast(bundle.missing_files?.length?'Bundle has missing files':'Bundle contents loaded');
  }catch(e){toast('Bundle preview failed: '+e.message);}
}

function openSignoffReview(){
  const jobId=window.workbenchReportJob;
  if(mode!=='live'||!jobId){toast('Load a live terminal report before signing off');return;}
  setupForm('Record review decision','This receipt is bound to report '+jobId+'. Enter the reviewer who performed this review and record the remaining obligations.', 'Record decision', form=>{
    setupField(form,'Reviewer name','reviewer');
    setupField(form,'Review notes','notes',{type:'textarea',help:'State what was checked, what remains open, and whether this is approval or acknowledgement.'});
    setupField(form,'Decision','approved',{options:[{label:'Approve evidence package',value:'true'},{label:'Keep review required',value:'false'}]});
  }, async data=>{
    const result=await setupRequest('/v1/jobs/'+encodeURIComponent(jobId)+'/signoff',{method:'POST',body:{reviewer:data.get('reviewer'),notes:data.get('notes'),approved:data.get('approved')==='true'}});
    setupDialog.close();$('#reportState').textContent=(result.status==='approved'?'Approved':'Review required')+' · report hash '+result.report_sha256.slice(0,12);$('#reportSummary').textContent='Reviewer '+result.reviewer+' · recorded '+new Date(result.signed_at).toLocaleString();toast('Review receipt recorded against report hash');
  });
}

$('#previewBundle').onclick=previewSelectedBundle;
$('#signoffButton').onclick=openSignoffReview;

function renderSafeEvidenceTab(button){
  const report=window.workbenchReport||{};const evidence=$('#evidenceView');const alternate=$('#alternateView');
  document.querySelectorAll('.tabs button').forEach(item=>item.classList.toggle('active',item===button));
  const showingEvidence=button.dataset.tab==='evidence';
  if(showingEvidence && (mode==='live' || $('#failureHeading').textContent!==demo.failures[0].id)){evidence.hidden=true;alternate.hidden=false;alternate.textContent='No rendered evidence is available for this selection yet.';return;}
  evidence.hidden=!showingEvidence;alternate.hidden=showingEvidence;if(showingEvidence)return;
  alternate.replaceChildren();const title=document.createElement('h3');title.textContent=button.textContent;alternate.append(title);
  const values=[['Result',report.execution?.status||'Not reported'],['Formal result',report.formal?.status||'Not reported'],['Closure items open',report.closure?.open??'Not reported'],['Claim boundary',report.claim_boundary||'Not reported']];
  for(const [label,value] of values){const row=document.createElement('div');row.className='prov-row';const name=document.createElement('span');name.textContent=label;const content=document.createElement('b');content.textContent=String(value);row.append(name,content);alternate.append(row);}
}
document.querySelectorAll('.tabs button').forEach(button=>button.onclick=()=>renderSafeEvidenceTab(button));

async function compareSelectedRuns(){
  const baseline=window.baselineJob,retest=window.retestJob;
  if(mode!=='live'||!baseline||!retest){toast('Approve a repair first, then wait for its retest to finish');return;}
  try{
    const result=await setupRequest('/v1/jobs/'+encodeURIComponent(baseline)+'/compare/'+encodeURIComponent(retest));
    const box=$('#comparisonDetail');box.hidden=false;box.replaceChildren();
    const title=document.createElement('h3');title.textContent=result.metrics?.failure_resolved?'Failure resolved':'Retest did not resolve the baseline failure';box.append(title);
    const text=document.createElement('p');text.textContent=result.metrics?.scope_comparable===false?'Baseline '+baseline+' → retest '+retest+' · INCOMPARABLE SCOPE: failure resolution and coverage delta are withheld.':'Baseline '+baseline+' → retest '+retest+' · coverage change '+(result.metrics?.coverage_delta_percentage_points??'not reported')+' percentage points.';box.append(text);
    const scope=document.createElement('p');scope.textContent=result.claim_boundary||'Comparison scope not reported.';box.append(scope);
    const hashes=document.createElement('pre');hashes.textContent='Baseline report: '+(result.baseline?.report_sha256||'not reported')+'\nRetest report: '+(result.retest?.report_sha256||'not reported');box.append(hashes);
    if(result.metrics?.scope_comparable===false){$('#signoffButton').disabled=true;$('#reportState').textContent='Incomparable retest · signoff blocked';toast('Retest scope is incomparable; signoff blocked');}
    else {$('#reportState').textContent='Comparison loaded · '+(result.comparison_sha256||'hash unavailable').slice(0,12);toast('Baseline and retest comparison loaded');}
  }catch(e){toast('Comparison unavailable: '+e.message);}
}
$('#compareButton').onclick=compareSelectedRuns;

function addRunActions(){
  for(const row of document.querySelectorAll('#jobsWrap tbody tr')){
    if(row.querySelector('.run-action')) continue;
    const status=(row.querySelector('.job-status')?.textContent||'').trim().toLowerCase();
    const id=row.querySelector('.job-select')?.dataset.job;
    if(!id || !['queued','running','failed'].includes(status)) continue;
    const cell=document.createElement('td');cell.className='run-action';
    const action=document.createElement('button');action.className='secondary';action.textContent=status==='failed'?'Retry':'Cancel';action.setAttribute('aria-label',action.textContent+' run '+id.slice(0,10));
    action.onclick=async()=>{
      action.disabled=true;
      try{
        if(status==='failed') await setupRequest('/v1/jobs/'+encodeURIComponent(id)+'/run-async',{method:'POST'});
        else await setupRequest('/v1/jobs/'+encodeURIComponent(id)+'/cancel',{method:'POST'});
        await loadJobs();toast(status==='failed'?'Retry accepted':'Run cancellation requested');
      }catch(e){action.disabled=false;toast('Run action failed: '+e.message);}
    };
    cell.append(action);row.append(cell);
  }
}
const jobsObserver=new MutationObserver(addRunActions);jobsObserver.observe($('#jobsWrap'),{childList:true,subtree:true});addRunActions();

// Polling may fail transiently. Preserve the last rendered table instead of
// replacing a useful run list with an empty error state, and keep a selected
// run addressable after reload.
let lastKnownJobsHTML='';
const jobsStateObserver=new MutationObserver(()=>{
  const wrap=$('#jobsWrap');
  if(wrap.querySelector('table')) lastKnownJobsHTML=wrap.innerHTML;
  else if(lastKnownJobsHTML && /No jobs for this project yet|Could not load/i.test(wrap.textContent||'')){
    wrap.innerHTML=lastKnownJobsHTML;
    const note=document.createElement('p');note.className='help';note.textContent='Showing the last known run list; refresh to retry the service.';wrap.prepend(note);
  }
});
jobsStateObserver.observe($('#jobsWrap'),{childList:true,subtree:true});
document.addEventListener('click',event=>{
  const button=event.target.closest?.('.job-select');if(!button)return;
  const next=new URL(location.href);next.searchParams.set('job',button.dataset.job);history.replaceState({},'',next);
});
let restoredRunAddress=false;
function restoreRunFromAddress(){
  if(restoredRunAddress)return;
  const id=new URLSearchParams(location.search).get('job');if(!id)return;
  const button=document.querySelector('.job-select[data-job="'+CSS.escape(id)+'"]');if(button){restoredRunAddress=true;button.click();}
}
new MutationObserver(restoreRunFromAddress).observe($('#jobsWrap'),{childList:true,subtree:true});
