#!/usr/bin/env bash
set -u

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
VENV_PY="$BACKEND_DIR/.venv/bin/python"
TOOLS_DIR="$ROOT_DIR/external-tools"
REPORT_DIR="$ROOT_DIR/backend/.data/toolkit-install"
REPORT_FILE="$REPORT_DIR/install-report.txt"

mkdir -p "$TOOLS_DIR" "$REPORT_DIR"
: > "$REPORT_FILE"

log() {
  printf '%s\n' "$*"
  printf '%s\n' "$*" >> "$REPORT_FILE"
}

run() {
  log ""
  log "==> $*"
  "$@"
  local rc=$?
  if [ "$rc" -eq 0 ]; then
    log "OK: $*"
  else
    log "FAILED ($rc): $*"
  fi
  return "$rc"
}

clone_or_update() {
  local url="$1"
  local dir="$2"
  if [ -d "$dir/.git" ]; then
    log ""
    log "==> Updating $dir"
    git -C "$dir" pull --ff-only
    local rc=$?
    if [ "$rc" -eq 0 ]; then
      log "OK: updated $dir"
    else
      log "FAILED ($rc): update $dir"
    fi
    return "$rc"
  fi
  run git clone "$url" "$dir"
}

have_cmd() {
  command -v "$1" >/dev/null 2>&1
}

log "AIMC toolkit installer"
log "Root: $ROOT_DIR"
log "Report: $REPORT_FILE"
log "Date: $(date -Is)"

if [ ! -x "$VENV_PY" ]; then
  log "FAILED: backend venv Python not found at $VENV_PY"
  log "Create the backend venv first, then rerun this script."
  exit 1
fi

log ""
log "Environment"
log "Python: $("$VENV_PY" --version 2>&1)"
log "Pip: $("$VENV_PY" -m pip --version 2>&1)"
log "Disk:"
df -h "$ROOT_DIR" | tee -a "$REPORT_FILE"

log ""
log "Step 1: Python package tooling"
run "$VENV_PY" -m pip install --upgrade pip setuptools wheel

log ""
log "Step 2: Install Python-runnable AIMC simulators"
run "$VENV_PY" -m pip install aihwkit

clone_or_update "https://github.com/sandialabs/cross-sim.git" "$TOOLS_DIR/cross-sim"
if [ -d "$TOOLS_DIR/cross-sim" ]; then
  run "$VENV_PY" -m pip install "$TOOLS_DIR/cross-sim"
fi

log ""
log "Step 3: Install local build helper for gem5/ALPINE"
run "$VENV_PY" -m pip install scons

log ""
log "Step 4: Clone compiler and system simulator source trees"
clone_or_update "https://github.com/PlatinumCD/analog-mlir.git" "$TOOLS_DIR/analog-mlir"
clone_or_update "https://github.com/gem5-X/ALPINE.git" "$TOOLS_DIR/ALPINE"
clone_or_update "https://github.com/sstsimulator/sst-core.git" "$TOOLS_DIR/sst-core"

log ""
log "Step 5: Run AIHWKIT smoke"
"$VENV_PY" - <<'PY' 2>&1 | tee -a "$REPORT_FILE"
import torch
import aihwkit
from aihwkit.nn import AnalogLinear
from aihwkit.simulator.configs import TorchInferenceRPUConfig
torch.manual_seed(7)
layer = AnalogLinear(4, 2, rpu_config=TorchInferenceRPUConfig())
x = torch.tensor([[1.0, -0.5, 0.25, 2.0]], dtype=torch.float32)
y = layer(x).detach()
print("AIHWKIT_SMOKE=ok")
print("torch_version=" + str(torch.__version__))
print("aihwkit_version=" + str(getattr(aihwkit, "__version__", "unknown")))
print("analog_forward_shape=" + str(tuple(y.shape)))
print("analog_forward_sum=" + str(round(float(y.sum()), 6)))
PY
AIHWKIT_RC=${PIPESTATUS[0]}
if [ "$AIHWKIT_RC" -eq 0 ]; then
  log "OK: AIHWKIT smoke"
else
  log "FAILED ($AIHWKIT_RC): AIHWKIT smoke"
fi

log ""
log "Step 6: Run CrossSim smoke"
"$VENV_PY" - <<'PY' 2>&1 | tee -a "$REPORT_FILE"
import numpy as np
from simulator import AnalogCore, CrossSimParameters
params = CrossSimParameters()
weights = np.array([[1.0, -0.5], [0.25, 0.75]], dtype=float)
vector = np.array([2.0, 4.0], dtype=float)
core = AnalogCore(weights, params=params)
analog = core @ vector
ideal = weights @ vector
print("CROSSSIM_SMOKE=ok")
print("analog=" + str(np.round(analog, 6).tolist()))
print("ideal=" + str(np.round(ideal, 6).tolist()))
print("max_abs_error=" + str(float(np.max(np.abs(analog - ideal)))))
PY
CROSSSIM_RC=${PIPESTATUS[0]}
if [ "$CROSSSIM_RC" -eq 0 ]; then
  log "OK: CrossSim smoke"
else
  log "FAILED ($CROSSSIM_RC): CrossSim smoke"
fi

log ""
log "Step 7: Try analog-mlir configure"
ANALOG_MLIR_RC=1
if [ -d "$TOOLS_DIR/analog-mlir" ]; then
  if [ -x "$BACKEND_DIR/.venv/bin/cmake" ]; then
    "$BACKEND_DIR/.venv/bin/cmake" -S "$TOOLS_DIR/analog-mlir" -B "$TOOLS_DIR/analog-mlir/build" 2>&1 | tee -a "$REPORT_FILE"
    ANALOG_MLIR_RC=${PIPESTATUS[0]}
  elif have_cmd cmake; then
    cmake -S "$TOOLS_DIR/analog-mlir" -B "$TOOLS_DIR/analog-mlir/build" 2>&1 | tee -a "$REPORT_FILE"
    ANALOG_MLIR_RC=${PIPESTATUS[0]}
  else
    log "FAILED: cmake not found for analog-mlir configure."
  fi
fi
if [ "$ANALOG_MLIR_RC" -eq 0 ]; then
  log "OK: analog-mlir configured"
else
  log "BLOCKED: analog-mlir needs LLVM/MLIR development files. Missing symptom is usually MLIRConfig.cmake."
fi

log ""
log "Step 8: Try ALPINE AIMClib checker"
ALPINE_RC=1
if [ -d "$TOOLS_DIR/ALPINE/aimclib" ]; then
  (
    cd "$TOOLS_DIR/ALPINE/aimclib" &&
    g++ -O3 -DUSE_CHECKER -include cstdint example.cc -o example_checker.out &&
    ./example_checker.out
  ) 2>&1 | tee -a "$REPORT_FILE"
  ALPINE_RC=${PIPESTATUS[0]}
fi
if [ "$ALPINE_RC" -eq 0 ]; then
  log "OK: ALPINE AIMClib checker compiled and ran."
else
  log "FAILED: ALPINE AIMClib checker did not compile or run."
fi

log ""
log "Step 9: Try ALPINE gem5-X build probe"
ALPINE_GEM5_RC=1
if [ -d "$TOOLS_DIR/ALPINE/gem5-X-ALPINE" ] && [ -x "$BACKEND_DIR/.venv/bin/scons" ]; then
  (
    cd "$TOOLS_DIR/ALPINE/gem5-X-ALPINE" &&
    "$BACKEND_DIR/.venv/bin/scons" build/ARM/gem5.opt -j2
  ) 2>&1 | tee -a "$REPORT_FILE"
  ALPINE_GEM5_RC=${PIPESTATUS[0]}
fi
if [ "$ALPINE_GEM5_RC" -eq 0 ]; then
  log "OK: ALPINE gem5-X built."
else
  log "BLOCKED: ALPINE gem5-X did not build. Common blockers: Python 2-era SCons scripts, missing Python 2/SCons, or gem5 system dependencies."
fi

log ""
log "Step 10: Try SST bootstrap"
SST_RC=1
if [ -d "$TOOLS_DIR/sst-core" ]; then
  (
    cd "$TOOLS_DIR/sst-core" &&
    ./autogen.sh
  ) 2>&1 | tee -a "$REPORT_FILE"
  SST_RC=${PIPESTATUS[0]}
fi
if [ "$SST_RC" -eq 0 ]; then
  log "OK: SST bootstrap completed. Next step: configure and make install into a local prefix."
else
  log "BLOCKED: SST bootstrap failed. Common blocker: missing libtool/autoconf/automake/OpenMPI development tools."
fi

log ""
log "System packages likely needed for the blocked source builds:"
log "  sudo apt-get update"
log "  sudo apt-get install -y build-essential git autoconf automake libtool pkg-config libopenmpi-dev openmpi-bin python2 python2.7 scons libmlir-15-dev mlir-15-tools llvm-15-dev"
log ""
log "After installing system packages, rerun:"
log "  bash scripts/install-aimc-toolkits.sh"
log ""
log "Frontend:"
log "  http://127.0.0.1:8080/toolkit-results-first-principles.html"
log ""
log "Done. Full report written to:"
log "  $REPORT_FILE"
