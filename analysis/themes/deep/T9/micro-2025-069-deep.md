# RTGS: Real-Time 3D Gaussian Splatting SLAM via Multi-Level Redundancy Reduction

**Venue:** MICRO · **Subtheme:** 3D Graphics Acceleration (SLAM)

## What It Does

RTGS is an algorithm-hardware co-design for real-time 3D Gaussian Splatting (3DGS) SLAM on edge devices. On the algorithm side, it exploits inter-iteration workload similarity in SLAM: Gaussians (position, covariance, color) remain fixed between tracking iterations (only camera pose updates), enabling aggressive kernel-level redundancy. RTGS detects frame-to-frame Gaussian relevance changes via bounding-box culling and adapts the working set size. Hardware-wise, RTGS uses a multi-level redundancy architecture: L1 (pixel-level) caches recent splatting results, L2 (tile-level) reuses sorted Gaussian indices, and L3 (scene-level) maintains a compact Gaussian hierarchy. The GPU kernel fuses multiple rendering passes (splatting, differentiable blending, visibility sorting) into a single memory-resident pipeline, eliminating intermediate materialization to DRAM.

Data path: camera pose → Gaussian culling → per-pixel splatting (with cached Gaussian order) → blended output. Redundancy is exploited by (1) pinning Gaussians to GPU fast memory when unchanged, (2) reusing sorted z-order lists across frames, and (3) deferring expensive operations (full covariance projection) until Gaussians actually move.

## The Key Result

RTGS achieves 33+ FPS (real-time) on edge devices (Qualcomm Adreno GPU, ARM Mali-G77) compared to 5–8 FPS for naive 3DGS-SLAM. On an NVIDIA Jetson Orin, RTGS delivers 45 FPS tracking + 2 ms bundle adjustment, vs. 12 FPS baseline. Memory bandwidth usage drops 2.8x due to redundancy exploitation. Latency per frame: 25 ms (RTGS) vs. 150+ ms (standard 3DGS).

## Why This Approach

3DGS-based SLAM is memory-bound: sorting Gaussians by depth per pixel incurs 10–20 billion memory operations per frame. Naive GPU implementations thrash caches and saturate memory bandwidth. RTGS's inter-iteration redundancy is the key insight: in SLAM, most frames change camera pose by <10cm/frame, leaving 95%+ of Gaussian positions stable. By caching per-pixel splatting results and reusing Gaussian sort orders, RTGS eliminates 70% of redundant memory traffic. This is critical for edge deployment where bandwidth is 10–100x lower than data-center GPUs.

## What It Leaves Open

- Accuracy degradation under fast camera motion: redundancy caches assume smooth tracking; rapid rotation or fast motion causes stale caches and artifacts
- Scaling to large-scale SLAM (100k+ Gaussians): L3 hierarchy overhead and culling cost not fully characterized
- Generalization to other 3D representations (NeRF, mesh, point cloud) unclear; SfM is specific to Gaussian structure
- Dynamic scenes (moving objects) not addressed; redundancy assumes static environment
- Comparison against specialized 3D inference accelerators (e.g., Gfxip IP cores) missing; unclear if software solutions match hardware efficiency

