#!/usr/bin/env bash
set -euo pipefail

REPRO="${AIMC_CTS_REPRO:-/home/mehtama1/eda-tools/OpenLane/designs/aimc_operation_partition_output_registered/runs/aimc_operation_partition_output_registered_cts/issue_reproducible}"
WORK_ROOT="${AIMC_CTS_WORK_ROOT:-/tmp/aimc-operation-partition-cts-experiments}"
VARIANT="${1:-list}"
TIMEOUT_SECONDS="${AIMC_CTS_TIMEOUT_SECONDS:-180}"
RUNNER="${AIMC_CTS_RUNNER:-auto}"
OPENLANE_IMAGE="${AIMC_OPENLANE_IMAGE:-ghcr.io/the-openroad-project/openlane:ff5509f65b17bfa4068d5336495ab1718987ff69-amd64}"

usage() {
  cat <<'USAGE'
Usage:
  ./run_isolated_cts_experiment.sh list
  ./run_isolated_cts_experiment.sh baseline
  ./run_isolated_cts_experiment.sh single_corner
  ./run_isolated_cts_experiment.sh small_clusters
  ./run_isolated_cts_experiment.sh no_post_processing

Environment:
  AIMC_CTS_REPRO            OpenLane issue_reproducible directory.
  AIMC_CTS_WORK_ROOT        Scratch directory for copied experiments.
  AIMC_CTS_TIMEOUT_SECONDS  Timeout per experiment, default 180.
  AIMC_CTS_RUNNER           auto, host, or docker. Default auto.
  AIMC_OPENLANE_IMAGE       Docker image for docker runner.

The script copies the OpenLane issue reproducible before editing it.
USAGE
}

if [ "$VARIANT" = "list" ] || [ "$VARIANT" = "--help" ] || [ "$VARIANT" = "-h" ]; then
  usage
  exit 0
fi

case "$VARIANT" in
  baseline|single_corner|small_clusters|no_post_processing) ;;
  *)
    echo "FAIL unknown CTS experiment variant: $VARIANT" >&2
    usage >&2
    exit 1
    ;;
esac

if [ ! -f "$REPRO/run.sh" ] || [ ! -f "$REPRO/run.tcl" ]; then
  echo "FAIL reproducible does not contain run.sh and run.tcl: $REPRO" >&2
  exit 1
fi

DEST="$WORK_ROOT/$VARIANT"
rm -rf "$DEST"
mkdir -p "$WORK_ROOT"
cp -a "$REPRO" "$DEST"

case "$VARIANT" in
  baseline)
    ;;
  single_corner)
    sed -i 's/export CTS_MULTICORNER_LIB=.*/export CTS_MULTICORNER_LIB='\''0'\'';/' "$DEST/run.sh"
    sed -i 's/set ::env(CTS_MULTICORNER_LIB) "1";/set ::env(CTS_MULTICORNER_LIB) "0";/' "$DEST/run.tcl"
    ;;
  small_clusters)
    sed -i 's/export CTS_SINK_CLUSTERING_SIZE=.*/export CTS_SINK_CLUSTERING_SIZE='\''8'\'';/' "$DEST/run.sh"
    sed -i 's/export CTS_SINK_CLUSTERING_MAX_DIAMETER=.*/export CTS_SINK_CLUSTERING_MAX_DIAMETER='\''12'\'';/' "$DEST/run.sh"
    sed -i 's/set ::env(CTS_SINK_CLUSTERING_SIZE) "25";/set ::env(CTS_SINK_CLUSTERING_SIZE) "8";/' "$DEST/run.tcl"
    sed -i 's/set ::env(CTS_SINK_CLUSTERING_MAX_DIAMETER) "50";/set ::env(CTS_SINK_CLUSTERING_MAX_DIAMETER) "12";/' "$DEST/run.tcl"
    ;;
  no_post_processing)
    sed -i 's/export CTS_DISABLE_POST_PROCESSING=.*/export CTS_DISABLE_POST_PROCESSING='\''1'\'';/' "$DEST/run.sh"
    sed -i 's/set ::env(CTS_DISABLE_POST_PROCESSING) "0";/set ::env(CTS_DISABLE_POST_PROCESSING) "1";/' "$DEST/run.tcl"
    ;;
esac

echo "variant,$VARIANT"
echo "work_dir,$DEST"
echo "timeout_seconds,$TIMEOUT_SECONDS"
echo "run,$DEST/run.sh"
echo "runner,$RUNNER"

cd "$DEST"
chmod +x run.sh

if [ "$RUNNER" = "auto" ]; then
  if command -v openroad >/dev/null 2>&1; then
    RUNNER="host"
  else
    RUNNER="docker"
  fi
fi

case "$RUNNER" in
  host)
    run_cmd=(timeout "$TIMEOUT_SECONDS" ./run.sh)
    ;;
  docker)
    if ! command -v docker >/dev/null 2>&1; then
      echo "FAIL docker command not found" >&2
      exit 1
    fi
    if ! timeout 30 docker info >/dev/null 2>&1; then
      echo "FAIL docker daemon does not respond" >&2
      exit 1
    fi
    run_cmd=(
      timeout "$TIMEOUT_SECONDS"
      docker run --rm
      -v "$DEST:/work"
      -w /work
      --user "$(id -u):$(id -g)"
      --network host
      --security-opt seccomp=unconfined
      "$OPENLANE_IMAGE"
      sh -c "TOOL_BIN=openroad ./run.sh"
    )
    ;;
  *)
    echo "FAIL unknown AIMC_CTS_RUNNER: $RUNNER" >&2
    exit 1
    ;;
esac

if "${run_cmd[@]}" > "experiment-$VARIANT.log" 2>&1; then
  echo "result,completed"
else
  status=$?
  if [ "$status" -eq 124 ]; then
    echo "result,timeout"
  else
    echo "result,failed"
  fi
fi

if [ -f "experiment-$VARIANT.log" ]; then
  grep -E "CTS-0049|CTS-0038|Number of created patterns|Clock Tree|error|Error|ERROR" "experiment-$VARIANT.log" | tail -n 40 || true
fi
