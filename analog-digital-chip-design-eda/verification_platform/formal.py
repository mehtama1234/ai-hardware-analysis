"""Formal-tool adapter primitives."""

from __future__ import annotations

from dataclasses import asdict, replace
from pathlib import Path
import re
from typing import Literal, Sequence
import hashlib
import json

from .ledger import ToolRun
from .runner import run_command
from .rtl import ingest_rtl_ports
from .ledger import ProvenanceLedger
from .triage import Failure


def parse_yosys_sat_result(log: str) -> Literal["proven", "counterexample", "unknown"]:
    """Classify Yosys SAT output using its explicit terminal markers."""
    if "SAT proof finished - no model found" in log:
        return "proven"
    if "SAT proof finished - model found" in log or "FAIL!" in log:
        return "counterexample"
    return "unknown"


def parse_yosys_counterexample(log: str) -> list[dict[str, str | int]]:
    """Extract the compact ``sat -show`` model table from a failed proof.

    Yosys prints one row per time step.  The parser intentionally returns only
    scalar values and preserves the special ``init`` row; unsupported output is
    represented by an empty list rather than being mistaken for a proof.
    """
    if parse_yosys_sat_result(log) != "counterexample":
        return []
    rows: list[dict[str, str | int]] = []
    pattern = re.compile(r"^\s*(init|\d+)\s+\\?([^\s]+)\s+(-?\d+)\s+([0-9a-fA-FxXzZ]+)\s+([01xXzZ]+)\s*$")
    for line in log.splitlines():
        match = pattern.match(line)
        if not match:
            continue
        time_token, signal, decimal, _hex, binary = match.groups()
        rows.append({
            "time": time_token if time_token == "init" else int(time_token),
            "signal": signal,
            "decimal": int(decimal),
            "binary": binary,
        })
    return rows


def counterexample_to_failure(log: str, *, signal: str, expected_value: str) -> Failure | None:
    """Project the first violating shown value into the common failure schema."""
    if not signal or not expected_value:
        raise ValueError("signal and expected_value are required")
    try:
        expected = int(expected_value, 0)
    except ValueError as exc:
        raise ValueError("expected_value must be an integer literal") from exc
    for row in parse_yosys_counterexample(log):
        if row["signal"] != signal or row["time"] == "init":
            continue
        actual = int(row["decimal"])
        if actual != expected:
            return Failure(int(row["time"]), signal, str(expected), str(actual))
    return None


def yosys_syntax_check(
    rtl: str | Path,
    *,
    run_root: str | Path,
    top: str | None = None,
    source_revision: str = "unknown",
    timeout_seconds: float = 60.0,
) -> ToolRun:
    """Run Yosys parsing/elaboration and record it as a distinct formal-stage run."""
    command = ["yosys", "-p", f"read_verilog -sv {Path(rtl)}"]
    if top:
        command[-1] += f"; hierarchy -top {top}"
    return run_command(command, tool="yosys-formal-preflight", run_root=run_root, source_revision=source_revision, timeout_seconds=timeout_seconds)


def yosys_sat_prove(
    rtl: str | Path,
    *,
    top: str,
    signal: str,
    expected_value: str,
    run_root: str | Path,
    sequence: int = 3,
    source_revision: str = "unknown",
    timeout_seconds: float = 60.0,
) -> ToolRun:
    """Run a bounded SAT proof for a simple signal invariant."""
    if sequence < 1 or not top or not signal or not expected_value:
        raise ValueError("top, signal, expected_value, and positive sequence are required")
    script = f"read_verilog -sv {Path(rtl)}; prep -top {top}; sat -seq {sequence} -prove {signal} {expected_value} -show {signal}"
    run = run_command(["yosys", "-p", script], tool="yosys-sat", run_root=run_root, source_revision=source_revision, timeout_seconds=timeout_seconds)
    log_path = Path(run_root) / "stdout.log"
    proof_result = parse_yosys_sat_result(log_path.read_text(encoding="utf-8")) if log_path.is_file() else "unknown"
    run = replace(run, metadata={**run.metadata, "proof_result": proof_result})
    ProvenanceLedger(runs=[run]).write(Path(run_root) / "provenance-ledger.json")
    return run


def run_yosys_signal_reachability(
    rtl: str | Path,
    *,
    top: str,
    signal: str,
    value: str = "1",
    run_root: str | Path,
    sequence: int = 3,
    source_revision: str = "unknown",
    timeout_seconds: float = 60.0,
) -> dict[str, object]:
    """Check bounded reachability of a scalar signal value with Yosys SAT."""
    if not top or not signal or not value or sequence < 1 or not source_revision:
        raise ValueError("top, signal, value, positive sequence, and source_revision are required")
    source = Path(rtl).resolve()
    root = Path(run_root)
    script = f"read_verilog -formal -sv {source}; prep -top {top}; flatten; sat -seq {sequence} -set {signal} {value} -show {signal}"
    run = run_command(["yosys", "-p", script], tool="yosys-signal-reachability", run_root=root, source_revision=source_revision, timeout_seconds=timeout_seconds, run_id="signal-reachability")
    log_path = root / "stdout.log"
    log = log_path.read_text(encoding="utf-8") if log_path.is_file() else ""
    if "SAT solving finished - model found" in log:
        status = "reachable"
    elif "SAT solving finished - no model found" in log:
        status = "unreachable"
    else:
        status = "unknown" if run.status == "passed" else "blocked"
    result: dict[str, object] = {"schema_version": "yosys-signal-reachability-v1", "status": status, "top": top, "signal": signal, "value": value, "sequence": sequence, "source_revision": source_revision, "source": {"path": str(source), "sha256": hashlib.sha256(source.read_bytes()).hexdigest()}, "tool_run": asdict(run), "claim_boundary": "bounded signal-value reachability only; does not establish compound antecedent activity or property correctness"}
    result["result_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    root.mkdir(parents=True, exist_ok=True)
    (root / "signal-reachability-result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def run_yosys_antecedent_reachability(
    rtl: str | Path | Sequence[str | Path],
    *,
    top: str,
    antecedent: str,
    allowed_signals: set[str],
    run_root: str | Path,
    sequence: int = 3,
    source_revision: str = "unknown",
    timeout_seconds: float = 60.0,
) -> dict[str, object]:
    """Check bounded reachability for validated conjunction/disjunction atoms."""
    if not top or not antecedent.strip() or sequence < 1 or not source_revision:
        raise ValueError("top, antecedent, positive sequence, and source_revision are required")
    branches: list[list[tuple[str, str]]] = []
    for branch_text in antecedent.split("||"):
        constraints: list[tuple[str, str]] = []
        for atom in branch_text.split("&&"):
            atom = atom.strip().strip("() ")
            match = re.fullmatch(r"(!)?([A-Za-z_]\w*)(?:\s*==\s*(1'b[01]|[01]))?", atom)
            if not match:
                return {"schema_version": "yosys-antecedent-reachability-v1", "status": "blocked", "antecedent": antecedent, "blocked_reason": "only conjunctions/disjunctions of scalar boolean atoms are supported", "source_revision": source_revision}
            negated, signal, literal = match.groups()
            if signal not in allowed_signals:
                return {"schema_version": "yosys-antecedent-reachability-v1", "status": "blocked", "antecedent": antecedent, "blocked_reason": f"antecedent signal is outside validated scope: {signal}", "source_revision": source_revision}
            constraints.append((signal, literal[-1] if literal else ("0" if negated else "1")))
        branches.append(constraints)
    sources = [Path(rtl).resolve()] if isinstance(rtl, (str, Path)) else [Path(item).resolve() for item in rtl]
    if not sources or any(not source.is_file() for source in sources):
        raise ValueError("all RTL antecedent-reachability sources must exist")
    reads = "; ".join(f"read_verilog -formal -sv {source}" for source in sources)
    root = Path(run_root)
    branch_results: list[dict[str, object]] = []
    for index, constraints in enumerate(branches):
        sets = " ".join(f"-set {signal} {value}" for signal, value in constraints)
        script = f"{reads}; prep -top {top}; flatten; sat -seq {sequence} {sets}"
        run = run_command(["yosys", "-p", script], tool="yosys-antecedent-reachability", run_root=root / f"branch-{index}", source_revision=source_revision, timeout_seconds=timeout_seconds, run_id=f"antecedent-reachability-{index}")
        log_path = root / f"branch-{index}" / "stdout.log"
        log = log_path.read_text(encoding="utf-8") if log_path.is_file() else ""
        branch_status = "reachable" if "SAT solving finished - model found" in log else "unreachable" if "SAT solving finished - no model found" in log else "unknown" if run.status == "passed" else "blocked"
        branch_results.append({"branch": index, "constraints": [{"signal": signal, "value": value} for signal, value in constraints], "status": branch_status, "tool_run": asdict(run)})
    statuses = [str(item["status"]) for item in branch_results]
    status = "reachable" if "reachable" in statuses else "unreachable" if statuses and all(item == "unreachable" for item in statuses) else "unknown" if all(item in {"unknown", "unreachable"} for item in statuses) else "blocked"
    result: dict[str, object] = {"schema_version": "yosys-antecedent-reachability-v1", "status": status, "top": top, "antecedent": antecedent, "branches": branch_results, "sequence": sequence, "source_revision": source_revision, "sources": [{"path": str(source), "sha256": hashlib.sha256(source.read_bytes()).hexdigest()} for source in sources], "claim_boundary": "bounded reachability of parsed scalar Boolean branches; not complete compound SVA vacuity proof"}
    result["result_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    root.mkdir(parents=True, exist_ok=True)
    (root / "antecedent-reachability-result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def run_yosys_assertion_proof(
    sources: list[str | Path],
    *,
    top: str,
    run_root: str | Path,
    sequence: int = 6,
    source_revision: str = "unknown",
    timeout_seconds: float = 60.0,
) -> dict[str, object]:
    """Run and classify a formal assertion bundle with Yosys SAT.

    ``sources`` must include the DUT and a formal top containing immediate
    ``assert`` statements (normally generated from a lowered property or a
    specification model).  A passing Yosys process is not itself called a
    proof: the report distinguishes ``proven``, ``counterexample``, and
    ``unknown`` from the solver's terminal marker.
    """
    if not sources or not top or sequence < 1 or not source_revision:
        raise ValueError("sources, top, positive sequence, and source_revision are required")
    paths = [Path(source).resolve() for source in sources]
    if any(not path.is_file() for path in paths):
        raise ValueError("all formal assertion sources must exist")
    root = Path(run_root)
    reads = "; ".join(f"read_verilog -formal -sv {path}" for path in paths)
    script = f"{reads}; prep -top {top}; flatten; select -module {top}; sat -seq {sequence} -prove-asserts"
    run = run_command(
        ["yosys", "-p", script], tool="yosys-assertion-proof", run_root=root,
        source_revision=source_revision, timeout_seconds=timeout_seconds, run_id="assertion-proof",
    )
    log_path = root / "stdout.log"
    log = log_path.read_text(encoding="utf-8") if log_path.is_file() else ""
    solver_result = parse_yosys_sat_result(log)
    assertion_count = len(re.findall(r"\bassert\s*\(", "\n".join(path.read_text(encoding="utf-8") for path in paths)))
    status = solver_result if run.status == "passed" else "blocked"
    result: dict[str, object] = {
        "schema_version": "yosys-assertion-proof-v1",
        "status": status,
        "solver_result": solver_result,
        "top": top,
        "sequence": sequence,
        "assertion_count": assertion_count,
        "source_revision": source_revision,
        "sources": [{"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()} for path in paths],
        "tool_run": asdict(run),
        "claim_boundary": "bounded Yosys SAT assertion result; proven is limited to the supplied formal model, sequence depth, and assumptions",
    }
    result["result_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    root.mkdir(parents=True, exist_ok=True)
    (root / "assertion-proof-result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def run_yosys_inductive_proof(
    sources: list[str | Path],
    *,
    top: str,
    run_root: str | Path,
    source_revision: str = "unknown",
    timeout_seconds: float = 60.0,
    max_steps: int = 4,
) -> dict[str, object]:
    """Run Yosys temporal induction and preserve its distinct proof status.

    This is intentionally separate from ``run_yosys_assertion_proof``: a
    finite ``-seq`` result is bounded evidence, while ``-tempinduct`` asks the
    backend to prove a base case and an inductive step.
    """
    if not sources or not top or not source_revision or max_steps < 1:
        raise ValueError("sources, top, source_revision, and positive max_steps are required")
    paths = [Path(source).resolve() for source in sources]
    if any(not path.is_file() for path in paths):
        raise ValueError("all formal assertion sources must exist")
    root = Path(run_root)
    reads = "; ".join(f"read_verilog -formal -sv {path}" for path in paths)
    script = f"{reads}; prep -top {top}; flatten; select -module {top}; sat -tempinduct -seq {max_steps} -set-assumes -prove-asserts"
    run = run_command(
        ["yosys", "-p", script], tool="yosys-inductive-proof", run_root=root,
        source_revision=source_revision, timeout_seconds=timeout_seconds, run_id="inductive-proof",
    )
    log_path = root / "stdout.log"
    log = log_path.read_text(encoding="utf-8") if log_path.is_file() else ""
    solver_result = "proven" if "Induction step proven: SUCCESS!" in log else "counterexample" if "Induction step failed" in log or "FAIL!" in log else "unknown"
    if run.status != "passed":
        status = "blocked"
    elif solver_result == "proven":
        status = "proven"
    elif solver_result == "counterexample":
        status = "counterexample"
    else:
        status = "unknown"
    result: dict[str, object] = {
        "schema_version": "yosys-inductive-proof-v1",
        "status": status,
        "solver_result": solver_result,
        "top": top,
        "max_steps": max_steps,
        "method": "temporal-induction",
        "source_revision": source_revision,
        "sources": [{"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()} for path in paths],
        "tool_run": asdict(run),
        "claim_boundary": "Yosys temporal induction for the supplied model, assumptions, and assertions; not general silicon correctness",
    }
    result["result_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    root.mkdir(parents=True, exist_ok=True)
    (root / "inductive-proof-result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def generate_assertion_wrapper(
    dut_source: str | Path,
    assertion_source: str | Path,
    *,
    top: str,
    output: str | Path,
    run_root: str | Path,
    source_revision: str,
    assertion_top: str = "agent_assertion",
    timeout_seconds: float = 60.0,
    allow_internal_signals: bool = False,
) -> dict[str, object]:
    """Generate and compile-check a port-validated DUT/assertion wrapper."""
    if not top or not assertion_top or not source_revision:
        raise ValueError("top, assertion_top, and source_revision are required")
    dut, assertion, target = Path(dut_source), Path(assertion_source), Path(output)
    root = Path(run_root)
    result: dict[str, object] = {"schema_version": "assertion-wrapper-v1", "source_revision": source_revision, "dut": str(dut), "assertion": str(assertion), "top": top, "assertion_top": assertion_top, "status": "blocked", "dut_sha256": hashlib.sha256(dut.read_bytes()).hexdigest(), "assertion_sha256": hashlib.sha256(assertion.read_bytes()).hexdigest()}
    inventory = ingest_rtl_ports(dut, root=dut.parent, source_revision=source_revision)
    module = next((item for item in inventory["modules"] if item["name"] == top), None)
    assertion_text = assertion.read_text(encoding="utf-8")
    assertion_match = re.search(rf"\bmodule\s+{re.escape(assertion_top)}\s*\((.*?)\)\s*;", assertion_text, re.S)
    if module is None or assertion_match is None:
        result["blocked_reason"] = "DUT or assertion module declaration was not found"
    else:
        dut_ports = {port["name"]: port for port in module["ports"]}
        assertion_ports = re.findall(r"\b(?:input|output|inout)\b(?:\s+(?:logic|wire|reg))?(?:\s+\[[^]]+\])?\s+([A-Za-z_]\w*)", assertion_match.group(1))
        internal_signals: set[str] = set()
        if allow_internal_signals:
            module_body = re.search(rf"\bmodule\s+{re.escape(top)}\b.*?\bendmodule\b", dut.read_text(encoding="utf-8"), re.S)
            if module_body:
                internal_signals = set(re.findall(r"\b(?:logic|wire|reg)\s+(?:\[[^]]+\]\s+)?([A-Za-z_]\w*)", module_body.group(0))) - set(dut_ports)
        missing = sorted(set(assertion_ports) - set(dut_ports) - internal_signals)
        if missing:
            result["blocked_reason"] = "assertion references non-port or unknown DUT signals"
            result["missing_signals"] = missing
        else:
            declarations = []
            connections = []
            for name in sorted(dut_ports):
                port = dut_ports[name]
                # Wrapper ports are nets so DUT instance outputs can drive them
                # under conservative Verilog frontends.
                kind = " wire"
                width = "" if port["range"] == "scalar" else f" {port['range']}"
                declarations.append(f"{port['direction']}{kind}{width} {name}")
                if name in assertion_ports:
                    connections.append(f".{name}({name})")
            for name in sorted(set(assertion_ports) & internal_signals):
                connections.append(f".{name}(dut_i.{name})")
            wrapper = f"module assertion_wrapper({', '.join(declarations)});\n  {top} dut_i({', '.join(f'.{name}({name})' for name in sorted(dut_ports))});\n  {assertion_top} assertion_i({', '.join(connections)});\nendmodule\n"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(wrapper, encoding="utf-8")
            compile_run = run_command(["iverilog", "-g2012", "-t", "null", str(dut.resolve()), str(assertion.resolve()), str(target.resolve())], tool="assertion-wrapper-compile", run_root=root / "compile", source_revision=source_revision, timeout_seconds=timeout_seconds, run_id="assertion-wrapper")
            result.update({"status": "passed" if compile_run.status == "passed" else "blocked", "output": str(target), "wrapper_sha256": hashlib.sha256(wrapper.encode()).hexdigest(), "compiler": asdict(compile_run), "allow_internal_signals": allow_internal_signals, "internal_signals": sorted(set(assertion_ports) & internal_signals)})
            if compile_run.status != "passed":
                result["blocked_reason"] = "generated assertion wrapper did not compile"
    result["result_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    root.mkdir(parents=True, exist_ok=True)
    (root / "assertion-wrapper-result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result
