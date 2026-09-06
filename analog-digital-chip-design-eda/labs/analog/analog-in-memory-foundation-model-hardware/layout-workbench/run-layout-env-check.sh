#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "AIMC converter Sky130 workbench environment"
echo "workbench: ${ROOT}"

required_files=(
  "${ROOT}/.magicrc"
  "${ROOT}/xschemrc.local"
  "${ROOT}/sky130-ngspice.includes"
  "/home/mehtama1/eda-tools/pdks/sky130A/libs.tech/magic/sky130A.tech"
  "/home/mehtama1/eda-tools/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice"
  "/home/mehtama1/eda-tools/pdks/sky130A/libs.tech/ngspice/corners/tt.spice"
)
missing=0
for file in "${required_files[@]}"; do
  if [[ ! -f "${file}" ]]; then
    echo "missing_file=${file}"
    missing=$((missing + 1))
  fi
done

declare -A tool_overrides=(
  [magic]="${MAGIC_BIN:-}"
  [xschem]="${XSCHEM_BIN:-}"
  [ngspice]="${NGSPICE_BIN:-}"
  [netgen]="${NETGEN_BIN:-}"
)
required_tools=(magic xschem ngspice netgen)
for tool in "${required_tools[@]}"; do
  candidate="${tool_overrides[${tool}]}"
  if [[ -n "${candidate}" ]]; then
    if [[ -x "${candidate}" ]]; then
      resolved="${candidate}"
    else
      echo "missing_tool_path=${tool}:${candidate}"
      missing=$((missing + 1))
      continue
    fi
  else
    if resolved="$(type -P "${tool}" 2>/dev/null)"; then
      :
    else
      resolved=""
    fi
    if [[ -z "${resolved}" ]]; then
      echo "missing_tool=${tool}"
      missing=$((missing + 1))
      continue
    fi
  fi
  if [[ "${tool}" == "magic" ]]; then
    magic_path="${resolved}"
  fi
  echo "tool_${tool}=${resolved}"
done

if [[ -n "${magic_path:-}" ]]; then
  if magic_version="$("${magic_path}" --version 2>/dev/null)"; then
    :
  else
    magic_version="unknown"
  fi
  echo "magic_version=${magic_version:-unknown}"
  if [[ -z "${magic_version}" ]] || [[ "$(printf '%s\n' "8.3.411" "${magic_version}" | sort -V | head -n 1)" != "8.3.411" ]]; then
    echo "incompatible_tool=magic_requires_at_least_8.3.411"
    missing=$((missing + 1))
  fi
fi

if (( missing > 0 )); then
  echo "ready_for_manual_layout_start=false"
  echo "missing_requirements=${missing}"
  exit 1
fi
echo "ready_for_manual_layout_start=true"
echo "not_post_layout_evidence=true"
