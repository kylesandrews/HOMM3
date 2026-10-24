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
        required_resources = [
            "config/widgets/adventureMap.json",
            "Mods/vcmi/mod.json",
            "LaunchScreen.storyboardc/Info.plist",
            "Assets.car",
            "THIRD_PARTY_NOTICES.txt",
            "license.txt",
        ]
        for relative in required_resources:
            if app + relative not in names:
                raise ValueError(f"Missing required runtime resource: {relative}")
        # Keep required third-party acknowledgments, but not an unsolicited
        # VCMI-branded startup logo.
        if app + "vcmi_logo.png" in names:
            raise ValueError("Obsolete startup logo is still bundled")
        notices = z.read(app + "THIRD_PARTY_NOTICES.txt").decode("utf-8")
        license_text = z.read(app + "license.txt").decode("utf-8")
        if "VCMI" not in notices or "GNU General Public License" not in notices:
            raise ValueError("Open-source acknowledgments are missing")
        if "GNU GENERAL PUBLIC LICENSE" not in license_text:
            raise ValueError("GPL license text is missing from app")
        if info.get("CFBundleDisplayName") != "Heroes III Mobile":
            raise ValueError("Unexpected visible iOS app name")
        # iPhone and iPad Home Screen icons are compiled from our AppIcon set.
        icons = info.get("CFBundleIcons", {}).get("CFBundlePrimaryIcon", {})
        if icons.get("CFBundleIconName") != "AppIcon":
            raise ValueError("Missing compiled iOS AppIcon metadata")
        # Confirm the actual IPA contains our *modified* adventure-map layout,
        # not just an executable compiled from modified source.
        layout_text = z.read(app + "config/widgets/adventureMap.json").decode("utf-8")
        if '"name": "iosQuickActions"' not in layout_text and '"name" : "iosQuickActions"' not in layout_text:
            raise ValueError("Custom iOS action dock was not bundled in the app")
        for action in ("iosQuickKingdom", "iosQuickQuest", "iosQuickMove",
                       "iosQuickCast", "iosQuickNextHero", "iosQuickEndTurn"):
            if action not in layout_text:
                raise ValueError(f"Missing custom iOS action: {action}")
        # The app should retain the upstream launcher for GOG data import.
        # This is a linked-symbol / static-string check, not a runtime UI test.
        with z.open(app + "vcmiclient") as executable:
            executable_bytes = executable.read()
        if b"VCMI_LAUNCH_TYPE" not in executable_bytes or b"qt_main_wrapper" not in executable_bytes:
            raise ValueError("Native launcher entry point appears to be missing")
        return {"archive": str(ipa_path), "bundle_id": info.get("CFBundleIdentifier"),
                "platform": "iPhoneOS", "architecture": "arm64",
                "minimum_ios": info.get("MinimumOSVersion"),
                "entries": len(names), "signed": False, "original_game_assets": False}

if __name__ == "__main__":
    result = check(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("vcmi-ios-unsigned.ipa"))
    print(json.dumps(result, indent=2))
