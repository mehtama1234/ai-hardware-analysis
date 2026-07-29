# VoLUT: Efficient Volumetric streaming enhanced by LUT-based super-resolution

**Venue:** MLSYS · **Subtheme:** 3D Video Streaming Optimization

## What It Does

VoLUT is a system for real-time 3D volumetric video streaming on mobile devices. Volumetric video (e.g., 3D point clouds, voxel grids) requires 100–1000 Mbps for lossless transmission—far exceeding typical mobile bandwidth (5–50 Mbps). VoLUT uses a two-stage super-resolution pipeline: Stage 1 compresses the volumetric video to low resolution (1/64 original), transmits over network, and decompresses on device. Stage 2 applies GPU-accelerated super-resolution via dilated k-NN interpolation: for each voxel, find k nearest neighbors in the low-resolution point cloud and interpolate. A learned lookup table (LUT) pre-computes interpolation weights for common neighborhood patterns, reducing per-voxel compute from 100+ operations to 10 LUT lookups.

Data path: point cloud (server) → spatial downsampling (1/64) → transmission → GPU decompression → dilated k-NN (with LUT acceleration) → high-res output.

## The Key Result

VoLUT achieves real-time (30 FPS) volumetric video playback on Qualcomm Snapdragon 888 (flagship mobile GPU) and 15 FPS on mid-range Mali-G77, compared to <1 FPS for naive point cloud rendering. Bandwidth reduction: 50x (100 Mbps → 2 Mbps) via compression + super-resolution, enabling WiFi streaming. Quality loss (PSNR) <2 dB compared to lossless transmission.

## Why This Approach

Mobile GPUs lack hardware rasterization for volumetric geometry; rendering k-NN interpolations for 10⁶+ points requires 10¹⁰+ floating-point operations per frame, saturating mobile GPU memory bandwidth. LUT-based approximation trades off ~1% PSNR for 10x speedup by replacing expensive operations with fast table lookups. This is critical for AR/VR applications (sports broadcasting, telepresence) where volumetric video is preferable to 2D video but bandwidth is limited.

## What It Leaves Open

- LUT generalization: tables optimized for face/body geometry; landscapes or sparse point clouds show higher PSNR degradation
- Dynamic geometry (moving people): super-resolution assumes static between compression rounds; fast motion causes artifacts
- Temporal coherence: frame-to-frame LUT coherence not exploited; independent per-frame processing misses correlation
- Comparison against traditional video codecs (H.264, H.265 on 2D projected video) missing; unclear if 3D volumetric is necessary for quality gains
- Scaling to higher resolutions (8K volumetric): LUT memory grows cubically; inference time and GPU memory bottlenecks not characterized

