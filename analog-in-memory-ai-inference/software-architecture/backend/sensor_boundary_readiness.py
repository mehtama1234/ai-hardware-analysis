SENSOR_BOUNDARY_SCHEMA_VERSION = "sensor-boundary-readiness-v0.1"


MODALITY_SENSOR_PROFILES = {
    "audio_wake_word": {
        "expected_sensors": ["microphone", "audio codec or analog front end"],
        "raw_signal_type": "pressure wave converted to analog voltage, then sampled audio or features",
        "preprocessing_owner": "sensor front end, audio DSP, or host runtime",
        "afe_status": "required",
        "event_stream_status": "not primary",
        "tactile_force_status": "not primary",
        "timestamp_sync_status": "simple window timing still needed",
        "front_end_questions": [
            "What is the microphone and codec idle power?",
            "Where are filtering, windowing, and feature extraction done?",
            "Is wake-word energy counted per hour, per wake, or only per inference?",
        ],
    },
    "health_wearable": {
        "expected_sensors": ["biological signal sensor", "motion sensor", "low-noise analog front end"],
        "raw_signal_type": "small analog biological or motion signal with noise, drift, and contact variation",
        "preprocessing_owner": "AFE, microcontroller, or host runtime before model input",
        "afe_status": "required",
        "event_stream_status": "possible for sparse events",
        "tactile_force_status": "possible but use-case specific",
        "timestamp_sync_status": "needed for sensor fusion and trend windows",
        "front_end_questions": [
            "What analog filtering and gain happen before inference?",
            "How do skin contact, motion, temperature, and sensor aging affect the tensor?",
            "Is preprocessing energy counted with inference energy?",
        ],
    },
    "industrial_anomaly": {
        "expected_sensors": ["vibration", "acoustic", "current", "pressure", "thermal"],
        "raw_signal_type": "machine-side analog or sampled time-series signals",
        "preprocessing_owner": "sensor node, AFE, microcontroller, or gateway",
        "afe_status": "often required",
        "event_stream_status": "possible for thresholded events",
        "tactile_force_status": "possible for force or pressure monitoring",
        "timestamp_sync_status": "needed when multiple sensors describe one machine state",
        "front_end_questions": [
            "Which filters and thresholds happen before the model?",
            "How are rare faults represented in the input stream?",
            "Is long-running sensor-node power counted?",
        ],
    },
    "robotics_perception": {
        "expected_sensors": ["camera", "depth", "tactile", "force", "proprioception", "inertial"],
        "raw_signal_type": "mixed camera frames, depth, force, tactile, and robot-state streams",
        "preprocessing_owner": "sensor stack, robot host, real-time controller, or accelerator-adjacent interface",
        "afe_status": "required for tactile, force, and analog state signals",
        "event_stream_status": "useful for low-latency motion or sparse visual changes",
        "tactile_force_status": "important for contact-rich tasks",
        "timestamp_sync_status": "critical",
        "front_end_questions": [
            "Which sensors feed the model and at what rate?",
            "Where are camera, tactile, force, and proprioception streams synchronized?",
            "Does the accelerator see raw signals, preprocessed tensors, or action-state embeddings?",
        ],
    },
    "object_detection": {
        "expected_sensors": ["camera", "optional event camera", "optional depth"],
        "raw_signal_type": "image frames or sparse event stream converted to model tensors",
        "preprocessing_owner": "image sensor, ISP, host runtime, or accelerator preprocessor",
        "afe_status": "sensor-owned",
        "event_stream_status": "optional but important for sparse low-latency vision",
        "tactile_force_status": "not primary",
        "timestamp_sync_status": "needed for moving scenes or sensor fusion",
        "front_end_questions": [
            "Is image signal processing counted in latency and energy?",
            "Are event-camera streams supported directly or converted into dense frames?",
            "How do lighting, motion blur, and sensor placement affect model input?",
        ],
    },
    "vision_classification": {
        "expected_sensors": ["camera", "optional presence or environment sensor"],
        "raw_signal_type": "image frame after sensor and image-signal processing",
        "preprocessing_owner": "image sensor, ISP, host runtime, or accelerator preprocessor",
        "afe_status": "sensor-owned",
        "event_stream_status": "not primary",
        "tactile_force_status": "not primary",
        "timestamp_sync_status": "needed if decisions depend on time or multiple sensors",
        "front_end_questions": [
            "Where are resize, crop, color conversion, and normalization done?",
            "Is camera and ISP power included in the product energy number?",
            "What happens under low light, glare, vibration, or dirty lenses?",
        ],
    },
    "edge_llm": {
        "expected_sensors": ["text input", "optional audio", "optional camera", "optional robot state"],
        "raw_signal_type": "tokens, embeddings, or preprocessed multimodal features",
        "preprocessing_owner": "host runtime or upstream perception stack",
        "afe_status": "depends on attached sensors",
        "event_stream_status": "depends on attached vision path",
        "tactile_force_status": "depends on attached body or device",
        "timestamp_sync_status": "needed for multimodal physical context",
        "front_end_questions": [
            "Which upstream model or sensor stack produces tokens or embeddings?",
            "Is multimodal preprocessing counted before the LLM or VLA block?",
            "What sensor context can be stale without hurting the task?",
        ],
    },
}


DOMAIN_SENSOR_OVERRIDES = {
    "sensory_hardware": {
        "expected_sensors": ["event vision", "tactile", "force", "MEMS", "radar", "biological signal"],
        "event_stream_status": "first-class question",
        "tactile_force_status": "first-class question",
        "afe_status": "central product boundary",
    },
    "robotics_vla": {
        "event_stream_status": "useful for motion and low-latency perception",
        "tactile_force_status": "important for grasp, slip, and contact tasks",
        "timestamp_sync_status": "critical",
    },
    "industrial": {
        "afe_status": "often required",
        "timestamp_sync_status": "needed for multi-sensor machine state",
    },
}


def _source_status(measurement_evidence, source_id):
    for source in (measurement_evidence or {}).get("required_sources", []):
        if source.get("id") == source_id:
            return source.get("status", "missing")
    return "missing"


def _summary_value(report, key, default="unknown"):
    return ((report or {}).get("summary") or {}).get(key, default)


def _selected_domain(physical_ai_map, target_profile, modality):
    if physical_ai_map and physical_ai_map.get("selected_domain"):
        return physical_ai_map["selected_domain"]
    if target_profile == "robotics":
        return "robotics_vla"
    if modality == "industrial_anomaly":
        return "industrial"
    if modality == "health_wearable":
        return "sensory_hardware"
    if modality in {"object_detection", "vision_classification"}:
        return "infrastructure"
    return "ambient_home"


def _sensor_profile(selected_domain, modality):
    profile = dict(MODALITY_SENSOR_PROFILES.get(modality, MODALITY_SENSOR_PROFILES["vision_classification"]))
    override = DOMAIN_SENSOR_OVERRIDES.get(selected_domain, {})
    for key, value in override.items():
        if key == "expected_sensors":
            profile[key] = sorted(set(profile.get(key, []) + value))
        else:
            profile[key] = value
    return profile


def _readiness(profile, board_status, power_status):
    if board_status != "imported artifact" and power_status != "imported artifact":
        return "sensor_boundary_unproven"
    if power_status != "imported artifact":
        return "needs_sensor_energy_accounting"
    if profile["timestamp_sync_status"] in {"critical", "needed for multimodal physical context"}:
        return "needs_timestamp_sync_evidence"
    return "prototype_sensor_boundary_review"


def build_sensor_boundary_readiness(
    package_report,
    physical_ai_map=None,
    runtime_profile=None,
    system_boundary=None,
    measurement_evidence=None,
):
    summary = package_report.get("summary", {})
    target_profile = summary.get("target_profile", "wearable")
    modality = summary.get("modality", "vision_classification")
    selected_domain = _selected_domain(physical_ai_map, target_profile, modality)
    profile = _sensor_profile(selected_domain, modality)
    board_status = _source_status(measurement_evidence, "board_runtime")
    power_status = _source_status(measurement_evidence, "power_thermal")
    task_status = _source_status(measurement_evidence, "task_accuracy")
    readiness = _readiness(profile, board_status, power_status)
    total_energy = _summary_value(system_boundary, "total_energy_uj", _summary_value(runtime_profile, "energy_uj", "not profiled"))
    total_latency = _summary_value(system_boundary, "total_latency_ms", _summary_value(runtime_profile, "latency_ms", "not profiled"))
    conversion_energy = _summary_value(system_boundary, "conversion_energy_uj", "unknown")
    memory_energy = _summary_value(system_boundary, "memory_energy_uj", "unknown")
    return {
        "result_type": "sensor_boundary_readiness",
        "schema_version": SENSOR_BOUNDARY_SCHEMA_VERSION,
        "provenance": "derived from selected Physical AI domain, modality, target profile, runtime profile, system boundary, and measurement evidence state",
        "confidence": "low",
        "package_id": package_report.get("package_id"),
        "target_profile": target_profile,
        "modality": modality,
        "selected_domain": selected_domain,
        "readiness": readiness,
        "summary": {
            "plain_reading": (
                "A physical AI product starts with a physical signal, not a tensor. This report shows what must happen before inference and why "
                "sensor, preprocessing, synchronization, and front-end power cannot be hidden behind an inference-only number."
            ),
            "expected_sensors": ", ".join(profile["expected_sensors"]),
            "raw_signal_type": profile["raw_signal_type"],
            "preprocessing_owner": profile["preprocessing_owner"],
            "afe_status": profile["afe_status"],
            "event_stream_status": profile["event_stream_status"],
            "tactile_force_status": profile["tactile_force_status"],
            "timestamp_sync_status": profile["timestamp_sync_status"],
            "energy_accounting_gap": "sensor, AFE, preprocessing, synchronization, and host input costs are not proven as part of completed sensor-to-output energy",
            "board_runtime_status": board_status,
            "power_thermal_status": power_status,
            "task_accuracy_status": task_status,
            "profiled_inference_energy_uj": total_energy,
            "profiled_inference_latency_ms": total_latency,
            "conversion_energy_uj": conversion_energy,
            "memory_energy_uj": memory_energy,
        },
        "boundary_choices": [
            {
                "name": "raw-sensor-adjacent chip",
                "plain_meaning": "The chip sits close to microphones, image sensors, tactile arrays, force sensors, MEMS, or other physical inputs.",
                "what_it_must_own": [
                    "analog front-end or sensor interface",
                    "filtering, sampling, event handling, or feature extraction",
                    "calibration and drift behavior before the model",
                    "timestamping and synchronization when multiple sensors are fused",
                    "sensor-to-output energy and latency accounting",
                ],
                "risk": "higher integration burden, but stronger story for low-power physical AI if measured",
            },
            {
                "name": "digital-tensor accelerator",
                "plain_meaning": "The chip receives already prepared tensors from a host, ISP, DSP, microcontroller, or sensor processor.",
                "what_it_must_own": [
                    "clear tensor format contract",
                    "supported shapes, precision, and layout",
                    "runtime and profiling hooks",
                    "honest exclusion of sensor and preprocessing costs",
                    "handoff contract with the upstream preprocessing owner",
                ],
                "risk": "simpler accelerator boundary, but weaker claim if sensor and preprocessing energy dominate the product",
            },
        ],
        "sensor_front_end_questions": profile["front_end_questions"],
        "evidence_status": [
            {
                "name": "sensor-to-tensor interface",
                "status": "missing interface evidence",
                "why_it_matters": "The product must say exactly what input the chip accepts and who prepares it.",
            },
            {
                "name": "sensor and preprocessing energy",
                "status": power_status,
                "why_it_matters": "Completed product energy includes sensing and preprocessing, not only inference.",
            },
            {
                "name": "sensor-to-output latency",
                "status": board_status,
                "why_it_matters": "Physical AI latency starts at the real signal or event, not at the first model layer.",
            },
            {
                "name": "timestamp and synchronization",
                "status": "missing sync evidence",
                "why_it_matters": "Fusion of camera, tactile, force, motion, or biological signals needs timing rules.",
            },
            {
                "name": "task result under real sensor conditions",
                "status": task_status,
                "why_it_matters": "Sensor noise, placement, drift, and preprocessing can change the task metric.",
            },
        ],
        "evidence_needed": [
            "sensor-to-tensor interface contract",
            "sensor, AFE, preprocessing, host-input, and inference energy in one accounting table",
            "physical-event-to-output latency trace",
            "timestamp and synchronization behavior for multi-sensor inputs",
            "task accuracy under sensor noise, placement, lighting, motion, contact, or drift conditions",
            "clear statement of whether the product is raw-sensor-adjacent or a digital-tensor accelerator",
        ],
        "what_not_to_claim": [
            "Do not count inference-only energy as full sensor-to-output energy.",
            "Do not claim raw sensor support when the chip only accepts prepared digital tensors.",
            "Do not claim event-camera, tactile, force, health, or industrial sensor readiness without naming the interface and preprocessing owner.",
            "Do not hide ISP, DSP, AFE, filtering, windowing, timestamping, host input, or synchronization costs.",
            "Do not assume a model that works on clean tensors will work on noisy physical signals.",
        ],
    }
