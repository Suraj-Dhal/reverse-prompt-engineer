#!/usr/bin/env python3
"""Build reproducible release archives.

Creates, in dist/:
  reverse-prompt-engineer-<version>-plugin.zip   full plugin (manifests, skill, icon, licence, docs)
  reverse-prompt-engineer-<version>-skill.zip    the skill folder alone, for skill uploads
                                                 (for example Claude.ai > Settings > Capabilities)
  SHA256SUMS.txt                                 checksums for both archives

Archives are reproducible: entries are sorted and carry fixed timestamps and
permissions, so the same commit always yields identical file contents. The
compressed bytes (and so the checksums) are identical when built with the same
Python/zlib version, as in CI; other zlib versions may compress slightly differently.

Usage:
    python3 scripts/package.py [--out dist]
"""
from __future__ import annotations

import argparse
import hashlib
import sys
import zipfile
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import PLUGIN_NAME, ROOT, load_json  # noqa: E402

FIXED_DATE = (2026, 1, 1, 0, 0, 0)
PLUGIN_PATHS = [
    "plugin.json",
    ".codex-plugin",
    ".claude-plugin",
    "skills",
    "assets",
    "LICENSE",
    "README.md",
    "CHANGELOG.md",
    "SECURITY.md",
    "docs",
]
EXCLUDE_PARTS = {"__pycache__", ".DS_Store", "results"}


def _files(root: Path, rel_paths: Iterable[str]) -> List[Path]:
    out: List[Path] = []
    for rel in rel_paths:
        p = root / rel
        if p.is_file():
            out.append(p)
        elif p.is_dir():
            out.extend(f for f in p.rglob("*") if f.is_file() and not EXCLUDE_PARTS & set(f.parts))
        else:
            raise SystemExit(f"package: missing path {rel}")
    return sorted(set(out), key=lambda f: f.relative_to(root).as_posix())


def _write_zip(dest: Path, entries: List[Tuple[str, bytes]]) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(dest, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for arcname, data in sorted(entries):
            info = zipfile.ZipInfo(arcname, date_time=FIXED_DATE)
            info.external_attr = 0o644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            zf.writestr(info, data, compresslevel=9)


def build(root: Path = ROOT, out: Optional[Path] = None) -> List[Path]:
    manifest, err = load_json(root / "plugin.json")
    if err:
        raise SystemExit(f"package: {err}")
    version = manifest["version"]
    out = out or root / "dist"
    prefix = PLUGIN_NAME

    plugin_entries = [
        (f"{prefix}/{f.relative_to(root).as_posix()}", f.read_bytes()) for f in _files(root, PLUGIN_PATHS)
    ]
    skill_dir = root / "skills" / PLUGIN_NAME
    skill_entries = [
        (f"{prefix}/{f.relative_to(skill_dir).as_posix()}", f.read_bytes()) for f in _files(skill_dir, ["."])
    ]
    skill_entries.append((f"{prefix}/LICENSE.txt", (root / "LICENSE").read_bytes()))

    plugin_zip = out / f"{prefix}-{version}-plugin.zip"
    skill_zip = out / f"{prefix}-{version}-skill.zip"
    _write_zip(plugin_zip, plugin_entries)
    _write_zip(skill_zip, skill_entries)

    sums = out / "SHA256SUMS.txt"
    lines = [f"{hashlib.sha256(z.read_bytes()).hexdigest()}  {z.name}" for z in (plugin_zip, skill_zip)]
    sums.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return [plugin_zip, skill_zip, sums]


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Build reproducible release archives.")
    ap.add_argument("--out", type=Path, default=None, help="output directory (default: dist/)")
    args = ap.parse_args(argv)
    for path in build(out=args.out):
        size = path.stat().st_size
        print(f"{path.relative_to(ROOT) if ROOT in path.parents else path}  ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
