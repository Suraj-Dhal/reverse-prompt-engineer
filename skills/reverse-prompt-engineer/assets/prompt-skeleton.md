# Prompt skeleton

Use this order for the reconstructed prompt. **Every section is optional.** Include a section only when the evidence supports it, and leave out empty sections rather than filling them with generic text. A short, low-evidence target may need only Task and Output format.

```text
ROLE
You are {{ROLE}} with expertise in … .               ← only if the target shows a clear persona or expertise level

CONTEXT
Audience: …   Purpose: …   Use: …                     ← who reads it, and why
Background facts to rely on: …                        ← names, figures, dates and units, exactly as sourced

TASK
Write / analyse / build … .                           ← one clear, imperative objective

INPUTS
Use: {{SOURCE_1}}, {{SOURCE_2}} … .                   ← what the model is given
If sources conflict: prefer … .                       ← source precedence, when material
If an input is missing: … .                           ← missing-input handling

METHOD
1. …                                                  ← the steps, framework or analysis the target reflects
2. …

SCENARIOS                                             ← only for multi-case tasks
- If <condition A>: <action> → <output A>. Exception: … .
- If <condition B>: … .

CONSTRAINTS
Must: … .   Must not: … .                             ← scope, exclusions, compliance, tone limits
Length: … .   Language: … .   Tone: … .

OUTPUT FORMAT
Sections, in order: … .                               ← the observed structure, tables, schema, citations

QUALITY CHECKS
Before finishing, verify that … .                     ← acceptance criteria the target appears to satisfy
```

## Writing rules

- **Imperative and testable:** "List three risks, each with likelihood and impact", not "Discuss risks".
- **Exact facts:** copy figures, units, names and dates exactly as they appear in the source.
- **Placeholders:** use `{{UPPER_SNAKE_CASE}}` only for genuinely missing values, never for facts you could copy from the evidence.
- **No commentary:** the prompt speaks to the model. Evidence labels, confidence and caveats go in Reasoning.
- **No bloat:** if removing a line would not change the output, remove it.
- **Language:** write the prompt so that it reproduces the target's language; if the prompt is in another language, state the output language and script explicitly.
- The arrows (`←`) and their notes are guidance for you. Never copy them into the prompt.
