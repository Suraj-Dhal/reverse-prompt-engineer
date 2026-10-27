"""Tests for scripts/validate.py, including regressions for every v0.2.0 validator defect."""
from __future__ import annotations

import contextlib
import io
import re
import unittest

from _support import ROOT, SKILL, RepoCopyTestCase

import validate  # noqa: E402

ORIGINAL_DEFAULT_PROMPT = (
    "Reconstruct one plausible, copy-ready user-level prompt from this output and its relevant context. "
    "Preserve material requirements and scenario logic, distinguish evidence from inference, and explain uncertainty."
)


def errors_of(root):
    report = validate.Validator(root).run()
    return [msg for _title, errs, _warns in report.sections for msg in errs]


class RepositoryIsValid(unittest.TestCase):
    def test_current_repository_passes(self):
        errs = errors_of(ROOT)
        self.assertEqual(errs, [], "validator errors:\n" + "\n".join(errs))


class DetectsDefects(RepoCopyTestCase):
    def assertError(self, fragment):
        errs = errors_of(self.repo)
        self.assertTrue(any(fragment in e for e in errs), f"expected an error containing {fragment!r}; got:\n" + "\n".join(errs))

    # H1 -----------------------------------------------------------------------
    def test_orphaned_reference_file_is_an_error(self):
        text = re.sub(r"\[([^\]]*)\]\(references/context-preservation\.md\)", r"\1", self.read(SKILL))
        self.assertNotIn("references/context-preservation.md)", text)
        self.write(SKILL, text)
        self.assertError("context-preservation.md is never linked")

    def test_link_in_code_does_not_count_as_wiring(self):
        text = re.sub(r"\[([^\]]*)\]\(references/context-preservation\.md\)", r"`[\1](references/context-preservation.md)`", self.read(SKILL))
        self.write(SKILL, text)
        self.assertError("context-preservation.md is never linked")

    # H2 -----------------------------------------------------------------------
    def test_v020_default_prompt_is_rejected(self):
        self.edit_json(".codex-plugin/plugin.json", lambda d: d["interface"].__setitem__("defaultPrompt", ORIGINAL_DEFAULT_PROMPT))
        self.assertError("defaultPrompt entries must be strings of at most 128 characters")

    def test_short_description_limit(self):
        self.edit_json(".codex-plugin/plugin.json", lambda d: d["interface"].__setitem__("shortDescription", "x" * 31))
        self.assertError("shortDescription exceeds 30 characters")

    def test_low_contrast_brand_color(self):
        self.edit_json(".codex-plugin/plugin.json", lambda d: d["interface"].__setitem__("brandColor", "#FFFF66"))
        self.assertError("brandColor contrast")

    # H4: drift, crash, newline bug, code fences ---------------------------------
    def test_version_drift_between_manifests(self):
        self.edit_json(".codex-plugin/plugin.json", lambda d: d.__setitem__("version", "9.9.9"))
        self.assertError("'version' differs from plugin.json")

    def test_skill_metadata_version_drift(self):
        self.write(SKILL, self.read(SKILL).replace('version: "1.0.0"', 'version: "0.9.0"'))
        self.assertError("metadata.version")

    def test_missing_manifest_is_reported_not_a_crash(self):
        (self.repo / "plugin.json").unlink()
        errs = errors_of(self.repo)  # must not raise
        self.assertTrue(any("plugin.json" in e and "missing" in e for e in errs))
        self.assertFalse(any("check crashed" in e for e in errs), errs)

    def test_multiple_errors_print_on_separate_lines(self):
        (self.repo / "SECURITY.md").unlink()
        (self.repo / "CONTRIBUTING.md").unlink()
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = validate.main(["--root", str(self.repo)])
        out = buf.getvalue()
        self.assertEqual(code, 1)
        self.assertNotIn("\\n", out)
        self.assertIn("required file missing: SECURITY.md\n", out)
        self.assertIn("required file missing: CONTRIBUTING.md\n", out)

    def test_links_inside_code_are_ignored_but_real_links_checked(self):
        self.write("docs/scratch.md", "```md\n[broken](nope.md)\n```\n\nInline `[also](nope.md)` is fine.\n")
        self.assertEqual([e for e in errors_of(self.repo) if "scratch.md" in e], [])
        self.write("docs/scratch.md", "A real [broken link](nope.md).\n")
        self.assertError("docs/scratch.md: broken relative link 'nope.md'")

    # M6 -----------------------------------------------------------------------
    def test_dev_artefacts_inside_skill_folder(self):
        self.write("skills/reverse-prompt-engineer/tests/test_x.py", "pass\n")
        self.assertError("skill folder contains 'tests'")

    # Misc ---------------------------------------------------------------------
    def test_license_holder_must_match_author(self):
        self.write("LICENSE", self.read("LICENSE").replace("Suraj Dhal", "Someone Else"))
        self.assertError("copyright holder")

    def test_unbalanced_trigger_set(self):
        self.edit_json(
            "evals/fixtures/trigger-evals.json",
            lambda cases: [c.__setitem__("expected_trigger", True) for c in cases],
        )
        self.assertError("unbalanced")

    def test_generated_suite_drift(self):
        self.edit_json(
            "evals/fixtures/reconstruction-evals.json",
            lambda cases: cases[0].__setitem__("title", "Renamed case"),
        )
        self.assertError("generated eval suite is out of date")

    def test_skill_description_length(self):
        text = self.read(SKILL)
        start = text.index("description: ") + len("description: ")
        end = text.index("\n", start)
        self.write(SKILL, text[:start] + "x" * 1025 + text[end:])
        self.assertError("description must be 1-1024 characters")

    def test_changelog_version_mismatch(self):
        self.write("CHANGELOG.md", self.read("CHANGELOG.md").replace("## [1.0.0]", "## [1.0.1]", 1))
        self.assertError("CHANGELOG.md: latest released version")


if __name__ == "__main__":
    unittest.main()
