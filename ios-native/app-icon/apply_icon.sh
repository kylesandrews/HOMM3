#!/usr/bin/env bash
# Apply Heroes III logo-inspired artwork to the upstream VCMI Xcode asset catalog.
# The generated AppIcon PNGs are compiled into Assets.car by Apple's actool.
set -euo pipefail
BASE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UPSTREAM="${1:?Pass the checked-out VCMI source directory}"
CATALOG="$UPSTREAM/clientapp/ios/Images.xcassets/AppIcon.appiconset"
SOURCE="$BASE/heroes-iii-icon.svg"

command -v rsvg-convert >/dev/null || { echo "Install librsvg (rsvg-convert) on the macOS build host." >&2; exit 1; }
command -v sips >/dev/null || { echo "Apple sips is required on macOS." >&2; exit 1; }
test -f "$SOURCE"
test -f "$CATALOG/Contents.json"

rsvg-convert --width=1024 --height=1024 --output="$CATALOG/Icon-App-1024.png" "$SOURCE"
python3 - "$CATALOG" <<'PY'
import json, pathlib, subprocess, sys
root = pathlib.Path(sys.argv[1])
config = root / "Contents.json"
data = json.loads(config.read_text())
seen = set()
for item in data["images"]:
    if item.get("idiom") == "ios-marketing":
        size = 1024
        item["filename"] = "Icon-App-1024.png"
    else:
        pts = float(item["size"].split("x")[0])
        scale = int(item["scale"].removesuffix("x"))
        size = round(pts * scale)
    filename = item.get("filename")
    assert filename, item
    if filename != "Icon-App-1024.png" and filename not in seen:
        subprocess.run(["sips", "-z", str(size), str(size),
                        str(root / "Icon-App-1024.png"), "--out", str(root / filename)],
                       check=True, capture_output=True)
    seen.add(filename)
config.write_text(json.dumps(data, indent=2) + "\n")
assert len(seen) >= 15, f"Unexpectedly few icon catalog entries: {seen}"
print(f"Heroes III icon: generated {len(seen)} Apple icon sizes, including 1024px")
PY
