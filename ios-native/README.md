# Heroes III Mobile — native VCMI iOS build

This branch implements an independent, touch-adapted VCMI iOS client for **Heroes of Might and Magic III: Complete Edition**. No original game files are distributed.

## Native implementation

- Engine source pinned to [VCMI bae8baf](https://github.com/vcmi/vcmi/commit/bae8bafd2ec3bbf7ec2cacea5c6868ed3b019405).
- Landscape action bar with six real VCMI commands: Kingdom, Quest Log, Move Hero, Cast Spell, Next Hero and End Turn.
- iOS-only hit targets of at least 44 logical pixels; keeps original native controls on desktop.
- **Dedicated 63-pixel control strip:** adventure-map viewport is shortened by the same amount on supported landscape screens so gameplay tiles are not hidden underneath buttons.
- Responsive dock positioning is checked for six compact-to-tablet landscape viewports.
- Bundled game files are detected automatically on iOS: when original Data/H3Bitmap.lod and Data/H3Sprite.lod are included and no explicit launch mode is selected, gameplay starts directly instead of showing the installer.
- Original VCMI engine implements maps, combat, AI, save files and campaigns. The separate SwiftUI prototype does not supply real gameplay.

## Builds and testing

[Native macOS build workflow](https://github.com/kylesandrews/HOMM3/actions/workflows/heroes-mobile-native-ios.yml) runs from the repository main branch, checks out this source branch, restores official VCMI iOS dependencies, compiles for iPhoneOS ARM64, packages an unsigned IPA and tests the bundled launcher, resources and button layout.

[Native build #7 (v0.9)](https://github.com/kylesandrews/HOMM3/actions/runs/39875596004) compiled and packaged successfully with the reserved control strip and bundled-data auto-launch code. Actual device gameplay, original GOG game data and Apple signing have not yet been validated.

For actual use:
- [iPhone installation / game data import](INSTALL_IPHONE.md)
- [Physical-device acceptance tests](DEVICE_TEST_PLAN.md)
- Apple's development signing or a trusted sideloading tool is required to install an unsigned IPA.
- Import your legally obtained Complete Edition GOG offline installer `.exe` and matching `.bin` through the VCMI launcher. Alternatively copy extracted `Data`, `Maps`, and optionally `Mp3` to the app's Documents folder.

**Release definition:** An unsigned successful compiler build is not evidence of complete gameplay. The port remains in testing until launching, combat, saving/loading and Complete Edition content have been checked on an actual iPhone or iPad.

## Licensing and attribution

VCMI is available under GPL-2.0-or-later, with the [upstream license text](https://github.com/kylesandrews/HOMM3/blob/main/VCMI-GPL-2.0-LICENSE.txt) preserved in this repository. Original Heroes III game files are copyright-protected and must remain user-supplied. This is an independent, unofficial project.
