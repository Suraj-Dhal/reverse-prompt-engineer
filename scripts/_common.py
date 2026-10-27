"""Shared helpers for the repository's maintenance scripts (standard library only)."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent
PLUGIN_NAME = "reverse-prompt-engineer"
SKILL_DIR = ROOT / "skills" / PLUGIN_NAME
FIXTURES_DIR = ROOT / "evals" / "fixtures"

MANIFESTS = {
    "agent-plugins": Path("plugin.json"),
    "codex": Path(".codex-plugin/plugin.json"),
    "claude": Path(".claude-plugin/plugin.json"),
    "claude-marketplace": Path(".claude-plugin/marketplace.json"),
}

PLACEHOLDER_RE = re.compile(r"\{\{\s*([^{}]*?)\s*\}\}")
VALID_PLACEHOLDER_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text_lf(path: Path, text: str) -> None:
    """Write UTF-8 text with LF line endings on every OS (Path.write_text(newline=) needs Python 3.10)."""
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def load_json(path: Path) -> Tuple[Optional[Any], Optional[str]]:
    """Return (data, error). Never raises for missing or malformed files."""
    if not path.is_file():
        return None, f"missing file: {path.relative_to(ROOT) if path.is_absolute() and ROOT in path.parents else path}"
    try:
        return json.loads(read_text(path)), None
    except json.JSONDecodeError as exc:
        return None, f"invalid JSON in {path.name}: {exc.msg} (line {exc.lineno}, column {exc.colno})"


def _unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def parse_frontmatter(text: str) -> Tuple[Optional[Dict[str, Any]], str, Optional[str]]:
    """Parse the YAML frontmatter subset used by SKILL.md.

    Supports ``key: value`` pairs and one level of nested mappings. Returns
    ``(frontmatter, body, error)``.
    """
    if not text.startswith("---\n"):
        return None, text, "frontmatter must start on line 1 with '---'"
    end = text.find("\n---\n", 4)
    if end == -1:
        return None, text, "frontmatter is not closed with '---'"
    block, body = text[4:end], text[end + 5 :]
    data: Dict[str, Any] = {}
    current: Optional[str] = None
    for lineno, raw in enumerate(block.splitlines(), start=2):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw.startswith((" ", "\t")):
            if current is None or not isinstance(data.get(current), dict):
                return None, body, f"unexpected indentation on frontmatter line {lineno}"
            key, sep, value = raw.strip().partition(":")
            if not sep:
                return None, body, f"expected 'key: value' on frontmatter line {lineno}"
            data[current][key.strip()] = _unquote(value)
            continue
        key, sep, value = raw.partition(":")
        if not sep:
            return None, body, f"expected 'key: value' on frontmatter line {lineno}"
        key = key.strip()
        if key in data:
            return None, body, f"duplicate frontmatter key '{key}'"
        if value.strip():
            data[key] = _unquote(value)
            current = None
        else:
            data[key] = {}
            current = key
    return data, body, None


_FENCE_RE = re.compile(r"^(\s*)(`{3,}|~{3,})")


def iter_fenced_blocks(text: str) -> Iterator[Tuple[str, str, int]]:
    """Yield (info_string, content, start_line) for each fenced code block."""
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        m = _FENCE_RE.match(lines[i])
        if m:
            fence = m.group(2)
            info = lines[i][m.end():].strip()
            start = i
            i += 1
            content: List[str] = []
            while i < len(lines):
                close = _FENCE_RE.match(lines[i])
                if close and close.group(2)[0] == fence[0] and len(close.group(2)) >= len(fence) and not lines[i][close.end():].strip():
                    break
                content.append(lines[i])
                i += 1
            yield info, "\n".join(content), start + 1
        i += 1


def strip_code(text: str) -> str:
    """Remove fenced code blocks and inline code spans (for link checking)."""
    out: List[str] = []
    in_fence: Optional[str] = None
    for line in text.split("\n"):
        m = _FENCE_RE.match(line)
        if in_fence is None and m:
            in_fence = m.group(2)
            out.append("")
            continue
        if in_fence is not None:
            if m and m.group(2)[0] == in_fence[0] and len(m.group(2)) >= len(in_fence) and not line[m.end():].strip():
                in_fence = None
            out.append("")
            continue
        out.append(re.sub(r"`+[^`]*`+", "", line))
    return "\n".join(out)


def markdown_links(text: str) -> List[str]:
    return re.findall(r"(?<!!)\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)", strip_code(text))


def markdown_files(root: Path = ROOT) -> List[Path]:
    skip = {".git", "dist", "node_modules", "results"}
    return sorted(
        p for p in root.rglob("*.md") if not any(part in skip for part in p.relative_to(root).parts)
    )


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()
