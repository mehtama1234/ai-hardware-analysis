# A 0.75mm2 407μW Real-Time Speech Audio Denoiser with Quantized Cascaded Redundant Convolutional Encoder-Decoder for Wearable IoT Devices

**Venue:** VLSID · **Theme:** Edge Quantized Inference

## What It Does

Real-time audio denoising on wearable IoT devices requires extremely low power consumption and minimal silicon area while maintaining quality comparable to cloud-based processing.

On-device audio denoising enables consistent performance across platforms and protects user privacy. Efficient hardware implementation of ML models is critical for battery-powered wearable devices operating in real-time.

Quantized cascaded redundant convolutional encoder-decoder (Conv-ED) network with optimized hardware quantization. Specialized processing element activation routing scheme to minimize on-chip memory accesses.

## The Key Experiment

- **power consumption:** 407 μW
- **operating voltage:** 0.65V
- **operating frequency:** 18.5 MHz
- **die area:** 0.75 mm²
- **latency per frame:** 8ms (real-time)
- **memory reduction:** 75%
- **memory access reduction:** 5-9x
- **audio quality metric:** Highest PESQ score

**Compared against:** Previous audio denoiser designs; Cloud-based audio processing

**Hardware:** Wearable IoT devices; Hearables; Smart earbuds; Battery-powered audio systems · **Workloads:** Real-time audio denoising; Speech enhancement

## Why This Approach

Integrated speech denoiser achieving 407μW power consumption on 28nm CMOS with 75% memory reduction via quantization and 5-9x on-chip memory access reduction via specialized routing.

This paper sits in the **quantization** subtheme. The core tension: lower precision = smaller model = less memory bandwidth, but at the cost of rounding error that compounds across layers. This paper's bet: Quantized convolutional encoder-decoder for audio denoising.

## What It Leaves Open

- Evaluation on specific audio datasets
- generalization to other audio tasks not explored. Single-voltage operation point (0.65V) evaluated.

**Tags:** audio-processing, speech-enhancement, neural-network-accelerator, wearable, low-power, IoT, quantization, encoder-decoder
