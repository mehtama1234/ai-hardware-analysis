#!/usr/bin/env bash
set -euo pipefail

REPRO="${TOY_CTS_REPRO:-/home/mehtama1/eda-tools/OpenLane/designs/toy_cts_probe/runs/toy_cts_probe_cts/issue_reproducible}"
WORK_ROOT="${TOY_CTS_WORK_ROOT:-/tmp/toy-cts-characterization-probe}"
TIMEOUT_SECONDS="${TOY_CTS_TIMEOUT_SECONDS:-180}"
OPENLANE_IMAGE="${AIMC_OPENLANE_IMAGE:-ghcr.io/the-openroad-project/openlane:ff5509f65b17bfa4068d5336495ab1718987ff69-amd64}"

if [ ! -f "$REPRO/run.sh" ] || [ ! -f "$REPRO/openlane/scripts/openroad/cts.tcl" ]; then
  echo "FAIL missing toy CTS issue reproducible: $REPRO" >&2
  exit 1
fi

rm -rf "$WORK_ROOT"
mkdir -p "$(dirname "$WORK_ROOT")"
cp -a "$REPRO" "$WORK_ROOT"

CTS_TCL="$WORK_ROOT/openlane/scripts/openroad/cts.tcl"
sed -i 's/lappend -max_cap/lappend cts_characterization_args -max_cap/' "$CTS_TCL"
sed -i 's/lappend -max_slew/lappend cts_characterization_args -max_slew/' "$CTS_TCL"

echo "work_dir,$WORK_ROOT"
echo "timeout_seconds,$TIMEOUT_SECONDS"
echo "patched_cts_tcl,$CTS_TCL"

cd "$WORK_ROOT"
chmod +x run.sh

if ! command -v docker >/dev/null 2>&1; then
  echo "FAIL docker command not found" >&2
  exit 1
fi
if ! timeout 30 docker info >/dev/null 2>&1; then
  echo "FAIL docker daemon does not respond" >&2
  exit 1
fi

if timeout "$TIMEOUT_SECONDS" docker run --rm \
  -v "$WORK_ROOT:/work" \
  -w /work \
  --user "$(id -u):$(id -g)" \
  --network host \
  --security-opt seccomp=unconfined \
  "$OPENLANE_IMAGE" \
  sh -c "TOOL_BIN=openroad ./run.sh" > fixed-characterization.log 2>&1; then
  echo "result,completed"
else
  status=$?
  if [ "$status" -eq 124 ]; then
    echo "result,timeout"
  else
    echo "result,failed"
  fi
fi

grep -E "CTS-0049|CTS-0038|cts_report|Clock Tree|error|Error|ERROR|completed|failed|timeout" fixed-characterization.log | tail -n 80 || true
