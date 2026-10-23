# Heroes III Mobile (unofficial iOS client)

This repository is developing a **touch-optimized iOS build of [VCMI](https://github.com/vcmi/vcmi)** for legally obtained **Heroes of Might and Magic III: Complete Edition** data (Restoration of Erathia, Armageddon's Blade, Shadow of Death).

**Development status:** The iOS v0.9 engine compiled and packaged successfully with conditional bundled-game auto-launch. Its Apple signing, real GOG assets, and physical-device gameplay are not yet verified.

## Download the unsigned test build

- [Verified native v0.8 build #5](https://github.com/kylesandrews/HOMM3/actions/runs/39830594417/artifacts/12448653647) — download the GitHub artifact ZIP, then extract `vcmi-ios-unsigned.ipa`. This version includes the **reserved, non-overlapping mobile action strip**. Apple signing is required before installation.
- [GitHub Actions build history](https://github.com/kylesandrews/HOMM3/actions/workflows/heroes-mobile-native-ios.yml)
- [Physical device test matrix](https://github.com/kylesandrews/HOMM3/blob/ios-native-port/ios-native/DEVICE_TEST_PLAN.md)
- [Apple Silicon local native build script](https://github.com/kylesandrews/HOMM3/blob/ios-native-port/ios-native/build-ios-local.sh)
- [iPhone installation instructions](https://github.com/kylesandrews/HOMM3/blob/ios-native-port/ios-native/INSTALL_IPHONE.md)
- [Native iOS source customization](https://github.com/kylesandrews/HOMM3/tree/ios-native-port)
- [Upstream iOS build instructions](https://github.com/vcmi/vcmi/blob/develop/docs/developers/Building_iOS.md)

The custom adventure-map toolbar includes **Kingdom, Quest Log, Move Hero, Cast Spell, Next Hero, End Turn**, uses VCMI's original game commands, and targets smaller landscape iPhones as well as larger screens. The iOS map viewport is shortened to reserve a separate control strip, so gameplay tiles are not obscured.

## Verified v0.9 native engine

[Heroes III Mobile v0.9 GitHub build #7](https://github.com/kylesandrews/HOMM3/actions/runs/39875596004) **succeeded** for iPhoneOS ARM64, including native Xcode compilation, IPA packaging and validation. The app detects `Data/H3Bitmap.lod` and `Data/H3Sprite.lod` bundled inside the IPA and auto-launches gameplay by default when no user launch preference exists. Engine-only builds still show the VCMI launcher. **The game-data-inclusive build is not publicly available**, because original Heroes III Complete resources require separate distribution rights.

The repo includes a [one-click Mac build wizard](https://github.com/kylesandrews/HOMM3/blob/ios-native-port/ios-native/standalone/Build%20Private%20IPA.command) for private, locally supplied game data. The self-contained app must be signed before installing.

## Private one-click Mac packaging kit v1.1

The latest Mac toolkit includes the **verified v0.9 ARM64 iOS engine** and a Finder-openable packaging wizard. It validates your matching GOG Complete Edition installer pair and available disk space, extracts those files privately on your Mac, and packages a single **unsigned** IPA. The output is branded "Heroes III Mobile" and is designed to launch the packaged game directly without a second game-file import.

The packager refuses to overwrite previous builds, confirms the customized iPhoneOS ARM64 executable, validates four Complete Edition base-and-expansion archives, and emits a separate audio/video completeness audit. [All 13 packaging regression tests passed](https://github.com/kylesandrews/HOMM3/actions/runs/39909826129).

**Important:** The published toolkit includes NO original GOG game content. An asset-inclusive IPA may only be used or shared as authorized by its game-content rights. It still requires Apple signing, and its full gameplay behavior has not been validated on physical iPhone hardware.

## Private self-contained build (no game-file import required)

The [standalone IPA packager](https://github.com/kylesandrews/HOMM3/blob/ios-native-port/ios-native/standalone/README.md) is on the [ios-native-port branch](https://github.com/kylesandrews/HOMM3/tree/ios-native-port/ios-native/standalone). Download the unsigned engine build, extract your own GOG Complete Edition `.exe` and matching `.bin` locally, then embed the resulting `Data`, `Maps` and optional `Mp3` in one **unsigned** IPA using the offline packager. Sign the completed IPA before installation. No post-install import is necessary because VCMI searches the app bundle root for game files.

[Standalone packaging tests — successful](https://github.com/kylesandrews/HOMM3/actions/runs/39834935050). These tests use simulated files, not original copyrighted Heroes III data.

**Redistribution restriction:** A GOG purchase is a personal-use license and does not grant public redistribution rights for the original Heroes III assets. Keep the game-data-inclusive IPA private unless you have a separate rights-holder license authorizing distribution. The open-source engine-only IPA is appropriate for public distribution subject to VCMI's GPL terms.

## Getting your Complete Edition data into the app

The engine is open-source, but the original game content is not. You must supply your own GOG offline installer `.exe` and matching `.bin`; the iOS VCMI launcher normally offers an import flow. Alternatively transfer `Data`, `Maps`, and optionally `Mp3` to the application's Documents folder using iOS Files/Finder.

Do not commit the game installer or original assets to a public GitHub repository. An unsigned IPA **cannot be installed directly** until it is signed with an Apple development certificate or an appropriate sideloading tool.

## Reproducible build

The main branch workflow checks out the engine at a fixed upstream revision, applies the modified source from the `ios-native-port` branch, resolves the official iOS Conan dependency cache, compiles with Xcode, packages an unsigned IPA, validates its contents, and uploads the artifact.

## Attribution and licensing

VCMI's [GPL v2 license text](VCMI-GPL-2.0-LICENSE.txt) is preserved here. GOG installers, maps, sound packs, and Apple signing credentials are intentionally excluded from build artifacts. Existing tracked proprietary files must be removed separately; adding ignore patterns does not untrack them.


This is an independent, unofficial project. It is not affiliated with Ubisoft, New World Computing, 3DO, or the VCMI project. VCMI is GPL-2.0-or-later; share modifications under the applicable license. Original Heroes III game data remains separately licensed and is not part of the compiled application.