# Verification platform primitives

This package is the first implementation slice of the evidence-backed AI verification platform. It is deterministic infrastructure for agent proposals; it does not make an LLM claim or mark closure without tool evidence.

The main entry points are:

- `ingest_markdown()` — parse explicit `REQ-ID: text` requirements and hash the source;
- `plan_ir()` and `write_sva_module()` — produce conservative, traceable SVA plans and source;
- `run_pipeline()` — persist ingestion, planning, generation, and tool execution in one run root;
- `run_command()` — execute a tool without a shell and record logs, status, and artifact hashes;
- `parse_failure()`, `signal_values()`, and `dependency_cone()` — extract focused debug evidence;
- `evaluate_closure()` and `build_pov_report()` — enforce evidence gates and summarize pilot metrics;
- `yosys_sat_prove()` — run bounded SAT invariants; and
- `authorize()` / `apply_to_copy()` — require human approval for intent-changing repairs.

The seeded executable example is in `../benchmarks/seeded_counter`. It intentionally fails, which verifies that the platform preserves failure evidence instead of reporting a false pass.
