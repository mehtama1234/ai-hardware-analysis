EVIDENCE_BRIEF_SCHEMA_VERSION = "evidence-brief-v0.1"


def _section(title, lines):
    return [f"## {title}", "", *lines, ""]


def _bullet(text):
    return f"- {text}"


def _status_counts(claims):
    return {
        "supported": sum(1 for claim in claims if claim.get("status") == "supported"),
        "needs_review": sum(1 for claim in claims if claim.get("status") == "needs review"),
        "blocked": sum(1 for claim in claims if claim.get("status") == "blocked"),
    }


def _active_evidence_rows(evidence_audit):
    rows = []
    for source in evidence_audit.get("sources", []):
        rows.append({
            "source_id": source.get("source_id"),
            "artifact_name": source.get("artifact_name"),
            "status": source.get("status"),
            "imported_count": source.get("imported_count", 0),
            "local_generated_count": source.get("local_generated_count", 0),
            "nonlocal_count": source.get("nonlocal_count", 0),
            "latest_import_id": source.get("latest_import_id"),
            "latest_is_local_generated": source.get("latest_is_local_generated", False),
            "latest_payload_status": source.get("latest_payload_status"),
            "refresh_behavior": source.get("local_refresh_behavior"),
        })
    return rows


def _claim_rows(claim_readiness):
    rows = []
    for claim in claim_readiness.get("lab_claims", []):
        rows.append({
            "claim_id": claim.get("id"),
            "name": claim.get("name"),
            "status": claim.get("status"),
            "required_sources": claim.get("required_sources", []),
            "missing_sources": claim.get("missing_sources", []),
            "quality_issues": claim.get("quality_issues", []),
            "safe_statement": claim.get("safe_statement"),
        })
    production = claim_readiness.get("production_claim") or {}
    rows.append({
        "claim_id": production.get("id", "P1"),
        "name": production.get("name", "Production readiness"),
        "status": production.get("status", "blocked"),
        "required_sources": production.get("required_sources", []),
        "missing_sources": production.get("missing_sources", []),
        "quality_issues": [],
        "safe_statement": production.get("safe_statement"),
    })
    return rows


def _what_to_say(package_report, claim_rows, evidence_audit):
    summary = package_report.get("summary", {})
    supported = [claim for claim in claim_rows if claim.get("status") == "supported"]
    needs_review = [claim for claim in claim_rows if claim.get("status") == "needs review"]
    nonlocal_sources = evidence_audit.get("summary", {}).get("sources_with_nonlocal_evidence", 0)
    return [
        f"This package is for {summary.get('target_profile', 'the selected target')} and {summary.get('modality', 'the selected workload')}, not for every edge AI use case.",
        f"The current evidence set supports {len(supported)} lab claim(s) and leaves {len(needs_review)} lab claim(s) needing review.",
        f"There are {nonlocal_sources} required evidence source(s) with non-local evidence attached.",
        "The useful comparison is completed inference at a fixed accuracy, latency, and energy target.",
        "Analog compute is most compelling when repeated matrix-style inference work is power or heat limited and the model can tolerate the numeric behavior of the analog path.",
    ]


def _what_not_to_claim(claim_readiness):
    base = [
        "Do not say analog is automatically better than digital. Digital compute is precise, flexible, mature, and easier to program.",
        "Do not treat a peak TOPS/W number as the full answer. Ask what was counted and compare energy per completed inference.",
        "Do not treat one edge workload as the whole market. Wearables, cameras, robots, and sensors have different limits.",
        "Do not say a prototype or tapeout proves production readiness. Production also needs yield, repeatability, calibration cost, packaging, drift, software support, and customer integration.",
        "Do not turn local simulated evidence into measured hardware proof.",
    ]
    return base + claim_readiness.get("do_not_claim", [])


def _next_evidence(claim_rows, active_evidence):
    next_steps = []
    for claim in claim_rows:
        status = claim.get("status")
        if status == "supported":
            continue
        if claim.get("missing_sources"):
            next_steps.append(
                f"Attach {', '.join(claim['missing_sources'])} before using the claim '{claim.get('name')}'."
            )
        for issue in claim.get("quality_issues", []):
            next_steps.append(f"Resolve evidence quality issue for '{claim.get('name')}': {issue}")
    if any(row.get("latest_is_local_generated") for row in active_evidence):
        next_steps.append("Replace local-generated runtime, power, thermal, and accuracy artifacts with board, lab, or external-tool evidence before making measured claims.")
    next_steps.append("Keep production readiness blocked until silicon repeatability, calibration flow, software path, and real operating conditions are proven.")
    return next_steps


def _readiness_ladder(claim_rows, active_evidence):
    supported = [claim for claim in claim_rows if claim.get("status") == "supported" and claim.get("claim_id") != "P1"]
    needs_review = [claim for claim in claim_rows if claim.get("status") == "needs review"]
    blocked = [claim for claim in claim_rows if claim.get("status") == "blocked" and claim.get("claim_id") != "P1"]
    nonlocal_sources = sum(1 for row in active_evidence if row.get("nonlocal_count", 0) > 0)
    local_latest = sum(1 for row in active_evidence if row.get("latest_is_local_generated"))
    all_lab_supported = len(supported) == 4 and not needs_review and not blocked
    return [
        {
            "level": 0,
            "name": "Concept discussion",
            "status": "allowed",
            "what_it_allows": "You can explain the architecture idea, why analog compute can reduce data movement for repeated matrix math, and where the hard engineering risks are.",
            "evidence_needed": "No package evidence is required, but you should avoid measured performance language.",
            "do_not_cross": "Do not imply this proves a model, a board, or a customer workload.",
        },
        {
            "level": 1,
            "name": "Package analysis",
            "status": "allowed",
            "what_it_allows": "You can discuss this model's estimated operator fit, boundary cost, quantization risk, and simulated completed-inference result.",
            "evidence_needed": "Keep the language tied to the package analysis and simulation provenance.",
            "do_not_cross": "Do not call estimates measured hardware results.",
        },
        {
            "level": 2,
            "name": "Evidence-backed lab claims",
            "status": "allowed" if supported else "blocked",
            "what_it_allows": f"You can make the supported lab claim(s): {', '.join(claim['name'] for claim in supported) or 'none yet'}.",
            "evidence_needed": "Attach normalized compiler, runtime, power, analog-error, and task-accuracy artifacts for each claim you want to make.",
            "do_not_cross": "Do not use one supported lab claim as proof for another claim.",
        },
        {
            "level": 3,
            "name": "Measured workload claim",
            "status": "allowed" if all_lab_supported and nonlocal_sources >= 5 and local_latest == 0 else "needs evidence",
            "what_it_allows": "You can discuss completed-inference accuracy, latency, and energy for one defined model, dataset, hardware setup, and target condition.",
            "evidence_needed": "Use non-local board or external-tool evidence for every required source, with passing payload checks and counted-cost details.",
            "do_not_cross": "Do not generalize one workload result to all edge AI or all model classes.",
        },
        {
            "level": 4,
            "name": "Production readiness",
            "status": "blocked",
            "what_it_allows": "No production readiness claim is allowed from this package alone.",
            "evidence_needed": "Prove yield, chip-to-chip repeatability, calibration cost, drift, packaging, software integration, customer setup, and operating-condition behavior.",
            "do_not_cross": "Do not say a prototype, tapeout, or lab package proves production readiness.",
        },
    ]


def _markdown(package_report, claim_rows, active_evidence, readiness_ladder, what_to_say, what_not_to_claim, next_evidence):
    summary = package_report.get("summary", {})
    claim_table = [
        "| Claim | Status | Safe reading |",
        "| --- | --- | --- |",
    ]
    for claim in claim_rows:
        claim_table.append(
            f"| {claim.get('name', 'claim')} | {claim.get('status', 'unknown')} | {claim.get('safe_statement', 'No statement available.')} |"
        )
    evidence_table = [
        "| Source | Imports | Local | Non-local | Latest |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for row in active_evidence:
        latest = "local" if row.get("latest_is_local_generated") else "non-local" if row.get("latest_import_id") else "missing"
        evidence_table.append(
            f"| {row.get('source_id', 'source')} | {row.get('imported_count', 0)} | {row.get('local_generated_count', 0)} | {row.get('nonlocal_count', 0)} | {latest} |"
        )
    ladder_table = [
        "| Level | Status | What it allows | Next proof |",
        "| ---: | --- | --- | --- |",
    ]
    for item in readiness_ladder:
        ladder_table.append(
            f"| {item.get('level')} {item.get('name')} | {item.get('status')} | {item.get('what_it_allows')} | {item.get('evidence_needed')} |"
        )
    lines = [
        "# Evidence Brief",
        "",
        f"Package: {package_report.get('package_id', 'unknown')}",
        f"Project: {summary.get('project_name') or 'not attached'}",
        f"Target: {summary.get('target_profile', 'unknown')}",
        f"Modality: {summary.get('modality', 'unknown')}",
        f"Claim level: {package_report.get('claim_level', 'unknown')}",
        "Production readiness remains blocked. Lab evidence can support narrow lab claims, not production readiness.",
        "",
        *_section("Claim Table", claim_table),
        *_section("Active Evidence", evidence_table),
        *_section("Readiness Ladder", ladder_table),
        *_section("What To Say Clearly", [_bullet(item) for item in what_to_say]),
        *_section("What Not To Claim", [_bullet(item) for item in what_not_to_claim]),
        *_section("Next Evidence", [_bullet(item) for item in next_evidence]),
    ]
    return "\n".join(lines).strip() + "\n"


def build_evidence_brief(package_report, measurement_evidence, claim_readiness, evidence_audit):
    claim_rows = _claim_rows(claim_readiness)
    active_evidence = _active_evidence_rows(evidence_audit)
    counts = _status_counts([row for row in claim_rows if row.get("claim_id") != "P1"])
    ladder = _readiness_ladder(claim_rows, active_evidence)
    say = _what_to_say(package_report, claim_rows, evidence_audit)
    do_not_claim = _what_not_to_claim(claim_readiness)
    next_steps = _next_evidence(claim_rows, active_evidence)
    confidence = "medium" if counts["supported"] and not counts["needs_review"] else "low"
    brief = {
        "result_type": "evidence_brief",
        "schema_version": EVIDENCE_BRIEF_SCHEMA_VERSION,
        "package_id": package_report.get("package_id") or measurement_evidence.get("summary", {}).get("package_id"),
        "provenance": "derived from package evidence audit and claim readiness",
        "confidence": confidence,
        "summary": {
            "claim_level": package_report.get("claim_level"),
            "supported_lab_claims": counts["supported"],
            "needs_review_lab_claims": counts["needs_review"],
            "blocked_lab_claims": counts["blocked"],
            "production_readiness": claim_readiness.get("production_claim", {}).get("status", "blocked"),
            "active_imports": evidence_audit.get("summary", {}).get("total_imports", 0),
            "local_generated_imports": evidence_audit.get("summary", {}).get("local_generated_imports", 0),
            "nonlocal_imports": evidence_audit.get("summary", {}).get("nonlocal_imports", 0),
            "plain_reading": "Production readiness remains blocked. Lab claims depend on the attached evidence and its quality.",
        },
        "claim_table": claim_rows,
        "active_evidence": active_evidence,
        "readiness_ladder": ladder,
        "what_to_say": say,
        "what_not_to_claim": do_not_claim,
        "next_evidence": next_steps,
    }
    brief["markdown"] = _markdown(package_report, claim_rows, active_evidence, ladder, say, do_not_claim, next_steps)
    return brief
