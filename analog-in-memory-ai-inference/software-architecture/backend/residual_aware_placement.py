from pathlib import Path
import json


BASE_DIR = Path(__file__).resolve().parent
RESIDUAL_AWARE_PLACEMENT = (
    BASE_DIR.parents[3]
    / "analog-digital-chip-design-eda"
    / "evidence"
    / "aimc-simulator-adapters"
    / "residual-aware-placement-decisions.json"
)


def _operator_ids(payload):
    rows = payload.get("placement_rows") or payload.get("rows") or []
    return {
        row.get("operator_id")
        for row in rows
        if isinstance(row, dict) and row.get("operator_id")
    }


def load_residual_aware_placement(raw_placement):
    if not RESIDUAL_AWARE_PLACEMENT.exists():
        return {
            "result_type": "residual_aware_placement_unavailable",
            "available": False,
            "reason": "residual-aware placement evidence has not been generated",
            "expected_path": str(RESIDUAL_AWARE_PLACEMENT),
        }
    payload = json.loads(RESIDUAL_AWARE_PLACEMENT.read_text(encoding="utf-8"))
    raw_ids = _operator_ids(raw_placement)
    filtered_ids = _operator_ids(payload)
    if raw_ids and filtered_ids and raw_ids != filtered_ids:
        return {
            "result_type": "residual_aware_placement_unavailable",
            "available": False,
            "reason": "residual-aware placement rows do not match this package's operator set",
            "raw_operator_ids": sorted(raw_ids),
            "residual_aware_operator_ids": sorted(filtered_ids),
            "source_path": str(RESIDUAL_AWARE_PLACEMENT),
        }
    summary = payload.get("summary") if isinstance(payload.get("summary"), dict) else {}
    return {
        **payload,
        "available": True,
        "plain_reading": (
            "Structural analog placement has been filtered through calibrated simulator residual evidence. "
            f"{summary.get('residual_aware_analog_allowed', 0)} rows remain analog-allowed."
        ),
        "source_path": str(RESIDUAL_AWARE_PLACEMENT),
    }
