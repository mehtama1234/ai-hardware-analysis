#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SESSION_NAME="${COLAB_SESSION_NAME:-${GRAPH_EXPERIMENT:-graph}-decode-$(date -u +%Y%m%dT%H%M%S)}"
DEST="${ROOT_DIR}/gpu-runs/imports/${SESSION_NAME}"
mkdir -p "${DEST}"
if colab --auth oauth2 sessions | rg -F "[${SESSION_NAME}]"; then
  echo 'Session name already exists; refusing to reuse.' >&2
  exit 2
fi
colab --auth oauth2 new -s "${SESSION_NAME}" --gpu T4
trap 'colab --auth oauth2 stop -s "${SESSION_NAME}"' EXIT
colab --auth oauth2 sessions > "${DEST}/colab-session.txt"
for file in graph_decode.py run_real_model_graph_decode.py; do
  colab --auth oauth2 upload -s "${SESSION_NAME}" "${ROOT_DIR}/batch1-decode-vertical-slice/${file}" "/content/${file}"
done
colab --auth oauth2 upload -s "${SESSION_NAME}" "${ROOT_DIR}/batch1-decode-vertical-slice/tests/test_graph_decode.py" /content/test_graph_decode.py
if [[ "${GRAPH_EXPERIMENT:-graph}" == "slots" || "${GRAPH_EXPERIMENT:-graph}" == "continuous" || "${GRAPH_EXPERIMENT:-graph}" == "load" || "${GRAPH_EXPERIMENT:-graph}" == "comparison" ]]; then
  for file in slot_decode.py run_slot_decode.py; do
    colab --auth oauth2 upload -s "${SESSION_NAME}" "${ROOT_DIR}/batch1-decode-vertical-slice/${file}" "/content/${file}"
  done
  colab --auth oauth2 upload -s "${SESSION_NAME}" "${ROOT_DIR}/batch1-decode-vertical-slice/tests/test_slot_decode.py" /content/test_slot_decode.py
fi
if [[ "${GRAPH_EXPERIMENT:-graph}" == "continuous" || "${GRAPH_EXPERIMENT:-graph}" == "load" || "${GRAPH_EXPERIMENT:-graph}" == "comparison" ]]; then
  for file in continuous_service.py real_model_service.py run_continuous_http.py; do
    colab --auth oauth2 upload -s "${SESSION_NAME}" "${ROOT_DIR}/batch1-decode-vertical-slice/${file}" "/content/${file}"
  done
  colab --auth oauth2 upload -s "${SESSION_NAME}" "${ROOT_DIR}/batch1-decode-vertical-slice/tests/test_continuous_service.py" /content/test_continuous_service.py
fi
if [[ "${GRAPH_EXPERIMENT:-graph}" == "load" || "${GRAPH_EXPERIMENT:-graph}" == "comparison" ]]; then
  for file in continuous_http.py run_continuous_load.py; do
    colab --auth oauth2 upload -s "${SESSION_NAME}" "${ROOT_DIR}/batch1-decode-vertical-slice/${file}" "/content/${file}"
  done
  colab --auth oauth2 upload -s "${SESSION_NAME}" "${ROOT_DIR}/batch1-decode-vertical-slice/tests/test_continuous_http.py" /content/test_continuous_http.py
fi
if [[ "${GRAPH_EXPERIMENT:-graph}" == "comparison" ]]; then
  for file in microbatch_control.py run_serving_comparison.py; do
    colab --auth oauth2 upload -s "${SESSION_NAME}" "${ROOT_DIR}/batch1-decode-vertical-slice/${file}" "/content/${file}"
  done
  colab --auth oauth2 upload -s "${SESSION_NAME}" "${ROOT_DIR}/batch1-decode-vertical-slice/tests/test_microbatch_control.py" /content/test_microbatch_control.py
fi
if [[ -n "${GRAPH_REPLAY_REPORT:-}" ]]; then
  colab --auth oauth2 upload -s "${SESSION_NAME}" "${GRAPH_REPLAY_REPORT}" /content/graph-original.json
  colab --auth oauth2 upload -s "${SESSION_NAME}" "$(dirname "${GRAPH_REPLAY_REPORT}")/graph-decode-source.tar.gz" /content/graph-decode-source.tar.gz
  colab --auth oauth2 upload -s "${SESSION_NAME}" "${ROOT_DIR}/batch1-decode-vertical-slice/replay_graph_decode.py" /content/replay_graph_decode.py
fi
REMOTE_STATUS=0
if [[ -n "${SERVING_REPLAY_REPORT:-}" ]]; then
  colab --auth oauth2 upload -s "${SESSION_NAME}" "${SERVING_REPLAY_REPORT}" /content/serving-original.json
  colab --auth oauth2 upload -s "${SESSION_NAME}" "$(dirname "${SERVING_REPLAY_REPORT}")/serving-source.tar.gz" /content/serving-source.tar.gz
  for file in replay_serving_comparison.py replay_graph_decode.py verify_serving_comparison.py verify_continuous_load.py; do
    colab --auth oauth2 upload -s "${SESSION_NAME}" "${ROOT_DIR}/batch1-decode-vertical-slice/${file}" "/content/${file}"
  done
fi
colab --auth oauth2 exec -s "${SESSION_NAME}" -f "${ROOT_DIR}/scripts/run_graph_decode_colab.py" --timeout 3600 || REMOTE_STATUS=$?
colab --auth oauth2 download -s "${SESSION_NAME}" /content/graph-decode-results.tar.gz "${DEST}/graph-decode-results.tar.gz"
tar -xzf "${DEST}/graph-decode-results.tar.gz" -C "${DEST}"
echo "Evidence saved in ${DEST}"
exit "${REMOTE_STATUS}"
