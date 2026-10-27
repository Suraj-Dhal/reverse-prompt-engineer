"""Tests for scripts/build_evals.py (fixtures -> claude plugin eval suite)."""
from __future__ import annotations

import json
import re
import unittest

from _support import ROOT, RepoCopyTestCase

import build_evals  # noqa: E402

PROMPT_MD_KEYS = {
    "schema_version", "name", "description", "tags", "plugins", "runs", "expected_outcome",
    "model", "max_turns", "timeout_seconds", "allowed_tools", "append_system_prompt", "env",
}
GRADER_KEYS = {
    "type", "weight", "arm", "pattern", "flags", "match", "target", "tool", "input_match",
    "min", "max", "before", "after", "path", "exists", "criteria", "focus", "baseline_file",
}


def frontmatter_keys(text):
    assert text.startswith("---\n"), text[:40]
    block = text[4 : text.index("\n---\n", 4)]
    return [ln.split(":", 1)[0] for ln in block.splitlines() if ln and not ln.startswith("#")]


class GeneratedSuite(unittest.TestCase):
    def test_committed_suite_matches_fixtures(self):
        self.assertEqual(build_evals.check(ROOT), [])

    def test_build_is_deterministic(self):
        self.assertEqual(build_evals.build(ROOT), build_evals.build(ROOT))

    def test_case_counts(self):
        files = build_evals.build(ROOT)
        trig = json.loads((ROOT / "evals/fixtures/trigger-evals.json").read_text(encoding="utf-8"))
        beh = json.loads((ROOT / "evals/fixtures/reconstruction-evals.json").read_text(encoding="utf-8"))
        prompts = [p for p in files if p.name == "prompt.md"]
        self.assertEqual(len(prompts), len(trig) + len(beh))

    def test_frontmatter_uses_only_known_keys(self):
        for path, content in build_evals.build(ROOT).items():
            keys = set(frontmatter_keys(content))
            allowed = PROMPT_MD_KEYS if path.name == "prompt.md" else GRADER_KEYS
            self.assertTrue(keys <= allowed, f"{path}: unknown keys {keys - allowed}")

    def test_every_case_checks_skill_activation_unless_opted_out(self):
        files = build_evals.build(ROOT)
        beh = json.loads((ROOT / "evals/fixtures/reconstruction-evals.json").read_text(encoding="utf-8"))
        opted_out = {c["id"] for c in beh if c.get("require_skill") is False}
        for prompt in (p for p in files if p.name == "prompt.md"):
            graders = {p.name for p in files if p.parent == prompt.parent / "graders"}
            case_id = prompt.parent.name.split("-", 1)[0]
            if case_id in opted_out:
                self.assertNotIn("skill-fired.md", graders)
                self.assertTrue(graders - {"no-exact-recovery-claim.md"}, f"{prompt}: needs its own graders")
            else:
                self.assertTrue({"skill-fired.md", "skill-not-fired.md"} & graders, prompt)

    def test_every_behaviour_case_has_a_judge_or_custom_graders(self):
        files = build_evals.build(ROOT)
        for prompt in (p for p in files if p.name == "prompt.md" and "behavior" in p.parts):
            graders = {p.name for p in files if p.parent == prompt.parent / "graders"}
            standard = {"skill-fired.md", "no-exact-recovery-claim.md", "contract-sections.md", "confidence-stated.md"}
            self.assertTrue("rubric.md" in graders or graders - standard, prompt)

    def test_negative_triggers_score_in_both_arms(self):
        files = build_evals.build(ROOT)
        neg = [c for p, c in files.items() if p.name == "skill-not-fired.md"]
        self.assertEqual(len(neg), 20)
        for content in neg:
            self.assertIn("min: 0", content)
            self.assertIn("max: 0", content)
            self.assertIn("arm: both", content)

    def test_regex_patterns_compile(self):
        for path, content in build_evals.build(ROOT).items():
            m = re.search(r"^pattern: '(.*)'$", content, re.M)
            if m:
                re.compile(m.group(1).replace("''", "'"))

    def test_skill_input_match_accepts_namespaced_and_bare_names(self):
        pat = re.compile(build_evals.SKILL_INPUT_MATCH)
        self.assertTrue(pat.search('{"skill": "reverse-prompt-engineer"}'))
        self.assertTrue(pat.search('{"skill":"reverse-prompt-engineer:reverse-prompt-engineer"}'))
        self.assertFalse(pat.search('{"skill": "reverse-prompt-engineer-extra"}'))


class StaleCases(RepoCopyTestCase):
    def test_stale_generated_case_is_detected_and_removed(self):
        stale = self.repo / "evals/trigger/T99-old-case"
        stale.mkdir(parents=True)
        (stale / "prompt.md").write_text(f"---\n# {build_evals.MARKER} from x.\n---\n\nold\n", encoding="utf-8")
        self.assertTrue(any("stale case" in p for p in build_evals.check(self.repo)))
        build_evals.write(self.repo)
        self.assertFalse(stale.exists())
        self.assertEqual(build_evals.check(self.repo), [])

    def test_hand_written_cases_are_left_alone(self):
        manual = self.repo / "evals/behavior/manual-case"
        manual.mkdir(parents=True)
        (manual / "prompt.md").write_text("---\nmax_turns: 5\n---\n\nhello\n", encoding="utf-8")
        build_evals.write(self.repo)
        self.assertTrue(manual.exists())


if __name__ == "__main__":
    unittest.main()
