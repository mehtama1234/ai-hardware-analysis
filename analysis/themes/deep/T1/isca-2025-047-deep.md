# Dadu-Corki: Algorithm-Architecture Co-Design for Embodied AI-powered Robotic Manipulation

**Venue:** ISCA · **Theme:** Hardware-Fused Attention

## What It Does

Embodied AI robotic manipulation systems run LLM inference on a frame-by-frame basis, creating cumulative sequential latencies (LLM inference, robot control, data communication) that reach 249 ms per frame and prevent real-time operation at >=30 Hz. LLM inference alone consumes 72.7% of latency and 95.8% of energy per frame.

LLM-controlled robots require real-time control (>=30 Hz, preferably 100 Hz), but existing vision-centric frame-by-frame pipelines inherited from video processing violate the frequency-decoupled front-end/back-end principle standard in robotics.

Corki decouples LLM inference from robot control by replacing per-frame discrete action prediction with cubic polynomial trajectory prediction over multiple future steps, reducing LLM inference frequency by up to 5.1x. A custom dataflow ASIC accelerator implements task-space computed torque control (TS-CTC) with pipelined link-level computations (pose, velocity, acceleration, force units connected via FIFOs and line buffers) and an application-specific approximate computing unit that skips matrix recomputation when joint angular movement is below a threshold (saving >51% of matrix updates). Communication latency is hidden by pipelining image capture and transmission concurrent with trajectory execution.

## The Key Experiment

- **speedup:** 5.9x end-to-end; 29x control acceleration on FPGA; LLM inference frequency reduced 5.1x
- **energy or tops w:** 9.2x energy reduction (Corki-9 variant)
- **area:** 13.6% DSP, 7.8% FF, 16.9% LUT, 6.6% BRAM on Xilinx Zynq-7000 ZC706
- **ppa:** None
- **accuracy:** Success rate improvement up to 13.9% (up to 17.3% average job length improvement on seen tasks)
- **other:** None

**Compared against:** RoboFlamingo on Nvidia V100 GPU with Intel Core i7-6770HQ CPU control

**Hardware:** FPGA; ASIC; GPU · **Workloads:** LLM-inference; vision

## Why This Approach

Replacing frame-by-frame discrete action prediction with cubic trajectory prediction decouples the LLM inference rate from the control rate, enabling a purpose-built TS-CTC hardware accelerator with approximate computing that achieves 29x control speedup on FPGA.

This paper sits in the **attention efficiency** subtheme. The core constraint: generating one token requires reading all past key-value vectors from memory — O(n) bandwidth per step. This paper's angle: Corki algorithm: predict cubic polynomial robot trajectory for multiple future steps instead of per-frame discrete actions, reducing LLM inference frequency by up to 5.1x..

## What It Leaves Open

- Currently limited to robotic arms with <=9 DoF
- trajectory-based decoupling requires algorithm retraining and may not generalize directly to higher-DoF humanoid robots.

**Tags:** embodied-AI, robot-manipulation, LLM-inference, trajectory-prediction, algorithm-architecture-codesign, approximate-computing
