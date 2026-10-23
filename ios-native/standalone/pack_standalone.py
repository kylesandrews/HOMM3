#!/usr/bin/env python3
"""Build a self-contained, *unsigned* VCMI iOS IPA from locally licensed assets.

No GOG game data is downloaded, committed to GitHub, or sent to a server.
Distribution of game data requires separate rights-holder authorization.
"""
import argparse
import hashlib
import json
import os
import plistlib
import struct
from pathlib import Path
import shutil
import sys
import tempfile
import zipfile

APP = "Payload/vcmiclient.app/"
GAME_DIRS = ("Data", "Maps", "Mp3")
REQUIRED_DATA = ("h3bitmap.lod", "h3sprite.lod", "h3ab_bmp.lod", "h3ab_spr.lod")
DISPLAY_NAME = "Heroes III Mobile"

class PackagingError(Exception):
    pass


def resolve_game_root(root: Path) -> Path:
    root = root.expanduser().resolve(strict=True)
    if not root.is_dir():
        raise PackagingError("Game input must be an extracted game directory.")
    queue = [(root, 0)]
    while queue:
        base, depth = queue.pop(0)
        folders = {p.name.casefold(): p for p in base.iterdir() if p.is_dir() and not p.is_symlink()}
        data, maps = folders.get("data"), folders.get("maps")
        if data and maps:
            files = {p.name.casefold() for p in data.iterdir() if p.is_file()}
            if all(x in files for x in REQUIRED_DATA):
                return base
        if depth < 4:
            for child in base.iterdir():
                if child.is_dir() and not child.is_symlink() and not child.name.startswith("."):
                    queue.append((child, depth + 1))
    raise PackagingError("Can't find extracted Heroes III Complete folders with Data/H3Bitmap.lod, Data/H3Sprite.lod, and Maps. Extract the GOG installer first.")


def collect_assets(root: Path):
    found = {p.name.casefold(): p for p in root.iterdir() if p.is_dir() and not p.is_symlink()}
    output = []
    for name in GAME_DIRS:
        folder = found.get(name.casefold())
        if folder is None:
            if name == "Mp3":
                continue
            raise PackagingError(f"Missing required game folder: {name}")
        for parent, dirnames, filenames in os.walk(folder, followlinks=False):
            dirnames[:] = sorted(d for d in dirnames if not (Path(parent) / d).is_symlink())
            for file in sorted(filenames):
                p = Path(parent) / file
                if p.is_symlink():
                    raise PackagingError(f"Asset symbolic links are not permitted: {p}")
                if not p.is_file() or p.name in (".DS_Store", "Thumbs.db"):
                    continue
                if p.suffix.lower() in (".exe", ".bin", ".p12", ".mobileprovision", ".pem"):
                    raise PackagingError(f"Refusing executable, installer, or credential inside game data: {p}")
                rel = Path(name) / p.relative_to(folder)
                if any(part in ("..", "") for part in rel.parts):
                    raise PackagingError(f"Unsafe path: {rel}")
                output.append((p, APP + rel.as_posix()))
    available_data = {p.name.casefold() for p in found["data"].iterdir() if p.is_file()}
    missing = sorted(set(REQUIRED_DATA) - available_data)
    if missing:
        raise PackagingError("Incomplete Heroes III Complete Edition data: missing " + ", ".join(missing) + ". Ensure the original GOG installer and matching -1.bin were both extracted.")
    if len(output) < 5 or not any(f.lower().endswith((".h3m", ".h3c")) for _, f in output):
        raise PackagingError("No Heroes III scenario or campaign files found under Maps.")
    if len({dest.casefold() for _, dest in output}) != len(output):
        raise PackagingError("Case-insensitive filename collision in original data.")
    return output


def package(base_ipa: Path, extracted_dir: Path, result_ipa: Path, mode: str, *, dry_run=False):
    game_root = resolve_game_root(extracted_dir)
    assets = collect_assets(game_root)
    if base_ipa.resolve() == result_ipa.resolve():
        raise PackagingError("Input and output IPA must be different paths.")
    if not base_ipa.exists():
        raise PackagingError("Engine-only base IPA is missing.")
    if result_ipa.exists():
        raise PackagingError("Output IPA already exists. Choose a new filename to protect your previous build.")
    total_bytes = sum(p.stat().st_size for p, _ in assets)
    normalized = [dest.casefold() for _, dest in assets]
    audit = {
        "edition_archives_present": list(REQUIRED_DATA),
        "maps_and_campaign_files": sum(x.endswith((".h3m", ".h3c")) for x in normalized),
        "music_mp3_files": sum(x.startswith((APP + "Mp3/").casefold()) and x.endswith(".mp3") for x in normalized),
        "sound_archives": sum(x.startswith((APP + "Data/").casefold()) and x.endswith(".snd") for x in normalized),
        "video_archives": sum(x.startswith((APP + "Data/").casefold()) and x.endswith(".vid") for x in normalized),
    }
    with zipfile.ZipFile(base_ipa) as source:
        if source.testzip() is not None:
            raise PackagingError("Engine IPA failed ZIP integrity validation.")
        originals = set(source.namelist())
        if APP + "Info.plist" not in originals or APP + "vcmiclient" not in originals:
            raise PackagingError("Not a valid VCMI iPhone IPA.")
        info = plistlib.loads(source.read(APP + "Info.plist"))
        if info.get("CFBundleSupportedPlatforms") != ["iPhoneOS"] or info.get("CFBundleExecutable") != "vcmiclient":
            raise PackagingError("Base IPA is not the expected iPhoneOS VCMI client.")
        with source.open(APP + "vcmiclient") as binary:
            header = binary.read(16)
        if len(header) != 16 or struct.unpack("<IIII", header)[:2] != (0xfeedfacf, 0x0100000c):
            raise PackagingError("Base IPA does not contain an ARM64 iOS executable.")
        if APP + "config/widgets/adventureMap.json" not in originals:
            raise PackagingError("This IPA is missing the VCMI adventure-map configuration.")
        if "iosQuickActions" not in source.read(APP + "config/widgets/adventureMap.json").decode("utf-8"):
            raise PackagingError("Base IPA is not a Heroes III Mobile customized engine build.")
        info["CFBundleDisplayName"] = DISPLAY_NAME
        original_plist = source.read(APP + "Info.plist")
        plist_fmt = plistlib.FMT_BINARY if original_plist.startswith(b"bplist") else plistlib.FMT_XML
        branded_plist = plistlib.dumps(info, fmt=plist_fmt, sort_keys=False)
        if any("/_CodeSignature/" in n for n in originals):
            raise PackagingError("The input app is already signed. Add game files to an unsigned IPA, then sign the complete result.")
        if any(n.startswith(APP + directory + "/") for n in originals for directory in GAME_DIRS):
            raise PackagingError("Base IPA already contains game folders; prevent accidental asset mixing/overwrites.")
        if any(dest in originals for _, dest in assets):
            raise PackagingError("Duplicate resource paths in app bundle.")
        if dry_run:
            return {"mode":mode,"game_root":str(game_root),"assets":len(assets),"source_bytes":total_bytes,"display_name":DISPLAY_NAME,"output":str(result_ipa),"dry_run":True,"audit":audit}
        result_ipa.parent.mkdir(parents=True, exist_ok=True)
        # Check available space before writing potentially >1 GB of data.
        free = shutil.disk_usage(result_ipa.parent).free
        conservative = total_bytes + base_ipa.stat().st_size + 64 * 1024 * 1024
        if free < conservative:
            raise PackagingError(f"Not enough free disk space: need approximately {conservative / 2**30:.2f} GiB on the output volume (available {free / 2**30:.2f} GiB).")
        fd, name = tempfile.mkstemp(prefix="._vcmi_private_", suffix=".ipa", dir=result_ipa.parent)
        os.close(fd)
        tmp = Path(name)
        try:
            with zipfile.ZipFile(tmp, "w", allowZip64=True) as target:
                for item in source.infolist():
                    if item.filename == APP + "Info.plist":
                        target.writestr(item, branded_plist)
                    else:
                        with source.open(item) as reader, target.open(item, "w", force_zip64=True) as writer:
                            shutil.copyfileobj(reader, writer, length=1024 * 1024)
                for disk, dest in assets:
                    arcinfo = zipfile.ZipInfo(dest)
                    arcinfo.compress_type = zipfile.ZIP_DEFLATED
                    arcinfo.external_attr = 0o100644 << 16
                    with disk.open("rb") as reader, target.open(arcinfo, "w", force_zip64=True) as writer:
                        shutil.copyfileobj(reader, writer, length=1024 * 1024)
            with zipfile.ZipFile(tmp) as check:
                first_bad = check.testzip()
                if first_bad is not None:
                    raise PackagingError(f"Corrupted output IPA member: {first_bad}")
                names = set(check.namelist())
                if not all(dest in names for _, dest in assets):
                    raise PackagingError("Not all game assets were embedded.")
                result_info = plistlib.loads(check.read(APP + "Info.plist"))
                if result_info.get("CFBundleDisplayName") != DISPLAY_NAME:
                    raise PackagingError("The branded iPhone app display name is missing.")
                if not all(APP + "Data/" + f in names or
                           any(n.casefold() == (APP + "Data/" + f).casefold() for n in names)
                           for f in REQUIRED_DATA):
                    raise PackagingError("Required GOG data archives missing from finished IPA.")
            os.replace(tmp, result_ipa)
        finally:
            if tmp.exists():
                tmp.unlink()
    digest_hash = hashlib.sha256()
    with result_ipa.open("rb") as completed:
        while True:
            chunk = completed.read(1024 * 1024)
            if not chunk:
                break
            digest_hash.update(chunk)
    digest = digest_hash.hexdigest()
    manifest = {"mode": mode, "kind":"self-contained unsigned VCMI iOS IPA", "asset_count":len(assets),"asset_source_bytes":total_bytes,"ipa_bytes":result_ipa.stat().st_size, "ipa_sha256":digest,"asset_paths":[x for x in GAME_DIRS if any(dest.startswith(APP+x+"/") for _,dest in assets)],"game_files_publicly_redistributable": False,"signed":False,"requires_data_import_after_install":False,"requires_apple_signing":True,"display_name":DISPLAY_NAME,"audit":audit}
    result_ipa.with_suffix(".manifest.json").write_text(json.dumps(manifest, indent=2)+"\n",encoding="utf-8")
    audit_lines = [
        "Heroes III Mobile — Private Complete Edition Packaging Audit",
        "The original game assets remain privately owned. This report does not grant redistribution rights.",
        f"SHA256: {digest}",
        f"Total embedded files: {len(assets)}",
        f"Extracted source bytes: {total_bytes}",
        f"Map and campaign files: {audit['maps_and_campaign_files']}",
        f"Music MP3 files: {audit['music_mp3_files']}",
        f"Sound archives: {audit['sound_archives']}",
        f"Video archives: {audit['video_archives']}",
        "Required Complete Edition graphics archives: " + ", ".join(REQUIRED_DATA),
        "WARNING: Audio/music may be missing." if not audit["sound_archives"] or not audit["music_mp3_files"] else "Sound and music files detected.",
        "WARNING: Cutscene video may be missing." if not audit["video_archives"] else "Video archive detected.",
        "UNSIGNED: Sign this IPA before iPhone installation.",
        "UNTESTED: Physical-device gameplay and complete campaign support still require verification.",
    ]
    result_ipa.with_suffix(".audit.txt").write_text("\n".join(audit_lines)+"\n", encoding="utf-8")
    return manifest


def main():
    parser = argparse.ArgumentParser(description="Offline personal or rights-authorized packaging of Heroes III game data into an unsigned native VCMI IPA")
    parser.add_argument("--base-ipa", required=True, type=Path, help="unsigned engine-only VCMI IPA")
    parser.add_argument("--game-dir", required=True, type=Path, help="extracted Heroes III Complete installation (Data and Maps folders)")
    parser.add_argument("--out", required=True, type=Path, help="self-contained unsigned IPA destination; keep private unless licensed to redistribute")
    parser.add_argument("--mode", required=True, choices=("personal", "licensed-distribution"), help="personal use or separately authorized distribution")
    parser.add_argument("--rights-confirmed", action="store_true", help="confirm you have the legal rights for the selected use; this does not grant any rights")
    parser.add_argument("--dry-run",action="store_true",help="validate the game folders without writing an IPA")
    args = parser.parse_args()
    if not args.rights_confirmed:
        parser.error("You must acknowledge that you have the necessary rights for your selected use. Personal GOG purchase alone does not permit redistribution.")
    try:
        result = package(args.base_ipa, args.game_dir, args.out, args.mode, dry_run=args.dry_run)
        print(json.dumps(result, indent=2))
    except (OSError, zipfile.BadZipFile, PackagingError) as err:
        print(f"Packaging stopped: {err}",file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
