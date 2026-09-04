#!/usr/bin/env bash
set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
  echo "Run this script with sudo:"
  echo "  sudo ./scripts/install_ubuntu_eda_tools.sh"
  exit 1
fi

apt-get update
apt-get install -y \
  build-essential \
  git \
  python3 \
  python3-pip \
  python3-venv \
  ngspice \
  yosys \
  iverilog \
  verilator \
  gtkwave \
  magic \
  klayout \
  graphviz

cat <<'MSG'

Installed common Ubuntu EDA packages.

Notes:
- xschem, openroad, and openlane may require separate install paths depending on the desired version.
- OpenLane is usually easiest through a containerized flow.
- Run ./scripts/check_tools.sh again to see what remains missing.
MSG

