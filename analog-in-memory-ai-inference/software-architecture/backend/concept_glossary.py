CONCEPT_GLOSSARY_SCHEMA_VERSION = "concept-glossary-v0.1"


TERMS = [
    {
        "term": "Analog compute",
        "plain_meaning": "Compute with physical signal levels instead of only exact digital bits.",
        "why_it_matters": "It can reduce energy for repeated math when the workload can tolerate small numeric error.",
        "watch_out": "Physical signals can shift with temperature, voltage, noise, device variation, and aging.",
    },
    {
        "term": "In-memory compute",
        "plain_meaning": "Do some work where data already sits instead of moving it back and forth to a separate compute unit.",
        "why_it_matters": "Data movement is often a large part of inference energy.",
        "watch_out": "The system still has to handle control, unsupported operators, conversion, and result movement.",
    },
    {
        "term": "Compute-in-memory / CIM",
        "plain_meaning": "A memory block that can also perform some compute.",
        "why_it_matters": "It can make weight-heavy matrix operations cheaper by reducing weight movement.",
        "watch_out": "A CIM macro result is not the same as full-chip or product efficiency.",
    },
    {
        "term": "Processing-in-memory / PIM",
        "plain_meaning": "A broader term for putting processing close to or inside memory.",
        "why_it_matters": "It targets the cost of moving data through the memory hierarchy.",
        "watch_out": "PIM can be analog, digital, lookup-based, or hybrid; do not mix claims across types.",
    },
    {
        "term": "MAC",
        "plain_meaning": "Multiply-accumulate: multiply numbers and add the results together.",
        "why_it_matters": "Matrix multiplication is built from many MAC operations, so AI inference does a lot of them.",
        "watch_out": "Fast MACs do not guarantee fast completed inference if memory, conversion, or fallback dominates.",
    },
    {
        "term": "ADC",
        "plain_meaning": "Analog-to-digital converter: turns a physical analog signal back into digital bits.",
        "why_it_matters": "The digital system usually needs results in digital form for control, storage, or later layers.",
        "watch_out": "ADC area and energy can be large enough to erase some analog gains.",
    },
    {
        "term": "DAC",
        "plain_meaning": "Digital-to-analog converter: turns digital bits into analog signal levels.",
        "why_it_matters": "Analog arrays often need analog inputs.",
        "watch_out": "Frequent DAC use means frequent boundary cost.",
    },
    {
        "term": "Quantization",
        "plain_meaning": "Use fewer bits to represent model values.",
        "why_it_matters": "Lower precision can reduce memory, energy, and compute cost.",
        "watch_out": "Some layers or workloads lose accuracy when precision is too low.",
    },
    {
        "term": "Calibration",
        "plain_meaning": "Measure and adjust the system so physical behavior matches what the model expects.",
        "why_it_matters": "Analog hardware behavior changes across chips and conditions.",
        "watch_out": "Calibration has cost and may need to be repeated across temperature, voltage, aging, or workload changes.",
    },
    {
        "term": "TOPS/W",
        "plain_meaning": "Trillions of operations per second per watt.",
        "why_it_matters": "It can be a useful peak efficiency signal.",
        "watch_out": "It may exclude ADC/DAC, memory traffic, host work, idle power, or accuracy requirements.",
    },
    {
        "term": "Completed inference energy",
        "plain_meaning": "Energy used to run one full model inference from input to output.",
        "why_it_matters": "This is closer to what a device battery or thermal budget feels.",
        "watch_out": "It must say what was counted and which accuracy and latency target was held fixed.",
    },
    {
        "term": "Analog/digital boundary",
        "plain_meaning": "The point where work moves between analog compute and digital logic.",
        "why_it_matters": "Every boundary can add conversion, scheduling, memory, and validation cost.",
        "watch_out": "Too many crossings can reduce the value of the analog path.",
    },
    {
        "term": "Prototype chip",
        "plain_meaning": "Silicon that demonstrates an idea or early implementation.",
        "why_it_matters": "It is a major step beyond slides or simulation.",
        "watch_out": "It does not prove production readiness by itself.",
    },
    {
        "term": "Production readiness",
        "plain_meaning": "The technology is ready to be built, shipped, supported, and trusted by customers.",
        "why_it_matters": "Customers need repeatable behavior, software support, yield, reliability, and integration.",
        "watch_out": "Lab evidence and prototype demos are not enough on their own.",
    },
]


def build_concept_glossary(package_report=None):
    summary = (package_report or {}).get("summary", {})
    return {
        "result_type": "concept_glossary",
        "schema_version": CONCEPT_GLOSSARY_SCHEMA_VERSION,
        "provenance": "curated plain-language glossary for analog and in-memory AI inference",
        "confidence": "medium",
        "package_id": (package_report or {}).get("package_id"),
        "summary": {
            "target_profile": summary.get("target_profile"),
            "modality": summary.get("modality"),
            "term_count": len(TERMS),
            "plain_reading": "Use this glossary to explain terms simply before discussing claims, evidence, or architecture tradeoffs.",
        },
        "terms": TERMS,
        "do_not_use_as_proof": [
            "A definition explains a concept; it does not prove this package is measured or production-ready.",
            "Use package evidence, not glossary language, when making claims.",
        ],
    }
