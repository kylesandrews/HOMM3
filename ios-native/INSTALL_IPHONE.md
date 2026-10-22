# Installing Heroes III Mobile (native unsigned test build)

This is a custom build of the **VCMI** engine for **Heroes of Might and Magic III: Complete Edition**. It is not a commercially licensed Heroes III release. The current UI customization adds six landscape adventure-map controls and larger touch targets.

## Building from source on an Apple Silicon Mac

From a clone of this repository checked out on the `ios-native-port` branch, run `bash ios-native/build-ios-local.sh`. The script checks tools, applies our custom VCMI changes, compiles an unsigned iPhoneOS application, packages `out/vcmi-ios-unsigned.ipa`, and verifies the package. It does not import GOG game files.

This particular local script uses prebuilt dependencies with Apple Silicon-hosted Qt tools. For Intel Macs, use the [GitHub Actions build](https://github.com/kylesandrews/HOMM3/actions/workflows/heroes-mobile-native-ios.yml) or follow VCMI's Intel-specific host-tool instructions.

## What you need

- An iPhone/iPad running a supported iOS version (the compiled test bundle has an iOS 12 minimum).
- The unsigned `vcmi-ios-unsigned.ipa` from GitHub Actions.
- A local signing/sideloading utility such as **AltStore Classic** or **Sideloadly**, or Xcode with your Apple Development signing identity.
- Your legally obtained GOG offline installer pair (`.exe` and matching `-1.bin`). Keep the two files together.

**Signing is required:** An unsigned IPA cannot simply be tapped to install in iOS Files. If using a free Apple ID, its development provisioning may expire periodically. Never submit Apple credentials in a public GitHub issue or repository.

## Install

1. Obtain the artifact named **heroes-iii-ios-native-build** from the successful workflow run. Unzip the outer Actions artifact. Find `vcmi-ios-unsigned.ipa` inside.
2. In AltStore Classic (or another signing tool), select this IPA and allow the tool to sign/install the application. Use only an app-signing method you trust.
3. Launch the app. If the VCMI launcher presents **Install game data**, first choose the GOG `.exe`, then the matching `.bin`.
4. If the app launches directly instead of presenting a launcher, extract your legally obtained game installation on a computer and copy its `Data`, `Maps`, and optionally `Mp3` folders to the VCMI app's **Documents** folder using Finder / iTunes file sharing or the iOS Files app.
5. Start or restart the game and check that the original Heroes III maps load. On the landscape adventure map, check Kingdom, Quest, Move, Cast, Next Hero, End Turn.

**Important:** Transferring extracted assets through the Google Drive iOS app can rename `.snd` files to `.au`. Check and correct those extensions if transferring by that method. Prefer copying the original GOG installer pair unchanged.

This package has no GOG game assets bundled and no code signature. It is a **development test build**, not yet validated for launch, audio, saves, networking, or performance on physical hardware.

## References
- VCMI official iOS installation instructions: https://github.com/vcmi/vcmi/blob/develop/docs/players/Installation_iOS.md
- VCMI official iOS build instructions: https://github.com/vcmi/vcmi/blob/develop/docs/developers/Building_iOS.md

## Licensing
VCMI is GPL-2.0-or-later. Proprietary Heroes III assets must be obtained separately. The game and the VCMI engine have distinct licensing terms.
