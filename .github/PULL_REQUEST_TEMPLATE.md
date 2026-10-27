## What and why

<!-- What does this change, and what problem does it solve? Link issues: "Fixes #123". -->

## Type of change

- [ ] Skill behaviour (`SKILL.md`, `references/`, `assets/`)
- [ ] Eval fixtures / graders
- [ ] Tooling (`scripts/`, `tests/`, workflows)
- [ ] Manifests / listing metadata
- [ ] Documentation only
- [ ] **Breaking:** changes the response contract or the skill name (needs a major version)

## Checklist

- [ ] `python3 scripts/validate.py` passes
- [ ] `python3 -m unittest discover -s tests` passes
- [ ] Fixtures changed → ran `python3 scripts/build_evals.py` and committed the generated suite
- [ ] New `references/` or `assets/` files are linked from the Reference map in `SKILL.md`
- [ ] Behaviour changed → added or updated an eval case that would have caught the old behaviour
- [ ] `CHANGELOG.md` updated under `[Unreleased]`
- [ ] Examples and fixtures use synthetic data only

## Live eval results (for behaviour changes)

<!-- e.g. `claude plugin eval . --case 'B12*' --runs 3 --ablation none` → 1.00 (3/3). Paste the summary table. -->
