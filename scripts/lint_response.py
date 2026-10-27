#!/usr/bin/env python3
"""Check a Reverse Prompt Engineer response against the default response contract.

This is a *format* linter. It verifies structure (two sections in order, one
fenced prompt block, well-formed placeholders, a stated confidence level) and
flags a small set of prohibited claims. It cannot judge whether a
reconstruction is faithful: use the behavioural evals for that.

Usage:
    python3 scripts/lint_response.py response.md
    python3 scripts/lint_response.py - < response.md
    python3 scripts/lint_response.py --examples skills/reverse-prompt-engineer/references/worked-examples.md

Exit codes: 0 = pass (warnings allowed), 1 = contract errors, 2 = usage error.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import PLACEHOLDER_RE, VALID_PLACEHOLDER_RE, iter_fenced_blocks  # noqa: E402

PROMPT_HEADING = "reconstructed prompt"
REASONING_HEADING = "reasoning"
REASONING_LABELS = [
    "Observable clues",
    "Likely intent",
    "Context preserved",
    "Prompt-design factors",
    "Confidence and limits",
]
CONFIDENCE_RE = re.compile(r"overall\s+confidence\s*:?\s*\**\s*:?\s*\**\s*(high|moderate|low)\b", re.I)
AUDIT_STATUSES = {"followed", "partly", "missed", "not verifiable"}
MIN_PROMPT_WORDS = 8
MAX_REASONING_WORDS = 600

# Claims the skill must never make. Matched outside the prompt block, case-insensitively.
PROHIBITED_CLAIMS = [
    (
        re.compile(
            r"\b(?:here\s+is|here's|this\s+is|below\s+is|i\s+(?:have\s+)?(?:recovered|extracted|retrieved))\s+"
            r"(?:(?:the|its)\s+(?:exact|actual|original|real|hidden|verbatim)|your\s+(?:exact|actual|real|hidden|verbatim))\s+"
            r"(?:hidden\s+|system\s+|original\s+)?prompt\b",
            re.I,
        ),
        "claims exact or hidden-prompt recovery",
    ),
    (
        re.compile(r"\bthe\s+(?:exact|verbatim)\s+(?:hidden\s+|system\s+)?prompt\s+(?:was|is)\s*:", re.I),
        "presents a prompt as the exact original",
    ),
    (
        re.compile(r"\bI\s+(?:ran|executed|tested)\s+(?:the|this|your)\s+(?:code|snippet|script|function)\b", re.I),
        "claims code execution (verify this was real before shipping)",
    ),
]

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")


@dataclass
class LintResult:
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    placeholders: List[str] = field(default_factory=list)
    confidence: Optional[str] = None

    @property
    def ok(self) -> bool:
        return not self.errors

    def as_dict(self) -> dict:
        return {
            "ok": self.ok,
            "errors": self.errors,
            "warnings": self.warnings,
            "placeholders": self.placeholders,
            "confidence": self.confidence,
        }


def _headings(text: str) -> List[Tuple[int, int, str]]:
    """Return (line_index, level, title) for ATX headings outside fenced code."""
    fenced = set()
    for _info, content, start in iter_fenced_blocks(text):
        n = content.count("\n") + 1 if content else 0
        fenced.update(range(start - 1, start + n + 1))
    result = []
    for idx, line in enumerate(text.split("\n")):
        if idx in fenced:
            continue
        m = _HEADING_RE.match(line)
        if m:
            title = re.sub(r"[*_`]", "", m.group(2)).strip().rstrip(":").strip()
            result.append((idx, len(m.group(1)), title))
    return result


def _words(text: str) -> int:
    return len(re.findall(r"\S+", text))


def lint(text: str, *, allow_extra_sections: bool = False, mode: Optional[str] = None) -> LintResult:
    res = LintResult()
    text = text.replace("\r\n", "\n")
    lines = text.split("\n")
    heads = _headings(text)

    prompt_h = next((h for h in heads if h[2].lower() == PROMPT_HEADING), None)
    if prompt_h is None:
        res.errors.append("missing 'Reconstructed Prompt' heading")
        return res
    level = prompt_h[1]
    if level != 2:
        res.warnings.append(f"'Reconstructed Prompt' is a level-{level} heading; the contract uses level 2 (##)")
    reasoning_h = next(
        (h for h in heads if h[2].lower() == REASONING_HEADING and h[1] == level and h[0] > prompt_h[0]),
        None,
    )
    if reasoning_h is None:
        res.errors.append("missing 'Reasoning' heading at the same level after 'Reconstructed Prompt'")
        return res

    main = [h for h in heads if h[1] <= level]
    extras = [h[2] for h in main if h not in (prompt_h, reasoning_h)]
    if extras and not allow_extra_sections:
        res.errors.append("unexpected main section(s): " + ", ".join(repr(e) for e in extras))
    if main and main[0] != prompt_h:
        res.errors.append("'Reconstructed Prompt' must be the first main section")

    preamble = "\n".join(lines[: prompt_h[0]]).strip()
    if preamble:
        res.warnings.append("text before 'Reconstructed Prompt'; the contract starts with that heading")

    next_main_after_reasoning = next((h[0] for h in main if h[0] > reasoning_h[0]), len(lines))
    prompt_section = "\n".join(lines[prompt_h[0] + 1 : reasoning_h[0]])
    reasoning = "\n".join(lines[reasoning_h[0] + 1 : next_main_after_reasoning])

    # --- Reconstructed Prompt section --------------------------------------
    blocks = list(iter_fenced_blocks(prompt_section))
    if not blocks:
        res.errors.append("no fenced code block in 'Reconstructed Prompt'; the prompt must be in one block")
        prompt_text = ""
    else:
        if len(blocks) > 1:
            res.errors.append(f"{len(blocks)} fenced blocks in 'Reconstructed Prompt'; the contract requires exactly one")
        info, prompt_text, _ = blocks[0]
        if info.split()[:1] != ["text"]:
            res.warnings.append(f"prompt block is tagged '{info or '(none)'}'; the contract uses 'text'")
        if _words(prompt_text) < MIN_PROMPT_WORDS:
            res.errors.append(f"prompt block has fewer than {MIN_PROMPT_WORDS} words")
    outside = prompt_section
    for _info, content, _start in blocks:
        outside = outside.replace(content, "")
    prose = [ln for ln in outside.split("\n") if ln.strip() and not re.match(r"^\s*(`{3,}|~{3,})", ln)]
    if len(prose) > 1:
        res.warnings.append(f"{len(prose)} lines of prose in 'Reconstructed Prompt'; at most one short lead-in line is expected")

    # --- Placeholders --------------------------------------------------------
    if prompt_text.count("{{") != prompt_text.count("}}"):
        res.errors.append("unbalanced '{{' / '}}' in the prompt block")
    seen: List[str] = []
    for name in PLACEHOLDER_RE.findall(prompt_text):
        if not VALID_PLACEHOLDER_RE.match(name):
            res.errors.append(f"placeholder '{{{{{name}}}}}' is not UPPER_SNAKE_CASE")
        elif name not in seen:
            seen.append(name)
    res.placeholders = seen
    for name in seen:
        if "{{" + name + "}}" not in reasoning and name not in reasoning:
            res.warnings.append(f"placeholder {{{{{name}}}}} is not listed in Reasoning")

    # --- Reasoning -------------------------------------------------------------
    lower = reasoning.lower()
    missing = [label for label in REASONING_LABELS if label.lower() not in lower]
    if missing:
        res.warnings.append("Reasoning is missing label(s): " + ", ".join(missing))
    m = CONFIDENCE_RE.search(reasoning)
    if m:
        res.confidence = m.group(1).capitalize()
        sentence = re.split(r"(?<=[.!?])\s|\n", reasoning[m.start():], maxsplit=1)[0]
        levels = {lv.lower() for lv in re.findall(r"\b(high|moderate|medium|low)\b", sentence, re.I)}
        if len(levels) > 1:
            res.warnings.append("overall confidence is split across levels; state exactly one and explain nuance afterwards")
    else:
        res.errors.append("Reasoning does not state 'Overall confidence: High | Moderate | Low'")
    if _words(reasoning) > MAX_REASONING_WORDS:
        res.warnings.append(f"Reasoning is {_words(reasoning)} words; aim for concise (usually 120-350)")

    sub = [h for h in heads if reasoning_h[0] < h[0] < next_main_after_reasoning and h[1] > level]
    sub_titles = [h[2].lower() for h in sub]
    audit_present = any(t.startswith("requirement audit") for t in sub_titles)
    improvements_present = any(t.startswith("optional improvements") for t in sub_titles)
    if mode == "audit" and not audit_present:
        res.errors.append("audit mode: missing '### Requirement audit' inside Reasoning")
    if mode == "optimise" and not improvements_present:
        res.errors.append("optimise mode: missing '### Optional improvements (not evidence)' inside Reasoning")
    if audit_present:
        audit_idx = next(h[0] for h in sub if h[2].lower().startswith("requirement audit"))
        table_rows = [ln for ln in lines[audit_idx + 1 : next_main_after_reasoning] if ln.strip().startswith("|")]
        if len(table_rows) < 3:
            res.errors.append("'Requirement audit' must contain a table with at least one requirement row")
        else:
            header = [c.strip().lower() for c in table_rows[0].strip().strip("|").split("|")]
            if "status" not in header:
                res.errors.append("'Requirement audit' table needs a 'Status' column")
            else:
                col = header.index("status")
                for row in table_rows[2:]:
                    cells = [c.strip() for c in row.strip().strip("|").split("|")]
                    if col < len(cells) and cells[col].lower() not in AUDIT_STATUSES:
                        res.warnings.append(f"audit status '{cells[col]}' is not one of Followed, Partly, Missed, Not verifiable")

    # --- Prohibited claims (outside the prompt block) --------------------------
    scan = text.replace(prompt_text, "") if prompt_text else text
    for pattern, message in PROHIBITED_CLAIMS:
        hit = pattern.search(scan)
        if hit:
            res.errors.append(f"{message}: \"{hit.group(0)}\"")
    return res


def extract_examples(markdown: str) -> List[Tuple[str, str]]:
    """Return (example_id, response_text) for each '<!-- example-response: id -->' block."""
    out = []
    lines = markdown.split("\n")
    marker = re.compile(r"<!--\s*example-response:\s*([\w-]+)\s*-->")
    blocks = list(iter_fenced_blocks(markdown))
    for idx, line in enumerate(lines):
        m = marker.search(line)
        if not m:
            continue
        nxt = next((b for b in blocks if b[2] - 1 > idx), None)
        if nxt is None:
            out.append((m.group(1), ""))
        else:
            out.append((m.group(1), nxt[1]))
    return out


def _print(name: str, res: LintResult) -> None:
    status = "PASS" if res.ok else "FAIL"
    detail = f"confidence={res.confidence or '-'}, placeholders={len(res.placeholders)}"
    print(f"{status}  {name}  ({detail})")
    for e in res.errors:
        print(f"  error:   {e}")
    for w in res.warnings:
        print(f"  warning: {w}")


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("path", nargs="?", help="response file to lint, or '-' for stdin")
    ap.add_argument("--examples", metavar="FILE", help="lint every example response embedded in a Markdown file")
    ap.add_argument("--mode", choices=["audit", "optimise"], help="also require the mode-specific sub-section")
    ap.add_argument("--allow-extra-sections", action="store_true", help="permit main sections beyond the two-section contract")
    ap.add_argument("--strict", action="store_true", help="treat warnings as errors")
    ap.add_argument("--json", action="store_true", help="print machine-readable results")
    args = ap.parse_args(argv)

    if bool(args.path) == bool(args.examples):
        ap.error("give exactly one of PATH or --examples")

    targets: List[Tuple[str, str]] = []
    try:
        if args.examples:
            targets = extract_examples(Path(args.examples).read_text(encoding="utf-8"))
            if not targets:
                print(f"no '<!-- example-response: ... -->' blocks found in {args.examples}", file=sys.stderr)
                return 2
        elif args.path == "-":
            targets = [("<stdin>", sys.stdin.read())]
        else:
            targets = [(args.path, Path(args.path).read_text(encoding="utf-8"))]
    except OSError as exc:
        print(f"cannot read input: {exc}", file=sys.stderr)
        return 2

    results = []
    failed = False
    for name, text in targets:
        res = lint(text, allow_extra_sections=args.allow_extra_sections, mode=args.mode)
        if args.strict and res.warnings:
            res.errors.extend(f"(strict) {w}" for w in res.warnings)
            res.warnings = []
        failed |= not res.ok
        results.append((name, res))

    if args.json:
        print(json.dumps({name: r.as_dict() for name, r in results}, indent=2, ensure_ascii=False))
    else:
        for name, res in results:
            _print(name, res)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
