# Self-contained Heroes III Complete IPA: offline packager

This builds **one unsigned iPhone IPA including all licensed game files** from the VCMI engine-only build and a locally extracted Heroes III Complete installation. There is no post-install game data import. VCMI already searches the installed app bundle for resources in `VCMIDirsIOS::dataPaths()`, including the bundle root.

**Rights notice:** Buying the game through GOG allows personal use, not public redistribution of proprietary game files. Keep the asset-inclusive output private unless you've separately obtained permission to redistribute the original Heroes III Complete assets. The engine-only IPA and modified engine source remain separate under VCMI's GPL-2.0-or-later. Signing credentials must also remain private. The flags in these scripts do not convey any intellectual property rights.

## Build from your own GOG installer

1. Download your GOG Complete Edition offline `.exe` and matching `-1.bin` locally into the same folder. The separate update patch is not required.
2. On macOS, install `innoextract` (for example `brew install innoextract`). Certain installer generations also need `unar`.
3. Run the extraction script, substituting your actual filenames:

```bash
bash ios-native/standalone/prepare_gog.sh "/private/GOG/setup_homm3_complete.exe" "/private/Heroes3-extracted"
```

4. Download the **unsigned engine-only** `vcmi-ios-unsigned.ipa` from the latest successful GitHub Actions run at https://github.com/kylesandrews/HOMM3/actions/workflows/heroes-mobile-native-ios.yml

5. Build the private self-contained app:

```bash
python3 ios-native/standalone/pack_standalone.py \
  --base-ipa "/private/vcmi-ios-unsigned.ipa" \
  --game-dir "/private/Heroes3-extracted" \
  --out "/private/HeroesIII-Complete-personal-unsigned.ipa" \
  --mode personal --rights-confirmed
```

The script locates the `Data`, `Maps` and optional `Mp3` directories, validates the four Complete Edition graphics archives (`H3Bitmap.lod`, `H3Sprite.lod`, `H3ab_bmp.lod`, `H3ab_spr.lod`) and maps, streams the files directly into `Payload/vcmiclient.app`, preserves all original engine resources, runs ZIP integrity checks, and writes an SHA-256 manifest plus a readable `.audit.txt` report. It refuses already-signed builds, collisions, installers, and private signing credentials. It does not upload anything.

**Sign after bundling.** IPA modification invalidates existing Apple signatures. Use your Apple Development team/authorized sideloading process to sign the final IPA; distributing a signed app to other people additionally requires appropriate Apple distribution provisioning/TestFlight/App Store eligibility. An unsigned IPA cannot be installed by tapping it.

This tool provides a private self-contained test build; actual gameplay and save/load still need physical device verification. For a publicly shareable edition, obtain redistribution rights for every bundled Heroes III asset or replace them all with assets licensed for distribution. The GOG data alone does not confer those rights.

Run Python tests from the standalone folder: `python3 -m unittest -v test_packaging.py`.

## One-command personal build

Download the unsigned engine-only IPA, keep your matching GOG `.exe` and `-1.bin` together locally, then run:

```bash
bash ios-native/standalone/build_personal_ipa.sh \
  '/private/GOG/setup_heroes_of_might_and_magic_3_complete_4.0_(3.2)_gog_0.1_(77075).exe' \
  '/private/vcmi-ios-unsigned.ipa' \
  '/private/HeroesIII-personal-unsigned.ipa'
```

This extracts the GOG game files into a temporary private folder, embeds them in the IPA, and removes the temporary extraction after packaging. It never uploads the original assets. The result must still be signed for iPhone installation and cannot be publicly redistributed without relevant rights-holder permission.

## v0.9: direct launch for self-contained builds

The iOS source override `ios-native/overrides/clientapp/ios/main.m` now checks the application bundle's `Data` directory for the original `H3Bitmap.lod` and `H3Sprite.lod` archives, case-insensitively. When both exist and the user hasn't explicitly selected a launch mode, the app launches gameplay directly; when they're absent, the normal VCMI import launcher appears. The explicit app setting and `VCMI_LAUNCH_TYPE` environment override take precedence. This still requires compiling the v0.9 engine: adding files to an earlier v0.8 IPA alone will not enable auto-launch.

If you downloaded the complete Mac kit, double-click `Build Private Heroes III IPA.command`. Its engine IPA is already included, and it will prompt for your GOG `.exe`, verify the matching `-1.bin`, and create the private standalone IPA. The tool requires Python 3 and `innoextract` (installed with Homebrew if available and you approve it).

The current implementation has build and mock-data tests; a real game-data install and physical iPhone gameplay test are still required.

## v1.1 asset-completeness audit

The builder now **rejects an incomplete Complete Edition installation** if either the base graphics archives or Armageddon's Blade graphics archives are missing. It records counts of maps/campaign files, music MP3s, sound archives and video archives in the `.manifest.json` and `.audit.txt` files alongside your private IPA. Missing optional soundtrack or video assets produce warnings rather than hiding the omissions; if you want all Complete Edition media, verify and re-extract the GOG installer pair before signing.

The v1.1 test suite includes 13 offline regression tests, including missing-expansion detection, archive integrity, app name, and no-overwrite behavior. Running them does not test real game playback. The original Complete Edition archives must remain private unless the rights holder authorizes redistribution.
