#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DESIGN_NAME="${AIMC_OPENLANE_DESIGN:-aimc_control_plane}"
PREP_NAME="${AIMC_OPENLANE_PREP:-aimc-control-plane-openlane-prep}"
RTL_FILE="${AIMC_OPENLANE_RTL:-$DESIGN_NAME.v}"
SOURCE_DIR="$ROOT/labs/eda/$PREP_NAME"
OPENLANE_ROOT="${OPENLANE_ROOT:-$HOME/eda-tools/OpenLane}"
TARGET_DIR="$OPENLANE_ROOT/designs/$DESIGN_NAME"
TAG="${TAG:-aimc_control_plane_local}"
CONFIG_NAME="${CONFIG_NAME:-config}"

if [ ! -f "$OPENLANE_ROOT/flow.tcl" ]; then
  echo "FAIL OpenLane flow.tcl not found at $OPENLANE_ROOT/flow.tcl" >&2
  exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "FAIL docker command not found" >&2
  exit 1
fi

if ! timeout 30 docker info >/dev/null 2>&1; then
  echo "FAIL docker daemon does not respond" >&2
  exit 1
fi

OPENLANE_ARCH=""
if [ -f "$OPENLANE_ROOT/docker/current_platform.py" ]; then
  OPENLANE_ARCH="$(python3 "$OPENLANE_ROOT/docker/current_platform.py" 2>/dev/null || true)"
fi
if [ -n "$OPENLANE_ARCH" ]; then
  IMAGE_PATTERN="(^efabless/openlane:.*-$OPENLANE_ARCH$|^ghcr.io/the-openroad-project/openlane:.*-$OPENLANE_ARCH$)"
else
  IMAGE_PATTERN='(^efabless/openlane:|^ghcr.io/the-openroad-project/openlane:)'
fi

if ! timeout 60 docker images --format '{{.Repository}}:{{.Tag}}' 2>/dev/null | grep -Eq "$IMAGE_PATTERN"; then
  echo "FAIL OpenLane Docker image is missing" >&2
  echo "Try from $OPENLANE_ROOT:" >&2
  echo "  make pull-openlane" >&2
  if [ -n "$OPENLANE_ARCH" ]; then
    echo "Then make sure the architecture image exists, for example a tag ending in -$OPENLANE_ARCH." >&2
  fi
  exit 1
fi

mkdir -p "$TARGET_DIR/src"
cp "$SOURCE_DIR/config.json" "$TARGET_DIR/config.json"
for config in "$SOURCE_DIR"/config*.tcl; do
  if [ -f "$config" ]; then
    cp "$config" "$TARGET_DIR/$(basename "$config")"
  fi
done
cp "$SOURCE_DIR/pin_order.cfg" "$TARGET_DIR/pin_order.cfg"
for source in "$SOURCE_DIR"/src/*.v; do
  if [ -f "$source" ]; then
    cp "$source" "$TARGET_DIR/src/$(basename "$source")"
  fi
done
for constraint in "$SOURCE_DIR"/src/*.sdc; do
  if [ -f "$constraint" ]; then
    cp "$constraint" "$TARGET_DIR/src/$(basename "$constraint")"
  fi
done

echo "Staged $DESIGN_NAME into $TARGET_DIR"
cd "$OPENLANE_ROOT"
docker run --rm \
  -v "$OPENLANE_ROOT:/openlane" \
  -v "$OPENLANE_ROOT/designs:/openlane/install" \
  -v "$HOME:$HOME" \
  -v "${PDK_ROOT:-$HOME/.ciel}:${PDK_ROOT:-$HOME/.ciel}" \
  -e PDK_ROOT="${PDK_ROOT:-$HOME/.ciel}" \
  -e PDK=sky130A \
  --user "$(id -u):$(id -g)" \
  --network host \
  --security-opt seccomp=unconfined \
  ghcr.io/the-openroad-project/openlane:ff5509f65b17bfa4068d5336495ab1718987ff69-amd64 \
  sh -c "./flow.tcl -design $DESIGN_NAME -config_file designs/$DESIGN_NAME/$CONFIG_NAME.tcl -tag $TAG -overwrite"
