# Contributing

Thanks for helping improve Reverse Prompt Engineer. This guide covers setup, the change workflow, conventions, and how releases are made.

## Ground rules

- **The response contract is the public API.** Changing the two sections, the single prompt block, the placeholder format, the five Reasoning labels or the confidence statement is a breaking change and needs a major version (see [CHANGELOG.md](CHANGELOG.md)).
- **Behaviour changes come with evals.** If you change what the skill does, add or update a fixture that would have caught the old behaviour.
- **Honesty over polish.** Never weaken a boundary (no exact-prompt claims, no fabrication, injection resistance, privacy, safety) to make a case pass.
- **Synthetic data only.** Fixtures and examples use fictional names, firms and figures, never real personal data.

## Setup

You need Python 3.9 or later. Everything uses the standard library; `jsonschema` is optional, for the schema tests.

```bash
git clone https://github.com/Suraj-Dhal/reverse-prompt-engineer.git
cd reverse-prompt-engineer
python3 -m pip install jsonschema        # optional
```

For behavioural evals and the official validator you also need [Claude Code](https://code.claude.com) 2.1.269 or later.

## Everyday commands

| Task | Command |
|---|---|
| Structural validation | `python3 scripts/validate.py` |
| Unit tests | `python3 -m unittest discover -s tests` |
| Regenerate the eval suite after editing fixtures | `python3 scripts/build_evals.py` |
| Lint a saved response | `python3 scripts/lint_response.py response.md` |
| Official Claude Code validation | `claude plugin validate . --strict` |
| Quick live check (costs a little) | `claude plugin eval . --tag smoke --runs 1 --ablation none` |
| Build release ZIPs | `python3 scripts/package.py` |

## Making a change

1. Create a branch: `git switch -c fix/short-description`.
2. Make the change. Typical touch points:
   - Runtime behaviour → `skills/reverse-prompt-engineer/SKILL.md` and/or `references/`. Every new file under `references/` or `assets/` must be linked from the **Reference map** in `SKILL.md`, or the validator fails.
   - New or changed expectations → `evals/fixtures/*.json`, then `python3 scripts/build_evals.py`.
   - Format rules → `scripts/lint_response.py`, its tests, and `references/worked-examples.md`.
   - Listing metadata → update **all** manifests (`plugin.json`, `.codex-plugin/plugin.json`, `.claude-plugin/*.json`); the validator checks that they agree.
3. Run `python3 scripts/validate.py` and `python3 -m unittest discover -s tests`. Both must pass.
4. For behaviour changes, run the affected live cases and note the scores in your PR.
5. Add a line under `## [Unreleased]` in `CHANGELOG.md`.
6. Open a pull request using the template.

## Writing style for skill files

- Imperative, specific, testable: "List every placeholder under Confidence and limits", not "Be clear about placeholders".
- Prefer one precise rule over three vague ones. Every line in `SKILL.md` costs context on every activation.
- Keep `SKILL.md` under 500 lines; move depth into `references/` and link it from the Reference map.
- Examples must not be copies of eval cases (that teaches to the test).

## Commit messages

Use the imperative mood with a short summary line: `Add audit-mode table check to linter`. Reference issues where relevant (`Fixes #12`).

## Releasing (maintainers)

1. `python3 scripts/bump_version.py X.Y.Z`. This updates every manifest and the `SKILL.md` metadata, and turns `[Unreleased]` into a dated section.
2. Edit the new CHANGELOG section and add the compare link.
3. `python3 scripts/validate.py && python3 -m unittest discover -s tests && claude plugin validate . --strict`
4. Commit (`Release vX.Y.Z`) and push to `main`, through a pull request or directly.
5. The **Release** workflow notices that `plugin.json` has a version with no tag yet. It validates and tests the commit, creates the annotated tags `vX.Y.Z` and `reverse-prompt-engineer--vX.Y.Z` (Claude Code's plugin release tag, used for dependency version ranges), builds the ZIPs and checksums, and publishes the GitHub release with the CHANGELOG notes. Pushing a `vX.Y.Z` tag yourself also works; the workflow is idempotent.

## Licence of contributions

By submitting a contribution, you agree that it is licensed under the project's [MIT License](LICENSE) ("inbound = outbound"), and you confirm that you have the right to license it.

## Code of conduct

Be kind, assume good faith, and keep discussion about the work. Harassment or discrimination is not tolerated; the maintainer may remove content or contributors that break this rule.
