#!/usr/bin/env python3
"""Preflight source and layout checks for the Heroes III iOS client."""
import json
import re
import sys
from pathlib import Path

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("vcmi-src")
cpp = (root / "client/adventureMap/AdventureMapWidget.cpp").read_text()
layout = (root / "config/widgets/adventureMap.json").read_text()
assert "#ifndef VCMI_IOS" in cpp
assert 'input["exists"]["iosOnly"].Bool()' in cpp
assert 'input["mobileTouchTarget"].Bool()' in cpp
# VCMI widget JSON permits comments.
clean = re.sub(r"//[^\n]*", "", layout)
data = json.loads(clean)
dock = next(x for x in data["items"] if x.get("name") == "iosQuickActions")
assert dock["exists"]["iosOnly"] is True
assert dock["hideWhen"] == "worldViewMode"
buttons = [x for x in dock["items"] if x["type"] == "adventureMapButton"]
expected = ("adventureKingdomOverview", "adventureQuestLog",
            "adventureMoveHero", "adventureCastSpell", "adventureNextHero",
            "adventureEndTurn")
assert tuple(x["hotkey"] for x in buttons) == expected
for button in buttons:
    assert button["mobileTouchTarget"] is True
    assert button["area"]["width"] >= 44 and button["area"]["height"] >= 44
    assert button["area"]["left"] + button["area"]["width"] <= dock["area"]["width"]
# Ensure the fixed-size action dock fits classic small iPhone landscape views
# as well as newer large iPhone/iPad viewport sizes.
area = dock["area"]
for screen_w, screen_h in [(568, 320), (667, 375), (812, 375),
                           (852, 393), (1024, 768), (1194, 834)]:
    assert screen_w > dock["exists"]["widthMin"]
    assert screen_h > dock["exists"]["heightMin"]
    left = screen_w - area["right"] - area["width"]
    top = screen_h - area["bottom"] - area["height"]
    assert left >= 0, (screen_w, left)
    assert top >= 0, (screen_h, top)
    assert left + area["width"] <= screen_w - 199
    assert top + area["height"] <= screen_h - 47
print("Native VCMI iOS source and mobile action dock: passed")
