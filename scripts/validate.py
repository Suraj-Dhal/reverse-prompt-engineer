#!/usr/bin/env python3
"""Structural validation for the Reverse Prompt Engineer plugin.

Checks manifests (Agent Plugins, OpenAI Codex, Claude Code and its marketplace),
cross-manifest consistency, the SKILL.md contract and progressive-disclosure
wiring, eval fixtures and the generated eval suite, worked examples, licence,
required files and Markdown links.

This is *structural* validation. It does not prove the skill behaves well with
a live model; run the behavioural evals for that (see docs/evaluation.md).

Usage:
    python3 scripts/validate.py            # exit 0 = pass, 1 = errors found
    python3 scripts/validate.py --verbose  # also list passing checks
"""
from __future__ import annotations

import argparse
import re
import struct
import sys
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_evals  # noqa: E402
import lint_response  # noqa: E402
from _common import (  # noqa: E402
    MANIFESTS,
    PLUGIN_NAME,
    ROOT,
    load_json,
    markdown_files,
    markdown_links,
    parse_frontmatter,
    read_text,
)

AGENT_PLUGINS_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
AGENT_PLUGINS_KEYS = {
    "$schema", "name", "version", "description", "author", "homepage",
    "repository", "license", "keywords", "extensions",
}
SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SKILL_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
CODEX_LIMITS = {"displayName": 30, "shortDescription": 30, "longDescription": 4000, "developerName": 80}
CODEX_REQUIRED = ["displayName", "shortDescription", "longDescription", "developerName", "category", "capabilities"]
IDENTITY_FIELDS = ["name", "version", "description", "author", "homepage", "repository", "license", "keywords"]
REQUIRED_FILES = [
    "LICENSE", "README.md", "CHANGELOG.md", "CONTRIBUTING.md", "SECURITY.md", ".gitignore",
    "assets/icon.png",
    "docs/how-it-works.md", "docs/installation.md", "docs/usage.md",
    "docs/evaluation.md", "docs/licensing.md", "docs/review-v0.2.0.md",
    "evals/README.md", "evals/fixtures/trigger-evals.json", "evals/fixtures/reconstruction-evals.json",
]
SKILL_REQUIRED_PHRASES = [
    "## Reconstructed Prompt",
    "## Reasoning",
    "Overall confidence",
    "exact historical prompt",
    "{{UPPER_SNAKE_CASE}}",
    "### Requirement audit",
    "### Optional improvements (not evidence)",
]
MIT_PERMISSION = "Permission is hereby granted, free of charge, to any person obtaining a copy"
MIN_EXAMPLES = 3


class Report:
    def __init__(self) -> None:
        self.sections: List[Tuple[str, List[str], List[str]]] = []

    def add(self, title: str, errors: List[str], warnings: List[str]) -> None:
        self.sections.append((title, errors, warnings))

    @property
    def errors(self) -> int:
        return sum(len(e) for _, e, _ in self.sections)

    @property
    def warnings(self) -> int:
        return sum(len(w) for _, _, w in self.sections)


class Validator:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.manifests: Dict[str, Optional[dict]] = {}
        self.skill_fm: Dict[str, object] = {}

    # ------------------------------------------------------------------ helpers
    def p(self, rel: str) -> Path:
        return self.root / rel

    def rel(self, path: Path) -> str:
        try:
            return path.resolve().relative_to(self.root).as_posix()
        except ValueError:
            return path.as_posix()

    # ------------------------------------------------------------------ checks
    def check_manifests_parse(self, e: List[str], w: List[str]) -> None:
        for key, relpath in MANIFESTS.items():
            data, err = load_json(self.root / relpath)
            if err:
                e.append(f"{relpath.as_posix()}: {err}")
            elif not isinstance(data, dict):
                e.append(f"{relpath.as_posix()}: top level must be a JSON object")
                data = None
            self.manifests[key] = data
        for path in sorted(self.root.rglob("*.json")):
            parts = path.relative_to(self.root).parts
            if any(x in parts for x in (".git", "results", "node_modules", "dist")):
                continue
            _, err = load_json(path)
            if err:
                e.append(f"{self.rel(path)}: {err}")

    def check_agent_plugins(self, e: List[str], w: List[str]) -> None:
        m = self.manifests.get("agent-plugins")
        if not m:
            return
        if m.get("$schema") != AGENT_PLUGINS_SCHEMA:
            e.append(f"plugin.json: $schema must be {AGENT_PLUGINS_SCHEMA}")
        name = m.get("name", "")
        if not (1 <= len(name) <= 64 and re.match(r"^[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$", name)) or "--" in name or ".." in name:
            e.append(f"plugin.json: name '{name}' breaks Agent Plugins naming rules")
        if name != PLUGIN_NAME:
            e.append(f"plugin.json: name must be '{PLUGIN_NAME}'")
        unknown = sorted(set(m) - AGENT_PLUGINS_KEYS)
        if unknown:
            e.append(f"plugin.json: unknown top-level field(s) for the closed Agent Plugins schema: {', '.join(unknown)}")
        for ns in (m.get("extensions") or {}):
            if not re.match(r"^[a-z0-9-]+(\.[a-z0-9-]+)+$", ns):
                e.append(f"plugin.json: extension namespace '{ns}' is not reverse-domain")
        version = m.get("version", "")
        if not SEMVER_RE.match(version):
            e.append(f"plugin.json: version '{version}' is not SemVer")

    def check_identity(self, e: List[str], w: List[str]) -> None:
        sources = {k: self.manifests.get(k) for k in ("agent-plugins", "codex", "claude")}
        ref = sources["agent-plugins"]
        if not ref:
            return
        for key, data in sources.items():
            if key == "agent-plugins" or not data:
                continue
            for field in IDENTITY_FIELDS:
                if data.get(field) != ref.get(field):
                    e.append(f"{MANIFESTS[key].as_posix()}: '{field}' differs from plugin.json")
        for field in ("homepage", "repository"):
            u = urlparse(str(ref.get(field, "")))
            if u.scheme != "https" or not u.netloc:
                e.append(f"plugin.json: {field} must be an https URL")
        author = ref.get("author") or {}
        if not author.get("name"):
            e.append("plugin.json: author.name is required")
        if ref.get("license") != "MIT":
            e.append("plugin.json: license must be the SPDX identifier 'MIT'")

        version = ref.get("version")
        meta = self.skill_fm.get("metadata") if isinstance(self.skill_fm.get("metadata"), dict) else {}
        if meta and meta.get("version") != version:
            e.append(f"SKILL.md: metadata.version '{meta.get('version')}' differs from manifest version '{version}'")
        if self.skill_fm.get("license") and self.skill_fm.get("license") != ref.get("license"):
            e.append("SKILL.md: license differs from manifest license")
        changelog = self.p("CHANGELOG.md")
        if changelog.is_file():
            released = re.findall(r"^## \[(\d+\.\d+\.\d+[^\]]*)\]", read_text(changelog), re.M)
            if not released:
                e.append("CHANGELOG.md: no released version heading like '## [1.0.0] - YYYY-MM-DD'")
            elif released[0] != version:
                e.append(f"CHANGELOG.md: latest released version {released[0]} differs from manifest version {version}")

    def _png_size(self, path: Path) -> Optional[Tuple[int, int]]:
        with path.open("rb") as fh:
            head = fh.read(24)
        if head[:8] != b"\x89PNG\r\n\x1a\n" or head[12:16] != b"IHDR":
            return None
        return struct.unpack(">II", head[16:24])

    @staticmethod
    def _luminance(hex_color: str) -> float:
        def chan(v: int) -> float:
            c = v / 255
            return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
        r, g, b = (int(hex_color[i : i + 2], 16) for i in (1, 3, 5))
        return 0.2126 * chan(r) + 0.7152 * chan(g) + 0.0722 * chan(b)

    def check_codex(self, e: List[str], w: List[str]) -> None:
        codex = self.manifests.get("codex")
        portable = self.manifests.get("agent-plugins")
        ifaces = []
        if codex:
            ifaces.append((".codex-plugin/plugin.json interface", codex.get("interface")))
            if codex.get("skills") not in ("./skills", "./skills/"):
                e.append(".codex-plugin/plugin.json: skills must be './skills/'")
            if "hooks" in codex:
                e.append(".codex-plugin/plugin.json: 'hooks' is rejected by Codex validation")
        if portable:
            ifaces.append(("plugin.json extensions.com.openai.interface",
                           ((portable.get("extensions") or {}).get("com.openai") or {}).get("interface")))
        if len(ifaces) == 2 and ifaces[0][1] != ifaces[1][1]:
            e.append("Codex interface objects in plugin.json and .codex-plugin/plugin.json differ")
        for label, iface in ifaces:
            if not isinstance(iface, dict):
                e.append(f"{label}: missing")
                continue
            for key in CODEX_REQUIRED:
                if key not in iface or iface[key] in ("", None):
                    e.append(f"{label}: '{key}' is required")
            for key, limit in CODEX_LIMITS.items():
                if len(str(iface.get(key, ""))) > limit:
                    e.append(f"{label}: {key} exceeds {limit} characters")
            caps = iface.get("capabilities", [])
            if not isinstance(caps, list) or len(caps) > 20 or any(not isinstance(c, str) or len(c) > 120 for c in caps):
                e.append(f"{label}: capabilities must be at most 20 strings of at most 120 characters")
            dp = iface.get("defaultPrompt", [])
            dp_list = [dp] if isinstance(dp, str) else dp
            if not isinstance(dp_list, list) or len(dp_list) > 3:
                e.append(f"{label}: defaultPrompt must be a string or a list of at most 3 strings")
            else:
                for s in dp_list:
                    if not isinstance(s, str) or len(s) > 128:
                        e.append(f"{label}: defaultPrompt entries must be strings of at most 128 characters")
                    elif len(s) > 60:
                        w.append(f"{label}: defaultPrompt '{s[:30]}…' is over ~50 characters (Codex prefers short starters)")
                if len(set(dp_list)) != len(dp_list):
                    e.append(f"{label}: defaultPrompt entries must be unique")
            for key in ("websiteURL", "privacyPolicyURL", "termsOfServiceURL", "supportURL"):
                if key in iface:
                    u = urlparse(iface[key])
                    if u.scheme != "https" or not u.netloc or len(iface[key]) > 1024 or u.username:
                        e.append(f"{label}: {key} must be an https URL of at most 1024 characters")
            color = iface.get("brandColor")
            if color is not None:
                if not re.match(r"^#[0-9A-Fa-f]{6}$", str(color)):
                    e.append(f"{label}: brandColor must be #RRGGBB")
                else:
                    contrast = 1.05 / (self._luminance(color) + 0.05)
                    if contrast < 2.0:
                        e.append(f"{label}: brandColor contrast against white is {contrast:.2f}:1 (needs 2:1)")
            for key in ("logo", "composerIcon", "logoDark", "composerIconDark"):
                if key in iface:
                    self._check_image(f"{label}: {key}", iface[key], e)

    def _check_image(self, label: str, relpath: str, e: List[str], min_px: int = 48, max_px: int = 4096) -> None:
        if not str(relpath).startswith("./"):
            e.append(f"{label}: path must start with './'")
            return
        path = self.root / relpath[2:]
        if not path.is_file():
            e.append(f"{label}: file not found: {relpath}")
            return
        if path.stat().st_size > 5 * 1024 * 1024:
            e.append(f"{label}: larger than 5 MiB")
        if path.suffix.lower() == ".png":
            size = self._png_size(path)
            if not size:
                e.append(f"{label}: not a valid PNG")
            elif size[0] != size[1] or not (min_px <= size[0] <= max_px):
                e.append(f"{label}: must be square, {min_px}-{max_px} px (is {size[0]}x{size[1]})")

    def check_claude(self, e: List[str], w: List[str]) -> None:
        m = self.manifests.get("claude")
        if m:
            name = m.get("name", "")
            if re.match(r"^(claude|anthropic|anthropics|cc-plugin)-", name) or name in {"claude", "anthropic", "claude-code"}:
                e.append(f".claude-plugin/plugin.json: name '{name}' is reserved by Claude Code")
            if "icon" in m:
                self._check_image(".claude-plugin/plugin.json: icon", m["icon"], e, min_px=512, max_px=2048)
            for comp in ("skills", "commands", "agents"):
                if comp in m:
                    w.append(f".claude-plugin/plugin.json: '{comp}' set; the default directory scan may change")
        mk = self.manifests.get("claude-marketplace")
        if mk:
            if not (mk.get("owner") or {}).get("name"):
                e.append(".claude-plugin/marketplace.json: owner.name is required")
            mname = mk.get("name", "")
            if not mname or re.search(r"[\s/\\]|\.\.", mname) or mname.startswith("claudeai-"):
                e.append(f".claude-plugin/marketplace.json: invalid marketplace name '{mname}'")
            entries = [p for p in mk.get("plugins", []) if isinstance(p, dict) and p.get("name") == PLUGIN_NAME]
            if len(entries) != 1:
                e.append(f".claude-plugin/marketplace.json: needs exactly one '{PLUGIN_NAME}' entry")
            else:
                entry = entries[0]
                if entry.get("source") not in ("./", "."):
                    e.append(".claude-plugin/marketplace.json: plugin source must be './' (this repository)")
                if "version" in entry:
                    w.append(".claude-plugin/marketplace.json: entry 'version' is overridden by plugin.json; omit it")
                ref = self.manifests.get("agent-plugins") or {}
                if entry.get("description") != ref.get("description"):
                    e.append(".claude-plugin/marketplace.json: entry description differs from plugin.json")
        if (self.root / "CLAUDE.md").exists():
            w.append("CLAUDE.md at the plugin root is not loaded by Claude Code and triggers a validate warning")

    def check_skill(self, e: List[str], w: List[str]) -> None:
        skill_dir = self.root / "skills" / PLUGIN_NAME
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            e.append(f"skills/{PLUGIN_NAME}/SKILL.md missing")
            return
        others = sorted(p.name for p in (self.root / "skills").iterdir() if p.is_dir() and p.name != PLUGIN_NAME)
        if others:
            w.append(f"additional skills found: {', '.join(others)} (not covered by these checks)")
        text = read_text(skill_md)
        fm, body, err = parse_frontmatter(text)
        if err:
            e.append(f"SKILL.md: {err}")
            return
        self.skill_fm = fm or {}
        unknown = sorted(set(self.skill_fm) - SKILL_KEYS)
        if unknown:
            e.append(f"SKILL.md: unsupported frontmatter key(s): {', '.join(unknown)}")
        name = str(self.skill_fm.get("name", ""))
        if not (1 <= len(name) <= 64 and SKILL_NAME_RE.match(name)):
            e.append(f"SKILL.md: name '{name}' breaks Agent Skills naming rules")
        if name != skill_dir.name:
            e.append(f"SKILL.md: name '{name}' must match its directory '{skill_dir.name}'")
        desc = str(self.skill_fm.get("description", ""))
        if not 1 <= len(desc) <= 1024:
            e.append(f"SKILL.md: description must be 1-1024 characters (is {len(desc)})")
        if "compatibility" in self.skill_fm and not 1 <= len(str(self.skill_fm["compatibility"])) <= 500:
            e.append("SKILL.md: compatibility must be 1-500 characters")
        if "metadata" in self.skill_fm and not isinstance(self.skill_fm["metadata"], dict):
            e.append("SKILL.md: metadata must be a mapping of strings")
        body_lines = body.count("\n") + 1
        if body_lines >= 500:
            e.append(f"SKILL.md: body is {body_lines} lines (keep it under 500)")
        words = len(body.split())
        if words > 3500:
            w.append(f"SKILL.md: body is {words} words (~{int(words * 1.4)} tokens); the recommended budget is 5000 tokens")
        for phrase in SKILL_REQUIRED_PHRASES:
            if phrase not in body:
                e.append(f"SKILL.md: required contract text missing: {phrase!r}")

        # progressive disclosure: every link resolves, every resource is linked
        linked = set()
        for link in markdown_links(body):
            target = link.split("#", 1)[0]
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            path = (skill_dir / target).resolve()
            if not path.exists():
                e.append(f"SKILL.md: broken link {link}")
            linked.add(path)
        for sub in ("references", "assets"):
            for f in sorted((skill_dir / sub).glob("**/*")):
                if f.is_file() and f.resolve() not in linked:
                    e.append(f"SKILL.md: {self.rel(f)} is never linked, so agents will never load it")
        for f in sorted(skill_dir.iterdir()):
            if f.name not in {"SKILL.md", "references", "assets", "scripts"}:
                e.append(f"skill folder contains '{f.name}'; keep dev artefacts (tests, evals) outside the runtime skill")

    def check_required_files(self, e: List[str], w: List[str]) -> None:
        for relpath in REQUIRED_FILES:
            if not self.p(relpath).is_file():
                e.append(f"required file missing: {relpath}")

    def check_license(self, e: List[str], w: List[str]) -> None:
        lic = self.p("LICENSE")
        if not lic.is_file():
            return
        text = read_text(lic)
        if not text.startswith("MIT License"):
            e.append("LICENSE: must start with 'MIT License'")
        if MIT_PERMISSION not in text or "WITHOUT WARRANTY OF ANY KIND" not in text:
            e.append("LICENSE: standard MIT permission and warranty text not found")
        author = ((self.manifests.get("agent-plugins") or {}).get("author") or {}).get("name", "")
        m = re.search(r"Copyright \(c\) (\d{4})(?:[-–]\d{4})? (.+)", text)
        if not m:
            e.append("LICENSE: missing 'Copyright (c) <year> <holder>' line")
        elif author and m.group(2).strip() != author:
            e.append(f"LICENSE: copyright holder '{m.group(2).strip()}' differs from author '{author}'")

    def check_fixtures(self, e: List[str], w: List[str]) -> None:
        trig, err = load_json(self.p("evals/fixtures/trigger-evals.json"))
        if err:
            e.append(err)
            trig = []
        beh, err = load_json(self.p("evals/fixtures/reconstruction-evals.json"))
        if err:
            e.append(err)
            beh = []
        if not isinstance(trig, list) or not isinstance(beh, list):
            e.append("eval fixtures must be JSON arrays")
            return

        ids = [c.get("id") for c in trig if isinstance(c, dict)]
        if len(ids) != len(set(ids)):
            e.append("trigger-evals.json: duplicate ids")
        for i, c in enumerate(trig, 1):
            if not isinstance(c, dict):
                e.append(f"trigger case #{i}: must be an object")
                continue
            cid = c.get("id", f"#{i}")
            if not re.match(r"^T\d{2,3}$", str(c.get("id", ""))):
                e.append(f"trigger case {cid}: id must look like T01")
            if not isinstance(c.get("query"), str) or not c["query"].strip():
                e.append(f"trigger case {cid}: query must be a non-empty string")
            if not isinstance(c.get("expected_trigger"), bool):
                e.append(f"trigger case {cid}: expected_trigger must be true or false")
            tags = c.get("tags", [])
            if not isinstance(tags, list) or "trigger" not in tags or any(not isinstance(t, str) for t in tags):
                e.append(f"trigger case {cid}: tags must be strings and include 'trigger'")
        n = len(trig)
        pos = sum(1 for c in trig if isinstance(c, dict) and c.get("expected_trigger") is True)
        if n < 40:
            e.append(f"trigger-evals.json: {n} cases (need at least 40)")
        if n and not (0.4 <= pos / n <= 0.6):
            e.append(f"trigger-evals.json: unbalanced ({pos} positive of {n}); keep each class at 40-60%")

        required = ["id", "title", "prompt", "input", "context_available", "must_preserve",
                    "expected_output", "prohibited", "pass_fail", "tags", "critical"]
        bids = [c.get("id") for c in beh if isinstance(c, dict)]
        if len(bids) != len(set(bids)):
            e.append("reconstruction-evals.json: duplicate ids")
        expected_ids = [f"B{i:02d}" for i in range(1, len(beh) + 1)]
        if bids != expected_ids:
            e.append("reconstruction-evals.json: ids must run B01, B02, ... with no gaps, in order")
        if len(beh) < 25:
            e.append(f"reconstruction-evals.json: {len(beh)} cases (need at least 25)")
        for c in beh:
            if not isinstance(c, dict):
                e.append("behaviour case must be an object")
                continue
            cid = c.get("id", "?")
            for key in required:
                if key not in c:
                    e.append(f"behaviour case {cid}: missing '{key}'")
            for key in ("must_preserve", "expected_output", "prohibited", "pass_fail"):
                v = c.get(key)
                if key in c and (not isinstance(v, list) or not v or any(not isinstance(x, str) or not x.strip() for x in v)):
                    e.append(f"behaviour case {cid}: '{key}' must be a non-empty list of strings")
            if isinstance(c.get("prompt"), str) and len(c["prompt"].strip()) < 40:
                e.append(f"behaviour case {cid}: prompt is too short to be a runnable case")
            for key in ("critical", "contract", "require_skill", "rubric"):
                if key in c and not isinstance(c[key], bool):
                    e.append(f"behaviour case {cid}: '{key}' must be true or false")
            if "behavior" not in c.get("tags", []):
                e.append(f"behaviour case {cid}: tags must include 'behavior'")
            names = set()
            for g in c.get("graders", []):
                gname = g.get("name", "")
                if not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", gname) or gname in names:
                    e.append(f"behaviour case {cid}: grader name '{gname}' must be a unique kebab-case slug")
                names.add(gname)
                if g.get("type") != "regex":
                    e.append(f"behaviour case {cid}: grader '{gname}' type must be 'regex'")
                match = g.get("match", "contains")
                if match not in ("contains", "not_contains") and not re.match(r"^count:\d+$", str(match)):
                    e.append(f"behaviour case {cid}: grader '{gname}' has invalid match '{match}'")
                try:
                    re.compile(g.get("pattern", ""))
                except re.error as exc:
                    w.append(f"behaviour case {cid}: grader '{gname}' pattern does not compile in Python ({exc}); check it is valid JavaScript")
        smoke = [c.get("id") for c in list(trig) + list(beh) if isinstance(c, dict) and "smoke" in c.get("tags", [])]
        if not smoke:
            w.append("no cases tagged 'smoke'; a cheap smoke subset is recommended")

    def check_generated_suite(self, e: List[str], w: List[str]) -> None:
        try:
            problems = build_evals.check(self.root)
        except SystemExit as exc:
            e.append(str(exc))
            return
        if problems:
            e.append(f"generated eval suite is out of date ({len(problems)} problem(s)); run: python3 scripts/build_evals.py")
            e.extend(f"  {p}" for p in problems[:10])

    def check_examples(self, e: List[str], w: List[str]) -> None:
        path = self.root / "skills" / PLUGIN_NAME / "references" / "worked-examples.md"
        if not path.is_file():
            e.append("worked-examples.md missing")
            return
        examples = lint_response.extract_examples(read_text(path))
        if len(examples) < MIN_EXAMPLES:
            e.append(f"worked-examples.md: {len(examples)} example response(s); need at least {MIN_EXAMPLES}")
        for ex_id, text in examples:
            res = lint_response.lint(text)
            e.extend(f"worked example '{ex_id}': {msg}" for msg in res.errors)
            w.extend(f"worked example '{ex_id}': {msg}" for msg in res.warnings)

    def check_links(self, e: List[str], w: List[str]) -> None:
        for md in markdown_files(self.root):
            for link in markdown_links(read_text(md)):
                target = link.split("#", 1)[0]
                if not target or "://" in target or target.startswith(("mailto:", "#")):
                    continue
                if not (md.parent / target).resolve().exists():
                    e.append(f"{self.rel(md)}: broken relative link '{link}'")

    # ------------------------------------------------------------------ driver
    def run(self) -> Report:
        report = Report()
        checks: List[Tuple[str, Callable[[List[str], List[str]], None]]] = [
            ("Manifests parse", self.check_manifests_parse),
            ("Agent Plugins manifest", self.check_agent_plugins),
            ("SKILL.md and progressive disclosure", self.check_skill),
            ("Identity consistency (manifests, SKILL.md, CHANGELOG)", self.check_identity),
            ("OpenAI Codex listing", self.check_codex),
            ("Claude Code manifest and marketplace", self.check_claude),
            ("Required files", self.check_required_files),
            ("MIT licence", self.check_license),
            ("Eval fixtures", self.check_fixtures),
            ("Generated eval suite in sync", self.check_generated_suite),
            ("Worked examples meet the response contract", self.check_examples),
            ("Markdown relative links", self.check_links),
        ]
        for title, fn in checks:
            errors: List[str] = []
            warnings: List[str] = []
            try:
                fn(errors, warnings)
            except Exception as exc:  # a crashing check is a reported failure, never a traceback
                errors.append(f"check crashed: {type(exc).__name__}: {exc}")
            report.add(title, errors, warnings)
        return report


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Structural validation for the Reverse Prompt Engineer plugin.")
    ap.add_argument("--root", type=Path, default=ROOT, help="repository root (default: this checkout)")
    ap.add_argument("--verbose", action="store_true", help="also list checks that passed")
    args = ap.parse_args(argv)

    report = Validator(args.root).run()
    for title, errors, warnings in report.sections:
        if errors:
            print(f"FAIL  {title}")
        elif warnings:
            print(f"WARN  {title}")
        elif args.verbose:
            print(f"ok    {title}")
        for msg in errors:
            print(f"      error:   {msg}")
        for msg in warnings:
            print(f"      warning: {msg}")
    status = "FAIL" if report.errors else "PASS"
    print(f"\n{status}: {len(report.sections)} checks, {report.errors} error(s), {report.warnings} warning(s).")
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
