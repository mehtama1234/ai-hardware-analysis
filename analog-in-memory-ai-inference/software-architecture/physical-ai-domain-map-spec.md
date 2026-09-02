# Physical AI Domain Map Spec

Start from the [Connected System Map](connected-system-map.html). This specification uses the same contract: object, constraint, design move, evidence, allowed claim, refused claim, and next handoff.

## Purpose

This document adds the missing layer above the analog in-memory inference workbench.

The current workbench answers a lower-level question:

```text
Can this model run well on a power-constrained edge AI compute path?
```

The Physical AI layer answers the larger question:

```text
Where does this kind of edge AI compute matter in the real world, and what evidence would prove it?
```

Physical AI should not be treated as only robots. A robot is one visible form. The wider idea is any system that uses sensors, local compute, and software to understand the physical world and act on it. Sometimes the action is movement. Sometimes it is a warning, a control signal, a maintenance decision, a changed display, or a local answer from a camera.

This spec should become a first-class frontend and backend artifact named `physical_ai_map`.

## Core Framing

Physical AI has four basic parts:

```text
physical world
  -> sensors
  -> local or nearby model inference
  -> decision logic
  -> action, alert, control, or human handoff
```

Analog and in-memory AI inference sits inside the model-inference part. It is not the whole system.

The careful statement is:

```text
Analog or in-memory compute can be useful when the physical system must run AI near the sensor, under tight power or heat limits, and the model can tolerate the numeric behavior of the hardware.
```

The unsafe statement is:

```text
Physical AI needs analog compute, therefore analog compute wins everywhere.
```

That is too broad. Many Physical AI systems need precise digital control, flexible software, large memory, high safety assurance, cloud reasoning, or mature tooling more than they need analog efficiency.

## Why This Matters For The Product

An AI chip company is not only selling a circuit. It is selling a way to make edge inference practical in devices where power, heat, battery, size, or local latency are hard limits.

The frontend should therefore show two layers:

```text
Layer 1: Physical AI domain map
  Which real-world system is this for?
  What sensors does it use?
  What does the model need to do?
  What counts as failure?
  Where does edge compute matter?

Layer 2: Analog in-memory model-fit workbench
  Which operators run on analog?
  Which operators stay digital?
  What quantization is safe?
  What are the ADC/DAC and memory costs?
  What evidence supports the claim?
```

Without Layer 1, the workbench can become technically correct but disconnected from the customer story. Without Layer 2, the Physical AI story can become broad market language with no proof.

## Domain Map

### Autonomous Mobility And Transportation

Autonomous mobility includes cars, robotaxis, delivery vehicles, drones, and other moving systems that must understand a changing outdoor or indoor world.

The sensor mix can include cameras, radar, lidar, inertial sensors, GPS, wheel sensors, microphones, and vehicle-health sensors. The model does not see clean database rows. It sees noisy physical signals that change with lighting, weather, speed, vibration, occlusion, and sensor placement.

The hard part is not only recognizing objects. The system must do useful work within a strict time budget. Late answers can be useless. Unstable answers can be dangerous. Average accuracy is not enough because rare cases matter.

Where edge compute matters:

- low-latency perception near the sensor
- reduced data movement across the vehicle
- less heat in sealed or compact compute modules
- graceful behavior when cloud connectivity is absent
- repeated inference over camera, radar, or sensor streams

Where analog or in-memory compute may help:

- repeated matrix-heavy perception blocks
- compact neural networks that run continuously
- sensor-adjacent inference where moving raw data is expensive
- power-limited subsystems such as small drones or low-power monitors

Where it gets harder:

- safety-critical decisions need strong validation
- perception is only one part of planning and control
- sensor fusion and temporal consistency matter
- rare-case behavior is more important than average benchmark score
- software, diagnostics, and certification burden can dominate

Evidence needed before a strong claim:

- completed inference latency at the required frame or sensor rate
- accuracy on the target task, including rare and difficult scenes
- power and heat measured at system level
- behavior across temperature, voltage, vibration, and sensor variation
- proof that fallback digital paths do not erase the gain

### Smart Home And Ambient Hardware

Ambient hardware includes smart displays, cameras, speakers, appliances, locks, lighting, environmental sensors, and future AI-first devices that respond to people and rooms.

These systems are usually not dramatic. They sit in the background. They listen, see, sense, classify, wake up, or make small decisions. Their value often comes from being always available without becoming hot, slow, noisy, or battery hungry.

Where edge compute matters:

- wake-word and event detection
- local image or audio classification
- privacy-preserving inference without always streaming raw data
- low idle power for always-on devices
- fast response when a person speaks, moves, or enters a room

Where analog or in-memory compute may help:

- always-on small models
- repeated audio or image inference
- compact devices with limited cooling
- devices that need local response before a cloud call

Where it gets harder:

- false wake-ups annoy users
- missed events reduce trust
- consumer products need low cost and simple updates
- software support and developer experience matter as much as raw efficiency
- privacy claims require careful system design, not just local compute

Evidence needed before a strong claim:

- energy per wake or per local inference
- idle power over a realistic duty cycle
- false accept and false reject behavior
- privacy boundary: what stays on device, what leaves the device
- update and model-management path

### Industrial AI And Engineering Systems

Industrial Physical AI includes factory sensing, machine health monitoring, quality inspection, digital twins, design tools, and engineering models trained on physical product data.

The system may not move like a robot. It may estimate machine wear, detect defects, predict failures, search CAD constraints, or support a design decision. The physical world enters through vibration, images, thermal signals, acoustic signals, pressure, current, logs, CAD files, material models, and manufacturing history.

Where edge compute matters:

- always-on machine monitoring
- local defect detection on a production line
- low-latency control support
- local inference when connectivity is weak or data is sensitive
- avoiding raw sensor data transfer from many machines

Where analog or in-memory compute may help:

- steady repeated inference close to sensors
- anomaly models that run continuously
- compact vision models for inspection
- energy-constrained retrofit sensors

Where it gets harder:

- rare failures are the events that matter most
- calibration data may not include enough true faults
- false negatives can be expensive
- every site may have different machines, materials, and operating conditions
- integration with existing industrial systems is often the real blocker

Evidence needed before a strong claim:

- recall on rare faults, not only average accuracy
- threshold stability after quantization and analog error
- behavior across machine state, temperature, vibration, and sensor aging
- maintenance workflow integration
- measured power for long-running duty cycles

### Smart Infrastructure And Asset Management

Smart infrastructure includes construction sites, warehouses, buildings, utilities, traffic systems, ports, roads, bridges, and distributed assets.

The goal is to turn static physical assets into systems that can report state, detect change, and support human decisions. The action may be a search result, alert, work order, map update, compliance check, or routing change.

Where edge compute matters:

- local camera or sensor analytics
- reducing raw video upload
- fast search or alerting near the asset
- low-power monitoring across many locations
- operation during unreliable network conditions

Where analog or in-memory compute may help:

- repeated object detection or classification
- event detection in smart cameras
- battery-powered sensor nodes
- local filtering before cloud indexing

Where it gets harder:

- infrastructure environments are messy and changing
- cameras and sensors may be poorly placed
- models need updates as sites change
- system value depends on workflow integration
- one camera benchmark does not prove a deployment

Evidence needed before a strong claim:

- site-level accuracy across real lighting, occlusion, and layout changes
- energy and thermal behavior inside the deployed enclosure
- network savings from local inference
- operator workflow evidence: did it reduce search, inspection, or response time?
- clear human review path for uncertain outputs

### Precision Agriculture

Precision agriculture uses sensors and local inference to make field-level or plant-level decisions. Examples include weed detection, crop-health monitoring, harvesting support, soil sensing, irrigation control, and livestock monitoring.

Outdoor agriculture is hard because light, dust, weather, vibration, plant growth, soil, and seasonal change all affect the input. The model must work outside clean lab conditions.

Where edge compute matters:

- inference on tractors, implements, drones, and field sensors
- low-latency weed or crop detection
- battery or solar-powered sensing
- operation in areas with poor connectivity
- reducing cloud upload from many field devices

Where analog or in-memory compute may help:

- high-rate vision pipelines on field equipment
- always-on low-power sensors
- compact devices that cannot carry large batteries or cooling
- repeated local classification tasks

Where it gets harder:

- outdoor variation is severe
- false positives and false negatives have different costs
- ruggedization may matter more than peak efficiency
- maintenance and calibration must work for non-expert users
- the deployment may be seasonal and cost-sensitive

Evidence needed before a strong claim:

- field data across lighting, weather, soil, crop stage, and motion
- latency at the real equipment speed
- power and thermal behavior in outdoor enclosures
- model behavior after sensor dirt, vibration, and aging
- economic metric: less chemical use, better yield, less labor, or fewer passes

### Defense, Aerospace, And Extreme Environments

Defense, aerospace, maritime, and space systems often have strict size, weight, power, cost, thermal, radiation, reliability, and connectivity constraints.

These systems may use cameras, radar, sonar, infrared, inertial sensors, RF sensors, health sensors, and local navigation signals. Cloud dependence may be impossible. Human intervention may be delayed or unavailable.

Where edge compute matters:

- local perception and navigation
- low-power sensing on unmanned systems
- autonomy when communication is delayed or denied
- compact compute in weight-limited platforms
- thermal control in sealed or harsh environments

Where analog or in-memory compute may help:

- repeated perception or signal-processing models under a power budget
- small autonomous platforms
- sensor-side filtering before higher-level processing
- always-on monitoring with limited energy

Where it gets harder:

- reliability expectations are high
- environmental variation is extreme
- security and supply-chain concerns matter
- software update paths may be constrained
- testing must cover rare and harsh operating conditions

Evidence needed before a strong claim:

- behavior across temperature, voltage, shock, vibration, and aging
- fault behavior and recovery
- security and update model
- measured system power under mission duty cycle
- safety boundary between AI output and final control authority

### Sensory Hardware And The Machine-Readable World

Some Physical AI systems focus on sensing rather than final action. Event cameras, tactile sensors, force sensors, MEMS microphones, radar chips, inertial sensors, chemical sensors, and low-power vision sensors all make the physical world easier for software to read.

This domain matters because better sensing can reduce the compute problem. A sensor that emits only useful change, force, slip, pressure, or event information may reduce the amount of data the model must process.

Where edge compute matters:

- sensor-side preprocessing
- low-latency feature extraction
- filtering before data leaves the sensor module
- local event detection
- preserving privacy or bandwidth

Where analog or in-memory compute may help:

- compute near sensor memory
- small repeated models close to the signal source
- low-power always-on event filtering
- feature extraction before digital host processing

Where it gets harder:

- sensor noise and calibration dominate behavior
- model performance depends on the sensor, not only the neural network
- data formats may be unusual
- developer tools are less mature than for normal images or audio
- benchmark translation can be difficult

Evidence needed before a strong claim:

- sensor-specific accuracy and failure analysis
- latency from physical event to model output
- energy from sensing plus preprocessing plus inference
- calibration and drift behavior
- tool support for training and debugging sensor-native models

## Embodied AI And VLA Systems

Robots are still important, but they should be treated as one branch of Physical AI, not the whole topic.

Vision-language-action systems, often called VLA systems, combine language instructions, camera input, robot state, and action outputs. In simple words:

```text
instruction + what the system sees + body state -> next physical action
```

The hard part is that the model is tied to a body. A different arm, hand, camera position, gripper, wheel base, or sensor layout changes what actions mean. A command like "pick this up" is not only a language task. It must become motion through a specific physical machine.

Fast hardware adaptation means the system can reuse learned behavior across different bodies with less new data. Low-data bootstrapping means it can learn a new task from a small number of demonstrations. These are important because collecting physical data is slow, expensive, and sometimes risky.

Where edge compute matters:

- local perception and control support
- low-latency action loops
- operation when cloud connectivity is absent or too slow
- privacy or safety boundaries
- reduced data movement from cameras and sensors

Where analog or in-memory compute may help:

- repeated perception blocks
- compact local policy or state-estimation models
- sensor-side inference before a higher-level planner
- power-limited mobile platforms

Where it gets harder:

- action errors can affect the physical world
- latency jitter can matter more than average speed
- safety controllers must remain outside the neural model
- many operators may stay digital
- the model, runtime, sensors, and body calibration must be tested together

Evidence needed before a strong claim:

- task success rate on the target body
- worst-case latency and jitter
- collision, force, and safety-controller behavior
- adaptation data size and retraining cost
- behavior when sensors shift, lighting changes, or objects move unexpectedly

## VLA-Era Implications For Analog IMC Startups

Edge-optimized vision-language-action models change the silicon question.

The older edge AI story was often:

```text
small vision model
  -> mostly convolution
  -> fixed weights
  -> fixed camera task
  -> classify or detect
```

The newer Physical AI story is closer to:

```text
language instruction
  + camera or event stream
  + robot/body state
  + tactile or force signal
  + changing task context
  -> action-support output
```

That shift is good for an energy-efficient edge AI chip because more intelligence must run locally. It is also dangerous for a narrow analog chip because the model and system are less static.

### Shift From CNNs To Transformer-Class Workloads

Many analog and in-memory AI designs are strongest when the workload is repeated multiply-add work with reused weights. CNN backbones and dense layers can fit that shape well.

Transformer-class VLA models add harder pieces:

- attention
- token processing
- multimodal fusion
- normalization-heavy paths
- nonlinear functions such as softmax or GeLU
- dynamic sequence lengths
- memory-heavy key/value movement
- language, vision, and body-state inputs in one graph

The first-principles issue is simple: analog arrays can be very good at doing many multiply-adds cheaply, but a transformer is not only multiply-adds. It also needs routing, indexing, normalization, reductions, format changes, memory movement, and control flow. If those parts stay digital and move data back and forth too often, the analog gain can shrink.

Roadmap implication:

```text
Do not build a pure analog-only story.
Build a hybrid digital-analog architecture.
```

The analog core should handle the heavy linear algebra where it is a real fit. Digital companion logic should handle attention control, softmax or softmax-like paths, normalization-adjacent work, sparse routing, safety checks, and unsupported operators. The product claim should be about completed inference, not the analog array alone.

What to say clearly:

```text
For transformer-class Physical AI models, the useful architecture is likely hybrid. The analog core can target repeated matrix-heavy blocks, while digital logic handles dynamic control, nonlinear operators, safety paths, and model glue.
```

What not to overclaim:

```text
Do not say a high analog MAC efficiency number proves the chip is VLA-ready. VLA readiness depends on memory movement, attention support, operator coverage, compiler mapping, latency jitter, and task accuracy.
```

### The Static-Weight Assumption Gets Weaker

Some analog IMC approaches store weights inside memory-like devices. That can be powerful when weights are written once or rarely changed. But Physical AI models may need adaptation:

- new robot body
- new camera position
- new gripper
- new sensor mix
- new workspace
- new object set
- new local task
- customer fine-tune

If weights need to change often, weight writing becomes part of the product. It is no longer a rare manufacturing or setup event.

The hard question is:

```text
How expensive is it to update the model on the actual chip?
```

That includes:

- write latency
- write energy
- endurance
- voltage requirements
- calibration after writing
- accuracy drift after repeated writes
- whether updates happen on device or off device
- whether only a small adapter is updated or the whole model changes

Roadmap implication:

```text
Treat weight update as a first-class benchmark.
```

The startup should not only report inference energy. It should report how the chip handles model update, partial rewrite, recalibration, and rollback. If the memory element is slow to write, high voltage, or low endurance, the product may still fit fixed models but struggle with adaptive Physical AI.

What to say clearly:

```text
If the target system needs frequent adaptation, the memory technology and calibration flow matter as much as inference efficiency.
```

What not to overclaim:

```text
Do not assume a chip that is efficient for fixed-weight inference is automatically good for adaptive robotics or VLA workloads.
```

### Multi-Embodiment Means Flexible Compute Fabric

A physical model is tied to a body. Different bodies have different sensors, degrees of freedom, camera positions, joint limits, timing loops, and safety envelopes.

For silicon, this means the chip cannot assume one tidy input and one tidy output. It may need to handle:

- RGB frames
- event streams
- depth
- radar or lidar features
- proprioception
- force and torque
- tactile arrays
- audio
- language tokens
- action heads
- safety status

The chip does not need to run every part in analog. But the system must make it easy to map the right part to the right compute path.

Roadmap implication:

```text
Build for operator and sensor flexibility, not only peak array efficiency.
```

The compiler/runtime should be able to say:

- this projection goes analog
- this attention path stays digital
- this sensor preprocessing runs on a small digital block
- this safety path bypasses the neural accelerator
- this control loop is handled by a deterministic controller
- this evidence does or does not include host overhead

What to say clearly:

```text
Physical AI needs a flexible system boundary. The analog core is one compute region inside a larger runtime that also includes digital operators, sensor interfaces, memory, host control, and safety logic.
```

What not to overclaim:

```text
Do not claim one analog mapping proves support for every robot body, sensor layout, or action space.
```

### Drift And Calibration Become Safety Issues

Analog compute uses physical signals. Physical signals can shift with temperature, voltage, device variation, aging, noise, and calibration state.

In a normal classifier, drift might reduce accuracy. In Physical AI, drift can change a physical decision. That makes calibration more than a lab detail.

The product needs to answer:

- how often calibration runs
- whether calibration happens on boot, on schedule, or continuously
- what happens when calibration fails
- how the system detects drift
- whether sensitive layers are protected digitally
- whether safety controllers can reject unsafe outputs
- how accuracy changes over temperature and voltage
- how behavior changes over device aging

Roadmap implication:

```text
Build calibration, drift detection, and fallback behavior into the product story.
```

What to say clearly:

```text
For Physical AI, analog calibration is part of reliability. The question is not only whether the model is accurate today, but whether it stays within limits as the device heats, ages, and moves through real conditions.
```

What not to overclaim:

```text
Do not say analog inference is safe for physical systems unless drift, calibration, and fallback behavior are tested under the target conditions.
```

### Deterministic Control Is A Separate Layer

A VLA model may help choose or support an action, but the final motion loop often needs deterministic timing and safety behavior. Neural inference is usually not the same thing as motor control.

The system may include:

- high-level planner
- VLA or perception model
- state estimator
- motion planner
- safety monitor
- real-time joint controller
- motor driver

An analog AI chip may accelerate inference, but it should not pretend to replace every deterministic control path.

Roadmap implication:

```text
Design clean interfaces to real-time controllers.
```

The chip should expose predictable latency, bounded jitter where needed, timestamps, health status, confidence or uncertainty outputs, and a way for downstream controllers to reject, clamp, or ignore neural outputs.

What to say clearly:

```text
The inference chip should fit into a tiered control stack. It can make local intelligence cheaper, but deterministic control and safety enforcement still need their own path.
```

What not to overclaim:

```text
Do not say the AI accelerator alone solves robotics control. It solves one part of the stack.
```

### The Compiler Wall May Decide Adoption

Special hardware fails when developers cannot use it.

Robotics and Physical AI teams will likely start from common model ecosystems and simulation stacks. They may use PyTorch, JAX, ONNX, custom kernels, simulator-generated models, or vendor runtimes. If using the chip requires manual graph surgery, hand placement, or weeks of vendor help, the energy advantage may not matter.

The compiler must hide most of the hardware complexity while still exposing enough detail for debugging.

The software path should support:

- ONNX import
- PyTorch export
- JAX/XLA path or at least a clear interchange path
- operator support report
- analog/digital placement report
- unsupported operator rewrite suggestions
- quantization and analog-error simulation
- calibration-aware mapping
- performance and energy profiling
- task accuracy validation
- fallback path reporting
- reproducible package export

Roadmap implication:

```text
Make zero-touch the goal, but make explainable mapping the requirement.
```

Zero-touch means the user can try the chip without becoming an analog-circuit expert. Explainable mapping means the system still shows where the model went, why it went there, what stayed digital, and what evidence supports the result.

What to say clearly:

```text
The compiler and runtime are part of the product. Customers do not buy an analog array. They buy a path from their model to a measured result.
```

What not to overclaim:

```text
Do not claim broad model support until the compiler can ingest real customer graphs and report unsupported operators honestly.
```

### Sensor Interfaces Can Become A Differentiator

Physical AI starts with physical signals. If the chip only accepts neatly preprocessed digital tensors, it may miss part of the opportunity.

Useful sensor-side capabilities may include:

- analog front-end support for force, torque, strain, pressure, thermal, or biological signals
- event-driven input for sparse vision streams
- timestamp handling
- low-power wake paths
- local feature extraction
- sensor calibration metadata
- synchronization across sensors

This does not mean every analog IMC chip must become a sensor hub. It means the roadmap should decide where the boundary sits:

```text
raw sensor -> AFE -> preprocessing -> neural inference -> host/runtime
```

or:

```text
external sensor processor -> digital tensor -> analog/digital inference chip
```

The right answer depends on product focus.

Roadmap implication:

```text
Pick the sensor boundary deliberately.
```

For wearables, industrial sensors, tactile systems, and event vision, closer sensor integration may be valuable. For larger robotics or mobility systems, a clean high-bandwidth digital interface to existing sensor processors may be more practical.

What to say clearly:

```text
Sensor integration is not automatically required, but the product must state where raw physical signals become model-ready tensors and who pays that energy, latency, and calibration cost.
```

What not to overclaim:

```text
Do not count only inference energy if sensor preprocessing, AFE power, synchronization, or host tensor preparation is outside the number.
```

### Roadmap Capabilities To Prioritize

For an analog or in-memory inference startup targeting Physical AI, the roadmap should prioritize:

- hybrid transformer-ready execution, with analog for matrix-heavy blocks and digital for dynamic control and unsupported operators
- memory technology and programming flow that can support the expected update pattern
- calibration and drift monitoring as product features
- compiler support for ONNX, PyTorch export, and a JAX/XLA interchange path
- explainable analog/digital placement reports
- task accuracy validation tied to the actual domain metric
- system-level energy per completed inference, not isolated macro efficiency
- bounded latency and jitter reporting for physical systems
- clean integration with deterministic controllers
- deliberate sensor boundary design
- evidence packaging that separates measured hardware, replay fixtures, simulation, and estimates

### Strategic Position

The opportunity is real because Physical AI pushes inference closer to sensors and bodies. Power, heat, size, and latency matter. That is the natural opening for efficient edge compute.

The threat is also real because Physical AI models are becoming more multimodal, more transformer-like, more adaptive, and more software-defined. A narrow fixed-function analog accelerator can be stranded if it cannot follow the model stack.

The balanced position is:

```text
Analog IMC can be compelling for Physical AI when it is part of a hybrid, compiler-supported, calibration-aware system that proves completed-task results under real domain constraints.
```

Not:

```text
Physical AI is growing, so analog IMC automatically wins.
```

## Cross-Domain Modality Map

The frontend should let the user think across both domain and modality.

```text
Domain: where the system is used
Modality: what kind of signal the model reads
Use case: what job the model performs
Evidence: what proves the claim
```

Example mapping:

| Domain | Modalities | Typical tasks | Main proof |
| --- | --- | --- | --- |
| Mobility | camera, radar, lidar, inertial | perception, detection, localization | worst-case latency and rare-scene behavior |
| Ambient home | audio, image, presence, environment | wake, detect, classify, respond | false wake, missed event, idle power |
| Industrial | vibration, image, acoustic, thermal, logs | anomaly, defect, wear estimate | rare-fault recall and threshold stability |
| Infrastructure | camera, location, asset sensors | detection, search, progress tracking | site-level accuracy and workflow impact |
| Agriculture | image, multispectral, soil, weather | weed, crop, harvest, irrigation | field accuracy and equipment-speed latency |
| Defense/aerospace | image, radar, RF, inertial, health | navigation, detection, monitoring | reliability under mission conditions |
| Sensory hardware | event vision, tactile, force, MEMS | feature extraction, event detection | sensor-to-output latency and drift |
| Robotics/VLA | image, language, proprioception, force | perceive, plan support, act | task success, safety, jitter, adaptation cost |

## How This Changes The Existing Workbench

The current workbench has these useful artifacts:

- `workload_fit`: compares edge workloads by modality
- `system_boundary`: shows analog, digital, conversion, memory, host, and fallback cost
- `toolchain_readiness`: shows what software support is needed
- `connection_playbook`: shows real compiler, simulator, board, power, and accuracy connections
- `evidence_brief`: explains what is supported and what is not
- `interview_brief`: turns the result into clear interview language

The new `physical_ai_map` artifact should connect those artifacts to real domains.

It should answer:

- Which Physical AI domain is the selected project closest to?
- Which sensors and model types are likely involved?
- What does the system do after inference?
- What makes the use case power or heat constrained?
- What metric matters most?
- What analog/in-memory claim is plausible?
- What evidence would upgrade the claim?
- What should not be claimed yet?

## Backend Artifact Shape

The backend should produce:

```json
{
  "result_type": "physical_ai_map",
  "schema_version": "physical-ai-map-v0.1",
  "provenance": "derived from selected target profile, modality, workload fit, system boundary, and package evidence",
  "confidence": "low",
  "selected_domain": "ambient_home",
  "selected_domain_label": "Smart home and ambient hardware",
  "summary": {
    "plain_reading": "This is an always-on local inference use case. The compute story is strongest if idle power, wake latency, and false wake behavior are measured together.",
    "analog_fit": "possible",
    "main_evidence_gap": "system-level energy and task accuracy under real duty cycle"
  },
  "domains": [
    {
      "id": "ambient_home",
      "label": "Smart home and ambient hardware",
      "fit": "possible",
      "why_it_matters": "...",
      "sensors": ["microphone", "camera", "presence", "environment"],
      "typical_tasks": ["wake-word", "event detection", "local classification"],
      "where_edge_compute_matters": ["idle power", "privacy", "local response"],
      "where_analog_may_help": ["always-on small models", "repeated local inference"],
      "where_it_gets_harder": ["false wakes", "missed events", "software update path"],
      "evidence_needed": ["energy per wake", "false accept/reject", "idle power"],
      "do_not_claim": ["Do not say local inference alone proves privacy."]
    }
  ],
  "cross_domain_rules": [
    "Do not say edge AI is one market.",
    "Do not use TOPS/W alone as proof.",
    "Do not treat a prototype chip as production readiness.",
    "Compare completed inference at fixed accuracy, latency, energy, and reliability."
  ]
}
```

## Frontend Panel

Add a panel after `Workload fit`.

Panel title:

```text
Physical AI Map
```

Panel purpose:

```text
Show where this selected workload sits in the larger Physical AI landscape and what evidence is needed before making a strong domain claim.
```

Left side:

- selected domain
- selected modality
- target device
- analog fit
- main evidence gap
- confidence

Right side:

- domain cards
- sensors
- tasks
- where edge compute matters
- where analog may help
- where it gets harder
- evidence needed
- do-not-claim guidance

The frontend should not show broad market claims as proof. It should keep the same style as the rest of the app: simple, specific, evidence-aware.

## Interview Language

### What To Say Clearly

Physical AI is broader than robots. It is any system that uses sensors, local compute, and software to understand the physical world and do something useful. A robot moves, but a camera, wearable, factory sensor, vehicle subsystem, or field device can also be Physical AI if it senses the world and makes local decisions.

Analog and in-memory AI are not the definition of Physical AI. They are possible compute approaches for the inference part. They become interesting when inference must happen near the sensor and the device is limited by battery, heat, size, or latency.

The strongest product story is not "we have a high TOPS/W number." The strongest story is "for this specific workload, on this target device, the system reaches the required accuracy, latency, energy, and reliability after counting the full path."

### What Not To Overclaim

Do not say analog compute is automatically better than digital compute. Digital compute is precise, flexible, mature, and easier to program. Analog compute is a tradeoff. It may save energy for repeated matrix-heavy inference, but it introduces physical behavior that must be calibrated and validated.

Do not say Physical AI is one market. A wearable, robot, vehicle, farm implement, smart camera, factory sensor, and space system do not have the same duty cycle, model size, safety risk, power budget, or evidence requirement.

Do not say a prototype chip proves production readiness. It proves the idea reached silicon. Production still requires yield, repeatability, calibration cost, packaging, software support, customer integration, long-term drift behavior, and operation across real conditions.

Do not say edge deployment alone proves privacy, safety, or reliability. Local compute can help, but the system still needs data boundaries, update controls, safety controllers, monitoring, and failure handling.

Do not use company examples or recent product claims in the app until they are source-checked. If the frontend references current products, papers, or roadmaps, the source link and date should be shown.

## Source-Check Backlog

The pasted examples are useful as direction, but the app should verify current claims before presenting them as facts. The source-check backlog should include:

- current autonomous mobility platform examples
- current ambient hardware roadmaps
- AI-first device claims
- industrial AI and engineering-model company claims
- construction and warehouse local-vision examples
- precision agriculture laser-weeding claims
- defense, aerospace, and space autonomy examples
- event-based vision and tactile-sensor examples
- Gemini Robotics, on-device VLA, motion-transfer, safety-report, and benchmark claims
- Microsoft Rho-alpha or other VLA-plus-robotics claims
- current JAX, PyTorch, XLA, ONNX, and simulator deployment paths for robotics models
- current edge digital competitors and their robotics positioning
- current FPGA, MCU, real-time processor, and motor-control timing claims
- current analog memory options for fast update and endurance
- current AFE, tactile, force, torque, and event-vision sensor interface claims

Until this source check is done, the app should use the conceptual domain map and avoid specific vendor claims.

## Acceptance Criteria

This spec is implemented when:

- the backend returns `physical_ai_map` for a saved package
- the artifact is saved in the package bundle
- the archive includes `physical-ai-map.json`
- the package `saved_artifacts` map links to `/deployment-packages/{package_id}/physical-ai-map`
- the frontend renders a `Physical AI Map` panel
- the smoke test checks that the frontend panel and backend endpoint exist
- the artifact explains domains in simple language
- each domain includes sensors, tasks, edge-compute reason, analog-fit reason, hard parts, evidence needed, and do-not-claim guidance
- the artifact includes VLA-era roadmap implications for analog IMC startups
- the roadmap section covers transformer readiness, weight updates, multi-embodiment flexibility, drift and calibration, deterministic control integration, compiler support, and sensor-interface boundaries
- the artifact separates conceptual guidance from source-checked company or product examples
