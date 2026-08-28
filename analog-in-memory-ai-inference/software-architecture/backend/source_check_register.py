SOURCE_CHECK_REGISTER_SCHEMA_VERSION = "source-check-register-v0.1"
CHECKED_DATE = "2026-08-25"


CHECKED_ITEMS = [
    {
        "id": "aspirare_semi",
        "name": "Aspirare Semi",
        "status": "source checked for company positioning only",
        "source_type": "company homepage",
        "sources": [
            {"label": "Aspirare Semi homepage", "url": "https://www.aspirare.io/"},
        ],
        "checked_claims": [
            "Aspirare describes an AI chip with analog compute cores for edge applications.",
            "Aspirare claims up to 2x higher performance and 10x lower energy consumption compared with traditional solutions.",
            "Aspirare targets edge inference use cases such as wearables, IoT, robotics, and thermally constrained devices.",
        ],
        "allowed_use": [
            "Use as the motivating company/topic area for analog edge AI inference.",
            "Use the claims only as company-stated claims, not as independently measured proof.",
        ],
        "do_not_claim": [
            "Do not say the app verified Aspirare silicon performance.",
            "Do not say prototype, tapeout, or company copy proves production readiness.",
        ],
    },
    {
        "id": "gemini_robotics_on_device_2",
        "name": "Google DeepMind Gemini Robotics On-Device 2",
        "status": "source checked for model positioning, inputs, outputs, and on-device VLA framing",
        "source_type": "official model page and model card",
        "sources": [
            {"label": "Gemini Robotics On-Device 2 product page", "url": "https://deepmind.google/models/gemini-robotics/on-device/"},
            {"label": "Gemini Robotics On-Device 2 model card", "url": "https://deepmind.google/models/model-cards/gemini-robotics-on-device-2/"},
            {"label": "Gemini Robotics 2 blog", "url": "https://deepmind.google/blog/gemini-robotics-2-brings-whole-body-intelligence-to-robots/"},
        ],
        "checked_claims": [
            "Google DeepMind describes Gemini Robotics On-Device 2 as an efficient VLA model optimized to run locally on robotic devices.",
            "The model card lists text, images, and robot proprioception as inputs, and numerical robot actions as outputs.",
            "The model card says the on-device model is based on Gemini Robotics 1.5 technology and on-device Gemma models.",
        ],
        "allowed_use": [
            "Use as an example of why edge silicon must think about VLA-style inputs, local deployment, and robotics runtime constraints.",
            "Use to motivate transformer/VLA readiness, control-boundary, compiler, and sensor-boundary questions.",
        ],
        "do_not_claim": [
            "Do not claim this app runs Gemini Robotics On-Device 2.",
            "Do not claim analog IMC hardware is automatically suited to this model.",
            "Do not claim robot safety or control readiness from VLA inference alone.",
        ],
    },
    {
        "id": "gemini_robotics_technical_report",
        "name": "Google DeepMind Gemini Robotics 2025 Technical Report",
        "status": "source checked for general VLA robotics research framing",
        "source_type": "research paper",
        "sources": [
            {"label": "Gemini Robotics: Bringing AI into the Physical World", "url": "https://arxiv.org/abs/2503.20020"},
        ],
        "checked_claims": [
            "The report introduces Gemini Robotics as a VLA model family for robotics.",
            "The abstract says Gemini Robotics can specialize to new short-horizon tasks from as few as 100 demonstrations and adapt to novel embodiments.",
            "The report discusses safety considerations for robotics foundation models.",
        ],
        "allowed_use": [
            "Use as a research source for the shift from narrow perception models to VLA-style robotics models.",
            "Use to motivate low-data adaptation and multi-embodiment questions.",
        ],
        "do_not_claim": [
            "Do not treat research-report results as evidence that any analog chip supports those models.",
            "Do not use the paper to claim production deployment readiness.",
        ],
    },
    {
        "id": "microsoft_rho_alpha",
        "name": "Microsoft Rho-alpha",
        "status": "source checked for early model positioning",
        "source_type": "official research and project pages",
        "sources": [
            {"label": "Microsoft Research: Advancing AI for the physical world", "url": "https://www.microsoft.com/en-us/research/story/advancing-ai-for-the-physical-world/"},
            {"label": "Rho-Alpha project page, Microsoft Foundry Labs", "url": "https://labs.ai.azure.com/projects/rho-alpha/"},
        ],
        "checked_claims": [
            "Microsoft describes Rho-alpha as translating natural-language commands into control signals for robotic systems doing bimanual manipulation.",
            "Microsoft describes it as a VLA+ model that adds tactile sensing beyond common VLA perceptual inputs.",
            "The Foundry Labs page describes Rho-Alpha as derived from Microsoft Phi-series models and integrating tactile sensing alongside vision.",
        ],
        "allowed_use": [
            "Use as a source-checked example of VLA work expanding beyond camera-plus-language toward tactile and force-style physical inputs.",
            "Use to motivate sensor-boundary and multimodal compiler concerns.",
        ],
        "do_not_claim": [
            "Do not claim availability, API support, benchmark superiority, or customer deployability unless separately sourced.",
            "Do not claim this app supports Rho-alpha.",
        ],
    },
    {
        "id": "openai_io_products",
        "name": "OpenAI and io Products",
        "status": "source checked for acquisition and hardware-design direction only",
        "source_type": "official company announcement",
        "sources": [
            {"label": "A letter from Sam & Jony, OpenAI", "url": "https://openai.com/sam-and-jony/"},
        ],
        "checked_claims": [
            "OpenAI announced in May 2025 that it was combining with io.",
            "OpenAI posted a July 9, 2025 update saying the io Products, Inc. team had officially merged with OpenAI.",
            "The same update says Jony Ive and LoveFrom remain independent and have design and creative responsibilities across OpenAI.",
        ],
        "allowed_use": [
            "Use only as evidence that major AI labs are exploring new AI hardware/product forms.",
        ],
        "do_not_claim": [
            "Do not claim a specific OpenAI device category, launch date, feature set, or screenless product unless separately sourced by OpenAI.",
            "Do not use speculative press details in the app.",
        ],
    },
    {
        "id": "sony_prophesee_imx636",
        "name": "Sony and Prophesee Event-Based Vision",
        "status": "source checked for event-camera sensor behavior and IMX636 product facts",
        "source_type": "official product and press pages",
        "sources": [
            {"label": "Sony Semiconductor event-based vision sensor overview", "url": "https://www.sony-semicon.com/en/products/is/industry/evs.html"},
            {"label": "Sony and Prophesee IMX636 page", "url": "https://www.prophesee.ai/event-based-sensor-imx636-sony-prophesee/"},
            {"label": "Sony and Prophesee press release on stacked event-based vision sensor", "url": "https://www.sony.com/en/SonyInfo/News/Press/202002/20-0219E/"},
        ],
        "checked_claims": [
            "Sony describes event-based vision sensors as detecting luminance changes asynchronously and outputting differential data with coordinates and time information.",
            "Prophesee lists IMX636 as a Sony co-developed event-based vision sensor with 1280 x 720 resolution.",
            "Prophesee lists IMX636 pixel latency as less than 100 microseconds at 1000 lux and standby power as 5 mW.",
        ],
        "allowed_use": [
            "Use as a concrete source-checked example for the sensor-boundary report.",
            "Use to explain why event streams are not the same as ordinary video frames.",
        ],
        "do_not_claim": [
            "Do not claim the analog inference chip supports IMX636 directly without an interface contract.",
            "Do not claim event-camera energy savings for the full product unless measured in that product.",
        ],
    },
    {
        "id": "nxp_nafeb43388",
        "name": "NXP NAFEB43388 Analog Front End",
        "status": "source checked for AFE component positioning only",
        "source_type": "official product page and documentation",
        "sources": [
            {"label": "NXP Analog Front End category page", "url": "https://www.nxp.com/products/analog-and-mixed-signal/analog-front-end%3AANALOG-FRONT-END"},
            {"label": "NXP NAFEB43388 product page", "url": "https://www.nxp.com/products/NAFEB43388"},
            {"label": "NXP NAFEB43388 documentation overview", "url": "https://docs.nxp.com/bundle/NAFEB43388/page/topics/overview.html"},
        ],
        "checked_claims": [
            "NXP describes NAFEB43388 as a compact, 8-input, 24-bit universal configurable analog input AFE with integrated DAC.",
            "NXP describes the product as a multichannel analog front end for high-precision measurements.",
            "The product page lists integrated ADC, DAC, programmable gain amplifier, low-drift voltage reference, and protection features.",
        ],
        "allowed_use": [
            "Use as an example of why sensor front ends and analog signal conditioning are separate from AI inference.",
            "Use to motivate the sensor-boundary question: does the chip own raw physical signals or only prepared tensors?",
        ],
        "do_not_claim": [
            "Do not claim this app integrates NXP hardware.",
            "Do not imply NAFEB43388 is a robot-wrist product unless that exact claim is source-checked from NXP material.",
        ],
    },
]


UNCHECKED_ITEMS = [
    "specific Apple ambient hardware roadmap claims",
    "specific OpenAI future device categories or launch timing",
    "Waymo, BYD, Hyundai, Nissan, Geely, Tensor, Prometheus, OpenSpace, PaXini, Anduril, Shield AI, Saronic examples",
    "exact paper records from the hardware conference list unless the paper, abstract, DOI, or proceedings page is linked",
    "TOPS/W numbers from individual papers unless the scope of measurement is attached",
]


def build_source_check_register(package_report=None):
    return {
        "result_type": "source_check_register",
        "schema_version": SOURCE_CHECK_REGISTER_SCHEMA_VERSION,
        "provenance": "curated source-check register with official pages, product pages, model cards, and papers",
        "confidence": "medium",
        "package_id": (package_report or {}).get("package_id"),
        "checked_date": CHECKED_DATE,
        "summary": {
            "checked_items": len(CHECKED_ITEMS),
            "unchecked_items": len(UNCHECKED_ITEMS),
            "frontend_policy": "show checked examples only with source, checked date, allowed use, and do-not-claim boundary",
            "plain_reading": "Current examples can help explain the landscape, but they must not imply compatibility, measured support, partnership, or production readiness.",
        },
        "use_rules": [
            "Use source-checked examples only as evidence-backed case studies, not as proof that this app supports the vendor product.",
            "Prefer official sources, product pages, model cards, papers, or standards documents.",
            "If a claim is from a news article, label it as press reporting rather than vendor-confirmed fact.",
            "If the source is current-product or roadmap material, show the checked date when it is added to the app.",
            "Do not use any vendor example to imply measured support, compatibility, partnership, or benchmark equivalence unless direct evidence exists.",
        ],
        "checked_items": CHECKED_ITEMS,
        "unchecked_items": UNCHECKED_ITEMS,
        "app_integration_decision": {
            "status": "checked examples may be shown only with guardrails",
            "reason": "The conceptual reports are implemented, but current vendor examples need source, date, allowed-use text, and a claim boundary wherever they appear.",
            "next_step": "Render checked records as guarded examples; keep unchecked items hidden by default.",
        },
    }
