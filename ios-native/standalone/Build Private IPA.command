#!/bin/bash
# Double-click on macOS to create a private, asset-inclusive unsigned iPhone IPA.
# This wizard never sends purchased game files to ChatGPT, GitHub, or a server.
set -euo pipefail
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
BASE="$(cd "$(dirname "$0")" && pwd)"
EXIT_STATUS=0
function finish {
  EXIT_STATUS="${1:-$?}"
  echo
  if [ "$EXIT_STATUS" -eq 0 ]; then
    echo "Completed. The IPA can be signed with AltStore or an Apple development certificate."
  else
    echo "Packaging did not finish. See the message above."
  fi
  read -r -p "Press Return to close this window..." _ || true
}
trap finish EXIT

echo "HEROES III COMPLETE — PRIVATE IPHONE PACKAGER"
echo "This is for personally licensed game data; do not redistribute without permission."
echo

if [ "$(uname -s)" != "Darwin" ]; then
  echo "This wizard must run on macOS."
  exit 1
fi

ENGINE="$BASE/engine/vcmi-ios-unsigned.ipa"
SCRIPT="$BASE/packager/pack_standalone.py"
[ -f "$ENGINE" ] || { echo "Missing bundled VCMI engine IPA: $ENGINE"; exit 1; }
[ -f "$SCRIPT" ] || { echo "Missing Python packaging script: $SCRIPT"; exit 1; }
command -v python3 >/dev/null || { echo "Python 3 is required; install Python 3 and retry."; exit 1; }

if ! command -v innoextract >/dev/null; then
  echo "The free 'innoextract' utility is required to unpack your GOG installer."
  if command -v brew >/dev/null; then
    read -r -p "Install it using Homebrew now? [y/N] " answer
    if [[ "$answer" == "y" || "$answer" == "Y" ]]; then
      brew install innoextract
    else
      echo "You can install it later with: brew install innoextract"
      exit 1
    fi
  else
    echo "Install Homebrew and then run: brew install innoextract"
    echo "https://brew.sh"
    exit 1
  fi
fi

echo "Choose the GOG Complete Edition setup EXE."
echo "The matching -1.bin file must be in the SAME folder as the EXE."
GOG_EXE="$(osascript -e 'POSIX path of (choose file with prompt "Choose the GOG Heroes III Complete installer EXE. Keep its matching -1.bin in the same folder.")')" || { echo "File selection cancelled."; exit 1; }
case "$GOG_EXE" in *.exe|*.EXE) : ;; *) echo "Selected file is not an .exe installer: $GOG_EXE"; exit 1;; esac
[ -f "$GOG_EXE" ] || { echo "Selected EXE does not exist."; exit 1; }
GAME_DIR="$(dirname "$GOG_EXE")"
GOG_PREFIX="${GOG_EXE%.*}"
BIN_FILE="${GOG_PREFIX}-1.bin"
[ -f "$BIN_FILE" ] || { echo "Matching installer data file missing: $BIN_FILE"; exit 1; }
python3 - "$GOG_EXE" "$BIN_FILE" <<'PY_CHECK_INSTALLER'
import sys
from pathlib import Path
exe, data = map(Path, sys.argv[1:])
assert exe.read_bytes()[:2] == b"MZ", "Selected EXE is not a Windows installer executable."
assert data.stat().st_size > 100 * 1024 * 1024, "Matching -1.bin is too small to be a Complete Edition installation."
print("Matching GOG files found: %.1f MiB data archive" % (data.stat().st_size / 2**20))
PY_CHECK_INSTALLER

OUTPUT="$(osascript -e 'POSIX path of (choose file name with prompt "Save your PRIVATE unsigned IPA (do not post it online)" default name "HeroesIII-Complete-private-unsigned.ipa")')" || { echo "Save cancelled."; exit 1; }
case "$OUTPUT" in *.ipa) : ;; *) OUTPUT="${OUTPUT}.ipa" ;; esac
[ "$OUTPUT" != "$ENGINE" ] || { echo "Output must not overwrite the engine IPA."; exit 1; }
mkdir -p "$(dirname "$OUTPUT")"
if [ -e "$OUTPUT" ]; then
  echo "An output IPA already exists here. Choose a new name instead to protect the previous build."
  exit 1
fi
python3 - "$BIN_FILE" "$OUTPUT" "$ENGINE" <<'PY_CHECK_SPACE'
import shutil, sys
from pathlib import Path
bin_file, output, engine = map(Path, sys.argv[1:])
source_size = bin_file.stat().st_size
scratch_free = shutil.disk_usage('/private/tmp').free
output_free = shutil.disk_usage(output.parent).free
scratch_min = int(source_size * 2.2)
output_min = int(source_size * 1.1) + engine.stat().st_size + 64*1024*1024
for label, available, needed in [("Temporary extraction disk",scratch_free,scratch_min),("Output disk",output_free,output_min)]:
    print("%s: %.2f GiB free / %.2f GiB estimated needed" % (label, available/2**30, needed/2**30))
    if available < needed:
        raise SystemExit("Insufficient free space. Free space or choose another output disk.")
PY_CHECK_SPACE
TMP="$(mktemp -d -t heroes-iii-personal)"
trap 'exit_code=$?; rm -rf "$TMP"; finish "$exit_code"' EXIT

echo "Extracting your privately owned GOG installation..."
innoextract --gog --extract --output-dir "$TMP" "$GOG_EXE"
echo "Validating and packaging your Heroes III Complete installation..."
python3 "$SCRIPT" --base-ipa "$ENGINE" --game-dir "$TMP" --out "$OUTPUT" --mode personal --rights-confirmed

echo
echo "Private unsigned IPA saved to: $OUTPUT"
echo "A checksum manifest was saved next to it."
echo "Before installing, sign the IPA with your Apple development identity or a trusted sideloading tool."
open -R "$OUTPUT" || true
