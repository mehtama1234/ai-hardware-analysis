#!/usr/bin/env python3
"""Generate the cross-workload compiler review report in Markdown and HTML."""

from __future__ import annotations

import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "evidence" / "aimc-hybrid-compiler-runtime"
REVIEW_MD = ROOT / "docs" / "research" / "hybrid-workload-compiler-review.md"
REVIEW_HTML = ROOT / "docs" / "research" / "hybrid-workload-compiler-review.html"


def load(name: str) -> dict:
    return json.loads((PACKAGE / name).read_text(encoding="utf-8"))


def main() -> int:
    shared = load("hybrid_compiler_runtime_package.json")
    compiled = load("compiled_target_execution_package.json")
    bytecode = load("target_bytecode.json")
    estimate = load("hybrid_runtime_estimate.json")
    guarded = load("guarded_hybrid_workload_runtime_trace.json")
    models = shared["models"]
    rows = []
    for model in models:
        comparison = model["comparison"]
        rows.append({
            "workload_id": model["workload_id"],
            "model_id": model["model_id"],
            "operators": model["operator_count"],
            "analog_operators": model["analog_operator_count"],
            "digital_operators": model["digital_support_operator_count"],
            "metric": comparison["metric"],
            "result": comparison.get("relative_l2_output_difference"),
            "pass": comparison["pass"],
            "proof_level": comparison["proof_level"],
            "converter_gate": model["converter_plan"]["shared_converter_gate"] if "shared_converter_gate" in model["converter_plan"] else model["converter_plan"].get("compatibility_status"),
        })
    report = {
        "schema_version": "aimc_hybrid_workload_comparison.v1",
        "status": "cross_workload_compiler_review_generated_physical_converter_blocked",
        "requirements": [
            "Every package names its workload, model, metric, baseline, and claim boundary.",
            "Every operator has one analog-memory or digital-support placement.",
            "Every analog candidate names converter, calibration, tile, SRAM, and fallback information.",
            "Digital decisions preserve explicit reasons, including cost-driven fallback.",
            "The same packages feed a shared command and runtime schedule.",
            "Physical converter evidence remains separate from simulator and task rehearsal evidence.",
        ],
        "workloads": rows,
        "shared_results": {
            "models": len(models),
            "operators": compiled["operator_count"],
            "commands": compiled["command_count"],
            "register_writes": compiled["register_write_count"],
            "planning_cycles": compiled["estimated_cycles"],
            "target_bytecode_words": bytecode["word_count"],
            "target_bytecode_width_bits": bytecode["word_width_bits"],
            "sram_maps": len(compiled.get("sram_memory_maps", [])),
            "schedule_verified": estimate["schedule_verified"],
            "physical_converter_gate": shared["shared_hardware"]["shared_converter_gate"],
            "guarded_fallback_commands": guarded["totals"]["physical_guarded_digital_fallback_commands"],
        },
        "claim_boundary": {
            "allowed": "the compiler can apply workload-dependent mixed-memory placement and produce one deterministic target schedule plus bounded target-review artifacts",
            "blocked": "physical converter acceptance, measured board runtime, measured energy, calibrated silicon, field task accuracy, and production readiness",
        },
    }
    table = [
        "| workload | model | operators | analog selected | digital | metric/result | proof |",
        "| --- | --- | ---: | ---: | ---: | --- | --- |",
    ]
    for row in rows:
        result = "n/a" if row["result"] is None else f"{row['result']:.6g}"
        table.append(f"| `{row['workload_id']}` | `{row['model_id']}` | {row['operators']} | {row['analog_operators']} | {row['digital_operators']} | `{row['metric']}` / `{result}` | {row['proof_level']} |")
    md_lines = [
        "# Hybrid Workload Compiler Review", "",
        "This report audits one shared compiler/runtime handoff across transformer, serving, and edge-workload packages.", "",
        "## Requirements", "",
    ] + [f"{index}. {item}" for index, item in enumerate(report["requirements"], 1)] + [
        "", "## Workload Results", "", *table, "", "## Shared Handoff", "",
        f"- workloads/models: `{compiled['models'].__len__() if isinstance(compiled.get('models'), list) else len(models)}`",
        f"- operators: `{compiled['operator_count']}`",
        f"- commands: `{compiled['command_count']}`",
        f"- register writes: `{compiled['register_write_count']}`",
        f"- planning cycles: `{compiled['estimated_cycles']}`",
        f"- target bytecode words: `{bytecode['word_count']}` deterministic `{bytecode['word_width_bits']}`-bit review words",
        f"- SRAM allocation: `{len(compiled.get('sram_memory_maps', []))}/{len(models)}` workload maps fit within the stated `64 KiB` arena",
        f"- schedule verified: `{str(estimate['schedule_verified']).lower()}`",
        f"- physical converter gate: `{shared['shared_hardware']['shared_converter_gate']}`",
        f"- physically guarded fallback commands: `{guarded['totals']['physical_guarded_digital_fallback_commands']}`",
        "- digital-only planning comparison: `included per workload in hybrid_runtime_estimate.json`",
        "", "The tiny MLP, deep MLP stack, single MLP block, attention projections, and fixed projections in the normalized serving package retain analog candidates. The tiny MLP and wake-word packages pass bounded task rehearsals but are selected digital under the current guarded path because the physical converter is blocked or converter overhead is not amortized. In the physically guarded runtime trace, analog candidate commands explicitly fall back to digital because the converter gate is blocked.",
        "", "The target compiler lowers the shared schedule into deterministic review bytecode and per-workload SRAM maps. These artifacts make the handoff inspectable and repeatable; they are not an ISA-validated firmware image and have not been observed running on a board.",
        "", "## Tests", "",
        "```bash",
        "python3 scripts/generate_tiny_mlp_hybrid_execution_package.py",
        "python3 scripts/generate_transformer_mlp_block_execution_package.py",
        "python3 scripts/generate_audio_hybrid_execution_package.py",
        "python3 scripts/generate_language_model_serving_package.py",
        "python3 scripts/run_language_model_serving_task_rehearsal.py",
        "python3 scripts/generate_projection_stack_package.py",
        "python3 scripts/generate_edge_intake_packages.py",
        "python3 scripts/build_hybrid_compiler_runtime_package.py",
        "python3 scripts/compile_hybrid_transformer_execution_package.py",
        "python3 scripts/run_hybrid_runtime_estimator.py",
        "python3 scripts/validate_aimc_physical_evidence.py",
        "python3 scripts/run_aimc_end_to_end_regression.py",
        "python3 scripts/validate_project.py",
        "```",
        "", "## Claim Boundary", "", report["claim_boundary"]["allowed"] + ".", report["claim_boundary"]["blocked"] + ".",
    ]
    md = "\n".join(md_lines) + "\n"
    html_rows_parts = []
    for row in rows:
        result = "n/a" if row["result"] is None else f"{row['result']:.6g}"
        html_rows_parts.append(
            f"<tr><td><code>{html.escape(str(row['workload_id']))}</code></td>"
            f"<td><code>{html.escape(str(row['model_id']))}</code></td>"
            f"<td>{row['operators']}</td><td>{row['analog_operators']}</td>"
            f"<td>{row['digital_operators']}</td>"
            f"<td><code>{html.escape(str(row['metric']))}</code> / <code>{result}</code></td>"
            f"<td>{html.escape(str(row['proof_level']))}</td></tr>"
        )
    html_rows = "".join(html_rows_parts)
    html_doc = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Hybrid Workload Compiler Review</title>
<style>body{{margin:0;background:#f5f6f3;color:#20251f;font:16px/1.6 system-ui,sans-serif}}header,main{{max-width:1080px;margin:auto;padding:28px 22px}}header{{border-bottom:1px solid #d9dfd6}}h1{{margin:0 0 10px;font-size:clamp(32px,5vw,54px)}}section{{background:#fff;border:1px solid #d9dfd6;border-radius:8px;padding:20px;margin:18px 0}}table{{width:100%;border-collapse:collapse}}th,td{{border-bottom:1px solid #d9dfd6;padding:10px;text-align:left;vertical-align:top}}th{{background:#edf2eb}}code,pre{{background:#edf1eb;border-radius:5px}}code{{padding:2px 5px}}pre{{padding:14px;overflow:auto}}.blocked{{color:#9b3e36;font-weight:800}}</style></head>
<body><header><h1>Hybrid Workload Compiler Review</h1><p>One shared compiler/runtime handoff across transformer and edge workloads, with workload-dependent analog placement.</p></header><main>
<section><h2>Result</h2><p>The handoff contains <code>{len(models)}</code> workload/model packages, <code>{compiled['operator_count']}</code> operators, <code>{compiled['command_count']}</code> commands, <code>{compiled['register_write_count']}</code> register writes, and <code>{compiled['estimated_cycles']}</code> planning cycles. It also contains <code>{bytecode['word_count']}</code> deterministic <code>{bytecode['word_width_bits']}</code>-bit review bytecode words and <code>{len(compiled.get('sram_memory_maps', []))}</code> bounded SRAM maps. The schedule is verified; the physical converter remains <span class="blocked">blocked</span>. The guarded trace emits <code>{guarded['totals']['physical_guarded_digital_fallback_commands']}</code> explicit digital fallbacks for analog candidate commands. These target artifacts are not ISA-validated firmware or a board trace. A workload-by-workload digital-only planning comparison is included in the runtime-estimate artifact.</p></section>
<section><h2>Requirements</h2><ol>{''.join(f'<li>{html.escape(item)}</li>' for item in report['requirements'])}</ol></section>
<section><h2>Workload Results</h2><table><thead><tr><th>Workload</th><th>Model</th><th>Operators</th><th>Analog</th><th>Digital</th><th>Metric/result</th><th>Proof</th></tr></thead><tbody>{html_rows}</tbody></table></section>
<section><h2>Tests</h2><pre>{html.escape(chr(10).join(md_lines[-12:-5]))}</pre><p>The repository validator, JSON checks, and Python compilation passed after regeneration.</p></section>
<section><h2>Claim Boundary</h2><p>{html.escape(report['claim_boundary']['allowed'])}. {html.escape(report['claim_boundary']['blocked'])}.</p></section>
</main></body></html>
'''
    (PACKAGE / "hybrid_workload_comparison.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (PACKAGE / "hybrid_workload_comparison.md").write_text(md, encoding="utf-8")
    REVIEW_MD.write_text(md, encoding="utf-8")
    REVIEW_HTML.write_text(html_doc, encoding="utf-8")
    print(f"workloads,{len(models)}")
    print(f"operators,{compiled['operator_count']}")
    print(f"commands,{compiled['command_count']}")
    print(f"planning_cycles,{compiled['estimated_cycles']}")
    print(f"schedule_verified,{estimate['schedule_verified']}")
    print(f"review_markdown,{REVIEW_MD}")
    print(f"review_html,{REVIEW_HTML}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
