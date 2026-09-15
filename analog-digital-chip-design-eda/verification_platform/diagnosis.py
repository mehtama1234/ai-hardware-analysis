"""Evidence-gated balanced diagnosis for hardware failures."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
from typing import Iterable

from .triage import Failure


@dataclass(frozen=True)
class BalancedDiagnosis:
    diagnosis_id: str
    source_revision: str
    failure: dict[str, object]
    for_evidence: tuple[str, ...]
    against_evidence: tuple[str, ...]
    causal_paths: tuple[tuple[str, ...], ...]
    status: str = "review_required"

    def validate(self) -> None:
        if not self.diagnosis_id or not self.source_revision:
            raise ValueError("diagnosis identity and source revision are required")
        if self.status != "review_required":
            raise ValueError("diagnosis must remain review_required")
        if not self.for_evidence or not self.against_evidence:
            raise ValueError("balanced diagnosis requires FOR and AGAINST evidence")
        if not self.failure.get("signal") or "cycle" not in self.failure:
            raise ValueError("diagnosis failure must include signal and cycle")
        for path in self.causal_paths:
            if not path:
                raise ValueError("causal paths cannot be empty")

    @property
    def diagnosis_sha256(self) -> str:
        self.validate()
        body = asdict(self)
        body["for_evidence"] = list(self.for_evidence)
        body["against_evidence"] = list(self.against_evidence)
        body["causal_paths"] = [list(path) for path in self.causal_paths]
        return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

    def record(self) -> dict[str, object]:
        self.validate()
        return {**asdict(self), "for_evidence": list(self.for_evidence), "against_evidence": list(self.against_evidence), "causal_paths": [list(path) for path in self.causal_paths], "diagnosis_sha256": self.diagnosis_sha256}


def build_balanced_diagnosis(
    failure: Failure,
    *,
    source_revision: str,
    for_evidence: Iterable[str],
    against_evidence: Iterable[str],
    causal_paths: Iterable[Iterable[str]] = (),
) -> BalancedDiagnosis:
    diagnosis = BalancedDiagnosis(
        diagnosis_id=f"diagnosis-{failure.signal}-{failure.cycle}",
        source_revision=source_revision,
        failure={"cycle": failure.cycle, "signal": failure.signal, "expected": failure.expected, "actual": failure.actual},
        for_evidence=tuple(item.strip() for item in for_evidence if item.strip()),
        against_evidence=tuple(item.strip() for item in against_evidence if item.strip()),
        causal_paths=tuple(tuple(node for node in path if node) for path in causal_paths),
    )
    diagnosis.validate()
    return diagnosis


def write_balanced_diagnosis(diagnosis: BalancedDiagnosis, path: str | Path) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(diagnosis.record(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output
