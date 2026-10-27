#!/usr/bin/env python3
"""Set a new version everywhere it is recorded, in one step.

Updates plugin.json, .codex-plugin/plugin.json, .claude-plugin/plugin.json and
the SKILL.md metadata, and turns the CHANGELOG "Unreleased" section into a
dated release section.

Usage:
    python3 scripts/bump_version.py 1.1.0
    python3 scripts/bump_version.py 1.1.0 --date 2026-12-01
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path
from typing import List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import PLUGIN_NAME, ROOT, write_text_lf  # noqa: E402

SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?$")
JSON_FILES = ["plugin.json", ".codex-plugin/plugin.json", ".claude-plugin/plugin.json"]


def bump(new: str, date: str, root: Path = ROOT) -> List[str]:
    changed = []
    for rel in JSON_FILES:
        p = root / rel
        text = p.read_text(encoding="utf-8")
        updated, n = re.subn(r'("version"\s*:\s*")[^"]+(")', rf"\g<1>{new}\g<2>", text, count=1)
        if n != 1:
            raise SystemExit(f"bump: no version field in {rel}")
        if updated != text:
            write_text_lf(p, updated)
            changed.append(rel)

    skill = root / "skills" / PLUGIN_NAME / "SKILL.md"
    text = skill.read_text(encoding="utf-8")
    updated, n = re.subn(r'(\n  version:\s*")[^"]+(")', rf"\g<1>{new}\g<2>", text, count=1)
    if n != 1:
        raise SystemExit("bump: no metadata.version in SKILL.md")
    if updated != text:
        write_text_lf(skill, updated)
        changed.append(skill.relative_to(root).as_posix())

    log = root / "CHANGELOG.md"
    text = log.read_text(encoding="utf-8")
    if f"## [{new}]" not in text:
        if "## [Unreleased]" not in text:
            raise SystemExit("bump: CHANGELOG.md has no '## [Unreleased]' section to release")
        text = text.replace("## [Unreleased]", f"## [Unreleased]\n\n## [{new}] - {date}", 1)
        repo = "https://github.com/Suraj-Dhal/reverse-prompt-engineer"
        link = f"[{new}]: {repo}/releases/tag/v{new}"
        if link not in text:
            text = text.rstrip("\n") + "\n" + link + "\n"
        write_text_lf(log, text)
        changed.append("CHANGELOG.md")
    return changed


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Set a new version everywhere it is recorded.")
    ap.add_argument("version", help="new SemVer version, e.g. 1.1.0")
    ap.add_argument("--date", default=dt.date.today().isoformat(), help="release date (default: today)")
    args = ap.parse_args(argv)
    if not SEMVER_RE.match(args.version):
        ap.error(f"'{args.version}' is not a SemVer version")
    changed = bump(args.version, args.date)
    print("Updated: " + (", ".join(changed) if changed else "nothing (already at that version)"))
    print("Next: edit the CHANGELOG entry, run python3 scripts/validate.py, then commit and tag v" + args.version)
    return 0


if __name__ == "__main__":
    sys.exit(main())
