# Engineering review of v0.2.0

This is the review that led to v1.0.0. It records what v0.2.0 did well, every defect or gap that was found, and how v1.0.0 resolves each one. The original package is preserved unchanged at git tag [`v0.2.0`](https://github.com/Suraj-Dhal/reverse-prompt-engineer/tree/v0.2.0), so every finding below can be checked against the source.

Severity scale: **High** (the plugin misbehaves or a promise in its docs is false), **Medium** (it works but is fragile, unmaintainable or untestable), **Low** (polish, consistency, hygiene).

## What v0.2.0 got right

These design decisions were sound and are kept in v1.0.0:

- **Honest capability boundaries.** The skill never claims to recover an exact historical prompt or a hidden system prompt, and says so up front.
- **Evidence classes** (explicit, observed, strong inference, weak inference, unknown, conflict) and a **source precedence ladder**. Together they make the reasoning auditable.
- **Prompt-injection stance.** Target material is treated as data, not instructions.
- **A fixed two-section output contract** (`Reconstructed Prompt`, `Reasoning`) that users can rely on.
- **An evaluation-first mindset.** Trigger and behavioural fixtures existed before any live testing, and the README was careful not to over-claim what they proved.

## Findings

| ID | Severity | Finding | Evidence in v0.2.0 | Resolution in v1.0.0 |
|---|---|---|---|---|
| H1 | High | Four of the five reference playbooks are never referenced from `SKILL.md`. Agent hosts load skill files progressively, following only links in `SKILL.md`, so most of the package's depth was never loaded. | `SKILL.md` mentions only `references/domain-routing.md` and the matrix template. `context-preservation.md`, `evidence-and-uncertainty.md`, `reconstruction-workflow.md` and `safety-and-trust-boundaries.md` are orphaned. | `SKILL.md` has a **Reference map** that says when to load each file. The validator now fails the build if any file under `references/` or `assets/` is not linked from `SKILL.md`. |
| H2 | High | The Codex `defaultPrompt` is one 211-character string. Codex shows at most three starter prompts of at most 128 characters each, so the prompt was truncated. | `.codex-plugin/plugin.json` → `interface.defaultPrompt` | Replaced with three short starter prompts. The validator enforces the listing limits (displayName/shortDescription ≤ 30, longDescription ≤ 4000, developerName ≤ 80, defaultPrompt ≤ 3 × 128, capabilities ≤ 20 × 120). |
| H3 | High | The output contract contradicts the modes the skill advertises. It mandates "exactly one prompt" and "no third section", yet the skill offers a requirements audit (T06), reconstruction plus optimisation (B14) and multi-output reconstruction, and never says where an audit, improvements or extra prompts go. Fixture B14's own expected output is ambiguous ("described separately within allowed structure or incorporated only if…"). | `SKILL.md` "Default response contract"; `reconstruction-evals.json` B14 | A **Modes** table gives each mode a single, deterministic placement inside the two-section contract (audit table and optional improvements go under `Reasoning`; an optimised variant appears only when explicitly requested and is labelled as not a reconstruction). B14 is rewritten to match. |
| H4 | High | The structural validator has three bugs and two blind spots. (a) With more than one error, `"\\n".join(...)` prints a literal `\n` and joins all errors onto one line. (b) A missing manifest crashes with a `FileNotFoundError` traceback instead of reporting. (c) The comment says links inside code fences are ignored, but they are not. It never reads `.codex-plugin/plugin.json`, and it never checks that the two manifests agree, so the versions could silently drift apart. | `skills/reverse-prompt-engineer/tests/validate_package.py`. Bugs (a) and (b) reproduced by deleting two required files, then a manifest. | Rewritten as `scripts/validate.py`: errors are collected and reported per check, nothing crashes, fenced and inline code are skipped, all four manifests are read, and identity fields (name, version, description, author, license, URLs) must match everywhere. Unit tests reproduce each original bug. |
| M1 | Medium | No licence. Code published without a licence is "all rights reserved" by default, so nobody may legally reuse it, which defeats the point of a shareable plugin. The manifests have no `license`, `homepage` or `repository` fields. | No `LICENSE` file | MIT `LICENSE`; `license`, `homepage` and `repository` set in every manifest; [licensing guide](licensing.md). |
| M2 | Medium | The behavioural fixtures describe scenarios but contain no runnable input (for example, "Here is a short, generic paragraph" with no paragraph), so no harness can execute them and there is no live evidence at all. | `reconstruction-evals.json` | Every behavioural case now has a concrete, self-contained `prompt` with synthetic target material. `scripts/build_evals.py` compiles the fixtures into a native `claude plugin eval` suite with deterministic and judge-scored graders. |
| M3 | Medium | No Claude Code distribution path. Claude Code can load the standard layout without a manifest, but there was no `.claude-plugin/plugin.json` metadata and no marketplace, so it could not be installed with one command. | No `.claude-plugin/` directory | `.claude-plugin/plugin.json` plus a single-plugin `.claude-plugin/marketplace.json`, checked with `claude plugin validate --strict` in CI. |
| M4 | Medium | The response format is not machine-checkable. There is no rule for how the prompt is delimited, how placeholders are written, or how confidence is stated, so the "copy-ready" promise cannot be tested. | `SKILL.md` | The prompt goes in one fenced `text` block; placeholders are `{{UPPER_SNAKE_CASE}}`; Reasoning uses five fixed labels and an overall confidence of High, Moderate or Low. `scripts/lint_response.py` checks a saved response against the contract. |
| M5 | Medium | Duplication. `reconstruction-workflow.md` restates the `SKILL.md` phases almost line for line, which wastes context and lets the two drift apart. | `references/reconstruction-workflow.md` | Rewritten as advanced procedures that `SKILL.md` does not cover (multi-output analysis, long-conversation compression, edited or post-processed output, audit mode). |
| M6 | Medium | Development artefacts ship inside the runtime skill folder, so every install and skill upload carries test code and fixtures. | `skills/reverse-prompt-engineer/tests/`, `.../evals/` | Moved to the repository root (`scripts/`, `tests/`, `evals/`). The skill folder now holds only `SKILL.md`, `references/` and `assets/`. |
| L1 | Low | No rule for non-English targets or users. | — | Language rule: the prompt is written to reproduce the target's language and Reasoning uses the user's language. Covered by fixture B24 and trigger T26. |
| L2 | Low | No worked examples, although the Agent Skills specification recommends input and output examples. | — | `references/worked-examples.md` holds three complete examples; CI lints each one against the contract. |
| L3 | Low | Inconsistencies: the README hard-codes the version, and the author name is "SURAJ DHAL" in the manifests but "Suraj Dhal" on GitHub. | `README.md`, manifests | The version lives only in machine-checked places. The author name is normalised to "Suraj Dhal". |
| L4 | Low | No changelog, contribution guide, security policy, CI or `.gitignore`. | — | All added, plus issue and PR templates. |
| L5 | Low | The "recommended regression additions" listed in the eval README were never implemented. | `evals/README.md` | All six are implemented as B17–B22, plus audit mode (B23), a non-English target (B24) and an unsafe objective (B25). |
| L6 | Low | The trigger set lacks near-miss negatives (AI-text detection, model attribution, prompt debugging, prompt writing from scratch) and non-English phrasing. | `trigger-evals.json` | 16 new trigger cases (T25–T40), keeping the positive and negative sets balanced at 20 each. |

## Verification of the original

The original package was checked before any changes:

- Its own validator: `PASS: structural validation, 24 trigger cases, 16 behavioral fixtures.`
- `claude plugin validate` (Claude Code 2.1.311): `Validation passed`.

Both passed, which illustrates why H1–H4 matter: every one of these defects sits outside what either check looks at.
