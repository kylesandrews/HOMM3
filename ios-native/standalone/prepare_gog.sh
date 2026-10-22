#!/usr/bin/env bash
# Extract a personally obtained GOG offline installer without uploading it.
# Its matching .bin file must be beside the .exe on the local computer.
set -euo pipefail
if [[ $# -ne 2 ]]; then
  echo "Usage: bash prepare_gog.sh /private/setup_heroes_iii_complete.exe /private/extracted-folder" >&2
  exit 2
fi
command -v innoextract >/dev/null || { echo "Install innoextract first (macOS: brew install innoextract)" >&2; exit 1; }
exe="$1"; target="$2"
[[ -f "$exe" && "$exe" == *.exe ]] || { echo "Provide the local GOG setup .exe, with matching .bin in the same directory" >&2; exit 1; }
mkdir -p "$target"
innoextract --gog --extract --output-dir "$target" "$exe"
printf 'Extracted to: %s\n' "$target"
printf 'Now use --game-dir "%s" with pack_standalone.py.\n' "$target"
