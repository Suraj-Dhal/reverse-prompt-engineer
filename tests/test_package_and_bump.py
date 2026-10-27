"""Tests for scripts/package.py and scripts/bump_version.py."""
from __future__ import annotations

import hashlib
import tempfile
import unittest
import zipfile
from pathlib import Path

from _support import ROOT, RepoCopyTestCase

import bump_version  # noqa: E402
import package  # noqa: E402
import validate  # noqa: E402


class Packaging(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.out = Path(self._tmp.name)
        self.paths = package.build(ROOT, self.out)

    def tearDown(self):
        self._tmp.cleanup()

    def names(self, zip_path):
        with zipfile.ZipFile(zip_path) as zf:
            return zf.namelist()

    def test_outputs(self):
        self.assertEqual(len(self.paths), 3)
        for p in self.paths:
            self.assertTrue(p.is_file(), p)

    def test_plugin_zip_contents(self):
        names = self.names(self.paths[0])
        for required in (
            "reverse-prompt-engineer/plugin.json",
            "reverse-prompt-engineer/.claude-plugin/plugin.json",
            "reverse-prompt-engineer/.codex-plugin/plugin.json",
            "reverse-prompt-engineer/skills/reverse-prompt-engineer/SKILL.md",
            "reverse-prompt-engineer/assets/icon.png",
            "reverse-prompt-engineer/LICENSE",
        ):
            self.assertIn(required, names)
        for excluded in ("/tests/", "/scripts/", "/evals/", "/.github/"):
            self.assertFalse(any(excluded in n for n in names), excluded)

    def test_skill_zip_is_upload_ready(self):
        names = self.names(self.paths[1])
        self.assertIn("reverse-prompt-engineer/SKILL.md", names)
        self.assertIn("reverse-prompt-engineer/LICENSE.txt", names)
        self.assertTrue(all(n.startswith("reverse-prompt-engineer/") for n in names))

    def test_reproducible(self):
        with tempfile.TemporaryDirectory() as other:
            again = package.build(ROOT, Path(other))
            for a, b in zip(self.paths[:2], again[:2]):
                self.assertEqual(hashlib.sha256(a.read_bytes()).hexdigest(), hashlib.sha256(b.read_bytes()).hexdigest())

    def test_checksums_match(self):
        lines = self.paths[2].read_text(encoding="utf-8").splitlines()
        for line in lines:
            digest, name = line.split("  ")
            self.assertEqual(hashlib.sha256((self.out / name).read_bytes()).hexdigest(), digest)


class ReleaseNotes(unittest.TestCase):
    def test_current_version_notes(self):
        import json
        import release_notes

        version = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))["version"]
        text = release_notes.notes(version)
        self.assertIn("### Added", text)
        self.assertNotIn("## [", text)            # only this version's section
        self.assertNotIn("[0.2.0]: http", text)  # no link references
        self.assertIn(f"/blob/v{version}/docs/installation.md", text)

    def test_unknown_version(self):
        import release_notes

        with self.assertRaises(SystemExit):
            release_notes.notes("99.0.0")


class VersionBump(RepoCopyTestCase):
    def test_bump_keeps_repository_valid(self):
        self.write("CHANGELOG.md", self.read("CHANGELOG.md").replace("## [Unreleased]", "## [Unreleased]\n\n### Added\n\n- Something.", 1))
        changed = bump_version.bump("1.1.0", "2026-12-01", self.repo)
        self.assertIn("CHANGELOG.md", changed)
        self.assertIn('"version": "1.1.0"', self.read("plugin.json"))
        self.assertIn('version: "1.1.0"', self.read("skills/reverse-prompt-engineer/SKILL.md"))
        log = self.read("CHANGELOG.md")
        self.assertIn("## [1.1.0] - 2026-12-01\n\n### Added\n\n- Something.", log)
        report = validate.Validator(self.repo).run()
        identity = [errs for title, errs, _ in report.sections if title.startswith("Identity")][0]
        self.assertEqual(identity, [])

    def test_bump_is_idempotent(self):
        bump_version.bump("1.1.0", "2026-12-01", self.repo)
        self.assertEqual(bump_version.bump("1.1.0", "2026-12-01", self.repo), [])


if __name__ == "__main__":
    unittest.main()
