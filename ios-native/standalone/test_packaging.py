import hashlib
import json
import plistlib
import struct
from pathlib import Path
import tempfile
import unittest
import zipfile
from pack_standalone import PackagingError, APP, resolve_game_root, package

class TestStandalone(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        self.base=self.root/"engine.ipa"
        with zipfile.ZipFile(self.base,"w") as z:
            z.writestr(APP+"Info.plist",plistlib.dumps({"CFBundleSupportedPlatforms":["iPhoneOS"],"CFBundleExecutable":"vcmiclient","CFBundleIdentifier":"com.example.test","CFBundleName":"VCMI"},fmt=plistlib.FMT_BINARY))
            z.writestr(APP+"vcmiclient",struct.pack("<IIII",0xfeedfacf,0x0100000c,0,2)+b"arm64-stub")
            z.writestr(APP+"config/settings.json",'{}')
            z.writestr(APP+"config/widgets/adventureMap.json",'{"items":[{"name":"iosQuickActions"}]}')
        self.game=self.root/"extract"/"app"/"Heroes 3 Complete"
        (self.game/"Data").mkdir(parents=True)
        (self.game/"Maps").mkdir()
        (self.game/"Mp3").mkdir()
        for f in ("H3Bitmap.lod","H3Sprite.lod"):
            (self.game/"Data"/f).write_bytes(b"fake-data")
        (self.game/"Maps"/"sample.h3m").write_bytes(b"sample map")
        (self.game/"Mp3"/"sample.mp3").write_bytes(b"sample music")
        self.output=self.root/"private"/"standalone.ipa"
    def tearDown(self):self.temp.cleanup()
    def test_finds_nested_game(self):self.assertEqual(resolve_game_root(self.root/"extract"),self.game)
    def test_packages_app_resources(self):
        m=package(self.base,self.root/"extract",self.output,"personal")
        self.assertEqual(m["asset_count"],4)
        self.assertTrue(self.output.exists())
        with zipfile.ZipFile(self.output) as z:
            self.assertIsNone(z.testzip())
            self.assertEqual(z.read(APP+"Data/H3Bitmap.lod"),b"fake-data")
            self.assertEqual(z.read(APP+"Maps/sample.h3m"),b"sample map")
            self.assertEqual(z.read(APP+"config/settings.json"),b"{}")
            self.assertEqual(plistlib.loads(z.read(APP+"Info.plist"))["CFBundleDisplayName"],"Heroes III Mobile")
        self.assertEqual(json.loads(self.output.with_suffix(".manifest.json").read_text())["ipa_sha256"],hashlib.sha256(self.output.read_bytes()).hexdigest())
    def test_dry_run(self):
        m=package(self.base,self.root/"extract",self.output,"personal",dry_run=True)
        self.assertTrue(m["dry_run"])
        self.assertFalse(self.output.exists())
    def test_missing_map_rejected(self):
        (self.game/"Maps"/"sample.h3m").unlink()
        with self.assertRaises(PackagingError):package(self.base,self.root/"extract",self.output,"personal")
    def test_signed_input_rejected(self):
        with zipfile.ZipFile(self.base,"a") as z:z.writestr(APP+"_CodeSignature/CodeResources",b"signed")
        with self.assertRaises(PackagingError):package(self.base,self.root/"extract",self.output,"personal")
    def test_symlink_rejected(self):
        (self.game/"Maps"/"link.h3m").symlink_to(self.game/"Maps"/"sample.h3m")
        with self.assertRaises(PackagingError):package(self.base,self.root/"extract",self.output,"personal")
    def test_executable_rejected(self):
        (self.game/"Data"/"installer.exe").write_bytes(b"unsafe")
        with self.assertRaises(PackagingError):package(self.base,self.root/"extract",self.output,"personal")
    def test_output_overwrite_rejected(self):
        self.output.parent.mkdir(parents=True)
        self.output.write_bytes(b"previous-user-build")
        with self.assertRaises(PackagingError):
            package(self.base,self.root/"extract",self.output,"personal")
        self.assertEqual(self.output.read_bytes(),b"previous-user-build")

    def test_not_arm64_rejected(self):
        with zipfile.ZipFile(self.base,"w") as z:
            z.writestr(APP+"Info.plist",plistlib.dumps({"CFBundleSupportedPlatforms":["iPhoneOS"],"CFBundleExecutable":"vcmiclient"}))
            z.writestr(APP+"vcmiclient",b"unknown-machine")
            z.writestr(APP+"config/widgets/adventureMap.json",'iosQuickActions')
        with self.assertRaises(PackagingError):
            package(self.base,self.root/"extract",self.output,"personal")

    def test_wrong_engine_rejected(self):
        with zipfile.ZipFile(self.base,"w") as z:
            z.writestr(APP+"Info.plist",plistlib.dumps({"CFBundleSupportedPlatforms":["iPhoneOS"],"CFBundleExecutable":"vcmiclient"}))
            z.writestr(APP+"vcmiclient",struct.pack("<IIII",0xfeedfacf,0x0100000c,0,2))
            z.writestr(APP+"config/widgets/adventureMap.json",'no-mobile-interface')
        with self.assertRaises(PackagingError):
            package(self.base,self.root/"extract",self.output,"personal")

    def test_existing_game_dir_rejected(self):
        with zipfile.ZipFile(self.base,"a") as z:z.writestr(APP+"Data/",b"")
        with self.assertRaises(PackagingError):package(self.base,self.root/"extract",self.output,"personal")

if __name__=='__main__':unittest.main()
