# Customer EDA adapter guide

The pilot's open-source tools are reference backends. Customer deployments can
add licensed simulators, formal engines, regression schedulers, or artifact
packagers behind the same adapter contract without changing the workbench.

## Adapter contract

Implement an adapter with a stable name, executable, argument list, timeout,
and expected output paths. Use `verification_platform.adapter.AdapterSpec` and
`execute_adapter` so every invocation produces the common `ToolRun` record:

```python
from verification_platform.adapter import AdapterSpec, execute_adapter

spec = AdapterSpec(
    name="customer-simulator",
    executable="customer-sim",
    expected_artifacts=("simulation/waveform.vcd", "simulation/result.json"),
)
run = execute_adapter(
    spec,
    ["--batch", "--test", "smoke"],
    run_root=job_root,
    source_revision=rtl_sha256,
    timeout_seconds=1800,
)
```

Adapters must run in the job workspace, return a nonzero result for tool or
test failure, preserve stdout/stderr within the runner's 2 MiB per-stream
bound (with truncation metadata), and never claim missing expected
artifacts as a pass. Formal adapters must also record the solver result,
bound/engine settings, and counterexample path when one exists. Regression
adapters must retain each test identity and aggregate status without dropping
individual failures.
Expected artifact paths must be relative to the supplied job workspace; the
adapter runner rejects absolute paths and traversal (`../`) before launching a
tool.
Command arguments are persisted in provenance after redacting recognized
secret flags (`--token`, `--password`, `--api-key`, `--license-key`, and
`KEY=value` forms); pass credentials through a secret manager whenever
possible.

## Registration and acceptance

1. Register the adapter identity and bounded output contract at deployment
   with `VERIFICATION_EDA_ADAPTERS='[{"name":"customer-sim","kind":"simulation","executable":"customer-sim","version":"2026.1","expected_artifacts":["simulation/waveform.vcd","simulation/result.json"],"timeout_seconds":1800}]'`.
   The `/v1/capabilities` response reports each registered adapter as
   `available` or `blocked`; malformed configuration makes capabilities
   unavailable instead of silently hiding a tool.
2. Register the executable and required environment in the deployment image or
   isolated worker profile.
3. Run `python3 scripts/preflight_registered_adapters.py --output adapters-preflight.json` and retain its digest-bound available/blocked result.
4. Add a capability entry so unavailable tools are reported as `blocked`, not
   silently treated as passing.
5. Add a fixture job with known pass, fail, timeout, and missing-artifact cases.
6. Submit a `customer-adapter` job with `adapter_name` and a list-valued
   `adapter_args`; unavailable registrations are rejected before queueing.
7. Verify the evidence endpoint contains source revision, tool identity,
   command metadata, bounded logs, expected artifacts, and durable events.
8. Request `/v1/jobs/{id}/proof-of-value` to produce the self-digested
   adapter report, then use the existing signoff route; blocked executions are
   not eligible for signoff.
9. Run the workbench handoff and signoff flow; customer-specific claims remain
   review-only until a human approves the resulting evidence package.

Do not put license keys in the repository or job payload. Mount them through a
secret manager and record only the adapter name and non-secret engine version
in evidence.
