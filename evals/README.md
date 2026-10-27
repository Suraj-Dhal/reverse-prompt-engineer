# Evaluation fixtures and scoring

These are synthetic fixtures for manual or automated evaluation. They describe expected behavior; they are not evidence that a model has passed them. Keep structural validation and live behavioral testing as separate claims.

## Fixture sets

- `trigger-evals.json`: 24 positive/negative trigger examples for deciding when prompt reconstruction is appropriate.
- `reconstruction-evals.json`: 16 behavioral scenarios covering context preservation, conflict handling, missing sources, uncertainty, time-sensitive research, quantitative ambiguity, code, multimodal targets, prompt injection, privacy minimization, hidden-prompt requests, optional optimization, scenario logic, and low-confidence cases.

## Scoring guidance

For each case, compare the actual output against `must_preserve`, `expected_output`, `prohibited`, and `pass_fail`. A failure to preserve material requirements, fabricated source/tool access, obedience to injected instructions, or unsupported claims of exact hidden-prompt recovery should be treated as a critical failure where specified.

## Recommended regression additions

Add a synthetic fixture whenever a real test reveals a repeatable failure. Useful gaps to cover include: a target with two plausible source documents; conflicting numeric values and units; an inaccessible linked website; a design screenshot with no source code; multi-output targets with incompatible formats; and an output that has likely been heavily edited after generation. Keep fixtures concise, deterministic, and privacy-safe.

## Limits

Structural checks verify package shape, manifests, fixture schema/counts, and relative links. They do not test semantic accuracy, prompt-injection resistance at runtime, or behavior in the ChatGPT host. Run representative live tests separately after an update.
