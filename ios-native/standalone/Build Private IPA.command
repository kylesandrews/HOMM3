#!/bin/bash
# Double-click on macOS to create a private, asset-inclusive unsigned iPhone IPA.
# This wizard never sends purchased game files to ChatGPT, GitHub, or a server.
set -euo pipefail
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
[ -f "${GOG_PREFIX}-1.bin" ] || { echo "Matching installer data file missing: ${GOG_PREFIX}-1.bin"; exit 1; }

OUTPUT="$(osascript -e 'POSIX path of (choose file name with prompt "Save your PRIVATE unsigned IPA (do not post it online)" default name "HeroesIII-Complete-private-unsigned.ipa")')" || { echo "Save cancelled."; exit 1; }
case "$OUTPUT" in *.ipa) : ;; *) OUTPUT="${OUTPUT}.ipa" ;; esac
[ "$OUTPUT" != "$ENGINE" ] || { echo "Output must not overwrite the engine IPA."; exit 1; }
mkdir -p "$(dirname "$OUTPUT")"
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
