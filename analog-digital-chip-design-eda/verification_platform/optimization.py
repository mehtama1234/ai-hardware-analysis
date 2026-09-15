"""Typed, evidence-bound state for closed-loop EDA optimization."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import csv
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

from .runner import run_command


@dataclass(frozen=True)
class OptimizationRun:
    candidate: dict[str, Any]
    metrics: dict[str, float]
    status: str
    runtime_seconds: float | None = None
    failure_reason: str | None = None
    fidelity: str = "full"
    tool: str = ""
    source_digest: str = ""
    configuration_digest: str = ""
    metrics_artifact_sha256: str = ""
    metrics_artifact_path: str = ""

    def validate(self) -> None:
        if not self.candidate:
            raise ValueError("optimization candidate must not be empty")
        if self.status not in {"passed", "failed"}:
            raise ValueError("optimization status must be passed or failed")
        if self.fidelity not in {"proxy", "full"}:
            raise ValueError("optimization fidelity must be proxy or full")
        required = {"wns", "area", "power"}
        if set(self.metrics) != required:
            raise ValueError("optimization metrics must contain exactly wns, area, and power")
        if any(not isinstance(value, (int, float)) for value in self.metrics.values()):
            raise ValueError("optimization metrics must be numeric")
        if self.runtime_seconds is not None and (not isinstance(self.runtime_seconds, (int, float)) or self.runtime_seconds < 0):
            raise ValueError("runtime_seconds must be a nonnegative number")
        for name, value in (("tool", self.tool), ("source_digest", self.source_digest), ("configuration_digest", self.configuration_digest), ("metrics_artifact_sha256", self.metrics_artifact_sha256)):
            if not isinstance(value, str):
                raise ValueError(f"optimization {name} must be a string")
        for digest_name, digest in (
            ("source_digest", self.source_digest),
            ("configuration_digest", self.configuration_digest),
            ("metrics_artifact_sha256", self.metrics_artifact_sha256),
        ):
            if digest and (len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest)):
                raise ValueError(f"{digest_name} must be a lowercase 64-character hex digest")
        if self.metrics_artifact_path and (Path(self.metrics_artifact_path).is_absolute() or ".." in Path(self.metrics_artifact_path).parts):
            raise ValueError("metrics_artifact_path must be relative to the measurement run")
        if self.status == "failed" and not self.failure_reason:
            raise ValueError("failed optimization runs require a failure reason")

    def record(self) -> dict[str, Any]:
        self.validate()
        return asdict(self)


@dataclass(frozen=True)
class OptimizationState:
    priors: dict[str, Any]
    rules: tuple[str, ...]
    sensitivities: dict[str, float]
    runs: tuple[OptimizationRun, ...]
    pareto_frontier: tuple[int, ...]
    schema_version: str = "eda-optimization-state-v1"
    source_revision: str = ""

    def to_dict(self) -> dict[str, Any]:
        for run in self.runs:
            run.validate()
        payload = asdict(self)
        payload["rules"] = list(self.rules)
        payload["runs"] = [run.record() for run in self.runs]
        payload["pareto_frontier"] = list(self.pareto_frontier)
        return payload

    def digest(self) -> str:
        return hashlib.sha256(json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def select_next_candidate(
    state: OptimizationState,
    proposals: list[dict[str, Any]],
    *,
    max_runtime_seconds: float | None = None,
    mode: str = "exploit",
) -> dict[str, Any]:
    """Select one bounded candidate using predicted QoR and stable tie-breaks.

    This is a proposal-ranking operation.  It does not add the candidate to
    measured history; callers must execute it and record the actual result.
    """
    if verify_optimization_state(state):
        raise ValueError("cannot select from invalid optimization state")
    if max_runtime_seconds is not None and max_runtime_seconds < 0:
        raise ValueError("max_runtime_seconds must not be negative")
    if mode not in {"explore", "exploit", "diversify", "repair", "prior_refinement"}:
        raise ValueError("unsupported optimization search mode")
    valid: list[dict[str, Any]] = []
    for index, proposal in enumerate(proposals):
        if not isinstance(proposal, dict) or not isinstance(proposal.get("candidate"), dict):
            raise ValueError(f"optimization proposal at index {index} is invalid")
        metrics = proposal.get("predicted_metrics")
        if not isinstance(metrics, dict) or set(metrics) != {"wns", "area", "power"}:
            raise ValueError(f"optimization proposal at index {index} has invalid predicted metrics")
        if any(not isinstance(value, (int, float)) for value in metrics.values()):
            raise ValueError(f"optimization proposal at index {index} has nonnumeric predicted metrics")
        runtime = proposal.get("estimated_runtime_seconds")
        if runtime is not None and (not isinstance(runtime, (int, float)) or runtime < 0):
            raise ValueError(f"optimization proposal at index {index} has invalid runtime")
        if max_runtime_seconds is not None and (runtime is None or runtime > max_runtime_seconds):
            continue
        valid.append(proposal)
    if not valid:
        raise ValueError("no optimization proposal satisfies the runtime budget")

    prior_candidate = state.priors.get("candidate", state.priors) if isinstance(state.priors, dict) else {}
    prior_candidate = prior_candidate if isinstance(prior_candidate, dict) else {}
    historical = [json.dumps(run.candidate, sort_keys=True, separators=(",", ":")) for run in state.runs]

    def distance(candidate: dict[str, Any], other: dict[str, Any]) -> int:
        keys = set(candidate) | set(other)
        return sum(candidate.get(key) != other.get(key) for key in keys)

    def sort_key(proposal: dict[str, Any]) -> tuple[Any, ...]:
        metrics = proposal["predicted_metrics"]
        candidate_key = json.dumps(proposal["candidate"], sort_keys=True, separators=(",", ":"))
        qos = (-float(metrics["wns"]), float(metrics["area"]), float(metrics["power"]))
        if mode == "explore":
            # Prefer candidates not previously measured, then lower runtime.
            return (candidate_key in historical, proposal.get("estimated_runtime_seconds") is None, proposal.get("estimated_runtime_seconds", float("inf")), *qos, candidate_key)
        if mode == "diversify":
            spread = min((distance(proposal["candidate"], run.candidate) for run in state.runs), default=0)
            return (-spread, *qos, candidate_key)
        if mode == "repair":
            return (not bool(proposal.get("repair") or proposal.get("failure_pattern")), *qos, candidate_key)
        if mode == "prior_refinement":
            return (distance(proposal["candidate"], prior_candidate), *qos, candidate_key)
        # exploit: higher predicted WNS, then lower area and power.
        return (*qos, candidate_key)

    selected = sorted(valid, key=sort_key)[0]
    configuration_digest = hashlib.sha256(
        json.dumps(selected["candidate"], sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return {
        "schema_version": "eda-optimization-recommendation-v1",
        "state_sha256": state.digest(),
        "candidate": selected["candidate"],
        "configuration_digest": configuration_digest,
        "predicted_metrics": selected["predicted_metrics"],
        "estimated_runtime_seconds": selected.get("estimated_runtime_seconds"),
        "mode": mode,
        "measured": False,
        "claim_boundary": "prediction-ranked proposal only; execute and record measured EDA results before updating optimization state",
    }


def decide_fidelity_promotion(
    recommendation: dict[str, Any],
    proxy_metrics: dict[str, float],
    *,
    minimum_wns: float,
    maximum_area: float,
    maximum_power: float,
) -> dict[str, Any]:
    """Gate an expensive full run using measured proxy metrics."""
    if recommendation.get("schema_version") != "eda-optimization-recommendation-v1":
        raise ValueError("unsupported optimization recommendation schema")
    if recommendation.get("measured") is not False:
        raise ValueError("fidelity promotion requires an unmeasured recommendation")
    if set(proxy_metrics) != {"wns", "area", "power"}:
        raise ValueError("proxy metrics must contain exactly wns, area, and power")
    if maximum_area < 0 or maximum_power < 0:
        raise ValueError("area and power limits must not be negative")
    reasons: list[str] = []
    if proxy_metrics["wns"] < minimum_wns:
        reasons.append("proxy WNS is below the minimum")
    if proxy_metrics["area"] > maximum_area:
        reasons.append("proxy area exceeds the maximum")
    if proxy_metrics["power"] > maximum_power:
        reasons.append("proxy power exceeds the maximum")
    return {
        "schema_version": "eda-fidelity-decision-v1",
        "state_sha256": recommendation["state_sha256"],
        "candidate": recommendation["candidate"],
        "proxy_metrics": dict(proxy_metrics),
        "decision": "promote_to_full" if not reasons else "reject_at_proxy",
        "reasons": reasons,
        "measured_full_run": False,
        "claim_boundary": "proxy-gated scheduling decision only; it is not full-flow QoR evidence",
    }


def record_optimization_result(
    state: OptimizationState,
    recommendation: dict[str, Any],
    *,
    fidelity: str,
    metrics: dict[str, float],
    status: str,
    runtime_seconds: float | None = None,
    failure_reason: str | None = None,
    tool: str = "",
    source_digest: str = "",
    configuration_digest: str = "",
    metrics_artifact_sha256: str = "",
    metrics_artifact_path: str = "",
) -> OptimizationState:
    """Append a measured result only when recommendation provenance matches."""
    if recommendation.get("schema_version") != "eda-optimization-recommendation-v1":
        raise ValueError("unsupported optimization recommendation schema")
    if recommendation.get("state_sha256") != state.digest():
        raise ValueError("optimization result is bound to a different state")
    if recommendation.get("measured") is not False:
        raise ValueError("optimization recommendation is already measured")
    expected_configuration_digest = recommendation.get("configuration_digest")
    if expected_configuration_digest:
        actual_configuration_digest = hashlib.sha256(
            json.dumps(recommendation.get("candidate", {}), sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        if expected_configuration_digest != actual_configuration_digest:
            raise ValueError("optimization recommendation configuration digest does not match candidate")
        if configuration_digest and configuration_digest != expected_configuration_digest:
            raise ValueError("optimization result configuration digest does not match recommendation")
    expected_source_digest = recommendation.get("source_digest")
    if expected_source_digest and source_digest and source_digest != expected_source_digest:
        raise ValueError("optimization result source digest does not match recommendation")
    run = OptimizationRun(
        candidate=dict(recommendation.get("candidate", {})), metrics=dict(metrics), status=status,
        runtime_seconds=runtime_seconds, failure_reason=failure_reason, fidelity=fidelity,
        tool=tool, source_digest=source_digest, configuration_digest=configuration_digest,
        metrics_artifact_sha256=metrics_artifact_sha256, metrics_artifact_path=metrics_artifact_path,
    )
    run.validate()
    return build_optimization_state(
        list(state.runs) + [run], priors=state.priors, rules=list(state.rules),
        sensitivities=state.sensitivities, source_revision=state.source_revision,
    )


def run_fidelity_command(
    recommendation: dict[str, Any],
    command: list[str],
    *,
    fidelity: str,
    run_root: str | Path,
    source_revision: str,
    timeout_seconds: float = 60.0,
    expected_artifacts: list[str] | None = None,
) -> dict[str, Any]:
    """Run one proxy/full command and parse its measured QoR artifact."""
    if recommendation.get("schema_version") != "eda-optimization-recommendation-v1":
        raise ValueError("unsupported optimization recommendation schema")
    if fidelity not in {"proxy", "full"}:
        raise ValueError("optimization fidelity must be proxy or full")
    artifacts = list(expected_artifacts or [])
    if "metrics.json" not in artifacts:
        artifacts.append("metrics.json")
    tool_run = run_command(
        command, tool=f"eda-{fidelity}", run_root=run_root, source_revision=source_revision,
        timeout_seconds=timeout_seconds, expected_artifacts=artifacts, run_id=fidelity,
    )
    output: dict[str, Any] = {
        "schema_version": "eda-fidelity-result-v1",
        "recommendation_state_sha256": recommendation["state_sha256"],
        "candidate": recommendation["candidate"],
        "fidelity": fidelity,
        "tool_run": asdict(tool_run),
        "status": tool_run.status,
        "metrics": None,
        "failure_reason": None,
    }
    metrics_path = Path(run_root) / "metrics.json"
    if tool_run.status != "passed":
        output["failure_reason"] = f"{fidelity} command did not pass"
        return output
    try:
        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        if not isinstance(metrics, dict) or set(metrics) != {"wns", "area", "power"} or any(not isinstance(value, (int, float)) for value in metrics.values()):
            raise ValueError("metrics.json must contain numeric wns, area, and power")
    except (OSError, json.JSONDecodeError, ValueError) as error:
        output["status"] = "blocked"
        output["failure_reason"] = f"invalid measured metrics: {error}"
        return output
    output["metrics"] = metrics
    output["metrics_artifact"] = {"path": "metrics.json", "sha256": hashlib.sha256(metrics_path.read_bytes()).hexdigest()}
    output["metrics_artifact_path"] = "metrics.json"
    output["runtime_seconds"] = tool_run.metadata.get("duration_seconds")
    return output


def load_openlane_metrics(run_dir: str | Path) -> dict[str, float]:
    """Map an OpenLane ``reports/metrics.csv`` row into the QoR contract."""
    metrics_path = Path(run_dir) / "reports" / "metrics.csv"
    try:
        with metrics_path.open(newline="", encoding="utf-8") as stream:
            rows = list(csv.DictReader(stream))
    except OSError as error:
        raise ValueError(f"OpenLane metrics are unavailable: {error}") from error
    if len(rows) != 1:
        raise ValueError("OpenLane metrics.csv must contain exactly one result row")
    row = rows[0]

    def number(names: tuple[str, ...], label: str) -> float:
        present: list[tuple[str, float]] = []
        for name in names:
            if row.get(name) not in (None, ""):
                try:
                    present.append((name, float(row[name])))
                except ValueError as error:
                    raise ValueError(f"OpenLane {label} is not numeric: {row[name]}") from error
        if not present:
            raise ValueError(f"OpenLane metrics are missing {label}")
        values = {value for _, value in present}
        if len(values) > 1:
            names_present = ", ".join(name for name, _ in present)
            raise ValueError(f"OpenLane metrics contain conflicting {label} aliases: {names_present}")
        return present[0][1]

    return {
        "wns": number(("spef_wns", "wns", "WNS"), "WNS"),
        "area": number(("DIEAREA_mm^2", "CoreArea_um^2", "area"), "area"),
        "power": number(("total_power", "TotalPower", "power", "Power"), "power"),
    }


def _dominates(left: OptimizationRun, right: OptimizationRun) -> bool:
    """Return whether left is no worse than right on all QoR objectives."""
    return (
        left.metrics["wns"] >= right.metrics["wns"]
        and left.metrics["area"] <= right.metrics["area"]
        and left.metrics["power"] <= right.metrics["power"]
        and left.metrics != right.metrics
    )


def build_optimization_state(
    runs: list[OptimizationRun],
    *,
    priors: dict[str, Any] | None = None,
    rules: list[str] | None = None,
    sensitivities: dict[str, float] | None = None,
    source_revision: str = "",
) -> OptimizationState:
    """Normalize measured runs and calculate a deterministic passing frontier."""
    for run in runs:
        run.validate()
    frontier = []
    for index, run in enumerate(runs):
        if run.status != "passed":
            continue
        if not any(other.status == "passed" and _dominates(other, run) for other in runs):
            frontier.append(index)
    state = OptimizationState(
        priors=dict(priors or {}), rules=tuple(rules or ()),
        sensitivities=dict(sensitivities or {}), runs=tuple(runs), pareto_frontier=tuple(frontier),
        source_revision=source_revision,
    )
    state.to_dict()
    return state


def verify_optimization_state(state: OptimizationState) -> list[str]:
    errors: list[str] = []
    if state.schema_version != "eda-optimization-state-v1":
        errors.append("unsupported optimization state schema")
    try:
        expected = build_optimization_state(
            list(state.runs), priors=state.priors, rules=list(state.rules),
            sensitivities=state.sensitivities, source_revision=state.source_revision,
        )
        if state.pareto_frontier != expected.pareto_frontier:
            errors.append("optimization Pareto frontier is inconsistent with runs")
    except ValueError as exc:
        errors.append(str(exc))
    return errors


def _optimization_state_from_dict(payload: dict[str, Any]) -> OptimizationState:
    if not isinstance(payload, dict):
        raise ValueError("optimization state must be a JSON object")
    runs_payload = payload.get("runs")
    if not isinstance(runs_payload, list):
        raise ValueError("optimization state runs must be a list")
    try:
        runs = [OptimizationRun(**run) for run in runs_payload]
        state = OptimizationState(
            priors=dict(payload.get("priors", {})),
            rules=tuple(payload.get("rules", [])),
            sensitivities=dict(payload.get("sensitivities", {})),
            runs=tuple(runs),
            pareto_frontier=tuple(payload.get("pareto_frontier", [])),
            schema_version=str(payload.get("schema_version", "")),
            source_revision=str(payload.get("source_revision", "")),
        )
    except (TypeError, ValueError) as error:
        raise ValueError(f"invalid optimization state fields: {error}") from error
    errors = verify_optimization_state(state)
    if errors:
        raise ValueError("invalid optimization state: " + "; ".join(errors))
    recorded_digest = payload.get("state_sha256")
    if not isinstance(recorded_digest, str) or recorded_digest != state.digest():
        raise ValueError("optimization state digest does not match its contents")
    return state


def load_optimization_state(path: str | Path) -> OptimizationState:
    """Load a persisted state only when its content and digest are valid."""
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"unable to load optimization state: {error}") from error
    return _optimization_state_from_dict(payload)


def write_optimization_state(state: OptimizationState, path: str) -> None:
    payload = state.to_dict()
    payload["state_sha256"] = state.digest()
    from pathlib import Path
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=output.parent, prefix=f".{output.name}.", delete=False) as stream:
        temporary = Path(stream.name)
        stream.write(serialized)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, output)


def append_optimization_result(
    path: str | Path,
    recommendation: dict[str, Any],
    *,
    fidelity: str,
    metrics: dict[str, float],
    status: str,
    runtime_seconds: float | None = None,
    failure_reason: str | None = None,
    tool: str = "",
    source_digest: str = "",
    configuration_digest: str = "",
    metrics_artifact_sha256: str = "",
    metrics_artifact_path: str = "",
) -> OptimizationState:
    """Atomically append one measured run to the persisted optimization history.

    The recommendation's state digest is checked against the file before the
    append. A stale agent recommendation therefore cannot overwrite a newer
    optimization history.
    """
    state = load_optimization_state(path)
    updated = record_optimization_result(
        state, recommendation, fidelity=fidelity, metrics=metrics, status=status,
        runtime_seconds=runtime_seconds, failure_reason=failure_reason,
        tool=tool, source_digest=source_digest, configuration_digest=configuration_digest,
        metrics_artifact_sha256=metrics_artifact_sha256, metrics_artifact_path=metrics_artifact_path,
    )
    write_optimization_state(updated, str(path))
    return updated
