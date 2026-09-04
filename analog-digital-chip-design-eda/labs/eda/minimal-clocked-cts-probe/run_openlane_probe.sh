#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"

export AIMC_OPENLANE_PREP="${AIMC_OPENLANE_PREP:-minimal-clocked-cts-probe}"
export AIMC_OPENLANE_DESIGN="${AIMC_OPENLANE_DESIGN:-toy_cts_probe}"
export AIMC_OPENLANE_RTL="${AIMC_OPENLANE_RTL:-toy_cts_probe.v}"
export CONFIG_NAME="${CONFIG_NAME:-config}"
export TAG="${TAG:-toy_cts_probe_cts}"

"$ROOT/scripts/run_aimc_openlane_flow.sh"
