# Heroes III Mobile — native VCMI port

This branch contains an **iOS adaptation of VCMI**, targeting **Heroes of Might and Magic III Complete** (Restoration of Erathia, Armageddon's Blade and Shadow of Death). This is not a complete game distribution and no copyrighted game data is included.

## Native implementation

- Pinned upstream engine revision: `bae8bafd2ec3bbf7ec2cacea5c6868ed3b019405`.
- A new landscape adventure-map quick-action dock: Kingdom, Quest, Move, Cast, Next Hero and End Turn.
- On iOS, mobile quick buttons use larger 44+ logical pixel touch targets.
- Existing VCMI commands are used; turn logic, maps, combat and AI remain upstream.
- `.github/workflows/heroes-ios.yml` attempts an **unsigned iOS build** on macOS when this branch changes.

## Build and testing

The source files in `ios-native/overrides/` replace corresponding upstream files in a checkout of the pinned engine. GitHub Actions applies the overrides and compiles `vcmiclient` with the official Conan + CMake iOS build preset. See the workflow log for the result.

After compilation succeeds, code signing requires an Apple Developer Team, and playing requires the original GOG Complete Edition offline installer pair, imported through VCMI's own installer interface. No GOG installers, music, maps or other game assets should be committed to this public repository.

**Status:** Native iOS source changes are implemented. A successful macOS compilation, installation and real gameplay test are still required before declaring a playable custom port. The existing SwiftUI prototype is a separate demonstration and should not be represented as VCMI gameplay.

## Legal

VCMI is GPL-2.0-or-later. Distribution of any modified engine binaries must comply with that license; the proprietary original game files remain separately user-provided.

Build reference: https://github.com/vcmi/vcmi/blob/develop/docs/developers/Building_iOS.md

Installer reference: https://github.com/vcmi/vcmi/blob/develop/docs/players/Installation_iOS.md
