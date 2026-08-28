INTERVIEW_BRIEF_SCHEMA_VERSION = "interview-brief-v0.1"


def _section(title, lines):
    return [f"## {title}", "", *lines, ""]


def _bullet(text):
    return f"- {text}"


def build_interview_brief(package_report, evidence_brief, system_boundary, workload_fit, toolchain_readiness, concept_glossary=None):
    package_summary = package_report.get("summary", {})
    evidence_summary = evidence_brief.get("summary", {})
    boundary_summary = system_boundary.get("summary", {})
    workload_summary = workload_fit.get("summary", {})
    toolchain_summary = toolchain_readiness.get("summary", {})
    glossary_summary = (concept_glossary or {}).get("summary", {})

    short_answer = (
        "Analog in-memory AI compute is interesting because many inference workloads spend a lot of energy moving numbers "
        "between memory and compute. If repeated matrix-style work can happen close to, or inside, the memory structure, "
        "the system may reduce data movement and heat. The hard part is that analog signals are not exact like digital bits, "
        "so the product has to prove accuracy, calibration, conversion cost, runtime behavior, and software usability for a specific workload."
    )

    first_principles = [
        {
            "title": "Why analog can help",
            "text": "AI inference repeats many multiply-add operations. Digital hardware stores values as bits, moves them to compute units, performs exact logic, and moves results again. Moving data costs energy. Analog or in-memory compute tries to do some of the multiply-add work where the weights already live, so less data has to move.",
        },
        {
            "title": "Why analog is hard",
            "text": "Analog values are physical signals. Physical signals can shift with temperature, voltage, device variation, noise, aging, and calibration state. That means the question is not whether analog is always better. The question is which model layers can tolerate that behavior while still meeting the task metric.",
        },
        {
            "title": "Why the boundary matters",
            "text": "A real product is not only an analog core. Some operators stay digital, data may cross ADC and DAC boundaries, memory traffic still exists, host control still exists, and fallback paths still exist. Energy claims should count completed inference, not only the core macro.",
        },
        {
            "title": "Why workload matters",
            "text": "Edge AI is not one market. A wake-word model, smart camera, robot, industrial sensor, health wearable, and edge LLM have different duty cycles, failure costs, latency targets, model sizes, and proof requirements.",
        },
        {
            "title": "Why software matters",
            "text": "Customers need a path from model import to quantization, compiler mapping, runtime execution, profiling, accuracy validation, evidence export, and debugging. Without that path, a strong circuit is hard to adopt.",
        },
    ]

    talking_points = [
        f"For this package, the selected target is {package_summary.get('target_profile', 'unknown')} and the selected workload is {package_summary.get('modality', 'unknown')}.",
        f"The current selected workload fit is {workload_summary.get('selected_fit', 'unknown')} with score {workload_summary.get('selected_score', 'unknown')}.",
        f"The boundary report counts {boundary_summary.get('analog_layers', 0)} analog layer(s), {boundary_summary.get('digital_layers', 0)} digital layer(s), {boundary_summary.get('fallback_layers', 0)} fallback layer(s), and {boundary_summary.get('boundary_events', 0)} boundary event(s).",
        f"The current evidence supports {evidence_summary.get('supported_lab_claims', 0)} lab claim(s), leaves {evidence_summary.get('needs_review_lab_claims', 0)} needing review, and keeps production readiness {evidence_summary.get('production_readiness', 'blocked')}.",
        f"The software path has {toolchain_summary.get('evidence_attached', 0)} step(s) with evidence attached and {toolchain_summary.get('workflow_available', 0)} step(s) where workflow is available but proof still needs to be attached.",
        f"The glossary contains {glossary_summary.get('term_count', 0)} plain-language term(s) for explaining the architecture without jargon.",
    ]

    questions_to_ask = [
        "Which operators run in the analog array today, and which stay digital?",
        "How often do ADCs and DACs fire during one completed inference?",
        "When you quote efficiency, does it include conversion, SRAM or DRAM traffic, host control, idle power, and thermal behavior?",
        "Which workload is the first customer target: wearable, camera, robot, industrial sensor, health signal, or edge LLM?",
        "What is the software path from ONNX or PyTorch model to mapped executable?",
        "How do you calibrate across temperature, voltage, device variation, and chip-to-chip differences?",
        "What evidence would move a result from prototype demo to production readiness?",
    ]

    do_not_say = [
        "Do not say analog is automatically better than digital.",
        "Do not use TOPS/W alone as proof of product value.",
        "Do not treat a prototype chip or tapeout as production readiness.",
        "Do not treat edge AI as one market.",
        "Do not imply local simulated evidence is measured hardware proof.",
        "Do not talk only about the core and ignore system costs around it.",
    ]

    markdown_lines = [
        "# Interview Brief",
        "",
        f"Package: {package_report.get('package_id', 'unknown')}",
        f"Target: {package_summary.get('target_profile', 'unknown')}",
        f"Workload: {package_summary.get('modality', 'unknown')}",
        "",
        *_section("Short Answer", [short_answer]),
        *_section("First Principles", [_bullet(f"{item['title']}: {item['text']}") for item in first_principles]),
        *_section("What To Say Clearly", [_bullet(item) for item in talking_points]),
        *_section("Questions To Ask", [_bullet(item) for item in questions_to_ask]),
        *_section("What Not To Overclaim", [_bullet(item) for item in do_not_say]),
    ]

    return {
        "result_type": "interview_brief",
        "schema_version": INTERVIEW_BRIEF_SCHEMA_VERSION,
        "provenance": "derived from evidence brief, system boundary, workload fit, and toolchain readiness",
        "confidence": "medium",
        "package_id": package_report.get("package_id"),
        "summary": {
            "target_profile": package_summary.get("target_profile"),
            "modality": package_summary.get("modality"),
            "production_readiness": evidence_summary.get("production_readiness", "blocked"),
            "selected_workload_fit": workload_summary.get("selected_fit"),
            "plain_reading": "Use this as an interview explanation guide. It is careful about what is proven, what is simulated, and what should be asked next.",
        },
        "short_answer": short_answer,
        "first_principles": first_principles,
        "what_to_say": talking_points,
        "questions_to_ask": questions_to_ask,
        "what_not_to_overclaim": do_not_say,
        "markdown": "\n".join(markdown_lines).strip() + "\n",
    }
