# Heroes III Mobile: physical iOS acceptance test

**Build:** unsigned iPhoneOS ARM64 VCMI client with six-button adventure dock.
**Required:** sign IPA using a trusted tool, install on a physical iPhone or iPad, and import your own GOG Heroes III Complete Edition files. No original game assets are distributed with this project.

## First launch

- [ ] Installed IPA launches without closing or crashing.
- [ ] VCMI launcher appears by default; the game can be started from it.
- [ ] Selecting GOG Complete Edition installer `.exe` followed by matching `-1.bin` finishes importing. Keep both local on device.
- [ ] A single-player scenario can be opened. Record a screenshot of the first adventure map.
- [ ] No missing textures, fonts, music, or sound files are reported.

## Adventure-map touch controls

Use **landscape** orientation.

- [ ] Six custom buttons appear in a separate bar **below** the adventure map rather than covering tiles.
- [ ] All six controls work: Kingdom, Quest Log, Move Hero, Cast Spell, Next Hero, End Turn.
- [ ] Selecting the last column of playable map tiles is possible without triggering a toolbar button.
- [ ] The toolbar icons do not overlap each other or extend into the minimap/side panel.
- [ ] Dragging pans the map; pinch zoom works; long press opens the correct contextual interaction.
- [ ] Existing hero/town list, resource bar, and minimap remain usable.
- [ ] Opening and closing a hero view or town view returns to the map cleanly.
- [ ] The toolbar does not block the World View / full-map overview.

## Original Complete Edition features

- [ ] New scenario launches with real Heroes III factions, heroes, creatures, and artifacts.
- [ ] Restoration of Erathia campaigns/maps are available.
- [ ] Armageddon's Blade campaigns/maps are available.
- [ ] Shadow of Death campaigns/maps are available.
- [ ] Hero can move on the map, claim a mine, collect resources, and engage combat.
- [ ] Tactical battle completes with expected result and returns to the adventure map.
- [ ] Save and load work across an app restart; autosaves are available as expected.
- [ ] Music and sound effects play and respect settings.
- [ ] Game resumes after switching to another app and back.

## Compatibility

Test at least one modern iPhone in landscape. Optionally test an older compact iPhone layout and an iPad. VCMI's logical render resolution and interface scaling can differ from physical screen points, so the source geometry checks are **not** a substitute for device screenshots.

## Report a problem

Provide **device model**, **iOS version**, **install/signing method**, **build run URL**, **app stage** (launcher/import/map/combat), and exact steps to reproduce.

If available, attach the `VCMI_Client_log.txt` file from the VCMI logs directory (remove any personal information first), plus screenshots. Do **not** upload purchased GOG binaries, Apple signing certificates, passwords or provisioning profiles.

## Release criterion

The game is a playable iOS port only once a signed app has launched with imported Complete Edition assets, finished an actual scenario/battle, and passed save/restart tests on physical hardware. Compilation alone does not meet this criterion.
