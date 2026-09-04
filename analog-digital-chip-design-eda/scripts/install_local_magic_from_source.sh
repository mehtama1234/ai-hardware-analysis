#!/usr/bin/env bash
set -euo pipefail

PREFIX="${MAGIC_PREFIX:-$HOME/eda-tools/magic}"
SRC="${MAGIC_SRC:-$HOME/eda-tools/magic-src}"
REPO="${MAGIC_REPO:-https://github.com/RTimothyEdwards/magic.git}"

echo "Local Magic source build"
echo "prefix: $PREFIX"
echo "source: $SRC"

for tool in git make gcc autoconf automake pkg-config tclsh; do
  command -v "$tool" >/dev/null || {
    echo "missing required build tool: $tool" >&2
    exit 1
  }
done

mkdir -p "$(dirname "$SRC")" "$(dirname "$PREFIX")"

if [ ! -d "$SRC/.git" ]; then
  git clone "$REPO" "$SRC"
else
  git -C "$SRC" fetch --tags --prune
  git -C "$SRC" pull --ff-only
fi

cd "$SRC"
./configure --prefix="$PREFIX"
make -j"$(nproc)"
make install

"$PREFIX/bin/magic" --version
echo "installed: $PREFIX/bin/magic"
