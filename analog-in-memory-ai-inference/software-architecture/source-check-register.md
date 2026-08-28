# Source-Check Register

Last checked: 2026-08-25

Purpose: keep current company, product, and paper examples out of the app until they have an explicit source, date, and usage decision.

This file is not a marketing page. It is a working register for deciding what can be cited in the Physical AI and analog in-memory inference workbench.

## Use Rules

- Use source-checked examples only as evidence-backed case studies, not as proof that this app supports the vendor product.
- Prefer official sources, product pages, model cards, papers, or standards documents.
- If a claim is from a news article, label it as press reporting rather than vendor-confirmed fact.
- If the source is current-product or roadmap material, show the checked date when it is later added to the app.
- Do not use any vendor example to imply measured support, compatibility, partnership, or benchmark equivalence unless we have direct evidence.

## Checked Items

### Aspirare Semi

Status: source checked for company positioning only.

Sources:

- [Aspirare Semi homepage](https://www.aspirare.io/)

Checked claims:

- Aspirare describes an AI chip with analog compute cores for edge applications.
- Aspirare claims up to 2x higher performance and 10x lower energy consumption compared with traditional solutions.
- Aspirare targets edge inference use cases such as wearables, IoT, robotics, and thermally constrained devices.

Allowed use:

- Use as the motivating company/topic area for analog edge AI inference.
- Use the claims only as company-stated claims, not as independently measured proof.

Do not claim:

- Do not say the app verified Aspirare silicon performance.
- Do not say prototype, tapeout, or company copy proves production readiness.

### Google DeepMind Gemini Robotics On-Device 2

Status: source checked for model positioning, inputs, outputs, and on-device VLA framing.

Sources:

- [Gemini Robotics On-Device 2 product page](https://deepmind.google/models/gemini-robotics/on-device/)
- [Gemini Robotics On-Device 2 model card](https://deepmind.google/models/model-cards/gemini-robotics-on-device-2/)
- [Gemini Robotics 2 blog](https://deepmind.google/blog/gemini-robotics-2-brings-whole-body-intelligence-to-robots/)

Checked claims:

- Google DeepMind describes Gemini Robotics On-Device 2 as an efficient VLA model optimized to run locally on robotic devices.
- The model card lists text, images, and robot proprioception as inputs, and numerical robot actions as outputs.
- The model card says the on-device model is based on Gemini Robotics 1.5 technology and on-device Gemma models.

Allowed use:

- Use as an example of why edge silicon must think about VLA-style inputs, local deployment, and robotics runtime constraints.
- Use to motivate transformer/VLA readiness, control-boundary, compiler, and sensor-boundary questions.

Do not claim:

- Do not claim this app runs Gemini Robotics On-Device 2.
- Do not claim analog IMC hardware is automatically suited to this model.
- Do not claim robot safety or control readiness from VLA inference alone.

### Google DeepMind Gemini Robotics 2025 Technical Report

Status: source checked for general VLA robotics research framing.

Sources:

- [Gemini Robotics: Bringing AI into the Physical World](https://arxiv.org/abs/2503.20020)

Checked claims:

- The report introduces Gemini Robotics as a VLA model family for robotics.
- The abstract says Gemini Robotics can specialize to new short-horizon tasks from as few as 100 demonstrations and adapt to novel embodiments.
- The report discusses safety considerations for robotics foundation models.

Allowed use:

- Use as a research source for the shift from narrow perception models to VLA-style robotics models.
- Use to motivate low-data adaptation and multi-embodiment questions.

Do not claim:

- Do not treat research-report results as evidence that any analog chip supports those models.
- Do not use the paper to claim production deployment readiness.

### Microsoft Rho-alpha

Status: source checked for early model positioning.

Sources:

- [Microsoft Research: Advancing AI for the physical world](https://www.microsoft.com/en-us/research/story/advancing-ai-for-the-physical-world/)
- [Rho-Alpha project page, Microsoft Foundry Labs](https://labs.ai.azure.com/projects/rho-alpha/)

Checked claims:

- Microsoft describes Rho-alpha as translating natural-language commands into control signals for robotic systems doing bimanual manipulation.
- Microsoft describes it as a VLA+ model that adds tactile sensing beyond common VLA perceptual inputs.
- The Foundry Labs page describes Rho-Alpha as derived from Microsoft Phi-series models and integrating tactile sensing alongside vision.

Allowed use:

- Use as a source-checked example of VLA work expanding beyond camera-plus-language toward tactile and force-style physical inputs.
- Use to motivate sensor-boundary and multimodal compiler concerns.

Do not claim:

- Do not claim availability, API support, benchmark superiority, or customer deployability unless separately sourced.
- Do not claim this app supports Rho-alpha.

### OpenAI and io Products

Status: source checked for acquisition and hardware-design direction only.

Sources:

- [A letter from Sam & Jony, OpenAI](https://openai.com/sam-and-jony/)

Checked claims:

- OpenAI announced in May 2025 that it was combining with io.
- OpenAI posted a July 9, 2025 update saying the io Products, Inc. team had officially merged with OpenAI.
- The same update says Jony Ive and LoveFrom remain independent and have design and creative responsibilities across OpenAI.

Allowed use:

- Use only as evidence that major AI labs are exploring new AI hardware/product forms.

Do not claim:

- Do not claim a specific OpenAI device category, launch date, feature set, or screenless product unless separately sourced by OpenAI.
- Do not use speculative press details in the app.

### Sony and Prophesee Event-Based Vision

Status: source checked for event-camera sensor behavior and IMX636 product facts.

Sources:

- [Sony Semiconductor event-based vision sensor overview](https://www.sony-semicon.com/en/products/is/industry/evs.html)
- [Sony and Prophesee IMX636 page](https://www.prophesee.ai/event-based-sensor-imx636-sony-prophesee/)
- [Sony and Prophesee press release on stacked event-based vision sensor](https://www.sony.com/en/SonyInfo/News/Press/202002/20-0219E/)

Checked claims:

- Sony describes event-based vision sensors as detecting luminance changes asynchronously and outputting differential data with coordinates and time information.
- Prophesee lists IMX636 as a Sony co-developed event-based vision sensor with 1280 x 720 resolution.
- Prophesee lists IMX636 pixel latency as less than 100 microseconds at 1000 lux and standby power as 5 mW.

Allowed use:

- Use as a concrete source-checked example for the sensor-boundary report.
- Use to explain why event streams are not the same as ordinary video frames.

Do not claim:

- Do not claim the analog inference chip supports IMX636 directly without an interface contract.
- Do not claim event-camera energy savings for the full product unless measured in that product.

### NXP NAFEB43388 Analog Front End

Status: source checked for AFE component positioning only.

Sources:

- [NXP Analog Front End category page](https://www.nxp.com/products/analog-and-mixed-signal/analog-front-end%3AANALOG-FRONT-END)
- [NXP NAFEB43388 product page](https://www.nxp.com/products/NAFEB43388)
- [NXP NAFEB43388 documentation overview](https://docs.nxp.com/bundle/NAFEB43388/page/topics/overview.html)

Checked claims:

- NXP describes NAFEB43388 as a compact, 8-input, 24-bit universal configurable analog input AFE with integrated DAC.
- NXP describes the product as a multichannel analog front end for high-precision measurements.
- The product page lists integrated ADC, DAC, programmable gain amplifier, low-drift voltage reference, and protection features.

Allowed use:

- Use as an example of why sensor front ends and analog signal conditioning are separate from AI inference.
- Use to motivate the sensor-boundary question: does the chip own raw physical signals or only prepared tensors?

Do not claim:

- Do not claim this app integrates NXP hardware.
- Do not imply NAFEB43388 is a robot-wrist product unless that exact claim is source-checked from NXP material.

## Not Yet Source Checked

Keep these out of the frontend until checked:

- specific Apple ambient hardware roadmap claims
- specific OpenAI future device categories or launch timing
- Waymo, BYD, Hyundai, Nissan, Geely, Tensor, Prometheus, OpenSpace, PaXini, Anduril, Shield AI, Saronic examples
- exact paper records from the hardware conference list unless the paper, abstract, DOI, or proceedings page is linked
- TOPS/W numbers from individual papers unless the scope of measurement is attached

## App Integration Decision

Current decision: do not add vendor case studies to the frontend yet.

Reason: the conceptual reports are now in place, but the app still needs a structured source field, checked date, source type, and claim-boundary display before current vendor examples are safe to show.

Next implementation option:

- add a backend `source_check_register` artifact that exposes this document as structured JSON
- render a small frontend `Source Checked Examples` panel that only shows records with `allowed_use`
- keep unchecked examples hidden by default
