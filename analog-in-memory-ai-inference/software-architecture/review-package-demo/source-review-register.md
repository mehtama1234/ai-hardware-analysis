# Source Review Register

This register explains how outside research and company examples may be used in the roadmap.

Outside sources can explain why a topic matters. They do not prove that our analog chip works. They do not prove compatibility, measured speed, measured power, calibration behavior, production readiness, or customer deployment.

Checked date: `2026-08-25`

## Source Use Rules

- Use source-checked examples only as context or case studies.
- Do not use a vendor example as proof that this product supports that vendor's model, sensor, board, or tool.
- Do not use market or funding examples as proof that our chip works.
- Do not use simulator papers as board measurements.
- Do not use board measurements from another chip as proof for this chip.
- Show the checked date when a current product, model, funding, or roadmap example is used.
- If the source is press reporting rather than an official product page, label it as press reporting.

## Checked Examples

### Aspirare Semi

Use: company/topic positioning for analog edge AI inference.

Sources:

- Aspirare Semi homepage: https://www.aspirare.io/

Allowed:

- Use as a motivating company area for analog edge inference.
- Use company-stated claims only as company-stated claims.

Do not claim:

- Do not say this package verified Aspirare silicon performance.
- Do not say prototype, tapeout, or company copy proves production readiness.

### Google DeepMind Gemini Robotics On-Device 2

Use: example of why edge silicon should think about VLA-style inputs, local deployment, robotics runtime constraints, and fast adaptation.

Sources:

- Gemini Robotics On-Device 2 product page: https://deepmind.google/models/gemini-robotics/on-device/
- Gemini Robotics On-Device 2 model card: https://deepmind.google/models/model-cards/gemini-robotics-on-device-2/
- Gemini Robotics 2 blog: https://deepmind.google/blog/gemini-robotics-2-brings-whole-body-intelligence-to-robots/

Allowed:

- Use to motivate transformer/VLA readiness, control-boundary checks, compiler checks, and sensor-boundary checks.

Do not claim:

- Do not claim this app runs Gemini Robotics On-Device 2.
- Do not claim analog in-memory compute is automatically suited to this model.
- Do not claim robot safety or control readiness from VLA inference alone.

### Google DeepMind Gemini Robotics Technical Report

Use: research framing for VLA robotics, low-data adaptation, and multi-embodiment questions.

Source:

- Gemini Robotics: Bringing AI into the Physical World: https://arxiv.org/abs/2503.20020

Allowed:

- Use as research context for the shift from narrow perception models to VLA-style robotics models.

Do not claim:

- Do not treat paper results as evidence that any analog chip supports those models.
- Do not use the paper to claim production deployment readiness.

### Microsoft Rho-alpha

Use: example of physical AI work that expands beyond camera and language toward tactile and force-style inputs.

Sources:

- Microsoft Research: Advancing AI for the physical world: https://www.microsoft.com/en-us/research/story/advancing-ai-for-the-physical-world/
- Rho-Alpha project page, Microsoft Foundry Labs: https://labs.ai.azure.com/projects/rho-alpha/

Allowed:

- Use to motivate sensor-boundary and multimodal compiler concerns.

Do not claim:

- Do not claim availability, API support, benchmark superiority, or customer deployability unless separately sourced.
- Do not claim this app supports Rho-alpha.

### OpenAI And io Products

Use: evidence that major AI labs are exploring new AI hardware and product forms.

Source:

- A letter from Sam & Jony, OpenAI: https://openai.com/sam-and-jony/

Allowed:

- Use only as high-level context for AI companies exploring hardware.

Do not claim:

- Do not claim a specific OpenAI device category, launch date, feature set, or screenless product unless separately sourced by OpenAI.
- Do not use speculative press details as product evidence.

### Sony And Prophesee Event-Based Vision

Use: source-checked example for sensor-boundary work and event-camera input behavior.

Sources:

- Sony Semiconductor event-based vision sensor overview: https://www.sony-semicon.com/en/products/is/industry/evs.html
- Sony and Prophesee IMX636 page: https://www.prophesee.ai/event-based-sensor-imx636-sony-prophesee/
- Sony and Prophesee press release: https://www.sony.com/en/SonyInfo/News/Press/202002/20-0219E/

Allowed:

- Use to explain why event streams are not the same as ordinary video frames.
- Use to motivate sensor-path import templates.

Do not claim:

- Do not claim this analog inference chip supports IMX636 directly without an interface contract.
- Do not claim event-camera energy savings for the full product unless measured in that product.

### NXP NAFEB43388 Analog Front End

Use: source-checked example of sensor front ends and analog signal conditioning.

Sources:

- NXP Analog Front End category page: https://www.nxp.com/products/analog-and-mixed-signal/analog-front-end%3AANALOG-FRONT-END
- NXP NAFEB43388 product page: https://www.nxp.com/products/NAFEB43388
- NXP NAFEB43388 documentation overview: https://docs.nxp.com/bundle/NAFEB43388/page/topics/overview.html

Allowed:

- Use to explain why sensor front ends are separate from AI inference.
- Use to motivate the question: does the chip own raw physical signals or only prepared tensors?

Do not claim:

- Do not claim this app integrates NXP hardware.
- Do not imply NAFEB43388 is a robot-wrist product unless that exact claim is source-checked from NXP material.

## Unchecked Or Hidden By Default

The following examples should stay out of strong product language until they are source-reviewed with links, checked dates, allowed-use notes, and do-not-claim boundaries:

- specific Apple ambient hardware roadmap claims
- specific OpenAI future device categories or launch timing
- Waymo, BYD, Hyundai, Nissan, Geely, Tensor, Prometheus, OpenSpace, PaXini, Anduril, Shield AI, and Saronic examples
- exact paper claims from hardware conference lists unless the paper, abstract, DOI, or proceedings page is linked
- TOPS/W numbers from individual papers unless the measurement scope is attached

## Package Rule

This source register supports context only.

It does not change the final fit answer. It does not unlock board, power, thermal, calibration, task accuracy, update, production, or customer deployment claims.
