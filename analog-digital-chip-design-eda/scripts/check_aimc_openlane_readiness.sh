#!/usr/bin/env bash
set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PREP_NAME="${AIMC_OPENLANE_PREP:-aimc-control-plane-openlane-prep}"
DESIGN_NAME="${AIMC_OPENLANE_DESIGN:-aimc_control_plane}"
TOP_NAME="${AIMC_OPENLANE_TOP:-$DESIGN_NAME}"
RTL_FILE="${AIMC_OPENLANE_RTL:-$DESIGN_NAME.v}"
DESIGN_DIR="$ROOT/labs/eda/$PREP_NAME"
OPENLANE_ROOT="${OPENLANE_ROOT:-$HOME/eda-tools/OpenLane}"
missing=0

say_ok() {
  printf 'OK      %s\n' "$1"
}

say_missing() {
  printf 'MISSING %s\n' "$1"
  missing=$((missing + 1))
}

say_warn() {
  printf 'WARN    %s\n' "$1"
}

has_cmd() {
  command -v "$1" >/dev/null 2>&1
}

printf 'AIMC OpenLane readiness\n'
printf '=======================\n'
printf 'prep,%s\n' "$PREP_NAME"
printf 'design,%s\n' "$DESIGN_NAME"
printf 'top,%s\n' "$TOP_NAME"

for rel in \
  "config.json" \
  "config.tcl" \
  "constraint.sdc" \
  "pin_order.cfg" \
  "src/$RTL_FILE" \
  "src/constraint.sdc"; do
  if [ -s "$DESIGN_DIR/$rel" ]; then
    say_ok "design file $rel"
  else
    say_missing "design file $rel"
  fi
done

if has_cmd python3; then
  if python3 -m json.tool "$DESIGN_DIR/config.json" >/dev/null 2>&1; then
    say_ok "config.json parses"
  else
    say_missing "config.json parses"
  fi
else
  say_missing "python3"
fi

if has_cmd yosys; then
  say_ok "yosys -> $(command -v yosys)"
  yosys_sources=""
  for source in "$DESIGN_DIR"/src/*.v; do
    if [ -s "$source" ]; then
      say_ok "design file src/$(basename "$source")"
      yosys_sources="$yosys_sources $source"
    fi
  done
  if yosys -q -p "read_verilog $yosys_sources; hierarchy -check -top $TOP_NAME; proc; opt; stat" >/dev/null 2>&1; then
    say_ok "packaged RTL lowers in Yosys"
  else
    say_missing "packaged RTL lowers in Yosys"
  fi
else
  say_missing "yosys"
fi

if has_cmd openlane; then
  say_ok "openlane host command -> $(command -v openlane)"
else
  say_warn "openlane host command not on PATH"
fi

if has_cmd openroad; then
  say_ok "openroad host command -> $(command -v openroad)"
else
  say_warn "openroad host command not on PATH"
fi

openlane_arch=""
if [ -f "$OPENLANE_ROOT/docker/current_platform.py" ] && has_cmd python3; then
  openlane_arch="$(python3 "$OPENLANE_ROOT/docker/current_platform.py" 2>/dev/null || true)"
fi

if [ -f "$OPENLANE_ROOT/flow.tcl" ] || [ -f "$OPENLANE_ROOT/Makefile" ]; then
  say_ok "OpenLane source -> $OPENLANE_ROOT"
else
  say_missing "OpenLane source at $OPENLANE_ROOT"
fi

if has_cmd docker; then
  say_ok "docker command -> $(command -v docker)"
  if timeout 30 docker info >/dev/null 2>&1; then
    say_ok "docker daemon responds"
    if [ -n "$openlane_arch" ]; then
      image_pattern="(^efabless/openlane:.*-$openlane_arch$|^ghcr.io/the-openroad-project/openlane:.*-$openlane_arch$)"
    else
      image_pattern='(^efabless/openlane:|^ghcr.io/the-openroad-project/openlane:)'
    fi
    image_count="$(timeout 60 docker images --format '{{.Repository}}:{{.Tag}}' 2>/dev/null | grep -Ec "$image_pattern")"
    if [ "$image_count" -gt 0 ]; then
      say_ok "OpenLane Docker image present"
    else
      say_missing "OpenLane Docker image present"
    fi
  else
    say_missing "docker daemon responds"
  fi
else
  say_missing "docker command"
fi

printf '\nResult\n'
printf '======\n'
if [ "$missing" -eq 0 ]; then
  printf 'READY for an OpenLane run attempt against:\n'
  printf '  %s/config.json\n' "$DESIGN_DIR"
else
  printf 'NOT READY for a full OpenLane run. Missing checks: %s\n' "$missing"
  printf 'The design package can still be reviewed and Yosys-checked locally.\n'
fi

exit 0
