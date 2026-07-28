# IRIS: Unleashing ISP-Software Cooperation to Optimize the Machine Vision Pipeline

**Venue:** HPCA · **Theme:** ISP-Memory Co-Processing

## What It Does

Continuous Vision (CV) SoC pipelines capture entire scenes at uniform high resolution (e.g., 4K), wasting memory bandwidth and backend compute on low-information regions (sky, road) that do not require full-resolution processing, while the ISP discards intermediate computations (edge masks, motion vectors) that could guide resolution reduction.

Mobile CV systems for autonomous driving and AR/VR face strict latency and energy constraints; uniform full-resolution capture causes both the frontend (ISP, memory bus) and backend (CPU/GPU) to process unnecessary data, and the ISP already generates the information needed to identify low-salience regions but discards it.

IRIS augments the frontend ISP with three lightweight hardware units: (1) an IRIS Saliency Scorer that reuses ISP byproducts (the edge mask from Edge Enhancement and motion vectors from Temporal Denoising's Block Matching Algorithm) to compute a per-region saliency score (ISS = EDM + alpha * EDM * MM) without any new image analysis; (2) a Quad Unit that applies a hierarchical quadtree-like grouping (16x16, 32x32, 64x64 pixel regions) and compares maximum quadblock ISS to a backend-provided threshold to decide resolution; and (3) a Downsampling Unit that reduces selected quadblocks from 32x32 or 64x64 to 16x16 in-pipeline. The resulting mixed-resolution frame with a Region Resolution Map metadata is stored in the framebuffer. On the backend, for Vision Transformers IRIS feeds a mixed-resolution tokenizer (Quadformer-style), and for visual localization (ORB-SLAM3) IRIS enables an iterative feature extraction algorithm that processes regions in descending ISS order and stops on diminishing marginal feature increase. The ISP extension is validated as cycle-accurate RTL that never stalls the ISP pipeline.

## The Key Experiment

- **speedup:** Localization: 22.8% avg latency reduction, 10.5% tail latency reduction; Classification: 37.5% avg latency reduction, 9% tail latency reduction
- **energy or tops w:** Localization: 22.5% energy reduction; Classification: 41.5% energy reduction
- **area:** Synthesized at 14nm with Synopsys; area overhead not quoted in headline but reported as negligible vs. ISP
- **accuracy:** ViT top-1 accuracy within 1% of baseline at ISS threshold 0.3; ORB-SLAM APE below 5mm at ISS=0.2, MFI=3%
- **other:** ~70% average image size reduction at threshold 0.5; 55% image size reduction at threshold 0.3

**Compared against:** Baseline uniform-resolution ISP pipeline (no downsampling); Software-only saliency generation (VL-SO, ViT-SO) without ISP hardware

**Hardware:** SoC · **Workloads:** vision; CNN; transformer

## Why This Approach

Repurposing already-computed ISP internal byproducts (edge mask from Edge Enhancement and motion vectors from Temporal Denoising) as a zero-additional-compute saliency scorer to drive per-region adaptive spatial resolution downsampling in the ISP pipeline before framebuffer write.

This paper sits in the **memory hierarchy** subtheme. The core constraint: compute starves waiting for data — arithmetic throughput far outpaces DRAM bandwidth. This paper's solution: IRIS: ISP hardware augmentation with Saliency Scorer, Quad Unit, and Downsampling Unit that performs mixed-resolution imaging by repurposing ISP byproducts at negligible added cost.

## What It Leaves Open

- Software-only saliency generation hurts performance (4.7% latency increase for small ViTs) because the overhead of computing saliency in software outweighs benefits, making IRIS dependent on ISP hardware augmentation that requires ISP redesign or cooperation from vendors.

**Tags:** isp, computer-vision, mixed-resolution, adaptive-sampling, saliency, edge-inference
