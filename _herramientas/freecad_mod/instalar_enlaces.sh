#!/usr/bin/env bash
# Crea los enlaces simbólicos desde el directorio de usuario de FreeCAD hacia este repositorio.
# Uso: bash _herramientas/freecad_mod/instalar_enlaces.sh [DIR_USUARIO_FREECAD]
# Por defecto: ~/snap/freecad/common (FreeCAD instalado como snap).
set -euo pipefail
AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST="${1:-$HOME/snap/freecad/common}"
mkdir -p "$DEST/Mod"
for d in "$AQUI"/Mod/*/; do
  n="$(basename "$d")"; ln -sfn "${d%/}" "$DEST/Mod/$n"; echo "Mod/$n -> ${d%/}"
done
for m in "$AQUI"/macros/*.FCMacro; do
  ln -sfn "$m" "$DEST/$(basename "$m")"; echo "$(basename "$m") -> $m"
done
