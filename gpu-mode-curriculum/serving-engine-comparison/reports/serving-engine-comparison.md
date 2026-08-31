# Serving Engine Comparison

Generated: `2026-08-31T01:53:09.320857+00:00`
Status: `comparison-ready`
Engines: `5`
Scenarios: `5`
Source trace report: `serving-traces/reports/serving-trace-report.json`

## Scenario Recommendations

| scenario | recommended | runner up | why |
|---|---|---|---|
| interactive-chat | tensorrt-llm | vllm | TensorRT-LLM balances low TTFT with enough throughput for request/response latency. |
| long-context-rag | vllm | tensorrt-llm | vLLM wins on KV-cache pressure and long-context memory efficiency. |
| mixed-prefill-decode | vllm | tensorrt-llm | vLLM has the best weighted score for mixed prefill/decode traffic. |
| offline-throughput | tensorrt-llm | vllm | TensorRT-LLM prioritizes output-token throughput over interactive latency. |
| portable-amd-nvidia | vllm | tgi | vLLM has the strongest cross-vendor and operations-weighted score. |

## Engine Scores

| scenario | engine | score | tok/s | p50 TTFT ms | peak KV blocks | features |
|---|---|---:|---:|---:|---:|---|
| interactive-chat | TensorRT-LLM | 0.889 | 2230.5829 | 1.5593 | 13.26 | engine-build, tensor-parallel, fp8, inflight-batching |
| interactive-chat | vLLM | 0.8821 | 1994.0059 | 1.7495 | 13.94 | paged-attention, continuous-batching, prefix-cache, openai-api |
| interactive-chat | SGLang | 0.8631 | 1926.4125 | 1.6734 | 14.62 | radix-cache, structured-output, speculative-decoding, continuous-batching |
| interactive-chat | Hugging Face TGI | 0.8399 | 1825.0223 | 1.9396 | 15.3 | continuous-batching, hf-hub, tensor-parallel, quantization |
| interactive-chat | HF Transformers Baseline | 0.6831 | 1047.698 | 2.2819 | 19.04 | hf-hub, eager-debugging, torch-compile-option, quantization-baseline |
| long-context-rag | vLLM | 0.8884 | 2661.8947 | 19.6006 | 345.22 | paged-attention, continuous-batching, prefix-cache, openai-api |
| long-context-rag | TensorRT-LLM | 0.862 | 2977.7128 | 17.4701 | 328.38 | engine-build, tensor-parallel, fp8, inflight-batching |
| long-context-rag | Hugging Face TGI | 0.8546 | 2436.3104 | 21.7311 | 378.9 | continuous-batching, hf-hub, tensor-parallel, quantization |
| long-context-rag | SGLang | 0.8489 | 2571.661 | 18.7484 | 362.06 | radix-cache, structured-output, speculative-decoding, continuous-batching |
| long-context-rag | HF Transformers Baseline | 0.7072 | 1398.6227 | 25.566 | 471.52 | hf-hub, eager-debugging, torch-compile-option, quantization-baseline |
| mixed-prefill-decode | vLLM | 0.8797 | 3784.9922 | 7.0766 | 103.32 | paged-attention, continuous-batching, prefix-cache, openai-api |
| mixed-prefill-decode | TensorRT-LLM | 0.862 | 4234.0591 | 6.3074 | 98.28 | engine-build, tensor-parallel, fp8, inflight-batching |
| mixed-prefill-decode | Hugging Face TGI | 0.8466 | 3464.2301 | 7.8458 | 113.4 | continuous-batching, hf-hub, tensor-parallel, quantization |
| mixed-prefill-decode | SGLang | 0.8458 | 3656.6874 | 6.769 | 108.36 | radix-cache, structured-output, speculative-decoding, continuous-batching |
| mixed-prefill-decode | HF Transformers Baseline | 0.6839 | 1988.7247 | 9.2304 | 141.12 | hf-hub, eager-debugging, torch-compile-option, quantization-baseline |
| offline-throughput | TensorRT-LLM | 0.889 | 4234.0591 | 6.3074 | 98.28 | engine-build, tensor-parallel, fp8, inflight-batching |
| offline-throughput | vLLM | 0.8858 | 3784.9922 | 7.0766 | 103.32 | paged-attention, continuous-batching, prefix-cache, openai-api |
| offline-throughput | Hugging Face TGI | 0.8466 | 3464.2301 | 7.8458 | 113.4 | continuous-batching, hf-hub, tensor-parallel, quantization |
| offline-throughput | SGLang | 0.8448 | 3656.6874 | 6.769 | 108.36 | radix-cache, structured-output, speculative-decoding, continuous-batching |
| offline-throughput | HF Transformers Baseline | 0.6303 | 1988.7247 | 9.2304 | 141.12 | hf-hub, eager-debugging, torch-compile-option, quantization-baseline |
| portable-amd-nvidia | vLLM | 0.8602 | 2661.8947 | 19.6006 | 345.22 | paged-attention, continuous-batching, prefix-cache, openai-api |
| portable-amd-nvidia | Hugging Face TGI | 0.8594 | 2436.3104 | 21.7311 | 378.9 | continuous-batching, hf-hub, tensor-parallel, quantization |
| portable-amd-nvidia | SGLang | 0.8073 | 2571.661 | 18.7484 | 362.06 | radix-cache, structured-output, speculative-decoding, continuous-batching |
| portable-amd-nvidia | TensorRT-LLM | 0.762 | 2977.7128 | 17.4701 | 328.38 | engine-build, tensor-parallel, fp8, inflight-batching |
| portable-amd-nvidia | HF Transformers Baseline | 0.7476 | 1398.6227 | 25.566 | 471.52 | hf-hub, eager-debugging, torch-compile-option, quantization-baseline |

## GPU Host Promotion

Scores are deterministic local estimates from trace replay; production acceptance requires measured vLLM/TGI/SGLang/TensorRT-LLM runs on a GPU host.
