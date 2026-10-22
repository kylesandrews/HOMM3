#!/usr/bin/env python3
"""Build a self-contained, *unsigned* VCMI iOS IPA from locally licensed assets.

No GOG game data is downloaded, committed to GitHub, or sent to a server.
Distribution of game data requires separate rights-holder authorization.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import zipfile

APP = "Payload/vcmiclient.app/"
GAME_DIRS = ("Data", "Maps", "Mp3")
REQUIRED_DATA = ("h3bitmap.lod", "h3sprite.lod")

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
    if len(output) < 3 or not any(f.lower().endswith((".h3m", ".h3c")) for _, f in output):
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
    total_bytes = sum(p.stat().st_size for p, _ in assets)
    with zipfile.ZipFile(base_ipa) as source:
        if source.testzip() is not None:
            raise PackagingError("Engine IPA failed ZIP integrity validation.")
        originals = set(source.namelist())
        if APP + "Info.plist" not in originals or APP + "vcmiclient" not in originals:
            raise PackagingError("Not a valid VCMI iPhone IPA.")
        if any("/_CodeSignature/" in n for n in originals):
            raise PackagingError("The input app is already signed. Add game files to an unsigned IPA, then sign the complete result.")
        if any(n.startswith(APP + directory + "/") for n in originals for directory in GAME_DIRS):
            raise PackagingError("Base IPA already contains game folders; prevent accidental asset mixing/overwrites.")
        if any(dest in originals for _, dest in assets):
            raise PackagingError("Duplicate resource paths in app bundle.")
        if dry_run:
            return {"mode":mode,"game_root":str(game_root),"assets":len(assets),"source_bytes":total_bytes,"output":str(result_ipa),"dry_run":True}
        result_ipa.parent.mkdir(parents=True, exist_ok=True)
        fd, name = tempfile.mkstemp(prefix="._vcmi_private_", suffix=".ipa", dir=result_ipa.parent)
        os.close(fd)
        tmp = Path(name)
        try:
            with zipfile.ZipFile(tmp, "w", allowZip64=True) as target:
                for info in source.infolist():
                    with source.open(info) as reader, target.open(info, "w", force_zip64=True) as writer:
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
            os.replace(tmp, result_ipa)
        finally:
            if tmp.exists():
                tmp.unlink()
    with result_ipa.open("rb") as completed:
        digest = hashlib.file_digest(completed, "sha256").hexdigest()
    manifest = {"mode": mode, "kind":"self-contained unsigned VCMI iOS IPA", "asset_count":len(assets),"asset_source_bytes":total_bytes,"ipa_bytes":result_ipa.stat().st_size, "ipa_sha256":digest,"asset_paths":[x for x in GAME_DIRS if any(dest.startswith(APP+x+"/") for _,dest in assets)],"game_files_publicly_redistributable": False,"signed":False,"requires_data_import_after_install":False,"requires_apple_signing":True}
    result_ipa.with_suffix(".manifest.json").write_text(json.dumps(manifest, indent=2)+"\n",encoding="utf-8")
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
