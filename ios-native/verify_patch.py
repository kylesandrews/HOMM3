#!/usr/bin/env python3
"""Check the custom iOS adventure-map layout against native VCMI geometry."""
import json
import re
import sys
import subprocess
from pathlib import Path

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("vcmi-src")
cpp = (root / "client/adventureMap/AdventureMapWidget.cpp").read_text()
layout = (root / "config/widgets/adventureMap.json").read_text()
ios_main = (root / "clientapp/ios/main.m").read_text()
assert "h3MobileHasBundledGameData()" in ios_main
assert '[NSUserDefaults.standardUserDefaults objectForKey:@"LaunchType"]' in ios_main
assert 'caseInsensitiveCompare:@"H3Bitmap.lod"' in ios_main
assert 'caseInsensitiveCompare:@"H3Sprite.lod"' in ios_main
assert "launchType = savedMode != nil" in ios_main
assert "#ifndef VCMI_IOS" in cpp
assert 'input["exists"]["iosOnly"].Bool()' in cpp
assert 'input["mobileTouchTarget"].Bool()' in cpp
assert "area.h = std::max(1, area.h - 63);" in cpp
data = json.loads(re.sub(r"//[^\n]*", "", layout))
dock = next(x for x in data["items"] if x.get("name") == "iosQuickActions")
assert dock["exists"] == {"iosOnly": True, "widthMin": 560, "heightMin": 300}
assert dock["hideWhen"] == "worldViewMode"
area = dock["area"]
assert area == {"left": 7, "right": 199, "bottom": 47, "height": 63}
background = next(x for x in dock["items"] if x["name"] == "iosQuickActionsBackground")
assert background["area"] == {"left": 0, "right": 0, "top": 0, "bottom": 0}
buttons = [x for x in dock["items"] if x["type"] == "adventureMapButton"]
expected = ("adventureKingdomOverview", "adventureQuestLog",
            "adventureMoveHero", "adventureCastSpell", "adventureNextHero",
            "adventureEndTurn")
assert tuple(x["hotkey"] for x in buttons) == expected
for button in buttons:
    assert button["mobileTouchTarget"] is True
    assert button["area"]["width"] >= 44 and button["area"]["height"] >= 44

# Each layout measurement uses the same rules as AdventureMapWidget::readArea.
for screen_w, screen_h in [(568, 320), (667, 375), (812, 375),
                           (852, 393), (1024, 768), (1194, 834)]:
    assert screen_w > dock["exists"]["widthMin"]
    assert screen_h > dock["exists"]["heightMin"]
    dock_w = screen_w - area["left"] - area["right"]
    dock_x = area["left"]
    dock_y = screen_h - area["bottom"] - area["height"]
    assert dock_w >= 362
    assert dock_y >= 7
    # The map ends at this strip's top after the iOS-only height adjustment.
    map_bottom = screen_h - 47 - 63
    assert map_bottom == dock_y
    edges = []
    for button in buttons:
        b = button["area"]
        x = dock_x + dock_w - b["right"] - b["width"]
        y = dock_y + b["top"]
        assert x >= dock_x
        assert x + b["width"] <= dock_x + dock_w
        assert y >= dock_y
        assert y + b["height"] <= dock_y + area["height"]
        edges.append((x, x + b["width"]))
    assert all(edges[i][1] <= edges[i + 1][0] for i in range(len(edges)-1))
# A portable preflight for the optional Apple Silicon local build script.
script = Path(__file__).with_name("build-ios-local.sh")
if script.exists():
    subprocess.run(["bash", "-n", str(script)], check=True)
print("iOS non-overlapping action dock and map viewport: passed")
