# Heroes III Mobile (unofficial iOS client)

This repository is developing a **touch-optimized iOS build of [VCMI](https://github.com/vcmi/vcmi)** for legally obtained **Heroes of Might and Magic III: Complete Edition** data (Restoration of Erathia, Armageddon's Blade, Shadow of Death).

**Development status:** Native VCMI compiled successfully for iPhoneOS ARM64 on GitHub Actions. An unsigned `.app` and IPA have been produced. **On-device gameplay, Apple signing, and imported GOG assets are not yet verified.**

## Download the unsigned test build

- [GitHub Actions builds](https://github.com/kylesandrews/HOMM3/actions/workflows/heroes-mobile-native-ios.yml) — open the newest **successful** run, download the artifact named `heroes-iii-ios-native-build`, then extract `vcmi-ios-unsigned.ipa` (or use the earlier verified [Build #2 artifact](https://github.com/kylesandrews/HOMM3/actions/runs/39820520554/artifacts/12445650701) containing a `.app` ZIP).
- [iPhone installation instructions](https://github.com/kylesandrews/HOMM3/blob/ios-native-port/ios-native/INSTALL_IPHONE.md)
- [Native iOS source customization](https://github.com/kylesandrews/HOMM3/tree/ios-native-port)
- [Upstream iOS build instructions](https://github.com/vcmi/vcmi/blob/develop/docs/developers/Building_iOS.md)

The custom adventure-map toolbar includes **Kingdom, Quest Log, Move Hero, Cast Spell, Next Hero, End Turn**, uses VCMI's original game commands, and targets smaller landscape iPhones as well as larger screens.

## Getting your Complete Edition data into the app

The engine is open-source, but the original game content is not. You must supply your own GOG offline installer `.exe` and matching `.bin`; the iOS VCMI launcher normally offers an import flow. Alternatively transfer `Data`, `Maps`, and optionally `Mp3` to the application's Documents folder using iOS Files/Finder.

Do not commit the game installer or original assets to a public GitHub repository. An unsigned IPA **cannot be installed directly** until it is signed with an Apple development certificate or an appropriate sideloading tool.

## Reproducible build

The main branch workflow checks out the engine at a fixed upstream revision, applies the modified source from the `ios-native-port` branch, resolves the official iOS Conan dependency cache, compiles with Xcode, packages an unsigned IPA, validates its contents, and uploads the artifact.

## Attribution and licensing

This is an independent, unofficial project. It is not affiliated with Ubisoft, New World Computing, 3DO, or the VCMI project. VCMI is GPL-2.0-or-later; share modifications under the applicable license. Original Heroes III game data remains separately licensed and is not part of the compiled application.