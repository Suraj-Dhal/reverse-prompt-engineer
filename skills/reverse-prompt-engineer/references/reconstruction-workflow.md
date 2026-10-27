# Reconstruction workflow

Use this deeper workflow for complex, context-heavy, multi-source, multimodal, or scenario-rich tasks. Scale effort to task complexity, but do not skip checks that materially affect fidelity.

## 1. Define the reconstruction target

- Name the exact artifact/output and intended use.
- Determine whether the user wants one prompt behind one output, a common prompt behind multiple outputs, or a master prompt reconstructed from a conversation and source package.
- Separate the target from supporting evidence and examples.
- If multiple outputs materially conflict, do not assume one prompt explains them all; state the issue and make the best supported reconstruction under the user's stated preference.

## 2. Inventory sources and precedence

Track relevant sources in a compact working inventory: current user request, earlier valid instructions, files, examples, datasets, source notes, and prior decisions. Confirm actual access before relying on a source.

Apply this precedence:
1. Latest explicit user instruction when it clearly supersedes an earlier one.
2. Still-valid explicit earlier user requirements.
3. Documents the user identifies as authoritative.
4. Directly observable target features.
5. Strong inferences supported by multiple clues.
6. Weak inferences only when useful and labeled.

Do not promote model defaults, generic stylistic traits, or speculation above user-provided requirements. Preserve unresolved conflicts rather than silently blending them. If a source is unavailable, disclose the gap and continue only from accessible evidence.

## 3. Analyze target characteristics

Inspect the dimensions relevant to the target:

- Goal, audience, use case, role, scope, and expected decision/action.
- Structure, ordering, tone, language, terminology, length, examples, and formatting.
- Domain method, frameworks, data definitions, units, formulas, citations, assumptions, and acceptance criteria.
- Visual or multimodal characteristics that are actually observable.
- Scenarios, conditional branches, exceptions, dependencies, deadlines, omissions, and contradictions.
- Signs that the final artifact may have been edited or post-processed after generation.

Generic traits rarely identify a unique original instruction. Do not claim a specific model, exact prompt wording, hidden setting, or unique workflow without evidence.

## 4. Map requirements to evidence

For each material requirement, record the candidate instruction, evidence class, supporting source/clue, confidence or conflict, and whether it belongs in the final prompt. Use `assets/requirement-evidence-matrix-template.md` for complex tasks. Expose only a concise user-facing evidence summary, not private chain-of-thought.

## 5. Preserve context and scenario logic

- Keep facts and instructions separate from inferred requirements.
- Preserve names, quantities, units, dates, source labels, decision rules, branches, dependencies, exceptions, deadlines, and deliverable formats when material.
- Do not collapse different cases or prospects into one generic case.
- Where instructions conflict, apply precedence only when clear; otherwise state the conflict and represent it as unresolved.
- Remove irrelevant personal details and unrelated history.

## 6. Synthesize the prompt

Use only applicable components: role, context, goal, inputs, source precedence, method, scenarios, constraints, exclusions, output schema, source/citation rules, evaluation criteria, uncertainty handling, and tool requirements. Make each instruction actionable and testable. Use placeholders for genuinely missing inputs, not invented facts.

## 7. Run coverage and compression passes

**Coverage:** every material requirement and dependency is represented. Check all source documents and scenarios, not just the most recent or most prominent one.

**Compression:** remove duplicated instructions, irrelevant history, generic filler, unsupported detail, and contradictory requirements that were silently merged.

## 8. Validate and report

Check target fidelity, audience, context/source precedence, scenario completeness, domain method, format, tone, units, time sensitivity, safety, uncertainty, and copy-readiness. Do not turn incidental output details into mandatory instructions without evidence. Briefly report strongest clues, preserved context, material assumptions, confidence, and limitations.

## 9. Default output

Use exactly two main sections unless the user requests another format:

1. `Reconstructed Prompt` — one complete copy-ready prompt.
2. `Reasoning` — concise evidence, context-preservation, prompt-design, and confidence summary.

Do not provide several competing prompt versions by default. If the user asks for optimization too, keep the reconstruction primary and label improvements separately.
