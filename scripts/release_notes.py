#!/usr/bin/env python3
"""Print the CHANGELOG section for one version (used as GitHub release notes).

Usage:
    python3 scripts/release_notes.py 1.0.0 > notes.md
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import ROOT  # noqa: E402

FOOTER = (
    "\n---\n\n"
    "**Install:** see [docs/installation.md](https://github.com/Suraj-Dhal/reverse-prompt-engineer/blob/{tag}/docs/installation.md). "
    "`*-skill.zip` is for skill upload (e.g. Claude.ai); `*-plugin.zip` is the full plugin. "
    "Verify downloads against `SHA256SUMS.txt`.\n"
)


def notes(version: str, root: Path = ROOT) -> str:
    text = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    m = re.search(rf"^## \[{re.escape(version)}\][^\n]*\n(.*?)(?=^## \[|^\[[^\]]+\]: |\Z)", text, re.S | re.M)
    if not m:
        raise SystemExit(f"release_notes: no CHANGELOG section for {version}")
    return m.group(1).strip() + "\n" + FOOTER.format(tag=f"v{version}")


def main(argv: Optional[List[str]] = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if len(args) != 1:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    sys.stdout.write(notes(args[0].lstrip("v")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
