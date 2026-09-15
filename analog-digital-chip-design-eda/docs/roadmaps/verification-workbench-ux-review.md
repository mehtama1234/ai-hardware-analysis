# Verification Workbench: end-to-end UX review and improvement brief

Date: 2026-09-09. Status: behavioral audit completed; the open-source pilot
vertical slice is implemented and verified through browser, service, worker,
adversarial, and handoff gates. Enterprise production integrations and
representative-user validation remain open.

## Product outcome

A verification engineer should be able to bring in a design, understand what the platform can check, run a reproducible verification task, investigate a failure, review a proposed change, compare its retest, and hand a precise evidence package to a lead. Every transition must preserve project, design revision, run, test, and evidence identity.

The lead should be able to answer: what changed, what is supported by evidence, what remains unresolved, and exactly what am I approving?

The current interface has useful ingredients: recognizable verification language, a visible failure queue, provenance, and review boundaries. But it presents these as a long dashboard rather than a connected working journey. Its appearance currently promises more continuity than its interactions provide.

## Current evidence and scope

Captured the current static application in headless Chromium at 1440 × 1024, plus a 390 × 844 responsive check. Clicked actual controls and recorded DOM state. No live customer service or proprietary tools were used. Live integration findings below come from source inspection and are distinguished from browser observations. No representative-user study or complete accessibility audit was performed. No runtime JavaScript errors occurred in the tested path; this did not mean the workflow succeeded.

Raw observations: [observations.json](../../evidence/verification-workbench/ux-audit/observations.json).

1. **Arrival and orientation — confusing.** [Screenshot](../../evidence/verification-workbench/ux-audit/01-overview.png). Most of the initial viewport is occupied by metrics, pipeline, and readiness before actionable evidence. The demo label sits at the bottom of the rail. A precise twelve-day signoff estimate appears without its basis. Put mode, project revision, and the most useful next action above the fold; make unsupported estimates unavailable.
2. **Select and investigate a failure — misleading.** [Screenshot](../../evidence/verification-workbench/ux-audit/02-selected-failure.png). Selecting `npu_dma_stress_random` changes the heading but retains the accumulator overflow evidence and P0 badge from another failure. A toast says evidence loaded. Source inspection confirms only heading and subheading change. Evidence must switch atomically with selection, or show an explicit missing-evidence state.
3. **Inspect design inputs — blocked.** [Screenshot](../../evidence/verification-workbench/ux-audit/03-collateral.png). Clicking the first artifact leaves the inspector invisible. Rows have uneven widths and cramped hashes. Reports navigation changes its selected styling but does not navigate to a report. Source inspection also shows live setup requires URL artifact IDs and a manually populated localStorage credential. Use selectable versioned artifacts, ordinary setup forms, and actual navigation.
4. **Review a repair — insufficient for approval.** [Screenshot](../../evidence/verification-workbench/ux-audit/04-repair-review.png). Creating a proposal exposes “Approve & run retest,” but no diff is shown. The screen still describes the unrelated accumulator issue. Approval must follow visible, immutable proposed changes and an explicit retest scope.
5. **Review results and sign off — blocked.** [Screenshot](../../evidence/verification-workbench/ux-audit/05-report.png). After loading the demo report, Sign off responds “Load a PoV report first.” Comparison placeholders occupy space without a selected comparison. The current demo cannot complete its advertised review journey.
6. **Use a narrow screen — incomplete.** [Screenshot](../../evidence/verification-workbench/ux-audit/06-mobile.png). Project selection and navigation disappear. The pipeline is clipped horizontally. Provide a compact project/menu control and a readable summary; detailed waveform work can remain desktop oriented.

### Additional source-inspected trust issues

- The dashboard API returns job counts and terminal jobs. The UI looks for different metrics and failures, then substitutes demo values while showing “Live API connected.” Live mode must never fill missing results with example evidence.
- Report rendering substitutes 86% coverage, three closure items, and “Bounded” when fields are missing. Missing, unsupported, failed, and verified are distinct states.
- Repair uses a job from the URL rather than a clearly selected run. Default replacement strings rename an assertion message; that is not evidence of a behavior repair. Preview and approval send different rationale text.
- Report selection takes the first terminal job without ensuring the correct report kind; regression has a separate API endpoint.
- Switching projects refreshes some lists but leaves report and repair state. Selection must invalidate dependent state and ignore responses from an earlier project.
- API content is inserted through HTML strings. Render untrusted names, logs, and diagnosis as text or sanitized structured content.
- Existing frontend tests mainly assert that strings and endpoint names appear in HTML. They do not establish that an engineer can complete the journey.

## Proposed journey

### 1. Enter the workspace and get to a first useful result

Offer “Explore sample project” and “Connect verification service” as explicit modes. Keep mode visible in the header. In connected mode, show service reachability and authorized projects. An offline service produces a recoverable connection state, never a populated example dashboard.

The empty project presents a short setup sequence: add design inputs, review extracted facts, choose a supported check, run. Use file upload or pasted multiline content with validation. Show unsupported inputs alongside supported ones, with a reason and remedy. Preserve completed setup if the user leaves.

The first milestone is a reproducible check with readable evidence. Hardware and commercial EDA licenses are not prerequisites for this open-source journey. Capability labels must reflect what the configured backend actually supports, including procedural checkers and review-only generated artifacts.

### 2. Establish what we are verifying

A Sources view lists immutable versions, content hashes, parsing status, and source references. Selecting an artifact opens its content and extracted interface information. Separate ingestion from interpretation: successful parsing does not mean the specification has been fully understood.

A Plan view links each requirement to its source, proposed check, status, and known limitations. Surface ambiguous timing, missing clocks/resets, and inconsistent signal widths for resolution. Show plan changes as a diff. Label coverage denominators: a percentage needs a named population and scope.

### 3. Configure and execute a check

“New run” opens a form with design version, testbench/checker, supported backend, seed or proof bound, and resource/time limits where supported. Populate selections from project artifacts; never require editing URL IDs. Before submission, summarize exactly what will run and what it can establish.

After submission, open the durable run detail. Show queued, preparing, compiling, executing, collecting evidence, and terminal outcomes only when supported by events. Distinguish tool failure from design failure. A compile error should offer its first useful diagnostic and source location. Queue delays should explain worker status when known.

Retry must say whether it reproduces identical inputs or creates a revised run. Preserve the original. Offer cancellation only in supported states and explain unavailable actions inline. Reconnect and reload should recover the same run, not reset the workflow.

### 4. Investigate one failure without losing context

Make the primary working screen a three-pane workspace:

- Left: filterable failure groups, affected tests/seeds, status, owner where supported, and selection.
- Center: selected failure, observed versus expected behavior, source/log/waveform tabs, and a synchronized time or cycle cursor when data supports it.
- Right: evidence-supported hypotheses, counterevidence, missing information, and the next useful action.

Use independently resizable panes and preserve selections in deep links. Open cited sources at the relevant line and version. If a waveform cannot be decoded, offer the actual file and state the limitation; do not draw a decorative line and call it waveform evidence.

AI findings should distinguish observations, hypotheses, and suggested experiments. Each factual claim needs an accessible evidence reference. Avoid an unexplained confidence decimal. Present why a hypothesis is plausible, what contradicts it, and which next check would distinguish competing explanations. Users should be able to reject or revise a hypothesis without destroying run evidence.

### 5. Review a change and retest it

A proposal is a separate review object attached to the baseline run and exact source version. Display the actual diff, rationale, affected requirements/checks, and planned retest. Allow reject, edit, or approve; editing invalidates the prior approval.

Approval must reference the same proposal content the user viewed. If the design changed, require a fresh review. Launch a retest with visible lineage and immediately open its run. Preserve a failed retest as useful evidence and offer the next investigation step.

For generated checkers, explicitly show specification grounding and untested assumptions. A checker derived from implementation details can reproduce the implementation's mistake. Procedural execution and bounded formal evidence must retain their actual scope.

### 6. Decide what the retest established

Compare a selected baseline and retest side by side: design/checker versions, inputs, failure signatures, scope, results, and available coverage. Explain changed conditions that make a comparison inconclusive. A pass with fewer checks is not automatically an improvement.

Distinguish original failure resolved, still failing, new failure, tool error, and inconclusive. Show coverage deltas only for comparable denominators and kinds. Keep remaining obligations visible; do not treat one passing retest as project closure.

### 7. Handoff and signoff

The report should be a readable argument: scope, changes, completed checks, findings, unresolved obligations, limitations, and evidence inventory. Reviewer actions need the actual report content, report identity/hash, and a usable bundle preview.

Distinguish acknowledging evidence from accepting closure; show the chosen decision and reviewer notes. Never invent reviewer identity. Persist the receipt with the exact report revision. A subsequent run creates new evidence and does not inherit the previous approval. Downloads should expose availability and missing files before claiming completeness.

## Cross-cutting interaction rules

- One primary action per working state; secondary actions remain available without competing for attention.
- Keep project, revision, run, mode, and evidence freshness visible near decisions.
- Use dedicated Overview, Sources & Plan, Runs, Investigation, and Reports destinations. Preserve browser back/forward, filters, and selected run.
- Keep project summaries compact. Move operational detail into the relevant task; avoid repeating the same readiness facts in cards, pipeline, and status tiles.
- Render readable code and aligned tables. Hashes can be truncated visually with copy/full-value access; source and test names need useful wrapping.
- Use persistent inline error messages for failed actions. Toasts may acknowledge success but must not carry the only explanation or recovery control.
- Preserve data during refresh, label stale content, and avoid replacing focused controls on polling.
- Keyboard users need visible focus, labeled inputs, meaningful tab relationships, and focus restoration after dialogs. Verify these behaviorally. Color must not be the only status cue.

## Implementation order and exit evidence

**First: repair trust and continuity.** Separate demo/live data; bind all evidence and mutations to selected identities; clear stale state; remove unsupported metric defaults; make navigation and artifact selection work; replace HTML injection. Exit: switching between distinct failures/projects never displays or acts on another selection's evidence, including delayed responses and connection errors.

**Second: complete one vertical journey.** Build connection/upload/run forms, the investigation workspace, a real proposal diff, linked retest, report preview, and a working review receipt. Exit: from a clean browser session, complete the open-source simulation/procedural-checker path without URL surgery, developer tools, or an operator explaining hidden prerequisites.

**Third: expand and harden.** Add capability-specific formal/regression experiences, comparative coverage, accessible responsive behavior, and failure recovery. Exit: unsupported, empty, expired-auth, interrupted-worker, stale-artifact, missing-waveform, and inconclusive-result scenarios each have an honest state and usable next step.

Do not declare commercial readiness from screenshots or a single successful demonstration.

## Adversarial LLM evaluation

Use the model as a skeptical verification engineer, a lead reviewing closure, and a first-time pilot user in separate evaluations. Supply the task, screenshots, DOM/action trace, API responses, and immutable artifact identities. Ask it to identify unsupported claims, misleading controls, missing prerequisites, wrong-evidence transitions, and approval actions whose effects cannot be inspected.

Require every finding to contain a reproducible action sequence, expected versus observed behavior, evidence reference, severity, and proposed acceptance test. Include traps: a passing run with missing evidence, a P1 failure beside a P0 failure, changed RTL after proposal creation, narrower retest scope, an API outage, and a formal timeout.

The judge's findings are hypotheses until reproduced. A favorable model score cannot override a failed browser assertion, missing artifact, or contradictory backend result. Keep deterministic browser checks for identity binding, state transitions, exact proposal approval, report selection, and authorization errors. Assess diagnosis correctness separately from interface usability.

## Measuring whether the experience improved

Record a baseline before setting speed-reduction claims. Measure unassisted completion rate, time to first valid run, time to locate the evidence supporting a failure, wrong-run actions, time to understand/reject a proposal, successful recovery after interruption, and reviewer time to identify remaining obligations. Track review quality as well as speed.

Proposed release gates: zero cross-project/wrong-run evidence actions in the adversarial suite; every consequential approval backed by inspectable content; no example values presented as live measurements; the main journey completes after a fresh session and after reload; all critical browser scenarios pass. Validate task clarity with representative engineers before claiming usability gains.
