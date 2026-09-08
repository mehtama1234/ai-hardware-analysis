"""Render scoped executable evidence; stale reports never become current results."""
import hashlib
import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.run_advanced_evidence_regression import REPO, REPORT, tasks, check_source_hashes, test_source_hashes


def esc(value):
    return html.escape(str(value), quote=True)


def checkpoint_current(report):
    if report.get("test_sources_unchanged_during_run") is not True:
        return False
    if report.get("test_source_sha256") != test_source_hashes():
        return False
    if {step.get("name") for step in report.get("steps", [])} != {name for name, _, _ in tasks()}:
        return False
    runner = ROOT / "scripts/run_advanced_evidence_regression.py"
    if report.get("runner_source_sha256") != hashlib.sha256(runner.read_bytes()).hexdigest():
        return False
    expected_artifacts = {name: artifact for name, _, artifact in tasks()}
    for step in report.get("steps", []):
        if step.get("artifact") != expected_artifacts[step["name"]]:
            return False
        if "artifact" in step:
            path = (REPO / step["artifact"]).resolve()
            if not path.is_relative_to(REPO) or not path.is_file() or \
                hashlib.sha256(path.read_bytes()).hexdigest() != step.get("artifact_sha256"):
                return False
            try:
                if check_source_hashes(json.loads(path.read_text())):
                    return False
            except (OSError, ValueError):
                return False
    return True


def render_experiment(name, relative, report, errors):
    link = "../../" + relative
    title = f'<h2>{esc(name)}</h2><p><a href="{esc(link)}">Raw JSON evidence</a></p>'
    if errors:
        return title + '<p class="warn">Not current: ' + esc("; ".join(errors)) + '</p>'
    status = report.get("status", report.get("correctness", {}).get("status", "recorded experiment"))
    parts = [title, f'<p>Reported status: {esc(status)}. Source hashes match.</p>']
    for key in ("scope", "boundary", "memory_scope", "timing_scope", "acceptance_scope", "limitations"):
        if key in report:
            parts.append(f'<p><strong>{esc(key)}:</strong> {esc(report[key])}</p>')
    scalars = {key: value for key, value in report.items()
               if isinstance(value, (int, float, bool)) and key not in {"cpu_threads"}}
    if scalars:
        parts.append('<dl>' + ''.join(f'<dt>{esc(k)}</dt><dd>{esc(v)}</dd>' for k, v in scalars.items()) + '</dl>')
    rows = report.get("rows", [])
    keys = ("name", "backend", "implementation", "sequence", "sequence_length", "evidence_kind",
            "accuracy", "tensor_storage_bytes", "saved_logical_bytes", "median_seconds",
            "packed_tensor_storage_bytes", "fp32_weight_storage_bytes", "output_relative_l2_error",
            "client_concurrency", "requests", "median_request_seconds",
            "p95_request_seconds_nearest_rank", "completed_output_tokens_per_second", "correct")
    present = [key for key in keys if any(key in row for row in rows)]
    if present:
        parts.append('<table><tr>' + ''.join(f'<th>{esc(key)}</th>' for key in present) + '</tr>')
        for row in rows:
            parts.append('<tr>' + ''.join(f'<td>{esc(row.get(key, "—"))}</td>' for key in present) + '</tr>')
        parts.append('</table>')
    parts.append('<details><summary>Experiment protocol and full report</summary><pre>' +
                 esc(json.dumps(report, indent=2)) + '</pre></details>')
    return ''.join(parts)


def build_page():
    checkpoint = json.loads(REPORT.read_text()) if REPORT.exists() else {}
    current = checkpoint_current(checkpoint)
    parts = ['<!doctype html><meta charset="utf-8"><title>Advanced executable evidence</title>',
        '<style>body{font:16px/1.6 system-ui;max-width:1100px;margin:2rem auto;padding:0 1rem}table{border-collapse:collapse;display:block;overflow:auto}td,th{border:1px solid #bbb;padding:.4rem;text-align:left}pre{white-space:pre-wrap;overflow-wrap:anywhere}.warn{background:#fff0ca;padding:1rem}h2{margin-top:3rem}</style>',
        '<nav><a href="index.html">Curriculum index</a> · <a href="../advanced-lab-phase/EXECUTABLE-CHECKPOINT.md">Walkthrough</a> · <a href="../advanced-lab-phase/REMAINING-WORK.md">Remaining work</a></nav>',
        '<h1>Advanced executable evidence</h1>',
        '<p>CPU experiments, analytical models and unavailable GPU paths are distinct. No full-goal completion is asserted.</p>',
        '<p class="warn">Checkpoint: ' + esc(checkpoint.get("status", "missing") if current else "stale or incomplete—rerun the checkpoint") + '</p>',
        '<pre>python3 gpu-mode-curriculum/scripts/run_advanced_evidence_regression.py\npython3 gpu-mode-curriculum/scripts/build_executable_evidence_page.py</pre>']
    for name, _, relative in tasks():
        if relative is None:
            continue
        path = REPO / relative
        try:
            report = json.loads(path.read_text())
            errors = check_source_hashes(report)
        except (OSError, ValueError) as exc:
            report, errors = {}, [str(exc)]
        parts.append(render_experiment(name, relative, report, errors))
    output = ROOT / "site/advanced-executable-evidence.html"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text('\n'.join(parts) + '\n')
    print("wrote", output, "checkpoint_current", current)


if __name__ == "__main__":
    build_page()
