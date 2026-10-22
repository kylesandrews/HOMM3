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

The script locates the `Data`, `Maps` and optional `Mp3` directories, validates required LOD data and maps, streams the files directly into `Payload/vcmiclient.app`, preserves all original engine resources, runs ZIP integrity checks, and writes an SHA-256 manifest. It refuses already-signed builds, collisions, installers, and private signing credentials. It does not upload anything.

**Sign after bundling.** IPA modification invalidates existing Apple signatures. Use your Apple Development team/authorized sideloading process to sign the final IPA; distributing a signed app to other people additionally requires appropriate Apple distribution provisioning/TestFlight/App Store eligibility. An unsigned IPA cannot be installed by tapping it.

This tool provides a private self-contained test build; actual gameplay and save/load still need physical device verification. For a publicly shareable edition, obtain redistribution rights for every bundled Heroes III asset or replace them all with assets licensed for distribution. The GOG data alone does not confer those rights.

Run Python tests from the standalone folder: `python3 -m unittest -v test_packaging.py`.
