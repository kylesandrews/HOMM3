# Heroes III Mobile — Home Screen icon

The iPhone/iPad icon is styled after the original **Heroes of Might and Magic III** title treatment: large Roman numeral III, metallic HEROES lettering, gold trim, and deep navy background. It is an independently drawn interpretation rather than an extracted game asset.

Source: `heroes-iii-icon.svg`. The native GitHub Actions build invokes `apply_icon.sh`, which renders the source artwork using `rsvg-convert` and generates every Apple `AppIcon.appiconset` size with `sips`. Xcode subsequently compiles the images into `vcmiclient.app/Assets.car`. The app bundle retains its existing bundle identifier so that users can update their personally signed copies rather than install a second separate app.

The companion private IPA updater can carry existing game content forward into the new icon-equipped engine without extracting GOG installers again. Apple signing is required afterward. Visual appearance and iOS icon caching still require device verification.

This artwork is intended for private fan use; a rights-holder license is needed where required for commercial/public distribution of branded game assets.
