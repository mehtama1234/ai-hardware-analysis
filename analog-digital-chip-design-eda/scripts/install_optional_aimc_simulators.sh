#!/usr/bin/env bash
set -euo pipefail

INSTALL_ROOT="${INSTALL_ROOT:-$HOME/eda-tools}"
VENV_DIR="${VENV_DIR:-$INSTALL_ROOT/aimc-simulators-venv}"
CROSSSIM_DIR="${CROSSSIM_DIR:-$INSTALL_ROOT/cross-sim}"
AIHWKIT_SPEC="${AIHWKIT_SPEC:-aihwkit==1.1.0}"
VENV_SYSTEM_SITE_PACKAGES="${VENV_SYSTEM_SITE_PACKAGES:-1}"

usage() {
  cat <<'MSG'
Install optional analog in-memory compute simulator adapters.

Usage:
  ./scripts/install_optional_aimc_simulators.sh --aihwkit
  ./scripts/install_optional_aimc_simulators.sh --crosssim
  ./scripts/install_optional_aimc_simulators.sh --all

Options:
  --aihwkit   Install IBM AIHWKIT into the local simulator virtualenv.
  --crosssim  Clone/update Sandia CrossSim and install it into the virtualenv.
  --all       Install both optional adapters.
  --help      Show this help.

Environment:
  INSTALL_ROOT   Default: $HOME/eda-tools
  VENV_DIR       Default: $INSTALL_ROOT/aimc-simulators-venv
  CROSSSIM_DIR   Default: $INSTALL_ROOT/cross-sim
  AIHWKIT_SPEC   Default: aihwkit==1.1.0
  VENV_SYSTEM_SITE_PACKAGES  Default: 1; expose the host PyTorch to the adapter venv

After install:
  source "$VENV_DIR/bin/activate"
  ./scripts/check_tools.sh
  python3 scripts/check_aimc_simulator_adapters.py

These tools are optional. Installing them may strengthen simulator evidence only
after a real run produces a strict payload accepted by the guarded importer.
MSG
}

want_aihwkit=0
want_crosssim=0

if [ "$#" -eq 0 ]; then
  usage
  exit 1
fi

for arg in "$@"; do
  case "$arg" in
    --aihwkit)
      want_aihwkit=1
      ;;
    --crosssim)
      want_crosssim=1
      ;;
    --all)
      want_aihwkit=1
      want_crosssim=1
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $arg" >&2
      usage
      exit 1
      ;;
  esac
done

ensure_python_venv() {
  if [ ! -d "$VENV_DIR" ]; then
    if [ "$VENV_SYSTEM_SITE_PACKAGES" = "1" ]; then
      python3 -m venv --system-site-packages "$VENV_DIR"
    else
      python3 -m venv "$VENV_DIR"
    fi
  fi
  "$VENV_DIR/bin/python" -m pip install --upgrade pip setuptools wheel
}

install_aihwkit() {
  ensure_python_venv
  # Colab and the lab simulator environment own the PyTorch installation.
  # Installing AIHWKIT with dependencies would silently replace it with a
  # large, unrelated CUDA stack. The pinned wheel is the adapter boundary;
  # reject a host without torch before downloading the adapter wheel.
  if ! "$VENV_DIR/bin/python" -c 'import torch' >/dev/null 2>&1; then
    echo "AIHWKIT requires an existing PyTorch installation in $VENV_DIR; refusing to install dependencies automatically." >&2
    return 2
  fi
  "$VENV_DIR/bin/python" -m pip install --no-deps "$AIHWKIT_SPEC"
  "$VENV_DIR/bin/python" - <<'PY'
import aihwkit
import torch
print(f"AIHWKIT {getattr(aihwkit, '__version__', 'unknown')} PyTorch {torch.__version__}")
PY
}

install_crosssim() {
  ensure_python_venv
  mkdir -p "$INSTALL_ROOT"
  if [ ! -d "$CROSSSIM_DIR/.git" ]; then
    git clone https://github.com/sandialabs/cross-sim.git "$CROSSSIM_DIR"
  else
    git -C "$CROSSSIM_DIR" pull --ff-only
  fi
  "$VENV_DIR/bin/python" -m pip install "$CROSSSIM_DIR"
}

if [ "$want_aihwkit" -eq 1 ]; then
  install_aihwkit
fi

if [ "$want_crosssim" -eq 1 ]; then
  install_crosssim
fi

cat <<MSG

Done. To use the optional simulator environment:
  source "$VENV_DIR/bin/activate"
  ./scripts/check_tools.sh
  python3 scripts/check_aimc_simulator_adapters.py
MSG
