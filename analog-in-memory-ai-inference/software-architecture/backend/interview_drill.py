INTERVIEW_DRILL_SCHEMA_VERSION = "interview-drill-v0.1"


def build_interview_drill(package_report, interview_brief, evidence_brief, research_guide, concept_glossary):
    summary = package_report.get("summary", {})
    evidence_summary = evidence_brief.get("summary", {})
    questions = [
        {
            "id": "Q1",
            "question": "Explain what this company is doing in simple terms.",
            "strong_answer": "They are trying to make AI inference more energy-efficient by doing some repeated math close to memory using analog compute. The value is strongest when moving data costs too much energy or heat for the device.",
            "follow_up": "Which workload is their first target and why is that workload a good fit?",
            "avoid": "Do not say analog is always better than digital.",
        },
        {
            "id": "Q2",
            "question": "Why can analog compute save energy?",
            "strong_answer": "Inference repeats many multiply-add operations. If weights stay near the compute path, less data moves through the memory hierarchy. Less movement can mean less energy and less heat.",
            "follow_up": "What energy costs are still outside the analog core?",
            "avoid": "Do not talk only about core MAC efficiency.",
        },
        {
            "id": "Q3",
            "question": "What makes analog compute hard?",
            "strong_answer": "Analog values are physical signals. They can shift with temperature, voltage, device variation, noise, aging, and calibration state. The model must tolerate that behavior or protect sensitive layers.",
            "follow_up": "How does the company calibrate and validate across real operating conditions?",
            "avoid": "Do not imply numeric error is harmless.",
        },
        {
            "id": "Q4",
            "question": "How should TOPS/W be discussed?",
            "strong_answer": "TOPS/W can be useful, but only if we know what was counted. I would rather compare energy per completed inference at a fixed accuracy and latency target.",
            "follow_up": "Does the number include ADC/DAC, memory, host, idle, fallback, and thermal behavior?",
            "avoid": "Do not treat a peak macro number as product proof.",
        },
        {
            "id": "Q5",
            "question": "What software support is needed?",
            "strong_answer": "Customers need model import, quantization, compiler mapping, runtime execution, profiling, accuracy validation, evidence export, and debugging. Hardware advantage is hard to adopt without that path.",
            "follow_up": "What model formats and operators are supported today?",
            "avoid": "Do not frame software as an afterthought.",
        },
        {
            "id": "Q6",
            "question": "How would you avoid overclaiming prototype progress?",
            "strong_answer": "A prototype chip is important because it shows silicon progress, but production readiness still needs yield, repeatability, calibration cost, packaging, long-term drift, software support, and customer integration.",
            "follow_up": "What evidence would move the product from prototype to customer-ready?",
            "avoid": "Do not say tapeout equals production readiness.",
        },
        {
            "id": "Q7",
            "question": "How would you decide whether a workload is a good fit?",
            "strong_answer": "I would look for repeated matrix-heavy inference, tight power or heat limits, tolerable numeric error, manageable analog/digital boundaries, and a clear task metric.",
            "follow_up": "Which workload has the cleanest first deployment path?",
            "avoid": "Do not treat all edge AI use cases as the same market.",
        },
        {
            "id": "Q8",
            "question": "What would you ask the team in the interview?",
            "strong_answer": "I would ask where the analog boundary sits, how often conversion happens, what is counted in efficiency numbers, how calibration works, what the software path looks like, and what evidence is still missing.",
            "follow_up": "Which of those questions is most important for the role?",
            "avoid": "Do not ask only high-level market questions; show you understand the engineering path.",
        },
    ]
    return {
        "result_type": "interview_drill",
        "schema_version": INTERVIEW_DRILL_SCHEMA_VERSION,
        "provenance": "derived from interview brief, evidence brief, research guide, and concept glossary",
        "confidence": "medium",
        "package_id": package_report.get("package_id"),
        "summary": {
            "target_profile": summary.get("target_profile"),
            "modality": summary.get("modality"),
            "question_count": len(questions),
            "production_readiness": evidence_summary.get("production_readiness", "blocked"),
            "plain_reading": "Use this to rehearse concise answers while keeping claims tied to evidence.",
        },
        "questions": questions,
        "source_context": {
            "interview_brief_points": len(interview_brief.get("what_to_say", [])),
            "research_papers": (research_guide.get("summary") or {}).get("paper_count", 0),
            "glossary_terms": (concept_glossary.get("summary") or {}).get("term_count", 0),
        },
    }
