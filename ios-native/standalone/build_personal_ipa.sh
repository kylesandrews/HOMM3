#!/usr/bin/env bash
# Build a private asset-inclusive unsigned iPhone IPA from the user's GOG installer.
set -euo pipefail
if [[ $# -ne 3 ]]; then
  echo 'Usage: bash build_personal_ipa.sh "/path/GOG/setup_heroes_iii_complete.exe" "/path/engine-only.ipa" "/private/HeroesIII-personal-unsigned.ipa"' >&2
  exit 2
fi
ROOT="$(cd "$(dirname "$0")" && pwd)"
GOG_EXE="$1"; ENGINE_IPA="$2"; OUTPUT_IPA="$3"
for tool in innoextract python3; do
  command -v "$tool" >/dev/null || { echo "Missing: $tool (macOS: brew install innoextract)" >&2; exit 1; }
done
[[ -f "$GOG_EXE" && -f "$ENGINE_IPA" ]] || { echo 'GOG installer exe and engine IPA must both exist.' >&2; exit 1; }
TEMP_EXTRACT="$(mktemp -d)"
trap 'rm -rf "$TEMP_EXTRACT"' EXIT
innoextract --gog --extract --output-dir "$TEMP_EXTRACT" "$GOG_EXE"
python3 "$ROOT/pack_standalone.py" --base-ipa "$ENGINE_IPA" --game-dir "$TEMP_EXTRACT" --out "$OUTPUT_IPA" --mode personal --rights-confirmed
printf '\nCreated personal, unsigned standalone IPA: %s\nSign it with Apple provisioning/AltStore before installation. Do not redistribute the proprietary game files.\n' "$OUTPUT_IPA"
