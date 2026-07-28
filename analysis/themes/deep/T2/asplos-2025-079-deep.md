# MVQ: Towards Efficient DNN Compression and Acceleration with Masked Vector Quantization

**Venue:** ASPLOS · **Theme:** Structured Pruning + Vector Quantization

## What It Does

Conventional vector quantization (VQ) for DNN compression treats all weights equally during k-means clustering, forcing important high-magnitude weights to align with unimportant zero-adjacent weights, causing large clustering errors on the weights that most affect accuracy and leading to significant accuracy degradation at high compression ratios.

Edge DNN deployment requires extreme compression ratios (20-30x) to fit models on-chip, but standard VQ methods sacrifice too much accuracy at these ratios because they fail to protect the important weights that govern model behavior.

MVQ is an algorithm-hardware co-design combining N:M structured pruning with masked k-means clustering. At the algorithm level: (1) N:M pruning removes unimportant weights with a regular sparse structure; (2) masked k-means treats only unpruned (important) weights during both assignment and codeword update, preventing zeros from distorting centroids; (3) 8-bit symmetric quantization applied to codebook; (4) masked gradient finetuning recovers accuracy. At the hardware level, the accelerator uses the Enhanced Weight Stationary (EWS) dataflow with: an assignment-aware weight-loading controller that reconstructs sparse weights from codebook + index + N:M mask using a Codebook Register File (CRF) and LZC-based mask decoder; and a sparsity-aware systolic array with Q=N/M x d active PEs per subvector instead of d PEs, reducing multiplier and register file count by 55%. Synthesized at 40nm 0.99V LVT using Synopsys Design Compiler.

## The Key Experiment

- **speedup:** EWS-CMS achieves 1.2-2.2x speedup over EWS baseline on 64x64 array
- **energy or tops w:** 2.3x energy efficiency improvement vs base EWS accelerator; 1.73x vs prior sparse accelerators; 6.9 TOPS/W for ResNet-18 64x64 at 40nm; 53.3-137.9% higher efficiency vs EWS baseline
- **area:** 55% reduction in systolic array size vs EWS baseline at 75% sparsity
- **ppa:** 40nm 0.99V; 73% higher energy efficiency vs S2TA (normalized to 40nm)
- **accuracy:** ResNet-18: 68.8% top-1 at ~22x compression (vs 68.2% PQF, 66.5% BGD); ResNet-50: 75.2% at ~22x (vs 74.2% PQF); VGG-16: 69.7% at ~28x; reduces FLOPs by ~70% (50% for lightweight models)
- **other:** Evaluated on ResNet-18/50, VGG-16, AlexNet, MobileNet-v1/v2, EfficientNet, MaskRCNN/COCO, DeepLab-V3/VOC

**Compared against:** base EWS accelerator; WS-base accelerator; SparTen (MICRO19); CGNet (MICRO19); SPOTS (TACO22); S2TA (HPCA22); BGD VQ; PQF VQ; PvQ

**Hardware:** ASIC · **Workloads:** CNN; vision

## Why This Approach

Masked k-means clustering that excludes pruned (zero) weights from both assignment and codeword update steps, ensuring codewords approximate important weights rather than being distorted by structured-pruning zeros.

This paper sits in the **quantization** subtheme. The core tension: lower precision = smaller model = less memory bandwidth, but at the cost of rounding error that compounds across layers. This paper's bet: Empirical demonstration that clustering error on important weights (not total SSE) is the key driver of VQ accuracy loss.

## What It Leaves Open

- Depthwise convolution layers do not benefit from MVQ because the small parameter count means weight loading is not the bottleneck
- only pointwise convolution results reported for lightweight models.

**Tags:** vector-quantization, n-m-sparsity, systolic-array, cnn-accelerator, edge-inference, hw-sw-codesign
