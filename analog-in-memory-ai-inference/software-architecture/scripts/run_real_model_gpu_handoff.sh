#!/usr/bin/env bash
set -euo pipefail

MODEL="${1:-openai-community/gpt2}"
OUTPUT="${2:-/tmp/transformer-real-model-gpu}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}/.."

python3 -c 'import torch; assert torch.cuda.is_available(), "CUDA device required for GPU handoff"; print(torch.cuda.get_device_name(0))'

python3 scripts/run_real_model_intake.py \
  --model "${MODEL}" \
  --device cuda \
  --output "${OUTPUT}/intake"

python3 scripts/run_real_model_serving_comparison.py \
  --model "${MODEL}" \
  --device cuda \
  --output "${OUTPUT}/serving"

python3 scripts/run_transformer_vertical_slice.py \
  --output "${OUTPUT}/package" \
  --real-model-intake "${OUTPUT}/intake/real_model_intake.json" \
  --real-model-serving-comparison "${OUTPUT}/serving/real_model_serving_comparison.json" \
  --real-model-evidence "${OUTPUT}/serving/real_model_serving_comparison.json"

echo "real-model GPU handoff complete: ${OUTPUT}/package"
