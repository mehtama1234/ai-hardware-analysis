#!/usr/bin/env bash
set -euo pipefail

SESSION_NAME="${COLAB_SESSION_NAME:-gpu-mode-handoff}"
GPU_TYPE="${COLAB_GPU_TYPE:-T4}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TOKEN_PATH="${HOME}/.config/colab-cli/token.json"

echo "== Colab CLI auth bootstrap =="
echo "Repo: ${ROOT_DIR}"
echo "Session: ${SESSION_NAME}"
echo "Requested GPU: ${GPU_TYPE}"
echo

if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  echo "ERROR: ${PYTHON_BIN} is not available on PATH." >&2
  exit 1
fi

install_colab_cli() {
  if command -v uv >/dev/null 2>&1; then
    echo "Installing google-colab-cli with uv tool install ..."
    if uv tool install google-colab-cli; then
      return 0
    fi
  fi

  if command -v pipx >/dev/null 2>&1; then
    echo "Installing google-colab-cli with pipx ..."
    if pipx install google-colab-cli; then
      return 0
    fi
  fi

  echo "Installing google-colab-cli with ${PYTHON_BIN} -m pip --user ..."
  if "${PYTHON_BIN}" -m pip install --user google-colab-cli; then
    return 0
  fi

  echo "Installing google-colab-cli from GitHub source with ${PYTHON_BIN} -m pip --user ..."
  "${PYTHON_BIN}" -m pip install --user "git+https://github.com/googlecolab/google-colab-cli.git"
}

if ! command -v colab >/dev/null 2>&1; then
  install_colab_cli
fi

if ! command -v colab >/dev/null 2>&1; then
  USER_BASE="$("${PYTHON_BIN}" -m site --user-base)"
  export PATH="${USER_BASE}/bin:${PATH}"
fi

if ! command -v colab >/dev/null 2>&1; then
  echo "ERROR: colab command still not found after install." >&2
  echo "Try adding your Python user bin directory to PATH, then rerun this script." >&2
  exit 1
fi

echo "Using Colab CLI: $(command -v colab)"
colab version || true
echo

cat <<'MSG'
Next, the Colab CLI may print a Google authorization URL.
Open that URL in your browser, sign into the Google account with Colab GPU access,
approve the request, then paste the returned code back into this terminal.

Do not paste that code or any token into chat.
MSG
echo

colab --auth oauth2 sessions || true

echo
if [[ -f "${TOKEN_PATH}" ]]; then
  echo "Auth cache found: ${TOKEN_PATH}"
else
  echo "Auth cache was not found at ${TOKEN_PATH}."
  echo "If the auth step above showed a URL, rerun the command after completing it:"
  echo "  colab --auth oauth2 sessions"
  exit 2
fi

echo
echo "Testing a short GPU session allocation. This may consume Colab compute units."
echo "Press Ctrl-C now if you only wanted to authenticate."
sleep 8

set +e
colab --auth oauth2 new -s "${SESSION_NAME}" --gpu "${GPU_TYPE}"
NEW_EXIT=$?
set -e

if [[ "${NEW_EXIT}" -ne 0 ]]; then
  echo
  echo "Colab auth exists, but GPU session allocation failed."
  echo "This is usually one of: no available ${GPU_TYPE}, no Colab Pro entitlement, quota exhausted, or missing consent."
  echo "You can retry with another GPU, for example:"
  echo "  COLAB_GPU_TYPE=L4 ${BASH_SOURCE[0]}"
  echo "  COLAB_GPU_TYPE=A100 ${BASH_SOURCE[0]}"
  exit "${NEW_EXIT}"
fi

echo
echo "Colab session is ready. URL:"
colab --auth oauth2 url -s "${SESSION_NAME}" || true
echo
echo "Stopping the test session so it does not burn compute."
colab --auth oauth2 stop -s "${SESSION_NAME}" || true

cat <<MSG

Done. Credentials are now local to this machine in:
  ${TOKEN_PATH}

Tell Codex this exact line when finished:
  Colab CLI auth is done; use session name ${SESSION_NAME} and GPU ${GPU_TYPE}.

MSG
