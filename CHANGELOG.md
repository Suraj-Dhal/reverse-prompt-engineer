# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html). For this plugin, the **public API** is the response contract (two sections, one fenced prompt block, five Reasoning labels, a single overall confidence level) and the skill's name: a breaking change to either means a new major version.

## [Unreleased]

## [1.0.0] - 2026-10-28

First stable release, following a full engineering review of v0.2.0. Every finding and its resolution is listed in [docs/review-v0.2.0.md](docs/review-v0.2.0.md).

### Added

- **Claude Code support:** `.claude-plugin/plugin.json` and a single-plugin `.claude-plugin/marketplace.json`, so the plugin installs with one command. Codex reads the same marketplace file (verified with `codex plugin add`).
- **Modes table** in `SKILL.md` with a deterministic placement for each mode: single output, shared prompt for several outputs, master prompt from conversation, requirements audit, reconstruction plus optimisation, and hidden-prompt requests.
- **Reference map** in `SKILL.md` that says when to load each playbook and asset (progressive disclosure).
- **Deterministic response contract:** one fenced `text` prompt block, `{{UPPER_SNAKE_CASE}}` placeholders, five labelled Reasoning items, and a single `Overall confidence: High | Moderate | Low`.
- Language rule (the prompt follows the target's language; Reasoning follows the user's), a low-evidence procedure with an example, and an "absence is weak evidence" rule.
- `references/worked-examples.md` with three complete examples (writing, code, audit mode), linted in CI.
- `assets/prompt-skeleton.md`, the canonical section order for reconstructed prompts.
- `domain-routing.md` sections for system-prompt-like targets and for multilingual and code-mixed targets.
- **Runnable behavioural evals:** every fixture now has a concrete `prompt`; `scripts/build_evals.py` compiles the fixtures into a native `claude plugin eval` suite (65 cases) with skill-activation, contract, confidence, no-exact-claim, case-specific regex and LLM-rubric graders.
- 9 new behavioural cases (B17–B25): two plausible source documents, conflicting numbers and units, an inaccessible URL, a design screenshot without code, multi-output with incompatible formats, a heavily edited output, audit mode, a non-English target, and an unsafe (phishing) objective.
- 16 new trigger cases (T25–T40), including near misses (AI-text detection, model attribution, prompt debugging, prompt writing) and Hinglish phrasing.
- JSON Schemas for both fixture files.
- `scripts/lint_response.py`, a response-contract linter for saved outputs.
- `scripts/package.py`, reproducible plugin and skill-upload ZIPs with SHA-256 checksums.
- `scripts/bump_version.py`, which sets a new version everywhere it is recorded in one step.
- Unit tests (standard-library `unittest`), including regressions for each v0.2.0 validator bug.
- GitHub Actions: CI (validation, tests, `claude plugin validate --strict`, packaging) on Linux and Windows; a release-on-version-bump workflow that creates the tags and the GitHub release (and back-fills the v0.2.0 baseline); a manually triggered live-eval workflow.
- MIT `LICENSE`; the documentation set (`docs/`: how it works, installation, usage, evaluation, licensing, review); `CONTRIBUTING.md`; `SECURITY.md`; issue and PR templates; an original icon.

### Changed

- The skill `description` was rewritten for activation accuracy: it covers hidden or system prompt requests and requests made before the output is pasted, and lists the near misses to avoid. Both gaps were found by the first live smoke run.
- `reconstruction-workflow.md` was rewritten as advanced procedures (multi-output, long context, edited outputs, audit mode, low evidence) instead of duplicating `SKILL.md`.
- Fixture B14's expected output now matches the new optimisation-mode rule. The B01 and B16 rubrics now state that labelled inference is allowed, matching the skill's evidence model.
- Audit mode keeps the user's wording; strengthening a requirement is listed as an optional improvement (found by live eval B23).
- The exact-recovery check (linter and eval grader) no longer flags "your original prompt", which is true in audit mode; B21's discount grader accepts any form of `30`.
- The eval fixtures and the validator moved out of the runtime skill folder (to `evals/` and `scripts/`), so installs and skill uploads contain only runtime files.
- The author name is normalised to "Suraj Dhal" across all manifests.

### Fixed

- Four of the five reference playbooks were never linked from `SKILL.md`, so agents never loaded them.
- The Codex `defaultPrompt` was a single 211-character string; Codex allows at most three starter prompts of 128 characters each.
- Validator: errors were joined with a literal `\n`; a missing manifest crashed with a traceback; links inside code fences were not ignored despite the comment saying so; the Codex manifest was never validated; manifest versions could drift.

## [0.2.0]

Original package as first authored: skill, five reference playbooks, the requirement matrix template, 24 trigger and 16 behavioural fixtures, and a structural validation script. Preserved unchanged at tag `v0.2.0`.

[Unreleased]: https://github.com/Suraj-Dhal/reverse-prompt-engineer/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/Suraj-Dhal/reverse-prompt-engineer/compare/v0.2.0...v1.0.0
[0.2.0]: https://github.com/Suraj-Dhal/reverse-prompt-engineer/releases/tag/v0.2.0
