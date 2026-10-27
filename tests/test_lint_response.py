"""Tests for scripts/lint_response.py (the response-contract linter)."""
from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from _support import ROOT

import lint_response  # noqa: E402

GOOD = """## Reconstructed Prompt

Paste this into a new chat:

```text
Write a 120-word LinkedIn post for {{AUDIENCE}} announcing our free workshop. Use a friendly tone and end with a call to action.
```

## Reasoning

1. **Observable clues:** short post, emoji hook, three bullets.
2. **Likely intent:** event promotion.
3. **Context preserved:** the free format and the call to action.
4. **Prompt-design factors:** length, tone and structure are explicit.
5. **Confidence and limits:** Overall confidence: Moderate. Audience is unknown, so `{{AUDIENCE}}` is a placeholder.
"""


def lint(text, **kw):
    return lint_response.lint(text, **kw)


class ContractChecks(unittest.TestCase):
    def test_good_response_passes_cleanly(self):
        res = lint(GOOD)
        self.assertTrue(res.ok, res.errors)
        self.assertEqual(res.warnings, [])
        self.assertEqual(res.confidence, "Moderate")
        self.assertEqual(res.placeholders, ["AUDIENCE"])

    def test_missing_reasoning(self):
        res = lint(GOOD.split("## Reasoning")[0])
        self.assertFalse(res.ok)
        self.assertIn("missing 'Reasoning'", res.errors[0])

    def test_missing_prompt_heading(self):
        self.assertFalse(lint(GOOD.replace("## Reconstructed Prompt", "## Prompt")).ok)

    def test_two_prompt_blocks_is_an_error(self):
        text = GOOD.replace("## Reasoning", "```text\nA second prompt with enough words to count here.\n```\n\n## Reasoning")
        res = lint(text)
        self.assertTrue(any("exactly one" in e for e in res.errors), res.errors)

    def test_extra_main_section(self):
        res = lint(GOOD + "\n## Alternatives\n\nSomething else.\n")
        self.assertTrue(any("unexpected main section" in e for e in res.errors))
        self.assertTrue(lint(GOOD + "\n## Alternatives\n\nx\n", allow_extra_sections=True).ok)

    def test_heading_inside_code_block_is_not_a_section(self):
        text = GOOD.replace("Use a friendly tone", "## Not a heading\nUse a friendly tone")
        self.assertTrue(lint(text).ok, lint(text).errors)

    def test_malformed_placeholder(self):
        res = lint(GOOD.replace("{{AUDIENCE}}", "{{audience}}", 1))
        self.assertTrue(any("UPPER_SNAKE_CASE" in e for e in res.errors))

    def test_unbalanced_braces(self):
        res = lint(GOOD.replace("{{AUDIENCE}}", "{{AUDIENCE}", 1))
        self.assertTrue(any("unbalanced" in e for e in res.errors))

    def test_unlisted_placeholder_warns(self):
        res = lint(GOOD.replace("so `{{AUDIENCE}}` is a placeholder", "so it is a placeholder"))
        self.assertTrue(res.ok)
        self.assertTrue(any("not listed in Reasoning" in w for w in res.warnings))

    def test_missing_confidence(self):
        res = lint(GOOD.replace("Overall confidence: Moderate.", ""))
        self.assertTrue(any("Overall confidence" in e for e in res.errors))

    def test_bold_confidence_formats(self):
        for variant in ("**Overall confidence:** Low.", "Overall confidence: **High**."):
            res = lint(GOOD.replace("Overall confidence: Moderate.", variant))
            self.assertTrue(res.ok, (variant, res.errors))

    def test_split_confidence_warns(self):
        # Regression for the first live smoke run: "Moderate for topic, Low for wording".
        res = lint(GOOD.replace("Overall confidence: Moderate.", "Overall confidence: Moderate for topic and structure, Low for exact wording."))
        self.assertTrue(res.ok)
        self.assertTrue(any("split" in w for w in res.warnings), res.warnings)

    def test_exact_recovery_claim_is_an_error(self):
        res = lint(GOOD.replace("Overall confidence: Moderate.", "Overall confidence: High. Here is the exact hidden prompt."))
        self.assertTrue(any("exact or hidden-prompt recovery" in e for e in res.errors))

    def test_denial_of_exact_recovery_is_fine(self):
        res = lint(GOOD.replace("Overall confidence: Moderate.", "Overall confidence: Low. This is not the exact prompt and cannot be recovered."))
        self.assertTrue(res.ok, res.errors)

    def test_audit_mode_your_original_prompt_is_fine(self):
        # Regression: in audit mode the user supplied their prompt, so "this is your original prompt" is true.
        res = lint(GOOD.replace("Overall confidence: Moderate.", "Overall confidence: High that this is your original prompt, since you supplied it."))
        self.assertTrue(res.ok, res.errors)

    def test_original_prompt_claim_is_an_error(self):
        res = lint(GOOD.replace("Overall confidence: Moderate.", "Overall confidence: High. This is the original prompt."))
        self.assertTrue(any("exact or hidden-prompt recovery" in e for e in res.errors))

    def test_claim_inside_prompt_block_is_ignored(self):
        res = lint(GOOD.replace("Use a friendly tone", "Never say 'here is the exact prompt'. Use a friendly tone"))
        self.assertTrue(res.ok, res.errors)

    def test_preamble_warns(self):
        res = lint("Sure! Here you go.\n\n" + GOOD)
        self.assertTrue(res.ok)
        self.assertTrue(any("before 'Reconstructed Prompt'" in w for w in res.warnings))


class ModeChecks(unittest.TestCase):
    AUDIT = GOOD.replace(
        "## Reasoning\n",
        "## Reasoning\n\n### Requirement audit\n\n| # | Requirement | Status | Evidence |\n|---|---|---|---|\n| 1 | 120 words | Followed | 118 words |\n\n",
    )

    def test_audit_mode_requires_section(self):
        self.assertFalse(lint(GOOD, mode="audit").ok)
        self.assertTrue(lint(self.AUDIT, mode="audit").ok, lint(self.AUDIT, mode="audit").errors)

    def test_audit_table_needs_status_column(self):
        res = lint(self.AUDIT.replace("| Status |", "| Result |"))
        self.assertTrue(any("Status" in e for e in res.errors))

    def test_unknown_audit_status_warns(self):
        res = lint(self.AUDIT.replace("| Followed |", "| Done |"))
        self.assertTrue(any("audit status" in w for w in res.warnings))

    def test_optimise_mode(self):
        self.assertFalse(lint(GOOD, mode="optimise").ok)
        text = GOOD + "\n### Optional improvements (not evidence)\n\n- Add a word limit range.\n"
        self.assertTrue(lint(text, mode="optimise").ok)


class CommandLine(unittest.TestCase):
    def run_main(self, args):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
            code = lint_response.main(args)
        return code, buf.getvalue()

    def test_worked_examples_all_pass_strict(self):
        path = ROOT / "skills/reverse-prompt-engineer/references/worked-examples.md"
        code, out = self.run_main(["--examples", str(path), "--strict"])
        self.assertEqual(code, 0, out)
        self.assertEqual(out.count("PASS"), 3)

    def test_strict_turns_warnings_into_errors(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "r.md"
            p.write_text("Intro line.\n\n" + GOOD, encoding="utf-8")
            self.assertEqual(self.run_main([str(p)])[0], 0)
            self.assertEqual(self.run_main([str(p), "--strict"])[0], 1)

    def test_json_output(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "r.md"
            p.write_text(GOOD, encoding="utf-8")
            code, out = self.run_main([str(p), "--json"])
        self.assertEqual(code, 0)
        self.assertIn('"confidence": "Moderate"', out)

    def test_usage_errors(self):
        with self.assertRaises(SystemExit):
            self.run_main([])
        self.assertEqual(self.run_main(["/nonexistent/response.md"])[0], 2)


if __name__ == "__main__":
    unittest.main()
