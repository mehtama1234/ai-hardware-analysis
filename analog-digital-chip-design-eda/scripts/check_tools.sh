#!/usr/bin/env bash
set -u

tools=(
  ngspice
  xschem
  magic
  klayout
  yosys
  iverilog
  verilator
  gtkwave
  python3
  pip
)

missing=0
optional_missing=0
sim_python="${AIMC_SIM_PYTHON:-$HOME/eda-tools/aimc-simulators-venv/bin/python}"
if [ ! -x "$sim_python" ]; then
  sim_python="python3"
fi
printf 'Chip/EDA tool check\n'
printf '===================\n'
for tool in "${tools[@]}"; do
  if command -v "$tool" >/dev/null 2>&1; then
    printf 'OK      %s -> %s\n' "$tool" "$(command -v "$tool")"
  else
    printf 'MISSING %s\n' "$tool"
    missing=$((missing + 1))
  fi
done

printf '\nContainer-backed flow checks\n'
printf '============================\n'
if command -v docker >/dev/null 2>&1; then
  printf 'OK      docker -> %s\n' "$(command -v docker)"
else
  printf 'MISSING docker\n'
  missing=$((missing + 1))
fi

if command -v openroad >/dev/null 2>&1; then
  printf 'OK      openroad host -> %s\n' "$(command -v openroad)"
elif command -v docker >/dev/null 2>&1 && docker images --format '{{.Repository}}:{{.Tag}}' | grep -q '^ghcr.io/the-openroad-project/openlane:'; then
  printf 'OK      openroad container -> OpenLane Docker image contains openroad\n'
else
  printf 'MISSING openroad host/container\n'
  missing=$((missing + 1))
fi

if command -v openlane >/dev/null 2>&1; then
  printf 'OK      openlane host -> %s\n' "$(command -v openlane)"
elif [ -f "$HOME/eda-tools/OpenLane/flow.tcl" ] && command -v docker >/dev/null 2>&1 && docker images --format '{{.Repository}}:{{.Tag}}' | grep -q '^ghcr.io/the-openroad-project/openlane:'; then
  printf 'OK      openlane source+container -> %s\n' "$HOME/eda-tools/OpenLane/flow.tcl"
else
  printf 'MISSING openlane host/source+container\n'
  missing=$((missing + 1))
fi

printf '\nOptional simulator adapter checks\n'
printf '=================================\n'
printf 'Simulator Python: %s\n' "$sim_python"
if "$sim_python" -c "import importlib.util; raise SystemExit(0 if importlib.util.find_spec('aihwkit') else 1)" >/dev/null 2>&1; then
  printf 'OK      aihwkit python module -> importable\n'
else
  printf 'OPTIONAL-MISSING aihwkit python module\n'
  optional_missing=$((optional_missing + 1))
fi

if "$sim_python" -c "import importlib.util; raise SystemExit(0 if importlib.util.find_spec('simulator') or importlib.util.find_spec('cross_sim') else 1)" >/dev/null 2>&1; then
  printf 'OK      crosssim python module -> importable\n'
else
  printf 'OPTIONAL-MISSING crosssim python module\n'
  optional_missing=$((optional_missing + 1))
fi

printf '\nMissing tools: %s\n' "$missing"
printf 'Optional missing simulator adapters: %s\n' "$optional_missing"
if [ "$missing" -gt 0 ]; then
  printf 'Run sudo ./scripts/install_ubuntu_eda_tools.sh for common Ubuntu packages.\n'
  printf 'Run ./scripts/install_extended_eda_tools.sh for xschem/OpenLane/OpenROAD paths.\n'
fi
