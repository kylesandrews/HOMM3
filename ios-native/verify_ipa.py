#!/usr/bin/env python3
"""Validate a native, unsigned iPhoneOS app package made by the VCMI workflow."""
import io
import json
import plistlib
import struct
import sys
import zipfile
from pathlib import Path

def check(ipa_path: Path):
    with zipfile.ZipFile(ipa_path) as z:
        bad = z.testzip()
        if bad:
            raise ValueError(f"Bad IPA entry: {bad}")
        names = z.namelist()
        app = "Payload/vcmiclient.app/"
        if app + "Info.plist" not in names:
            raise ValueError("Missing iOS Info.plist")
        if app + "vcmiclient" not in names:
            raise ValueError("Missing iOS executable")
        info = plistlib.loads(z.read(app + "Info.plist"))
        if info.get("CFBundleSupportedPlatforms") != ["iPhoneOS"]:
            raise ValueError("Not an iPhoneOS build")
        if info.get("CFBundlePackageType") != "APPL":
            raise ValueError("Bundle not an application")
        if info.get("CFBundleExecutable") != "vcmiclient":
            raise ValueError("Wrong executable name")
        with z.open(app + "vcmiclient") as executable:
            header = executable.read(16)
        magic, arch, _, kind = struct.unpack("<IIII", header)
        if (magic, arch, kind) != (0xfeedfacf, 0x0100000c, 2):
            raise ValueError("Executable is not arm64 Mach-O")
        if any("/_CodeSignature/" in name for name in names):
            raise ValueError("Unexpected signing resources in unsigned IPA")
        if any(name.lower().endswith((".exe", ".bin")) for name in names):
            raise ValueError("Found GOG installer files in distributable IPA")
        if not info.get("UIFileSharingEnabled"):
            raise ValueError("Game data transfer requires UIFileSharingEnabled")
        return {"archive": str(ipa_path), "bundle_id": info.get("CFBundleIdentifier"),
                "platform": "iPhoneOS", "architecture": "arm64",
                "minimum_ios": info.get("MinimumOSVersion"),
                "entries": len(names), "signed": False, "original_game_assets": False}

if __name__ == "__main__":
    result = check(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("vcmi-ios-unsigned.ipa"))
    print(json.dumps(result, indent=2))
