#!/usr/bin/env bash
set -euo pipefail

INSTALL_ROOT="${INSTALL_ROOT:-$HOME/eda-tools}"
JOBS="${JOBS:-$(nproc)}"

usage() {
  cat <<'MSG'
Install the heavier chip/EDA tools that are not covered by the basic apt script.

Usage:
  ./scripts/install_extended_eda_tools.sh --xschem
  ./scripts/install_extended_eda_tools.sh --openlane
  ./scripts/install_extended_eda_tools.sh --openroad-flow
  ./scripts/install_extended_eda_tools.sh --all

Options:
  --xschem         Build and install xschem from source.
  --openlane      Clone OpenLane and pull its Docker image.
  --openroad-flow Clone OpenROAD-flow-scripts and run its dependency/build flow.
  --docker-apt    Install Docker packages from Ubuntu apt if docker is missing.
  --all           Run xschem, openlane, and openroad-flow.
  --help          Show this help.

Environment:
  INSTALL_ROOT    Default: $HOME/eda-tools
  JOBS            Build parallelism. Default: nproc

Notes:
  - OpenLane uses Docker. You may need to log out and back in if you later add
    your user to the docker group.
  - OpenROAD/OpenLane can consume many GB because of containers, builds, PDKs,
    and generated runs.
MSG
}

want_xschem=0
want_openlane=0
want_openroad_flow=0
want_docker_apt=0

if [ "$#" -eq 0 ]; then
  usage
  exit 1
fi

for arg in "$@"; do
  case "$arg" in
    --xschem)
      want_xschem=1
      ;;
    --openlane)
      want_openlane=1
      ;;
    --openroad-flow)
      want_openroad_flow=1
      ;;
    --docker-apt)
      want_docker_apt=1
      ;;
    --all)
      want_xschem=1
      want_openlane=1
      want_openroad_flow=1
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $arg" >&2
      usage
      exit 1
      ;;
  esac
done

sudo_apt_install() {
  sudo apt-get update
  sudo apt-get install -y "$@"
}

ensure_git() {
  if ! command -v git >/dev/null 2>&1; then
    sudo_apt_install git
  fi
}

ensure_docker() {
  if command -v docker >/dev/null 2>&1; then
    return
  fi
  if [ "$want_docker_apt" -eq 1 ]; then
    sudo_apt_install docker.io
    return
  fi
  cat <<'MSG' >&2
Docker is required for OpenLane but is not installed.

Either install Docker yourself, or rerun with:
  ./scripts/install_extended_eda_tools.sh --openlane --docker-apt

After installing Docker, check access with:
  docker run hello-world
MSG
  exit 1
}

install_xschem() {
  ensure_git
  sudo_apt_install \
    build-essential \
    bison \
    flex \
    libcairo2-dev \
    libx11-dev \
    libxpm-dev \
    libxrender-dev \
    tcl-dev \
    tk-dev

  mkdir -p "$INSTALL_ROOT"
  if [ ! -d "$INSTALL_ROOT/xschem-src/.git" ]; then
    git clone https://github.com/StefanSchippers/xschem.git "$INSTALL_ROOT/xschem-src"
  else
    git -C "$INSTALL_ROOT/xschem-src" pull --ff-only
  fi

  (
    cd "$INSTALL_ROOT/xschem-src"
    ./configure
    make -j"$JOBS"
    sudo make install
  )
}

install_openlane() {
  ensure_git
  ensure_docker
  sudo_apt_install make python3 python3-pip python3-venv

  mkdir -p "$INSTALL_ROOT"
  if [ ! -d "$INSTALL_ROOT/OpenLane/.git" ]; then
    git clone https://github.com/The-OpenROAD-Project/OpenLane.git "$INSTALL_ROOT/OpenLane"
  else
    git -C "$INSTALL_ROOT/OpenLane" pull --ff-only
  fi

  (
    cd "$INSTALL_ROOT/OpenLane"
    if [ -f Makefile ]; then
      make pull-openlane || make pull-openlane-image || true
    fi
  )

  cat <<MSG

OpenLane source is at:
  $INSTALL_ROOT/OpenLane

If the image pull target was not available for this version, follow the
OpenLane README from that folder. Docker must work before OpenLane can run.
MSG
}

install_openroad_flow() {
  ensure_git
  sudo_apt_install build-essential cmake git libgmock-dev python3 python3-pip

  mkdir -p "$INSTALL_ROOT"
  if [ ! -d "$INSTALL_ROOT/OpenROAD-flow-scripts/.git" ]; then
    git clone --recursive https://github.com/The-OpenROAD-Project/OpenROAD-flow-scripts "$INSTALL_ROOT/OpenROAD-flow-scripts"
  else
    git -C "$INSTALL_ROOT/OpenROAD-flow-scripts" pull --ff-only
    git -C "$INSTALL_ROOT/OpenROAD-flow-scripts" submodule update --init --recursive
  fi

  (
    cd "$INSTALL_ROOT/OpenROAD-flow-scripts"
    sudo ./setup.sh
    ./build_openroad.sh --local
  )
}

mkdir -p "$INSTALL_ROOT"

if [ "$want_xschem" -eq 1 ]; then
  install_xschem
fi

if [ "$want_openlane" -eq 1 ]; then
  install_openlane
fi

if [ "$want_openroad_flow" -eq 1 ]; then
  install_openroad_flow
fi

echo
echo "Done. Run:"
echo "  ./scripts/check_tools.sh"
