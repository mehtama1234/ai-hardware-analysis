#!/usr/bin/env bash
set -euo pipefail

echo "AIMC converter Sky130 workbench environment"
echo "workbench: $(pwd)"
test -f .magicrc
test -f xschemrc.local
test -f sky130-ngspice.includes
test -f "/home/mehtama1/eda-tools/pdks/sky130A/libs.tech/magic/sky130A.tech"
test -f "/home/mehtama1/eda-tools/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice"
test -f "/home/mehtama1/eda-tools/pdks/sky130A/libs.tech/ngspice/corners/tt.spice"
command -v magic >/dev/null
command -v xschem >/dev/null
command -v ngspice >/dev/null
echo "ready_for_manual_layout_start=true"
echo "not_post_layout_evidence=true"
