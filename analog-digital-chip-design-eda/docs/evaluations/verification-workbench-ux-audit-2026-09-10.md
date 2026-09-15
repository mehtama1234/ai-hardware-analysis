# Verification Workbench UX audit

## Step 1 — Connected project failure recovery

Screenshot: `.artifacts/workbench-browser/live-unavailable.png`

Health: **pass after fix**.

The page makes the blocked state clear (`Project unavailable`, `401`, and
`no sample fallback`), keeps the next action visible, disables live metrics,
and leaves the run list empty. The breadcrumb now shows the requested project
(`missing`) instead of the sample project, so project identity remains
consistent across the header and context strip.

Accessibility observed: the mobile navigation remains visible, form controls
retain labels, and the context strip exposes project, run, evidence, and next
action as readable text. Screenshot review cannot establish full keyboard,
screen-reader, or contrast compliance; those remain covered by browser and
manual accessibility checks.

The screenshot represents the unauthorized live-project recovery state. It
does not prove enterprise identity/RBAC, managed observability, or customer
adapter behavior.

## Step 2 — Connected project with no collateral

Screenshot: `.artifacts/workbench-browser/handoff-signed.png`

Health: **pass after fix**.

The empty project state identifies the setup requirement (`upload RTL`), keeps
the run list and evidence pane honest, and visually de-emphasizes the disabled
`Run verification` action. This prevents an engineer from interpreting an
available button as permission to execute an unconfigured run.

The screenshot does not establish whether a real customer adapter is
available; that state is supplied by the connected setup contract.
