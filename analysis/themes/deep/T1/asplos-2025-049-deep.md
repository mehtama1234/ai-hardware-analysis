# Past-Future Scheduler for LLM Serving under SLA Guarantees

**Venue:** ASPLOS · **Theme:** KV Cache Scheduling

## What It Does

LLM serving frameworks using continuous batching suffer from either overestimation of memory consumption (conservative schedulers) or underestimation leading to harmful request evictions (aggressive schedulers), because neither accurately accounts for the dynamic memory release profile of concurrently running requests across future decoding steps.

As LLM inference scales to thousands of GPUs serving tens of millions of requests per day under strict SLA constraints (TTFT, TPOT, MTPOT), maximizing goodput (SLA-satisfying throughput) requires precise KV-cache memory estimation that adapts to varying input-output length distributions across chatbot, code, and reasoning workloads.

The Past-Future scheduler combines two components: (1) output length distribution prediction that samples predicted output lengths from the empirical distribution of recent historical requests (a sliding window of ~1,000 finished requests), updating each running request's predicted remaining length at every decode step using the conditional distribution P(l > l_current); and (2) future required memory estimation that sorts running requests by estimated remaining length, computes memory occupancy at each future completion event, and determines peak future memory as max(M_t+1, M_t+2, ...) across all future completion times. A queued request is admitted only if adding it keeps peak future memory below hardware capacity. This is implemented in LightLLM with <1% scheduling overhead using GPU-parallel computation.

## The Key Experiment

- **speedup:** 2-3x higher goodput over aggressive/conservative schedulers under heavy load
- **energy or tops w:** None
- **area:** None
- **ppa:** None
- **accuracy:** None
- **other:** Memory utilization approaches theoretical optimum (93-94% vs 98% oracle) while eviction rate drops to ~3-7% vs 93% for aggressive at watermark=99%; 50-60% throughput improvement on multimodal LLaVA and Qwen-VL models

**Compared against:** vLLM (aggressive scheduler); TGI (conservative scheduler); DeepSpeed-MII / FastGen (conservative); TensorRT-LLM (conservative)

**Hardware:** GPU · **Workloads:** LLM-inference; attention

## Why This Approach

The observation that LLM output length distributions are stable within adjacent time windows enables a parameter-free, model-agnostic historical-distribution sampling approach to precisely estimate peak future KV-cache memory demand for the entire running batch, eliminating both conservative underutilization and aggressive eviction.

This paper sits in the **attention efficiency** subtheme. The core constraint: generating one token requires reading all past key-value vectors from memory — O(n) bandwidth per step. This paper's angle: Discovery that LLM request output length distributions are stable within adjacent time windows, validated on six real-world trace datasets including BurstGPT and Mooncake..

## What It Leaves Open

- The scheduler relies on distribution stationarity within adjacent time windows and may perform poorly if output length distributions shift abruptly (e.g., sudden workload type change)
- warm-up period needed at service startup.

**Tags:** LLM-serving, KV-cache, scheduling, SLA, continuous-batching
