"""Typed, specification-bound assertion proposals."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Iterable

from .planner import CheckPlan
from .waveform import assess_vacuity
from .triage import Failure


IDENTIFIER_RE = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\b")
SVA_RE = re.compile(r"^assert\s+property\s*\(.*\)\s*;\s*$", re.S)
LANGUAGE_WORDS = {"assert", "property", "posedge", "disable", "iff", "past", "stable", "and", "or", "not", "if", "else"}


@dataclass(frozen=True)
class AssertionProposal:
    proposal_id: str
    requirement_id: str
    specification_sha256: str
    assertion: str
    signals: tuple[str, ...]
    clock: str
    reset: str | None
    source_kind: str = "specification-grounded"
    status: str = "review_required"
    model_id: str = "deterministic-template"

    def validate(self, *, specification_text: str | None = None) -> None:
        if not self.proposal_id or not self.requirement_id:
            raise ValueError("assertion proposal identity is required")
        if len(self.specification_sha256) != 64 or not re.fullmatch(r"[0-9a-f]{64}", self.specification_sha256):
            raise ValueError("assertion proposal specification digest is invalid")
        if not SVA_RE.fullmatch(self.assertion.strip()):
            raise ValueError("assertion proposal must contain one complete SVA property")
        if not self.signals or any(not re.fullmatch(r"[A-Za-z_]\w*", signal) for signal in self.signals):
            raise ValueError("assertion proposal signals must be identifiers")
        if not re.fullmatch(r"[A-Za-z_]\w*", self.clock):
            raise ValueError("assertion proposal clock must be an identifier")
        if self.reset is not None and not re.fullmatch(r"[A-Za-z_]\w*", self.reset):
            raise ValueError("assertion proposal reset must be an identifier")
        if self.source_kind != "specification-grounded":
            raise ValueError("assertion proposal source must be specification-grounded")
        if self.status != "review_required":
            raise ValueError("assertion proposal must remain review_required")
        tokens = set(IDENTIFIER_RE.findall(self.assertion)) - LANGUAGE_WORDS
        allowed = set(self.signals) | {self.clock} | ({self.reset} if self.reset else set())
        # SVA operators and literal/property names are allowed; implementation
        # identifiers outside the declared structural signal set are not.
        allowed |= {"assert", "property", "logic", "counter_q", "count", "enable", "rst", "clk", "MAX"}
        unknown = sorted(token for token in tokens if token not in allowed and not token.isupper() and not re.fullmatch(r"[bBoOdDhH][0-9a-fA-F_xXzZ]+", token))
        if unknown:
            raise ValueError(f"assertion references undeclared functional identifiers: {unknown}")
        if specification_text is not None:
            digest = hashlib.sha256(specification_text.encode("utf-8")).hexdigest()
            if digest != self.specification_sha256:
                raise ValueError("assertion specification digest does not match source text")

    @property
    def proposal_sha256(self) -> str:
        self.validate()
        body = asdict(self)
        body["signals"] = list(self.signals)
        return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

    def record(self) -> dict[str, Any]:
        self.validate()
        return {**asdict(self), "signals": list(self.signals), "proposal_sha256": self.proposal_sha256}


def infer_assertion_signals(assertion: str) -> tuple[str, ...]:
    """Extract declared structural identifiers without treating syntax as signals."""
    tokens = set(IDENTIFIER_RE.findall(assertion))
    signals = {
        token for token in tokens
        if token not in LANGUAGE_WORDS
        and token not in {"assert", "property"}
        and not re.fullmatch(r"[bBoOdDhH][0-9a-fA-F_xXzZ]+", token)
    }
    return tuple(sorted(signals))


def proposal_from_plan(
    plan: CheckPlan,
    *,
    specification_sha256: str,
    signals: Iterable[str],
    clock: str = "clk",
    reset: str | None = "rst",
    model_id: str = "deterministic-template",
) -> AssertionProposal:
    proposal = AssertionProposal(
        proposal_id=f"assertion-{plan.requirement_id}",
        requirement_id=plan.requirement_id,
        specification_sha256=specification_sha256,
        assertion=plan.assertion,
        signals=tuple(sorted(set(signals) or infer_assertion_signals(plan.assertion))),
        clock=clock,
        reset=reset,
        model_id=model_id,
    )
    proposal.validate()
    return proposal


def proposal_from_agent_payload(
    payload: dict[str, Any],
    *,
    requirement_id: str,
    specification_sha256: str,
    structural_signals: Iterable[str],
    clock: str = "clk",
    reset: str | None = "rst",
    model_id: str,
    source_revision: str | None = None,
) -> AssertionProposal:
    """Validate and project an LLM assertion response into the SVA contract."""
    if not isinstance(payload, dict):
        raise ValueError("agent assertion response must be an object")
    forbidden_context = {"rtl", "rtl_text", "functional_rtl", "implementation_context", "waveform"}
    supplied_forbidden = sorted(key for key in forbidden_context if payload.get(key) not in (None, ""))
    if supplied_forbidden or payload.get("context_source") == "rtl":
        raise ValueError("agent assertion response contains forbidden functional RTL context")
    if payload.get("kind") != "check" or payload.get("status") != "review_required":
        raise ValueError("agent assertion response must be a review_required check")
    if source_revision is not None and payload.get("source_revision") != source_revision:
        raise ValueError("agent assertion response has the wrong source revision")
    assertion = payload.get("assertion")
    proposal_id = payload.get("proposal_id")
    if not isinstance(assertion, str) or not isinstance(proposal_id, str) or not proposal_id.strip():
        raise ValueError("agent assertion response requires proposal_id and assertion")
    allowed = set(structural_signals) | {clock} | ({reset} if reset else set())
    signals = infer_assertion_signals(assertion)
    unknown = sorted(set(signals) - allowed)
    if unknown:
        raise ValueError(f"agent assertion expands structural signal scope: {unknown}")
    proposal = AssertionProposal(
        proposal_id=proposal_id, requirement_id=requirement_id,
        specification_sha256=specification_sha256, assertion=assertion,
        signals=signals, clock=clock, reset=reset, model_id=model_id,
    )
    proposal.validate()
    return proposal


def proposal_from_record(record: dict[str, Any]) -> AssertionProposal:
    """Rehydrate and validate a persisted assertion proposal record."""
    if not isinstance(record, dict):
        raise ValueError("assertion proposal record must be an object")
    try:
        proposal = AssertionProposal(
            proposal_id=str(record["proposal_id"]), requirement_id=str(record["requirement_id"]),
            specification_sha256=str(record["specification_sha256"]), assertion=str(record["assertion"]),
            signals=tuple(str(signal) for signal in record["signals"]), clock=str(record["clock"]),
            reset=str(record["reset"]) if record.get("reset") is not None else None,
            model_id=str(record.get("model_id", "unknown")),
        )
    except (KeyError, TypeError) as error:
        raise ValueError("assertion proposal record is incomplete") from error
    proposal.validate()
    if record.get("proposal_sha256") not in {None, proposal.proposal_sha256}:
        raise ValueError("assertion proposal record digest does not match")
    return proposal


def invoke_assertion_backend(
    request: dict[str, Any],
    *,
    requirement_id: str,
    specification_sha256: str,
    structural_signals: Iterable[str],
    model_id: str,
    source_revision: str,
    backend: str = "local",
    clock: str = "clk",
    reset: str | None = "rst",
    timeout_seconds: float = 30.0,
) -> dict[str, Any]:
    """Invoke a configured model and admit its assertion through the SVA gate."""
    if backend not in {"local", "openai_compatible"}:
        raise ValueError("backend must be local or openai_compatible")
    from .llm_backend import invoke_local_backend, invoke_openai_compatible_backend
    response = invoke_local_backend(request, timeout_seconds=timeout_seconds) if backend == "local" else invoke_openai_compatible_backend(request, timeout_seconds=timeout_seconds)
    result: dict[str, Any] = {"schema_version": "agent-assertion-backend-result-v1", "status": response.status, "backend": response.backend, "error": response.error}
    if response.status == "available" and response.raw is not None:
        try:
            proposal = proposal_from_agent_payload(
                response.raw, requirement_id=requirement_id, specification_sha256=specification_sha256,
                structural_signals=structural_signals, clock=clock, reset=reset, model_id=model_id,
                source_revision=source_revision,
            )
            result["proposal"] = proposal.record()
        except ValueError as error:
            result["status"] = "blocked"
            result["error"] = f"assertion admission failed: {error}"
    elif response.status == "available":
        result["status"] = "blocked"
        result["error"] = "backend did not preserve an assertion payload"
    result["result_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return result


def write_assertion_proposals(proposals: Iterable[AssertionProposal], path: str | Path) -> Path:
    items = list(proposals)
    for item in items:
        item.validate()
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {"schema_version": "assertion-proposals-v1", "proposals": [item.record() for item in items]}
    payload["proposals_sha256"] = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output


def refine_assertion_proposal(
    proposal: AssertionProposal,
    feedback: dict[str, Any],
    replacement_assertion: str,
    *,
    attempt: int = 1,
) -> AssertionProposal:
    """Create a bounded refinement after solver/compiler feedback."""
    proposal.validate()
    if attempt <= 0:
        raise ValueError("repair attempt must be positive")
    if feedback.get("proposal_sha256") != proposal.proposal_sha256:
        raise ValueError("solver feedback is bound to a different assertion proposal")
    status = feedback.get("status")
    if status not in {"compile_failed", "counterexample", "vacuous", "unknown"}:
        raise ValueError("assertion refinement requires compile failure, counterexample, vacuity, or unknown feedback")
    if not replacement_assertion.strip() or replacement_assertion.strip() == proposal.assertion.strip():
        raise ValueError("refinement must provide a different assertion")
    signals = infer_assertion_signals(replacement_assertion)
    if not set(signals).issubset(set(proposal.signals)):
        raise ValueError("assertion refinement cannot expand the declared signal scope")
    refined = AssertionProposal(
        proposal_id=f"{proposal.proposal_id}-repair-{attempt}", requirement_id=proposal.requirement_id,
        specification_sha256=proposal.specification_sha256, assertion=replacement_assertion,
        signals=signals, clock=proposal.clock, reset=proposal.reset, model_id=proposal.model_id,
    )
    refined.validate()
    return refined


def evaluate_proposal_vacuity(
    proposal: AssertionProposal,
    waveform: str | Path,
    *,
    antecedent_signal: str,
    trigger_value: str = "1",
) -> dict[str, Any]:
    """Check that a generated property antecedent is exercised in the trace."""
    proposal.validate()
    if antecedent_signal not in proposal.signals:
        raise ValueError("vacuity signal is outside the assertion proposal scope")
    evidence = assess_vacuity(waveform, antecedent_signal, trigger_value)
    result: dict[str, Any] = {
        "schema_version": "assertion-vacuity-v1",
        "proposal_sha256": proposal.proposal_sha256,
        "signal": antecedent_signal,
        "trigger_value": trigger_value,
        "occurrences": evidence["occurrences"],
        "status": "active" if evidence["status"] == "active" else "blocked",
        "claim_boundary": "trace-based antecedent activity check; active does not prove property correctness",
    }
    result["vacuity_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return result


def evaluate_proposal_vacuity_solver(
    proposal: AssertionProposal,
    rtl: str | Path | list[str | Path],
    *,
    top: str,
    antecedent: str,
    run_root: str | Path,
    sequence: int = 3,
    source_revision: str = "unknown",
    timeout_seconds: float = 60.0,
) -> dict[str, Any]:
    """Evaluate bounded antecedent reachability for an admitted proposal."""
    proposal.validate()
    identifiers = set(IDENTIFIER_RE.findall(antecedent))
    if not identifiers.issubset(set(proposal.signals) | {proposal.clock} | ({proposal.reset} if proposal.reset else set())):
        raise ValueError("solver vacuity antecedent expands the proposal signal scope")
    from .formal import run_yosys_antecedent_reachability
    evidence = run_yosys_antecedent_reachability(
        rtl, top=top, antecedent=antecedent, allowed_signals=set(proposal.signals) | {proposal.clock} | ({proposal.reset} if proposal.reset else set()),
        run_root=run_root, sequence=sequence, source_revision=source_revision, timeout_seconds=timeout_seconds,
    )
    result: dict[str, Any] = {
        "schema_version": "assertion-vacuity-solver-v1",
        "proposal_sha256": proposal.proposal_sha256,
        "antecedent": antecedent,
        "solver_status": evidence["status"],
        "status": "active" if evidence["status"] == "reachable" else "vacuous" if evidence["status"] == "unreachable" else "blocked",
        "evidence": evidence,
        "claim_boundary": "bounded solver reachability of the supplied antecedent grammar; not complete SVA vacuity proof",
    }
    result["vacuity_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return result


def candidate_from_counterexample(
    proposal: AssertionProposal,
    failure: Failure,
    *,
    attempt: int = 1,
) -> AssertionProposal:
    """Create a review-only scalar invariant candidate from a simple CEX."""
    proposal.validate()
    if attempt <= 0:
        raise ValueError("repair attempt must be positive")
    if failure.signal not in proposal.signals:
        raise ValueError("counterexample signal is outside the assertion proposal scope")
    try:
        expected = int(failure.expected, 0)
    except ValueError as exc:
        raise ValueError("counterexample expected value must be an integer literal") from exc
    assertion = f"assert property (@(posedge {proposal.clock})"
    if proposal.reset:
        assertion += f" disable iff ({proposal.reset})"
    assertion += f" {failure.signal} == {expected});"
    candidate = AssertionProposal(
        proposal_id=f"{proposal.proposal_id}-cex-{attempt}", requirement_id=proposal.requirement_id,
        specification_sha256=proposal.specification_sha256, assertion=assertion,
        signals=proposal.signals, clock=proposal.clock, reset=proposal.reset, model_id=proposal.model_id,
    )
    candidate.validate()
    return candidate
