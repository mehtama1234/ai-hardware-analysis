#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SESSION_NAME="${COLAB_SESSION_NAME:-architecture-characterization-$(date -u +%Y%m%dT%H%M%S)}"
ACCELERATOR="${COLAB_GPU:-T4}"
DEST="${ROOT_DIR}/gpu-runs/imports/${SESSION_NAME}"
mkdir -p "${DEST}"
if colab --auth oauth2 sessions | rg -F "[${SESSION_NAME}]"; then exit 2; fi
colab --auth oauth2 new -s "${SESSION_NAME}" --gpu "${ACCELERATOR}"
trap 'colab --auth oauth2 stop -s "${SESSION_NAME}"' EXIT
ARCHIVE="${DEST}/architecture-characterization-input.tgz"
MODE_FILE="${DEST}/architecture-mode.json"
printf '{"mode":"%s","profile":%s,"seconds":%s}\n' "${ARCHITECTURE_MODE:-full}" "${ARCHITECTURE_PROFILE:-0}" "${ARCHITECTURE_SECONDS:-4}" > "${MODE_FILE}"
tar -czf "${ARCHIVE}" -C "${ROOT_DIR}/batch1-decode-vertical-slice" \
  run_real_model_serving_characterization.py verify_serving_characterization.py \
  static_cache_graph_probe.py verify_static_cache_graph_probe.py \
  static_graph_bucket.py run_static_graph_bucket.py verify_static_graph_bucket.py \
  run_static_graph_http.py verify_static_graph_http.py \
  run_continuous_load.py verify_continuous_load.py hf_slot_decode.py \
  run_serving_comparison.py verify_serving_comparison.py microbatch_control.py \
  continuous_http.py continuous_service.py real_model_service.py slot_decode.py graph_decode.py \
  static_cache_graph_probe.py \
  -C "${DEST}" architecture-mode.json
colab --auth oauth2 upload -s "${SESSION_NAME}" "${ARCHIVE}" /content/architecture-characterization.tgz
colab --auth oauth2 exec -s "${SESSION_NAME}" -f "${ROOT_DIR}/scripts/run_architecture_colab.py" --timeout 1800 || REMOTE_STATUS=$?
REMOTE_STATUS="${REMOTE_STATUS:-0}"
colab --auth oauth2 download -s "${SESSION_NAME}" /content/architecture-characterization-results.tgz "${DEST}/architecture-characterization-results.tgz"
tar -xzf "${DEST}/architecture-characterization-results.tgz" -C "${DEST}"
echo "Evidence saved in ${DEST}"
exit "${REMOTE_STATUS}"
