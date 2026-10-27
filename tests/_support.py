"""Test helpers: import the scripts and work on throwaway copies of the repository."""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

SKILL = Path("skills/reverse-prompt-engineer/SKILL.md")


class RepoCopyTestCase(unittest.TestCase):
    """Gives each test a fresh copy of the repository in a temporary directory."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name) / "repo"
        shutil.copytree(
            ROOT,
            self.repo,
            ignore=shutil.ignore_patterns(".git", "dist", "__pycache__", "results", ".pytest_cache"),
        )

    def tearDown(self) -> None:
        self._tmp.cleanup()

    # convenience -----------------------------------------------------------
    def read(self, rel) -> str:
        return (self.repo / rel).read_text(encoding="utf-8")

    def write(self, rel, text: str) -> None:
        path = self.repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def edit_json(self, rel, fn) -> None:
        data = json.loads(self.read(rel))
        fn(data)
        self.write(rel, json.dumps(data, indent=2, ensure_ascii=False) + "\n")
