#!/usr/bin/env python3
"""Customize presentation of the VCMI-derived iOS client without erasing credits.

Changes only public-facing launch UI and home-screen title. The app bundle
retains upstream copyright, the full GPL license, and an accessible notice.
"""
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

TITLE = "Heroes III Mobile"
RESOURCE_NAME = "THIRD_PARTY_NOTICES.txt"

def patch(root: Path, notices_path: Path):
    storyboard = root / "clientapp/ios/LaunchScreen.storyboard"
    plist_path = root / "clientapp/ios/Info.plist"
    cmake_path = root / "clientapp/CMakeLists.txt"
    license_path = root / "license.txt"
    assert license_path.is_file(), "Preserve VCMI's original license.txt"
    assert notices_path.is_file(), "Third-party notice text is required"

    xml = storyboard.read_text()
    ET.fromstring(xml)
    # Apple's launch storyboard must contain no engine logo or placeholder.
    image_view = '''                        <subviews>
                            <imageView clipsSubviews="YES" userInteractionEnabled="NO" contentMode="scaleAspectFit" horizontalHuggingPriority="251" verticalHuggingPriority="251" image="vcmi_logo.png" translatesAutoresizingMaskIntoConstraints="NO" id="xBx-rS-h4V">
                                <rect key="frame" x="87.5" y="233.5" width="200" height="200"/>
                            </imageView>
                        </subviews>
'''
    constraints = '''                        <constraints>
                            <constraint firstItem="xBx-rS-h4V" firstAttribute="centerY" secondItem="Jnx-JV-IwA" secondAttribute="centerY" id="OgR-oG-SHt"/>
                            <constraint firstItem="xBx-rS-h4V" firstAttribute="centerX" secondItem="Jnx-JV-IwA" secondAttribute="centerX" id="eTp-at-qVT"/>
                        </constraints>
'''
    resources = '''    <resources>
        <image name="vcmi_logo.png" width="200" height="200"/>
    </resources>
'''
    if 'vcmi_logo.png' in xml:
        assert all(x in xml for x in (image_view, constraints, resources)), "Unexpected iOS launch storyboard markup"
        xml = xml.replace(image_view, "").replace(constraints, "").replace(resources, "")
    assert "vcmi_logo.png" not in xml
    ET.fromstring(xml)
    storyboard.write_text(xml)

    plist = plist_path.read_text()
    marker = "<key>CFBundleName</key>\n\t<string>$(APP_DISPLAY_NAME)</string>"
    replacement = f"<key>CFBundleName</key>\n\t<string>{TITLE}</string>\n\t<key>CFBundleDisplayName</key>\n\t<string>{TITLE}</string>"
    if marker in plist:
        plist = plist.replace(marker, replacement)
    assert replacement in plist, "Unknown Info.plist title template"
    ET.fromstring(plist)
    plist_path.write_text(plist)

    cmake = cmake_path.read_text()
    before = "foreach(XCODE_RESOURCE LaunchScreen.storyboard Images.xcassets Settings.bundle vcmi_logo.png)"
    after = "foreach(XCODE_RESOURCE LaunchScreen.storyboard Images.xcassets Settings.bundle THIRD_PARTY_NOTICES.txt)"
    if before in cmake:
        cmake = cmake.replace(before, after)
    assert after in cmake, "Unknown iOS resource registration"
    hook = '\tset(CMAKE_EXE_LINKER_FLAGS "-Wl,-e,_client_main")\nendif()'
    prefix = '''\t# The app is based on the VCMI engine. Preserve upstream copyright and license.
\ttarget_sources(vcmiclient PRIVATE "${CMAKE_SOURCE_DIR}/license.txt")
\tset_source_files_properties("${CMAKE_SOURCE_DIR}/license.txt" PROPERTIES MACOSX_PACKAGE_LOCATION Resources)

'''
    if prefix not in cmake:
        assert cmake.count(hook) == 1, "Unknown iOS linker flag anchor"
        cmake = cmake.replace(hook, prefix + hook)
    cmake_path.write_text(cmake)

    dst = root / "clientapp/ios" / RESOURCE_NAME
    dst.write_text(notices_path.read_text())
    assert "VCMI" in dst.read_text() and "GNU General Public License" in dst.read_text()
    print("iOS presentation customized: dark splash, Heroes III Mobile title, legal notices retained.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: apply_branding.py path/to/VCMI/source")
    patch(Path(sys.argv[1]), Path(__file__).with_name(RESOURCE_NAME))
