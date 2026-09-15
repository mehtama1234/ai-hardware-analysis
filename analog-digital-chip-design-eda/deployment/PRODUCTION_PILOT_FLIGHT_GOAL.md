# Production Pilot Flight

## Meaty end-to-end goal

Turn the certified provider-free verification workbench into a deployable customer-pilot service. A clean checkout must build one pinned image, start the API and worker with persistent state, onboard isolated synthetic tenants, execute the verification workflow through the deployed HTTP surface, survive service restart and evidence restoration, and produce a signed, content-addressed pilot handoff.

The flight covers collateral upload and digesting, typed planning, generated review artifacts, simulation/lint/formal-preflight execution, failure triage, repair approval, matched retest, scorecard generation, browser/API/CLI parity, tenant isolation, credential and adapter boundaries, queue behavior, observability, backup/restore, and archive replay. Commercial EDA tools and silicon are not prerequisites; unavailable adapters remain explicit blocked states.

## Definition of done

One command must:

1. validate Compose and Kubernetes deployment contracts and build the release image;
2. start API, worker, and persistent evidence services;
3. provision two isolated synthetic tenants and upload realistic collateral;
4. execute baseline, failure, triage, approved repair, retest, and scorecard workflows through the deployed API;
5. exercise timeout, malformed collateral, unavailable adapter, stale digest, cross-tenant, and invalid-credential paths;
6. restart the stack and prove job, artifact, approval, and evidence continuity;
7. verify browser, REST, and CLI acceptance plus health, queue, audit, and observability outputs;
8. create a signed pilot packet with immutable evidence and claim boundaries; and
9. export and replay the release in a clean temporary environment.

The result is a deployable reference pilot, not enterprise production sign-off, exhaustive coverage, formal completeness, silicon qualification, or measured customer ROI.

## First implementation slice

Start with deployment preflight and a local image/runtime smoke test. The existing customer-certification runner remains the workflow oracle; this goal adds the deployed execution boundary, persistent runtime checks, and recovery evidence around it.

The first slice is now exercised with `docker build -f deployment/Dockerfile -t verification-pilot:0.2.0-local .`, `python3 scripts/preflight_verification_deployment.py --render`, and `python3 scripts/verify_verification_image_runtime.py verification-pilot:0.2.0-local`. The current image is verified live and ready as UID 10001. Namespace sandbox probing remains a separate runtime gate because the default Docker invocation does not grant those capabilities; the host `verify_execution_sandbox_runtime.py` probe passes.

The local Compose flight has also been exercised with project `pilot-flight`: API and worker start together, `/readyz` passes, a project and specification are created through the authenticated REST API, and the project remains readable after a full Compose restart. Evidence is recorded in `.artifacts/production-pilot-flight-runtime.json`.

The deployed workflow runner is `python3 scripts/run_production_pilot_flight.py`. It starts the stack, creates a tenant and RTL/testbench collateral through REST, submits a worker simulation, waits for passing terminal evidence, restarts Compose, verifies project and job continuity, writes `.artifacts/production-pilot-flight.json`, and tears down the temporary stack.

The runner now also creates a second isolated tenant, executes a failing simulation baseline and approved repair/retest through the API, rejects a stale proposal digest, and verifies invalid-credential and cross-tenant artifact requests. The latest receipt records a passed retest and preserved state after restart.

`python3 scripts/build_production_pilot_packet.py` binds the deployed flight, scorecard, adversarial gate, archive replay, and commercial manifest into `.artifacts/production-pilot-packet.json` with a canonical packet digest for customer handoff.
