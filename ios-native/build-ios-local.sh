#!/usr/bin/env bash
# Build the open-source Heroes III Mobile VCMI client on macOS.
# Requires Xcode, CMake 3.21+, Conan 2.x, git, and Internet access.
# Does not use or redistribute Heroes III Complete copyrighted game assets.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VCMI_REV="bae8bafd2ec3bbf7ec2cacea5c6868ed3b019405"
VCMI_DIR="${VCMI_DIR:-$ROOT/../vcmi-native-upstream}"
OUT_DIR="$ROOT/out"
CACHE_URL="https://github.com/vcmi/vcmi-dependencies/releases/download/2026-10-13/dependencies-ios.txz"

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "ERROR: This script requires macOS / Xcode." >&2
  exit 1
fi
if [[ "$(uname -m)" != "arm64" ]]; then
  echo "ERROR: The official prebuilt iOS Conan cache contains Apple Silicon host tools." >&2
  echo "Use the macOS GitHub Actions workflow, or follow the VCMI Intel-Mac Qt host-tool instructions." >&2
  exit 1
fi
for cmd in xcodebuild git cmake conan curl ditto python3; do
  command -v "$cmd" >/dev/null || { echo "Missing prerequisite: $cmd" >&2; exit 1; }
done
mkdir -p "$OUT_DIR"

if [[ ! -d "$VCMI_DIR/.git" ]]; then
  git clone --recurse-submodules https://github.com/vcmi/vcmi.git "$VCMI_DIR"
fi
git -C "$VCMI_DIR" fetch origin "$VCMI_REV" --depth=1
git -C "$VCMI_DIR" checkout --detach "$VCMI_REV"
git -C "$VCMI_DIR" submodule update --init --recursive
cp "$ROOT/ios-native/overrides/client/adventureMap/AdventureMapWidget.cpp" "$VCMI_DIR/client/adventureMap/AdventureMapWidget.cpp"
cp "$ROOT/ios-native/overrides/config/widgets/adventureMap.json" "$VCMI_DIR/config/widgets/adventureMap.json"
python3 "$ROOT/ios-native/verify_patch.py" "$VCMI_DIR"
git -C "$VCMI_DIR" diff --check

# Prebuilt iOS Conan packages avoid unreliable system zlib resolution.
if [[ ! -f "$OUT_DIR/dependencies-ios.txz" ]]; then
  curl --fail --location --retry 3 "$CACHE_URL" --output "$OUT_DIR/dependencies-ios.txz"
fi
conan cache restore "$OUT_DIR/dependencies-ios.txz"
conan profile detect --force
(
  cd "$VCMI_DIR"
  conan install . --output-folder=conan-generated --build=never --profile=dependencies/conan_profiles/ios-arm64 --profile=dependencies/conan_profiles/base/apple-system -s '&:build_type=Debug'
  cmake --preset ios-device-conan -B out/build/ios-device-conan -D BUNDLE_IDENTIFIER_PREFIX=com.heroes3.mobilelocal -D CMAKE_XCODE_ATTRIBUTE_CODE_SIGNING_ALLOWED=NO
  cmake --build out/build/ios-device-conan --target vcmiclient --config Debug -- -quiet CODE_SIGNING_ALLOWED=NO
)
APP="$VCMI_DIR/out/build/ios-device-conan/bin/Debug/vcmiclient.app"
test -f "$APP/vcmiclient"
test -f "$APP/Info.plist"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT
mkdir -p "$STAGE/Payload"
ditto "$APP" "$STAGE/Payload/vcmiclient.app"
(cd "$STAGE" && ditto -c -k --sequesterRsrc --keepParent Payload "$OUT_DIR/vcmi-ios-unsigned.ipa")
python3 "$ROOT/ios-native/verify_ipa.py" "$OUT_DIR/vcmi-ios-unsigned.ipa"
shasum -a 256 "$OUT_DIR/vcmi-ios-unsigned.ipa" > "$OUT_DIR/vcmi-ios-unsigned.sha256"
echo "Unsigned IPA is ready at: $OUT_DIR/vcmi-ios-unsigned.ipa"
echo "It requires signing before iPhone installation and original GOG game data after launch."
