from hardware_profile import TARGET_PROFILES
from quantization import MODALITY_PROFILES


WORKLOAD_FIT_SCHEMA_VERSION = "workload-fit-v0.1"


WORKLOAD_CONTEXT = {
    "audio_wake_word": {
        "duty_cycle": "always listening, short bursts",
        "easier": "Small repeated models can benefit when battery life and idle heat matter more than peak throughput.",
        "harder": "False accepts and false rejects matter, so noise and first-layer signal handling need careful validation.",
    },
    "vision_classification": {
        "duty_cycle": "periodic frame inference",
        "easier": "Convolution and classifier layers can give useful analog coverage when the model is compact.",
        "harder": "Average top-1 accuracy can hide class-specific failures, and image input variation can stress calibration.",
    },
    "object_detection": {
        "duty_cycle": "frame stream with bursty post-processing",
        "easier": "Backbone convolution work can be a strong fit when the detector runs often on a thermal budget.",
        "harder": "Box heads, confidence scores, resize, NMS, and recall on small objects can limit what moves to analog.",
    },
    "robotics_perception": {
        "duty_cycle": "low-latency control loop",
        "easier": "Repeated perception blocks can save energy when the robot cannot move data to a larger processor.",
        "harder": "Worst-case latency, jitter, and rare unstable outputs matter more than average accuracy.",
    },
    "industrial_anomaly": {
        "duty_cycle": "steady monitoring with rare positive events",
        "easier": "Always-on sensing is a good energy story when the model runs continuously near the sensor.",
        "harder": "Rare fault recall is the real proof, and calibration data may miss the cases that matter most.",
    },
    "health_wearable": {
        "duty_cycle": "always-on or frequent personal signal inference",
        "easier": "Battery and heat limits are severe, so local low-energy inference can be valuable.",
        "harder": "User-dependent small signals and missed-event cost make validation stricter than a simple benchmark.",
    },
    "edge_llm": {
        "duty_cycle": "interactive token generation",
        "easier": "Large repeated matrix work creates a strong reason to reduce memory movement.",
        "harder": "Attention, normalization-adjacent paths, output logits, memory capacity, and token quality make full-system proof harder.",
    },
}


def _score_label(score):
    if score >= 75:
        return "strong candidate"
    if score >= 55:
        return "possible fit"
    if score >= 35:
        return "hard fit"
    return "poor fit"


def _target_modifier(target_profile, modality):
    if target_profile == "wearable" and modality in {"audio_wake_word", "health_wearable", "industrial_anomaly"}:
        return 8
    if target_profile == "camera" and modality in {"vision_classification", "object_detection"}:
        return 8
    if target_profile == "robotics" and modality == "robotics_perception":
        return 8
    if target_profile == "wearable" and modality == "edge_llm":
        return -14
    if target_profile == "robotics" and modality in {"audio_wake_word", "health_wearable"}:
        return -6
    return 0


def _difficulty_penalty(modality):
    return {
        "audio_wake_word": 6,
        "vision_classification": 8,
        "object_detection": 16,
        "robotics_perception": 18,
        "industrial_anomaly": 18,
        "health_wearable": 16,
        "edge_llm": 24,
    }.get(modality, 12)


def _row(modality, profile, selected_modality, target_profile, analysis, quantization_report, runtime_profile):
    summary = analysis.get("summary", {})
    runtime = runtime_profile.get("summary", {})
    analog_coverage = float(summary.get("analog_coverage_percent", 0) or 0)
    fallback_count = int(summary.get("fallback_count", 0) or 0)
    boundary_count = len(analysis.get("boundary_events", []))
    protected_layers = int((quantization_report.get("summary") or {}).get("protected_layers", 0) or 0)
    latency_margin = float((runtime.get("latency_target_ms", 0) or 0) - (runtime.get("latency_ms", 0) or 0))
    energy_margin = float((runtime.get("energy_target_uj", 0) or 0) - (runtime.get("energy_uj", 0) or 0))
    base = analog_coverage
    base += _target_modifier(target_profile, modality)
    base -= fallback_count * 3
    base -= boundary_count * 2
    base -= protected_layers * 1.5
    base -= _difficulty_penalty(modality)
    if latency_margin < 0:
        base -= 8
    if energy_margin < 0:
        base -= 8
    if modality == selected_modality:
        base += 5
    score = round(max(0, min(100, base)), 1)
    context = WORKLOAD_CONTEXT.get(modality, {})
    return {
        "modality": modality,
        "label": profile["label"],
        "selected": modality == selected_modality,
        "score": score,
        "fit": _score_label(score),
        "task_metric": profile["task_metric"],
        "primary_failure_cost": profile["primary_failure_cost"],
        "duty_cycle": context.get("duty_cycle", "workload duty cycle depends on deployment"),
        "where_analog_gets_easier": context.get("easier", "Analog is easier when repeated matrix work dominates and data movement is costly."),
        "where_it_gets_harder": context.get("harder", "Analog is harder when numeric sensitivity, unsupported operators, or system integration dominate."),
        "validation_focus": profile["plain_risk"],
    }


def build_workload_fit_matrix(analysis, quantization_report, runtime_profile, target_profile="wearable", modality="vision_classification"):
    target = TARGET_PROFILES.get(target_profile, TARGET_PROFILES["wearable"])
    rows = [
        _row(key, profile, modality, target_profile, analysis, quantization_report, runtime_profile)
        for key, profile in MODALITY_PROFILES.items()
    ]
    rows.sort(key=lambda item: (not item["selected"], -item["score"], item["label"]))
    selected = next((row for row in rows if row["selected"]), rows[0] if rows else None)
    return {
        "result_type": "workload_fit_matrix",
        "schema_version": WORKLOAD_FIT_SCHEMA_VERSION,
        "provenance": "derived from model fit, modality profile, target profile, and simulated runtime",
        "confidence": "low",
        "target_profile": target_profile,
        "target_label": target["label"],
        "selected_modality": modality,
        "summary": {
            "selected_fit": (selected or {}).get("fit"),
            "selected_score": (selected or {}).get("score"),
            "target_energy_uj": target["energy_target_uj"],
            "target_latency_ms": target["latency_target_ms"],
            "plain_reading": "Edge AI is not one market. The same hardware story changes with duty cycle, failure cost, model shape, and evidence target.",
        },
        "rows": rows,
        "do_not_claim": [
            "Do not use one selected modality as proof for all edge AI workloads.",
            "Do not compare workloads only by peak TOPS/W; compare completed inference under each workload's metric and target.",
            "Do not treat a high analog coverage score as enough when fallback operators, boundary crossings, or rare-event accuracy dominate.",
        ],
    }
