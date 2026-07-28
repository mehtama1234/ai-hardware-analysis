# DiffServe: Efficiently Serving Text-to-Image Diffusion Models with Query-Aware Model Scaling

**Venue:** MLSYS 2025 · **Theme:** Diffusion Model Serving

## What It Does

Text-to-image diffusion model serving faces two simultaneous challenges: high-quality models (e.g., SDv1.5 at 50 steps) are 4.6-18x slower than lightweight variants (SD-Turbo, SDXS), limiting throughput; and query demand fluctuates, causing static resource provisioning to either waste capacity during off-peak or fail SLOs during peak.

For 20-40% of queries, lightweight diffusion models produce images of equal or better quality than heavyweight models ('easy queries'). Routing these queries to lightweight models saves compute. However, existing metrics (CLIP Score, PickScore) cannot reliably identify easy queries (they perform no better than random routing), so a task-specific discriminator is needed. Dynamic resource allocation must co-optimize discriminator confidence threshold, model variant placement, and batch sizes.

DiffServe uses query-aware model cascades with two technical innovations: (1) Discriminator design - EfficientNet-V2 trained on binary real/fake classification (real = MSCOCO ground truth images, fake = generated images from both light and heavy models). At inference, confidence score (softmax output for 'real' class) determines if lightweight model output is accepted or deferred to heavyweight model. Counterintuitive finding: using heavyweight model outputs as 'real' training labels hurts performance; ground-truth images as 'real' labels produce the best discriminator. (2) Resource allocation via MILP - Controller periodically solves a Mixed Integer Linear Program maximizing confidence threshold (proxy for quality) subject to latency constraints (execution time + Little's Law queuing delay) and throughput constraints (device counts x per-device throughput >= demand). Variables: x1, x2 (device counts for light/heavy models), b1, b2 (batch sizes), t (confidence threshold). Demand estimated via exponentially weighted moving average with 5% over-provisioning factor. MILP solved asynchronously (~10ms overhead) off critical path.

## The Key Experiment

- **quality vs proteus:** Up to 20% FID improvement vs Proteus (random query-agnostic routing)
- **quality vs static:** Up to 24% FID improvement vs static configurations
- **slo violations vs static:** 19-70% lower SLO violation rate vs static provisioning
- **slo violations vs clipper heavy:** Up to 52x lower SLO violation vs Clipper-Heavy
- **milp runtime:** ~10ms MILP solver runtime (off critical path)

**Compared against:** Clipper-Light (all queries to lightweight model); Clipper-Heavy (all queries to heavyweight model); Proteus (dynamic model selection, random query routing); DIFFSERVE-Static (discriminator but fixed allocation)

**Hardware:** NVIDIA A100 · **Workloads:** text-to-image-generation; diffusion-model-serving

## Why This Approach

EfficientNet-V2 discriminator repurposed from real/fake classification to route diffusion model queries; MILP formulation co-optimizing confidence threshold, batch sizes, and device allocation for cascaded diffusion serving under dynamic demand.

This paper sits in the **attention efficiency** subtheme. The core constraint: generating one token requires reading all past key-value vectors from memory — O(n) bandwidth per step. This paper's angle: Query-aware model cascade for text-to-image diffusion serving using a trained discriminator.

## What It Leaves Open

- Discriminator training requires curating real/fake image datasets and offline model profiling
- MILP assumes deterministic execution times; variance in GPU execution affects queuing model accuracy
- Cascade depth limited to two models; extending to multi-stage cascades requires more complex MILP
- Reusing intermediate lightweight outputs in heavyweight inference showed mixed results (quality sometimes degraded)

**Tags:** diffusion-models, model-serving, cascaded-inference, MILP, resource-allocation, text-to-image, SLO, query-routing
