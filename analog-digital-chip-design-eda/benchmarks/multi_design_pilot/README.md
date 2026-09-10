# Multi-design open-source verification pilot

Run the complete baseline, diagnosis, approved isolated repair/retest, and
aggregate PoV report with:

```bash
python3 benchmarks/multi_design_pilot/run_pilot.py
python3 benchmarks/multi_design_pilot/validate_pilot.py
```

CI can use the same contract through `python3
benchmarks/multi_design_pilot/ci_gate.py`; the checked-in workflow installs
Icarus, Verilator, and Yosys before running the pilot and its tests.

The pilot covers `seeded_counter`, `seeded_fifo`, `seeded_regblock`, and the
hierarchical `register_peripheral`. It
uses Icarus/VVP through `verification_platform.simulation`, emits typed
planning and generated-check artifacts, and writes separate evidence roots for
each baseline and retest. The validator copies those roots to a temporary
clean checkout and verifies all content hashes.

The expected baseline result is four intentionally classified failures. The
expected retest result is four passing runs after explicit human-approved
repairs. A baseline failure is an expected benchmark outcome; the command
returns success when the expected failure and retest gates are both present.

The summary also reports planned versus unplanned requirements, unique failure
signatures, adapter runtime, baseline/retest functional-check coverage, repair
success, source preservation, and artifact-integrity metrics.

The CI gate also writes `pilot-release-manifest.json`, which identifies the
five benchmark designs, commands, evidence contract, open-source backend
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
