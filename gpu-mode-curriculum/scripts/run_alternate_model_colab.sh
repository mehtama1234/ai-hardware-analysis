#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SESSION_NAME="${COLAB_SESSION_NAME:-alternate-model-$(date -u +%Y%m%dT%H%M%S)}"
DEST="${ROOT_DIR}/gpu-runs/imports/${SESSION_NAME}"
mkdir -p "${DEST}"
if colab --auth oauth2 sessions | rg -F "[${SESSION_NAME}]"; then
  echo 'Session name already exists; refusing to reuse.' >&2
  exit 2
fi
colab --auth oauth2 new -s "${SESSION_NAME}" --gpu T4
trap 'colab --auth oauth2 stop -s "${SESSION_NAME}"' EXIT
ARCHIVE="${DEST}/alternate-model-input.tgz"
tar -czf "${ARCHIVE}" -C "${ROOT_DIR}/batch1-decode-vertical-slice" \
  run_continuous_load.py verify_continuous_load.py continuous_http.py \
  continuous_service.py real_model_service.py slot_decode.py graph_decode.py
colab --auth oauth2 upload -s "${SESSION_NAME}" "${ARCHIVE}" /content/alternate-model.tgz
colab --auth oauth2 exec -s "${SESSION_NAME}" -f "${ROOT_DIR}/scripts/run_alternate_model_colab.py" --timeout 3600 || REMOTE_STATUS=$?
REMOTE_STATUS="${REMOTE_STATUS:-0}"
colab --auth oauth2 download -s "${SESSION_NAME}" /content/alternate-model-results.tar.gz "${DEST}/alternate-model-results.tar.gz"
tar -xzf "${DEST}/alternate-model-results.tar.gz" -C "${DEST}"
echo "Evidence saved in ${DEST}"
exit "${REMOTE_STATUS}"
