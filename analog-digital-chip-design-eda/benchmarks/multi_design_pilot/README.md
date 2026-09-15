# Multi-design open-source verification pilot

Run the complete baseline, diagnosis, approved isolated repair/retest, and
aggregate PoV report with:

```bash
python3 benchmarks/multi_design_pilot/run_pilot.py
python3 benchmarks/multi_design_pilot/validate_pilot.py
# one-command closure-lab gate
python3 scripts/run_closure_lab.py
```

CI can use the same contract through `python3
benchmarks/multi_design_pilot/ci_gate.py`; the checked-in workflow installs
Icarus, Verilator, and Yosys before running the pilot and its tests.

The pilot covers `seeded_counter`, `seeded_fifo`, `seeded_regblock`, the
hierarchical `register_peripheral`, `seeded_handshake`, and `seeded_arbiter`. It
uses Icarus/VVP through `verification_platform.simulation`, emits typed
planning and generated-check artifacts, and writes separate evidence roots for
each baseline and retest. The validator copies those roots to a temporary
clean checkout and verifies all content hashes.

The expected baseline result is eleven intentionally classified failures. The
expected retest result is eleven passing runs after explicit human-approved
repairs. A baseline failure is an expected benchmark outcome; the command
returns success when the expected failure and retest gates are both present.

The release contract is deterministic: the pilot must report eleven designs,
eleven failed baselines, eleven passing retests, unchanged original sources, and
valid artifact, session, summary, and release digests. `validate_pilot.py`
copies the complete benchmark bundle to a temporary clean root before checking
those hashes, so validation does not depend on the source checkout's generated
files being trusted in place.

The summary also reports planned versus unplanned requirements, unique failure
signatures, adapter runtime, baseline/retest functional-check coverage, repair
success, source preservation, artifact-integrity metrics, and the count of
reviewable deterministic-reference agent proposals. Every failed baseline
produces `runs/latest/reference-agent-proposal.json`; the proposal is evidence
bound and remains review-required until a human and deterministic retest gate
close the loop.

`fault-taxonomy.json` records the intended failure class for every design. The
clean-checkout validator requires all eleven design IDs and eleven distinct
classes, preventing a release from inflating its count with duplicate fixtures.
Each baseline/retest pair also carries a scope ID derived from `spec.md` and
`tb.sv`; changing the retest scope causes validation to fail.

Every baseline also produces `runs/latest/next-test-proposal.json`. This is
the closure-lab handoff from measured coverage gaps to a bounded executable
test plan. It is source- and evidence-bound, requires human review, and does
not claim closure until an identical-scope retest creates new artifacts.

The CI gate also writes `pilot-release-manifest.json`, which identifies the
eleven benchmark designs, commands, evidence contract, open-source backend
policy, and the fact that this pilot requires no physical hardware.

The local service can be started from the repository root with:

```bash
uvicorn deployment.verification_service:app --host 0.0.0.0 --port 8080
```

Container deployment is defined in `deployment/Dockerfile`; `/healthz` and
`/readyz` provide orchestration probes.

Set `VERIFICATION_SERVICE_API_KEY` in a deployed environment to require the
same value in the `X-API-Key` header for job and evidence requests.

For a local container deployment, copy `deployment/.env.example` to
`deployment/.env`, set a secret, and run `docker compose -f
deployment/docker-compose.yml up --build`. Job artifacts persist in the
`verification-pilot-artifacts` volume; the container filesystem is read-only
apart from that volume and `/tmp`.

`customer-adapter-example.json` shows the configuration boundary for replacing
the open-source backends with a customer's simulator, formal engine, and
coverage exporter while preserving expected-artifact, proof-result, and human
approval policies.
