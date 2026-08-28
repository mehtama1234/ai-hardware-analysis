PHYSICAL_AI_MAP_SCHEMA_VERSION = "physical-ai-map-v0.1"


DOMAIN_DEFINITIONS = {
    "mobility": {
        "label": "Autonomous mobility and transportation",
        "modalities": ["vision_classification", "object_detection", "robotics_perception"],
        "target_profiles": ["robotics", "camera"],
        "sensors": ["camera", "radar", "lidar", "inertial", "GPS", "vehicle health"],
        "typical_tasks": ["perception", "detection", "localization", "navigation support"],
        "why_it_matters": "Moving systems need local answers because late or unstable perception can be useless.",
        "where_edge_compute_matters": [
            "low-latency perception near sensors",
            "less raw data movement across the vehicle",
            "operation when cloud connectivity is unavailable",
            "lower heat in sealed or compact compute modules",
        ],
        "where_analog_may_help": [
            "repeated matrix-heavy perception blocks",
            "sensor-adjacent inference where moving data is expensive",
            "compact models on small mobile platforms",
        ],
        "where_it_gets_harder": [
            "rare scenes matter more than average accuracy",
            "sensor fusion and temporal consistency are hard",
            "safety-critical decisions require stronger validation",
            "planning and control are separate from inference",
        ],
        "evidence_needed": [
            "completed inference latency at the real sensor rate",
            "accuracy on difficult and rare scenes",
            "system power and heat under realistic duty cycle",
            "fallback and conversion cost measured with the full stack",
        ],
        "do_not_claim": [
            "Do not claim vehicle or autonomy readiness from an inference benchmark alone.",
            "Do not treat perception acceleration as proof of planning or control safety.",
        ],
    },
    "ambient_home": {
        "label": "Smart home and ambient hardware",
        "modalities": ["audio_wake_word", "vision_classification", "object_detection"],
        "target_profiles": ["wearable", "camera"],
        "sensors": ["microphone", "camera", "presence", "environment"],
        "typical_tasks": ["wake-word", "event detection", "local classification", "presence response"],
        "why_it_matters": "Ambient devices need always-available local inference without high idle power, heat, or delay.",
        "where_edge_compute_matters": [
            "low idle power",
            "fast local response",
            "less raw audio or video upload",
            "operation before or without a cloud call",
        ],
        "where_analog_may_help": [
            "always-on small models",
            "repeated audio or image inference",
            "compact devices with limited cooling",
        ],
        "where_it_gets_harder": [
            "false wake-ups annoy users",
            "missed events reduce trust",
            "consumer products need simple updates and low cost",
            "privacy depends on the whole data path, not only local inference",
        ],
        "evidence_needed": [
            "energy per wake or local inference",
            "idle power over realistic duty cycle",
            "false accept and false reject behavior",
            "what data stays local and what leaves the device",
        ],
        "do_not_claim": [
            "Do not say local inference alone proves privacy.",
            "Do not use one quiet-room result as proof of always-on behavior.",
        ],
    },
    "industrial": {
        "label": "Industrial AI and engineering systems",
        "modalities": ["industrial_anomaly", "vision_classification", "object_detection"],
        "target_profiles": ["wearable", "camera", "robotics"],
        "sensors": ["vibration", "image", "acoustic", "thermal", "current", "pressure"],
        "typical_tasks": ["anomaly detection", "defect classification", "wear estimate", "quality inspection"],
        "why_it_matters": "Industrial systems often need continuous local sensing near machines, production lines, or assets.",
        "where_edge_compute_matters": [
            "always-on machine monitoring",
            "low-latency defect detection",
            "less raw sensor transfer from many machines",
            "local inference when data is sensitive or connectivity is weak",
        ],
        "where_analog_may_help": [
            "steady repeated inference close to sensors",
            "low-power retrofit sensor nodes",
            "compact vision models for inspection",
        ],
        "where_it_gets_harder": [
            "rare failures are the events that matter most",
            "calibration data may not include enough true faults",
            "site-to-site variation can dominate model behavior",
            "integration with existing industrial workflows can be the blocker",
        ],
        "evidence_needed": [
            "rare-fault recall",
            "threshold stability after quantization and analog error",
            "behavior across machine state, temperature, vibration, and sensor aging",
            "measured power for long-running monitoring",
        ],
        "do_not_claim": [
            "Do not approve from average accuracy alone.",
            "Do not treat a lab sensor trace as proof for every site.",
        ],
    },
    "infrastructure": {
        "label": "Smart infrastructure and asset management",
        "modalities": ["vision_classification", "object_detection", "industrial_anomaly", "edge_llm"],
        "target_profiles": ["camera", "wearable"],
        "sensors": ["camera", "location", "asset sensors", "environment", "logs"],
        "typical_tasks": ["detection", "search support", "progress tracking", "asset status"],
        "why_it_matters": "Distributed assets need local filtering and state detection before data reaches a central system.",
        "where_edge_compute_matters": [
            "local camera or sensor analytics",
            "reduced raw video upload",
            "fast alerts near the asset",
            "operation during unreliable network conditions",
        ],
        "where_analog_may_help": [
            "repeated detection or classification",
            "battery-powered monitoring nodes",
            "local filtering before cloud indexing",
        ],
        "where_it_gets_harder": [
            "sites change over time",
            "cameras and sensors may be poorly placed",
            "workflow integration is part of the product",
            "one benchmark does not prove a deployment",
        ],
        "evidence_needed": [
            "site-level accuracy across lighting and layout changes",
            "enclosure-level power and thermal behavior",
            "network savings from local inference",
            "operator workflow impact",
        ],
        "do_not_claim": [
            "Do not call local detection a full asset-management product.",
            "Do not claim site readiness without site data.",
        ],
    },
    "agriculture": {
        "label": "Precision agriculture",
        "modalities": ["vision_classification", "object_detection", "industrial_anomaly"],
        "target_profiles": ["camera", "robotics"],
        "sensors": ["image", "multispectral", "soil", "weather", "motion"],
        "typical_tasks": ["weed detection", "crop health", "harvest support", "irrigation decision"],
        "why_it_matters": "Field systems need local inference under outdoor variation, motion, dust, and limited connectivity.",
        "where_edge_compute_matters": [
            "low-latency crop or weed detection",
            "operation away from reliable networks",
            "battery or solar-powered sensing",
            "less cloud upload from field devices",
        ],
        "where_analog_may_help": [
            "high-rate vision on field equipment",
            "always-on low-power sensors",
            "compact devices without large batteries or cooling",
        ],
        "where_it_gets_harder": [
            "outdoor variation is severe",
            "ruggedization may matter more than peak efficiency",
            "maintenance must work for non-expert users",
            "deployment can be seasonal and cost-sensitive",
        ],
        "evidence_needed": [
            "field data across light, weather, crop stage, and motion",
            "latency at real equipment speed",
            "outdoor enclosure power and thermal behavior",
            "economic metric such as fewer passes, less labor, or less chemical use",
        ],
        "do_not_claim": [
            "Do not generalize from clean field images to all outdoor conditions.",
            "Do not ignore ruggedization and maintenance cost.",
        ],
    },
    "defense_aerospace": {
        "label": "Defense, aerospace, and extreme environments",
        "modalities": ["robotics_perception", "object_detection", "vision_classification", "industrial_anomaly"],
        "target_profiles": ["robotics", "camera", "wearable"],
        "sensors": ["image", "radar", "RF", "inertial", "health", "thermal"],
        "typical_tasks": ["navigation support", "detection", "monitoring", "health estimation"],
        "why_it_matters": "Extreme systems often cannot rely on cloud compute and must meet strict power, thermal, and reliability limits.",
        "where_edge_compute_matters": [
            "local perception and navigation support",
            "autonomy when communication is delayed or denied",
            "compact compute in weight-limited platforms",
            "thermal control in sealed or harsh environments",
        ],
        "where_analog_may_help": [
            "repeated perception or signal models under a power budget",
            "sensor-side filtering before higher-level processing",
            "always-on monitoring with limited energy",
        ],
        "where_it_gets_harder": [
            "reliability expectations are high",
            "environmental variation is extreme",
            "security and supply-chain concerns matter",
            "testing must cover rare operating conditions",
        ],
        "evidence_needed": [
            "behavior across temperature, voltage, shock, vibration, and aging",
            "fault behavior and recovery",
            "measured mission-duty-cycle power",
            "clear safety boundary between AI output and final control authority",
        ],
        "do_not_claim": [
            "Do not claim mission readiness from simulated inference only.",
            "Do not collapse reliability, safety, and security into a single performance number.",
        ],
    },
    "sensory_hardware": {
        "label": "Sensory hardware and machine-readable signals",
        "modalities": ["audio_wake_word", "health_wearable", "industrial_anomaly", "robotics_perception"],
        "target_profiles": ["wearable", "robotics"],
        "sensors": ["event vision", "tactile", "force", "MEMS", "radar", "biological signal"],
        "typical_tasks": ["feature extraction", "event detection", "signal classification", "local filtering"],
        "why_it_matters": "Better sensing can reduce compute by turning raw physical changes into useful events or features.",
        "where_edge_compute_matters": [
            "sensor-side preprocessing",
            "low-latency feature extraction",
            "local event detection",
            "less bandwidth before the host",
        ],
        "where_analog_may_help": [
            "compute close to sensor memory",
            "small repeated models near the signal source",
            "low-power always-on filtering",
        ],
        "where_it_gets_harder": [
            "sensor noise and calibration dominate behavior",
            "data formats may be unusual",
            "developer tools may be immature",
            "benchmark translation can be hard",
        ],
        "evidence_needed": [
            "sensor-specific failure analysis",
            "latency from physical event to model output",
            "energy for sensing plus preprocessing plus inference",
            "calibration and drift behavior",
        ],
        "do_not_claim": [
            "Do not count only inference energy when preprocessing and sensor power are outside the number.",
            "Do not assume normal image or audio tooling covers unusual sensors.",
        ],
    },
    "robotics_vla": {
        "label": "Robotics and VLA systems",
        "modalities": ["robotics_perception", "edge_llm", "object_detection"],
        "target_profiles": ["robotics"],
        "sensors": ["camera", "language", "proprioception", "force", "tactile", "depth"],
        "typical_tasks": ["perceive", "plan support", "action support", "state estimation"],
        "why_it_matters": "Embodied systems need local intelligence that works with a body, sensors, timing limits, and safety controllers.",
        "where_edge_compute_matters": [
            "local perception and action support",
            "low-latency sensor-to-decision loops",
            "operation when cloud connectivity is absent or too slow",
            "reduced data movement from cameras and sensors",
        ],
        "where_analog_may_help": [
            "repeated perception blocks",
            "matrix-heavy policy or state-estimation layers",
            "sensor-side inference before a higher-level planner",
        ],
        "where_it_gets_harder": [
            "action errors affect the physical world",
            "latency jitter can matter more than average speed",
            "safety controllers must remain outside the neural model",
            "many VLA operators may stay digital",
        ],
        "evidence_needed": [
            "task success rate on the target body",
            "worst-case latency and jitter",
            "collision, force, and safety-controller behavior",
            "behavior when sensors shift or objects move unexpectedly",
        ],
        "do_not_claim": [
            "Do not claim robot control readiness from inference alone.",
            "Do not claim one mapping supports every body, sensor layout, or action space.",
        ],
    },
}


MODALITY_DOMAIN_PRIORITIES = {
    "audio_wake_word": ["ambient_home", "sensory_hardware"],
    "vision_classification": ["ambient_home", "infrastructure", "industrial", "mobility"],
    "object_detection": ["infrastructure", "mobility", "agriculture", "robotics_vla"],
    "robotics_perception": ["robotics_vla", "mobility", "defense_aerospace", "sensory_hardware"],
    "industrial_anomaly": ["industrial", "infrastructure", "sensory_hardware"],
    "health_wearable": ["sensory_hardware", "ambient_home", "industrial"],
    "edge_llm": ["robotics_vla", "infrastructure", "ambient_home"],
}


TARGET_DOMAIN_PRIORITIES = {
    "wearable": ["ambient_home", "sensory_hardware", "industrial"],
    "camera": ["infrastructure", "ambient_home", "mobility", "agriculture"],
    "robotics": ["robotics_vla", "mobility", "defense_aerospace", "agriculture"],
}


def _selected_domain(target_profile, modality):
    scores = {domain_id: 0 for domain_id in DOMAIN_DEFINITIONS}
    for rank, domain_id in enumerate(MODALITY_DOMAIN_PRIORITIES.get(modality, [])):
        scores[domain_id] += 30 - rank * 4
    for rank, domain_id in enumerate(TARGET_DOMAIN_PRIORITIES.get(target_profile, [])):
        scores[domain_id] += 24 - rank * 3
    for domain_id, domain in DOMAIN_DEFINITIONS.items():
        if modality in domain["modalities"]:
            scores[domain_id] += 8
        if target_profile in domain["target_profiles"]:
            scores[domain_id] += 6
    return max(scores, key=lambda key: (scores[key], DOMAIN_DEFINITIONS[key]["label"]))


def _fit_label(score):
    if score >= 70:
        return "strong conceptual fit"
    if score >= 50:
        return "possible conceptual fit"
    if score >= 30:
        return "narrow fit"
    return "weak fit"


def _domain_score(domain, selected_domain_id, target_profile, modality, workload_fit, system_boundary):
    score = 20
    if modality in domain["modalities"]:
        score += 20
    if target_profile in domain["target_profiles"]:
        score += 16
    if domain is DOMAIN_DEFINITIONS[selected_domain_id]:
        score += 18
    selected_workload_score = ((workload_fit or {}).get("summary") or {}).get("selected_score")
    if selected_workload_score is not None and modality in domain["modalities"]:
        score += min(18, max(0, float(selected_workload_score) / 5))
    boundary_summary = (system_boundary or {}).get("summary") or {}
    boundary_events = int(boundary_summary.get("boundary_events", 0) or 0)
    fallback_layers = int(boundary_summary.get("fallback_layers", 0) or 0)
    score -= min(14, boundary_events * 1.5)
    score -= min(12, fallback_layers * 2)
    return round(max(0, min(100, score)), 1)


def _main_gap(modality, target_profile):
    if modality == "audio_wake_word":
        return "full duty-cycle idle energy plus false accept and false reject evidence"
    if modality in {"vision_classification", "object_detection"}:
        return "real-scene accuracy plus system-level energy and thermal evidence"
    if modality == "robotics_perception" or target_profile == "robotics":
        return "worst-case latency, jitter, safety handoff, and task success evidence"
    if modality == "industrial_anomaly":
        return "rare-fault recall and threshold stability evidence"
    if modality == "health_wearable":
        return "user-dependent signal quality, sensitivity, specificity, and long-duty-cycle energy evidence"
    if modality == "edge_llm":
        return "token/task quality, memory movement, attention support, and completed inference energy evidence"
    return "system-level accuracy, latency, energy, and reliability evidence"


def _analog_fit(summary, system_boundary):
    score = summary.get("selected_score")
    boundary_summary = (system_boundary or {}).get("summary") or {}
    fallback_layers = int(boundary_summary.get("fallback_layers", 0) or 0)
    boundary_events = int(boundary_summary.get("boundary_events", 0) or 0)
    if score is None:
        return "unknown until package analysis runs"
    if float(score) >= 70 and fallback_layers <= 1:
        return "promising if measured evidence confirms the full system"
    if float(score) >= 50:
        return "possible, but boundary and fallback costs must be counted"
    if boundary_events > 5 or fallback_layers > 2:
        return "limited until boundary and fallback costs are reduced"
    return "early analysis only"


def build_physical_ai_map(package_report, workload_fit=None, system_boundary=None, measurement_evidence=None):
    package_summary = package_report.get("summary", {})
    target_profile = package_summary.get("target_profile", "wearable")
    modality = package_summary.get("modality", "vision_classification")
    selected_domain_id = _selected_domain(target_profile, modality)
    selected_definition = DOMAIN_DEFINITIONS[selected_domain_id]
    workload_summary = (workload_fit or {}).get("summary") or {}
    domains = []
    for domain_id, domain in DOMAIN_DEFINITIONS.items():
        score = _domain_score(domain, selected_domain_id, target_profile, modality, workload_fit, system_boundary)
        domains.append({
            "id": domain_id,
            "label": domain["label"],
            "selected": domain_id == selected_domain_id,
            "score": score,
            "fit": _fit_label(score),
            "why_it_matters": domain["why_it_matters"],
            "sensors": domain["sensors"],
            "typical_tasks": domain["typical_tasks"],
            "where_edge_compute_matters": domain["where_edge_compute_matters"],
            "where_analog_may_help": domain["where_analog_may_help"],
            "where_it_gets_harder": domain["where_it_gets_harder"],
            "evidence_needed": domain["evidence_needed"],
            "do_not_claim": domain["do_not_claim"],
        })
    domains.sort(key=lambda item: (not item["selected"], -item["score"], item["label"]))
    required_sources = (measurement_evidence or {}).get("required_sources", [])
    missing_sources = [
        item["id"]
        for item in required_sources
        if item.get("status") not in {"evidence attached", "complete"}
    ]
    return {
        "result_type": "physical_ai_map",
        "schema_version": PHYSICAL_AI_MAP_SCHEMA_VERSION,
        "provenance": "derived from selected target profile, modality, workload fit, system boundary, and evidence state",
        "confidence": "low",
        "selected_domain": selected_domain_id,
        "selected_domain_label": selected_definition["label"],
        "target_profile": target_profile,
        "modality": modality,
        "summary": {
            "plain_reading": (
                f"This workload is closest to {selected_definition['label']}. "
                "The analog story is useful only if the selected domain's accuracy, latency, energy, and reliability evidence are collected together."
            ),
            "analog_fit": _analog_fit(workload_summary, system_boundary),
            "main_evidence_gap": _main_gap(modality, target_profile),
            "selected_workload_fit": workload_summary.get("selected_fit", "unknown"),
            "selected_workload_score": workload_summary.get("selected_score", "unknown"),
            "missing_evidence_sources": missing_sources,
        },
        "domains": domains,
        "cross_domain_rules": [
            "Do not say edge AI or Physical AI is one market.",
            "Do not use TOPS/W alone as proof.",
            "Do not treat a prototype chip as production readiness.",
            "Do not claim analog compute is automatically better than digital compute.",
            "Compare completed inference at fixed accuracy, latency, energy, and reliability.",
            "Keep current vendor, product, and paper examples out of the app until source-checked.",
        ],
        "source_check_policy": {
            "status": "conceptual_map_only",
            "plain_rule": "This artifact uses conceptual domain guidance and avoids current vendor or product claims until sources are attached.",
        },
    }
